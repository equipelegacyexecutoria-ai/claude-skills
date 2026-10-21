# Mixagem do Motion Dinâmico: voz + uma trilha por emoção (com cruzamento) + os efeitos anotados pelo gerador (sfx.json).
# Mede o volume de cada arquivo e iguala: voz em -20 LUFS, música em -33 (+ajuste dB por trilha), depois -14 LUFS no final.
# uso: python montar_mix.py <projeto> trilhas.json
#   trilhas.json = {"duracao": 73.6, "trilhas": [{"arquivo": "musicas/a.mp3", "entra": 0, "sai": 25.0, "inicio_no_arquivo": 0, "ajuste": 0}, ...],
#                   "efeitos_extra": [{"arquivo": "sfx/x.mp3", "momento": 40.6, "volume": 0.5}]}
#   Trilhas vizinhas se cruzam: a seguinte entra 0,8 s antes de a anterior sair (fade de saída/entrada automáticos).
import json, os, re, subprocess, sys
import numpy as np, soundfile as sf

PROJ, CFG = sys.argv[1], json.load(open(sys.argv[2], encoding="utf-8"))
AUD = os.path.join(PROJ, "assets", "audio")
MIX = os.path.join(os.path.expanduser("~"), ".claude", "skills", "motion-designer", "scripts", "mix_audio.py")


def lufs(p):
    r = subprocess.run(["ffmpeg", "-nostats", "-i", p, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True)
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    return float(m[-1]) if m else -20.0


def pico(p):
    try:
        d, sr = sf.read(p, always_2d=True)
    except Exception:  # mp3 sem suporte: decodifica com ffmpeg
        r = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", "48000", "-f", "f32le", "-"], capture_output=True)
        d, sr = np.frombuffer(r.stdout, np.float32)[:, None], 48000
    return float(np.argmax(np.abs(d).max(1)) / sr)


g = lambda alvo, atual: round(10 ** ((alvo - atual) / 20), 4)
voz = os.path.join(AUD, "voz.wav")
trilhas, X = [], 0.8
for i, t in enumerate(CFG["trilhas"]):
    p = os.path.join(AUD, t["arquivo"])
    entra = t["entra"] - (X if i > 0 else 0)
    trilhas.append({"arquivo": t["arquivo"], "inicio_no_arquivo": max(0, t.get("inicio_no_arquivo", 0) - (X if i > 0 else 0)), "entra": max(0, entra),
                    "sai": t["sai"], "volume": g(-33 + t.get("ajuste", 0), lufs(p)), "fade_entrada": X if i > 0 else 0.3,
                    "fade_saida": X if i < len(CFG["trilhas"]) - 1 else 1.4})
efeitos, cache = [], {}
lista = json.load(open(os.path.join(AUD, "sfx.json"), encoding="utf-8")) + CFG.get("efeitos_extra", [])
for e in lista:
    p = os.path.join(AUD, e["arquivo"])
    if e["arquivo"] not in cache:
        cache[e["arquivo"]] = (pico(p), lufs(p))
    pk, lv = cache[e["arquivo"]]
    efeitos.append({"arquivo": e["arquivo"], "momento": e["momento"], "pico": pk, "volume": round(g(-24, lv) * e.get("volume", 0.5), 4)})
cfg = {"duracao": CFG["duracao"], "saida": "mix.wav", "voz": {"arquivo": "voz.wav", "volume": g(-20, lufs(voz))},
       "trilhas": trilhas, "abaixar_musica_sob_voz": {"threshold": 0.05, "ratio": 2.5}, "efeitos": efeitos, "loudness": -14}
json.dump(cfg, open(os.path.join(AUD, "mix.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
subprocess.run([sys.executable, MIX, os.path.join(AUD, "mix.json")], check=True)
print("ok", len(trilhas), "trilhas,", len(efeitos), "efeitos")
