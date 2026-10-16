"""Uso: python voz_do_heygen.py <W> <nome> [<nome>...]
Tira a voz do vídeo do HeyGen (heygen/<nome>.mp4) para vozes/<nome>.wav e grava as palavras em vozes/frases.json."""
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from comum import palavras, ler_json, gravar_json  # noqa: E402

R = Path(sys.argv[1])
fr = ler_json(R / "vozes/frases.json", {})
for nome in sys.argv[2:]:
    v, w = R / "heygen" / f"{nome}.mp4", R / "vozes" / f"{nome}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(v), "-vn", "-ac", "1", "-ar", "48000", str(w)], check=True)
    pal = palavras(w)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(w)],
                               capture_output=True, text=True).stdout)
    fr[nome] = {"dur": round(dur, 2), "palavras": pal}
    print(nome, round(dur, 2), "s", len(pal), "palavras:", " ".join(p["p"] for p in pal))
gravar_json(R / "vozes/frases.json", fr)
