"""Acha no bruto (câmera deitada) trechos com o rosto sempre visível e firme, para a sincronia da boca.
Uso: python achar_trechos.py <bruto> <saida.json> <dur1> [<dur2> ...]
Lê o bruto a 10 q/s já desvirado (transpose=1) em 540x960; devolve, para cada duração, os 3 melhores
inícios (segundos) sem sobreposição: rosto detectado com confiança alta em todos os quadros e pouco movimento.
"""
import json, subprocess, sys
from pathlib import Path
import cv2, numpy as np

MOD = str(Path.home() / ".claude/skills/reels-novela-clailton/models/face_detection_yunet_2023mar.onnx")
bruto, saida, durs = sys.argv[1], sys.argv[2], [float(x) for x in sys.argv[3:]]
W, H, FPS = 540, 960, 10
p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", bruto, "-vf", f"fps={FPS},transpose=1,scale={W}:{H}",
                      "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
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
        regs.append((float(f[14]), (f[4] + f[6]) / 2, (f[5] + f[7]) / 2, float(f[2])))
    else:
        regs.append((0.0, 0, 0, 0))
conf = np.array([r[0] for r in regs]); ex = np.array([r[1] for r in regs]); ey = np.array([r[2] for r in regs])
larg = np.array([r[3] for r in regs])
# fala: energia da voz a 10 q/s (a sincronia da boca só anima bem quando ele está falando no trecho)
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", bruto, "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                     capture_output=True).stdout
au = np.frombuffer(raw, np.int16).astype(float) / 32768
db = np.array([20 * np.log10(np.sqrt((au[i * 1600:(i + 1) * 1600] ** 2).mean()) + 1e-9) for i in range(len(regs))])
fala = db > (np.percentile(db, 90) - 18)
res = {}
for d in durs:
    n = int(d * FPS) + 2
    cands = []
    for i in range(0, len(regs) - n):
        c = conf[i:i + n]
        if c.min() < 0.85 or fala[i:i + n].mean() < float(__import__("os").environ.get("FALA_MIN", "0.8")):
            continue
        mov = float(np.std(ex[i:i + n]) + np.std(ey[i:i + n]) + 0.5 * np.std(larg[i:i + n]))
        cands.append((mov, i / FPS))
    cands.sort()
    esc = []
    for mov, t in cands:
        if all(abs(t - u) > d + 1 for _, u in esc):
            esc.append((round(mov, 1), round(t, 2)))
        if len(esc) == int(__import__("os").environ.get("N_TRECHOS", "3")):
            break
    res[str(d)] = esc
    print(d, esc)
json.dump(res, open(saida, "w"), indent=1)
