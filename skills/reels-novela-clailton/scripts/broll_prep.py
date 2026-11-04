"""Prepara B-roll para a faixa da novela (1080x864), com o filtro pelicula da tela dividida.
uso: broll_prep.py <saida.mp4> <fonte> <inicio_fonte> <duracao> [forca=1.0]"""
import sys, subprocess, os
import numpy as np
sys.path.insert(0, os.path.expanduser('~/.claude/skills/reels-tela-dividida-clailton/scripts'))
from estilo_td import Estilo
out, src, ss, dur = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
forca = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
W, H = 1080, 864
n = int(round(dur * 30000 / 1001))
dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', str(ss), '-i', src, '-vf',
    f'fps=30000/1001,scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},format=rgb24',
    '-frames:v', str(n), '-f', 'rawvideo', '-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
    '-r', '30000/1001', '-i', '-', '-c:v', 'libx264', '-crf', '10', '-preset', 'medium', '-pix_fmt', 'yuv420p', out],
    stdin=subprocess.PIPE)
e = Estilo(forca, w=W, h=H)
k = 0
while True:
    b = dec.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    fr = np.frombuffer(b, np.uint8).reshape(H, W, 3)
    enc.stdin.write(e.aplicar(fr, k).tobytes()); k += 1
last = fr if k else None
while k < n and last is not None:
    enc.stdin.write(e.aplicar(last, k).tobytes()); k += 1
enc.stdin.close(); enc.wait(); dec.wait()
print(out, k, 'quadros')
