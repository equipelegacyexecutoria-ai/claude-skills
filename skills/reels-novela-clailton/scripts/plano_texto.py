"""Formato COMPACTO da legenda (economiza crédito do agente legendista).

Entrada do agente  -> palavras_legenda.txt  (gerado aqui: uma linha por frase, palavras numeradas)
Saída do agente    -> legenda.txt           (uma linha por tela), lido pelo legenda_novela.py

Formato do legenda.txt:
    # comentário
    esquerda | TALVEZ O @0 / *HÁBITO @2
    escada   | QUE MAIS VAI @3 / *MUDAR A TUA VIDA @6
    centro   | ***RENÚNCIA @260
    ancora   | P @27-35
- layout: centro | esquerda | escada | direita
- linhas separadas por " / "; cada linha termina com @índice da palavra falada que a dispara
- destaque: * = d1, ** = d2, *** = d3 no começo da linha
- ancora: texto @de-ate (título fixo enquanto as telas de baixo trocam)
- correção do Whisper: linha "correcao | i=212 whisper=Destocagem legenda=ESTOCAGEM motivo=..."

Uso: python plano_texto.py palavras <trabalho>      (gera palavras_legenda.txt)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

NIVEL = {1: "d1", 2: "d2", 3: "d3"}


def ler_plano(path: Path) -> dict:
    blocos, ancoras, correcoes = [], [], []
    for n, bruto in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        ln = bruto.strip()
        if not ln or ln.startswith("#"):
            continue
        if "|" not in ln:
            raise ValueError(f"legenda.txt linha {n}: falta '|': {ln}")
        cab, resto = [x.strip() for x in ln.split("|", 1)]
        cab = cab.lower()
        if cab == "correcao":
            correcoes.append(resto)
            continue
        if cab == "ancora":
            m = re.match(r"(.+?)\s*@(\d+)\s*-\s*(\d+)$", resto)
            if not m:
                raise ValueError(f"legenda.txt linha {n}: âncora precisa de 'TEXTO @de-ate': {ln}")
            ancoras.append({"texto": m.group(1).strip(), "de": int(m.group(2)), "ate": int(m.group(3))})
            continue
        if cab not in ("centro", "esquerda", "escada", "direita"):
            raise ValueError(f"legenda.txt linha {n}: layout desconhecido {cab!r}")
        linhas = []
        for parte in resto.split(" / "):
            m = re.match(r"(\**)\s*(.+?)\s*@(\d+)$", parte.strip())
            if not m:
                raise ValueError(f"legenda.txt linha {n}: cada linha precisa terminar com @índice: {parte!r}")
            ln_d = {"texto": m.group(2).strip(), "de": int(m.group(3))}
            if m.group(1):
                ln_d["destaque"] = NIVEL[min(3, len(m.group(1)))]
            linhas.append(ln_d)
        blocos.append({"layout": cab, "linhas": linhas})
    return {"blocos": blocos, "ancoras": ancoras, "correcoes": correcoes}


def palavras_legenda(trabalho: Path) -> Path:
    """Lista compacta para o legendista: frases (pausa >= 0,3 s) com as palavras numeradas."""
    pal = json.loads((trabalho / "palavras_corte.json").read_text(encoding="utf-8"))["palavras"]
    linhas, cur = [], []
    for w in pal:
        if cur and w["inicio"] - cur[-1]["fim"] >= 0.3:
            linhas.append(cur)
            cur = []
        cur.append(w)
    if cur:
        linhas.append(cur)
    txt = ["# palavras do corte: [índice]palavra — use o índice em @ na legenda.txt", ""]
    for ln in linhas:
        txt.append(f"{ln[0]['inicio']:6.1f}s  " + " ".join(f"[{w['i']}]{w['texto']}" for w in ln))
    out = trabalho / "palavras_legenda.txt"
    out.write_text("\n".join(txt) + "\n", encoding="utf-8")
    return out


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "palavras":
        print(palavras_legenda(Path(sys.argv[2])))
    elif len(sys.argv) >= 3 and sys.argv[1] == "ler":
        print(json.dumps(ler_plano(Path(sys.argv[2])), ensure_ascii=False, indent=1))
    else:
        print(__doc__)
