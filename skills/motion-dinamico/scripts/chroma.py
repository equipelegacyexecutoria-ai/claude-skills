# Recorta ilustrações geradas sobre fundo verde (#00FF00) do Google Flow.
# uso: python chroma.py <imagem.jpg> <saida_prefixo> [--separar] [--enquadrar]
#   --separar: cada objeto solto vira um PNG (<prefixo>_1.png, _2.png..., da esquerda para a direita, de cima para baixo)
#   --enquadrar: em vez disso, salva a imagem inteira cortada para 1080x1920 (mesmo enquadramento do separar_personagem.py)
import sys
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

src, pref = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGB")
a = np.asarray(im).astype(np.float32)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
verde = g - np.maximum(r, b)              # quanto o pixel é "mais verde"
alpha = np.clip(1 - (verde - 40) / 80, 0, 1)  # >120 = fundo, <40 = objeto
m = alpha > 0.5
m = ndimage.binary_opening(m, iterations=2)
m = ndimage.binary_fill_holes(m)
alpha = np.where(m, alpha, 0)
# tira o verde que "vaza" na borda
lim = np.maximum(r, b)
a[..., 1] = np.where(g > lim, lim + (g - lim) * 0.15, g)
rgba = np.dstack([a, alpha * 255]).astype(np.uint8)
out = Image.fromarray(rgba, "RGBA")
out.putalpha(Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)))

if "--enquadrar" in sys.argv:
    W, H = out.size; s = max(1080 / W, 1920 / H)
    o = out.resize((round(W * s), round(H * s)), Image.LANCZOS)
    x, y = (o.width - 1080) // 2, (o.height - 1920) // 2
    o.crop((x, y, x + 1080, y + 1920)).save(pref + ".png")
    print(pref + ".png")
else:
    lab, n = ndimage.label(m)
    tam = ndimage.sum(m, lab, range(1, n + 1))
    objs = []
    for i, t in enumerate(tam):
        if t < 3000:
            continue
        ys, xs = np.where(lab == i + 1)
        objs.append((ys.min(), xs.min(), ys.max(), xs.max(), i + 1))
    objs.sort(key=lambda o: (o[0] // 400, o[1]))
    for k, (y0, x0, y1, x1, i) in enumerate(objs, 1):
        so = np.where(lab == i, 255, 0).astype(np.uint8)
        peca = out.copy(); peca.putalpha(Image.fromarray(np.minimum(so, np.asarray(out.getchannel("A")))))
        peca.crop((x0, y0, x1 + 1, y1 + 1)).save(f"{pref}_{k}.png")
        print(f"{pref}_{k}.png", x1 - x0 + 1, y1 - y0 + 1)
