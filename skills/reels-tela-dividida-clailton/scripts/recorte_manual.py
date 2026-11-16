"""Recorte MANUAL de cena (16/11/2026, Fim do Mundo v3: "você erra constantemente o enquadramento").
O reenquadramento automático escolhe mal quando o assunto é largo (celular + mão, duas pessoas, ação no canto).
Aqui quem decide é você, olhando o quadro inteiro: centro x do assunto (0-1), início e duração.
Sai um mp4 já no formato do layout, para usar no plano com `arquivo "..."` (o render não recorta de novo).

uso: python recorte_manual.py <origem> <saida.mp4> <inicio_s> <dur_s> <cheia|dividida> <cx 0-1> [cy 0-1]
- cheia: 1080x1920 (cabem ~32% da largura de um vídeo 16:9: se o assunto é mais largo, use dividida)
- dividida: 1080x768 (cabem ~79% da largura de um 16:9)
- tarja preta de filme (2,39:1) é tirada antes (cropdetect).
Folha para decidir o cx: scripts/quadros_inteiros.py (régua 0-100% sobre o quadro inteiro)."""
import re, subprocess, sys

src, out, ini, dur, lay, cx = sys.argv[1:7]
cy = float(sys.argv[7]) if len(sys.argv) > 7 else 0.5
ini, dur, cx = float(ini), float(dur), float(cx)
W, H = (1080, 1920) if lay == "cheia" else (1080, 768)
info = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height",
                       "-of", "csv=p=0", src], capture_output=True, text=True).stdout.strip().split(",")
iw, ih = int(info[0]), int(info[1])
# tarja preta
r = subprocess.run(["ffmpeg", "-ss", str(ini), "-i", src, "-t", str(min(dur, 2)), "-vf", "cropdetect=24:2:0",
                    "-f", "null", "-"], capture_output=True, text=True).stderr
m = re.findall(r"crop=(\d+):(\d+):(\d+):(\d+)", r)
ax, ay, aw, ah = 0, 0, iw, ih
if m:
    cw, ch, cxx, cyy = map(int, m[-1])
    if ch < ih * 0.95 and cw > iw * 0.9:
        ax, ay, aw, ah = cxx, cyy, cw, ch
alvo = W / H
if aw / ah > alvo:                     # mais largo que o alvo: corta na largura
    ch2 = ah; cw2 = int(round(ah * alvo / 2) * 2)
    x = int(min(max(cx * aw - cw2 / 2, 0), aw - cw2)) + ax; y = ay
else:                                  # mais alto: corta na altura
    cw2 = aw; ch2 = int(round(aw / alvo / 2) * 2)
    y = int(min(max(cy * ah - ch2 / 2, 0), ah - ch2)) + ay; x = ax
vf = f"crop={cw2}:{ch2}:{x}:{y},scale={W}:{H}:flags=lanczos,setsar=1"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(ini), "-i", src, "-t", str(dur), "-an", "-vf", vf,
                "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p", out], check=True)
print(f"ok {out}  recorte {cw2}x{ch2}+{x}+{y} de {iw}x{ih} (ampliação {W / cw2:.2f}x)")
