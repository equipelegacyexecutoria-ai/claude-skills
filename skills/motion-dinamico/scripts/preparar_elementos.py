# Prepara os elementos baixados do Freepik (PNG sem fundo) para o Motion Dinâmico:
# corta a sobra transparente, reduz (lado maior 1500), põe borda branca de adesivo e salva com nome curto.
# Também gera uma grade (linhas a cada 100 px) de cada imagem para marcar pescoço/pivô dos bonecos.
# uso: python preparar_elementos.py <pasta_baixados> <projeto> mapa.json
#   mapa.json = {"cerebro": "human-brain-....png", "laibson": "laibson.jpg", ...}  (JPG = foto: só reduz, sem borda)
import json, os, sys
import numpy as np, cv2
from PIL import Image, ImageDraw

SRC, PROJ, MAPA = sys.argv[1], sys.argv[2], json.load(open(sys.argv[3], encoding="utf-8"))
DST = os.path.join(PROJ, "assets", "img"); GRADE = os.path.join(PROJ, "grade")
os.makedirs(DST, exist_ok=True); os.makedirs(GRADE, exist_ok=True)
B, PAD = 9, 12
for nome, f in MAPA.items():
    im = Image.open(os.path.join(SRC, f))
    if f.lower().endswith((".jpg", ".jpeg")):
        im = im.convert("RGB"); s = min(1.0, 1500 / max(im.size))
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS) if s < 1 else im
        im.save(os.path.join(DST, nome + ".jpg"), quality=92); print(nome, im.size, "foto"); continue
    im = im.convert("RGBA")
    im = im.crop(im.getchannel("A").point(lambda v: 255 if v > 10 else 0).getbbox())
    s = min(1.0, 1500 / max(im.size))
    if s < 1:
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    a = np.pad(np.array(im), ((PAD, PAD), (PAD, PAD), (0, 0)))
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * B + 1, 2 * B + 1))
    da = cv2.GaussianBlur(cv2.dilate((a[..., 3] > 60).astype(np.uint8) * 255, k), (0, 0), 1.2)
    papel = np.zeros_like(a); papel[..., :3] = 255; papel[..., 3] = da
    out = Image.alpha_composite(Image.fromarray(papel), Image.fromarray(a))
    out.save(os.path.join(DST, nome + ".png"), optimize=True)
    g = Image.new("RGBA", out.size, (110, 110, 110, 255)); g.alpha_composite(out); d = ImageDraw.Draw(g)
    for x in range(0, out.width, 100):
        d.line([(x, 0), (x, out.height)], fill=(255, 0, 0, 255) if x % 500 == 0 else (255, 255, 0, 150), width=2 if x % 500 == 0 else 1)
    for y in range(0, out.height, 100):
        d.line([(0, y), (out.width, y)], fill=(255, 0, 0, 255) if y % 500 == 0 else (255, 255, 0, 150), width=2 if y % 500 == 0 else 1)
    g.convert("RGB").save(os.path.join(GRADE, nome + ".jpg"), quality=80)
    print(nome, out.size)
