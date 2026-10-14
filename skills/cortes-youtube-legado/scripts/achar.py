"""Acha frases na transcrição e devolve o tempo DA AULA (para cravar cortes pelo texto, não pelo relógio).

Uso:
  python achar.py <trabalho> "frase exata ou quase" [--perto 01:20:40] [--raio 120]
  python achar.py <trabalho> --ep "<arquivo do episódio>" 13:16     (tempo do EPISÓDIO -> tempo da aula + palavras)

No plano.json, cada episódio aceita "cortar": lista de
  ["01:04:42.0", "01:04:49.2"]                              (intervalo da aula) ou
  {"frase": "e você acaba nem dando no final do ano o 14º salário", "perto": "01:04:44"}  ou
  {"de": "Então, o financeiro", "ate": "é aumentar faturamento", "perto": "02:04:24"}     ou
  {"de": "Aí eu peguei o regulamento", "ate_antes": "Eu só subi disso", "perto": "01:54:02"}
e o render tira esses pedaços dos trechos (o corte cai no meio da pausa antes/depois da frase).
Cortar pelo texto é mais seguro que pelo relógio: a frase é achada na transcrição e o corte nunca pega
meia palavra.
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import hms, ler_json, seg  # noqa: E402


def norm(t: str) -> str:
    t = unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9%]+", "", t)


def achar_frase(palavras: list[dict], frase: str, perto: float | None = None, raio: float = 120):
    """Melhor ocorrência da frase (tolera 1 palavra diferente a cada 6). Devolve (i0, i1) ou None."""
    alvo = [norm(x) for x in frase.split() if norm(x)]
    n = len(alvo)
    if not n:
        return None
    toks = [norm(w["t"]) for w in palavras]
    tol = n // 6
    melhor = None
    for i in range(len(toks) - n + 1):
        if perto is not None and abs(palavras[i]["ini"] - perto) > raio:
            continue
        erros = sum(1 for a, b in zip(alvo, toks[i:i + n]) if a != b)
        if erros <= tol:
            d = abs(palavras[i]["ini"] - perto) if perto is not None else 0
            chave = (erros, d)
            if melhor is None or chave < melhor[0]:
                melhor = (chave, (i, i + n - 1))
    return melhor[1] if melhor else None


def intervalo_de_corte(palavras: list[dict], i0: int, i1: int) -> tuple[float, float]:
    """Do meio da pausa antes da 1ª palavra ao meio da pausa depois da última (máx. 0,25 s de folga)."""
    a = palavras[i0]["ini"]
    b = palavras[i1]["fim"]
    if i0 > 0:
        a = max((palavras[i0 - 1]["fim"] + a) / 2, a - 0.25)
    if i1 + 1 < len(palavras):
        b = min((b + palavras[i1 + 1]["ini"]) / 2, b + 0.25)
    return round(a, 3), round(b, 3)


def _achar(palavras, frase, perto, raio):
    r = achar_frase(palavras, frase, perto, raio)
    if not r:
        raise SystemExit(f"[cortar] não achei a frase: {frase!r} perto de {hms(perto) if perto else '-'}")
    return r


def resolver_cortes(palavras: list[dict], cortes: list) -> list[tuple[float, float]]:
    """Cada corte: ["hh:mm:ss.ss", "hh:mm:ss.ss"] (tempo da aula) ou um dict com "perto" (opcional) e
    {"frase": "..."}                          tira só essa frase
    {"de": "...", "ate": "..."}               tira do início de "de" até o fim de "ate" (inclusive)
    {"de": "...", "ate_antes": "..."}         tira do início de "de" até logo antes de "ate_antes"
    """
    out = []
    for c in cortes or []:
        if not isinstance(c, dict):
            out.append((seg(c[0]), seg(c[1])))
            continue
        perto, raio = (seg(c["perto"]) if c.get("perto") else None), c.get("raio", 120)
        if "frase" in c:
            out.append(intervalo_de_corte(palavras, *_achar(palavras, c["frase"], perto, raio)))
            continue
        i0, _ = _achar(palavras, c["de"], perto, raio)
        depois = palavras[i0]["ini"]
        if "ate" in c:
            _, i1 = _achar(palavras, c["ate"], depois + raio / 2, raio / 2)
        else:
            j0, _ = _achar(palavras, c["ate_antes"], depois + raio / 2, raio / 2)
            i1 = j0 - 1
        if i1 < i0:
            raise SystemExit(f"[cortar] fim antes do início: {c}")
        out.append(intervalo_de_corte(palavras, i0, i1))
    return out


def tirar_intervalos(segs, cortes):
    """Subtrai os intervalos de corte dos trechos."""
    for x, y in sorted(cortes):
        novo = []
        for a, b in segs:
            if y <= a or x >= b:
                novo.append((a, b))
                continue
            if x > a:
                novo.append((a, x))
            if y < b:
                novo.append((y, b))
        segs = novo
    return [(a, b) for a, b in segs if b - a > 0.3]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("trabalho")
    ap.add_argument("frase", nargs="?")
    ap.add_argument("--perto")
    ap.add_argument("--raio", type=float, default=120)
    ap.add_argument("--ep")
    a = ap.parse_args()
    trab = Path(a.trabalho)
    pal = ler_json(trab / "transcricao.json")["palavras"]
    if a.ep:
        info = ler_json(trab / "render" / f"{a.ep}.json")
        t = seg(a.frase)
        off = 0.0
        for x, y in info["trechos_finais"]:
            if off <= t <= off + (y - x):
                ta = x + t - off
                viz = [w for w in pal if abs(w["ini"] - ta) <= 8]
                print(f"episódio {hms(t)} = aula {hms(ta, True)}")
                print(" ".join(f"[{hms(w['ini'], True)[3:]}]{w['t']}" for w in viz))
                return
            off += y - x
        print("fora do episódio")
        return
    r = achar_frase(pal, a.frase, seg(a.perto) if a.perto else None, a.raio)
    if not r:
        print("não achei")
        return
    i0, i1 = r
    x, y = intervalo_de_corte(pal, i0, i1)
    print(f"aula {hms(pal[i0]['ini'], True)} → {hms(pal[i1]['fim'], True)}  (corte {hms(x, True)} → {hms(y, True)})")
    print(" ".join(w["t"] for w in pal[max(0, i0 - 6):i1 + 7]))


if __name__ == "__main__":
    main()
