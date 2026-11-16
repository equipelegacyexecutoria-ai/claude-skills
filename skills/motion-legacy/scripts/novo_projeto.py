"""Cria um projeto novo de motion no estilo Legacy a partir do molde da skill.

uso: python novo_projeto.py <pasta_nova> <duracao_s>
- copia molde/ (index.html, fontes Urbanist, logos Legacy e Legacy Plan, hyperframes.json) para <pasta_nova>;
- ajusta a duração (data-duration do root e do áudio, const DUR);
- o áudio esperado é <pasta_nova>/assets/audio/mix.wav (gere com o mix_audio.py da skill motion-designer).
"""
import io, os, re, shutil, sys

dest, dur = sys.argv[1], float(sys.argv[2])
molde = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "molde")
if os.path.exists(dest) and os.listdir(dest):
    sys.exit(f"{dest} já existe e não está vazia")
shutil.copytree(molde, dest, dirs_exist_ok=True)
os.makedirs(os.path.join(dest, "assets", "audio"), exist_ok=True)
os.makedirs(os.path.join(dest, "assets", "video"), exist_ok=True)
p = os.path.join(dest, "index.html")
s = io.open(p, encoding="utf-8").read()
s = re.sub(r'data-duration="[\d.]+"', f'data-duration="{dur:g}"', s)
s = re.sub(r"const DUR = [\d.]+;", f"const DUR = {dur:g};", s)
io.open(p, "w", encoding="utf-8").write(s)
print("ok", os.path.abspath(dest))
