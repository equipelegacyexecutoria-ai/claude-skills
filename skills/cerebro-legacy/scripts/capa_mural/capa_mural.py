# Capa de card do MURAL v2: mesma identidade (grade, logo, Bebas branco + azul, Poppins cinza, destaques a direita),
# com margens fixas e o bloco da esquerda cabendo no recorte 701x430 usado como "capa externa" (MATERIAL FINALIZADO).
import os
from PIL import Image, ImageDraw, ImageFont

H = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Fonts")
BEBAS = os.path.join(H, "BebasNeue-Regular.ttf")
POP = os.path.join(FONTS, "Poppins-Regular.ttf")
W, HH = 1538, 433
CW, CH = 701, 430                 # recorte do card
M = 70                            # margem esquerda (e direita do recorte = 701 - M)
BG, LINE = (12, 12, 12), (31, 31, 31)
AZUL, CINZA, BRANCO = (39, 68, 203), (145, 145, 145), (255, 255, 255)
GAP_LOGO, GAP_SUB = 30, 30        # logo -> titulo, titulo -> subtitulo
SUB_PX, SUB_LH = 15.5, 24


def fundo():
    im = Image.new("RGB", (W, HH), BG)
    d = ImageDraw.Draw(im)
    for v in range(38, W, 39):
        d.line([(v, 0), (v, HH)], fill=LINE)
    for v in range(38, HH, 39):
        d.line([(0, v), (W, v)], fill=LINE)
    return im


def logo():
    # logo recortado do modelo, sem a grade: so os pixels claros/azuis sobre o fundo
    src = Image.open(os.path.join(H, "modelo_bibliografia.png")).convert("RGB").crop((66, 44, 258, 92))
    a = Image.new("L", src.size, 0)
    px, pa = src.load(), a.load()
    for y in range(src.size[1]):
        for x in range(src.size[0]):
            r, g, b = px[x, y]
            pa[x, y] = max(0, min(255, (max(r, g, b) - 34) * 3))
    return src, a


def ink(d, txt, font):
    return d.textbbox((0, 0), txt, font=font, anchor="ls")


def capa(t1, t2, sub, stats, base):
    im = fundo(); d = ImageDraw.Draw(im)
    lg, la = logo()
    # tamanho do titulo: o maior que cabe no recorte (largura) sem passar de 124 px
    larg = CW - 2 * M
    S = 124
    while S > 60:
        ft = ImageFont.truetype(BEBAS, S)
        if max(ink(d, t, ft)[2] - ink(d, t, ft)[0] for t in (t1, t2)) <= larg:
            break
        S -= 1
    ft = ImageFont.truetype(BEBAS, S)
    cap = -ink(d, "H", ft)[1]
    lgap = round(cap * 0.2)
    if any(ch in "ÁÉÍÓÚÂÊÔÃÕÀ" for ch in t2):   # acento da 2a linha nao pode encostar na 1a
        lgap += -ink(d, "Ú", ft)[1] - cap
    fs = ImageFont.truetype(POP, SUB_PX)
    linhas = sub.split("\n")
    sub_h = (len(linhas) - 1) * SUB_LH + 18
    total = lg.size[1] + GAP_LOGO + 2 * cap + lgap + GAP_SUB + sub_h
    y = (CH - total) // 2
    im.paste(lg, (M - 2, y), la)
    y += lg.size[1] + GAP_LOGO
    b1 = y + cap; b2 = b1 + lgap + cap
    for t, bl, cor in ((t1, b1, BRANCO), (t2, b2, AZUL)):
        bb = ink(d, t, ft)
        d.text((M - bb[0], bl), t, font=ft, fill=cor, anchor="ls")
    ys = b2 + GAP_SUB
    for i, ln in enumerate(linhas):
        d.text((M, ys + i * SUB_LH), ln, font=fs, fill=CINZA, anchor="lt")
    sub_fim = ys + (len(linhas) - 1) * SUB_LH + 18
    # destaques a direita, alinhados pela base com o subtitulo e com margem direita M
    fst = ImageFont.truetype(BEBAS, 48); fc = ImageFont.truetype(POP, 12.5)
    ws = [max(d.textlength(a, font=fst), d.textlength(c, font=fc)) for a, c in stats]
    gap = 56
    x2 = W - M - 19 - ws[1]
    x1 = x2 - gap - 19 - ws[0]
    bar_bot = sub_fim + 2; bar_top = bar_bot - 79
    for (a, c), x in zip(stats, (x1, x2)):
        x = round(x)
        d.rectangle([x, bar_top, x + 2, bar_bot], fill=AZUL)
        bb = ink(d, a, fst)
        d.text((x + 19 - bb[0], bar_top + 37), a, font=fst, fill=BRANCO, anchor="ls")
        d.text((x + 19, bar_top + 52), c, font=fc, fill=CINZA, anchor="lt")
    im.save(base + "_capa.png")
    im.crop((0, 0, CW, CH)).save(base + "_card.png")
    return im, S
