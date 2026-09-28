"""Queima a legenda no estilo da referência sobre o vertical limpo e copia os
finais para a pasta do projeto.

  clip-clean.mp4  (render da skill, sem legenda)  ->  clip-legendado.mp4
  + cópia em <projeto>/Cortes Finais - Executoria Cast Metal Glass/NN - Título.mp4
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import legenda_ref as L  # noqa: E402

RUN = Path(__file__).resolve().parent.parent
PROJ = RUN.parent.parent
DEST = PROJ / "Cortes Finais - Executoria Cast Metal Glass"
DEST.mkdir(exist_ok=True)

# nomes aprovados pelo usuário (2026-09-26)
NOMES = {
    "01": "Cliente com 20 milhões em obra vendida e sem caixa",
    "02": "Dívida não é o problema, depende de pra quê",
    "03": "Conhecimento sem gestão vira prisão",
    "04": "Fornecedor oferece o mais barato - nem manda pra mim",
    "05": "Markup não é margem",
    "06": "Eu sou outra pessoa",
    "07": "Tem produtos que eu recuso venda",
    "08": "Ninguém de fato é gestor",
    "09": "Eu quebrei pela primeira vez aos 20 anos",
    "10": "Crescemos 239% só no componente",
}

tr = json.loads((RUN / "02-transcript.json").read_text(encoding="utf-8"))
words = L.load_words(tr)
plans = json.loads((RUN / "11-edit-plans.json").read_text(encoding="utf-8"))["plans"]
only = set(sys.argv[1:])

for plan in plans:
    slug = plan["output_slug"]
    if only and not any(slug.startswith(o) for o in only):
        continue
    out = RUN / "output" / "final-clips" / plan["primary_context"] / slug
    ws = L.map_words(words, plan["timeline"])
    ws = L.corrigir(ws, slug)
    clip_end = sum(p["source_end"] - p["source_start"] for p in plan["timeline"])
    ass = out / "legenda-referencia.ass"
    ass.write_text(L.HEADER + "\n".join(L.build(ws, clip_end, slug)) + "\n", encoding="utf-8")
    (out / "legenda-palavras.json").write_text(json.dumps(ws, ensure_ascii=False, indent=1), encoding="utf-8")
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-i", "clip-clean.mp4",
        "-vf", "ass=legenda-referencia.ass:fontsdir=../../../../assets/fonts",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "copy", "-movflags", "+faststart", "clip-legendado.mp4",
    ], cwd=out, check=True)
    final = DEST / f"{slug[:2]} - {NOMES[slug[:2]]}.mp4"
    shutil.copy2(out / "clip-legendado.mp4", final)
    print(f"{slug}: {len(ws)} palavras -> {final}", flush=True)
