"""Recorta o busto do Clailton de um candidato de thumb (thumbs/epNN_candidatos.json) no quadro cheio da aula.
Uso: python busto.py <trabalho> <aula.mp4> <ep> <t_aula_em_segundos> <saida.png>"""
import json, subprocess, sys
from pathlib import Path
from PIL import Image
trab, aula, ep, t, saida = Path(sys.argv[1]), sys.argv[2], int(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
cands = json.load(open(trab / "thumbs" / f"ep{ep:02d}_candidatos.json", encoding="utf-8"))
c = min(cands, key=lambda c: abs(c["t"] - t))
x, y, w, h = c["rosto"]
q = Path(saida).with_suffix(".quadro.png")
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", str(c["t"]), "-i", aula, "-frames:v", "1", "-y", str(q)], check=True)
im = Image.open(q)
W, H = im.size
bw, bh = int(h * 3.6), int(h * 3.03)
cx = x + w / 2
l = int(max(0, min(W - bw, cx - bw / 2))); top = int(max(0, y - 0.64 * h))
bh = min(bh, H - top)
im.crop((l, top, l + bw, top + bh)).save(saida)
print(saida, c["t"], (l, top, bw, bh))
