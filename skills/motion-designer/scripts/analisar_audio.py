"""Analisa música ou efeitos para encaixar o vídeo na batida.

Música:  python analisar_audio.py musica.wav [--de 20 --ate 70]
  -> BPM, batidas no trecho, energia (RMS) a cada 0,5 s e as viradas (saltos fortes de energia).
Efeitos: python analisar_audio.py --picos efeito1.wav efeito2.wav ...
  -> duração, início do som e onde está o pico de cada efeito (para posicionar pelo pico).
"""
import argparse
import numpy as np
import librosa

p = argparse.ArgumentParser()
p.add_argument("arquivos", nargs="+")
p.add_argument("--picos", action="store_true")
p.add_argument("--de", type=float, default=0)
p.add_argument("--ate", type=float, default=None)
a = p.parse_args()

if a.picos:
    for f in a.arquivos:
        y, sr = librosa.load(f, sr=22050, mono=True)
        r = librosa.feature.rms(y=y, hop_length=220)[0]
        t = np.arange(len(r)) * 220 / sr
        print(f"{f}: duração {len(y)/sr:.2f}s | início {t[np.argmax(r > r.max()*0.2)]:.2f}s | pico {t[np.argmax(r)]:.2f}s")
else:
    f = a.arquivos[0]
    y, sr = librosa.load(f, sr=22050, mono=True)
    dur = len(y) / sr
    oe = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, b = librosa.beat.beat_track(onset_envelope=oe, sr=sr)
    bt = librosa.frames_to_time(b, sr=sr)
    ate = a.ate or dur
    print(f"duração {dur:.1f}s | BPM ~{float(np.atleast_1d(tempo)[0]):.1f}")
    print("batidas:", [round(float(x), 3) for x in bt if a.de <= x <= ate])
    hop = sr // 2
    r = librosa.feature.rms(y=y, hop_length=hop)[0]
    print("energia a cada 0,5 s (a partir de 0):", " ".join(f"{v:.2f}" for v in r))
    d = np.diff(r)
    viradas = [(i + 1) * 0.5 for i in np.argsort(d)[::-1][:8]]
    print("maiores viradas (s):", sorted(round(v, 1) for v in viradas if a.de <= v <= ate))
