# Separa o personagem do cenário usando duas versões da mesma ilustração (gerada no Google Flow): a cena com o
# personagem e a "mesma cena sem ele" (fundo). O que muda entre as duas é o personagem: vira um PNG transparente.
# Também tira bordas/molduras da ilustração (o usuário não quer borda nas laterais) e enquadra em 1080x1920.
# uso: python separar_personagem.py <com.jpg> <sem.jpg> <saida_prefixo> [--limiar 34] [--fundo-so]
#   gera <prefixo>_fundo.jpg (1080x1920), <prefixo>_pers.png (1080x1920, transparente) e <prefixo>_check.jpg
import sys
import numpy as np
from PIL import Image, ImageChops, ImageFilter, ImageDraw

com, sem, pref = sys.argv[1], sys.argv[2], sys.argv[3]
LIM = int(sys.argv[sys.argv.index("--limiar") + 1]) if "--limiar" in sys.argv else 34
A = Image.open(com).convert("RGB")
B = Image.open(sem).convert("RGB").resize(A.size, Image.LANCZOS)


def miolo(im):
    """Caixa sem a moldura: corta linhas/colunas da borda que são quase uniformes (papel creme, filete)."""
    a = np.asarray(im.convert("L"), dtype=np.float32)
    H, W = a.shape
    def corta(perfil, n):
        i = 0
        while i < n * 0.12 and perfil[i] < 9:
            i += 1
        return i
    dl = np.abs(np.diff(a, axis=1)).mean(0)  # variação ao longo de cada coluna
    dr = np.abs(np.diff(a, axis=0)).mean(1)
    sx = np.asarray([a[:, x].std() for x in range(W)]); sy = a.std(1)
    x0 = corta(sx, W); x1 = W - corta(sx[::-1], W); y0 = corta(sy, H); y1 = H - corta(sy[::-1], H)
    # moldura com filete escuro: pula mais um pouco
    return x0 + (6 if x0 else 0), y0 + (6 if y0 else 0), x1 - (6 if x1 < W else 0), y1 - (6 if y1 < H else 0)


cx0, cy0, cx1, cy1 = [max(a, b) if i < 2 else min(a, b) for i, (a, b) in enumerate(zip(miolo(A), miolo(B)))]
A, B = A.crop((cx0, cy0, cx1, cy1)), B.crop((cx0, cy0, cx1, cy1))

# alinhamento fino (a edição às vezes desloca alguns pixels): procura o deslocamento que minimiza a diferença no fundo
best = (1e18, 0, 0)
sa = np.asarray(A.convert("L").resize((A.width // 4, A.height // 4)), dtype=np.float32)
for dx in range(-3, 4):
    for dy in range(-3, 4):
        sb = np.asarray(B.convert("L").resize((B.width // 4, B.height // 4)), dtype=np.float32)
        sb = np.roll(np.roll(sb, dy, 0), dx, 1)
        e = np.median(np.abs(sa - sb))
        if e < best[0]:
            best = (e, dx, dy)
_, dx, dy = best
B = ImageChops.offset(B, dx * 4, dy * 4)

if "--fundo-so" not in sys.argv:
    d = ImageChops.difference(A, B).convert("L").point(lambda v: 255 if v > LIM else 0)
    d = d.filter(ImageFilter.MedianFilter(5)).filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.MinFilter(7))
    # fica só com as manchas grandes (o personagem), tapa furos
    m = np.asarray(d) > 0
    from scipy import ndimage
    lab, n = ndimage.label(m)
    if n:
        tam = ndimage.sum(m, lab, range(1, n + 1))
        keep = [i + 1 for i, t in enumerate(tam) if t > max(4000, tam.max() * 0.04)]
        if "--so-maior" in sys.argv:  # só a maior mancha (tira filetes de cenário que mudaram por deslocamento)
            m = ndimage.binary_opening(m, iterations=4)
            lab, n = ndimage.label(m)
            tam = ndimage.sum(m, lab, range(1, n + 1))
            keep = [int(np.argmax(tam)) + 1]
        m = np.isin(lab, keep)
    m = ndimage.binary_closing(m, iterations=10)  # fecha buracos onde roupa e cenário têm a mesma cor
    m = ndimage.binary_fill_holes(m)
    mask = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.3))
    pers = A.convert("RGBA"); pers.putalpha(mask)
else:
    pers = None


def enquadra(im):
    """Cobre 1080x1920 sem borda (corta o excesso no centro)."""
    W, H = im.size; s = max(1080 / W, 1920 / H)
    im = im.resize((round(W * s), round(H * s)), Image.LANCZOS)
    x, y = (im.width - 1080) // 2, (im.height - 1920) // 2
    return im.crop((x, y, x + 1080, y + 1920))


enquadra(B).save(pref + "_fundo.jpg", quality=93)
if pers is not None:
    p = enquadra(pers); p.save(pref + "_pers.png")
    chk = Image.new("RGBA", p.size, (255, 0, 255, 255)); chk.alpha_composite(p)
    chk.convert("RGB").resize((360, 640)).save(pref + "_check.jpg")
print(pref, "corte", (cx0, cy0, cx1, cy1), "desloc", dx * 4, dy * 4)
