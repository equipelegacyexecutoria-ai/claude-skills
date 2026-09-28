"""Confere a transcrição (VTT do usuário) contra o Whisper, no áudio de cada clipe
renderizado, antes de queimar a legenda. Lista só as divergências de palavra."""
from __future__ import annotations

import difflib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from faster_whisper import WhisperModel

sys.path.insert(0, str(Path(__file__).parent))
from legenda_ref import load_words, map_words  # noqa: E402

RUN = Path(__file__).resolve().parent.parent
tr = json.loads((RUN / "02-transcript.json").read_text(encoding="utf-8"))
words = load_words(tr)
plans = json.loads((RUN / "11-edit-plans.json").read_text(encoding="utf-8"))["plans"]


def carregar_whisper() -> WhisperModel:
    """GPU (float16) com as DLLs do CUDA 12 dos pacotes nvidia-cublas-cu12/nvidia-cudnn-cu12 da
    venv (o Windows não acha sozinho: registra as pastas bin); sem GPU, CPU int8 (~10x mais lento)."""
    import os
    import numpy as np
    base = Path(sys.prefix) / "Lib" / "site-packages" / "nvidia"
    for sub in ("cublas", "cudnn", "cuda_nvrtc"):
        d = base / sub / "bin"
        if d.exists():
            os.add_dll_directory(str(d))
            os.environ["PATH"] = str(d) + os.pathsep + os.environ.get("PATH", "")
    try:
        m = WhisperModel("large-v3-turbo", device="cuda", compute_type="float16")
        list(m.transcribe(np.zeros(16000, dtype="float32"), language="pt")[0])     # testa de verdade
        return m
    except Exception as e:  # noqa: BLE001
        print(f"[whisper] GPU indisponível ({e}); usando CPU int8", flush=True)
        return WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")


model = carregar_whisper()


def norm(t: str) -> str:
    return re.sub(r"[^\wÀ-ÿ%]", "", t.lower())


report = {}
for plan in plans:
    clip = RUN / "output" / "final-clips" / plan["primary_context"] / plan["output_slug"] / "clip-clean.mp4"
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "a.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(clip), "-ac", "1", "-ar", "16000", str(wav)], check=True)
        segs, _ = model.transcribe(str(wav), language="pt", word_timestamps=True, vad_filter=True, beam_size=5)
        wh = [{"text": w.word.strip(), "start": w.start} for s in segs for w in s.words]
    vt = map_words(words, plan["timeline"])
    a = [norm(w["text"]) for w in vt]
    b = [norm(w["text"]) for w in wh]
    diffs = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
        if op == "equal":
            continue
        t = vt[i1]["start"] if i1 < len(vt) else (vt[-1]["end"] if vt else 0)
        diffs.append({"t": round(t, 2), "op": op,
                      "vtt": " ".join(w["text"] for w in vt[i1:i2]),
                      "whisper": " ".join(w["text"] for w in wh[j1:j2]),
                      "contexto": " ".join(w["text"] for w in vt[max(0, i1 - 4):min(len(vt), i2 + 4)])})
    report[plan["output_slug"]] = diffs
    print(f"== {plan['output_slug']}: {len(diffs)} divergências", flush=True)
    for d in diffs:
        print(f"   {d['t']:6.2f}s {d['op']:7s} VTT[{d['vtt']}] x WHISPER[{d['whisper']}]  | {d['contexto']}", flush=True)
(RUN / "assets" / "conferencia-palavras.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
