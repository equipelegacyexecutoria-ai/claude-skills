"""Caminhos e funções comuns da skill teste-de-gancho-td."""
import json, os, subprocess, sys
from pathlib import Path

import numpy as np

SKILLS = Path.home() / ".claude/skills"
MOD = str(SKILLS / "reels-novela-clailton/models/face_detection_yunet_2023mar.onnx")
FONTES = SKILLS / "reels-novela-clailton/fonts"
FPS = 30000 / 1001
W, H = 1080, 1920
FORMATOS = ("TD", "NV", "ES", "CX")


def rodar(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)
    if r.returncode:
        sys.exit(r.stderr[-3000:])
    return r


def lufs(arq, ss=None, t=None):
    cmd = ["ffmpeg", "-v", "info"] + (["-ss", f"{ss:.3f}"] if ss is not None else []) + \
          (["-t", f"{t:.3f}"] if t else []) + ["-i", str(arq), "-af", "ebur128", "-f", "null", "-"]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    return float([l for l in r.splitlines() if l.strip().startswith("I:")][-1].split()[1])


def quadro(vid, t, w=W, h=H):
    """Um quadro RGB (h, w, 3) do vídeo no tempo t."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(vid), "-frames:v", "1",
                          "-vf", f"scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(h, w, 3).astype(float)


def py_com(*mods):
    """Python de uma venv que tem os módulos pedidos (as venvs variam de PC para PC)."""
    base = Path(os.environ.get("LOCALAPPDATA", ""))
    for v in ("corte-viral/venv", "reels-novela/venv", "reels-novela/venv-align"):
        py = base / v / "Scripts/python.exe"
        if py.exists():
            r = subprocess.run([str(py), "-c", "import " + ",".join(mods)], capture_output=True)
            if r.returncode == 0:
                return str(py)
    sys.exit(f"nenhuma venv tem {mods}: instale pelo requirements.txt da skill")


def whisper(gpu=True):
    from faster_whisper import WhisperModel
    if gpu:
        try:
            return WhisperModel("large-v3-turbo", device="cuda", compute_type="float16")
        except Exception:
            pass
    return WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")


def palavras(arq, ss=0.0, t=None):
    """Transcrição palavra a palavra: [{i, f, p}] (tempos a partir de ss)."""
    import tempfile
    wav = Path(tempfile.mkdtemp()) / "a.wav"
    rodar(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss:.3f}"] + (["-t", f"{t:.3f}"] if t else []) +
          ["-i", str(arq), "-vn", "-ac", "1", "-ar", "16000", str(wav)])
    for gpu in (True, False):   # PC sem as bibliotecas CUDA: a GPU "carrega" e falha só ao transcrever
        try:
            segs, _ = whisper(gpu).transcribe(str(wav), language="pt", word_timestamps=True,
                                              condition_on_previous_text=False)
            return [dict(i=round(w.start, 2), f=round(w.end, 2), p=w.word.strip()) for s in segs for w in s.words]
        except RuntimeError:
            if not gpu:
                raise


def pauta_teste(pauta):
    """Reels_Clailton_TD_Termômetro_... -> Reels_Clailton_TD_TESTE_Termômetro_... (regra do usuário, 13/10/2026)."""
    partes = pauta.split("_")
    if "TESTE" in partes:
        return pauta
    for k, p in enumerate(partes):
        if p.upper() in FORMATOS:
            return "_".join(partes[:k + 1] + ["TESTE"] + partes[k + 1:])
    return pauta + "_TESTE"


def ler_json(arq, padrao=None):
    arq = Path(arq)
    return json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else padrao


def gravar_json(arq, dado):
    Path(arq).write_text(json.dumps(dado, ensure_ascii=False, indent=1), encoding="utf-8")
