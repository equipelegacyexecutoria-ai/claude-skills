"""Alinhamento forçado (WhisperX + wav2vec2 português) das palavras do corte: tempo de cada
palavra com erro de ~1 quadro (o Whisper erra 2+ e 'estica' palavra por cima da pausa).

Roda na venv própria (torch CUDA): %LOCALAPPDATA%\\reels-novela\\venv-align\\Scripts\\python.exe
Mantém texto e índices do palavras_corte.json; só troca inicio/fim (e marca "alinhado").
Palavra que o alinhador não consegue (número, símbolo) fica com o tempo do Whisper.

Uso: python alinhar.py <trabalho>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

SR = 16000


def main() -> None:
    trabalho = Path(sys.argv[1])
    arq = trabalho / "palavras_corte.json"
    dados = json.loads(arq.read_text(encoding="utf-8"))
    pal = dados["palavras"]
    import torch
    import whisperx
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    audio = whisperx.load_audio(str(trabalho / "audio_corte16k.wav"))

    # segmentos = frases entre pausas (o alinhador trabalha dentro de cada janela)
    segs, cur = [], []
    for w in pal:
        if cur and (w["inicio"] - cur[-1]["fim"] >= 0.25 or len(cur) >= 25):
            segs.append(cur)
            cur = []
        cur.append(w)
    if cur:
        segs.append(cur)
    entrada = [{"start": max(0.0, s[0]["inicio"] - 0.15), "end": s[-1]["fim"] + 0.15,
                "text": " ".join(w["texto"] for w in s)} for s in segs]

    modelo, meta = whisperx.load_align_model(language_code="pt", device=dev)
    res = whisperx.align(entrada, modelo, meta, audio, dev, return_char_alignments=False)

    # o whisperx pode partir os segmentos em frases: casa pela SEQUÊNCIA de palavras
    import difflib
    import re
    import unicodedata

    def nrm(t: str) -> str:
        t = unicodedata.normalize("NFD", t.lower())
        return re.sub(r"[^a-z0-9%]", "", "".join(c for c in t if unicodedata.category(c) != "Mn"))

    alinhadas = res.get("word_segments") or [w for s in res["segments"] for w in s.get("words", [])]
    a = [nrm(w["texto"]) for w in pal]
    b = [nrm(w.get("word", "")) for w in alinhadas]
    ok = 0
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
        if op != "equal":
            continue
        for di in range(i2 - i1):
            w, x = pal[i1 + di], alinhadas[j1 + di]
            if "start" in x and "end" in x:
                w["inicio_whisper"] = w["inicio"]
                w["inicio"], w["fim"] = round(float(x["start"]), 3), round(float(x["end"]), 3)
                ok += 1
    for j, w in enumerate(pal):
        w["pausa_antes"] = round(w["inicio"] - pal[j - 1]["fim"], 3) if j else 9.0
    dados["alinhado"] = True
    dados["alinhadas"] = ok
    arq.write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"ok: {ok}/{len(pal)} palavras alinhadas ({dev})")


if __name__ == "__main__":
    main()
