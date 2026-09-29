"""Enquadramento da tela dividida: rotação do bruto + recortes 9:16 (aberto, fechado, dividida).

- Rotação: o bruto da tela dividida vem em 4K com a câmera DEITADA e sem metadado de rotação.
  Testa as 4 rotações com o detector de rosto e fica com a que acha o rosto em pé.
- Rosto (YuNet) a cada 0,5 s nos trechos do corte; mediana por segmento (tomada).
- Recortes por segmento, sempre medidos no quadro girado:
    aberto   rosto = 30% da largura, centro do rosto em y = 30% da altura
    fechado  punch-in de 1,5x (1,25x se o bruto já vier fechado), rosto em y = 33%
    dividida plano aberto "descido": faixa 1080x(1920-EMENDA) com o rosto a 62% da altura do quadro
  Nunca amplia mais que UPSCALE_MAX; se o bruto não deixar, fica o mais aberto possível (aviso).

Saída: <trabalho>/enquadramento_td.json
Uso: python enquadrar_td.py <trabalho> [--rot 0|90|180|270]
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
from td_comum import (DIVIDIDA_ROSTO_CY, EMENDA, FECHADO_FATOR, FECHADO_FATOR_MIN, H, MODELO_ROSTO,  # noqa: E402
                      ROSTO_ABERTO, ROSTO_CY_ABERTO, ROSTO_MAX, UPSCALE_MAX, W,
                      gravar_json, ler_json, rect_zoom, transpose_filtro)

PARALELO = 6
_local = threading.local()
GPU = "cuda" in subprocess.run(["ffmpeg", "-hide_banner", "-hwaccels"], capture_output=True, text=True).stdout


def detector(w: int, h: int):
    import cv2
    chave = (w, h)
    if getattr(_local, "chave", None) != chave:
        _local.det = cv2.FaceDetectorYN.create(str(MODELO_ROSTO), "", (w, h), 0.6, 0.3, 5000)
        _local.chave = chave
    return _local.det


def quadros(fonte: str, t0: float, dur: float, fps: float, rot: int, larg: int, w0: int, h0: int):
    """Quadros girados e reduzidos (larg = largura do quadro girado)."""
    rw, rh = (h0, w0) if rot in (90, 270) else (w0, h0)
    alt = int(round(larg * rh / rw / 2) * 2)
    t = transpose_filtro(rot)
    vf = f"fps={fps}," + (f"{t}," if t else "") + f"scale={larg}:{alt}"
    base = ["ffmpeg", "-v", "error"]
    for hw in ([["-hwaccel", "cuda"]] if GPU else []) + [[]]:
        p = subprocess.run(base + hw + ["-ss", f"{t0:.3f}", "-i", fonte, "-t", f"{dur:.3f}", "-vf", vf,
                                        "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True)
        if p.returncode == 0 and p.stdout:
            break
    n = len(p.stdout) // (larg * alt * 3)
    return np.frombuffer(p.stdout[: n * larg * alt * 3], np.uint8).reshape(n, alt, larg, 3), rw / larg


def melhor_rosto(img) -> list[float] | None:
    """[x, y, w, h, confiança, olhos_x, olhos_y] (olhos = ponto médio entre os dois olhos do YuNet)."""
    h, w = img.shape[:2]
    _, fs = detector(w, h).detect(img)
    if fs is None or not len(fs):
        return None
    f = max(fs, key=lambda f: f[2] * f[3] * f[14])
    olhos = [(float(f[4]) + float(f[6])) / 2, (float(f[5]) + float(f[7])) / 2]
    return [float(v) for v in f[:4]] + [float(f[14])] + olhos if f[14] >= 0.7 else None


def detectar_rotacao(fonte: str, segs: list[dict], w0: int, h0: int) -> tuple[int, dict]:
    ts = [s["src_in"] + (s["src_out"] - s["src_in"]) / 2 for s in segs]
    ts = [ts[int(i)] for i in np.linspace(0, len(ts) - 1, min(6, len(ts)))]
    placar = {}
    for rot in (0, 90, 270, 180):
        tot = 0.0
        for t in ts:
            fr, _ = quadros(fonte, t, 0.05, 30, rot, 720, w0, h0)
            if len(fr):
                f = melhor_rosto(fr[0])
                tot += f[4] if f else 0
        placar[rot] = round(tot, 2)
        if rot == 0 and tot >= 0.85 * len(ts):
            break                                   # em pé já na orientação original
    return max(placar, key=placar.get), placar


def recorte(cx: float, cy: float, fw: float, rw: int, rh: int, larg_rosto: float, cy_alvo: float,
            aspecto: float) -> tuple[list[float], float]:
    """Recorte [x, y, w, h] (aspecto = w/h) com o rosto ocupando larg_rosto da largura e o centro do
    rosto em cy_alvo da altura. Limitado ao quadro e a UPSCALE_MAX. Devolve (rect, larg_real_do_rosto)."""
    w_max = min(rw, rh * aspecto)
    w = min(max(fw / larg_rosto, min(W / UPSCALE_MAX, w_max)), w_max)
    h = w / aspecto
    x = min(max(cx - w / 2, 0), rw - w)
    y = min(max(cy - cy_alvo * h, 0), rh - h)
    return [round(x, 1), round(y, 1), round(w, 1), round(h, 1)], fw / w


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("trabalho")
    ap.add_argument("--rot", type=int, choices=[0, 90, 180, 270])
    a = ap.parse_args()
    T = Path(a.trabalho)
    corte = ler_json(T / "corte.json")
    fonte, segs = corte["fonte"], corte["segmentos"]
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                        "-of", "csv=p=0", fonte], capture_output=True, text=True)
    w0, h0 = [int(v) for v in r.stdout.strip().split("\n")[0].split(",")[:2]]
    if a.rot is None:
        rot, placar = detectar_rotacao(fonte, segs, w0, h0)
    else:
        rot, placar = a.rot, {}
    rw, rh = (h0, w0) if rot in (90, 270) else (w0, h0)
    print(f"bruto {w0}x{h0}, rotação {rot}° -> {rw}x{rh} {placar}", flush=True)

    def detectar(s: dict):
        fr, esc = quadros(fonte, s["src_in"], s["src_out"] - s["src_in"], 2, rot, 1080, w0, h0)
        out = []
        for k, img in enumerate(fr):
            f = melhor_rosto(img)
            if f:
                out.append((s["dst_in"] + k * 0.5, [f[0] * esc, f[1] * esc, f[2] * esc, f[3] * esc, f[5] * esc, f[6] * esc]))
        return out

    with ThreadPoolExecutor(PARALELO) as ex:
        res = list(ex.map(detectar, segs))
    todos = np.array([f for r_ in res for _, f in r_])
    if not len(todos):
        raise SystemExit("nenhum rosto encontrado no bruto")
    g = np.median(todos, axis=0)
    avisos = []
    saida = []
    alt_div = H - EMENDA
    for k, (s, r_) in enumerate(zip(segs, res)):
        fs_k = np.array([f for _, f in r_]) if r_ else np.array([g])
        if not r_:
            avisos.append(f"seg{k:02d}: rosto não achado, uso a mediana geral")
        fx, fy, fw, fh, ox, oy = np.median(fs_k, axis=0)
        cx, cy = fx + fw / 2, fy + fh / 2
        ab, la = recorte(cx, cy, fw, rw, rh, ROSTO_ABERTO, ROSTO_CY_ABERTO, W / H)
        fator = FECHADO_FATOR if la <= ROSTO_ABERTO * 1.12 else FECHADO_FATOR_MIN
        fator = min(fator, ROSTO_MAX / la, ab[2] / (W / UPSCALE_MAX))
        # regra do usuário (28/09/2026): todo zoom mantém a altura dos olhos. O fechado é o aberto
        # ampliado em volta do ponto entre os olhos, que fica parado no quadro (sempre cabe no aberto)
        olhos = [round(float(ox), 1), round(float(oy), 1)]
        fe = [round(v, 1) for v in rect_zoom(ab, olhos, fator)]
        lf = la * fator
        # dividida: mesma escala do aberto; a faixa de baixo mostra o rosto a 62% do quadro
        esc_ab = ab[2] / W                                   # px do bruto por px do quadro
        dw, dh = W * esc_ab, alt_div * esc_ab
        cy_band = (DIVIDIDA_ROSTO_CY * H - EMENDA) / alt_div
        dv = [min(max(cx - dw / 2, 0), rw - dw), min(max(cy - cy_band * dh, 0), rh - dh), dw, dh]
        if fe[2] < W / UPSCALE_MAX:
            avisos.append(f"seg{k:02d}: fechado ampliado {W / fe[2]:.2f}x")
        saida.append({"k": k, "rosto": [round(float(cx), 1), round(float(cy), 1), round(float(fw), 1)],
                      "olhos": olhos, "aberto": ab, "fechado": fe, "dividida": [round(v, 1) for v in dv],
                      "rosto_aberto": round(la, 3), "rosto_fechado": round(lf, 3), "amostras": len(r_)})
    la_med = float(np.median([s["rosto_aberto"] for s in saida]))
    if la_med > ROSTO_ABERTO * 1.15:
        avisos.append(f"bruto fechado: no plano mais aberto possível o rosto ocupa {la_med:.0%} da largura "
                      f"(padrão {ROSTO_ABERTO:.0%}); o fechado usa {FECHADO_FATOR_MIN}x")
    # queixo no quadro aberto (para a legenda não subir no rosto)
    gravar_json(T / "enquadramento_td.json", {"fonte": fonte, "rot": rot, "wh0": [w0, h0], "wh_rot": [rw, rh],
                                              "rotacao_placar": placar, "segmentos": saida, "avisos": avisos})
    print(f"ok: {len(saida)} segmentos; rosto no aberto ~{la_med:.0%} da largura")
    for av in avisos:
        print("  aviso:", av)


if __name__ == "__main__":
    main()
