"""Músicas favoritas do Clailton no Spotclai (coração no site), com o arquivo local de cada uma.

uso: python favoritas.py            -> lista as favoritas (instrumentais primeiro) e onde está o MP3
     python favoritas.py --json     -> o mesmo em JSON (para outros scripts)

Lê o campo `fav` de https://spotclai.vercel.app/api/songs na hora (a lista muda quando ele marca ou desmarca).
Faixas com voz cantada ficam marcadas: só entram se existir a versão instrumental na Spotclai
(regra do usuário de 16/11/2026: trilha sem voz cantada).
"""
import json, os, sys, urllib.request

PASTA = os.path.join(os.path.expanduser("~"), "Music", "Spotclai")
# conferido em 23/11/2026 (transcrição): estas favoritas têm letra cantada
COM_LETRA = {"Je te laisserai des mots", "Beanie", "The Night We Met"}

req = urllib.request.Request("https://spotclai.vercel.app/api/songs", headers={"User-Agent": "spotclai-sync"})
with urllib.request.urlopen(req, timeout=30) as r:
    songs = json.load(r)
fav = [s for s in songs if s.get("fav")]
out = []
for s in fav:
    arq = os.path.join(PASTA, s["file"]) if s.get("file") else ""
    letra = any(n.lower() in s["title"].lower() for n in COM_LETRA)
    out.append({"titulo": s["title"], "artista": s.get("artist", ""), "emocao": s.get("mood", ""),
                "arquivo": arq if arq and os.path.exists(arq) else "", "com_letra": letra})
out.sort(key=lambda x: (x["com_letra"], x["emocao"], x["titulo"]))
if "--json" in sys.argv:
    print(json.dumps(out, ensure_ascii=False, indent=1))
else:
    for x in out:
        marca = "LETRA (só versão instrumental)" if x["com_letra"] else "instrumental"
        print(f"{x['emocao']:11s} | {marca:31s} | {x['titulo']} - {x['artista']}")
        print(f"            {x['arquivo'] or 'SEM MP3 NESTE PC (rode o Spotclai Sync)'}")
