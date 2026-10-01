"""Fotos do Pexels para o B-roll da caixinha (sem marca d'água, verticais, alta resolução).

Os ids vêm da busca no navegador do app (ver SKILL.md, "B-roll"): abra
https://www.pexels.com/pt-br/procurar/<busca>/?orientation=portrait e rode no console
  [...document.querySelectorAll('article img')].map(i=>(i.currentSrc||i.src).match(/photos\\/(\\d+)/)?.[1]+'|'+i.alt)

  python pexels.py folha  <trabalho> <candidatos.json>    {"b01": [id, id, ...], ...} -> qa/pexels.jpg
  python pexels.py baixar <trabalho> <escolha.json>       {"b01": ["@28-35", id], ...}
      -> <trabalho>/pexels/bNN_<id>.jpg (2600 px de altura) + linhas "arquivo" no plano.txt
"""
from __future__ import annotations

import io
import json
import sys
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw

UA = {"User-Agent": "Mozilla/5.0"}


def url(i: int, **q) -> str:
    qs = "&".join(f"{k}={v}" for k, v in {"auto": "compress", **q}.items())
    return f"https://images.pexels.com/photos/{i}/pexels-photo-{i}.jpeg?{qs}"


def baixar_bytes(u: str) -> bytes:
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read()


def folha(T: Path, cands: dict) -> Path:
    tw, th, n = 220, 390, max(len(v) for v in cands.values())
    sheet = Image.new("RGB", (tw * n, (th + 30) * len(cands)), (25, 25, 25))
    d = ImageDraw.Draw(sheet)
    for r, (b, ids) in enumerate(cands.items()):
        for c, i in enumerate(ids):
            try:
                im = Image.open(io.BytesIO(baixar_bytes(url(i, w=500)))).convert("RGB")
            except Exception as e:  # noqa: BLE001
                print(f"{b} {i}: {e}")
                continue
            im.thumbnail((tw, th))
            sheet.paste(im, (c * tw, r * (th + 30) + 28))
            d.text((c * tw + 4, r * (th + 30) + 6), f"{b} {c} {i}", fill=(255, 220, 0))
    out = T / "qa" / "pexels.jpg"
    out.parent.mkdir(exist_ok=True)
    sheet.save(out, quality=85)
    return out


def baixar(T: Path, esc: dict) -> None:
    pasta = T / "pexels"
    pasta.mkdir(exist_ok=True)
    linhas = []
    for b, (faixa, i) in esc.items():
        p = pasta / f"{b}_{i}.jpg"
        if not p.exists():
            p.write_bytes(baixar_bytes(url(i, cs="tinysrgb", h=2600)))
        w, h = Image.open(p).size
        aviso = "" if w >= 1080 and h >= 1920 else "  <- BAIXA RESOLUÇÃO"
        print(f"{b} {faixa} {i} {w}x{h}{aviso}")
        linhas.append(f'{faixa} arquivo "{p.resolve()}"')
    plano = T / "plano.txt"
    antigo = plano.read_text(encoding="utf-8").splitlines() if plano.exists() else []
    resto = [ln for ln in antigo if ln.strip() and not ln.lstrip().startswith("@")]
    if not any(ln.startswith("SEMCTA") for ln in resto):
        resto = ["SEMABERTURA", "SEMCTA", "ESTILO 0"] + resto
    plano.write_text("\n".join(resto[:3] + linhas + resto[3:]) + "\n", encoding="utf-8")
    print(f"plano: {plano}")


def main() -> None:
    cmd, T, js = sys.argv[1], Path(sys.argv[2]), json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
    if cmd == "folha":
        print(folha(T, js))
    elif cmd == "baixar":
        baixar(T, js)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
