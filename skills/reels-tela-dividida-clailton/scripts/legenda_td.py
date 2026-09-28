"""Legenda da tela dividida (.ass para o libass): medida nos reels da equipe.

- corpo: 1 linha de 1-4 palavras, SF Pro Text Black, maiúscula 34 px, espaçamento -0,085 em com
  kerning à mão (texto.py da novela), centro em y=1175, branca, sombra v3 (halo + contato), troca
  seca no início da palavra.
- abertura (tela dividida): a legenda vira TARJA — caixa preta colada na emenda, texto branco
  (maiúscula 52 px). Com ETIQUETA no plano: etiqueta fixa colorida na emenda e legenda pequena
  embaixo, sobre o Clailton.
- item 'dividida' no meio do vídeo: legenda sobe para a emenda (o rosto dele fica embaixo).
- NUMERO: número grande (maiúscula 135 px) no meio da tela.
- CTA: a mesma da novela (máquina de escrever).

Uso: python legenda_td.py <trabalho>   (lê timeline.json; grava legenda.ass e copia as fontes)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from td_comum import (EMENDA, ETIQUETA_CAP, ETIQUETA_CORES, ETIQUETA_LEG_Y, FPS, LEG_CAP, LEG_MAX_LARG, LEG_TRACK, LEG_Y,  # noqa: E402
                      NUMERO_CAP, NUMERO_Y, TARJA_CAP, TARJA_PAD_X, TARJA_PAD_Y, W, gravar_json, ler_json)

import legenda_novela as LN  # noqa: E402  (HEADER, sombra v3, CTA, tempos)
from comum import preparar_fontes  # noqa: E402
from texto import ass_texto, fonte  # noqa: E402

BS = "\\"
F = fonte("SF-Pro-Text-Black.otf")
SOMBRA = LN.SOMBRA


def t_ass(n: int) -> str:
    return LN.ass_tempo(LN.borda(n))


def linha(texto: str, cap: float, cx: float, cy_cap: float, n0: int, n1: int, camada: int,
          larg_max: float = LEG_MAX_LARG, cor: str = "FFFFFF", sombra: bool = True) -> list[str]:
    """Uma linha centrada em cx, com o CENTRO DA MAIÚSCULA em cy_cap."""
    fs = F.fs_para_cap(cap)
    track = LEG_TRACK * fs
    larg = F.largura(texto, fs, track)
    if larg > larg_max:                                   # linha comprida encolhe
        fs *= larg_max / larg
        track = LEG_TRACK * fs
        larg = F.largura(texto, fs, track)
    x_orig = cx - larg / 2 - F.x0(texto, fs, track)
    y_orig = cy_cap - F.cap_px(fs) / 2 - F.captop_px(fs)
    corpo = ass_texto(F, texto, fs, track)
    ev = []
    if sombra:
        for sh in SOMBRA:
            tag = (BS + "an7" + BS + f"pos({x_orig + sh['dx']:.1f},{y_orig + sh['dy']:.1f})" + BS + f"fs{fs:.2f}"
                   + BS + "1c&H000000&" + BS + "3c&H000000&" + BS + f"bord{sh['bord']}" + BS + "shad0"
                   + BS + f"blur{sh['blur']}" + BS + f"alpha&H{sh['alpha']}&")
            ev.append(f"Dialogue: {camada},{t_ass(n0)},{t_ass(n1)},Cap,,0,0,0,,{{{tag}}}{corpo}")
    tag = (BS + "an7" + BS + f"pos({x_orig:.1f},{y_orig:.1f})" + BS + f"fs{fs:.2f}" + BS + f"1c&H{cor}&"
           + BS + "bord0" + BS + "shad0")
    ev.append(f"Dialogue: {camada + 1},{t_ass(n0)},{t_ass(n1)},Cap,,0,0,0,,{{{tag}}}{corpo}")
    return ev


def caixa(x0: float, y0: float, x1: float, y1: float, n0: int, n1: int, camada: int, cor_bgr: str) -> str:
    w, h = x1 - x0, y1 - y0
    tag = BS + "an7" + BS + f"pos({x0:.1f},{y0:.1f})" + BS + "p1" + BS + "bord0" + BS + "shad0" + BS + f"1c&H{cor_bgr}&"
    return f"Dialogue: {camada},{t_ass(n0)},{t_ass(n1)},Cap,,0,0,0,,{{{tag}}}m 0 0 l {w:.1f} 0 l {w:.1f} {h:.1f} l 0 {h:.1f}{{{BS}p0}}"


def tarja(texto: str, n0: int, n1: int, camada: int = 20, cor_caixa: str = "000000", cor_txt: str = "FFFFFF",
          cap: float = TARJA_CAP, topo: float = EMENDA - 6) -> list[str]:
    fs = F.fs_para_cap(cap)
    track = LEG_TRACK * fs
    larg = F.largura(texto, fs, track)
    if larg > W - 120:
        fs *= (W - 120) / larg
        track = LEG_TRACK * fs
        larg = F.largura(texto, fs, track)
    cap_px = F.cap_px(fs)
    alt = cap_px + 2 * (TARJA_PAD_Y + 7)
    x0 = (W - larg) / 2 - TARJA_PAD_X
    ev = [caixa(x0, topo, x0 + larg + 2 * TARJA_PAD_X, topo + alt, n0, n1, camada, cor_caixa)]
    ev += linha(texto, cap_px, W / 2, topo + alt / 2, n0, n1, camada + 1, larg_max=W - 120, cor=cor_txt, sombra=False)
    return ev


def etiqueta(texto: str, cor: str, n0: int, n1: int) -> list[str]:
    """Etiqueta fixa de 1-2 linhas (quebra no meio das palavras) em caixa colorida, na emenda."""
    palavras = texto.split()
    if len(" ".join(palavras)) > 22 and len(palavras) > 2:
        meio = min(range(1, len(palavras)), key=lambda k: abs(len(" ".join(palavras[:k])) - len(" ".join(palavras[k:]))))
        linhas = [" ".join(palavras[:meio]), " ".join(palavras[meio:])]
    else:
        linhas = [texto]
    fs = F.fs_para_cap(ETIQUETA_CAP)
    track = LEG_TRACK * fs * 0.6
    largs = [F.largura(l, fs, track) for l in linhas]
    esc = min(1.0, (W - 160) / max(largs))
    fs *= esc
    track *= esc
    largs = [F.largura(l, fs, track) for l in linhas]
    cap_px = F.cap_px(fs)
    entre = cap_px * 0.55
    alt = len(linhas) * cap_px + (len(linhas) - 1) * entre + 2 * 28
    topo = EMENDA - alt / 2
    x0 = (W - max(largs)) / 2 - 30
    cor_bgr = ETIQUETA_CORES.get(cor, "0000C3")
    txt = "000000" if cor == "branca" else "FFFFFF"
    ev = [caixa(x0, topo, x0 + max(largs) + 60, topo + alt, n0, n1, 20, cor_bgr)]
    for k, l in enumerate(linhas):
        cy = topo + 28 + k * (cap_px + entre) + cap_px / 2
        ev += linha(l, cap_px, W / 2, cy, n0, n1, 21, larg_max=W - 160, cor=txt, sombra=False)
    return ev, topo + alt


def em_dividida(tl: dict) -> list[tuple[int, int]]:
    faixas = [(tl["abertura"]["f0"], tl["abertura"]["f1"])]
    faixas += [(c["f0"], c["f1"]) for c in tl["camadas"] if c["layout"] == "dividida"]
    return faixas


def main() -> None:
    T = Path(sys.argv[1])
    tl = ler_json(T / "timeline.json")
    F_FALA = tl["frames_fala"]
    ev: list[str] = []
    ab = tl["abertura"]
    etq = ab.get("etiqueta")
    base_etq = None
    if etq and etq.get("texto"):
        e, base_etq = etiqueta(etq["texto"], etq["cor"], ab["f0"], ab["f1"])
        ev += e
    divs = em_dividida(tl)
    for t in tl["legendas"]:
        if t.get("oculta"):
            continue
        n0, n1 = t["f0"], min(t["f1"], F_FALA)
        if n1 <= n0:
            continue
        na_abertura = t["estilo"] == "tarja"
        if na_abertura and not base_etq:
            ev += tarja(t["texto"], n0, n1)
        elif na_abertura and base_etq:
            ev += linha(t["texto"], LEG_CAP, W / 2, max(base_etq + 90, ETIQUETA_LEG_Y), n0, n1, 10)
        elif any(a <= n0 < b for a, b in divs[1:]):
            # imagem em cima, Clailton embaixo: legenda na emenda (o rosto fica embaixo)
            ev += linha(t["texto"], LEG_CAP * 1.18, W / 2, EMENDA + 4, n0, n1, 10)
        else:
            ev += linha(t["texto"], LEG_CAP, W / 2, LEG_Y, n0, n1, 10)
    for nu in tl["numeros"]:
        ev += linha(nu["texto"].upper(), NUMERO_CAP, W / 2, NUMERO_Y, nu["f0"], nu["f1"], 30, larg_max=W - 140)
    fim = F_FALA / FPS
    total = fim
    if tl["cta"]:
        ev += LN.eventos_cta(fim)
        total = fim + LN.CTA_DUR
    (T / "legenda.ass").write_text(LN.HEADER + "\n".join(ev) + "\n", encoding="utf-8")
    preparar_fontes(T)
    gravar_json(T / "layout.json", {"fim_fala": round(fim, 3), "cta_inicio": round(fim, 3), "duracao_total": round(total, 3),
                                    "cta": tl["cta"], "frames_total": int(round(total * FPS)) if tl["cta"] else F_FALA})
    print(f"ok: legenda.ass ({len(ev)} eventos), {len(tl['legendas'])} telas, fim {total:.2f}s")


if __name__ == "__main__":
    main()
