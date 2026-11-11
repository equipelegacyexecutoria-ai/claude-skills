"""Legendas separadas em FUNDO VERDE (chroma key) para o editor montar por cima no Premiere (usuário, 06/11 e 11/11/2026).

  python legenda_verde.py <trabalho> <saida.mov> [--ate <s>] [--sem-cta]

Usa o legenda.ass do trabalho (o mesmo que foi queimado no vídeo, mesma posição, animação e sombra v3) sobre verde puro
#00FF00, 1080x1920, 29,97 fps, codec Animation (qtrle, sem perda: a borda da letra não borra no recorte), .mov.
  --ate <s>   corta tudo a partir desse segundo (NV_CTA: o início da animação, que cobre a legenda queimada)
  --sem-cta   tira o "ME SIGA PARA MAIS CONTEÚDOS" digitado do final
A duração é a do vídeo da novela (render_info.json ou o fim da última legenda).
"""
import json, re, subprocess, sys
from pathlib import Path

T = Path(sys.argv[1]).resolve()
saida = Path(sys.argv[2]).resolve()
ate = float(sys.argv[sys.argv.index("--ate") + 1]) if "--ate" in sys.argv else None
sem_cta = "--sem-cta" in sys.argv


def seg(s):
    h, m, x = s.split(":")
    return int(h) * 3600 + int(m) * 60 + float(x)


def fmt(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t - h * 3600 - m * 60
    return f"{h}:{m:02d}:{s:05.2f}"


linhas, fim, n_tirou = [], 0.0, 0
for ln in (T / "legenda.ass").read_text(encoding="utf-8").splitlines():
    if ln.startswith("Dialogue:"):
        p = ln.split(",", 9)
        a, b = seg(p[1]), seg(p[2])
        texto = re.sub(r"\{[^}]*\}", "", p[9])
        if sem_cta and ("Inter" in p[3] or "CTA" in p[3].upper() or "ME SIGA" in texto or "CONTEÚDOS COMO" in texto):
            n_tirou += 1
            continue
        if ate is not None:
            if a >= ate:
                n_tirou += 1
                continue
            if b > ate:
                p[2] = fmt(ate)
                b = ate
        fim = max(fim, b)
        ln = ",".join(p)
    linhas.append(ln)
ass = T / "legenda_verde.ass"
ass.write_text("\n".join(linhas) + "\n", encoding="utf-8")

dur = ate
if dur is None:
    ri = T / "render_info.json"
    info = json.loads(ri.read_text(encoding="utf-8")) if ri.exists() else {}
    q = int(info.get("quadros_fala") or 0) + int(info.get("quadros_cta") or 0)
    dur = q * 1001 / 30000 if q else fim + 0.5
    if sem_cta and info.get("quadros_fala"):
        dur = int(info["quadros_fala"]) * 1001 / 30000
saida.parent.mkdir(parents=True, exist_ok=True)
cmd = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=0x00FF00:s=1080x1920:r=30000/1001:d={dur:.3f}",
       "-vf", "ass=legenda_verde.ass:fontsdir=fonts", "-c:v", "qtrle", "-pix_fmt", "rgb24", "-an", str(saida)]
subprocess.run(cmd, cwd=T, check=True)
print(f"ok: {saida} ({dur:.2f} s; {n_tirou} linhas de legenda tiradas)")
