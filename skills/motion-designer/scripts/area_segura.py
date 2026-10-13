"""Pinta sobre os snapshots as zonas cobertas pela interface da rede (vermelho) e as margens (amarelo)
e monta uma folha para conferir se nada importante ficou fora da área segura.

Uso: python area_segura.py --formato 9x16 [--pasta <pasta dos frame-*.png>] [--saida area-segura.jpg]
Sem --pasta, usa o snapshot mais recente do projeto (rodar de dentro da pasta do projeto).
Formatos: 9x16 (Reels/Stories/TikTok/Shorts), 4x5, 1x1, 16x9 (YouTube).
"""
import argparse, glob, os
from PIL import Image, ImageDraw, ImageFont

p = argparse.ArgumentParser()
p.add_argument("--formato", default="9x16", choices=["9x16", "4x5", "1x1", "16x9"])
p.add_argument("--pasta", default=None, help="padrão: snapshot mais recente do projeto atual")
p.add_argument("--saida", default=None)
a = p.parse_args()

if not a.pasta:
    # CLI novo grava em .hyperframes/artifacts/snapshots/<id>/; o antigo, em snapshots/
    novas = glob.glob(os.path.join(".hyperframes", "artifacts", "snapshots", "*", ""))
    a.pasta = max(novas, key=os.path.getmtime) if novas else "snapshots"

# zonas na resolução de referência de cada formato; escaladas para o tamanho real do snapshot
REF = {
    "9x16": ((1080, 1920), [(0, 0, 1080, 220), (950, 1000, 1080, 1720), (0, 1480, 1080, 1920)], 80),
    "4x5": ((1080, 1350), [], 80),
    "1x1": ((1080, 1080), [], 80),
    "16x9": ((1920, 1080), [(0, 960, 1920, 1080)], 96),
}
(rw, rh), zonas, margem = REF[a.formato]
try:
    fonte = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 44)
except OSError:
    fonte = ImageFont.load_default()

quadros = []
for f in sorted(glob.glob(os.path.join(a.pasta, "frame-*.png"))):
    im = Image.open(f).convert("RGBA")
    sx, sy = im.width / rw, im.height / rh
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for x0, y0, x1, y1 in zonas:
        d.rectangle((x0 * sx, y0 * sy, x1 * sx, y1 * sy), fill=(255, 0, 0, 70))
    for x in (margem * sx, im.width - margem * sx):
        d.line([(x, 0), (x, im.height)], fill=(255, 210, 0, 200), width=3)
    t = os.path.basename(f).split("-at-")[-1].replace(".png", "")
    d.text((20, im.height - 80), t, fill=(255, 255, 255, 255), font=fonte, stroke_width=3, stroke_fill=(0, 0, 0, 255))
    w = 360 if rh >= rw else 480
    quadros.append(Image.alpha_composite(im, ov).convert("RGB").resize((w, int(w * im.height / im.width))))

if not quadros:
    raise SystemExit("nenhum frame-*.png em " + a.pasta)
cols = 6 if rh >= rw else 4
qw, qh = quadros[0].size
linhas = (len(quadros) + cols - 1) // cols
folha = Image.new("RGB", (qw * cols, qh * linhas), "white")
for i, q in enumerate(quadros):
    folha.paste(q, ((i % cols) * qw, (i // cols) * qh))
saida = a.saida or os.path.join(a.pasta, "area-segura.jpg")
folha.save(saida, quality=88)
print(saida, len(quadros))
