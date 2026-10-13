"""Enquadramento fixo da faixa 5:4 a partir do rosto (YuNet) nos trechos do corte.

A referência NÃO faz punch-in: o enquadramento é fixo. O recorte usa a ALTURA CHEIA do bruto
(nada é cortado em cima nem embaixo: o enquadramento vertical da gravação é intencional) e só
escolhe a posição horizontal, com o centro do rosto a 54% da largura. Aqui medimos o rosto no
bruto (só nos trechos usados) e calculamos UM recorte para o vídeo todo, sempre reduzindo a
partir do original (4K -> 1080), nunca ampliando.

Saída (<trabalho>/):
  enquadramento.json  {"crop": [w, h, x, y], "zoom", "rosto": {...}}
  rosto_corte.json    [{"t": tempo editado, "queixo": y do queixo no quadro 1080x1920}]

Uso: python enquadrar.py <pasta_trabalho> [--zoom Z] [--cx 0.54] [--cy 0.32]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import (FAIXA_H, FAIXA_W, FAIXA_Y0, FPS, MODELO_ROSTO, ROSTO_CX, ROSTO_CY, ROSTO_LARG,  # noqa: E402
                   gravar_json, ler_json, sonda)

AMOSTRA_W, AMOSTRA_H = 1920, 1080     # detecção em 1080p: o enquadramento aprovado foi calibrado assim
                                      # (em 540p a caixa do YuNet muda e o recorte sai ~30 px diferente)
PARALELO = 6                          # segmentos decodificados (GPU) e detectados (CPU) ao mesmo tempo
_local = threading.local()


def detector():
    if not hasattr(_local, "det"):
        import cv2
        _local.det = cv2.FaceDetectorYN.create(str(MODELO_ROSTO), "", (AMOSTRA_W, AMOSTRA_H), 0.6, 0.3, 5000)
    return _local.det


# decodifica o 4K na placa (NVDEC), descarta na própria GPU e só baixa os 2 quadros/s da amostra:
# quadros bit a bit iguais aos da CPU (mesmo md5), mais rápido. Sem cuda, tudo na CPU.
GPU = "cuda" in subprocess.run(["ffmpeg", "-hide_banner", "-hwaccels"], capture_output=True, text=True).stdout


def detectar(fonte: str, t0: float, t1: float, passo: float) -> list[tuple[float, list | None]]:
    n = max(1, int((t1 - t0) / passo))
    fsz = AMOSTRA_W * AMOSTRA_H * 3
    hw = ["-hwaccel", "cuda", "-hwaccel_output_format", "cuda"] if GPU else []
    vf = f"fps={1 / passo:.4f}," + ("hwdownload,format=nv12," if GPU else "") + f"scale={AMOSTRA_W}:{AMOSTRA_H}"
    p = subprocess.run(["ffmpeg", "-v", "error"] + hw + ["-ss", f"{t0:.3f}", "-i", fonte, "-t", f"{t1 - t0:.3f}",
                        "-vf", vf, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True)
    if GPU and (p.returncode or len(p.stdout) < fsz):
        # bruto H.264 4:2:2 10-bit: a NVDEC falha no hwdownload; refaz na CPU
        vf = f"fps={1 / passo:.4f},scale={AMOSTRA_W}:{AMOSTRA_H}"
        p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t0:.3f}", "-i", fonte, "-t", f"{t1 - t0:.3f}",
                            "-vf", vf, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True)
    if p.returncode:
        raise SystemExit(f"ffmpeg falhou na amostra do rosto: {p.stderr.decode(errors='replace')[-400:]}")
    out, det = [], detector()
    for k in range(len(p.stdout) // fsz):
        img = np.frombuffer(p.stdout[k * fsz:(k + 1) * fsz], np.uint8).reshape(AMOSTRA_H, AMOSTRA_W, 3)
        _, faces = det.detect(img)
        melhor = None
        if faces is not None and len(faces):
            f = max(faces, key=lambda f: f[2] * f[3])
            if f[-1] >= 0.7:
                melhor = [float(v) for v in f[:4]]
        out.append((t0 + k * passo, melhor))
    return out[:n + 1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("trabalho")
    ap.add_argument("--zoom", type=float)
    ap.add_argument("--cx", type=float, default=ROSTO_CX)
    ap.add_argument("--cy", type=float, default=ROSTO_CY)
    ap.add_argument("--so-rosto", action="store_true",
                    help="mantém o enquadramento.json (recorte aprovado) e só refaz o rosto_corte.json no corte atual")
    a = ap.parse_args()
    trabalho = Path(a.trabalho)
    corte = ler_json(trabalho / "corte.json")
    fonte = corte["fonte"]
    info = sonda(Path(fonte))
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    SW, SH = int(v["width"]), int(v["height"])
    amostras = []   # (t_editado, face em px do bruto, índice do segmento)
    esc = SW / AMOSTRA_W
    with ThreadPoolExecutor(PARALELO) as ex:
        res = list(ex.map(lambda s: detectar(fonte, s["src_in"], s["src_out"], 0.5), corte["segmentos"]))
    for k, (s, r) in enumerate(zip(corte["segmentos"], res)):
        for t, f in r:
            if f:
                f = [f[0] * esc, f[1] * esc, f[2] * esc, f[3] * esc]
            amostras.append((s["dst_in"] + (t - s["src_in"]), f, k))
    faces = np.array([f for _, f, _ in amostras if f])
    if len(faces) == 0:
        raise SystemExit("nenhum rosto encontrado")
    fx, fy, fw, fh = np.median(faces, axis=0)
    cx, cy = fx + fw / 2, fy + fh / 2

    # recorte 5:4 com a ALTURA CHEIA do bruto (zoom 1): o que o usuário enquadrou em cima e embaixo é
    # intencional (30/09/2026: o caderno na mesa foi cortado pelo zoom automático). Só as laterais saem.
    # --zoom existe para pedido explícito de aproximar; sem ele, nunca corta em cima nem embaixo.
    zoom = float(min(max(a.zoom or 1.0, 1.0), 1.6))
    ch = int(round(SH / zoom / 2) * 2)
    cw = int(round(ch * 1.25 / 2) * 2)
    x = int(round(min(max(cx - a.cx * cw, 0), SW - cw)))
    y = int(round(min(max(cy - a.cy * ch, 0), SH - ch)))
    rosto = {"cx": round(float(cx), 1), "cy": round(float(cy), 1), "w": round(float(fw), 1), "h": round(float(fh), 1),
             "amostras": int(len(faces)), "de": len(amostras)}
    real = {"larg": round(float(fw / cw), 3), "cx": round(float((cx - x) / cw), 3), "cy": round(float((cy - y) / ch), 3)}
    # conferência por segmento: a mediana esconde tomada em que ele se deslocou ou encostou na borda
    avisos = []
    por_seg = {}      # tomada com o rosto deslocado: só desliza o recorte na horizontal
    for k in sorted({k for _, _, k in amostras}):
        fs_k = np.array([f for _, f, kk in amostras if f and kk == k])
        if len(fs_k) == 0:
            avisos.append(f"seg{k:02d}: rosto não encontrado")
            continue
        mx, my, mw, mh = np.median(fs_k, axis=0)
        cxk = (mx + mw / 2 - x) / cw
        # recorte fixo: só desliza a tomada em que o rosto encosta ou passa da borda lateral
        borda_fixo = min((fs_k[:, 0] - x).min(), (x + cw - (fs_k[:, 0] + fs_k[:, 2])).min()) / cw
        if borda_fixo < 0.03:
            xk = int(round(min(max(mx + mw / 2 - a.cx * cw, 0), SW - cw)))
            por_seg[str(k)] = [cw, ch, xk, y]
            novo = (mx + mw / 2 - xk) / cw
            avisos.append(f"seg{k:02d}: rosto em {cxk:.0%} da largura -> recorte deslizado para {novo:.0%}")
            cxk, xref = novo, xk
        else:
            xref = x
        borda = min((fs_k[:, 0] - xref).min(), (xref + cw - (fs_k[:, 0] + fs_k[:, 2])).min()) / cw
        if abs(mw / fw - 1) > 0.25:
            avisos.append(f"seg{k:02d}: rosto {mw / fw:.0%} do tamanho mediano")
        if borda < 0.05:
            avisos.append(f"seg{k:02d}: rosto a {borda:.0%} da borda do recorte")
    enq = trabalho / "enquadramento.json"
    if a.so_rosto and enq.exists():
        # corte refeito (correção v2, v3...): o recorte aprovado fica; só o queixo é medido de novo no corte atual
        # (13/10/2026: o rosto_corte.json era de um corte antigo e a legenda subiu no rosto do Clailton)
        cw, ch, x, y = ler_json(enq)["crop"]
    else:
        gravar_json(enq, {"fonte_wh": [SW, SH], "crop": [cw, ch, x, y], "zoom": round(zoom, 3),
                          "crops_segmento": por_seg, "rosto": rosto, "rosto_na_faixa": real, "avisos": avisos})
    # queixo no quadro final (para a legenda não subir no rosto)
    queixos = []
    for t, f, _ in amostras:
        if f:
            q = FAIXA_Y0 + (f[1] + f[3] - y) / ch * FAIXA_H
            queixos.append({"t": round(t, 3), "queixo": round(float(q), 1)})
    gravar_json(trabalho / "rosto_corte.json", queixos)
    print(f"ok: crop {cw}x{ch}+{x}+{y} (zoom {zoom:.2f}); rosto na faixa: {real}")
    for av in avisos:
        print("  aviso:", av)


if __name__ == "__main__":
    main()
