"""Legenda estilo NOVELA (Clailton) -> .ass 1080x1920 para queimar com o libass.

Referência decupada quadro a quadro: reel "Você quer ficar rico? Então torna-te um PHD"
(ver referencia/estilo-novela.md). Resumo do que este gerador reproduz:

- Faixa de imagem 1080x864 (5:4) centrada (y 528..1392), barras pretas em cima e embaixo.
- Legenda em SF Pro Text Black, caixa-alta, branca, blocos ("telas") de 1-3 linhas.
- Linha NORMAL: fs 75 (maiúscula ~45 px), espaçamento -0,075*fs, entra inteira quando a
  primeira palavra dela é falada.
- DESTAQUE: entra sozinho, maior, na hora da palavra. d1 ~640 px de largura (maiúscula 60-90),
  d2 forte ~780 px (95-120), d3 impacto = palavra sozinha na tela (150-205). Espaçamento -0,10*fs.
- Linhas coladas: 11 px entre a base de uma e o topo da maiúscula da seguinte.
- A sombra de cada linha cai POR CIMA da linha de baixo (efeito de profundidade da referência).
- Sombra v3 aprovada pelo usuário: halo (0,3) bord 10 blur 22 ~45% + contato (1,4) bord 2 blur 4 ~72%.
- Entrada: aparece desfocada ~23 px acima, desce e fica nítida em 8 quadros (curva medida).
- Troca de tela = corte seco (sem saída animada).
- Âncora opcional (ex.: "P" -> "PH" -> "PHD"): título fixo no alto à esquerda enquanto as
  telas de baixo trocam.
- CTA final: tela preta, "ME SIGA PARA MAIS / CONTEÚDOS COMO ESTE" digitado letra a letra
  (Inter 28pt ExtraBold, substituta da SF Pro Display Bold da referência).

Uso:
  python legenda_novela.py --plano legenda.json --palavras palavras_corte.json \
      --out legenda.ass [--rosto rosto_corte.json] [--layout-out layout.json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from texto import ass_texto, fonte  # noqa: E402

BS = "\\"
FPS = 30000 / 1001
W, H = 1080, 1920
FAIXA_Y0, FAIXA_H = 528, 864
FAIXA_Y1 = FAIXA_Y0 + FAIXA_H

# ---------------- fonte e tamanhos (calibrados contra a referência) ----------------
FONTE_ARQ = "SF-Pro-Text-Black.otf"
FONTE_ASS = "SFProText-Black"          # nome PostScript: "SF Pro Text Black" cai em Arial no libass
F = fonte(FONTE_ARQ)

FS_NORMAL = 75.0                       # maiúscula ~44 px (referência: 45 +- 1)
FS_NORMAL_MIN = 62.0                   # linha normal comprida encolhe até aqui
TRACK_NORMAL = -0.075                  # * fs, por letra (com kerning aplicado à mão)
TRACK_DESTAQUE = -0.100
NIVEIS = {                             # largura-alvo (px) e faixa de altura da maiúscula (px)
    "d1": dict(alvo=640, cap_min=60, cap_max=90),
    "d2": dict(alvo=780, cap_min=95, cap_max=120),
    "d3": dict(alvo=720, cap_min=150, cap_max=205),
}
CAP_ANCORA = 100.0

GAP = 11.0                             # base da linha de cima -> topo da maiúscula da de baixo
Y_CENTRO = 1120.0                      # centro vertical do bloco (~69% da faixa: peito)
TOPO_MIN = 880.0                       # bloco não sobe além disso (rosto)
BASE_MAX = FAIXA_Y1 - 30.0             # nem desce além disso
COR_DESTAQUE = "FFFFFF"                # RRGGBB dos destaques (d1/d2/d3); caixinha 0800 usa azul (--cor-destaque)
X_MIN, X_MAX = 95.0, 985.0             # margens laterais (tinta)
LARG_MAX = X_MAX - X_MIN
X_ESQ = 165.0                          # alinhamento à esquerda (15% da largura)
PASSO_ESCADA = 100.0
ESCADA_LINHA_MIN = 200.0               # px: linha mais estreita que isso na escada fica solta -> vira esquerda
X_ANCORA, Y_ANCORA = 97.0, 852.0       # tinta esquerda e topo da maiúscula da âncora
RECUO_SOB_ANCORA = 20.0

# ---------------- sombra v3 (aprovada) ----------------
# Camadas (medido na referência): linha de cima é branco chapado; a de baixo escurece ~25% no
# topo SÓ onde há letra em cima = o halo da linha de cima cai sobre ela. O contato (forte) fica
# embaixo de todas as linhas — senão apaga o acento da linha de baixo que sobe no vão.
SOMBRA = [dict(nome="halo", dx=0, dy=3, bord=10, blur=22, alpha="8C"),      # halo difuso ~45%
          dict(nome="contato", dx=1, dy=4, bord=2, blur=4, alpha="48")]     # contato ~72%

# ---------------- entrada (medida quadro a quadro na referência) ----------------
QUEDA = 23.0                                                # px que a linha desce ao entrar
R_POS = [1.0, 0.95, 0.55, 0.22, 0.09, 0.035, 0.01, 0.0]     # fração restante do deslocamento
R_BLUR = [1.0, 1.0, 0.72, 0.6, 0.47, 0.3, 0.13, 0.0]        # fração restante do desfoque


def blur_inicial(fs: float) -> float:
    return 4.2 + 0.0065 * max(0.0, fs - FS_NORMAL)          # ~4 nas pequenas, ~6 nas gigantes


# ---------------- CTA ----------------
CTA_FONTE_ARQ = "Inter_28pt-ExtraBold.ttf"
CTA_FONTE_ASS = "Inter 28pt ExtraBold"
CTA_LINHAS = ["ME SIGA PARA MAIS", "CONTEÚDOS COMO ESTE"]
CTA_CAP = 55.0
CTA_TOPOS = [811.0, 902.0]
CTA_TRACK = -1.5
CTA_DUR = 2.9                     # tela preta até o fim
CTA_ATRASO = 0                    # quadros entre o corte para o preto e a 1a letra
CTA_DIGITACAO = 0.76              # s entre a 1a e a última letra (~47 letras/s)
CTA_FADE_LETRA = 0.045            # cada letra acende em ~1,5 quadro
FIM_RESPIRO = 0.45                # última palavra -> corte para o preto

# O Whisper marca a palavra cedo demais quando ela vem colada na anterior (fala corrida):
# na referência a tela troca no ataque real, 0,1-0,28 s depois. Depois de pausa ele acerta.
ATRASO_FALA_CORRIDA = 0.15
PAUSA_CORRIDA = 0.12
TELA_MIN = 0.55                   # tela mais curta que isso não dá tempo de ler


# ======================================================================================
def ass_tempo(t: float) -> str:
    t = max(0.0, t)
    cs = int(round(t * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def quadro(t: float) -> int:
    return int(round(t * FPS))


def borda(n: int) -> float:
    """Tempo entre o quadro n-1 e o n (meio do intervalo): evento cobre quadros inteiros."""
    return (n - 0.5) / FPS


class Linha:
    def __init__(self, texto: str, tipo: str, t_in: float):
        self.texto = texto
        self.tipo = tipo                  # "normal" | "d1" | "d2" | "d3" | "ancora"
        self.t_in = t_in
        self.fs = FS_NORMAL
        self.track = TRACK_NORMAL * FS_NORMAL
        self.x = 0.0                      # tinta esquerda
        self.cap_top = 0.0

    @property
    def cap(self) -> float:
        return F.cap_px(self.fs)

    @property
    def largura(self) -> float:
        return F.largura(self.texto, self.fs, self.track)

    def dimensionar(self) -> list[str]:
        avisos = []
        if self.tipo == "normal":
            self.fs = FS_NORMAL
            self.track = TRACK_NORMAL * self.fs
            while self.largura > LARG_MAX - 60 and self.fs > FS_NORMAL_MIN:
                self.fs -= 1
                self.track = TRACK_NORMAL * self.fs
            if self.largura > LARG_MAX:
                avisos.append(f"linha normal larga demais ({self.largura:.0f}px): {self.texto}")
        elif self.tipo == "ancora":
            self.fs = F.fs_para_cap(CAP_ANCORA)
            self.track = TRACK_DESTAQUE * self.fs
        else:
            nv = NIVEIS[self.tipo]
            # largura/altura quase linear no fs: acha o fs que dá a largura-alvo
            fs0 = 100.0
            w0 = F.largura(self.texto, fs0, TRACK_DESTAQUE * fs0)
            fs = fs0 * nv["alvo"] / max(w0, 1)
            cap = F.cap_px(fs)
            cap = min(max(cap, nv["cap_min"]), nv["cap_max"])
            fs = F.fs_para_cap(cap)
            self.fs, self.track = fs, TRACK_DESTAQUE * fs
            while self.largura > LARG_MAX and self.fs > FS_NORMAL * 1.15:
                self.fs *= 0.98
                self.track = TRACK_DESTAQUE * self.fs
            if self.largura > LARG_MAX:
                avisos.append(f"destaque largo demais ({self.largura:.0f}px): {self.texto}")
        return avisos


class Bloco:
    def __init__(self, idx: int, linhas: list[Linha], layout: str | None, t_in: float):
        self.idx = idx
        self.linhas = linhas
        self.layout = layout
        self.t_in = t_in
        self.t_out = t_in
        self.sob_ancora = False


# ======================================================================================
def carregar(plano_path: Path, palavras_path: Path):
    if plano_path.suffix.lower() == ".txt":              # formato compacto (plano_texto.py)
        from plano_texto import ler_plano
        plano = ler_plano(plano_path)
    else:
        plano = json.loads(plano_path.read_text(encoding="utf-8"))
    pal = json.loads(palavras_path.read_text(encoding="utf-8"))
    palavras = pal["palavras"] if isinstance(pal, dict) else pal
    global ALINHADO
    ALINHADO = bool(isinstance(pal, dict) and pal.get("alinhado"))
    return plano, palavras


ALINHADO = False     # palavras com alinhamento forçado: tempo certo, sem compensação


def inicio_legenda(p: dict) -> float:
    t = float(p["inicio"])
    if not ALINHADO and float(p.get("pausa_antes", 9.0)) < PAUSA_CORRIDA:
        t += ATRASO_FALA_CORRIDA        # só com o tempo cru do Whisper (que adianta na fala corrida)
    return t


def validar_texto(t: str) -> str:
    t = t.strip()
    if t != t.upper():
        raise ValueError(f"legenda deve vir em caixa-alta: {t!r}")
    if re.search(r"[{}\\]", t):
        raise ValueError(f"caractere proibido na legenda: {t!r}")
    return re.sub(r"\s+", " ", t)


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s.upper())
    return re.sub(r"[^A-Z0-9%]", "", "".join(c for c in s if unicodedata.category(c) != "Mn"))


# palavra escrita na legenda -> formas faladas aceitas (normalização do estilo)
EQUIV = {"ESTOU": {"TO"}, "PARA": {"PRA", "PRO"}, "ESTA": {"TA"}, "VOCE": {"CE", "OCE"},
         "ESTAMOS": {"TAMO", "TAMOS"}, "ESTAVA": {"TAVA"}, "ESTAO": {"TAO"}}


def confere_palavra(texto_linha: str, palavras: list[dict], de: int) -> bool:
    """A linha começa pela fala do índice 'de'? Tolera: normalização (tô->ESTOU), hífen (TORNE-SE),
    artigo acrescentado na legenda e muleta falada que a legenda descartou ("Eu não tô" -> NÃO ESTOU)."""
    faladas = [_norm(p["texto"]) for p in palavras[de:de + 2]]
    escritas = [_norm(x.split("-")[0]) for x in texto_linha.split()][:2]
    for e in escritas:
        for f in faladas:
            if not e or not f:
                continue
            if e == f or f in EQUIV.get(e, set()) or (e[:1].isdigit() and not f.isdigit()):
                return True
            if min(len(e), len(f)) >= 4 and (e.startswith(f) or f.startswith(e)):
                return True
    return False


def montar(plano: dict, palavras: list[dict], fim_fala: float | None = None):
    avisos: list[str] = []
    blocos: list[Bloco] = []
    ultimo_de = -1
    for bi, b in enumerate(plano["blocos"]):
        linhas = []
        for ln in b["linhas"]:
            de = int(ln["de"])
            if not (0 <= de < len(palavras)):
                raise ValueError(f"bloco {bi+1}: índice de palavra fora do corte: {de}")
            if de <= ultimo_de:
                raise ValueError(f"bloco {bi+1}: 'de'={de} não é maior que o da linha anterior ({ultimo_de})")
            ultimo_de = de
            tipo = ln.get("destaque") or "normal"
            if tipo not in ("normal", "d1", "d2", "d3"):
                raise ValueError(f"bloco {bi+1}: destaque inválido {tipo!r}")
            texto = validar_texto(ln["texto"])
            if not confere_palavra(texto, palavras, de):
                avisos.append(f"bloco {bi+1}: '{texto}' aponta para a palavra falada "
                              f"'{palavras[de]['texto']}' (i={de}) — índice certo?")
            linhas.append(Linha(texto, tipo, inicio_legenda(palavras[de])))
        # linhas entram em ordem, com pelo menos 2 quadros entre elas
        for k in range(1, len(linhas)):
            linhas[k].t_in = max(linhas[k].t_in, linhas[k - 1].t_in + 2 / FPS)
        blocos.append(Bloco(bi, linhas, b.get("layout"), linhas[0].t_in))
        if len(blocos) > 1 and blocos[-1].t_in <= blocos[-2].t_in:
            raise ValueError(f"bloco {bi+1} começa antes (ou junto) do bloco {bi}: confira os índices 'de'")
    for k, b in enumerate(blocos):
        if k + 1 < len(blocos):
            b.t_out = blocos[k + 1].t_in
            if b.t_out < b.t_in + TELA_MIN:
                avisos.append(f"bloco {k+1} fica só {b.t_out - b.t_in:.2f}s na tela (mínimo {TELA_MIN}s)")
            for ln in b.linhas:
                if ln.t_in >= b.t_out - 1 / FPS:
                    avisos.append(f"bloco {k+1}: a linha '{ln.texto}' entra depois do próximo bloco")
        else:
            # a última tela vai até o fim da imagem (corte.json), onde entra a CTA
            ultimo = max(float(p["fim"]) for p in palavras)
            b.t_out = fim_fala if fim_fala else ultimo + FIM_RESPIRO
    # âncoras
    ancoras = []
    for a in plano.get("ancoras", []) or []:
        t0 = inicio_legenda(palavras[int(a["de"])])
        t_ate = inicio_legenda(palavras[int(a["ate"])])
        fim = next((b.t_in for b in blocos if b.t_in > t_ate + 1e-3), blocos[-1].t_out)
        ln = Linha(validar_texto(a["texto"]), "ancora", t0)
        ancoras.append((ln, t0, fim))
        for b in blocos:
            if b.t_in >= t0 - 1e-3 and b.t_in < fim - 1e-3:
                b.sob_ancora = True
    return blocos, ancoras, avisos


# ======================================================================================
def vao_entre(cima: Linha, baixo: Linha) -> float:
    """Espaço entre a base da linha de cima e o topo da maiúscula da de baixo.
    Padrão GAP (colado, como na referência). Abre SÓ quando um acento da linha de baixo
    (ou a cedilha/rabo da de cima) bate numa letra da outra linha — senão o acento some
    dentro da letra de cima (ex.: TALVEZ O / HÁBITO)."""
    precisa = GAP
    gc = [(x0 + cima.x - F.x0(cima.texto, cima.fs, cima.track), x1 + cima.x - F.x0(cima.texto, cima.fs, cima.track),
           des) for x0, x1, _, des in F.glifos(cima.texto, cima.fs, cima.track)]
    gb = [(x0 + baixo.x - F.x0(baixo.texto, baixo.fs, baixo.track), x1 + baixo.x - F.x0(baixo.texto, baixo.fs, baixo.track),
           sub) for x0, x1, sub, _ in F.glifos(baixo.texto, baixo.fs, baixo.track)]
    for (a0, a1, des) in gc:
        for (b0, b1, sub) in gb:
            if (des > 1 or sub > 1) and min(a1, b1) - max(a0, b0) > -2:
                precisa = max(precisa, des + sub + 4)
    return precisa


def layout_bloco(b: Bloco, queixo: float | None) -> list[str]:
    avisos = []
    for ln in b.linhas:
        avisos += ln.dimensionar()
    n = len(b.linhas)

    # 1) horizontal (o vão vertical depende de onde cada letra caiu)
    modo = b.layout or padrao_layout(b)
    ws = [ln.largura for ln in b.linhas]
    if b.sob_ancora and modo == "centro":
        modo = "esquerda"
    if modo == "centro":
        for ln, w in zip(b.linhas, ws):
            ln.x = (W - w) / 2
    elif modo in ("esquerda", "direita"):
        x0 = X_ANCORA + RECUO_SOB_ANCORA if b.sob_ancora else X_ESQ
        for ln in b.linhas:
            ln.x = x0
        if modo == "direita" and n >= 2:
            # a última fecha pela direita na borda da linha MAIS LARGA de cima (09/10/2026: alinhada só com a
            # penúltima, "TORCENDO / PARA QUE ELE / NÃO ACONTEÇA" ficou com duas bordas direitas = quebrada)
            borda_dir = max(ln.x + w for ln, w in zip(b.linhas[:-1], ws[:-1]))
            b.linhas[-1].x = max(x0, borda_dir - ws[-1])
        desloc = max(0.0, max(ln.x + ln.largura for ln in b.linhas) - X_MAX)
        for ln in b.linhas:
            ln.x = max(X_MIN, ln.x - desloc)
    elif modo == "escada" and min(ws) < ESCADA_LINHA_MIN:
        # linha curta na escada ("A", "SE", "AÍ VAI") fica solta, longe das outras: o usuário reprovou 3x
        # (09/10/2026, "o A ficou completamente fora da diagramação"). Vira esquerda.
        avisos.append(f"bloco {b.idx+1}: escada com linha curta ('{b.linhas[ws.index(min(ws))].texto}'), virou esquerda")
        modo = "esquerda"
        x0 = X_ANCORA + RECUO_SOB_ANCORA if b.sob_ancora else X_ESQ
        for ln in b.linhas:
            ln.x = x0
        desloc = max(0.0, max(ln.x + ln.largura for ln in b.linhas) - X_MAX)
        for ln in b.linhas:
            ln.x = max(X_MIN, ln.x - desloc)
    elif modo == "escada":
        passo = PASSO_ESCADA
        while True:
            larg = max(i * passo + w for i, w in enumerate(ws))
            if larg <= LARG_MAX or passo <= 30:
                break
            passo -= 10
        larg = max(i * passo + w for i, w in enumerate(ws))
        if b.sob_ancora:
            x0 = X_ANCORA + RECUO_SOB_ANCORA
        else:
            x0 = max(X_MIN, (W - larg) / 2)
        for i, ln in enumerate(b.linhas):
            ln.x = x0 + i * passo
        if larg > LARG_MAX:
            avisos.append(f"bloco {b.idx+1}: escada não coube, virou centro")
            for ln, w in zip(b.linhas, ws):
                ln.x = (W - w) / 2
    else:
        raise ValueError(f"bloco {b.idx+1}: layout desconhecido {modo!r}")
    b.layout = modo
    for ln in b.linhas:
        if ln.x < X_MIN - 1 or ln.x + ln.largura > X_MAX + 1:
            avisos.append(f"bloco {b.idx+1}: '{ln.texto}' encosta na margem")

    # 2) vertical: linhas coladas, com vão maior só onde acento/cedilha colide
    vaos = [vao_entre(b.linhas[i], b.linhas[i + 1]) for i in range(n - 1)]
    alt = sum(ln.cap for ln in b.linhas) + sum(vaos)
    if b.sob_ancora:
        topo = Y_ANCORA + F.cap_px(F.fs_para_cap(CAP_ANCORA)) + GAP + 6
    else:
        topo = Y_CENTRO - alt / 2
        topo = max(topo, TOPO_MIN)
        if queixo is not None:
            topo = max(topo, queixo + 12)
        if topo + alt > BASE_MAX:
            topo = BASE_MAX - alt
    y = topo
    for i, ln in enumerate(b.linhas):
        ln.cap_top = y
        y += ln.cap + (vaos[i] if i < n - 1 else 0)
    return avisos


def padrao_layout(b: Bloco) -> str:
    n = len(b.linhas)
    if n == 1:
        return "centro"
    if n == 3:
        return "escada"
    return "esquerda" if b.idx % 2 == 0 else "centro"


def layout_ancora(ln: Linha):
    ln.dimensionar()
    ln.x = X_ANCORA
    ln.cap_top = Y_ANCORA


# ======================================================================================
def eventos_linha(ln: Linha, t_out: float, base_layer: int, layer_contato: int = 5) -> list[str]:
    """Entrada quadro a quadro (8 quadros) + estado parado até t_out.
    Camadas: contato em layer_contato (abaixo de TODAS as linhas); halo em base_layer e
    texto em base_layer+1 (linha de cima com base maior: o halo dela cai na de baixo)."""
    ev = []
    n0 = quadro(ln.t_in)
    n_out = quadro(t_out)
    if n_out <= n0:
        return ev
    x_orig = ln.x - F.x0(ln.texto, ln.fs, ln.track)          # \an7: origem da caixa
    y_orig = ln.cap_top - F.captop_px(ln.fs)
    corpo = ass_texto(F, ln.texto, ln.fs, ln.track)
    b0 = blur_inicial(ln.fs)
    estados = [(R_POS[k] * QUEDA, R_BLUR[k] * b0) for k in range(len(R_POS))]
    trechos = []
    for k, (dy, bl) in enumerate(estados[:-1]):
        n = n0 + k
        if n >= n_out:
            break
        trechos.append((n, n + 1, dy, bl))
    n_parado = n0 + len(estados) - 1
    if n_parado < n_out:
        trechos.append((n_parado, n_out, 0.0, 0.0))
    for (na, nb, dy, bl) in trechos:
        t0, t1 = ass_tempo(borda(na)), ass_tempo(borda(nb))
        for sh in SOMBRA:
            tag = (BS + "an7" + BS + f"pos({x_orig + sh['dx']:.1f},{y_orig - dy + sh['dy']:.1f})"
                   + BS + f"fs{ln.fs:.2f}" + BS + "1c&H000000&" + BS + "3c&H000000&"
                   + BS + f"bord{sh['bord']}" + BS + "shad0" + BS + f"blur{sh['blur'] + bl:.2f}"
                   + BS + f"alpha&H{sh['alpha']}&")
            camada = layer_contato if sh["nome"] == "contato" else base_layer
            ev.append(f"Dialogue: {camada},{t0},{t1},Cap,,0,0,0,,{{{tag}}}{corpo}")
        cor = COR_DESTAQUE if ln.tipo in ("d1", "d2", "d3") else "FFFFFF"
        tag = (BS + "an7" + BS + f"pos({x_orig:.1f},{y_orig - dy:.1f})" + BS + f"fs{ln.fs:.2f}"
               + BS + f"1c&H{cor[4:6]}{cor[2:4]}{cor[0:2]}&" + BS + "bord0" + BS + "shad0" + BS + f"blur{bl:.2f}")
        ev.append(f"Dialogue: {base_layer + 1},{t0},{t1},Cap,,0,0,0,,{{{tag}}}{corpo}")
    return ev


def eventos_cta(t0: float) -> list[str]:
    fc = fonte(CTA_FONTE_ARQ)
    fs = fc.fs_para_cap(CTA_CAP)
    ev = []
    n_ini = quadro(t0) + CTA_ATRASO
    fim = t0 + CTA_DUR
    total = sum(len(l) for l in CTA_LINHAS)
    passo = CTA_DIGITACAO / max(1, total - 1)
    k = 0
    for li, txt in enumerate(CTA_LINHAS):
        x0, x1, fsps = fc.layout(txt, fs, CTA_TRACK)
        x_orig = (W - (x1 - x0)) / 2 - x0
        y_orig = CTA_TOPOS[li] - fc.captop_px(fs)
        partes = []
        for c, sp in zip(txt, fsps):
            ms0 = int(round(k * passo * 1000))
            ms1 = ms0 + int(CTA_FADE_LETRA * 1000)
            if c == " ":
                partes.append("{" + BS + f"fsp{sp:.2f}" + "} ")
            else:
                partes.append("{" + BS + f"fsp{sp:.2f}" + BS + "alpha&HFF&" + BS
                              + f"t({ms0},{ms1}," + BS + "alpha&H00&)}" + c)
            k += 1
        tag = BS + "an7" + BS + f"pos({x_orig:.1f},{y_orig:.1f})" + BS + f"fs{fs:.2f}" + BS + "bord0" + BS + "shad0"
        ev.append(f"Dialogue: 50,{ass_tempo(borda(n_ini))},{ass_tempo(fim)},CTA,,0,0,0,,{{{tag}}}" + "".join(partes))
    return ev


HEADER = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{FONTE_ASS},75,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: CTA,{CTA_FONTE_ASS},90,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def queixo_no_intervalo(rosto: list[dict] | None, t0: float, t1: float) -> float | None:
    if not rosto:
        return None
    ys = sorted(r["queixo"] for r in rosto if t0 - 0.05 <= r["t"] <= t1 + 0.05 and r.get("queixo"))
    if not ys:
        return None
    return ys[min(len(ys) - 1, int(0.9 * len(ys)))]      # p90: uma abaixada rápida não empurra a tela


def sha256(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def gerar(plano: dict, palavras: list[dict], rosto: list[dict] | None = None, com_cta: bool = True,
          fim_fala: float | None = None):
    blocos, ancoras, avisos = montar(plano, palavras, fim_fala)
    ev: list[str] = []
    for b in blocos:
        avisos += layout_bloco(b, queixo_no_intervalo(rosto, b.t_in, b.t_out))
        n = len(b.linhas)
        for i, ln in enumerate(b.linhas):
            ev += eventos_linha(ln, b.t_out, 10 + 2 * (n - 1 - i))
    for ln, t0, t1 in ancoras:
        layout_ancora(ln)
        ev += eventos_linha(ln, t1, 40)
    fim_fala = blocos[-1].t_out
    cta_ini = fim_fala
    if com_cta:
        ev += eventos_cta(cta_ini)
    info = {
        "fim_fala": round(fim_fala, 3),
        "cta_inicio": round(cta_ini, 3),
        "duracao_total": round(cta_ini + (CTA_DUR if com_cta else 0), 3),
        "blocos": [{"bloco": b.idx + 1, "t_in": round(b.t_in, 3), "t_out": round(b.t_out, 3), "layout": b.layout,
                    "sob_ancora": b.sob_ancora,
                    "linhas": [{"texto": ln.texto, "tipo": ln.tipo, "t_in": round(ln.t_in, 3), "fs": round(ln.fs, 1),
                                "cap": round(ln.cap, 1), "x": round(ln.x, 1), "largura": round(ln.largura, 1),
                                "cap_top": round(ln.cap_top, 1)} for ln in b.linhas]}
                   for b in blocos],
        "ancoras": [{"texto": ln.texto, "t_in": round(t0, 3), "t_out": round(t1, 3)} for ln, t0, t1 in ancoras],
        "avisos": avisos,
    }
    return HEADER + "\n".join(ev) + "\n", info


def main() -> None:
    global Y_CENTRO, TOPO_MIN, BASE_MAX, COR_DESTAQUE
    ap = argparse.ArgumentParser()
    ap.add_argument("--cor-destaque", help="RRGGBB dos destaques (padrão branco)")
    ap.add_argument("--plano", required=True)
    ap.add_argument("--palavras", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--rosto")
    ap.add_argument("--layout-out")
    ap.add_argument("--corte", help="corte.json: a CTA entra exatamente no fim da imagem (duracao_fala)")
    ap.add_argument("--sem-cta", action="store_true")
    # posição do bloco em outros formatos (edição simples: tela cheia, legenda no peito)
    ap.add_argument("--y-centro", type=float, help=f"centro vertical do bloco (padrão {Y_CENTRO:.0f})")
    ap.add_argument("--topo-min", type=float, help=f"o bloco não sobe além disso (padrão {TOPO_MIN:.0f})")
    ap.add_argument("--base-max", type=float, help=f"o bloco não desce além disso (padrão {BASE_MAX:.0f})")
    a = ap.parse_args()
    Y_CENTRO = a.y_centro if a.y_centro is not None else Y_CENTRO
    TOPO_MIN = a.topo_min if a.topo_min is not None else TOPO_MIN
    BASE_MAX = a.base_max if a.base_max is not None else BASE_MAX
    COR_DESTAQUE = (a.cor_destaque or COR_DESTAQUE).lstrip("#").upper()
    plano, palavras = carregar(Path(a.plano), Path(a.palavras))
    rosto = json.loads(Path(a.rosto).read_text(encoding="utf-8")) if a.rosto else None
    fim = None
    if a.corte:
        fim = float(json.loads(Path(a.corte).read_text(encoding="utf-8"))["duracao_fala"])
    ass, info = gerar(plano, palavras, rosto, com_cta=not a.sem_cta, fim_fala=fim)
    # trava: o render recusa legenda feita sobre outra versão das palavras do corte
    info["palavras_sha256"] = sha256(Path(a.palavras))
    Path(a.out).write_text(ass, encoding="utf-8")
    if a.layout_out:
        Path(a.layout_out).write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"blocos": len(info["blocos"]), "fim_fala": info["fim_fala"],
                      "duracao_total": info["duracao_total"], "avisos": info["avisos"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
