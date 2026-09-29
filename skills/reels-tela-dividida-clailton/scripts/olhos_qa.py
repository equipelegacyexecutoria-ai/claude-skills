"""Conferência da regra "todo zoom mantém os olhos na mesma altura" (usuário, 28/09/2026) no vídeo final.

Mede os olhos (YuNet) 2 quadros antes e 2 depois de cada troca de zoom (aberto <-> fechado) e ao longo
de cada zoom animado; grava qa/zoom_olhos.jpg com as 6 trocas de maior diferença (linha vermelha na
altura dos olhos do quadro de antes) e imprime a mediana e o máximo (px de 1920).
Diferença que sobra = a cabeça mudou de altura entre os dois momentos (o plano_td já corrige o que
o bruto deixa, com ajuste animado discreto no fechado).

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
    fps = tl["fps"]
    det = cv2.FaceDetectorYN.create(str(MODELO_ROSTO), "", (LARG, ALT), 0.6, 0.3, 5000)

    def quadro(t: float) -> np.ndarray:
        p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", V, "-frames:v", "1", "-vf",
                            f"scale={LARG}:{ALT}", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True)
        return np.frombuffer(p.stdout, np.uint8).reshape(ALT, LARG, 3).copy()

    def olhos(img: np.ndarray):
        _, fs = det.detect(img)
        if fs is None or not len(fs):
            return None
        f = max(fs, key=lambda f: f[2] * f[3])
        return (f[5] + f[7]) / 2 * 1920 / ALT

    pl = [p for p in tl["planos"] if p["visivel"] and p["zoom"] in ("aberto", "fechado")]
    pares = []
    for a, b in zip(pl, pl[1:]):
        if a["f1"] != b["f0"] or a["zoom"] == b["zoom"]:
            continue
        qa_, qb = quadro((b["f0"] - 2) / fps), quadro((b["f0"] + 2) / fps)
        oa, ob = olhos(qa_), olhos(qb)
        if oa is not None and ob is not None:
            pares.append((abs(ob - oa), b["f0"] / fps, a["zoom"], b["zoom"], qa_, qb, oa))
    if not pares:
        print("sem trocas de zoom medidas")
        return
    d = np.array([p[0] for p in pares])
    print(f"{len(d)} trocas de zoom: diferença na altura dos olhos mediana {np.median(d):.0f}px, "
          f"máx {d.max():.0f}px (de 1920)")
    for p in (x for x in pl if x.get("escala")):
        ys = [y for y in (olhos(quadro((p["f0"] + k) / fps)) for k in range(0, p["f1"] - p["f0"], 6)) if y]
        if ys:
            print(f"zoom animado {p['f0'] / fps:.2f}s: olhos entre {min(ys):.0f} e {max(ys):.0f}px (cabeça + zoom)")
    w_, h_ = 270, 480
    sel = sorted(pares, key=lambda x: -x[0])[:6]
    folha = Image.new("RGB", (2 * w_ * 3 + 20, (h_ + 30) * 2), (20, 20, 20))
    dr = ImageDraw.Draw(folha)
    for k, (dif, t, za, zb, a, b, oa) in enumerate(sel):
        r, c = divmod(k, 3)
        x0, y0 = c * (2 * w_ + 10), r * (h_ + 30)
        for j, img in enumerate((a, b)):
            im = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).resize((w_, h_))
            yy = oa / 1920 * h_
            ImageDraw.Draw(im).line([(0, yy), (w_, yy)], fill=(255, 40, 40), width=2)
            folha.paste(im, (x0 + j * w_, y0 + 30))
        dr.text((x0 + 4, y0 + 6), f"{t:.1f}s {za} -> {zb}  (olhos {dif:.0f}px)", fill=(255, 220, 0))
    (T / "qa").mkdir(exist_ok=True)
    folha.save(T / "qa" / "zoom_olhos.jpg", quality=88)
    print("folha:", T / "qa" / "zoom_olhos.jpg")


if __name__ == "__main__":
    main()
