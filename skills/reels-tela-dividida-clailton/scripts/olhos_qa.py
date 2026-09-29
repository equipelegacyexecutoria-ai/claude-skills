"""Conferência da regra dos olhos (usuário, 28/09/2026) no vídeo final.

Enquadramento padrão = aberto; linha dos olhos padrão = timeline["linha_olhos"]. Em cada corte que
entra no zoom (fechado), mede os olhos (YuNet) no 1º quadro depois do corte e compara com a linha padrão
(só a altura). Grava qa/zoom_olhos.jpg com as 6 entradas de zoom mais longe da linha (quadro antes e
depois do corte, linha vermelha = linha padrão) e imprime a mediana e o máximo (px de 1920).

Uso: python olhos_qa.py <trabalho> <final.mp4>
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from td_comum import MODELO_ROSTO  # noqa: E402

LARG, ALT = 540, 960


def main() -> None:
    T, V = Path(sys.argv[1]), sys.argv[2]
    tl = json.loads((T / "timeline.json").read_text(encoding="utf-8"))
    fps, linha = tl["fps"], tl.get("linha_olhos")
    if linha is None:
        print("timeline sem linha_olhos (rode o plano_td de novo)")
        return
    det = cv2.FaceDetectorYN.create(str(MODELO_ROSTO), "", (LARG, ALT), 0.6, 0.3, 5000)

    def quadro(f: int) -> np.ndarray:
        p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{(f - 0.5) / fps:.4f}", "-i", V, "-frames:v", "1", "-vf",
                            f"scale={LARG}:{ALT}", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True)
        return np.frombuffer(p.stdout, np.uint8).reshape(ALT, LARG, 3).copy()

    def olhos(img: np.ndarray):
        _, fs = det.detect(img)
        if fs is None or not len(fs):
            return None
        f = max(fs, key=lambda f: f[2] * f[3])
        return (f[5] + f[7]) / 2 * 1920 / ALT

    medidas = []
    for p in tl["planos"]:
        if not (p["visivel"] and p["zoom"] == "fechado"):
            continue
        antes, depois = quadro(p["f0"] - 1), quadro(p["f0"])
        o = olhos(depois)
        if o is not None:
            medidas.append((abs(o - linha), p["f0"] / fps, antes, depois))
    if not medidas:
        print("sem entradas de zoom medidas")
        return
    d = np.array([m[0] for m in medidas])
    print(f"linha padrão dos olhos: {linha:.0f}px · {len(d)} entradas de zoom: distância dos olhos à linha no 1º "
          f"quadro depois do corte = mediana {np.median(d):.0f}px, máx {d.max():.0f}px (de 1920)")
    w_, h_ = 270, 480
    folha = Image.new("RGB", (2 * w_ * 3 + 20, (h_ + 30) * 2), (20, 20, 20))
    dr = ImageDraw.Draw(folha)
    for k, (dif, t, a, b) in enumerate(sorted(medidas, key=lambda m: -m[0])[:6]):
        r, c = divmod(k, 3)
        x0, y0 = c * (2 * w_ + 10), r * (h_ + 30)
        for j, img in enumerate((a, b)):
            im = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).resize((w_, h_))
            yy = linha / 1920 * h_
            ImageDraw.Draw(im).line([(0, yy), (w_, yy)], fill=(255, 40, 40), width=2)
            folha.paste(im, (x0 + j * w_, y0 + 30))
        dr.text((x0 + 4, y0 + 6), f"{t:.1f}s corte para o zoom (olhos a {dif:.0f}px da linha)", fill=(255, 220, 0))
    (T / "qa").mkdir(exist_ok=True)
    folha.save(T / "qa" / "zoom_olhos.jpg", quality=88)
    print("folha:", T / "qa" / "zoom_olhos.jpg")


if __name__ == "__main__":
    main()
