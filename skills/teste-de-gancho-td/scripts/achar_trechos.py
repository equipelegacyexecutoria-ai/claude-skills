"""Acha no bruto trechos bons para a sincronia da boca: rosto sempre visível e firme, olhando para a câmera
(de frente) e FALANDO desde o 1º quadro (com ele calado a boca quase não mexe; virando o rosto, a 1ª palavra
"parece IA" — lições de 10–11/10/2026).

Uso: python achar_trechos.py <bruto> <saida.json> <dur1> [<dur2> ...]
     GIRAR=auto|1|0 (padrão auto: bruto deitado, mais largo que alto, é desvirado com transpose=1)
     N_TRECHOS=3  FALA_MIN=0.8
Devolve, para cada duração, os N melhores inícios (s) sem sobreposição: [nota, início] (nota menor = melhor).
"""
import json, os, subprocess, sys
from pathlib import Path

import cv2, numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from comum import MOD  # noqa: E402


def girar(bruto):
    g = os.environ.get("GIRAR", "auto")
    if g != "auto":
        return g == "1"
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                        "-of", "csv=p=0", bruto], capture_output=True, text=True).stdout.strip().split(",")
    return int(r[0]) > int(r[1])


bruto, saida, durs = sys.argv[1], sys.argv[2], [float(x) for x in sys.argv[3:]]
W, H, FPS = 540, 960, 10
vf = f"fps={FPS}," + ("transpose=1," if girar(bruto) else "") + \
     f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", bruto, "-vf", vf, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                     stdout=subprocess.PIPE)
det = cv2.FaceDetectorYN.create(MOD, "", (W, H), 0.5, 0.3, 5000)
regs = []
while True:
    buf = p.stdout.read(W * H * 3)
    if len(buf) < W * H * 3:
        break
    fr = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    _, f = det.detect(fr)
    if f is not None and len(f):
        f = max(f, key=lambda r: r[2] * r[3])
        meio_olhos = (f[4] + f[6]) / 2
        dist_olhos = abs(f[6] - f[4]) + 1e-6
        frente = abs(f[8] - meio_olhos) / dist_olhos      # nariz fora do meio dos olhos = rosto virado
        regs.append((float(f[14]), meio_olhos, (f[5] + f[7]) / 2, float(f[2]), float(frente)))
    else:
        regs.append((0.0, 0, 0, 0, 1.0))
conf, ex, ey, larg, frente = (np.array([r[k] for r in regs]) for k in range(5))
# fala: energia da voz a 10 q/s
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", bruto, "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                     capture_output=True).stdout
au = np.frombuffer(raw, np.int16).astype(float) / 32768
db = np.array([20 * np.log10(np.sqrt((au[i * 1600:(i + 1) * 1600] ** 2).mean()) + 1e-9) for i in range(len(regs))])
fala = db > (np.percentile(db, 90) - 18)
FALA_MIN = float(os.environ.get("FALA_MIN", "0.8"))
N = int(os.environ.get("N_TRECHOS", "3"))
res = {}
for d in durs:
    n = int(d * FPS) + 2
    cands = []
    for i in range(0, len(regs) - n):
        if conf[i:i + n].min() < 0.85 or fala[i:i + n].mean() < FALA_MIN or not fala[i:i + 3].all():
            continue
        mov = float(np.std(ex[i:i + n]) + np.std(ey[i:i + n]) + 0.5 * np.std(larg[i:i + n]))
        nota = mov + 30 * float(frente[i:i + n].mean()) + 60 * float(frente[i:i + 5].mean())
        cands.append((nota, i / FPS))
    cands.sort()
    esc = []
    for nota, t in cands:
        if all(abs(t - u) > d + 1 for _, u in esc):
            esc.append((round(nota, 1), round(t, 2)))
        if len(esc) == N:
            break
    res[str(d)] = esc
    print(d, esc if esc else "nenhum trecho: tente FALA_MIN=0.6")
json.dump(res, open(saida, "w"), indent=1)
