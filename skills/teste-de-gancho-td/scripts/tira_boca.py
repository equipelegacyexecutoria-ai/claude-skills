"""Confere a sincronia da boca: tira com a boca ampliada em 10 pontos de cada resultado (ls/<nome>.mp4) e
quanto a boca mudou em relação ao trecho real (fontes/<nome>.mp4). Boca que quase não mexe ou rosto virando
na 1ª palavra = refazer com outro trecho do bruto.

Uso: python tira_boca.py <W> <nome> [<nome> ...]  -> <W>/ls/bocas.jpg (uma linha por nome)
"""
import sys
from pathlib import Path

import cv2, numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from comum import MOD  # noqa: E402

R, nomes = Path(sys.argv[1]), sys.argv[2:]
linhas = []
for n in nomes:
    a, b = cv2.VideoCapture(str(R / f"ls/{n}.mp4")), cv2.VideoCapture(str(R / f"fontes/{n}.mp4"))
    tot = int(a.get(cv2.CAP_PROP_FRAME_COUNT))
    det = cv2.FaceDetectorYN.create(MOD, "", (int(a.get(3)), int(a.get(4))), 0.6, 0.3, 5000)
    alvos = set(np.linspace(2, max(3, tot - 3), 10).astype(int))
    crops, difs, i = [], [], 0
    while True:
        oa, fa = a.read()
        ob, fb = b.read()
        if not oa:
            break
        if i in alvos:
            _, f = det.detect(fa)
            if f is not None and len(f):
                f = max(f, key=lambda r: r[2] * r[3])
                mx, my, w = int((f[10] + f[12]) / 2), int((f[11] + f[13]) / 2), int(f[2] * 0.6)
                ca = fa[my - w // 2:my + w // 3, mx - w // 2:mx + w // 2]
                crops.append(cv2.resize(ca, (160, 112)))
                if ob:
                    cb = fb[my - w // 2:my + w // 3, mx - w // 2:mx + w // 2]
                    difs.append(np.abs(ca.astype(float) - cb.astype(float)).mean())
        i += 1
    linha = np.hstack(crops + [np.zeros((112, 160, 3), np.uint8)] * (10 - len(crops)))
    rot = np.zeros((112, 300, 3), np.uint8)
    cv2.putText(rot, n, (8, 45), 0, 0.8, (255, 255, 255), 2)
    cv2.putText(rot, f"mudanca {np.mean(difs) if difs else 0:.1f}", (8, 90), 0, 0.7, (0, 255, 255), 2)
    linhas.append(np.hstack([rot, linha]))
    print(f"{n:18s} mudança média na boca " + (f"{np.mean(difs):5.1f}" if difs else "  -  (sem fontes/" + n + ".mp4)") + f"  ({len(crops)} quadros com rosto)")
cv2.imwrite(str(R / "ls/bocas.jpg"), np.vstack(linhas))
print("conferir a olho:", R / "ls/bocas.jpg", "(a boca tem que abrir e fechar nas palavras desde o 1º quadro)")
