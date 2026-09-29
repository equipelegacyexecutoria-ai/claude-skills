"""Enxergar a onda sonora do corte: lista cada silêncio (emenda ou pausa dentro da frase) e desenha a
forma de onda + espectro em volta dele, com as emendas marcadas (pedido do usuário, 28/09/2026: "cortes
certeiros, sem espacinho em branco, sem cortar a voz").

Voz = envelope de 5 ms no áudio ORIGINAL (48 kHz) acima do limiar da tomada; o espectro (0-8 kHz)
mostra o "s"/"x" final (chiado agudo), que tem pouca energia mas é voz.

Uso: python ondas.py <trabalho> [--min 0.10] [--folha N]
Saída: qa/ondas.txt (todos os silêncios >= --min, em ordem) e qa/ondas_NN.jpg (os N maiores).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import FPS, ler_json  # noqa: E402

SR = 48000
HOP = 0.005


def audio48(T: Path, fonte: str) -> np.ndarray:
    arq = T / "audio48k.wav"
    if not arq.exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", fonte, "-map", "0:a:0", "-ac", "1", "-ar", str(SR),
                        "-c:a", "pcm_s16le", str(arq)], check=True)
    with wave.open(str(arq), "rb") as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768


def envelope(x: np.ndarray) -> np.ndarray:
    """dB por janela de 10 ms a cada 5 ms."""
    h, win = int(SR * HOP), int(SR * 0.010)
    n = max(1, (len(x) - win) // h)
    idx = np.arange(n)[:, None] * h + np.arange(win)[None, :]
    return 20 * np.log10(np.sqrt((x[idx] ** 2).mean(axis=1)) + 1e-9)


def agudo(x: np.ndarray) -> np.ndarray:
    """Envelope (dB) só do agudo (> ~3 kHz, diferença de 1ª ordem duas vezes): pega o "s" final."""
    y = np.diff(np.diff(x, prepend=0), prepend=0)
    return envelope(y)


def montar(T: Path) -> tuple[np.ndarray, list[float]]:
    corte = ler_json(T / "corte.json")
    x = audio48(T, corte["fonte"])
    partes, emendas, t = [], [], 0.0
    for k, s in enumerate(corte["segmentos"]):
        a = int(round(s["frame_in"] / FPS * SR))
        n = int(round(s["frames"] / FPS * SR))
        partes.append(x[a:a + n])
        if k:
            emendas.append(t)
        t += n / SR
    return np.concatenate(partes), emendas


def silencios(env: np.ndarray, hf: np.ndarray, minimo: float, ag: np.ndarray | None = None,
              ref: tuple | None = None) -> tuple[list[tuple[float, float]], float]:
    """Silêncio de VERDADE: fora da voz e fora da onda fraca da própria palavra (decaimento, "s" solto,
    preparação do ataque — o que o usuário circulou em amarelo em 29/09/2026). Mesmos limiares do
    borda_voz.py (ref = piso, lim, lim_hf do bruto)."""
    if ref:
        piso, lim, lim_hf = ref
    else:
        piso, alto = float(np.percentile(env, 10)), float(np.percentile(env, 95))
        lim, lim_hf = max(piso + 9, alto - 26), float(np.percentile(hf, 10)) + 18
    voz = (env >= lim) | (hf >= lim_hf)
    fraco = env >= piso + 16
    if ag is not None:
        fraco |= (ag >= 0.35) & (env >= piso + 10)
    # a onda fraca encostada na voz (buraco <= 80 ms) é palavra
    marca = voz.copy()
    for passo in (1, -1):
        rng = range(len(voz)) if passo == 1 else range(len(voz) - 1, -1, -1)
        dentro, buraco = False, 0
        for i in rng:
            if voz[i]:
                dentro, buraco = True, 0
            elif dentro and fraco[i]:
                marca[i], buraco = True, 0
            elif dentro:
                buraco += 1
                if buraco > 16:
                    dentro = False
    out, k = [], 0
    while k < len(marca):
        if marca[k]:
            k += 1
            continue
        a = k
        while k < len(marca) and not marca[k]:
            k += 1
        if (k - a) * HOP >= minimo and a > 0 and k < len(marca):
            out.append((a * HOP, k * HOP))
    return out, lim


def folha(x: np.ndarray, sil: list, emendas: list[float], destino: Path, titulo: str) -> None:
    w_, h_ = 520, 230
    cols = 2
    rows = (len(sil) + cols - 1) // cols
    img = Image.new("RGB", (cols * w_, rows * h_), (18, 18, 18))
    d = ImageDraw.Draw(img)
    for i, (a, b) in enumerate(sil):
        c, r = i % cols, i // cols
        x0, y0 = c * w_, r * h_
        t0, t1 = max(0.0, a - 0.35), min(len(x) / SR, b + 0.35)
        seg = x[int(t0 * SR):int(t1 * SR)]
        # espectro 0-8 kHz (em cima) e onda (embaixo)
        nfft, hop = 512, 240
        if len(seg) > nfft:
            fr = np.lib.stride_tricks.sliding_window_view(seg, nfft)[::hop] * np.hanning(nfft)
            sp = 20 * np.log10(np.abs(np.fft.rfft(fr, axis=1))[:, :86] + 1e-6).T[::-1]
            sp = np.clip((sp - sp.max() + 70) / 70, 0, 1)
            im = Image.fromarray((sp * 255).astype(np.uint8)).resize((w_ - 10, 80))
            img.paste(Image.merge("RGB", (im, im.point(lambda v: v * 0.6), im.point(lambda v: v * 0.2))), (x0 + 5, y0 + 22))
        n = w_ - 10
        pts = np.array_split(seg, n)
        mid, amp = y0 + 160, 55
        for j, p in enumerate(pts):
            if len(p):
                d.line([(x0 + 5 + j, mid - p.max() * amp * 3), (x0 + 5 + j, mid - p.min() * amp * 3)], fill=(90, 200, 255))

        def px(t: float) -> float:
            return x0 + 5 + (t - t0) / (t1 - t0) * n
        d.rectangle([px(a), y0 + 104, px(b), y0 + 216], outline=(255, 210, 0))
        for e in emendas:
            if t0 <= e <= t1:
                d.line([(px(e), y0 + 20), (px(e), y0 + 222)], fill=(255, 50, 50), width=2)
        tipo = "EMENDA" if any(a - 0.02 <= e <= b + 0.02 for e in emendas) else "dentro da frase"
        d.text((x0 + 6, y0 + 4), f"{a:.2f}s  silêncio {b - a:.2f}s  ({tipo})", fill=(255, 255, 255))
    d.text((6, rows * h_ - 14), titulo, fill=(160, 160, 160))
    img.save(destino, quality=88)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("trabalho")
    ap.add_argument("--min", type=float, default=0.10)
    ap.add_argument("--folha", type=int, default=12)
    a = ap.parse_args()
    T = Path(a.trabalho)
    x, emendas = montar(T)
    env, hf = envelope(x), agudo(x)
    from borda_voz import VozFina, _agudo
    vf = VozFina(T, ler_json(T / "corte.json")["fonte"])
    sil, lim = silencios(env, hf, a.min, _agudo(x, len(env)), (vf.piso, vf.lim, vf.lim_hf))
    (T / "qa").mkdir(exist_ok=True)
    linhas = [f"# {len(sil)} silêncios >= {a.min:.2f}s (limiar de voz {lim:.0f} dB); vermelho = emenda"]
    for s0, s1 in sil:
        tipo = "EMENDA" if any(s0 - 0.02 <= e <= s1 + 0.02 for e in emendas) else "frase"
        linhas.append(f"{s0:7.2f}s  {s1 - s0:.2f}s  {tipo}")
    (T / "qa" / "ondas.txt").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    maiores = sorted(sorted(sil, key=lambda s: s[0] - s[1])[:a.folha])
    if maiores:
        folha(x, maiores, emendas, T / "qa" / "ondas_01.jpg", f"{len(maiores)} maiores silêncios")
    tot = sum(s1 - s0 for s0, s1 in sil)
    print(f"{len(sil)} silêncios >= {a.min:.2f}s, somando {tot:.1f}s de {len(x) / SR:.1f}s; "
          f"{sum(1 for s in sil if s[1] - s[0] >= 0.2)} com >= 0,20s -> {T / 'qa' / 'ondas_01.jpg'}")
    print(json.dumps([round(s1 - s0, 2) for s0, s1 in sil]))


if __name__ == "__main__":
    main()
