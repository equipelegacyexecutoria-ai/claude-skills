"""Confere o que este PC tem para fazer motion e mostra como instalar o que faltar.

Uso: python ~/.claude/skills/motion-designer/scripts/verificar_ambiente.py
Não instala nada sozinho: só lista. Instalar = pedir o "sim" do usuário antes.
"""
import importlib.util, os, shutil, subprocess, sys, glob

ok, falta = [], []


def cmd(nome, args):
    exe = shutil.which(args[0])
    if not exe:
        return None
    try:
        r = subprocess.run([exe] + args[1:], capture_output=True, text=True, timeout=60)
        return (r.stdout or r.stderr).strip().splitlines()[0] if (r.stdout or r.stderr) else "ok"
    except Exception as e:  # noqa: BLE001
        return f"erro: {e}"


def checa(nome, valor, instalar, obrigatorio=True):
    (ok if valor else falta).append((nome, valor, instalar, obrigatorio))


checa("Node.js 20+", cmd("node", ["node", "-v"]), "winget install OpenJS.NodeJS.LTS")
checa("ffmpeg", cmd("ffmpeg", ["ffmpeg", "-version"]), "winget install Gyan.FFmpeg")
checa("yt-dlp", cmd("yt-dlp", ["yt-dlp", "--version"]), "winget install yt-dlp.yt-dlp")
checa("Python " + sys.version.split()[0], sys.version_info >= (3, 10), "winget install Python.Python.3.12")

for mod, pip, obrig in [("librosa", "librosa", True), ("soundfile", "soundfile", True),
                        ("faster_whisper", "faster-whisper nvidia-cublas-cu12 nvidia-cudnn-cu12==9.*", True),
                        ("pypdf", "pypdf", False), ("PIL", "pillow", True), ("manim", "manim", False)]:
    checa(f"python: {mod}", importlib.util.find_spec(mod) is not None, f"pip install {pip}", obrig)

home = os.path.expanduser("~")
skills = os.path.join(home, ".claude", "skills")
for s in ["hyperframes", "hyperframes-core", "hyperframes-animation", "product-launch-video", "media-use", "watch"]:
    checa(f"skill {s}", os.path.isdir(os.path.join(skills, s)),
          "chega pela sincronia (abrir conversa nova); se faltar: npx hyperframes skills update product-launch-video")

dif = glob.glob(os.path.join(os.environ.get("LOCALAPPDATA", ""), "DiffusionStudio", "app-*", "resources", "cli", "bin", "dapi.cmd"))
checa("Diffusion Studio (opcional)", dif[-1] if dif else None,
      "baixar Diffusion-Studio-x64-Setup.exe da release mais nova em github.com/diffusionstudio/editor (pedir o sim)", False)

print("== Instalado ==")
for n, v, _, _ in ok:
    print(f"  OK  {n}: {v if isinstance(v, str) else ''}")
print("\n== Falta ==" if falta else "\nNada faltando.")
for n, _, inst, obrig in falta:
    print(f"  {'FALTA' if obrig else 'opcional'}  {n}  ->  {inst}")
print("\nHyperFrames não precisa instalar: 'npx hyperframes@latest' baixa na hora.")
