"""Prepara um vídeo editado para a Sala de Revisão (Artifact).

Gera a prévia leve (540p, até ~13,5 MB — limite seguro por arquivo do Artifact) e deixa
tudo pronto numa pasta de envio dentro da pasta de trabalho atual:

  <pasta>/index.html                 (cópia da página da skill, sempre a versão mais nova)
  <pasta>/media/<id>_<versao>.mp4    (prévia)
  <pasta>/<id>_<versao>.json         (dados da versão para gravar no banco da página)

Uso:
  python preparar_revisao.py "C:\\Render\\Reels Editados\\<PAUTA> - EDITADO.mp4" --pauta "<PAUTA>" \\
      [--versao v2] [--obs "o que mudou"] [--drive "<link do arquivo final>"] [--pasta C:\\Render\\_sala_revisao]
  python preparar_revisao.py --so-pagina [--pasta ...]     (só atualiza a cópia da página)
"""
import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
SALA_URL = "https://claude.ai/artifact/HAcqomJqf9NXRNtyYbkX6v"
LIMITE_MB = 13.5
AUDIO_KBPS = 96


def slug(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")[:120]


def formato_da_pauta(pauta):
    p = "_" + pauta.upper() + "_"
    for marca, nome in (("_TD_", "TD"), ("_NV_", "NV"), ("_NOVELA_", "NV"), ("_ES_", "ES"), ("_CX_", "CX")):
        if marca in p:
            return nome
    return ""


def ffprobe(video):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,r_frame_rate:format=duration", "-of", "json", str(video)],
        capture_output=True, text=True, check=True).stdout
    info = json.loads(out)
    st = info["streams"][0]
    num, den = st["r_frame_rate"].split("/")
    return float(info["format"]["duration"]), int(st["width"]), int(st["height"]), round(float(num) / float(den), 3)


def gerar_previa(video, destino, dur, largura, altura):
    total_kbit = LIMITE_MB * 8 * 1024 * 1024 / 1000 * 0.97
    v_kbps = int(min(2000, total_kbit / dur - AUDIO_KBPS))
    if v_kbps < 150:
        sys.exit(f"Vídeo longo demais para caber em {LIMITE_MB} MB ({dur:.0f}s). Divida em partes.")
    lado = 540 if v_kbps >= 350 else 432
    escala = f"scale={lado}:-2" if altura > largura else f"scale=-2:{lado}"
    nulo = "NUL" if os.name == "nt" else "/dev/null"
    with tempfile.TemporaryDirectory() as tmp:
        log = str(Path(tmp) / "pass")
        base = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-vf", escala,
                "-c:v", "libx264", "-preset", "medium", "-b:v", f"{v_kbps}k",
                "-pix_fmt", "yuv420p", "-passlogfile", log]
        subprocess.run(base + ["-pass", "1", "-an", "-f", "mp4", nulo], check=True)
        subprocess.run(base + ["-pass", "2", "-c:a", "aac", "-b:a", f"{AUDIO_KBPS}k",
                               "-movflags", "+faststart", str(destino)], check=True)
    mb = Path(destino).stat().st_size / 1024 / 1024
    if mb > 14.5:
        sys.exit(f"Prévia ficou com {mb:.1f} MB (limite 15 MB). Rode de novo.")
    return v_kbps, mb


def copiar_pagina(pasta):
    pasta.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SKILL / "pagina" / "index.html", pasta / "index.html")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video", nargs="?")
    ap.add_argument("--pauta", help="PAUTA do card do Notion (vira o id e o título)")
    ap.add_argument("--versao", default="v1")
    ap.add_argument("--obs", default="")
    ap.add_argument("--drive", default="", help="link do arquivo final no Drive (opcional; pode entrar depois)")
    ap.add_argument("--notion", default="", help="link do card no Notion")
    ap.add_argument("--pasta", default=str(Path.cwd() / "_sala_revisao"))
    ap.add_argument("--so-pagina", action="store_true")
    a = ap.parse_args()
    pasta = Path(a.pasta).resolve()

    copiar_pagina(pasta)
    if a.so_pagina:
        print(json.dumps({"file_path": str(pasta / "index.html"), "root": str(pasta)}, ensure_ascii=False))
        return
    if not a.video or not a.pauta:
        sys.exit("Informe o vídeo e --pauta.")

    vid = slug(a.pauta)
    versao = a.versao.lower()
    if not re.fullmatch(r"v\d+", versao):
        sys.exit("--versao deve ser v1, v2, v3...")
    dur, w, h, fps = ffprobe(a.video)
    (pasta / "media").mkdir(exist_ok=True)
    rel = f"media/{vid}_{versao}.mp4"
    kbps, mb = gerar_previa(a.video, pasta / rel, dur, w, h)

    entrada = {"v": versao, "arquivo": rel, "data": dt.date.today().isoformat(),
               "duracao": round(dur, 2), "fps": fps, "obs": a.obs}
    if a.drive:
        entrada["drive"] = a.drive
    dados = {
        "id": vid,
        "titulo": a.pauta.replace("_", " ").strip(),
        "pauta": a.pauta,
        "formato": formato_da_pauta(a.pauta),
        "notion": a.notion,
        "versao": entrada,
        "link_revisao": f"{SALA_URL}#{vid}",
        "publicar": {"url": SALA_URL, "file_path": str(pasta / "index.html"), "root": str(pasta), "files": {rel: rel}},
    }
    (pasta / f"{vid}_{versao}.json").write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Prévia {rel}: {mb:.1f} MB · {kbps} kbps · {dur:.1f}s · {fps} fps")
    print(json.dumps(dados, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
