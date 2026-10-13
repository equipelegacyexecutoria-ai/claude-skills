"""Funções comuns da skill cortes-youtube-legado."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
_WHISPER = None


def hms(s: float, ms: bool = False) -> str:
    s = max(0.0, float(s))
    h, r = divmod(s, 3600)
    m, sec = divmod(r, 60)
    if ms:
        return f"{int(h):02d}:{int(m):02d}:{sec:06.3f}"
    return f"{int(h):02d}:{int(m):02d}:{int(sec):02d}"


def seg(x) -> float:
    """'1:02:03.5' / '62:03' / 3723.5 -> segundos."""
    if isinstance(x, (int, float)):
        return float(x)
    p = [float(v) for v in str(x).strip().split(":")]
    t = 0.0
    for v in p:
        t = t * 60 + v
    return t


def slug(txt: str, n: int = 60) -> str:
    t = unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode()
    t = re.sub(r"[^A-Za-z0-9]+", "-", t).strip("-").lower()
    return t[:n].strip("-")


def ler_json(p: Path):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def gravar_json(p: Path, obj) -> None:
    Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def rodar(cmd: list, cwd=None) -> subprocess.CompletedProcess:
    cmd = [str(c) for c in cmd]
    if cmd and Path(cmd[0]).stem in ("ffmpeg", "ffprobe") and "-v" not in cmd:
        cmd = [cmd[0], "-v", "error"] + cmd[1:]
    return subprocess.run(cmd, check=True, cwd=cwd)


def sonda(path: Path) -> dict:
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration:stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
                        "-of", "json", str(path)], capture_output=True, text=True, check=True)
    return json.loads(p.stdout)


def whisper():
    """faster-whisper large-v3-turbo na GPU (float16), com volta automática para CPU int8.
    As DLLs do CUDA vêm dos pacotes nvidia-* da venv: registra as pastas bin antes de carregar."""
    global _WHISPER
    if _WHISPER is not None:
        return _WHISPER
    base = Path(sys.prefix) / "Lib" / "site-packages" / "nvidia"
    if base.exists():
        for sub in ("cublas", "cudnn", "cuda_nvrtc"):
            d = base / sub / "bin"
            if d.exists():
                os.add_dll_directory(str(d))
                os.environ["PATH"] = str(d) + os.pathsep + os.environ.get("PATH", "")
    import numpy as np
    from faster_whisper import WhisperModel
    try:
        m = WhisperModel("large-v3-turbo", device="cuda", compute_type="float16")
        list(m.transcribe(np.zeros(16000, dtype="float32"), language="pt")[0])
        m.dispositivo = "GPU float16"
    except Exception as e:  # noqa: BLE001
        print(f"[whisper] GPU indisponível ({e}); usando CPU int8", flush=True)
        m = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
        m.dispositivo = "CPU int8 (~10x mais lento)"
    _WHISPER = m
    return m
