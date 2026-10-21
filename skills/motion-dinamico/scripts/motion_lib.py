# Motion Dinâmico: monta o index.html (HyperFrames) a partir das cenas escritas em Python e anota os efeitos sonoros.
# Uso típico (cenas.py do vídeo):
#   import sys; sys.path.insert(0, r"<skill>/scripts"); from motion_lib import *
#   v = Video(PROJETO, PALAVRAS_JSON, DUR, kicker="DEFEITO DE FÁBRICA")
#   v.cena("s1", 0, 3.4, "tenso", [img(...), titulo(...)], """ entra("#s1-x", 0.2, "pop"); """)
#   v.expert("assets/expert_a.mp4", 0, 3.4, cx=540, cy=760, w=640, h=800)
#   v.legenda(troca={30: "Laibson"}, destaque={2, 6}); v.gerar()
import html, json, os, re
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
_TAM, _RIG = {}, {}

FUNDOS = {  # fundo escuro com brilho (referências: dados com brilho amarelo; quadro de investigação)
    "escuro": "radial-gradient(ellipse 90% 55% at 50% 30%, #3a1711 0%, #1d0c09 55%, #0b0605 100%)",
    "tenso": "radial-gradient(ellipse 90% 55% at 50% 32%, #44120e 0%, #1f0908 55%, #090404 100%)",
    "quente": "radial-gradient(ellipse 90% 58% at 50% 32%, #5a2a10 0%, #2a120a 55%, #0d0604 100%)",
    "frio": "radial-gradient(ellipse 90% 55% at 50% 32%, #1d2230 0%, #10121a 55%, #06070a 100%)",
}


def esc(s):
    return html.escape(s, quote=False)


def h_de(nome, w):
    W, H = _TAM[nome]
    return round(w * H / W)


def camada(z, conteudo, nocomp=False, ident=""):
    nc = ' data-nocomp="1"' if nocomp else ""
    i = f' id="{ident}"' if ident else ""
    return f'<div class="z"{i} data-z="{z}"{nc}>{conteudo}</div>'


def _it(ident, cx, cy, w, h, dentro, cls="", estilo=""):
    return (f'<div class="it {cls}" id="{ident}" style="left:{cx - w / 2:.0f}px; top:{cy - h / 2:.0f}px; width:{w}px; height:{h}px;{estilo}">'
            f'<div class="fl">{dentro}</div></div>')


def img(ident, nome, cx, cy, w, z=0, cls="rec", estilo="", dentro="", nocomp=False):
    """Elemento recortado (PNG com borda branca) centrado em (cx, cy), largura w. A altura sai da proporção."""
    h = h_de(nome, w)
    ext = "jpg" if os.path.exists(os.path.join(_PROJ[0], "assets", "img", nome + ".jpg")) else "png"
    d = f'<img class="{cls}" src="assets/img/{nome}.{ext}" alt="" style="width:100%; height:100%;{estilo}" />{dentro}'
    return camada(z, _it(ident, cx, cy, w, h, d), nocomp)


_PROJ = [""]


def boneco(ident, rig, cx, cy, w, z=0):
    """Pessoa recortada com a cabeça separada (recortar_cabeca.py): a cabeça balança no pescoço."""
    r = _RIG[rig]
    h = round(w * r["H"] / r["W"])
    d = f'<div class="boneco rec" data-rig="{rig}" style="left:0; top:0; width:100%; height:100%"></div>'
    return camada(z, _it(ident, cx, cy, w, h, d))


def caixa(ident, cx, cy, w, h, conteudo, z=0, cls="", estilo=""):
    return camada(z, _it(ident, cx, cy, w, h, conteudo, cls, estilo))


def titulo(ident, linhas, cx, top, z=140, w=920, alinha="center"):
    """linhas: [(tamanho, [(texto, t, estilo), ...]), ...]. Cada palavra entra no tempo em que é falada.
    estilo: '' branco, 'ac' amarelo, 'rd' vermelho-laranja, 'hl' caixa amarela com texto escuro, 'dim' cinza, 'it' itálico (combináveis)."""
    out = []
    for tam, palavras in linhas:
        ps = []
        for texto, t, est in palavras:
            if "hl" in est.split():
                ps.append(f'<span class="pw {est}" data-t="{t}"><span class="marca"></span><span class="txt">{esc(texto)}</span></span>')
            else:
                ps.append(f'<span class="pw {est}" data-t="{t}">{esc(texto)}</span>')
        out.append(f'<div class="ln" style="font-size:{tam}px">{" ".join(ps)}</div>')
    it = f'<div class="it tit" id="{ident}" style="left:{cx - w / 2:.0f}px; top:{top}px; width:{w}px; text-align:{alinha}">{"".join(out)}</div>'
    return camada(z, it)


def letras(texto):
    return "".join(f'<span class="ch">{"&nbsp;" if c == " " else esc(c)}</span>' for c in texto)


def etiqueta(ident, texto, cx, cy, tam=44, z=150, cls="tag"):
    """Pílula (tag amarela; cls='tag lin' = contorno luminoso)."""
    it = f'<div class="it ctr" id="{ident}" style="left:{cx - 450}px; top:{cy}px; width:900px; text-align:center"><span class="{cls}" style="font-size:{tam}px">{esc(texto)}</span></div>'
    return camada(z, it)


def carimbo(ident, texto, cx, cy, tam=80, z=160, rot=-5):
    it = (f'<div class="it ctr" id="{ident}" style="left:{cx - 450}px; top:{cy}px; width:900px; text-align:center">'
          f'<span class="carimbo" style="font-size:{tam}px; transform:rotate({rot}deg)">{esc(texto)}</span></div>')
    return camada(z, it)


def svg(ident, conteudo, z=60, vb="0 0 1080 1920", estilo="left:0; top:0; width:1080px; height:1920px"):
    return camada(z, f'<svg class="it" id="{ident}" viewBox="{vb}" style="position:absolute; {estilo}; overflow:visible">{conteudo}</svg>')


def brilho(ident, cx, cy, r, cor="255,120,40", a=0.55, z=-300):
    it = (f'<div class="it" id="{ident}" style="left:{cx - r}px; top:{cy - r}px; width:{2 * r}px; height:{2 * r}px; border-radius:50%;'
          f' background: radial-gradient(circle, rgba({cor},{a}) 0%, rgba({cor},{a * .4:.2f}) 38%, rgba({cor},0) 70%)"></div>')
    return camada(z, it)


def cartao(ident, nome, cx, cy, rotulo, rot=0, pos="center", tam=42, w=420, h=440, z=0):
    """Cartão escuro com contorno luminoso: imagem em cima, rótulo embaixo."""
    fit = "contain" if pos == "center" else "cover"
    c = (f'<div class="card" style="width:{w}px; height:{h}px; transform:rotate({rot}deg)"><div class="foto" style="height:{h - 100}px">'
         f'<img src="assets/img/{nome}.png" alt="" style="object-fit:{fit}; object-position:{pos}" /></div>'
         f'<div class="rot" style="font-size:{tam}px">{esc(rotulo)}</div></div>')
    return caixa(ident, cx, cy, w, h, c, z)


def polaroid(ident, nome, cx, cy, w, legenda="", rot=3, z=0, digitar=True):
    """Foto presa com alfinete vermelho (quadro de investigação). A legenda pode ser digitada (digita('#id .ch'))."""
    W, H = _TAM[nome]
    fh = round((w - 36) * H / W)
    leg = letras(legenda) if digitar else esc(legenda)
    ext = "jpg" if os.path.exists(os.path.join(_PROJ[0], "assets", "img", nome + ".jpg")) else "png"
    c = (f'<div class="polaroid" style="width:{w}px; transform:rotate({rot}deg)"><span class="pino"></span>'
         f'<img src="assets/img/{nome}.{ext}" alt="" style="width:{w - 36}px; height:{fh}px" /><div class="pleg">{leg}</div></div>')
    return caixa(ident, cx, cy, w, fh + 110, c, z)


def selo(ident, nome, cx, cy, d=200, rotulo="", z=0):
    """Ícone dentro de um círculo com anel luminoso (linha do tempo das referências)."""
    r = f'<div class="selo-rot">{esc(rotulo)}</div>' if rotulo else ""
    c = f'<div class="selo" style="width:{d}px; height:{d}px"><img src="assets/img/{nome}.png" alt="" /></div>{r}'
    return caixa(ident, cx, cy, d, d, c, z)


def linha(ident_path, d, z=40, cor="#ffc414", larg=8, tracejada=False, seta=False):
    """Caminho luminoso (linha do tempo / ligação). Animar com traco('#id', t, dur)."""
    das = ' stroke-dasharray="2 22"' if tracejada else ""
    mk = ' marker-end="url(#seta)"' if seta else ""
    p = f'<path id="{ident_path}" class="luz" d="{d}" fill="none" stroke="{cor}" stroke-width="{larg}" stroke-linecap="round" stroke-linejoin="round"{das}{mk}/>'
    return svg(ident_path + "-svg", p, z)


def raios(ident, z=-500, op=0.35):
    return camada(z, f'<div class="raios" id="{ident}" style="opacity:{op}"></div>')


# ------------------------------------------------------------------ efeitos sonoros automáticos
# Cada chamada de animação vira um efeito (o mixador posiciona pelo pico do som). Volume relativo à voz.
SFX = {
    "pop": ("pop.mp3", 0.55), "sobe": ("whoosh-short.mp3", 0.35), "esq": ("whoosh-short.mp3", 0.45), "dir": ("whoosh-short.mp3", 0.45),
    "fade": (None, 0), "carimbo": ("impact-bass-1.mp3", 0.6), "digita": ("typing.mp3", 0.5), "traco": ("whoosh-short.mp3", 0.25),
    "bz": ("whoosh.mp3", 0.4), "soco": ("impact-bass-2.mp3", 0.35), "marca": ("click-soft.mp3", 0.35), "brilho": ("sparkle.mp3", 0.45),
    "ok": ("chime.mp3", 0.4), "tag": ("click.mp3", 0.35), "teclado": ("cta_teclado.mp3", 1.0), "tique": ("click-soft.mp3", 0.5),
    "virada": ("riser.mp3", 0.5), "doc": ("whoosh-doc.mp3", 0.4),
}


def _coleta_sfx(js):
    ev = []
    for m in re.finditer(r'entra\("([^"]+)",\s*([\d.]+)(?:,\s*"(\w+)")?', js):
        ev.append((float(m.group(2)), m.group(3) or "sobe", m.group(1)))
    for nome in ("carimbo", "digita", "traco", "bz", "soco"):
        for m in re.finditer(nome + r'\("([^"]+)",\s*([\d.]+)', js):
            ev.append((float(m.group(2)), nome, m.group(1)))
    for m in re.finditer(r'sfx\("(\w+)",\s*([\d.]+)', js):  # pedido explícito na cena: sfx("brilho", 48.5)
        ev.append((float(m.group(2)), m.group(1), ""))
    return ev


class Video:
    def __init__(self, projeto, palavras, dur, kicker=""):
        self.proj, self.dur, self.kicker = projeto, dur, kicker
        _PROJ[0] = projeto
        imgdir = os.path.join(projeto, "assets", "img")
        _TAM.clear(); _TAM.update({f.rsplit(".", 1)[0]: Image.open(os.path.join(imgdir, f)).size for f in os.listdir(imgdir) if f.endswith((".png", ".jpg"))})
        pj = os.path.join(projeto, "assets", "partes", "partes.json")
        _RIG.clear(); _RIG.update(json.load(open(pj, encoding="utf-8")) if os.path.exists(pj) else {})
        self.ws = json.load(open(palavras, encoding="utf-8"))["palavras"]
        self.cenas, self.experts, self.leg, self.sfx_extra = [], [], [], []

    def cena(self, ident, t0, t1, fundo, itens, js, sobre=None, js_sobre=""):
        self.cenas.append(dict(id=ident, t0=t0, t1=t1, fundo=fundo, itens=itens, js=js, sobre=sobre or [], js_sobre=js_sobre))

    def expert(self, arquivo, t0, dur, cx=540, cy=760, w=640, h=800):
        """Clailton (vídeo) num cartão com contorno luminoso. Fica na raiz (regra do HyperFrames para vídeo)."""
        self.experts.append(dict(arquivo=arquivo, t0=t0, dur=dur, cx=cx, cy=cy, w=w, h=h))

    def legenda(self, troca=None, destaque=None, fora=None, max_pal=4, max_car=24):
        """Legenda palavra a palavra: o grupo aparece apagado e cada palavra acende quando é falada (destaque em amarelo)."""
        troca, destaque, fora = troca or {}, destaque or set(), fora or set()
        grupos, atual = [], []
        for w in self.ws:
            if w["i"] in fora:
                continue
            texto = troca.get(w["i"], w["texto"]).rstrip(",.")
            if atual and (len(atual) >= max_pal or sum(len(a[0]) + 1 for a in atual) + len(texto) > max_car or w["inicio"] - atual[-1][2] > 0.45):
                grupos.append(atual); atual = []
            atual.append((texto, w["inicio"], w["fim"], w["i"] in destaque))
            if w["texto"][-1] in ",.?!":
                grupos.append(atual); atual = []
        if atual:
            grupos.append(atual)
        for k, g in enumerate(grupos):
            fim = min(g[-1][2] + 0.5, grupos[k + 1][0][1] if k + 1 < len(grupos) else self.dur)
            ps = " ".join(f'<span class="w{" ac" if d else ""}" data-t="{t:.2f}">{esc(x)}</span>' for x, t, _, d in g)
            self.leg.append(f'<div class="grupo" data-fim="{fim:.2f}">{ps}</div>')

    def gerar(self):
        secoes, js, eventos = [], [], []
        for n, c in enumerate(self.cenas):
            d = c["t1"] - c["t0"]
            secoes.append(f'''
      <section id="{c["id"]}" class="cena clip" data-start="{c["t0"]}" data-duration="{d:.2f}" data-track-index="{n}" style="z-index:1">
        <div class="fundo" style="background:{FUNDOS.get(c["fundo"], c["fundo"])}"></div><div class="pontos"></div>
        <div class="bz" id="{c["id"]}-bz"><div class="palco"><div class="mundo" id="{c["id"]}-mundo">
          {"".join(c["itens"])}
        </div></div></div>
      </section>''')
            js.append(f"// ---------- {c['id']} ({c['t0']}–{c['t1']})\n" + c["js"].strip())
            eventos += _coleta_sfx(c["js"])
            if c["sobre"]:
                secoes.append(f'''
      <section id="{c["id"]}f" class="cena clip" data-start="{c["t0"]}" data-duration="{d:.2f}" data-track-index="{60 + n}" style="z-index:7">
        <div class="palco"><div class="mundo" id="{c["id"]}f-mundo">{"".join(c["sobre"])}</div></div>
      </section>''')
                js.append(c["js_sobre"].strip())
                eventos += _coleta_sfx(c["js_sobre"])
        ex_html, ex_js = [], []
        for k, e in enumerate(self.experts):
            l, t = e["cx"] - e["w"] / 2, e["cy"] - e["h"] / 2
            ex_html.append(f'''
      <div id="ex{k}m" class="moldura clip" data-start="{e["t0"]}" data-duration="{e["dur"]}" data-track-index="{40 + 2 * k}" style="left:{l - 14:.0f}px; top:{t - 14:.0f}px; width:{e["w"] + 28}px; height:{e["h"] + 28}px"></div>
      <video id="ex{k}v" class="clip expert" src="{e["arquivo"]}" muted playsinline data-start="{e["t0"]}" data-duration="{e["dur"]}" data-track-index="{41 + 2 * k}"
        style="inset:auto; left:{l:.0f}px; top:{t:.0f}px; width:{e["w"]}px; height:{e["h"]}px"></video>''')
            ex_js.append(f'cartaoVideo(["#ex{k}m", "#ex{k}v"], {e["t0"]}, {e["dur"]}, {k % 2});')
            eventos.append((e["t0"], "bz", ""))
        tpl = open(os.path.join(AQUI, "molde.html"), encoding="utf-8").read()
        kick = f'<div id="kicker"><span class="pt"></span>{esc(self.kicker)}</div>' if self.kicker else ""
        out = (tpl.replace("%%DUR%%", str(self.dur)).replace("%%SECOES%%", "".join(secoes)).replace("%%EXPERT%%", "".join(ex_html))
               .replace("%%KICKER%%", kick).replace("%%LEGENDA%%", "\n          ".join(self.leg)).replace("%%RIG%%", json.dumps(_RIG))
               .replace("%%EXPERTJS%%", "\n        ".join(ex_js)).replace("%%CENAS%%", "\n\n        ".join(js)))
        open(os.path.join(self.proj, "index.html"), "w", encoding="utf-8").write(out)
        # efeitos sonoros: um por evento, sem empilhar (mínimo 0,12 s entre efeitos)
        sfx, ult = [], -9
        for t, tipo, _ in sorted(eventos):
            arq, vol = SFX.get(tipo, (None, 0))
            if not arq or t - ult < 0.12:
                continue
            sfx.append({"arquivo": f"sfx/{arq}", "momento": round(t + (0.1 if tipo in ("pop", "carimbo") else 0), 3), "volume": vol, "tipo": tipo})
            ult = t
        os.makedirs(os.path.join(self.proj, "assets", "audio"), exist_ok=True)
        json.dump(sfx, open(os.path.join(self.proj, "assets", "audio", "sfx.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print("ok", len(self.cenas), "cenas,", len(self.leg), "grupos de legenda,", len(sfx), "efeitos sonoros")
