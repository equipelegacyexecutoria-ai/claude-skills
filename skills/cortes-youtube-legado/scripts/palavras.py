"""Mostra as palavras (com tempo) em volta de instantes da aula, para cravar os pontos de corte.

Uso: python palavras.py <trabalho> 00:11:10 00:26:04 ... [--janela 12]
Cada palavra sai como  [mm:ss.cc]palavra~ss.cc (início e fim) e as pausas ≥ 0,4 s aparecem como  ·· 0.85s ··
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import hms, ler_json, seg  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("trabalho")
    ap.add_argument("tempos", nargs="+")
    ap.add_argument("--janela", type=float, default=12)
    a = ap.parse_args()
    pal = ler_json(Path(a.trabalho) / "transcricao.json")["palavras"]
    for t in a.tempos:
        t0 = seg(t)
        print(f"===== {hms(t0)} (±{a.janela:.0f}s)")
        sel = [w for w in pal if t0 - a.janela <= w["ini"] <= t0 + a.janela]
        linha, ant = [], None
        for w in sel:
            if ant is not None and w["ini"] - ant["fim"] >= 0.4:
                print(" ".join(linha))
                print(f"   ·· {w['ini'] - ant['fim']:.2f}s ··")
                linha = []
            linha.append(f"[{hms(w['ini'], True)[3:]}]{w['t']}~{w['fim'] % 60:05.2f}")
            ant = w
        if linha:
            print(" ".join(linha))


if __name__ == "__main__":
    main()
