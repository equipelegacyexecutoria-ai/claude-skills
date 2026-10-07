"""Ouve o começo e o fim de cada bruto de uma pasta, para descobrir qual roteiro é de qual vídeo
e anotar para o editor onde há conversa de set, regravações e o CTA gravado.

Usa o Whisper da skill reels-novela-clailton (comum.whisper: GPU com volta para CPU).

Uso: <python da venv> ouvir_brutos.py <pasta_dos_brutos> [segundos_inicio=75] [segundos_fim=50]
Saída: para cada vídeo, duração e as frases do começo e do fim com o tempo (m:ss) no bruto.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".claude/skills/reels-novela-clailton/scripts"))
from comum import whisper  # noqa: E402

VIDEO = {".mp4", ".mov", ".mxf", ".m4v", ".mkv"}


def duracao(v: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(v)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def mmss(t: float) -> str:
    return f"{int(t // 60)}:{int(t % 60):02d}"


def trecho(model, v: Path, ini: float, dur: float, tmp: Path) -> list[str]:
    wav = tmp / f"{v.stem}_{int(ini)}.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{ini:.2f}", "-t", f"{dur:.2f}", "-i", str(v),
                    "-map", "0:a:0", "-ac", "1", "-ar", "16000", str(wav)], check=True)
    # condition_on_previous_text=False: evita o Whisper "travar" repetindo a mesma frase em tomadas refeitas
    segs, _ = model.transcribe(str(wav), language="pt", beam_size=1, vad_filter=True,
                               condition_on_previous_text=False)
    return [f"  {mmss(ini + s.start)} {s.text.strip()}" for s in segs]


def main() -> None:
    pasta = Path(sys.argv[1])
    s_ini = float(sys.argv[2]) if len(sys.argv) > 2 else 75
    s_fim = float(sys.argv[3]) if len(sys.argv) > 3 else 50
    videos = sorted(p for p in pasta.iterdir() if p.suffix.lower() in VIDEO)
    if not videos:
        sys.exit(f"Nenhum vídeo em {pasta}")
    model = whisper()
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for v in videos:
            d = duracao(v)
            print(f"=== {v.name} ({mmss(d)}, {v.stat().st_size / 1e9:.2f} GB)")
            print("  -- começo --")
            print("\n".join(trecho(model, v, 0, min(s_ini, d), tmp)))
            if d > s_ini:
                ini = max(s_ini, d - s_fim)
                print("  -- fim --")
                print("\n".join(trecho(model, v, ini, d - ini, tmp)))
            print(flush=True)


if __name__ == "__main__":
    main()
