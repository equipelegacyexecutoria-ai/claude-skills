"""Gera audio/mix.json da versão e mixa (voz + música + efeitos) em projeto/assets/audio/mix.wav.

uso: python gerar_mix.py <pasta_da_versao> --musica <arquivo.mp3> --cliques "23.86,31.18,..."
        [--virada 16.0] [--volume 0.05] [--chave-virada agora]

- --cliques: tempos dos cliques/toques (window.__CLIQUES da página; ver SKILL.md, passo 7).
- --virada: segundo da MÚSICA em que ela cresce; ele cai na palavra --chave-virada (padrão "agora", a virada
  "Agora, você entra direto pelo..."). Adaptive Flow (Kerei, Artlist) cresce em 16,0 s.
- --volume 0.05 deixou a música ~11 dB abaixo da voz da Lívia (aprovado). Música mais alta no arquivo: baixe o valor.
Efeitos baixos: whoosh nas viagens da câmera, clique suave em cada clique, "data click" no aviso de check-in, logo no fecho.
"""
import argparse, io, json, os, subprocess, sys

SK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SFX = os.path.join(SK, "molde", "assets", "audio", "sfx").replace("\\", "/")
ap = argparse.ArgumentParser()
ap.add_argument("pasta")
ap.add_argument("--musica", required=True)
ap.add_argument("--cliques", required=True)
ap.add_argument("--virada", type=float, default=16.0)
ap.add_argument("--volume", type=float, default=0.05)
ap.add_argument("--chave-virada", default="agora")
a = ap.parse_args()
d = os.path.abspath(a.pasta)
tx = json.load(io.open(os.path.join(d, "audio", "voz.wav.tx.json"), encoding="utf-8"))
cfg = json.load(io.open(os.path.join(d, "k.json"), encoding="utf-8"))
TT = tx["TT"]
for x, y in sorted(cfg.get("remover", []), reverse=True):
    del TT[x:y + 1]
K = cfg["K"]
T = lambda k: TT[K[k]] if k in K else None
dur = float(cfg.get("duracao") or round(TT[-1] + 3.0))


def e(arq, t, vol, pico=0.0):
    return {"arquivo": f"{SFX}/{arq}", "momento": round(t, 2), "pico": pico, "volume": vol}


ef = []
for k, extra, vol in [("antes", 0.2, 0.08), ("agora", 0.55, 0.07), ("vou", 0.2, 0.07)]:
    if T(k) is not None:
        ef.append(e("air_motion_whoosh.wav", T(k) + extra, vol, 0.813))
if T("pronto1") is not None:
    ef.append(e("data_point_click.wav", T("pronto1"), 0.10, 0.062))
if T("dentro") is not None:
    ef.append(e("data_point_click.wav", T("dentro") - 0.2, 0.10, 0.062))
if T("nos") is not None:
    ef.append(e("logo.wav", T("nos") + 0.35, 0.2))
ef += [e("soft_ui_click.wav", float(t), 0.11, 0.072) for t in a.cliques.split(",") if t.strip()]
tv = T(a.chave_virada) or 0.0
mix = {"duracao": dur, "saida": "../projeto/assets/audio/mix.wav",
       "voz": {"arquivo": "voz.wav", "atempo": 1.0, "inicio": 0.25, "volume": 1.0},
       "trilhas": [{"arquivo": os.path.abspath(a.musica).replace("\\", "/"), "inicio_no_arquivo": round(max(0.0, a.virada - tv), 2),
                    "entra": 0, "sai": dur, "volume": a.volume, "fade_saida": 2.5, "fade_entrada": 0.4}],
       "abaixar_musica_sob_voz": {"threshold": 0.05, "ratio": 1.6}, "efeitos": ef}
cam = os.path.join(d, "audio", "mix.json")
json.dump(mix, io.open(cam, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
mixer = os.path.join(os.path.expanduser("~"), ".claude", "skills", "motion-designer", "scripts", "mix_audio.py")
subprocess.run([sys.executable, mixer, cam], check=True)
print("ok", cam)
