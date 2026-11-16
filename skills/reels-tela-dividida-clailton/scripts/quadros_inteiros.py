"""uso: python quadros_inteiros.py <trabalho> b03,b13,... <saida.jpg>  — quadro inteiro de cada cena escolhida (10/50/90%% do trecho) com régua x 0-100, para decidir o recorte do recorte_manual.py."""
"""Folha com o quadro INTEIRO (16:9) de cada cena escolhida, em 3 momentos do trecho usado, com régua de x (0-100%)."""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
T = Path(sys.argv[1]); ids = sys.argv[2].split(',')
esc = json.load(open(T / 'midia' / 'escolhas.json', encoding='utf-8'))
tl = json.load(open(T / 'timeline.json', encoding='utf-8'))
itens = {i['id']: i for i in tl.get('itens', tl.get('imagens', []))} if isinstance(tl, dict) else {}
f = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 18)
linhas = []
for i in ids:
    e = esc[i]; arq = e['arquivo']; ent = float(e.get('entrada') or 0)
    it = itens.get(i, {}); dur = (it.get('fim', 0) - it.get('inicio', 0)) if it else 2.5
    dur = dur if dur > 0 else 2.5
    fr = []
    for k in (0.1, 0.5, 0.9):
        t = ent + dur * k
        r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.2f}', '-i', arq, '-frames:v', '1', '-vf', 'scale=480:-2', '-f', 'image2pipe', '-c:v', 'png', '-'], capture_output=True)
        try:
            import io; im = Image.open(io.BytesIO(r.stdout)).convert('RGB')
        except Exception:
            im = Image.new('RGB', (480, 270), (60, 0, 0))
        d = ImageDraw.Draw(im)
        for x in range(0, 101, 10):
            X = int(x / 100 * (im.width - 1)); d.line([(X, 0), (X, 8)], fill=(255, 255, 0), width=2); d.text((X + 2, 8), str(x), font=f, fill=(255, 255, 0))
        d.text((4, im.height - 24), f'{i} t={t:.1f}', font=f, fill=(0, 255, 255))
        fr.append(im)
    w = sum(x.width for x in fr); h = max(x.height for x in fr)
    row = Image.new('RGB', (w, h)); xx = 0
    for x in fr: row.paste(x, (xx, 0)); xx += x.width
    linhas.append(row)
W = max(r.width for r in linhas); H = sum(r.height for r in linhas)
out = Image.new('RGB', (W, H)); y = 0
for r in linhas: out.paste(r, (0, y)); y += r.height
out.save(sys.argv[3], quality=85); print('ok', sys.argv[3])
for i in ids: print(i, esc[i]['arquivo'], esc[i].get('entrada'), esc[i].get('midia'))

