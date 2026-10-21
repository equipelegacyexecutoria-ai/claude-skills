# Cria o projeto HyperFrames de um Motion Dinâmico e copia fontes, textura de grão e o kit de efeitos sonoros.
# uso: python novo_projeto.py "<Desktop>/Projetos Edições/Motion Designer/videos/<nome>"
import os, shutil, subprocess, sys

DEST = os.path.abspath(sys.argv[1])
SK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SFX = os.path.join(os.path.expanduser("~"), ".claude", "skills", "media-use", "audio", "assets", "sfx")
if not os.path.exists(os.path.join(DEST, "hyperframes.json")):
    pai, nome = os.path.split(DEST)
    os.makedirs(pai, exist_ok=True)
    subprocess.run(f'npx hyperframes init "{nome}" --non-interactive --example=blank', cwd=pai, shell=True, check=True)
for sub in ("fonts", "fx", "img", "partes", "audio/sfx", "audio/musicas"):
    os.makedirs(os.path.join(DEST, "assets", sub), exist_ok=True)
for f in os.listdir(os.path.join(SK, "assets", "fonts")):
    shutil.copy2(os.path.join(SK, "assets", "fonts", f), os.path.join(DEST, "assets", "fonts", f))
shutil.copy2(os.path.join(SK, "assets", "fx", "grao.png"), os.path.join(DEST, "assets", "fx", "grao.png"))
for f in os.listdir(SFX):
    if f.endswith(".mp3"):
        shutil.copy2(os.path.join(SFX, f), os.path.join(DEST, "assets", "audio", "sfx", f))
for f in os.listdir(os.path.join(SK, "assets", "sfx")):
    shutil.copy2(os.path.join(SK, "assets", "sfx", f), os.path.join(DEST, "assets", "audio", "sfx", f))
print("ok", DEST)
