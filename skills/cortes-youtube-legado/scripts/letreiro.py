"""Letreiro discreto (lower third) no estilo do card da CTA: caixa azul em degradê, etiqueta verde opcional.

Para que serve (só quando ajuda quem assiste de fora da aula, nunca enfeite):
  - episódio que é uma LISTA: "FINANCEIRO · 1/15  Aumentar lucratividade" (o slide de letra miúda não se lê no celular);
  - quem é a pessoa da história na abertura: "Sylvester Stallone, antes de Rocky";
  - o que está desfocado: "A LUTA QUE INSPIROU ROCKY  Muhammad Ali x Chuck Wepner, 1975".
Nunca é legenda da fala. No plano.json, por episódio:
  "letreiros": [{"frase": "no financeiro, vamos aumentar a lucratividade", "perto": "01:57:33",
                 "tag": "FINANCEIRO · 1/15", "texto": "Aumentar lucratividade"},
                {"aula": "02:56:29.1", "onde": "abertura", "texto": "Sylvester Stallone, antes de Rocky", "dur": 5}]
Dura "dur" s (padrão 6) ou até o próximo letreiro. Fica embaixo à esquerda, alinhado com o slide (x 96), na
faixa escura abaixo do slide no layout "slide + janela".

Teste: python letreiro.py "Aumentar lucratividade" saida.png --tag "FINANCEIRO · 1/15"
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qr_card import SS, fonte  # noqa: E402

X, MARGEM_BAIXO, LARG_MAX = 96, 34, 1190      # em 1080p


def desenhar(texto: str, tag: str | None = None, altura_video: int = 1080) -> tuple[Image.Image, int]:
    """Devolve (PNG com sombra, margem da sombra em px do vídeo)."""
    k = altura_video / 1080 * SS
    H, R, pad = int(72 * k), int(14 * k), int(22 * k)
    t_px = 34
    while True:
        ft = fonte("SF-Pro-Display-Bold.otf", t_px * k)
        fg = fonte("SF-Pro-Display-Bold.otf", 21 * k)
        tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
        bt = tmp.textbbox((0, 0), texto, font=ft)
        bg = tmp.textbbox((0, 0), tag, font=fg) if tag else (0, 0, 0, 0)
        pw = (bg[2] - bg[0]) + int(22 * k) if tag else 0
        W = pad + (pw + int(16 * k) if tag else 0) + (bt[2] - bt[0]) + pad
        if W <= LARG_MAX * k or t_px <= 22:
            break
        t_px -= 2
    sombra = int(14 * k)
    img = Image.new("RGBA", (W + 2 * sombra, H + 2 * sombra), (0, 0, 0, 0))
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((sombra, sombra + int(3 * k), sombra + W, sombra + H + int(3 * k)),
                                         R, fill=(0, 0, 0, 120))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(int(8 * k))))

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
    branco = (255, 255, 255, 255)
    x = pad
    if tag:
        ph = (bg[3] - bg[1]) + int(16 * k)
        y0 = (H - ph) / 2
        d.rounded_rectangle((x, y0, x + pw, y0 + ph), int(6 * k), fill=(34, 197, 72, 255))
        d.text((x + (pw - (bg[2] - bg[0])) / 2 - bg[0], y0 + (ph - (bg[3] - bg[1])) / 2 - bg[1]), tag,
               font=fg, fill=branco)
        x += pw + int(16 * k)
    d.text((x - bt[0], (H - (bt[3] - bt[1])) / 2 - bt[1]), texto, font=ft, fill=branco)
    img.alpha_composite(card, (sombra, sombra))
    img = img.resize((img.width // SS, img.height // SS), Image.LANCZOS)
    return img, sombra // SS


def posicao(img: Image.Image, sombra: int, altura_video: int = 1080) -> tuple[int, int]:
    """Canto do PNG (com a sombra) no quadro: caixa em x 96, 34 px acima da borda de baixo."""
    s = altura_video / 1080
    h_caixa = img.height - 2 * sombra
    return round(X * s) - sombra, round(altura_video - MARGEM_BAIXO * s - h_caixa) - sombra


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("texto")
    ap.add_argument("saida")
    ap.add_argument("--tag")
    ap.add_argument("--altura-video", type=int, default=1080)
    a = ap.parse_args()
    img, sombra = desenhar(a.texto, a.tag, a.altura_video)
    img.save(a.saida)
    print(f"ok: {a.saida} {img.size} posição {posicao(img, sombra, a.altura_video)}")


if __name__ == "__main__":
    main()
