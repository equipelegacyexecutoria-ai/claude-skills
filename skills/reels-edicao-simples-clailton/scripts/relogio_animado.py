"""Relógio (cronômetro) animado + tique-taque para o "em apenas 60 segundos" (nota da Sala, v2 [00:00]).

Uso: python gerar_relogio.py <pasta_saida> <duracao_s>
Saída: <pasta>/f_0000.png ... (RGBA 320x320, 29,97 fps) e <pasta>/tique_taque.wav (48 kHz estéreo).
Cores Legacy: mostrador branco, contorno #141826, azul #3c83f6. Sombra no padrão v3 (halo + contato).
"""
import math
import sys
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

FPS = 30000 / 1001
TAM = 320            # lado do quadro (px da saída)
SS = 4               # supersampling
CX, CY = 160, 182    # centro do mostrador no quadro
R = 80               # raio externo do mostrador
ESCURO = (20, 24, 38)
AZUL = (60, 131, 246)
BRANCO = (255, 255, 255)
TIQUE = 0.30         # s entre um tique e outro
VOLTA = 0.75         # s por volta do ponteiro ("relógio correndo")


def ease_out_back(x: float) -> float:
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def desenhar(progresso: float, ang_ponteiro: float) -> Image.Image:
    s = SS
    im = Image.new("RGBA", (TAM * s, TAM * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy, r = CX * s, CY * s, R * s
    # coroa e botão lateral
    d.rounded_rectangle([cx - 15 * s, cy - r - 24 * s, cx + 15 * s, cy - r - 10 * s], radius=4 * s, fill=ESCURO)
    d.rectangle([cx - 6 * s, cy - r - 12 * s, cx + 6 * s, cy - r + 4 * s], fill=ESCURO)
    a = math.radians(-45)
    bx, by = cx + (r + 6 * s) * math.sin(-a), cy - (r + 6 * s) * math.cos(-a)
    d.ellipse([bx - 9 * s, by - 9 * s, bx + 9 * s, by + 9 * s], fill=ESCURO)
    # aro e mostrador
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ESCURO)
    ri = r - 11 * s
    d.ellipse([cx - ri, cy - ri, cx + ri, cy + ri], fill=BRANCO)
    # tempo correndo: arco azul que enche
    if progresso > 0:
        rp = ri - 7 * s
        arco = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(arco).pieslice([cx - rp, cy - rp, cx + rp, cy + rp], -90, -90 + 360 * progresso,
                                      fill=AZUL + (60,))
        im.alpha_composite(arco)
        d = ImageDraw.Draw(im)
    # marcas
    for k in range(12):
        ang = math.radians(k * 30)
        l = 12 * s if k % 3 == 0 else 7 * s
        x0, y0 = cx + (ri - 3 * s) * math.sin(ang), cy - (ri - 3 * s) * math.cos(ang)
        x1, y1 = cx + (ri - 3 * s - l) * math.sin(ang), cy - (ri - 3 * s - l) * math.cos(ang)
        d.line([x0, y0, x1, y1], fill=ESCURO, width=(5 if k % 3 == 0 else 3) * s)
    # ponteiro
    ang = math.radians(ang_ponteiro)
    hx, hy = cx + (ri - 16 * s) * math.sin(ang), cy - (ri - 16 * s) * math.cos(ang)
    tx, ty = cx - 12 * s * math.sin(ang), cy + 12 * s * math.cos(ang)
    d.line([tx, ty, hx, hy], fill=AZUL, width=6 * s)
    d.ellipse([cx - 9 * s, cy - 9 * s, cx + 9 * s, cy + 9 * s], fill=ESCURO)
    d.ellipse([cx - 4 * s, cy - 4 * s, cx + 4 * s, cy + 4 * s], fill=AZUL)
    return im.resize((TAM, TAM), Image.LANCZOS)


def com_sombra(icone: Image.Image) -> Image.Image:
    """Sombra v3 da legenda aplicada ao ícone: halo difuso (y3, borda 10, desfoque 22, 45%) + contato
    (x1 y4, borda 2, desfoque 4, 72%)."""
    a = icone.split()[3]
    out = Image.new("RGBA", icone.size, (0, 0, 0, 0))
    for dx, dy, borda, blur, op in ((0, 3, 10, 22, 0.45), (1, 4, 2, 4, 0.72)):
        m = a.filter(ImageFilter.MaxFilter(borda * 2 + 1 if borda < 6 else 11))
        if borda >= 6:
            m = m.filter(ImageFilter.MaxFilter(9))
        m = m.filter(ImageFilter.GaussianBlur(blur))
        m = m.point(lambda v, op=op: int(v * op))
        camada = Image.new("RGBA", icone.size, (0, 0, 0, 0))
        camada.putalpha(m)
        out.alpha_composite(camada, (dx, dy))
    out.alpha_composite(icone)
    return out


def quadros(pasta: Path, dur: float) -> None:
    n = int(round(dur * FPS))
    ent, sai = 0.25, 0.20
    for i in range(n):
        t = i / FPS
        if t < ent:
            esc = max(0.0, ease_out_back(t / ent))
            alfa = min(1.0, t / (ent * 0.6))
        elif t > dur - sai:
            x = (t - (dur - sai)) / sai
            esc, alfa = 1 - x ** 2, 1 - x
        else:
            esc, alfa = 1.0, 1.0
        # balanço a cada tique (some rápido)
        k = int((t - 0.05) // TIQUE) if t >= 0.05 else -1
        dt = t - 0.05 - k * TIQUE if k >= 0 else 9
        balanco = (5.0 if k % 2 == 0 else -5.0) * math.exp(-dt / 0.06) if k >= 0 else 0.0
        icone = desenhar(min(1.0, t / (dur - sai)), 360 * t / VOLTA)
        icone = com_sombra(icone)
        if esc <= 0.01 or alfa <= 0.01:
            Image.new("RGBA", (TAM, TAM), (0, 0, 0, 0)).save(pasta / f"f_{i:04d}.png")
            continue
        lado = max(1, int(TAM * esc))
        q = icone.rotate(balanco, resample=Image.BICUBIC, center=(CX, CY)).resize((lado, lado), Image.LANCZOS)
        if alfa < 1:
            q.putalpha(q.split()[3].point(lambda v: int(v * alfa)))
        f = Image.new("RGBA", (TAM, TAM), (0, 0, 0, 0))
        # escala em volta do centro do mostrador
        ox, oy = int(CX - CX * esc), int(CY - CY * esc)
        f.alpha_composite(q, (ox, oy))
        f.save(pasta / f"f_{i:04d}.png")
    print(f"ok: {n} quadros")


def tique(sr: int, agudo: bool, rng) -> np.ndarray:
    n = int(0.09 * sr)
    t = np.arange(n) / sr
    f = 3300.0 if agudo else 2350.0
    ruido = rng.standard_normal(n) * np.exp(-t / 0.0035)
    espectro = np.fft.rfft(ruido)
    fr = np.fft.rfftfreq(n, 1 / sr)
    espectro *= np.exp(-((fr - f) / 1400.0) ** 2) + 0.15
    ruido = np.fft.irfft(espectro, n)
    corpo = (np.sin(2 * np.pi * f * t) * np.exp(-t / 0.010)
             + 0.45 * np.sin(2 * np.pi * (f * 1.52) * t) * np.exp(-t / 0.006)
             + 0.35 * np.sin(2 * np.pi * (780 if agudo else 620) * t) * np.exp(-t / 0.018))
    x = 0.8 * ruido / (np.abs(ruido).max() + 1e-9) + 0.6 * corpo
    sala = rng.standard_normal(int(0.012 * sr)) * np.exp(-np.arange(int(0.012 * sr)) / (0.003 * sr))
    x = np.convolve(x, np.r_[1.0, 0.18 * sala / np.abs(sala).max()])[:n]
    return x / np.abs(x).max()


def audio(pasta: Path, dur: float) -> None:
    sr = 48000
    rng = np.random.default_rng(7)
    y = np.zeros(int((dur + 0.2) * sr))
    k, t0 = 0, 0.05
    while t0 < dur - 0.15:
        s = tique(sr, k % 2 == 0, rng) * (0.55 if k % 2 == 0 else 0.48)
        i = int(t0 * sr)
        y[i:i + len(s)] += s[: len(y) - i]
        k += 1
        t0 += TIQUE
    y = np.clip(y, -1, 1)
    est = np.stack([y, y], 1)
    with wave.open(str(pasta / "tique_taque.wav"), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((est * 32767).astype("<i2").tobytes())
    print(f"ok: {k} tiques")


if __name__ == "__main__":
    pasta = Path(sys.argv[1])
    pasta.mkdir(parents=True, exist_ok=True)
    dur = float(sys.argv[2])
    quadros(pasta, dur)
    audio(pasta, dur)
