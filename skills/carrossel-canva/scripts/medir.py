#!/usr/bin/env python3
"""Calcula tamanhos e posições do carrossel LEGACY sem medir nada na hora.

Usa as larguras reais das fontes do Canva e a curva do degradê do template
(references/metricas.json). Os comandos de página devolvem o que muda em relação
à página-modelo para o texto que veio: fonte, posição do texto, do degradê e da
foto, e a faixa da imagem que continua visível (onde o sujeito precisa estar).

  python3 scripts/medir.py capa "Linha 1" "Linha 2" "Pergunta"
  python3 scripts/medir.py pag3 "Título do card" "Parágrafo 1" "Parágrafo 2" ...
  python3 scripts/medir.py pag2 "Parágrafo 1" "Parágrafo 2" ...
  python3 scripts/medir.py titulo "Título do card"
  python3 scripts/medir.py corpo "Parágrafo 1" ... [--tam 40] [--larg 974]

Tamanhos em px do design (o que o conector usa; `format_text` só aceita número
inteiro). No painel do Canva o número mostrado é px × 0,75 (campo "ui").
"""
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(AQUI, "..", "references", "metricas.json"), encoding="utf-8") as f:
    M = json.load(f)

CAIXA_CAPA, ALVO_CAPA, BASE_CAPA = 981, 975, 1250
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

def capa(linhas):
    if len(linhas) != 3:
        sys.exit("capa: passe exatamente 3 linhas (branca menor, branca maior, pergunta dourada)")
    res = []
    for t in linhas:
        em = largura_em(t.upper(), "bebas", -0.02)
        ui_val = int(ALVO_CAPA / em * 0.75 * 10) / 10  # arredonda para baixo no passo do Canva
        px = round(ui_val / 0.75, 3)
        res.append({"texto": t, "px": px, "px_inteiro": int(px), "ui": ui_val, "largura": round(em * px)})
    s = [r["px"] for r in res]
    altura = 0.95 * sum(s) + 0.149 * s[0] + 0.088 * s[2]
    top = BASE_CAPA - altura
    tops = [top]  # 3 caixas separadas (uma por linha): mesmo espaçamento da caixa única
    tops.append(tops[0] + 1.099 * s[0] - 0.149 * s[1])
    tops.append(tops[1] + 1.099 * s[1] - 0.149 * s[2])
    enc, ops = encaixe("capa", top)
    return {
        "linhas": res,
        "caixa_unica": {
            "format_text_px": int(min(s)),
            "top": round(top, 1),
            "ajuste_manual_ui": [r["ui"] for r in res],
        },
        "tres_caixas": {"tops": [round(t, 1) for t in tops], "left": 50.64},
        "altura_bloco": round(altura, 1),
        **enc,
        "operacoes": [{"op": "position_element", "elemento": "MANCHETE", "top": round(top, 1), "left": 50.64}] + ops,
        "nota": "círculo em x 590-1022, y 278-711: o sujeito da foto principal fica à esquerda ou no centro",
    }


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


def quebrar(par, px, larg):
    linhas, atual = [], ""
    for w in par.split(" "):
        tent = w if not atual else atual + " " + w
        if largura_em(tent, "poppins_bold") * px * 1.011 <= larg or not atual:  # 1,1%: calibrado com a quebra real do Canva
            atual = tent
        else:
            linhas.append(atual)
            atual = w
    linhas.append(atual)
    return linhas


def corpo(pars, px=40.0, larg=974.0):
    def medir(l):
        ls = [quebrar(p, px, l) for p in pars]
        n = sum(len(x) for x in ls) + (len(pars) - 1)
        orf = [x[-1] for x in ls if len(x) > 1 and " " not in x[-1]]
        return n, orf, ls

    n, orf, ls = medir(larg)
    out = {"linhas": n, "orfas": orf}
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
        "corpo": {"px": px, "linhas": c["linhas"], "orfas": c["orfas"], "largura": l, "top": c_top},
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
        "corpo": {"px": px, "linhas": c["linhas"], "orfas": c["orfas"], "largura": l, "top_calculado": topo},
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
    opts = {"--tam": 40.0, "--larg": 974.0}
    textos = []
    i = 0
    while i < len(args):
        if args[i] in opts:
            opts[args[i]] = float(args[i + 1])
            i += 2
        else:
            textos.append(args[i])
            i += 1
    if cmd == "capa":
        r = capa(textos)
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
