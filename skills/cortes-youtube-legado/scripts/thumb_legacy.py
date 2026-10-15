"""Monta a thumb do YouTube na identidade da Legacy, no estilo do ROI Hunters (spec: references/pesquisa-thumbs.md).

Entrada: o Clailton recortado sem fundo (PNG com transparência; ampliado 4x e sem fundo no Magnific = ~183 créditos),
os textos e, se quiser, um "objeto" do tema (recorte do slide da aula, foto, gráfico).

  python thumb_legacy.py A saida.png --pessoa cut.png --apoio "SEU LUCRO É SÓ" --golpe "UM SINTOMA" [--objeto slide.png] [--balao "Faz essa conta"]
  python thumb_legacy.py B saida.png --pessoa cut.png --linhas "QUEM NÃO|MEDE NÃO|GERENCIA" [--fundo quadro.png]

A = "ROI Legacy": linha de apoio branca + golpe em tarja azul, Clailton à direita, objeto à esquerda.
B = "Palestrante": 2–3 linhas grandes à esquerda, a última em degradê azul, Clailton maior à direita.
Sai em 2560×1440 (o YouTube aceita e o teste A/B não perde nitidez) + uma cópia 1280×720 e a conferência em 246×138.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageEnhance

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import SKILL  # noqa: E402

S = 2                                   # tudo é pensado em 1280×720 e desenhado ×2
W, H = 1280 * S, 720 * S
NAVY_ESC, NAVY, AZUL, AZUL_CLARO, AZUL_FORTE = (7, 21, 45), (18, 48, 95), (60, 131, 246), (111, 166, 255), (47, 111, 224)
GOLPE_FONTE = "C:/Windows/Fonts/impact.ttf"
APOIO_FONTE = "C:/Windows/Fonts/Poppins-ExtraBold.ttf" if Path("C:/Windows/Fonts/Poppins-ExtraBold.ttf").exists() \
    else str(SKILL / "fonts" / "SF-Pro-Display-Bold.otf")
LOGO = Path("C:/Render/_youtube/recursos/logo_legacy_white.png")


def fonte_para_altura(caminho: str, altura_maiuscula: int) -> ImageFont.FreeTypeFont:
    """Acha o tamanho de fonte cuja maiúscula ('H') mede a altura pedida."""
    tam = altura_maiuscula
    for _ in range(40):
        f = ImageFont.truetype(caminho, tam)
        b = f.getbbox("H")
        h = b[3] - b[1]
        if abs(h - altura_maiuscula) <= 1:
            return f
        tam = max(4, int(tam * altura_maiuscula / max(1, h)))
    return ImageFont.truetype(caminho, tam)


def fundo(base: Image.Image | None) -> Image.Image:
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - 420 * S) / W) ** 2 + ((yy - 300 * S) / H) ** 2)
    f = np.clip(d / 0.9, 0, 1)[..., None]
    img = (np.array(NAVY, np.float32) * (1 - f) + np.array(NAVY_ESC, np.float32) * f).astype(np.uint8)
    im = Image.fromarray(img, "RGB").convert("RGBA")
    if base is not None:                                   # quadro da aula, desfocado e escurecido, por baixo
        b = base.convert("RGB").resize((W, H)).filter(ImageFilter.GaussianBlur(20 * S))
        b = ImageEnhance.Brightness(b).enhance(0.3).convert("RGBA")
        im = Image.blend(b, im, 0.7)
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))            # grade fina da identidade ("Nova Logo")
    dg = ImageDraw.Draw(g)
    for x in range(0, W, 64 * S):
        dg.line((x, 0, x, H), fill=(255, 255, 255, 13), width=S)
    for y in range(0, H, 64 * S):
        dg.line((0, y, W, y), fill=(255, 255, 255, 13), width=S)
    return Image.alpha_composite(im, g)


def brilho(img: Image.Image, cx: int, cy: int, raio: int, cor, alfa: float) -> Image.Image:
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a = np.clip(1 - np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / raio, 0, 1) ** 1.6 * alfa * 255
    camada = np.zeros((H, W, 4), np.uint8)
    camada[..., :3] = cor
    camada[..., 3] = a.astype(np.uint8)
    return Image.alpha_composite(img, Image.fromarray(camada, "RGBA"))


def pessoa_tratada(caminho: str, altura_cabeca: int) -> tuple[Image.Image, tuple[int, int]]:
    """Recorte com contorno branco (4 px), halo azul e ajuste leve de cor. Devolve a imagem e o (x, y) do topo da
    cabeça dentro dela (para posicionar)."""
    p = Image.open(caminho).convert("RGBA")
    a = np.array(p)[..., 3]
    ys, xs = np.where(a > 40)
    topo = ys.min()
    # cabeça ≈ do topo até 34% da altura do busto (o recorte é cabeça até a cintura)
    cab_px = (ys.max() - topo) * 0.34
    k = altura_cabeca / max(1.0, cab_px)
    p = p.resize((int(p.width * k), int(p.height * k)), Image.LANCZOS)
    rgb = ImageEnhance.Contrast(p.convert("RGB")).enhance(1.12)
    rgb = ImageEnhance.Color(rgb).enhance(1.08).filter(ImageFilter.UnsharpMask(2, 60, 2))
    p = Image.merge("RGBA", (*rgb.split(), p.split()[3]))
    m = 30 * S
    tela = Image.new("RGBA", (p.width + 2 * m, p.height + 2 * m), (0, 0, 0, 0))
    alfa = Image.new("L", tela.size, 0)
    alfa.paste(p.split()[3], (m, m))
    contorno = alfa.filter(ImageFilter.MaxFilter(2 * 4 * S + 1))
    halo = alfa.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(28 * S))
    tela = Image.alpha_composite(tela, Image.merge("RGBA", (*Image.new("RGB", tela.size, AZUL).split(),
                                                            halo.point(lambda v: int(v * 0.55)))))
    tela = Image.alpha_composite(tela, Image.merge("RGBA", (*Image.new("RGB", tela.size, (255, 255, 255)).split(),
                                                            contorno)))
    tela.alpha_composite(p, (m, m))
    topo_y = int(topo * k) + m
    xs2 = np.where(np.array(p)[..., 3][int(topo * k):int(topo * k) + int(altura_cabeca * 0.6)].max(0) > 40)[0]
    cx = int(xs2.mean()) + m if len(xs2) else tela.width // 2
    return tela, (cx, topo_y)


def sombra_texto(img, xy, texto, f, cor=(255, 255, 255), off=3, blur=8, alfa=150):
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((xy[0], xy[1] + off * S), texto, font=f, fill=(0, 0, 0, alfa))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(blur * S)))
    ImageDraw.Draw(img).text(xy, texto, font=f, fill=cor)
    return img


def logo(img: Image.Image) -> Image.Image:
    if LOGO.exists():
        lg = Image.open(LOGO).convert("RGBA")
        w = 170 * S
        lg = lg.resize((w, int(lg.height * w / lg.width)), Image.LANCZOS)
        img.alpha_composite(lg, (32 * S, 28 * S))
    return img


def objeto(img: Image.Image, caminho: str) -> Image.Image:
    o = Image.open(caminho).convert("RGB")
    caixa = (520 * S, 290 * S)
    o.thumbnail(caixa, Image.LANCZOS)
    pad = 10 * S
    card = Image.new("RGBA", (o.width + 2 * pad, o.height + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 14 * S, fill=(255, 255, 255, 255))
    card.paste(o, (pad, pad))
    card = card.rotate(3, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    x, y = 80 * S, 84 * S
    sh.paste(Image.new("RGBA", card.size, (0, 0, 0, 115)), (x, y + 12 * S), card)
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(24 * S)))
    img.alpha_composite(card, (x, y))
    return img


def variante_a(args) -> Image.Image:
    img = fundo(Image.open(args.fundo) if args.fundo else None)
    img = brilho(img, 960 * S, 300 * S, 420 * S, AZUL, 0.35)
    if args.objeto:
        img = objeto(img, args.objeto)
    pes, (cx, ty) = pessoa_tratada(args.pessoa, (args.cabeca or 360) * S)
    img.alpha_composite(pes, ((args.x or 980) * S - cx, 40 * S - ty))
    # linha de apoio
    fa = fonte_para_altura(APOIO_FONTE, 40 * S)
    while fa.getlength(args.apoio) > 980 * S and fa.size > 20:
        fa = ImageFont.truetype(APOIO_FONTE, fa.size - 2)
    wa = fa.getlength(args.apoio)
    ba = fa.getbbox(args.apoio)
    img = sombra_texto(img, (600 * S - wa / 2, 492 * S - ba[3]), args.apoio, fa)
    # tarja + golpe
    cap = 140 * S
    while True:
        fg = fonte_para_altura(GOLPE_FONTE, cap)
        wg = fg.getlength(args.golpe)
        if wg <= 1000 * S or cap <= 110 * S:
            break
        cap -= 4 * S
    bx0 = 600 * S - wg / 2 - 36 * S
    bx1 = 600 * S + wg / 2 + 36 * S
    if bx1 > 1110 * S:
        bx0 -= bx1 - 1110 * S
        bx1 = 1110 * S
    bx0 = max(32 * S, bx0)
    y0, y1 = 508 * S, 684 * S
    tw, th = int(bx1 - bx0), y1 - y0
    xx = np.linspace(0, 1, tw)[None, :, None]
    grad = (np.array(AZUL_FORTE) * (1 - xx) + np.array(AZUL) * xx).repeat(th, 0).astype(np.uint8)
    tarja = Image.fromarray(np.dstack([grad, np.full((th, tw), 255, np.uint8)]), "RGBA")
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    glow.paste(Image.new("RGBA", (tw, th), AZUL_CLARO + (90,)), (int(bx0), y0))
    img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(18 * S)))
    img.alpha_composite(tarja, (int(bx0), y0))
    bg = fg.getbbox(args.golpe)
    gx = (bx0 + bx1) / 2 - wg / 2
    gy = y0 + (th - (bg[3] - bg[1])) / 2 - bg[1]
    img = sombra_texto(img, (gx, gy), args.golpe, fg, off=2, blur=4, alfa=90)
    if args.balao:
        fb = ImageFont.truetype(APOIO_FONTE.replace("ExtraBold", "Bold"), 26 * S)
        bb = fb.getbbox(args.balao)
        card = Image.new("RGBA", (bb[2] - bb[0] + 32 * S, bb[3] - bb[1] + 20 * S), (0, 0, 0, 0))
        dc = ImageDraw.Draw(card)
        dc.rounded_rectangle((0, 0, card.width - 1, card.height - 1), 10 * S, fill=AZUL_CLARO + (255,))
        dc.text((16 * S - bb[0], 10 * S - bb[1]), args.balao, font=fb, fill=NAVY_ESC)
        card = card.rotate(4, expand=True, resample=Image.BICUBIC)
        img.alpha_composite(card, (600 * S, 340 * S))
    return logo(img)


def variante_b(args) -> Image.Image:
    img = fundo(Image.open(args.fundo) if args.fundo else None)
    img = brilho(img, 980 * S, 330 * S, 460 * S, AZUL, 0.30)
    pes, (cx, ty) = pessoa_tratada(args.pessoa, (args.cabeca or 420) * S)
    img.alpha_composite(pes, ((args.x or 1000) * S - cx, 34 * S - ty))
    linhas = [l.strip() for l in args.linhas.split("|") if l.strip()]
    cap = 96 * S
    while True:
        f = fonte_para_altura(GOLPE_FONTE, cap)
        if max(f.getlength(l) for l in linhas) <= 600 * S or cap <= 60 * S:
            break
        cap -= 4 * S
    alt = cap + 40 * S                                  # folga para acento e til (NÃO, VOCÊ)
    total = alt * len(linhas) - 40 * S
    y = (720 * S - total) / 2 - 10 * S
    for i, l in enumerate(linhas):
        b = f.getbbox(l)
        pos = (72 * S, y - b[1])
        if i == len(linhas) - 1:                          # palavra-chave em degradê azul
            mask = Image.new("L", img.size, 0)
            ImageDraw.Draw(mask).text(pos, l, font=f, fill=255)
            sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
            sh.paste(Image.new("RGBA", img.size, (0, 0, 0, 140)), (0, 4 * S), mask)
            img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(10 * S)))
            xx = np.linspace(0, 1, W)[None, :, None]
            grad = (np.array(AZUL_CLARO) * (1 - xx) + np.array(AZUL) * xx).repeat(H, 0).astype(np.uint8)
            camada = Image.fromarray(grad, "RGB").convert("RGBA")
            camada.putalpha(mask)
            img = Image.alpha_composite(img, camada)
        else:
            img = sombra_texto(img, pos, l, f, off=4, blur=10, alfa=140)
        y += alt
    return logo(img)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("variante", choices=["A", "B"])
    ap.add_argument("saida")
    ap.add_argument("--pessoa", required=True)
    ap.add_argument("--apoio", default="")
    ap.add_argument("--golpe", default="")
    ap.add_argument("--linhas", default="")
    ap.add_argument("--objeto")
    ap.add_argument("--balao")
    ap.add_argument("--fundo")
    ap.add_argument("--cabeca", type=int, help="altura da cabeça em px de 1280×720 (A: 360, B: 420); diminua se a tarja cobrir o rosto")
    ap.add_argument("--x", type=int, help="centro da cabeça em x (A: 980, B: 1000)")
    a = ap.parse_args()
    img = (variante_a if a.variante == "A" else variante_b)(a).convert("RGB")
    out = Path(a.saida)
    img.save(out, quality=95)
    img.resize((1280, 720), Image.LANCZOS).save(out.with_name(out.stem + "_1280.jpg"), quality=92)
    img.resize((246, 138), Image.LANCZOS).save(out.with_name(out.stem + "_mini.png"))
    print("ok:", out)


if __name__ == "__main__":
    main()
