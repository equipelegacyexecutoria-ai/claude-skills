"""Confere se a máquina está pronta para a skill (rodar antes do 1º vídeo de um lote).

- Python e módulos (faster-whisper, opencv, numpy, pillow, fonttools, uharfbuzz)
- Whisper na GPU (sem GPU funciona, ~10x mais lento)
- venv do alinhador (WhisperX + torch CUDA + modelo wav2vec2 português); sem ela o corte usa
  os tempos do Whisper refinados pela energia (pior: legenda até 0,2 s adiantada)
- ffmpeg com libass (filtro "ass" por palavra inteira: "lowpass"/"bass" enganam busca por trecho),
  libx264, silencedetect, ebur128, alimiter; NVDEC (cuda) é opcional
- fontes e modelo de rosto da skill
- agentes da novela presentes em ~/.claude/agents (a única cópia, que sincroniza)

Uso: python verificar.py   (sai com 1 se faltar algo obrigatório)
"""
from __future__ import annotations

import importlib
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import FONTS, MODELO_ROSTO, SKILL  # noqa: E402

AGENTES_USUARIO = Path.home() / ".claude" / "agents"
ok = True


def linha(status: str, txt: str) -> None:
    print(f"[{status}] {txt}")


def falha(txt: str) -> None:
    global ok
    ok = False
    linha("FALTA", txt)


print(f"Python {sys.version.split()[0]} em {sys.executable}")
for mod in ("faster_whisper", "cv2", "numpy", "PIL", "fontTools", "uharfbuzz"):
    try:
        m = importlib.import_module(mod)
        linha("ok", f"{mod} {getattr(m, '__version__', '')}")
    except Exception as e:  # noqa: BLE001
        falha(f"módulo {mod}: {e} (pip install -r {SKILL / 'requirements.txt'})")

try:
    from comum import whisper
    linha("ok", f"Whisper large-v3-turbo: {whisper().dispositivo}")
except Exception as e:  # noqa: BLE001
    falha(f"Whisper não carrega: {e}")

PY_ALINHA = Path(os.environ.get("LOCALAPPDATA", "")) / "reels-novela" / "venv-align" / "Scripts" / "python.exe"
if PY_ALINHA.exists():
    r = subprocess.run([str(PY_ALINHA), "-c", "import torch, whisperx; print(torch.__version__, torch.cuda.is_available())"],
                       capture_output=True, text=True)
    if r.returncode:
        linha("aviso", f"venv do alinhador quebrada: {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else r.returncode}")
    else:
        tv, cuda = r.stdout.split()
        linha("ok" if cuda == "True" else "aviso", f"alinhador WhisperX (torch {tv}, {'GPU' if cuda == 'True' else 'CPU: ~1 min a mais'})")
    hf = Path.home() / ".cache" / "huggingface" / "hub" / "models--jonatasgrosman--wav2vec2-large-xlsr-53-portuguese"
    linha("ok" if hf.exists() else "aviso", "modelo wav2vec2 português" + ("" if hf.exists() else " não baixado (baixa 1,2 GB no 1º uso)"))
else:
    linha("aviso", f"sem alinhador ({PY_ALINHA}): legenda sai com o tempo do Whisper (ver SKILL.md, Ambiente)")

try:
    v = subprocess.run(["ffmpeg", "-hide_banner", "-version"], capture_output=True, text=True).stdout.split("\n")[0]
    linha("ok", v)
    filtros = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout
    for f in ("ass", "silencedetect", "ebur128", "alimiter", "loudnorm", "setparams"):
        if re.search(rf"^\s*\S+\s+{f}\s", filtros, re.M):
            linha("ok", f"filtro {f}")
        else:
            falha(f"ffmpeg sem o filtro {f}")
    enc = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True).stdout
    (linha("ok", "encoder libx264") if re.search(r"\slibx264\s", enc) else falha("ffmpeg sem libx264"))
    hw = subprocess.run(["ffmpeg", "-hide_banner", "-hwaccels"], capture_output=True, text=True).stdout
    linha("ok" if "cuda" in hw else "aviso", "decodificação NVDEC (cuda)" + ("" if "cuda" in hw else " indisponível: usa CPU"))
except FileNotFoundError:
    falha("ffmpeg não está no PATH")

for f in ("SF-Pro-Text-Black.otf", "Inter_28pt-ExtraBold.ttf"):
    (linha("ok", f"fonte {f}") if (FONTS / f).exists() else falha(f"fonte {FONTS / f}"))
(linha("ok", "modelo YuNet") if MODELO_ROSTO.exists() else falha(f"modelo {MODELO_ROSTO}"))

for nome in ("novela-decupador", "novela-legendista", "novela-legendista-rapido",
             "novela-revisao-decupagem", "novela-revisor"):
    if (AGENTES_USUARIO / f"{nome}.md").exists():
        linha("ok", f"agente {nome}")
    else:
        falha(f"agente {nome} ausente em {AGENTES_USUARIO}: rode a sincronia (sync.ps1 -Modo agora)")

print("PRONTO" if ok else "FALTA ALGO — corrija antes de editar")
sys.exit(0 if ok else 1)
