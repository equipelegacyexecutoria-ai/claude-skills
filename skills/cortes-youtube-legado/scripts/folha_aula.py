"""Folha de quadros espalhados de uma ou mais aulas (para ver se é a versão com slide ou a câmera crua).

Uso: python folha_aula.py <saida.jpg> <video1> [<video2> ...] [--n 12]
Cada vídeo vira uma faixa de N quadros (320 px) com o nome e a duração; funciona direto no G: (lê só os
pedaços necessários). Versão boa = quadros com slide grande + Clailton numa janela à direita (fundo
vermelho escuro) e vinheta "LEGADO EMPRESARIAL"; câmera crua = só auditório.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import SKILL, hms, sonda  # noqa: E402


def quadro(video: str, t: float):
    p = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{t:.1f}", "-i", video, "-frames:v", "1",
                        "-vf", "scale=320:180", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True)
    img = cv2.imdecode(np.frombuffer(p.stdout, np.uint8), cv2.IMREAD_COLOR)
    return img if img is not None else np.zeros((180, 320, 3), np.uint8)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("saida")
    ap.add_argument("videos", nargs="+")
    ap.add_argument("--n", type=int, default=12)
    a = ap.parse_args()
    fnt = ImageFont.truetype(str(SKILL / "fonts" / "SF-Pro-Display-Bold.otf"), 18)
    faixas = []
    for v in a.videos:
        dur = float(sonda(Path(v))["format"]["duration"])
        imgs = [quadro(v, dur * (k + 1) / (a.n + 1)) for k in range(a.n)]
        cols = 6
        linhas = (a.n + cols - 1) // cols
        F = Image.new("RGB", (cols * 320, linhas * 180 + 28), (20, 20, 20))
        ImageDraw.Draw(F).text((6, 4), f"{Path(v).name} · {hms(dur)}", fill="yellow", font=fnt)
        for k, im in enumerate(imgs):
            F.paste(Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)), ((k % cols) * 320, 28 + (k // cols) * 180))
        faixas.append(F)
        print(f"ok: {Path(v).name} ({hms(dur)})", flush=True)
    W = max(f.width for f in faixas)
    out = Image.new("RGB", (W, sum(f.height for f in faixas)), "black")
    y = 0
    for f in faixas:
        out.paste(f, (0, y))
        y += f.height
    out.save(a.saida, quality=85)
    print(f"folha: {a.saida}")


if __name__ == "__main__":
    main()
