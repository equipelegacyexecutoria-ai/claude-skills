"""Prévia rápida: o quadro final (1080x1920) de um instante do vídeo editado, montado direto do
bruto com o recorte e a legenda .ass — sem render completo. Para conferir tela, acento, sombra.

Uso: python previa_quadro.py <trabalho> <t1,t2,...> <saida.png> [--faixa]
     (--faixa: corta só a faixa de imagem; vários tempos viram uma folha)
"""
from __future__ import annotations

import subprocess
import sys
from io import BytesIO
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import FAIXA_H, FAIXA_W, FAIXA_Y0, FPS, H, W, ler_json, preparar_fontes  # noqa: E402


def quadro(trabalho: Path, t: float) -> Image.Image:
    corte = ler_json(trabalho / "corte.json")
    enq = ler_json(trabalho / "enquadramento.json")
    segs = corte["segmentos"]
    n = int(round(t * FPS))                       # quadro do vídeo editado
    t = n / FPS
    k = max(i for i, s in enumerate(segs) if s["dst_in"] <= t + 1e-6)
    s = segs[k]
    src = (s["frame_in"] + (n - round(s["dst_in"] * FPS))) / FPS
    cw, ch, x, y = enq.get("crops_segmento", {}).get(str(k), enq["crop"])
    vf = (f"crop={cw}:{ch}:{x}:{y},scale={FAIXA_W}:{FAIXA_H}:flags=lanczos,pad={W}:{H}:0:{FAIXA_Y0}:black,"
          f"setpts=PTS-STARTPTS+{t:.4f}/TB,ass=legenda.ass:fontsdir=fonts")
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(0.0, src - 0.5 / FPS):.4f}", "-i", corte["fonte"],
                        "-frames:v", "1", "-vf", vf, "-f", "image2pipe", "-vcodec", "png", "-"],
                       capture_output=True, check=True, cwd=trabalho)
    return Image.open(BytesIO(p.stdout)).convert("RGB")


def main() -> None:
    trabalho = Path(sys.argv[1]).resolve()
    tempos = [float(v) for v in sys.argv[2].split(",")]
    saida = Path(sys.argv[3])
    so_faixa = "--faixa" in sys.argv
    preparar_fontes(trabalho)
    ims = [quadro(trabalho, t) for t in tempos]
    if so_faixa:
        ims = [im.crop((0, FAIXA_Y0, W, FAIXA_Y0 + FAIXA_H)) for im in ims]
    if len(ims) == 1:
        ims[0].save(saida)
    else:
        cols = 2
        w, h = ims[0].size
        rows = (len(ims) + cols - 1) // cols
        sh = Image.new("RGB", (cols * w + (cols - 1) * 10, rows * h + (rows - 1) * 10), (60, 0, 60))
        for i, im in enumerate(ims):
            sh.paste(im, ((i % cols) * (w + 10), (i // cols) * (h + 10)))
        sh.save(saida)
    print(f"ok: {saida}")


if __name__ == "__main__":
    main()
