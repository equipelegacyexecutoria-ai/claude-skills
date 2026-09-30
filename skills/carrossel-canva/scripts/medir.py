#!/usr/bin/env python3
"""Calcula tamanhos e posições do carrossel LEGACY sem medir nada na hora.

Usa as larguras reais das fontes do Canva e a curva do degradê do template
(references/metricas.json). Os comandos de página devolvem o que muda em relação
à página-modelo para o texto que veio: fonte, posição do texto, do degradê e da
foto, e a faixa da imagem que continua visível (onde o sujeito precisa estar).

  python3 scripts/medir.py manchete "Manchete inteira" "Pergunta" [--circulo esquerda]
  python3 scripts/medir.py capa "Linha 1" "Linha 2" "Pergunta" [--circulo esquerda]
  python3 scripts/medir.py pag3 "Título do card" "Parágrafo 1" "Parágrafo 2" ...
  python3 scripts/medir.py pag2 "Parágrafo 1" "Parágrafo 2" ...
  python3 scripts/medir.py titulo "Título do card"
  python3 scripts/medir.py corpo "Parágrafo 1" ... [--tam 40] [--larg 974]

Tamanhos em px do design (o que o conector usa; `format_text` só aceita número
inteiro). No painel do Canva o número mostrado é px × 0,75 (campo "ui").
"""
import json
import re
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(AQUI, "..", "references", "metricas.json"), encoding="utf-8") as f:
    M = json.load(f)

CAIXA_CAPA, ALVO_CAPA, BASE_CAPA = 981, 975, 1250
# Capa aprovada em 28/09/2026 (DAHWgdFSrXw): círculo de 462 px a y 330. Desde 29/09/2026 o logo
# da Legacy (versão do aniversário, com confete) já vem no template como um GRUPO 127,9×124,1
# (logo + confete): só se reposiciona, com o topo 150 px acima do topo da H1 (medido na capa das
# Bets e no template do usuário).
CIRC_LADO, CIRC_TOP = 462.15, 330.14
LOGO_LEFT, LOGO_ACIMA, LOGO_H = 476.97, 160.0, 119.65  # logo do template LEGACY de 30/09/2026
ESC, H_FADE = M["degrade"]["escuro"], M["degrade"]["altura_img"]

# Páginas-modelo LEGACY, lidas no template em 2026-09-27: (top, left, altura) da foto e do
# retângulo do degradê; "ib" = topo e altura da imagem FADE dentro do retângulo; "ref" =
# escuridão do degradê no topo do texto. Cards: a mesma do título na pág. 3 do template
# (~0,77, calculada abaixo); capa: 0,70 (a manchete só sobe o degradê se começar acima de y~960).
PAG = {
    "capa": {"foto": (-10.0, -10.8, 1142.42), "degrade": (386.8, -51.39, 747.62),
             "ib": (-467.71, 1447.38), "ref": 0.70},
    "pag2": {"foto": (-17.47, -14.3, 1210.46), "degrade": (472.23, -13.19, 769.05),
             "ib": (-608.4, 1433.93), "ref": None},
    "pag3": {"foto": (-17.47, -14.3, 942.88), "degrade": (333.65, 0.0, 813.45),
             "ib": (-620.47, 1433.93), "ref": None},
}
TITULO_TOP, CORPO_TOP, CORPO_BASE, TOPO_MINIMO = 776.6, 884.6, 1317.0, 350.0
PAG2_BASE = 1290.3
FOTO_MINIMA = 250  # foto visível (escuro < 50%) até menos que isso: card fica só com texto


def largura_em(texto, fonte, espaco=0.0):
    tab = M[fonte]
    padrao = 400 if fonte == "bebas" else 600
    total = sum(tab.get(c, 1200 if ord(c) > 0x2FFF else padrao) for c in texto)
    return total / 1000 + espaco * len(texto)


def ui(px):
    return round(px * 0.75, 1)


# ---------- degradê e foto ----------

def linha_do_escuro(d):
    """Linha da imagem FADE (0 a 1350) em que a escuridão chega a d."""
    n = len(ESC)
    for i in range(1, n):
        if ESC[i] >= d:
            a, b = ESC[i - 1], ESC[i]
            f = (d - a) / (b - a) if b > a else 0.0
            return (i - 1 + f) * H_FADE / (n - 1)
    return float(H_FADE)


def y_do_escuro(p, g_top, d):
    ib_top, ib_h = PAG[p]["ib"]
    return g_top + ib_top + linha_do_escuro(d) * ib_h / H_FADE


def escuro_em(p, g_top, y):
    """Escuridão do degradê na altura y da página."""
    ib_top, ib_h = PAG[p]["ib"]
    i = (y - g_top - ib_top) * H_FADE / ib_h * (len(ESC) - 1) / H_FADE
    if i <= 0:
        return ESC[0]
    if i >= len(ESC) - 1:
        return ESC[-1]
    a = int(i)
    return ESC[a] + (ESC[a + 1] - ESC[a]) * (i - a)


REF_CARD = escuro_em("pag3", PAG["pag3"]["degrade"][0], TITULO_TOP)
PAG["pag2"]["ref"] = PAG["pag3"]["ref"] = REF_CARD


def encaixe(p, topo_texto):
    """Sobe o degradê (e a foto, se preciso) para o texto que começa em topo_texto."""
    g0, gl, gh = PAG[p]["degrade"]
    f0, fl, fh = PAG[p]["foto"]
    g = min(g0, topo_texto - y_do_escuro(p, 0.0, PAG[p]["ref"]))
    if g0 - g < 3:
        g = g0
    f = f0 - max(0.0, (f0 + fh) - (g + gh))  # a foto nunca passa do fim do degradê
    if f0 - f < 1:
        f = f0
    y50 = y_do_escuro(p, g, 0.5)
    if y50 < FOTO_MINIMA:  # texto ocupa o card quase todo: a foto não apareceria
        return {"foto_util": False, "foto_visivel_ate_y": round(y50), "sujeito_entre_pct": None}, [
            {"op": "delete_element", "elemento": "FOTO"}]
    ini = max(0.0, -f) / fh
    fim = (y50 - f) / fh
    res = {
        "foto_util": True,
        "degrade_top": round(g, 1),
        "foto_top": round(f, 1),
        "foto_visivel_ate_y": round(y50),
        "sujeito_entre_pct": [round(100 * ini), round(100 * fim)],
    }
    ops = []
    if g != g0:
        ops.append({"op": "position_element", "elemento": "DEGRADE", "top": round(g, 1), "left": gl})
    if f != f0:
        ops.append({"op": "position_element", "elemento": "FOTO", "top": round(f, 1), "left": fl})
    return res, ops


# ---------- textos ----------

def dividir_manchete(texto):
    """Quebra a manchete em H1 + H2 onde a menor das duas linhas fica com a maior fonte.

    Aprovado em 28/09/2026 ("O Brasil vive a maior onda de / empresas quebrando da sua
    história"): as duas linhas brancas grandes, nenhuma miúda. Vírgula no fim da H1 ganha
    um bônus pequeno (quebra natural). Manchete com duas frases ("… do país. Hoje quase…")
    ou com "|" marcando a quebra: quebra ali, sem calcular."""
    if "|" in texto:
        a, b = texto.split("|", 1)
        return [a.strip(), b.strip()]
    fim = re.search(r"[.!?]\s+(?=\S+\s+\S)", texto)
    if fim and len(texto[:fim.start()].split()) >= 2:
        return [texto[:fim.end()].strip(), texto[fim.end():].strip()]
    p = texto.split()
    melhor = None
    for i in range(2, len(p) - 1):  # cada linha com pelo menos 2 palavras
        a, b = " ".join(p[:i]), " ".join(p[i:])
        pa = ALVO_CAPA / largura_em(a.upper(), "bebas", -0.02)
        pb = ALVO_CAPA / largura_em(b.upper(), "bebas", -0.02)
        nota = min(pa, pb) + (6 if a.endswith(",") else 0)
        if melhor is None or nota > melhor[0]:
            melhor = (nota, a, b)
    return [melhor[1], melhor[2]] if melhor else [texto, ""]


def capa(linhas, circulo="direita"):
    if len(linhas) != 3:
        sys.exit("capa: passe exatamente 3 linhas (branca, branca, pergunta dourada)")
    res = []
    for t in linhas:
        em = largura_em(t.upper(), "bebas", -0.02)
        px = int(ALVO_CAPA / em)  # format_text só aceita inteiro: para baixo, a linha nunca quebra
        res.append({"texto": t, "px": px, "ui": ui(px), "largura": round(em * px)})
    s = [r["px"] for r in res]
    altura = 0.95 * sum(s) + 0.149 * s[0] + 0.088 * s[2]
    top = BASE_CAPA - altura
    # H1, H2 e H3 são 3 caixas (uma por linha) com o mesmo espaçamento de uma caixa só com lh 0.95
    tops = [top]
    tops.append(tops[0] + 1.099 * s[0] - 0.149 * s[1])
    tops.append(tops[1] + 1.099 * s[1] - 0.149 * s[2])
    enc, ops = encaixe("capa", top)
    manchete = []
    for nome, px, t in zip(("H1", "H2", "H3"), s, tops):
        manchete.append({"op": "format_text", "elemento": nome, "font_size": px})
        manchete.append({"op": "position_element", "elemento": nome, "top": round(t, 1), "left": 50.64})
    # Logo Legacy (grupo logo + confete) centralizado logo acima da H1; círculo de 462 px do lado
    # oposto ao sujeito / ponto de fuga da foto principal, sempre acima do logo.
    logo_top = tops[0] - LOGO_ACIMA
    c_top = min(CIRC_TOP, logo_top - 12 - CIRC_LADO)
    c_left = 50.64 if circulo == "esquerda" else round(1080 - 50.64 - CIRC_LADO, 2)
    extras = [
        {"op": "resize_element", "elemento": "CIRCULO", "width": CIRC_LADO, "height": CIRC_LADO},
        {"op": "position_element", "elemento": "CIRCULO", "top": round(c_top, 1), "left": c_left},
        {"op": "position_element", "elemento": "LOGO", "top": round(logo_top, 1), "left": LOGO_LEFT,
         "nota": "LOGO = o grupo (logo + confete) que já vem na capa do template"},
    ]
    out = {
        "linhas": res,
        "altura_bloco": round(altura, 1),
        **enc,
        "circulo": {"lado": circulo, "x": [c_left, round(c_left + CIRC_LADO)], "y": [round(c_top), round(c_top + CIRC_LADO)]},
        "operacoes": manchete + extras + ops,
        "nota": "sujeito / ponto de fuga da foto principal do lado oposto ao círculo; nada importante atrás do logo",
    }
    if c_top < 150:
        out["aviso"] = "manchete alta demais (linha curta = fonte enorme): círculo e logo apertados; conferir na miniatura"
    return out


def titulo(texto, px=80.0355, caixa=931):
    texto = texto.replace("\n", " ")
    em = largura_em(texto.upper(), "bebas")
    larg = em * px
    out = {"largura": round(larg), "linhas": 1 if larg <= caixa - 6 else 2}
    if out["linhas"] == 1:
        out["altura"] = 96
        return out
    palavras = texto.split(" ")
    w = lambda t: largura_em(t.upper(), "bebas") * px
    melhor = None
    for i in range(1, len(palavras)):
        a, b = " ".join(palavras[:i]), " ".join(palavras[i:])
        wa, wb = w(a), w(b)
        if max(wa, wb) > caixa - 6:
            continue
        nota = abs(wa - wb) - (200 if a.endswith(",") else 0)
        if melhor is None or nota < melhor[0]:
            melhor = (nota, a + "\n" + b)
    if melhor is None:  # nem em 2 linhas: 3 linhas equilibradas
        out["linhas"] = 3
        for i in range(1, len(palavras) - 1):
            for j in range(i + 1, len(palavras)):
                partes = [" ".join(palavras[:i]), " ".join(palavras[i:j]), " ".join(palavras[j:])]
                ws = [w(x) for x in partes]
                if max(ws) > caixa - 6:
                    continue
                nota = max(ws) - min(ws)
                if melhor is None or nota < melhor[0]:
                    melhor = (nota, "\n".join(partes))
    out["quebra"] = melhor[1] if melhor else None
    out["altura"] = 96 + 80 * (out["linhas"] - 1)
    return out


NBSP = " "
# Palavras de ligação que não podem ficar no fim da linha (regra do usuário, 30/09/2026).
CONECTORES = set("e a o as os à às ao aos de do da dos das em no na nos nas um uma uns umas que para pra por "
                 "pelo pela pelos pelas com sem ou se mas nem ele ela eles elas seu sua seus suas meu minha "
                 "é como quando onde porque".split())


def _quebrar(par, px, larg):
    linhas, atual = [], ""
    for w in par.split(" "):
        tent = w if not atual else atual + " " + w
        if largura_em(tent.replace(NBSP, " "), "poppins_bold") * px * 1.011 <= larg or not atual:  # 1,1%: calibrado com a quebra real do Canva
            atual = tent
        else:
            linhas.append(atual)
            atual = w
    linhas.append(atual)
    return linhas


def colar_conectores(par, px=None, larg=None):
    """Devolve o parágrafo com espaço inseparável depois de CADA conector: ele nunca fica no fim da
    linha, quebre o Canva onde quebrar (a previsão do script erra 1 palavra às vezes; colar só onde
    o script previa a quebra deixou "um" e "de" no fim da linha em 30/09/2026).
    Não muda o texto, só a quebra."""
    palavras = par.split(" ")
    out = ""
    for i, w in enumerate(palavras):
        out += w
        if i < len(palavras) - 1:
            out += NBSP if w.replace(NBSP, " ").split(" ")[-1].lower() in CONECTORES else " "
    return out


def quebrar(par, px, larg):
    return _quebrar(colar_conectores(par, px, larg), px, larg)


def corpo(pars, px=40.0, larg=974.0):
    def medir(l):
        ls = [quebrar(p, px, l) for p in pars]
        n = sum(len(x) for x in ls) + (len(pars) - 1)
        orf = [x[-1] for x in ls if len(x) > 1 and " " not in x[-1].replace(NBSP, " ")]
        return n, orf, ls

    n, orf, ls = medir(larg)
    out = {"linhas": n, "orfas": orf, "pars": [colar_conectores(p, px, larg) for p in pars]}
    if orf:
        for l in (960, 945, 930, 920, 900, 880, 860, 850):
            n2, o2, _ = medir(l)
            if not o2 and n2 <= n:
                out["sugestao_largura"] = l
                break
    altura = 1.175 * px + (n - 1) * 1.375 * px
    out["altura"] = round(altura, 1)
    out["corpo_top_pag3"] = CORPO_TOP if CORPO_TOP + altura <= CORPO_BASE else round(CORPO_BASE - altura, 1)
    out["linhas_texto"] = [l for x in ls for l in x]
    return out


def pag3(titulo_txt, pars, larg=974.0):
    """Card com título (pág. 3): título Bebas 80 + corpo Poppins 40 (36 se não couber)."""
    t = titulo(titulo_txt)
    for px in (40.0, 36.0):
        c = corpo(pars, px, larg)
        l = c.get("sugestao_largura", larg)
        if l != larg:
            c = corpo(pars, px, l)
        c_top = c["corpo_top_pag3"]
        t_top = round(c_top - 12 - t["altura"], 1)
        if t_top >= TOPO_MINIMO:
            break
    enc, ops_enc = encaixe("pag3", t_top)
    ops = []
    if t_top != TITULO_TOP:
        ops.append({"op": "position_element", "elemento": "TITULO", "top": t_top, "left": 64.22})
    if px != 40.0:
        ops.append({"op": "format_text", "elemento": "CORPO", "font_size": int(px)})
    if l != larg:
        ops.append({"op": "resize_element", "elemento": "CORPO", "width": l})
    if c_top != CORPO_TOP:
        ops.append({"op": "position_element", "elemento": "CORPO", "top": c_top, "left": 68.22})
    out = {
        "titulo": {"texto": t.get("quebra") or titulo_txt, "linhas": t["linhas"], "top": t_top},
        "corpo": {"px": px, "linhas": c["linhas"], "orfas": c["orfas"], "largura": l, "top": c_top,
                  "pars": c["pars"], "linhas_texto": c["linhas_texto"]},
        **enc,
        "operacoes": ops + ops_enc,
    }
    avisos = []
    if t_top < TOPO_MINIMO:
        avisos.append("card muito longo: mesmo com o corpo em 36 px o título passa do limite")
    if not enc["foto_util"]:
        avisos.append("texto ocupa o card: sem foto (não buscar imagem; a foto de exemplo é apagada)")
    if avisos:
        out["aviso"] = "; ".join(avisos) + ". Contar na entrega."
    return out


def pag2(pars, larg=974.0):
    """Corpo simples (pág. 2): ancorado embaixo; 53 px até 6 linhas, 44 até 9, 40 acima."""
    c = corpo(pars, 53.333, larg)
    px = 53.333
    if c["linhas"] > 6:
        px = 44.0 if c["linhas"] <= 9 else 40.0
        c = corpo(pars, px, larg)
    l = c.get("sugestao_largura", larg)
    if l != larg:
        c = corpo(pars, px, l)
    topo = round(PAG2_BASE - c["altura"], 1)
    enc, ops_enc = encaixe("pag2", topo)
    ops = [{"op": "format_text", "elemento": "CORPO", "font_size": int(px)}] if px != 53.333 else []
    if l != larg:
        ops.append({"op": "resize_element", "elemento": "CORPO", "width": l})
    out = {
        "corpo": {"px": px, "linhas": c["linhas"], "orfas": c["orfas"], "largura": l, "top_calculado": topo,
                  "pars": c["pars"], "linhas_texto": c["linhas_texto"]},
        **enc,
        "operacoes": ops + ops_enc,
    }
    if not enc["foto_util"]:
        out["aviso"] = "texto ocupa o card: sem foto (não buscar imagem; a foto de exemplo é apagada). Contar na entrega."
    return out


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd, args = sys.argv[1], sys.argv[2:]
    opts = {"--tam": 40.0, "--larg": 974.0, "--circulo": "direita"}
    textos = []
    i = 0
    while i < len(args):
        if args[i] in opts:
            opts[args[i]] = args[i + 1] if args[i] == "--circulo" else float(args[i + 1])
            i += 2
        else:
            textos.append(args[i])
            i += 1
    if cmd == "manchete":
        h1, h2 = dividir_manchete(textos[0])
        r = capa([h1, h2, textos[1]], opts["--circulo"])
    elif cmd == "capa":
        r = capa(textos, opts["--circulo"])
    elif cmd == "pag3":
        r = pag3(textos[0], textos[1:], opts["--larg"])
    elif cmd == "pag2":
        r = pag2(textos, opts["--larg"])
    elif cmd == "titulo":
        r = titulo(" ".join(textos))
    elif cmd == "corpo":
        r = corpo(textos, opts["--tam"], opts["--larg"])
    else:
        sys.exit(__doc__)
    print(json.dumps(r, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
