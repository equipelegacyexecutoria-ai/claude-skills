# Capa de card do MURAL (Notion) no padrao "Cerebro Legacy": 1538x433, grade escura, logo, titulo Bebas branco + azul,
# subtitulo cinza em Poppins e dois destaques a direita com barra azul.
import os, sys, json
from PIL import Image, ImageDraw, ImageFont

H = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Fonts")
BEBAS = os.path.join(H, "BebasNeue-Regular.ttf")
POP = os.path.join(FONTS, "Poppins-Regular.ttf")
W, HH = 1538, 433
BG, LINE = (12, 12, 12), (31, 31, 31)
AZUL, CINZA, BRANCO = (39, 68, 203), (145, 145, 145), (255, 255, 255)
P = dict(title_px=133, t1_base=192, t2_base=306, x=73, sub_px=15.5, sub_top=342, sub_lh=23,
         stat_px=48, stat_base=347, cap_px=12.5, cap_top=362, bar_top=310, bar_h=79, stat_x=(1060, 1270))


def fundo():
    im = Image.new("RGB", (W, HH), BG)
    d = ImageDraw.Draw(im)
    for v in range(38, W, 39):
        d.line([(v, 0), (v, HH)], fill=LINE)
    for v in range(38, HH, 39):
        d.line([(0, v), (W, v)], fill=LINE)
    logo = Image.open(os.path.join(H, "modelo_bibliografia.png")).convert("RGB").crop((60, 40, 310, 104))
    im.paste(logo, (60, 40))
    return im


def texto_base(d, xy, txt, font, cor):
    # x = inicio da tinta, y = linha de base (acento nao desloca a linha)
    b = d.textbbox((0, 0), txt, font=font, anchor="ls")
    d.text((xy[0] - b[0], xy[1]), txt, font=font, fill=cor, anchor="ls")
    return b[2] - b[0]


def capa(t1, t2, sub, stats, saida, p=P):
    im = fundo(); d = ImageDraw.Draw(im)
    ft = ImageFont.truetype(BEBAS, p["title_px"])
    texto_base(d, (p["x"], p["t1_base"]), t1, ft, BRANCO)
    texto_base(d, (p["x"] - 5, p["t2_base"]), t2, ft, AZUL)
    fs = ImageFont.truetype(POP, p["sub_px"])
    for i, ln in enumerate(sub.split("\n")):
        d.text((p["x"] - 2, p["sub_top"] + i * p["sub_lh"]), ln, font=fs, fill=CINZA)
    fst = ImageFont.truetype(BEBAS, p["stat_px"]); fc = ImageFont.truetype(POP, p["cap_px"])
    for (big, small), x in zip(stats, p["stat_x"]):
        d.rectangle([x, p["bar_top"], x + 2, p["bar_top"] + p["bar_h"]], fill=AZUL)
        texto_base(d, (x + 19, p["stat_base"]), big, fst, BRANCO)
        d.text((x + 18, p["cap_top"]), small, font=fc, fill=CINZA)
    im.save(saida)
    return im


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    for c in spec:
        capa(c["t1"], c["t2"], c["sub"], c["stats"], c["out"])
