"""Balanço de branco por vídeo (usuário, 09/10/2026: "a cor desse vídeo ficou bem esverdeada, ajuste o white balance").

Mede os quase-brancos da imagem (parede branca do estúdio: claros, pouco saturados, sem estourar) e calcula ganhos
R/G/B que levam esse branco ao branco QUENTE dos vídeos aprovados (R/G 1,015 e B/G 0,975, medidos no "Quem Tem
Poucos Amigos" v2), mantendo o brilho. Grava <trabalho>/cor.txt; o render_final.py aplica sozinho (em RGB, BT.709).

Uso: python balanco_branco.py <trabalho> <video ou bruto> [--forca 1.0]
     (--forca < 1 corrige só parte do desvio; apague cor.txt para voltar à cor original)
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ALVO_RG, ALVO_BG = 1.015, 0.975


def medir(video: str, faixa: bool) -> np.ndarray:
    vf = "fps=1/4" + (",crop=1080:864:0:528" if faixa else "") + ",scale=540:-2"
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                       capture_output=True, check=True)
    w = 540
    x = np.frombuffer(r.stdout, np.uint8).astype(float).reshape(-1, 3)
    lum, sat = x.mean(1), x.max(1) - x.min(1)
    m = (lum > 170) & (lum < 245) & (sat < 40)
    if m.sum() < 5000:
        raise SystemExit("poucos pixels brancos para medir (sem parede branca no quadro?) — ajuste na mão")
    return x[m].mean(0)


def main() -> None:
    T, video = Path(sys.argv[1]), sys.argv[2]
    forca = float(sys.argv[sys.argv.index("--forca") + 1]) if "--forca" in sys.argv else 1.0
    faixa = "EDITADO" in Path(video).name                   # vídeo final: mede só a faixa de imagem
    r, g, b = medir(video, faixa)
    kr = (ALVO_RG * g / r) ** forca                         # ganhos relativos ao verde
    kb = (ALVO_BG * g / b) ** forca
    kg = 1 / (0.2126 * kr + 0.7152 + 0.0722 * kb)           # mantém o brilho (luma BT.709)
    kr, kb = kr * kg, kb * kg
    filtro = f"colorchannelmixer=rr={kr:.4f}:gg={kg:.4f}:bb={kb:.4f}"
    (T / "cor.txt").write_text(filtro + "\n", encoding="utf-8")
    print(json.dumps({"branco_medido_rgb": [round(r, 1), round(g, 1), round(b, 1)],
                      "ganhos": {"r": round(kr, 4), "g": round(kg, 4), "b": round(kb, 4)}, "cor.txt": filtro}))


if __name__ == "__main__":
    main()
