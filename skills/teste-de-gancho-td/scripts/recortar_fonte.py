"""Recorta do bruto o trecho real que vai para a sincronia da boca (vertical 1080x1920, sem som) e faz
uma tira de quadros para conferir a olho (mão longe da boca, olhando para a câmera, mesma roupa do reel).

Uso: python recortar_fonte.py <bruto> <início_s> <duração_s> <saída.mp4>      (GIRAR=auto|1|0)
     duração = duração da fala nova + 0,1 s (a ferramenta aceita até 30 s)
"""
import os, subprocess, sys
from pathlib import Path

bruto, ini, dur, saida = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), Path(sys.argv[4])
g = os.environ.get("GIRAR", "auto")
if g == "auto":
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                        "-of", "csv=p=0", bruto], capture_output=True, text=True).stdout.strip().split(",")
    g = "1" if int(r[0]) > int(r[1]) else "0"
vf = ("transpose=1," if g == "1" else "") + \
     "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920"
saida.parent.mkdir(parents=True, exist_ok=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ini:.3f}", "-t", f"{dur:.3f}", "-i", bruto, "-an",
                "-vf", vf, "-c:v", "libx264", "-crf", "14", "-preset", "slow", "-pix_fmt", "yuv420p", str(saida)],
               check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(saida), "-vf", "fps=1.5,scale=150:-1,tile=12x1",
                "-frames:v", "1", str(saida.with_suffix(".jpg"))], check=True)
print("ok:", saida, "| tira:", saida.with_suffix(".jpg"))
