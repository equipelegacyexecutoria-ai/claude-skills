"""Constantes e utilitários comuns do pipeline Reels Novela."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
FONTS = SKILL / "fonts"
MODELO_ROSTO = SKILL / "models" / "face_detection_yunet_2023mar.onnx"

FPS_NUM, FPS_DEN = 30000, 1001
FPS = FPS_NUM / FPS_DEN
W, H = 1080, 1920
FAIXA_W, FAIXA_H = 1080, 864          # 5:4, igual à referência
FAIXA_Y0 = (H - FAIXA_H) // 2         # 528

# enquadramento-alvo (medido na referência): rosto com 23% da largura da faixa,
# centro do rosto a 54% da largura e 32% da altura da faixa
ROSTO_LARG = 0.23
ROSTO_CX = 0.54
ROSTO_CY = 0.32

# ritmo do corte (medido na referência: 0,10-0,26 s entre frases)
PAUSA_ENTRE = 0.18      # silêncio que fica entre trechos colados
PAUSA_MAX = 0.30        # pausa interna maior que isso é encurtada... (usuário reprovou 0,45 s)
PAUSA_ALVO = 0.16       # ...para isso
FIM_RESPIRO = 0.45      # imagem depois da última palavra, antes do corte seco para a CTA

# entrega
CRF = 10                # "sem comprimir": visualmente sem perda
PRESET = "slow"
AUDIO_BR = "320k"
LUFS = -14.0
TRUE_PEAK = -1.0


_WHISPER = None


def whisper():
    """faster-whisper large-v3-turbo na GPU (RTX 4070: float16) com volta automática para CPU int8.
    As DLLs do CUDA vêm dos pacotes nvidia-cublas-cu12 / nvidia-cudnn-cu12 da venv (o Windows não
    acha sozinho: registra as pastas bin)."""
    global _WHISPER
    if _WHISPER is not None:
        return _WHISPER
    import os
    import sys as _sys
    base = Path(_sys.prefix) / "Lib" / "site-packages" / "nvidia"
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
        list(m.transcribe(np.zeros(16000, dtype="float32"), language="pt")[0])      # testa de verdade
        m.dispositivo = "GPU float16"
        _WHISPER = m
    except Exception as e:  # noqa: BLE001
        print(f"[whisper] GPU indisponível ({e}); usando CPU int8", flush=True)
        _WHISPER = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
        _WHISPER.dispositivo = "CPU int8 (~10x mais lento)"
    return _WHISPER


def rodar(cmd: list[str], cwd: Path | str | None = None, silencioso: bool = True) -> subprocess.CompletedProcess:
    if silencioso and cmd and Path(cmd[0]).stem in ("ffmpeg", "ffprobe") and "-v" not in cmd:
        cmd = [cmd[0], "-v", "error"] + cmd[1:]
    return subprocess.run(cmd, check=True, cwd=cwd, capture_output=False)


def sonda(path: Path) -> dict:
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration:stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels,pix_fmt",
                        "-of", "json", str(path)], capture_output=True, text=True, check=True)
    return json.loads(p.stdout)


def ler_json(p: Path):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def gravar_json(p: Path, obj) -> None:
    Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def preparar_fontes(trabalho: Path) -> Path:
    """Copia as fontes para <trabalho>/fonts (o filtro ass do ffmpeg usa caminho relativo)."""
    dest = Path(trabalho) / "fonts"
    dest.mkdir(parents=True, exist_ok=True)
    for f in FONTS.iterdir():
        if f.suffix.lower() in (".otf", ".ttf"):
            shutil.copy2(f, dest / f.name)
    return dest
