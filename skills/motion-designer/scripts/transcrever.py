"""Transcreve um áudio/vídeo com faster-whisper (placa de vídeo se houver; senão processador).

Uso: python transcrever.py <arquivo> [idioma=pt] [saida.txt]
Serve para: conferir a pronúncia da narração, provar que a voz está clara na mixagem final e
transcrever tutoriais/referências quando a legenda do YouTube falhar.
"""
import os, site, subprocess, sys, tempfile

for sp in site.getsitepackages() + [site.getusersitepackages()]:
    for sub in ("nvidia/cublas/bin", "nvidia/cudnn/bin"):
        d = os.path.join(sp, sub)
        if os.path.isdir(d):
            os.add_dll_directory(d)
            os.environ["PATH"] = d + os.pathsep + os.environ["PATH"]

import soundfile as sf
from faster_whisper import WhisperModel

arq = sys.argv[1]
idioma = sys.argv[2] if len(sys.argv) > 2 else "pt"
saida = sys.argv[3] if len(sys.argv) > 3 else None

# decodifica com ffmpeg para WAV 16 kHz mono (o leitor interno do faster-whisper falha em algumas versões)
wav = os.path.join(tempfile.gettempdir(), "transcrever_tmp.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", arq, "-ac", "1", "-ar", "16000", wav], check=True)
audio, _ = sf.read(wav, dtype="float32")

try:
    m = WhisperModel("large-v3", device="cuda", compute_type="float16")
except Exception:  # noqa: BLE001
    m = WhisperModel("small", device="cpu", compute_type="int8")
segs, _ = m.transcribe(audio, language=idioma, vad_filter=True)
linhas = [f"[{int(s.start//60):02d}:{int(s.start%60):02d}] {s.text.strip()}" for s in segs]
texto = "\n".join(linhas)
if saida:
    open(saida, "w", encoding="utf-8").write(texto)
print(texto)
