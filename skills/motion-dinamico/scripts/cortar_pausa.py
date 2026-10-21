# Corta uma pausa (silêncio longo do especialista) do vídeo já renderizado, sem refazer as cenas.
# A imagem e a voz perdem o trecho [ini, fim); os efeitos sonoros depois do corte andam junto; a música NÃO é cortada
# (a mixagem é refeita com as trilhas contínuas, só com os tempos ajustados), então não há pulo na trilha.
# uso: python cortar_pausa.py <projeto> <render.mp4> <ini> <fim> <trilhas.json> <saida.mp4>
#   ini/fim em segundos do vídeo renderizado (arredondados para o quadro, 30 fps). Antes de renderizar, faça o texto que
#   estava na tela sair antes de `ini` e o próximo entrar perto de `fim` (senão o corte pega a animação no meio).
import json, os, shutil, subprocess, sys, tempfile
import numpy as np, soundfile as sf

PROJ, VIDEO, INI, FIM, TRILHAS, SAIDA = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), sys.argv[5], sys.argv[6]
FPS = 30
f0, f1 = round(INI * FPS), round(FIM * FPS)
INI, FIM = f0 / FPS, f1 / FPS
D = FIM - INI
S = os.path.dirname(os.path.abspath(__file__))


def mover(t):
    """Tempo da versão longa → tempo da versão cortada."""
    return t if t <= INI else (INI if t < FIM else t - D)


tmp = tempfile.mkdtemp(prefix="cortar_pausa_")
aud = os.path.join(tmp, "assets", "audio")
shutil.copytree(os.path.join(PROJ, "assets", "audio"), aud)

# voz: tira o trecho com 10 ms de fade nas pontas
a, sr = sf.read(os.path.join(aud, "voz.wav"))
i0, i1, x = int(INI * sr), int(FIM * sr), int(0.01 * sr)
antes, depois = a[:i0].copy(), a[i1:].copy()
rampa = np.linspace(1, 0, x)[:, None] if a.ndim > 1 else np.linspace(1, 0, x)
antes[-x:] *= rampa; depois[:x] *= rampa[::-1]
sf.write(os.path.join(aud, "voz.wav"), np.concatenate([antes, depois]), sr)

# efeitos: os que caem dentro do corte saem; os de depois andam junto
efeitos = json.load(open(os.path.join(aud, "sfx.json"), encoding="utf-8"))
novos = [dict(e, momento=round(mover(e["momento"]), 3)) for e in efeitos if not (INI < e["momento"] < FIM)]
json.dump(novos, open(os.path.join(aud, "sfx.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# trilhas: tempos ajustados, música contínua
cfg = json.load(open(TRILHAS, encoding="utf-8"))
cfg["duracao"] = round(cfg["duracao"] - D, 3)
for t in cfg["trilhas"]:
    t["entra"], t["sai"] = round(mover(t["entra"]), 3), round(mover(t["sai"]), 3)
for e in cfg.get("efeitos_extra", []):
    e["momento"] = round(mover(e["momento"]), 3)
tj = os.path.join(tmp, "trilhas.json")
json.dump(cfg, open(tj, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
subprocess.run([sys.executable, os.path.join(S, "montar_mix.py"), tmp, tj], check=True)

# imagem: tira os quadros do corte e junta com a mixagem nova
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", VIDEO, "-i", os.path.join(aud, "mix.wav"),
                "-vf", f"select='not(between(n\\,{f0}\\,{f1 - 1}))',setpts=N/{FPS}/TB", "-map", "0:v", "-map", "1:a",
                "-c:v", "libx264", "-crf", "14", "-preset", "slow", "-pix_fmt", "yuv420p", "-r", str(FPS),
                "-c:a", "aac", "-b:a", "320k", "-shortest", SAIDA], check=True)
shutil.rmtree(tmp, ignore_errors=True)
print(f"ok corte {INI:.3f}–{FIM:.3f} ({D:.2f} s) -> {SAIDA}")
