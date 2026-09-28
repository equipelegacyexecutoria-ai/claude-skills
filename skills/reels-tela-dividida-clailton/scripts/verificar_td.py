"""Confere o ambiente da skill tela dividida antes do 1º vídeo de um lote.

Uso: python verificar_td.py [--instalar]   (--instalar: pip install yt-dlp ddgs httpx na venv principal)
"""
from __future__ import annotations

import importlib
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from td_comum import NOVELA, SKILL, python_align, python_principal  # noqa: E402

ok = True


def item(nome: str, cond: bool, dica: str = "") -> None:
    global ok
    print(f"  [{'ok' if cond else 'FALTA'}] {nome}" + ("" if cond else f"  -> {dica}"))
    ok &= cond


def main() -> None:
    if "--instalar" in sys.argv:
        subprocess.run([python_principal(), "-m", "pip", "install", "-q", "yt-dlp", "ddgs", "httpx", "curl_cffi"], check=False)
        subprocess.run([python_align(), "-m", "pip", "install", "-q", "--no-deps", "timm"], check=False)
    print("Skill tela dividida:")
    item("skill reels-novela-clailton", (NOVELA / "scripts" / "montar_corte.py").exists(), "instale a skill da novela")
    item("fontes (SF Pro Text Black, Inter)", (NOVELA / "fonts" / "SF-Pro-Text-Black.otf").exists(), "pacote da novela")
    item("ffmpeg no PATH", shutil.which("ffmpeg") is not None, "winget install Gyan.FFmpeg")
    item("node (JS do YouTube)", shutil.which("node") is not None, "winget install OpenJS.NodeJS.LTS")
    for mod in ("cv2", "PIL", "numpy", "uharfbuzz", "fontTools", "httpx", "ddgs", "yt_dlp", "curl_cffi", "faster_whisper"):
        try:
            importlib.import_module(mod)
            item(f"módulo {mod}", True)
        except Exception:  # noqa: BLE001
            item(f"módulo {mod}", False, "python verificar_td.py --instalar")
    r = subprocess.run([python_align(), "-c", "import torch, transformers; print(torch.cuda.is_available())"],
                       capture_output=True, text=True)
    item("venv do alinhador (torch + transformers)", r.returncode == 0, "instale o pacote da novela (venv-align)")
    item("GPU no torch (CLIP)", "True" in r.stdout, "sem GPU o CLIP roda na CPU (mais lento)")
    r = subprocess.run([python_align(), "-c", "import timm"], capture_output=True, text=True)
    item("timm na venv do alinhador (detector de marca d'água)", r.returncode == 0,
         f'"{python_align()}" -m pip install --no-deps timm')
    item("pesos do detector de marca d'água", (SKILL / "models" / "watermark_model_v1.pt").exists(),
         "baixa sozinho na 1ª busca (GitHub LAION-5B-WatermarkDetection)")
    cache = Path.home() / ".cache" / "huggingface" / "hub" / "models--openai--clip-vit-large-patch14"
    item("modelo CLIP ViT-L/14 no cache", cache.exists(),
         f'"{python_align()}" -c "from transformers import CLIPModel; CLIPModel.from_pretrained(\'openai/clip-vit-large-patch14\')"')
    r = subprocess.run([python_principal(), "-m", "yt_dlp", "--version"], capture_output=True, text=True)
    item(f"yt-dlp {r.stdout.strip()}", r.returncode == 0, "python verificar_td.py --instalar")
    item("agente td-planejador instalado", (Path.home() / ".claude" / "agents" / "td-planejador.md").exists(),
         f"copie {SKILL / 'agentes' / 'td-planejador.md'} para ~/.claude/agents/")
    print("TUDO OK" if ok else "FALTA ALGO (ver acima)")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
