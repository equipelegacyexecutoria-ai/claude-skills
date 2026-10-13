"""Baixa (se for link) e corta um vídeo de referência em quadros a cada 0,5 s, com o tempo gravado,
montando folhas 6x6 para estudar a gramática do motion.

Uso: python quadros_referencia.py <url-ou-arquivo> --saida <pasta> [--intervalo 0.5] [--largura 480]
Saída: <pasta>/f_###.jpg e <pasta>/folha_N.jpg
"""
import argparse, glob, os, shutil, subprocess

p = argparse.ArgumentParser()
p.add_argument("fonte")
p.add_argument("--saida", required=True)
p.add_argument("--intervalo", type=float, default=0.5)
p.add_argument("--largura", type=int, default=480)
a = p.parse_args()

os.makedirs(a.saida, exist_ok=True)
video = a.fonte
if a.fonte.startswith("http"):
    destino = os.path.join(a.saida, "referencia.%(ext)s")
    subprocess.run(["yt-dlp", "-q", "-S", "res:720", "-o", destino, a.fonte], check=True)
    video = sorted(glob.glob(os.path.join(a.saida, "referencia.*")))[0]

fonte = "C\\:/Windows/Fonts/arial.ttf" if os.name == "nt" else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
fps = 1 / a.intervalo
filtro = (f"fps={fps},scale={a.largura}:-2,"
          f"drawtext=fontfile='{fonte}':text='%{{pts\\:hms}}':x=8:y=8:fontsize=20:fontcolor=red:box=1:boxcolor=black@0.5")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vf", filtro, os.path.join(a.saida, "f_%03d.jpg")], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "1", "-i", os.path.join(a.saida, "f_%03d.jpg"),
                "-vf", "tile=6x6", os.path.join(a.saida, "folha_%d.jpg")], check=True)
n = len(glob.glob(os.path.join(a.saida, "f_*.jpg")))
print(f"{n} quadros; folhas:", sorted(glob.glob(os.path.join(a.saida, "folha_*.jpg"))))
