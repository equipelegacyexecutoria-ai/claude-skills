"""Card da CTA "SESSÃO ESTRATÉGICA GRATUITA · APONTE A CÂMERA" com QR code (PNG com transparência).

Visual copiado do Executoria Cast (youtube.com/watch?v=v0jEA57pYL8, 17:08): caixa azul em degradê com cantos
arredondados no canto superior esquerdo, QR em quadro branco à esquerda, texto branco à direita e
"GRATUITA" numa pílula verde. Tamanho de referência em 1920×1080: ~300×150 px; aqui um pouco maior
(escala 1,3: ~390×195) para o QR sair com 4 px por módulo e ler de longe na TV/computador.
URL curta (≤106 caracteres = QR versão 5, 37 módulos): campanha com código curto, ex. t12a10e1.

Uso: python qr_card.py "<url>" <saida.png> [--escala 1.15] [--altura-video 1080]
Confere sozinho que o QR gerado lê a URL certa (OpenCV) e reprova se não ler.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import SKILL  # noqa: E402

FONTES = SKILL / "fonts"
SS = 3  # supersampling


def fonte(nome: str, px: float) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTES / nome), int(round(px)))


def qr_matriz(url: str) -> np.ndarray:
    prm = cv2.QRCodeEncoder_Params()
    prm.correction_level = cv2.QRCodeEncoder_CORRECT_LEVEL_L   # tela limpa: L deixa o QR menos denso
    enc = cv2.QRCodeEncoder_create(prm)
    m = enc.encode(url)                       # 0 = preto, 255 = branco, já com zona de silêncio
    return m


def desenhar(url: str, escala: float, altura_video: int) -> Image.Image:
    k = escala * altura_video / 1080 * SS
    W, H, R = int(300 * k), int(150 * k), int(16 * k)
    sombra = int(14 * k)
    img = Image.new("RGBA", (W + 2 * sombra, H + 2 * sombra), (0, 0, 0, 0))

    # sombra suave atrás do card (separa do fundo claro do telão)
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((sombra, sombra + int(3 * k), sombra + W, sombra + H + int(3 * k)),
                                         R, fill=(0, 0, 0, 120))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(int(8 * k))))

    # degradê azul (escuro embaixo/esquerda -> claro em cima/direita), como na referência
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    f = np.clip((xx / W) * 0.65 + (1 - yy / H) * 0.35, 0, 1)[..., None]
    c0, c1 = np.array([10, 52, 112], np.float32), np.array([28, 120, 214], np.float32)
    grad = (c0 * (1 - f) + c1 * f).astype(np.uint8)
    card = Image.fromarray(np.dstack([grad, np.full((H, W), 255, np.uint8)]), "RGBA")
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, W - 1, H - 1), R, fill=255)
    card.putalpha(mask)
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((1, 1, W - 2, H - 2), R, outline=(120, 180, 255, 110), width=max(1, int(1.2 * k)))

    # QR em quadro branco
    pad = int(12 * k)
    q = H - 2 * pad
    d.rounded_rectangle((pad, pad, pad + q, pad + q), int(8 * k), fill=(255, 255, 255, 255))
    caixa_qr = (sombra + pad, sombra + pad, q)   # o QR entra depois da redução, em pixels inteiros

    # texto à direita, centralizado na coluna
    x0, x1 = pad + q + int(10 * k), W - int(10 * k)
    cx = (x0 + x1) / 2
    branco = (255, 255, 255, 255)

    def centro(txt, fnt, y, cor=branco):
        b = d.textbbox((0, 0), txt, font=fnt)
        d.text((cx - (b[2] - b[0]) / 2 - b[0], y - b[1]), txt, font=fnt, fill=cor)
        return y + (b[3] - b[1])

    y = int(16 * k)
    y = centro("SESSÃO", fonte("SF-Pro-Display-Medium.otf", 15 * k), y) + int(5 * k)
    y = centro("ESTRATÉGICA", fonte("SF-Pro-Display-Bold.otf", 19.5 * k), y) + int(7 * k)
    # pílula verde
    fg = fonte("SF-Pro-Display-Bold.otf", 20 * k)
    b = d.textbbox((0, 0), "GRATUITA", font=fg)
    pw, ph = (b[2] - b[0]) + int(16 * k), (b[3] - b[1]) + int(11 * k)
    d.rounded_rectangle((cx - pw / 2, y, cx + pw / 2, y + ph), int(5 * k), fill=(34, 197, 72, 255))
    d.text((cx - (b[2] - b[0]) / 2 - b[0], y + (ph - (b[3] - b[1])) / 2 - b[1]), "GRATUITA", font=fg, fill=branco)
    y += ph + int(9 * k)
    d.line((x0 + int(6 * k), y, x1 - int(6 * k), y), fill=(255, 255, 255, 150), width=max(1, int(1.2 * k)))
    y += int(8 * k)
    fa = fonte("SF-Pro-Display-Medium.otf", 13 * k)
    y = centro("APONTE A", fa, y) + int(4 * k)
    centro("CÂMERA", fa, y)

    img.alpha_composite(card, (sombra, sombra))
    img = img.resize((img.width // SS, img.height // SS), Image.LANCZOS)

    # QR em pixels inteiros por módulo, com 2 módulos de margem branca (+ a borda do quadro branco)
    bx, by, bq = (v // SS for v in caixa_qr)
    m = qr_matriz(url)
    n = m.shape[0]
    px = max(2, bq // (n + 4))
    lado = n * px
    qi = Image.fromarray(m).convert("L").resize((lado, lado), Image.NEAREST).convert("RGBA")
    img.alpha_composite(qi, (bx + (bq - lado) // 2, by + (bq - lado) // 2))
    return img


def conferir(png: Path, url: str) -> bool:
    im = cv2.imread(str(png), cv2.IMREAD_UNCHANGED)
    if im.shape[2] == 4:  # compõe sobre um fundo médio
        a = im[..., 3:4] / 255.0
        im = (im[..., :3] * a + 128 * (1 - a)).astype(np.uint8)
    for fator in (1.0, 0.8):  # lê também reduzido (vídeo um pouco menor que a tela cheia)
        t = cv2.resize(im, None, fx=fator, fy=fator, interpolation=cv2.INTER_AREA)
        lidos = {d.detectAndDecode(t)[0] for d in (cv2.QRCodeDetector(), cv2.QRCodeDetectorAruco())}
        val = url if url in lidos else next(iter(lidos - {""}), "")
        if val != url:
            print(f"[qr] NÃO leu a {fator:.0%}: {val!r}")
            return False
    return True


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("saida")
    ap.add_argument("--escala", type=float, default=1.3)
    ap.add_argument("--altura-video", type=int, default=1080)
    a = ap.parse_args()
    img = desenhar(a.url, a.escala, a.altura_video)
    img.save(a.saida)
    ok = conferir(Path(a.saida), a.url)
    print(f"{'ok' if ok else 'ERRO'}: {a.saida} {img.size} -> {a.url}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
