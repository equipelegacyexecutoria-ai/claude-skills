"""Medidas de texto idênticas às do libass (HarfBuzz + métricas da fonte).

- O libass escala a fonte para que (ascender + descender) = tamanho ASS (\\fs).
- \\fsp é somado DEPOIS de cada glifo.
- O libass DESLIGA o kerning quando \\fsp != 0. Por isso o kerning da fonte é
  aplicado à mão: cada letra recebe o seu próprio \\fsp = espaçamento + kerning do par.
  (Sem isso, com espaçamento negativo, "VA", "TA", "AT" se atropelam e o resto abre.)
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

FONTS = Path(__file__).resolve().parent.parent / "fonts"
BS = "\\"


class Fonte:
    def __init__(self, arquivo: str):
        path = FONTS / arquivo
        self.tt = TTFont(str(path))
        self.upm = self.tt["head"].unitsPerEm
        os2 = self.tt["OS/2"]
        # o libass imita o GDI: usa usWinAscent/usWinDescent (na SF Pro = hhea; na Inter não)
        self.asc = os2.usWinAscent
        self.desc = os2.usWinDescent
        self.cap = os2.sCapHeight
        self.gs = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()
        self.hbfont = hb.Font(hb.Face(hb.Blob.from_file_path(str(path))))
        self._bounds: dict[str, tuple | None] = {}
        self._cache: dict[tuple, tuple] = {}

    # ---- métricas verticais (px, para um \fs do libass) ----
    def em(self, fs: float) -> float:
        return fs * self.upm / (self.asc + self.desc)

    def cap_px(self, fs: float) -> float:
        return self.em(fs) * self.cap / self.upm

    def fs_para_cap(self, cap_px: float) -> float:
        return cap_px * (self.asc + self.desc) / self.cap

    def captop_px(self, fs: float) -> float:
        """Do topo da caixa (\\an7) até o topo das maiúsculas."""
        return self.em(fs) * (self.asc - self.cap) / self.upm

    # ---- horizontal ----
    def _gb(self, name: str):
        if name not in self._bounds:
            bp = BoundsPen(self.gs)
            self.gs[name].draw(bp)
            self._bounds[name] = bp.bounds
        return self._bounds[name]

    def _shape(self, texto: str, kern: bool):
        buf = hb.Buffer()
        buf.add_str(texto)
        buf.guess_segment_properties()
        hb.shape(self.hbfont, buf, {"kern": kern, "liga": False, "clig": False})
        return [(self.order[i.codepoint], i.cluster, p.x_advance, p.x_offset)
                for i, p in zip(buf.glyph_infos, buf.glyph_positions)]

    def layout(self, texto: str, fs: float, track: float):
        """Posição de cada letra como o libass vai desenhar com os \\fsp por letra.

        Devolve (x0_tinta, x1_tinta, fsp_por_letra) com a origem do texto em x=0.
        """
        chave = (texto, round(fs, 2), round(track, 3))
        if chave in self._cache:
            return self._cache[chave]
        s = self.em(fs) / self.upm
        com = self._shape(texto, True)
        sem = self._shape(texto, False)
        if len(com) != len(sem) or len(com) != len(texto):
            raise ValueError(f"texto com glifos compostos não suportado: {texto!r}")
        fsps = []
        x = 0.0
        x0 = x1 = None
        for (g, _, adv_k, off), (_, _, adv, _) in zip(com, sem):
            b = self._gb(g)
            if b:
                a, z = x + (off + b[0]) * s, x + (off + b[2]) * s
                x0 = a if x0 is None else min(x0, a)
                x1 = z if x1 is None else max(x1, z)
            kern_px = (adv_k - adv) * s
            fsp = track + kern_px
            fsps.append(fsp)
            x += adv * s + fsp          # o libass avança sem kerning + \fsp da letra
        res = (x0 or 0.0, x1 or 0.0, fsps)
        self._cache[chave] = res
        return res

    def glifos(self, texto: str, fs: float, track: float) -> list[tuple[float, float, float, float]]:
        """Caixa de tinta de cada letra: (x0, x1, subida acima da maiúscula, descida abaixo da base),
        em px, com a origem do texto em x=0 (mesmas posições do libass com \\fsp por letra)."""
        s = self.em(fs) / self.upm
        _, _, fsps = self.layout(texto, fs, track)
        out = []
        x = 0.0
        for (g, _, adv_k, off), (_, _, adv, _), sp in zip(self._shape(texto, True), self._shape(texto, False), fsps):
            b = self._gb(g)
            if b:
                out.append((x + (off + b[0]) * s, x + (off + b[2]) * s,
                            max(0.0, (b[3] - self.cap) * s), max(0.0, -b[1] * s)))
            x += adv * s + sp
        return out

    def largura(self, texto: str, fs: float, track: float) -> float:
        x0, x1, _ = self.layout(texto, fs, track)
        return x1 - x0

    def x0(self, texto: str, fs: float, track: float) -> float:
        return self.layout(texto, fs, track)[0]


def escapar(c: str) -> str:
    return {"{": "(", "}": ")", "\\": "/"}.get(c, c)


def ass_texto(f: Fonte, texto: str, fs: float, track: float) -> str:
    """Texto com um \\fsp por letra (kerning + espaçamento)."""
    _, _, fsps = f.layout(texto, fs, track)
    partes = []
    ultimo = None
    for c, sp in zip(texto, fsps):
        v = round(sp, 2)
        if v != ultimo:
            partes.append("{" + BS + f"fsp{v:g}" + "}")
            ultimo = v
        partes.append(escapar(c))
    return "".join(partes)


@lru_cache(maxsize=4)
def fonte(arquivo: str) -> Fonte:
    return Fonte(arquivo)
