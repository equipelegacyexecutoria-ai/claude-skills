"""Borda EXATA da voz no áudio original (48 kHz, envelope de 5 ms) — pedido do usuário (28/09/2026):
"cortes certeiros, no limite da onda, sem espacinho em branco e sem cortar a voz".

Voz = envelope de banda larga acima do limiar da gravação OU chiado agudo acima do piso (o "s"/"x" final
tem pouca energia mas é voz). A borda é estendida enquanto a onda ainda decai (histerese de 6 dB, até
80 ms), para não comer o fim da palavra. Respiro e ambiente ficam abaixo do limiar e saem.
Conferência visual: ondas.py (forma de onda + espectro de cada silêncio).
"""
from __future__ import annotations

import subprocess
import wave
from pathlib import Path

import numpy as np

SR = 48000
HOP = 0.005
EXTENSAO = 0.03          # s: quanto a borda pode crescer enquanto a onda ainda decai (histerese)
MIN_VOZ = 0.03           # s: menos que isso acima do limiar é estalo, não voz
TOM = 0.45               # periodicidade mínima de um quadro "com tom" (voz vibra; respiro não)
VOZ_TOM_MIN = 0.03       # s: um trecho precisa de pelo menos isso com tom para ser voz
COLADO = 0.03            # s: chiado sem tom a até isso de uma palavra é parte dela


def audio48(T: Path, fonte: str) -> np.ndarray:
    arq = T / "audio48k.wav"
    if not arq.exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", fonte, "-map", "0:a:0", "-ac", "1", "-ar", str(SR),
                        "-c:a", "pcm_s16le", str(arq)], check=True)
    with wave.open(str(arq), "rb") as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768


def _env(x: np.ndarray) -> np.ndarray:
    h, win = int(SR * HOP), int(SR * 0.010)
    n = max(1, (len(x) - win) // h)
    idx = np.arange(n)[:, None] * h + np.arange(win)[None, :]
    return 20 * np.log10(np.sqrt((x[idx] ** 2).mean(axis=1)) + 1e-9)


def _vozeado(x: np.ndarray, n: int) -> np.ndarray:
    """Periodicidade (0..1) a cada 5 ms: pico da autocorrelação normalizada entre 70 e 450 Hz, janela de
    30 ms, a 16 kHz. Voz vibra (tem tom); respiro, estalo de boca e ruído de sala não."""
    y = np.convolve(x, np.ones(3, np.float32) / 3, mode="same")[::3].astype(np.float32)   # 48 -> 16 kHz
    h, win, nfft = 80, 480, 1024
    lo, hi = 16000 // 450, 16000 // 70
    out = np.zeros(n, np.float32)
    han = np.hanning(win).astype(np.float32)
    for c0 in range(0, n, 8000):
        c1 = min(n, c0 + 8000)
        idx = np.clip(np.arange(c0, c1)[:, None] * h + np.arange(win)[None, :], 0, len(y) - 1)
        fr = y[idx] * han
        fr -= fr.mean(axis=1, keepdims=True)
        r = np.fft.irfft(np.abs(np.fft.rfft(fr, nfft, axis=1)) ** 2, axis=1)
        out[c0:c1] = r[:, lo:hi].max(axis=1) / (r[:, 0] + 1e-9)
    return out


class VozFina:
    def __init__(self, T: Path, fonte: str):
        x = audio48(T, fonte)
        self.env = _env(x)
        arq = T / "vozeado.npy"
        tom = np.load(arq) if arq.exists() else None
        if tom is None or len(tom) != len(self.env):
            tom = _vozeado(x, len(self.env))
            np.save(arq, tom)
        self.tom = tom
        self.hf = _env(np.diff(np.diff(x, prepend=0), prepend=0))      # agudo (> ~3 kHz): "s", "x", "f"
        piso, alto = float(np.percentile(self.env, 10)), float(np.percentile(self.env, 95))
        self.piso = piso
        self.lim = max(piso + 9, alto - 26)                                   # pela VOZ: ruído de sala e respiro ficam em ~-49 dB (voz -14)
        self.lim_hf = float(np.percentile(self.hf, 10)) + 18                  # "s" final acima do chiado de fundo

    def regioes(self, t0: float, t1: float) -> list[tuple[float, float]]:
        """Trechos de voz (s do bruto) dentro de [t0, t1], com a borda estendida no decaimento."""
        a, b = max(0, int(t0 / HOP)), min(len(self.env), int(t1 / HOP))
        if b <= a:
            return []
        e, h = self.env[a:b], self.hf[a:b]
        voz = (e >= self.lim) | (h >= self.lim_hf)
        fraco = (e >= max(self.lim - 5, self.piso + 6)) | (h >= self.lim_hf - 3)
        ext = int(EXTENSAO / HOP)
        out, k = [], 0
        while k < len(voz):
            if not voz[k]:
                k += 1
                continue
            i = k
            while k < len(voz) and voz[k]:
                k += 1
            j = k
            if (j - i) * HOP < MIN_VOZ:
                continue
            ii = i
            while ii > 0 and i - ii < ext and fraco[ii - 1]:
                ii -= 1
            jj = j
            while jj < len(voz) and jj - j < ext and fraco[jj]:
                jj += 1
            forte = (e[ii:jj] >= self.lim).sum() * HOP >= MIN_VOZ          # volume de voz
            tom = (self.tom[a + ii:a + jj] >= TOM).sum() * HOP >= VOZ_TOM_MIN  # vibra
            out.append([(a + ii) * HOP, (a + jj) * HOP, forte or tom])
        # trecho só de chiado e sem tom (respiro, estalo de boca: -42 a -47 dB) sai, salvo se estiver colado
        # (<= COLADO) num trecho de voz: é o "s"/"x" da palavra (o "s" de "voltas")
        out = [r for r in out if r[2] or any(q[2] and (0 <= r[0] - q[1] <= COLADO or 0 <= q[0] - r[1] <= COLADO)
                                              for q in out)]
        fund = []
        for r in (r[:2] for r in out):
            if fund and r[0] <= fund[-1][1]:
                fund[-1][1] = max(fund[-1][1], r[1])
            else:
                fund.append(r)
        return [(round(p, 3), round(q, 3)) for p, q in fund]
