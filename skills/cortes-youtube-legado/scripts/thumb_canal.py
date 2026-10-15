"""Thumb no padrão do canal "Legacy Executoria Empresarial" (aba Ao vivo, ago–out/2026; pedido do usuário, 15/10/2026).

Fundo quase preto com textura e brilho azul atrás do Clailton; Clailton recortado (foto do ensaio de estúdio, sem
contorno branco) à direita e NA FRENTE do texto; texto à esquerda em caixa-alta: linha de apoio branca (Montserrat
ExtraBold) + palavra-chave grossa em azul (Impact engordado, degradê #19B8FA→#0686D6, filete ciano) ou vermelha
(palavra negativa); linha final branca opcional. Sem logo, sem tarja.

  python thumb_canal.py saida.jpg --pessoa recorte.png --apoio "PARE DE DECIDIR" --golpe "SÓ PELO|CAIXA" [--rodape "..."]
         [--cor azul|vermelho] [--x 1000] [--cabeca 270] [--espelhar]

"|" quebra a linha à força; sem "|", o texto quebra sozinho. Sai em 1280×720 (JPG) + _mini.png (246×138, conferência).
Fotos do ensaio: G:/Meu Drive/4. Design/11 - Fotos/Clailton/2026_02_23_Fotos_Estudio_Clailton (recorte sem fundo no
Magnific, 3 créditos cada; os prontos ficam em C:/Render/_youtube/fotos_clailton/recortes).
"""
from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont

S = 2
W, H = 1280 * S, 720 * S
FONTES = Path("C:/Render/_youtube/recursos/fonts")
GOLPE = "C:/Windows/Fonts/impact.ttf"
CORES = {
    "azul": {"topo": (25, 184, 250), "base": (6, 134, 214), "traco": (0, 150, 234), "filete": (63, 196, 255)},
    "vermelho": {"topo": (255, 60, 60), "base": (200, 10, 18), "traco": (227, 18, 27), "filete": (255, 110, 110)},
}


def apoio_fonte(cap: int) -> ImageFont.FreeTypeFont:
    caminho = FONTES / "Montserrat-VF.ttf"
    tam = cap
    for _ in range(30):
        f = ImageFont.truetype(str(caminho), tam)
        try:
            f.set_variation_by_name("ExtraBold")
        except Exception:
            pass
        b = f.getbbox("H")
        if abs((b[3] - b[1]) - cap) <= 1:
            return f
        tam = max(4, int(tam * cap / max(1, b[3] - b[1])))
    return f


def golpe_fonte(cap: int) -> ImageFont.FreeTypeFont:
    tam = cap
    for _ in range(30):
        f = ImageFont.truetype(GOLPE, tam)
        b = f.getbbox("H")
        if abs((b[3] - b[1]) - cap) <= 1:
            return f
        tam = max(4, int(tam * cap / max(1, b[3] - b[1])))
    return f


def quebrar(texto: str, f, largura: int) -> list[str]:
    """Quebra em linhas que cabem em `largura`, equilibradas (sem palavra sozinha na última). "|" força a quebra."""
    if "|" in texto:
        return [t.strip() for t in texto.split("|") if t.strip()]
    pal = texto.split()
    if f.getlength(texto) <= largura or len(pal) == 1:
        return [texto]
    import itertools
    for n in range(2, len(pal) + 1):
        melhor = None
        for cortes in itertools.combinations(range(1, len(pal)), n - 1):
            ls = [" ".join(pal[a:b]) for a, b in zip((0,) + cortes, cortes + (len(pal),))]
            m = max(f.getlength(l) for l in ls)
            if m <= largura and (melhor is None or m < melhor[0]):
                melhor = (m, ls)
        if melhor:
            return melhor[1]
    return pal


def fundo(espelhar: bool) -> Image.Image:
    rng = np.random.default_rng(7)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    base = np.zeros((H, W, 3), np.float32)
    base[:] = (4, 7, 13)
    # brilho azul atrás da cabeça e do ombro
    cx = (W - 1060 * S) if espelhar else 1060 * S
    for (gx, gy, r, cor, k) in [(cx, 230 * S, 430 * S, (10, 63, 208), 0.95), (cx, 420 * S, 600 * S, (1, 23, 98), 0.8)]:
        d = np.sqrt((xx - gx) ** 2 + (yy - gy) ** 2) / r
        a = np.clip(1 - d, 0, 1) ** 1.8 * k
        base += np.array(cor, np.float32) * a[..., None]
    # canto do texto puxando para bordô muito escuro
    tx = W * 0.0 if not espelhar else W * 1.0
    d = np.sqrt((xx - tx) ** 2 + (yy - H) ** 2) / (900 * S)
    base += np.array((20, 0, 4), np.float32) * (np.clip(1 - d, 0, 1) ** 1.5)[..., None]
    # textura sutil e vinheta
    ruido = rng.normal(0, 3.2, (H // 2, W // 2)).astype(np.float32)
    ruido = cv2.resize(cv2.GaussianBlur(ruido, (0, 0), 1.2), (W, H))
    base += ruido[..., None]
    v = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.8)) ** 2)
    base *= np.clip(1.15 - v * 0.55, 0.45, 1)[..., None]
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def cabeca(p: Image.Image) -> tuple[int, int, int]:
    """(topo_y, centro_x, altura_cabeça) no recorte: do topo até o pescoço (a linha mais estreita depois da parte
    mais larga da cabeça, antes de os ombros abrirem). Braço levantado na altura da cabeça engana: use --cab-foto."""
    a = np.array(p.split()[3]) > 40
    alt = a.shape[0]
    topo = int(np.where(a.any(1))[0][0])
    w = a.sum(1).astype(float)
    k = max(5, alt // 150)
    ws = np.convolve(w, np.ones(k) / k, "same")
    i_max = topo + int(np.argmax(ws[topo:topo + int(alt * 0.22)]))
    seg = ws[i_max:topo + int(alt * 0.5)]
    j = int(np.argmax(seg > 1.6 * ws[i_max])) if (seg > 1.6 * ws[i_max]).any() else len(seg)
    pesc = i_max + int(np.argmin(seg[:max(1, j)]))
    linha = a[topo:topo + max(20, (pesc - topo) // 3)]
    cols = np.where(linha.any(0))[0]
    return topo, int(cols.mean()), max(1, pesc - topo)


def pessoa(img: Image.Image, caminho: str, cx_alvo: int, cab_alvo: int, espelhar: bool, cab_foto: int | None = None) -> Image.Image:
    p = Image.open(caminho).convert("RGBA")
    p = p.crop(p.getbbox())
    if espelhar:
        p = p.transpose(Image.FLIP_LEFT_RIGHT)
    al = np.array(p.split()[3]).astype(np.float32)
    n = max(8, int(p.width * 0.06))
    for lado in ("esq", "dir"):
        col = al[:, 0] if lado == "esq" else al[:, -1]
        if (col > 128).mean() > 0.05:            # o corpo encosta na borda da foto: degradê de n px
            rampa = np.linspace(0, 1, n)[None, :]
            if lado == "esq":
                al[:, :n] *= rampa
            else:
                al[:, -n:] *= rampa[:, ::-1]
    p.putalpha(Image.fromarray(al.clip(0, 255).astype(np.uint8)))
    topo, cx, cab = cabeca(p)
    if cab_foto:
        cab = cab_foto
    k = cab_alvo * S / max(1, cab)
    p = p.resize((int(p.width * k), int(p.height * k)), Image.LANCZOS)
    rgb = ImageEnhance.Contrast(p.convert("RGB")).enhance(1.08)
    rgb = rgb.filter(ImageFilter.UnsharpMask(2, 50, 2))
    p = Image.merge("RGBA", (*rgb.split(), p.split()[3]))
    # sombra suave atrás, para descolar do fundo
    pos = (int(cx_alvo * S - cx * k), int(30 * S - topo * k))
    sombra = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sombra.paste(Image.new("RGBA", p.size, (0, 0, 0, 150)), pos, p)
    tela = Image.new("RGBA", img.size, (0, 0, 0, 0))
    tela.paste(p, pos, p)
    return sombra.filter(ImageFilter.GaussianBlur(18 * S)), tela


def texto_golpe(img: Image.Image, linhas: list[str], f, x0: int, y0: int, cor: dict, alinhar: str) -> int:
    cap = f.getbbox("H")[3] - f.getbbox("H")[1]
    passo = int(cap * (1.3 if any(c in ''.join(linhas[1:]) for c in 'ÃÕÁÉÍÓÚÂÊÔÀÇ') else 1.18))
    mascara = Image.new("L", img.size, 0)
    filete = Image.new("L", img.size, 0)
    dm, df = ImageDraw.Draw(mascara), ImageDraw.Draw(filete)
    y = y0
    for ln in linhas:
        w = f.getlength(ln)
        x = x0 if alinhar == "esq" else x0 - w
        topo = f.getbbox("H")[1]
        dm.text((x, y - topo), ln, font=f, fill=255, stroke_width=2 * S, stroke_fill=255)
        df.text((x, y - topo), ln, font=f, fill=255, stroke_width=5 * S, stroke_fill=255)
        y += passo
    # filete ciano por fora
    camada = Image.new("RGBA", img.size, cor["filete"] + (0,))
    camada.putalpha(filete)
    img = Image.alpha_composite(img, camada)
    # corpo em degradê vertical, com textura leve (o "cetim" do original)
    yy = np.linspace(0, 1, img.height)[:, None, None]
    grad = np.array(cor["topo"], np.float32) * (1 - yy) + np.array(cor["base"], np.float32) * yy
    grad = np.repeat(grad, img.width, 1)
    rng = np.random.default_rng(3)
    tex = cv2.GaussianBlur(rng.normal(0, 1, (img.height // 3, img.width // 3)).astype(np.float32), (0, 0), 0.8)
    tex = cv2.resize(tex, (img.width, img.height))[..., None] * 6
    corpo = Image.fromarray(np.clip(grad + tex, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    corpo.putalpha(mascara)
    # sombra curta embaixo da palavra
    sombra = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sombra.paste(Image.new("RGBA", img.size, (0, 0, 0, 120)), (0, 4 * S), filete)
    img = Image.alpha_composite(img, sombra.filter(ImageFilter.GaussianBlur(6 * S)))
    return Image.alpha_composite(img, corpo), y


def branco(img: Image.Image, linhas: list[str], f, x0: int, y0: int, alinhar: str, entre: float = 1.32) -> tuple:
    cap = f.getbbox("H")[3] - f.getbbox("H")[1]
    d = ImageDraw.Draw(img)
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    y = y0
    pos = []
    for ln in linhas:
        w = f.getlength(ln)
        x = x0 if alinhar == "esq" else x0 - w
        topo = f.getbbox("H")[1]
        pos.append((x, y - topo, ln))
        ds.text((x, y - topo + 3 * S), ln, font=f, fill=(0, 0, 0, 140))
        y += int(cap * entre)
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(5 * S)))
    d = ImageDraw.Draw(img)
    for x, yy, ln in pos:
        d.text((x, yy), ln, font=f, fill=(255, 255, 255))
    return img, y - int(cap * (entre - 1))


def montar(a) -> Image.Image:
    esp = a.espelhar
    alinhar = "dir" if esp else "esq"
    x0 = (1190 if esp else 90) * S
    larg = (a.largura or 600) * S
    img = fundo(esp)
    cx = a.x or (280 if esp else 1000)
    sombra_p, camada_p = pessoa(img, a.pessoa, cx, a.cabeca or 285, esp, a.cab_foto)
    # onde o corpo começa na faixa do texto: a palavra-chave pode encostar no ombro, não sumir atrás dele
    al = np.array(camada_p.split()[3])[200 * S:560 * S] > 60
    colunas = np.where(al.any(0))[0]
    if len(colunas):
        livre = (colunas.min() - x0) / S + 40 if not esp else (x0 - colunas.max()) / S + 40
    else:
        livre = 640
    lim_golpe = min(a.largura_golpe or 640, max(380, int(livre)))
    camada_texto = Image.new("RGBA", img.size, (0, 0, 0, 0))
    fa = apoio_fonte(int((a.cap_apoio or 46) * S))
    ap = quebrar(a.apoio.upper(), fa, larg) if a.apoio else []
    linhas_g = quebrar(a.golpe.upper(), golpe_fonte(120 * S), larg + 60 * S)
    cap_g = (a.cap_golpe or (170 if len(linhas_g) == 1 else 118 if len(linhas_g) == 2 else 100)) * S
    fg = golpe_fonte(cap_g)
    while max(fg.getlength(l) for l in linhas_g) > lim_golpe * S and cap_g > 70 * S:
        cap_g -= 4 * S
        fg = golpe_fonte(cap_g)
    fr = apoio_fonte(int((a.cap_rodape or 34) * S))
    rod = quebrar(a.rodape.upper(), fr, larg) if a.rodape else []
    # altura total para centrar o bloco em y≈360
    cap_a = fa.getbbox("H")[3] - fa.getbbox("H")[1]
    h_ap = (len(ap) * cap_a * 1.32 - cap_a * 0.32) if ap else 0
    h_g = len(linhas_g) * cap_g * 1.2 - cap_g * 0.2
    cap_r = fr.getbbox("H")[3] - fr.getbbox("H")[1]
    h_r = (len(rod) * cap_r * 1.32 - cap_r * 0.32) if rod else 0
    acento = any(c in linhas_g[0] for c in 'ÃÕÁÉÍÓÚÂÊÔÀ')
    gap1, gap2 = ((34 + (int(cap_g / S * 0.22) if acento else 0)) * S if ap else 0), (34 * S if rod else 0)
    total = h_ap + gap1 + h_g + gap2 + h_r
    y = int(max(70 * S, (H - total) / 2 + (a.desce or 0) * S))
    if ap:
        camada_texto, y = branco(camada_texto, ap, fa, x0, y, alinhar)
        y += gap1
    camada_texto, y = texto_golpe(camada_texto, linhas_g, fg, x0, y, CORES[a.cor], alinhar)
    if rod:
        y += gap2 - int(cap_g * 0.2)
        camada_texto, _ = branco(camada_texto, rod, fr, x0, y, alinhar)
    img = Image.alpha_composite(img, camada_texto)
    img = Image.alpha_composite(img, sombra_p)
    return Image.alpha_composite(img, camada_p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("saida")
    ap.add_argument("--pessoa", required=True)
    ap.add_argument("--apoio", default="")
    ap.add_argument("--golpe", required=True)
    ap.add_argument("--rodape", default="")
    ap.add_argument("--cor", choices=list(CORES), default="azul")
    ap.add_argument("--x", type=int, help="centro da cabeça em x (1280×720); padrão 1000 (ou 280 espelhado)")
    ap.add_argument("--cabeca", type=int, help="altura da cabeça em px; padrão 270")
    ap.add_argument("--espelhar", action="store_true", help="pessoa à esquerda, texto alinhado à direita")
    ap.add_argument("--largura", type=int, help="largura do bloco de texto (padrão 600)")
    ap.add_argument("--largura-golpe", type=int, help="largura máxima da palavra-chave (padrão 640)")
    ap.add_argument("--cap-apoio", type=int)
    ap.add_argument("--cap-golpe", type=int)
    ap.add_argument("--cap-rodape", type=int)
    ap.add_argument("--cab-foto", type=int, help="altura da cabeça (topo ao pescoço) em px na foto, se a medição errar")
    ap.add_argument("--desce", type=int, help="desloca o bloco de texto para baixo (px)")
    a = ap.parse_args()
    img = montar(a).convert("RGB").resize((1280, 720), Image.LANCZOS)
    out = Path(a.saida)
    img.save(out, quality=92)
    img.resize((246, 138), Image.LANCZOS).save(out.with_name(out.stem + "_mini.png"))
    print("ok:", out)


if __name__ == "__main__":
    main()
