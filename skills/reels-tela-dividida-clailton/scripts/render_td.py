"""Render final da tela dividida: composição quadro a quadro + legenda (libass) + áudio da novela.

- Clailton: cada plano da timeline é decodificado do bruto (NVDEC) já recortado no zoom do plano
  (aberto 9:16, fechado 9:16, ou faixa de baixo da tela dividida), girado se a câmera veio deitada.
  Busca exata como no render da novela (-ss antes do -i, meio quadro antes). Plano coberto por
  imagem em tela cheia nem é decodificado.
- Imagem parada: recorte 'cover' no assunto (rosto) + zoom-out constante de ~5%/s terminando em 1,0.
- Vídeo: recorte 'cover' no assunto, sem zoom, sem áudio, conformado a 29,97.
- Cartão: imagem a 86% da largura sobre fundo claro em degradê, sombra suave, quase parado.
- Tela dividida: imagem em y 0..EMENDA, Clailton embaixo. Saída da abertura: flash de exposição.
- Áudio: fatias exatas do bruto + normalização (-16 LUFS / -1 dBTP, limitador suave) da novela; som de
  teclado padrão na CTA (RN.mixar_teclado, 1o toque na 1a letra). H.264 High CRF 10 slow, BT.709, AAC 320k (qualidade máxima, como a novela).

Uso: python render_td.py <trabalho> <saida.mp4> [--sem-cuda] [--sem-clique] [--ate SEG] [--rapido]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import queue
import shutil
import subprocess
import sys
import threading
import time
import wave
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from td_comum import (CARTAO_CY, CARTAO_LARG, EMENDA, FLASH_ANTES, FLASH_DEPOIS, FPS, FPS_DEN, FPS_NUM, H,  # noqa: E402
                      W, ZOOM_CARTAO, ZOOM_FOTO, ZOOM_FOTO_MAX, filtro_recorte, gravar_json, ler_json, movel,
                      rect_plano, regiao_plano, wh_video)
from midia_util import area_util, caixa_cover  # noqa: E402  (area_util: premiere_td importa daqui)
from estilo_td import Estilo  # noqa: E402
from td_comum import ESTILO_FORCA  # noqa: E402
from collections import deque  # noqa: E402
from concurrent.futures import ThreadPoolExecutor  # noqa: E402

import render_final as RN  # noqa: E402  (áudio da novela)
from comum import AUDIO_BR, CRF, PRESET  # noqa: E402

GPU = "cuda" in subprocess.run(["ffmpeg", "-hide_banner", "-hwaccels"], capture_output=True, text=True).stdout
MATRIZ_IN = "in_color_matrix=bt709:in_range=tv"
BAIXO_H = H - EMENDA


# ------------------------------------------------------------------ leitura de quadros
class Leitor(threading.Thread):
    """Roda uma lista de comandos ffmpeg (rawvideo rgb24 de tamanho fixo) em ordem e põe os quadros
    numa fila limitada (memória: ~40 quadros de 1080x1920)."""

    def __init__(self, tarefas: list[tuple[str, list[str], int, int, int]], maxq: int = 40):
        super().__init__(daemon=True)
        self.tarefas = tarefas            # (chave, cmd, w, h, n_quadros)
        self.q: queue.Queue = queue.Queue(maxq)
        self.erro = None

    def run(self):
        try:
            for chave, cmd, w, h, n in self.tarefas:
                tam = w * h * 3
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                ult = None
                for _ in range(n):
                    b = p.stdout.read(tam)
                    if len(b) < tam:
                        break
                    ult = np.frombuffer(b, np.uint8).reshape(h, w, 3)
                    self.q.put((chave, ult))
                    n -= 1
                p.stdout.close()
                p.wait()
                if ult is None:
                    ult = np.zeros((h, w, 3), np.uint8)
                    print(f"  AVISO: {chave} sem quadros ({p.stderr.read()[-200:]!r})", flush=True)
                for _ in range(n):                       # faltou quadro: segura o último
                    self.q.put((chave, ult))
        except Exception as e:  # noqa: BLE001
            self.erro = e
            self.q.put((None, None))

    def pegar(self, chave: str) -> np.ndarray:
        k, fr = self.q.get()
        if k is None:
            raise SystemExit(f"leitor falhou: {self.erro!r}")
        if k != chave:
            raise SystemExit(f"leitor fora de ordem: esperava {chave}, veio {k}")
        return fr


def filtro_trecho(m: dict, c: dict) -> tuple[list[str], str, int, int]:
    """Entrada (-ss) e filtro do trecho de vídeo no layout do item — o MESMO no render e no Premiere:
    área útil (sem tarja de filme) + recorte por plano do reenquadramento (reenquadrar_td), ou o foco
    manual do plano (foco=0.3), ou o recorte antigo pelos rostos da miniatura."""
    faixa = c["layout"] in ("topo", "dividida")
    ow, oh = (W, EMENDA) if faixa else (W, H)
    bx, by, vw, vh = area_util(m["arquivo"])
    rec = (m.get("recortes") or {}).get("faixa" if faixa else "vertical")
    ss = ["-ss", f"{m['entrada']:.3f}"] if m.get("entrada") else []
    if rec and c.get("foco") is None:
        alvo = ow / oh
        if vw / vh > alvo:
            cw, ch, eixo, folga = vh * alvo, vh, "x", vw - vh * alvo
        else:
            cw, ch, eixo, folga = vw, vw / alvo, "y", vh - vw / alvo
        vals = [(r["t"], int(round(r["p"] * folga))) for r in rec]
        expr = str(vals[-1][1])
        for k in range(len(vals) - 2, -1, -1):                 # if(lt(t,t1),x0,if(lt(t,t2),x1,x2))
            expr = f"if(lt(t,{vals[k + 1][0]:.3f}),{vals[k][1]},{expr})"
        xs = f"{bx}+{expr}" if eixo == "x" else str(bx)
        ys = f"{by}+{expr}" if eixo == "y" else str(by)
        corte = f"setpts=PTS-STARTPTS,crop=w={int(cw) // 2 * 2}:h={int(ch) // 2 * 2}:x='{xs}':y='{ys}'"
    else:
        rost = m.get("rostos")
        if rost and (bx or by):
            fw, fh = wh_video(m["arquivo"])
            rost = [[(r[0] * fw - bx) / vw, (r[1] * fh - by) / vh, r[2] * fw / vw, r[3] * fh / vh] + r[4:] for r in rost]
        x, y, cw, ch = caixa_cover(vw, vh, ow, oh, (c.get("foco"), None) if c.get("foco") is not None else None, rost)
        corte = f"crop={int(cw) // 2 * 2}:{int(ch) // 2 * 2}:{int(x + bx)}:{int(y + by)}"
    return ss, f"fps={FPS_NUM}/{FPS_DEN},{corte},scale={ow}:{oh}:flags=lanczos", ow, oh


def quadro_rect(dec: np.ndarray, reg: list[float], r: list[float]) -> np.ndarray:
    """Plano móvel (zoom animado ou ajuste dos olhos, em keyframes): o plano vem decodificado na região
    `reg` do bruto em resolução maior e cada quadro recorta o retângulo r (px do bruto) dela."""
    x, y, w, h = r
    q = dec.shape[1] / reg[2]                                 # px decodificado por px do bruto
    xd, yd, wd, hd = (x - reg[0]) * q, (y - reg[1]) * q, w * q, h * q
    M = np.array([[wd / W, 0, xd + 0.5 * wd / W - 0.5], [0, hd / H, yd + 0.5 * hd / H - 0.5]], np.float64)
    return cv2.warpAffine(dec, M, (W, H), flags=cv2.INTER_CUBIC | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REFLECT)


def cmd_bruto(fonte: str, frame_in: int, n: int, vf: str, cuda: bool) -> list[str]:
    t = max(0.0, (frame_in - 0.5) / FPS)
    return (["ffmpeg", "-v", "error"] + (["-hwaccel", "cuda"] if cuda else [])
            + ["-ss", f"{t:.6f}", "-i", fonte, "-frames:v", str(n), "-an", "-sn", "-vf", vf,
               # passthrough: saída 'rawvideo' em modo CFR duplicava o 1º quadro quando a busca caía entre
               # quadros (plano inteiro 1 quadro atrasado; pego pela conferência de sincronia)
               "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])


# ------------------------------------------------------------------ imagens
def aparar_bordas(img: Image.Image, rostos: list | None):
    """Tira faixa lisa (preta/branca) gravada na borda da imagem (print, still com tarja)."""
    a = np.asarray(img.convert("L"), dtype=np.int16)
    h, w = a.shape

    def liso(v: np.ndarray) -> bool:
        return v.std() < 4 and (v.mean() < 25 or v.mean() > 235)

    t = 0
    while t < h * 0.3 and liso(a[t]):
        t += 1
    b = h
    while b > h * 0.7 and liso(a[b - 1]):
        b -= 1
    lft = 0
    while lft < w * 0.3 and liso(a[:, lft]):
        lft += 1
    r = w
    while r > w * 0.7 and liso(a[:, r - 1]):
        r -= 1
    if (t + h - b) < h * 0.03 and (lft + w - r) < w * 0.03:
        return img, rostos
    novos = None
    if rostos:
        novos = [[(f[0] * w - lft) / (r - lft), (f[1] * h - t) / (b - t), f[2] * w / (r - lft), f[3] * h / (b - t)] + f[4:]
                 for f in rostos]
    return img.crop((lft, t, r, b)), novos


class Imagem:
    """Imagem parada pronta para o zoom: reduzida uma vez para ~1,25x o tamanho de saída."""

    def __init__(self, caminho: str, ow: int, oh: int, rostos: list, foco, zoom_max: float):
        img = Image.open(caminho).convert("RGB")
        img, rostos = aparar_bordas(img, rostos)
        x, y, w, h = caixa_cover(img.width, img.height, ow, oh, foco, rostos)
        esc = min(1.0, (ow * (1 + zoom_max) * 1.05) / w)
        if esc < 1.0:
            img = img.resize((max(1, int(img.width * esc)), max(1, int(img.height * esc))), Image.LANCZOS)
            x, y, w, h = x * esc, y * esc, w * esc, h * esc
        self.arr = np.ascontiguousarray(np.asarray(img))
        self.box = (x, y, w, h)
        self.ow, self.oh = ow, oh

    def quadro(self, s: float) -> np.ndarray:
        """s = escala (1,0 = recorte cover inteiro; >1 = mais perto)."""
        x, y, w, h = self.box
        cx, cy = x + w / 2, y + h / 2
        w2, h2 = w / s, h / s
        x0, y0 = cx - w2 / 2, cy - h2 / 2
        M = np.array([[w2 / self.ow, 0, x0 + 0.5 * w2 / self.ow - 0.5], [0, h2 / self.oh, y0 + 0.5 * h2 / self.oh - 0.5]],
                     np.float64)
        return cv2.warpAffine(self.arr, M, (self.ow, self.oh), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP,
                              borderMode=cv2.BORDER_REFLECT)


def fundo_cartao() -> np.ndarray:
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * CARTAO_CY) / H) ** 2)
    v = 244 - 42 * np.clip(d / 0.75, 0, 1) ** 1.6
    return np.repeat(v[..., None], 3, axis=2).astype(np.uint8)


class Cartao:
    def __init__(self, caminho: str):
        img = Image.open(caminho).convert("RGB")
        cw = int(W * CARTAO_LARG)
        ch = int(cw * img.height / img.width)
        if ch > H * 0.58:
            ch = int(H * 0.58)
            cw = int(ch * img.width / img.height)
        self.card = np.asarray(img.resize((cw, ch), Image.LANCZOS))
        base = fundo_cartao().astype(np.float32)
        sombra = np.zeros((H, W), np.float32)
        x0, y0 = (W - cw) // 2, int(H * CARTAO_CY - ch / 2)
        sombra[y0 + 14:y0 + ch + 14, x0 + 4:x0 + cw + 4] = 1.0
        sombra = cv2.GaussianBlur(sombra, (0, 0), 18) * 0.38
        self.fundo = (base * (1 - sombra[..., None])).astype(np.uint8)
        self.x0, self.y0 = x0, y0

    def quadro(self, s: float) -> np.ndarray:
        fr = self.fundo.copy()
        ch, cw = self.card.shape[:2]
        if abs(s - 1) > 1e-3:
            nw, nh = int(round(cw * s)), int(round(ch * s))
            card = cv2.resize(self.card, (nw, nh), interpolation=cv2.INTER_LINEAR)
        else:
            card, nw, nh = self.card, cw, ch
        x0, y0 = W // 2 - nw // 2, int(H * CARTAO_CY - nh / 2)
        xa, ya = max(0, x0), max(0, y0)
        xb, yb = min(W, x0 + nw), min(H, y0 + nh)
        fr[ya:yb, xa:xb] = card[ya - y0:yb - y0, xa - x0:xb - x0]
        return fr


# ------------------------------------------------------------------ principal
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("trabalho")
    ap.add_argument("saida")
    ap.add_argument("--sem-cuda", action="store_true")
    ap.add_argument("--sem-clique", action="store_true", help="CTA sem o som de teclado")
    ap.add_argument("--ate", type=float, help="renderiza só os primeiros N segundos (prévia)")
    ap.add_argument("--rapido", action="store_true", help="prévia: preset veryfast CRF 18")
    ap.add_argument("--estilo", type=float, help="força da camada película (0 desliga; padrão: plano ou td_comum)")
    a = ap.parse_args()
    T = Path(a.trabalho).resolve()
    saida = Path(a.saida).resolve()
    cuda = GPU and not a.sem_cuda
    corte = ler_json(T / "corte.json")
    enq = ler_json(T / "enquadramento_td.json")
    tl = ler_json(T / "timeline.json")
    esc = ler_json(T / "midia" / "escolhas.json")
    lay = ler_json(T / "layout.json")
    fonte, segs = corte["fonte"], corte["segmentos"]
    rot, (w0, h0) = enq["rot"], enq["wh0"]
    F_FALA = tl["frames_fala"]
    F_TOTAL = lay["frames_total"]
    if a.ate:
        F_TOTAL = min(F_TOTAL, int(a.ate * FPS))
    seg_f0 = tl["segmentos_f0"]
    tmp = T / "tmp_render"
    tmp.mkdir(exist_ok=True)
    t_ini = time.time()

    # ---------------- áudio
    print("áudio...", flush=True)
    aud = RN.montar_audio(fonte, segs, lay["frames_total"] - F_FALA, tmp)
    audio = Path(aud["path"])
    if tl["cta"] and not a.sem_clique:                       # som de teclado padrão, 1o toque na 1a letra
        import legenda_novela as LN
        RN.mixar_teclado(audio, (F_FALA + LN.CTA_ATRASO) / FPS)

    # ---------------- planos do Clailton (só os visíveis)
    tarefas = []
    for i, p in enumerate(tl["planos"]):
        if not p["visivel"]:
            continue
        s = segs[p["seg"]]
        e = enq["segmentos"][p["seg"]]
        n = p["f1"] - p["f0"]
        if p["zoom"] == "dividida":
            vf = filtro_recorte(e["dividida"], rot, w0, h0, W, BAIXO_H, rgb=True)
            ow, oh = W, BAIXO_H
        elif movel(p):                                       # zoom animado / olhos na linha: região maior
            reg, ow, oh = regiao_plano(p, e)
            p["_reg"] = reg
            vf = filtro_recorte(reg, rot, w0, h0, ow, oh, rgb=True)
        else:                                                # rect: fechado com os olhos na linha (plano_td)
            vf = filtro_recorte(rect_plano(p, e, 0), rot, w0, h0, W, H, rgb=True)
            ow, oh = W, H
        tarefas.append((f"p{i}", cmd_bruto(fonte, s["frame_in"] + (p["f0"] - seg_f0[p["seg"]]), n, vf, cuda), ow, oh, n))
    clailton = Leitor(tarefas)
    clailton.start()

    # ---------------- camadas (imagem / vídeo / cartão)
    camadas = sorted(tl["camadas"], key=lambda c: c["f0"])
    por_id = {c["id"]: c for c in camadas}

    def midia_de(c: dict) -> dict:
        alvo = c["igual"] if c["tipo"] == "igual" else c["id"]
        if alvo not in esc:
            raise SystemExit(f"{c['id']}: sem mídia escolhida (rode buscar_td.py)")
        return esc[alvo]

    videos: dict[str, Leitor] = {}

    def prepara_video(c: dict) -> Leitor:
        m = midia_de(c)
        ss, vf, ow, oh = filtro_trecho(m, c)                  # entrada + recorte por plano (reenquadramento)
        n = c["f1"] - c["f0"]
        vf += f":{MATRIZ_IN},format=rgb24,tpad=stop_mode=clone:stop_duration=5"
        cmd = ["ffmpeg", "-v", "error"] + ss + ["-i", m["arquivo"], "-frames:v", str(n), "-an", "-vf", vf,
                                                "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
        lt = Leitor([(c["id"], cmd, ow, oh, n)], maxq=30)
        lt.start()
        return lt

    cache_img: dict[str, object] = {}

    def fonte_quadro(c: dict):
        m = midia_de(c)
        if m["midia"] == "video":
            return None
        chave = c["id"]
        if chave not in cache_img:
            d = (c["f1"] - c["f0"]) / FPS
            if c["layout"] == "cartao":
                cache_img[chave] = Cartao(m["arquivo"])
            else:
                ow, oh = (W, EMENDA) if c["layout"] in ("topo", "dividida") else (W, H)
                zm = min(ZOOM_FOTO_MAX, ZOOM_FOTO * d) if c.get("zoom") not in ("0", "nao") else 0.0
                foco = (c.get("foco"), None) if c.get("foco") is not None else None
                cache_img[chave] = Imagem(m["arquivo"], ow, oh, m.get("rostos"), foco, zm)
        return cache_img[chave]

    def escala(c: dict, k: int) -> float:
        d = (c["f1"] - c["f0"]) / FPS
        t = k / FPS
        if c["layout"] == "cartao":
            return 1.0 + ZOOM_CARTAO * t
        if c.get("zoom") in ("0", "nao"):
            return 1.0
        z = min(ZOOM_FOTO_MAX, ZOOM_FOTO * d)
        if c.get("zoom") == "in":
            return 1.0 + z * (t / max(d, 1e-6))
        return 1.0 + z * (1 - t / max(d, 1e-6))          # zoom-out terminando em 1,0

    # ---------------- encoder
    preset, crf = ("veryfast", 18) if a.rapido else (PRESET, CRF)
    tmp_out = T / "final_tmp.mp4"
    enc_cmd = ["ffmpeg", "-hide_banner", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
               "-r", f"{FPS_NUM}/{FPS_DEN}", "-i", "-", "-i", str(audio),
               # a legenda entra DEPOIS da conversão para YUV: com "YCbCr Matrix: TV.709" o libass sobre RGB
               # comprime o branco para 235 (texto acinzentado)
               "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,ass=legenda.ass:fontsdir=fonts,"
                      "setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv",
               "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-profile:v", "high",
               "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
               "-color_range", "tv", "-c:a", "aac", "-b:a", AUDIO_BR, "-ar", "48000", "-movflags", "+faststart",
               "-shortest", str(tmp_out)]
    enc = subprocess.Popen(enc_cmd, stdin=subprocess.PIPE, cwd=T)

    ab_f1 = tl["abertura"]["f1"]
    flash = {}
    if ab_f1 > 0:                                            # sem abertura (edição simples): sem flash
        for k, g in enumerate(reversed(FLASH_ANTES)):
            flash[ab_f1 - 1 - k] = g
        for k, g in enumerate(FLASH_DEPOIS):
            flash[ab_f1 + k] = g

    planos = tl["planos"]
    pi = 0
    preto = np.zeros((H, W, 3), np.uint8)
    corpo = [c for c in camadas if not c["id"].startswith("t")]
    topo = [c for c in camadas if c["id"].startswith("t")]
    # camada de estilo "película" (cor, vinheta, papel + retícula fixos, grão leve, poeira) SÓ NO B-ROLL: na
    # tela cheia de imagem, o quadro todo; na dividida, a faixa de cima; o Clailton passa limpo. 6 threads.
    forca = a.estilo if a.estilo is not None else (tl.get("estilo") if tl.get("estilo") is not None else ESTILO_FORCA)
    estilo = Estilo(forca) if forca > 0 else None
    pool = ThreadPoolExecutor(6) if estilo else None
    fila: deque = deque()

    def saida_de(x) -> np.ndarray:
        return x.result() if hasattr(x, "result") else x

    def escreve(fr_: np.ndarray, n_: int, area_: tuple[int, int] | None) -> None:
        if estilo is None:
            enc.stdin.write(memoryview(np.ascontiguousarray(fr_)))
            return
        fila.append(pool.submit(estilo.aplicar, fr_, n_, area_) if area_ else fr_)   # na ordem, com ou sem estilo
        while len(fila) > 8:
            enc.stdin.write(memoryview(np.ascontiguousarray(saida_de(fila.popleft()))))

    print(f"  estilo: {'força ' + str(forca) if estilo else 'desligado'}", flush=True)
    t_comp = time.time()
    for n in range(F_TOTAL):
        area = None                                          # região de B-roll no quadro (recebe o estilo)
        if n >= F_FALA:
            fr = preto
        else:
            while planos[pi]["f1"] <= n:
                pi += 1
            p = planos[pi]
            cl = clailton.pegar(f"p{pi}") if p["visivel"] else None
            if cl is not None and movel(p) and p["zoom"] != "dividida":
                cl = quadro_rect(cl, p["_reg"], rect_plano(p, enq["segmentos"][p["seg"]], n - p["f0"]))
            c = next((x for x in corpo if x["f0"] <= n < x["f1"]), None)
            if c is None and n < ab_f1:
                c = next((x for x in topo if x["f0"] <= n < x["f1"]), None)
            # vídeo: começa a decodificar 45 quadros antes
            for x in corpo + topo:
                if x["id"] not in videos and x["f0"] - 45 <= n < x["f1"] and midia_de(x)["midia"] == "video":
                    videos[x["id"]] = prepara_video(x)
            if c is None:
                fr = cl
            else:
                k = n - c["f0"]
                m = midia_de(c)
                if m["midia"] == "video":
                    img = videos[c["id"]].pegar(c["id"])
                else:
                    img = fonte_quadro(c).quadro(escala(c, k))
                if c["layout"] in ("topo", "dividida"):
                    fr = np.vstack([img, cl]) if cl is not None and cl.shape[0] == BAIXO_H else img
                    area = (0, EMENDA)
                else:
                    fr = img
                    area = (0, H)
            if n in flash:
                fr = np.clip(fr.astype(np.float32) * flash[n], 0, 255).astype(np.uint8)
        escreve(fr, n, area)
        if n % 300 == 0:
            el = time.time() - t_comp
            print(f"  quadro {n}/{F_TOTAL} ({n / max(el, 1e-6):.1f} q/s)", flush=True)
    while fila:
        enc.stdin.write(memoryview(np.ascontiguousarray(saida_de(fila.popleft()))))
    if pool:
        pool.shutdown()
    enc.stdin.close()
    rc = enc.wait()
    if rc:
        raise SystemExit(f"encoder falhou ({rc})")
    print(f"  composição+encode: {time.time() - t_comp:.0f}s", flush=True)
    saida.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(tmp_out), str(saida))
    gravar_json(T / "render_info.json", {"video": str(saida), "gerado_em": datetime.now().isoformat(timespec="seconds"),
                                         "crf": crf, "preset": preset, "quadros": F_TOTAL, "rot": rot,
                                         "teclado_cta": bool(tl["cta"] and not a.sem_clique),
                                         "loudness": {k: aud[k] for k in ("entrada", "saida", "ganho_db", "modo")},
                                         "tempo_s": round(time.time() - t_ini, 1)})
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"ok: {saida} ({time.time() - t_ini:.0f}s)")


if __name__ == "__main__":
    main()
