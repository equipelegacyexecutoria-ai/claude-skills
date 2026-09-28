"""Identificação de locutor pela VOZ (só numpy): MFCC + GMM diagonal por pessoa.

Por que existe: no plano das duas convidadas, o movimento de boca engana (quem
escuta bebe água, olha em volta, sorri). A voz não engana. A imagem fica só para
LOCALIZAR o rosto; quem fala é decidido aqui.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

SR = 16000
N_FFT, HOP, WIN = 512, 160, 400          # 25 ms / 10 ms
N_MEL, N_MFCC = 32, 16

# trechos de treino: quem fala é inequívoco pelo conteúdo (e conferido)
TREINO = {
    "apresentador": [(5.0, 45.0), (56.5, 92.4), (3700.0, 3730.0)],
    "jane": [(93.8, 122.5), (396.7, 440.0)],
    "fernanda": [(596.4, 700.0)],
}
# validação: trechos diferentes, conferidos visualmente
TESTE = {
    "jane": [(1489.5, 1508.0), (2306.0, 2320.0)],
    "fernanda": [(1696.7, 1703.9)],
    "apresentador": [(4457.9, 4492.8)],
}


def audio(video: str, a: float, b: float) -> np.ndarray:
    p = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{a:.3f}", "-i", video, "-t", f"{b - a:.3f}",
                        "-vn", "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True)
    return np.frombuffer(p.stdout, np.int16).astype(np.float32) / 32768.0


def _mel_fb() -> np.ndarray:
    def hz2mel(h): return 2595 * np.log10(1 + h / 700)
    def mel2hz(m): return 700 * (10 ** (m / 2595) - 1)
    mels = np.linspace(hz2mel(80), hz2mel(7600), N_MEL + 2)
    bins = np.floor((N_FFT + 1) * mel2hz(mels) / SR).astype(int)
    fb = np.zeros((N_MEL, N_FFT // 2 + 1))
    for i in range(1, N_MEL + 1):
        l, c, r = bins[i - 1], bins[i], bins[i + 1]
        for k in range(l, c):
            fb[i - 1, k] = (k - l) / max(1, c - l)
        for k in range(c, r):
            fb[i - 1, k] = (r - k) / max(1, r - c)
    return fb


FB = _mel_fb()
DCT = np.cos(np.pi / N_MEL * (np.arange(N_MEL)[None, :] + 0.5) * np.arange(N_MFCC)[:, None])
WINDOW = np.hamming(WIN)


def mfcc(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Devolve (features [T, 2*(N_MFCC-1)], energia log [T])."""
    if x.size < WIN:
        return np.zeros((0, 2 * (N_MFCC - 1))), np.zeros(0)
    x = np.append(x[0], x[1:] - 0.97 * x[:-1])
    n = 1 + (x.size - WIN) // HOP
    idx = np.arange(WIN)[None, :] + HOP * np.arange(n)[:, None]
    frames = x[idx] * WINDOW
    spec = np.abs(np.fft.rfft(frames, N_FFT)) ** 2
    mel = np.log(spec @ FB.T + 1e-10)
    c = mel @ DCT.T                       # [T, N_MFCC]
    energy = c[:, 0].copy()
    c = c[:, 1:]                          # sem c0 (volume)
    d = np.zeros_like(c)
    d[2:-2] = (c[4:] - c[:-4] + 2 * (c[3:-1] - c[1:-3])) / 10.0
    return np.hstack([c, d]), energy       # 15 cepstrais + 15 deltas


def speech_frames(feat: np.ndarray, energy: np.ndarray) -> np.ndarray:
    if energy.size == 0:
        return feat
    thr = np.percentile(energy, 35)
    return feat[energy > thr]


class GMM:
    def __init__(self, k: int = 16, iters: int = 40, seed: int = 0):
        self.k, self.iters, self.rng = k, iters, np.random.default_rng(seed)

    def fit(self, X: np.ndarray) -> "GMM":
        n, d = X.shape
        self.mu = X[self.rng.choice(n, self.k, replace=False)]
        self.var = np.tile(X.var(0) + 1e-3, (self.k, 1))
        self.w = np.full(self.k, 1.0 / self.k)
        for _ in range(self.iters):
            ll = self._comp_ll(X)                        # [n, k]
            m = ll.max(1, keepdims=True)
            r = np.exp(ll - m)
            r /= r.sum(1, keepdims=True)
            nk = r.sum(0) + 1e-6
            self.w = nk / n
            self.mu = (r.T @ X) / nk[:, None]
            self.var = (r.T @ (X ** 2)) / nk[:, None] - self.mu ** 2 + 1e-3
        return self

    def _comp_ll(self, X: np.ndarray) -> np.ndarray:
        return (np.log(self.w)[None, :]
                - 0.5 * np.sum(np.log(2 * np.pi * self.var), 1)[None, :]
                - 0.5 * (((X[:, None, :] - self.mu[None]) ** 2) / self.var[None]).sum(2))

    def score(self, X: np.ndarray) -> float:
        ll = self._comp_ll(X)
        m = ll.max(1, keepdims=True)
        return float(np.mean(m[:, 0] + np.log(np.exp(ll - m).sum(1))))


class Voz:
    def __init__(self, video: str):
        self.video = video
        feats = {}
        for who, spans in TREINO.items():
            F = [speech_frames(*mfcc(audio(video, a, b))) for a, b in spans]
            feats[who] = np.vstack(F)
        allf = np.vstack(list(feats.values()))
        self.mean, self.std = allf.mean(0), allf.std(0) + 1e-6
        self.models = {w: GMM().fit((f - self.mean) / self.std) for w, f in feats.items()}

    def scores(self, a: float, b: float) -> dict[str, float]:
        f = speech_frames(*mfcc(audio(self.video, a, b)))
        if len(f) < 20:
            return {}
        f = (f - self.mean) / self.std
        return {w: m.score(f) for w, m in self.models.items()}

    def load(self, a: float, b: float) -> np.ndarray:
        return audio(self.video, a, b)

    def who_buf(self, buf: np.ndarray, t0: float, a: float, b: float) -> tuple[str | None, float]:
        """Como who(), mas fatiando um áudio já decodificado a partir de t0."""
        x = buf[int((a - t0) * SR): int((b - t0) * SR)]
        f = speech_frames(*mfcc(x))
        if len(f) < 20:
            return None, 0.0
        f = (f - self.mean) / self.std
        s = sorted(((m.score(f), w) for w, m in self.models.items()), reverse=True)
        return s[0][1], s[0][0] - s[1][0]

    def who(self, a: float, b: float) -> tuple[str | None, float, dict]:
        s = self.scores(a, b)
        if not s:
            return None, 0.0, s
        order = sorted(s.items(), key=lambda kv: kv[1], reverse=True)
        return order[0][0], order[0][1] - order[1][1], s


def phrases(words, a, b, gap=0.25):
    ws = [w for w in words if w["end"] > a and w["start"] < b]
    out, cur = [], []
    for w in ws:
        if cur and w["start"] - cur[-1]["end"] > gap:
            out.append(cur); cur = []
        cur.append(w)
    if cur:
        out.append(cur)
    return [(max(a, p[0]["start"]), min(b, p[-1]["end"]), " ".join(x["word"] for x in p)) for p in out]


if __name__ == "__main__":
    video, transcript = sys.argv[1], sys.argv[2]
    v = Voz(video)
    tr = json.loads(Path(transcript).read_text(encoding="utf-8"))
    words = [w for s in tr["segments"] for w in s.get("words", [])]
    ok = tot = 0
    for truth, spans in TESTE.items():
        for a, b in spans:
            for pa, pb, txt in phrases(words, a, b):
                if pb - pa < 0.6:
                    continue
                w, marg, _ = v.who(pa, pb)
                tot += 1
                ok += (w == truth)
                if w != truth:
                    print(f"  ERRO {pa:.1f}-{pb:.1f} verdade={truth} previsto={w} margem={marg:.2f} | {txt[:60]}")
    print(f"validação por frase (>=0,6s): {ok}/{tot} = {ok / max(1, tot):.1%}")
