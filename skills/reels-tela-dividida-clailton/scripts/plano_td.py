"""Plano visual (plano.txt, escrito pelo orquestrador) -> linha do tempo (timeline.json).

O orquestrador só escreve as decisões de imagem; o resto sai por regra (medida nos reels da equipe):
cortes no início da palavra, legenda em telas de 1-4 palavras, aberto/fechado do Clailton,
tarja na abertura, flash na saída da abertura, CTA.

Sintaxe do plano.txt (uma decisão por linha; # comenta; @a-b = índices de palavras_legenda.txt):
  ABERTURA @0-18                          tela dividida do quadro 0 até a palavra 18 (inclusive)
  ETIQUETA vermelha "TEXTO DA ETIQUETA"   opcional: etiqueta fixa na emenda (senão a legenda vira tarja preta)
  TOPO @0 foto "busca" | en: english description        imagem de cima na abertura, a partir da palavra 0
  @40-47 foto "busca" | en: ...           imagem em tela cheia (padrão)
  @48-55 dividida filme "busca no YouTube" | en: ...     imagem em cima, Clailton embaixo
  @56-60 cartao print "busca ou url=..."  cartão sobre fundo claro (print, notícia, documento, logo)
  @61-63 ia "prompt" | en: ...            ilustração gerada (arquivo em midia/<id>.png) ou, sem ela, busca
  @64-66 arquivo "C:\\caminho\\foto.jpg"
  opções depois do |: en: <descrição em inglês para o ranking>  url=<link>  t=<segundo no vídeo>
                      foco=<0..1 horizontal>  zoom=out|in|0
  FECHADO @90-93 / ABERTO @94-99          força o enquadramento do Clailton nesse trecho
  NUMERO @120-121 "0,07%"                 número grande sobre o Clailton
  SEMCTA                                  termina sem a CTA
  SEMZOOM                                 desliga o aberto/fechado automático (só o que o plano marcar)
  (padrão)                                zoom seco só nas emendas + zoom animado (keyframes) dentro
                                          do pedaço, olhos sempre na mesma altura (regra do usuário)
  ZOOMLIVRE                               volta ao fechado antigo (punch-in no meio da fala; evitar)

Uso: python plano_td.py <trabalho>   (lê plano.txt, palavras_corte.json, corte.json)
Saída: timeline.json + timeline.txt (resumo para conferir) e avisos.
"""
from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from td_comum import (ABERTO_MAX, FECHADO_MAX, FPS, LEAD, LEG_MAX_CHARS, LEG_MAX_PALAVRAS, PLANO_MIN,  # noqa: E402
                      ZOOM_SUAVE, ZOOM_SUAVE_INTERVALO, ZOOM_SUAVE_RAMPA, gravar_json, ler_json, suave)

TIPOS = {"foto", "filme", "video", "ia", "print", "arquivo"}
LAYOUTS = {"cheia", "dividida", "cartao", "cartão"}
FRACAS = {"DE", "DA", "DO", "DAS", "DOS", "A", "O", "AS", "OS", "E", "QUE", "EM", "NO", "NA", "NOS", "NAS", "UM",
          "UMA", "PARA", "POR", "COM", "SE", "SEM", "AO", "À", "AOS", "MAIS", "MEU", "MINHA", "TEU", "TUA", "SEU",
          "SUA", "NÃO", "MAS", "OU", "COMO", "QUANDO", "ESSE", "ESSA", "ESTE", "ESTA", "ISSO", "PELO", "PELA", "ATÉ",
          "É", "PORQUE", "NEM", "JÁ", "SÓ", "AQUELA", "AQUELE", "NESSE", "NESSA", "DESSE", "DESSA"}
TROCAS = {"TÔ": "ESTOU", "TÁ": "ESTÁ", "TAVA": "ESTAVA", "TAVAM": "ESTAVAM", "PRA": "PARA", "PRO": "PARA O",
          "PROS": "PARA OS", "PRAS": "PARA AS", "CÊ": "VOCÊ", "OCÊ": "VOCÊ", "TAMO": "ESTAMOS", "TÃO": "TÃO"}
CENSURA = {"ESTUPRO": "EST*PRO", "ESTUPRAR": "EST*PRAR", "ESTUPRADOR": "EST*PRADOR", "SUICÍDIO": "SUIC*DIO",
           "SUICIDA": "SUIC*DA", "PEDOFILIA": "PED*FILIA", "PEDÓFILO": "PED*FILO", "COCAÍNA": "COC**NA",
           "ASSASSINATO": "ASSASS*NATO"}
PUNCH_MAX_PALAVRAS = 6
PUNCH_MIN, PUNCH_MAX = 0.6, 2.8      # s: fechado em frase curta de fecho
FECHADO_MAX_FRACAO = 0.40
PAUSA_FRASE = 0.15
# tempo mínimo na tela (pedido do usuário, 27/09/2026: "pareceu que piscou"). Exceção só marcada no plano.
MIN_IMAGEM = 1.0      # s: nenhuma imagem/cena fica menos que isso
MIN_RAPIDO = 0.6      # s: exceção marcada com "rapido" na linha (lista em sequência rápida)
MIN_CLAILTON = 1.0    # s: Clailton entre duas imagens; menos que isso a imagem de antes emenda na próxima
MIN_LASCA = 0.5       # s: sobra do Clailton entre a imagem e uma emenda de tomada é engolida pela imagem


def q(t: float) -> int:
    return int(round(t * FPS))


def sem_acento(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def texto_legenda(palavra: str) -> str:
    """Português escrito em caixa-alta; tira pontuação menos ? e !; censura palavra sensível."""
    t = palavra.strip().upper()
    t = re.sub(r"[.,;:…\"“”()]", "", t)
    t = t.replace("--", "").strip("-")
    base = t.rstrip("?!")
    fim = t[len(base):]
    base = TROCAS.get(base, base)
    base = CENSURA.get(base, base)
    return base + fim[:1]


def fim_de_frase(palavra: str) -> bool:
    return bool(re.search(r"[.?!…]$", palavra.strip()))


def quebra(palavra: str) -> bool:
    return bool(re.search(r"[.,;:?!…]$", palavra.strip()))


# ------------------------------------------------------------------ leitura do plano
def ler_plano(p: Path) -> dict:
    pl = {"abertura": None, "etiqueta": None, "topo": [], "itens": [], "forca": [], "numeros": [], "cta": True,
          "auto_zoom": True, "zoom_corte": True, "avisos": []}
    for n, bruto in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        linha = bruto.split(" #")[0].strip() if not bruto.strip().startswith("#") else ""
        if not linha:
            continue
        up = linha.upper()
        faixa = re.search(r"@(\d+)(?:\s*-\s*(\d+))?", linha)
        a = int(faixa.group(1)) if faixa else None
        b = int(faixa.group(2)) if faixa and faixa.group(2) else a
        aspas = re.search(r"[\"“](.+?)[\"”]", linha)
        if up.startswith("SEMCTA"):
            pl["cta"] = False
        elif up.startswith("SEMZOOM"):
            pl["auto_zoom"] = False
        elif up.startswith("ZOOMCORTE"):                 # já é o padrão (planos antigos da ES trazem a linha)
            pl["zoom_corte"] = True
        elif up.startswith("ZOOMLIVRE"):
            pl["zoom_corte"] = False
        elif up.startswith("SEMABERTURA"):
            pl["sem_abertura"] = True
        elif up.startswith("ESTILO"):
            m_ = re.search(r"([\d.,]+)", linha)
            pl["estilo"] = float(m_.group(1).replace(",", ".")) if m_ else 1.0
        elif up.startswith("ABERTURA"):
            pl["abertura"] = {"i0": a or 0, "i1": b}
        elif up.startswith("ETIQUETA"):
            cor = re.search(r"\b(vermelha|azul|branca|preta)\b", linha, re.I)
            pl["etiqueta"] = {"texto": aspas.group(1).upper() if aspas else "", "cor": (cor.group(1).lower() if cor else "vermelha")}
        elif up.startswith("FECHADO") or up.startswith("ABERTO"):
            pl["forca"].append({"zoom": "fechado" if up.startswith("FECHADO") else "aberto", "i0": a, "i1": b})
        elif up.startswith("NUMERO") or up.startswith("NÚMERO"):
            pl["numeros"].append({"i0": a, "i1": b, "texto": aspas.group(1) if aspas else ""})
        elif up.startswith("TOPO") or linha.startswith("@"):
            it = item(linha, a, b, n)
            if up.startswith("TOPO"):
                it["layout"] = "topo"
                pl["topo"].append(it)
            else:
                pl["itens"].append(it)
        else:
            pl["avisos"].append(f"linha {n} ignorada: {linha[:60]}")
    return pl


def item(linha: str, a: int, b: int, n: int) -> dict:
    corpo, _, opc = linha.partition("|")
    pal = corpo.lower().split()
    tipo = next((w for w in pal if w in TIPOS), "foto")
    layout = next((w for w in pal if w in LAYOUTS), "cheia").replace("cartão", "cartao")
    aspas = re.search(r"[\"“](.+?)[\"”]", corpo)
    it = {"linha": n, "i0": a, "i1": b, "tipo": tipo, "layout": layout, "busca": aspas.group(1) if aspas else "",
          "en": None, "url": None, "t": None, "foco": None, "zoom": None, "nome": None, "igual": None,
          "rapido": bool(re.search(r"(?<![\w=])r[aá]pido\b", opc or corpo, re.I))}
    m = re.search(r"\bigual\s+([\w-]+)", corpo)
    if m:                                        # repete a mídia de outro item (id ou nome)
        it["tipo"], it["igual"] = "igual", m.group(1)
    m = re.search(r"en:\s*(.+?)(?=\s+(?:url=|t=|foco=|zoom=|id=|r[aá]pido\b)|$)", opc)
    if m:
        it["en"] = m.group(1).strip()
    for chave in ("url", "t", "foco", "zoom", "id"):
        m = re.search(rf"(?<![\w/]){chave}=(\S+)", linha)
        if m:
            v = m.group(1)
            it["nome" if chave == "id" else chave] = float(v) if chave in ("t", "foco") else v
    if tipo == "arquivo" and it["busca"]:
        it["arquivo"] = it["busca"]
    return it


# ------------------------------------------------------------------ linha do tempo
def montar(T: Path) -> dict:
    pal = ler_json(T / "palavras_corte.json")["palavras"]
    corte = ler_json(T / "corte.json")
    pl = ler_plano(T / "plano.txt")
    avisos = list(pl["avisos"])
    N = len(pal)
    # quadros de cada segmento (acumulado exato, igual ao render da novela)
    seg_f0, acc = [], 0
    for s in corte["segmentos"]:
        seg_f0.append(acc)
        acc += s["frames"]
    F_FALA = acc
    ini = [max(0, q(w["inicio"] - LEAD)) for w in pal]
    for k in range(1, N):                       # monotônico
        ini[k] = max(ini[k], ini[k - 1] + 1)
    # corte a até 6 quadros de uma emenda de tomada vai para a emenda (sem plano de 1-5 quadros)
    for k in range(N):
        perto = [s for s in seg_f0 if abs(s - ini[k]) <= 6]
        if perto:
            ini[k] = perto[0]
    for k in range(1, N):
        ini[k] = max(ini[k], ini[k - 1])

    def f_ini(i: int) -> int:
        return F_FALA if i >= N else ini[max(0, i)]

    def fim_item(i1: int) -> int:
        return f_ini(i1 + 1)

    def txt(i0: int, i1: int) -> str:
        return " ".join(w["texto"] for w in pal[i0:i1 + 1])

    # ---------------- abertura
    ab = pl["abertura"]
    if pl.get("sem_abertura"):                  # edição simples: começa direto no Clailton em tela cheia
        ab = {"i0": 0, "i1": -1}
        pl["topo"] = []
    elif ab is None:                            # padrão: 1ª frase (até ~6 s)
        i1 = 0
        while i1 < N - 1 and not fim_de_frase(pal[i1]["texto"]) and pal[i1 + 1]["inicio"] < 6.0:
            i1 += 1
        ab = {"i0": 0, "i1": i1}
        avisos.append(f"ABERTURA não definida: usei @0-{i1} ({txt(0, i1)[:50]})")
    ab_f1 = fim_item(ab["i1"]) if ab["i1"] >= 0 else 0
    topo = sorted(pl["topo"], key=lambda x: x["i0"])
    if not topo and ab_f1 > 0:
        avisos.append("abertura sem TOPO: a tela dividida precisa de imagem em cima")
    camadas = []
    for k, it in enumerate(topo):
        f0 = 0 if k == 0 else f_ini(it["i0"])
        f1 = f_ini(topo[k + 1]["i0"]) if k + 1 < len(topo) else ab_f1
        if f1 - f0 < 6:
            avisos.append(f"TOPO @{it['i0']} dura só {f1 - f0} quadros")
        i_fim = topo[k + 1]["i0"] - 1 if k + 1 < len(topo) else ab["i1"]
        camadas.append({**it, "id": f"t{k + 1:02d}", "f0": f0, "f1": f1, "i1": i_fim, "texto": txt(it["i0"], i_fim)})

    # ---------------- imagens do corpo
    itens = sorted(pl["itens"], key=lambda x: x["i0"])
    for k, it in enumerate(itens):
        f0, f1 = f_ini(it["i0"]), fim_item(it["i1"])
        if f0 < ab_f1:
            avisos.append(f"@{it['i0']}-{it['i1']} começa dentro da abertura: empurrado para o fim dela")
            f0 = ab_f1
        if k + 1 < len(itens) and f1 > f_ini(itens[k + 1]["i0"]):
            f1 = f_ini(itens[k + 1]["i0"])
            avisos.append(f"@{it['i0']}-{it['i1']} sobrepõe o próximo: encurtado")
        d = (f1 - f0) / FPS
        if it["layout"] == "cheia" and d > 5.0:
            avisos.append(f"@{it['i0']}-{it['i1']} {d:.1f}s em tela cheia: divida em 2 imagens ou use 'dividida'")
        camadas.append({**it, "id": f"b{k + 1:02d}", "f0": f0, "f1": f1, "texto": txt(it["i0"], it["i1"])})
    camadas = [c for c in camadas if c["f1"] > c["f0"]]
    nomes = {c["nome"]: c["id"] for c in camadas if c.get("nome")}
    for c in camadas:                            # 'igual X' aponta para o id do item X
        if c["tipo"] == "igual":
            alvo = nomes.get(c["igual"], c["igual"])
            orig = next((o for o in camadas if o["id"] == alvo and o["tipo"] != "igual"), None)
            if orig is None:
                avisos.append(f"{c['id']}: 'igual {c['igual']}' não encontrado")
                c["tipo"] = "foto"
            else:
                c["igual"] = alvo
                c["en"] = c["en"] or orig.get("en")
                c["busca"] = c["busca"] or orig.get("busca")
    impor_minimos(camadas, ab_f1, F_FALA, seg_f0, avisos)
    for c in camadas:
        if c["id"].startswith("t") and (c["f1"] - c["f0"]) / FPS < MIN_IMAGEM:
            avisos.append(f"{c['id']} (TOPO) fica só {(c['f1'] - c['f0']) / FPS:.2f}s: junte com o TOPO vizinho")

    # ---------------- visibilidade do Clailton por quadro
    # estado: 'dividida' (abertura / item dividida) | 'cheio' (Clailton em tela cheia) | 'coberto'
    estado = ["cheio"] * F_FALA
    for f in range(0, min(ab_f1, F_FALA)):
        estado[f] = "dividida"
    for c in camadas:
        if c["id"].startswith("t"):
            continue
        for f in range(c["f0"], min(c["f1"], F_FALA)):
            estado[f] = "dividida" if c["layout"] == "dividida" else "coberto"

    # ---------------- aberto/fechado do Clailton
    zoom = ["aberto"] * F_FALA
    forcado = [None] * F_FALA
    for fz in pl["forca"]:
        for f in range(f_ini(fz["i0"]), fim_item(fz["i1"])):
            if 0 <= f < F_FALA:
                forcado[f] = fz["zoom"]
                zoom[f] = fz["zoom"]
    escala = [1.0] * F_FALA                      # zoom animado (ZOOMCORTE): escala sobre o aberto
    if pl.get("zoom_corte"):
        escala = auto_zoom_cortes(pal, F_FALA, estado, zoom, forcado, seg_f0, corte["segmentos"], f_ini, pl["auto_zoom"])
    else:
        if pl["auto_zoom"]:
            auto_fechado(pal, ini, F_FALA, estado, zoom, forcado, seg_f0, f_ini)
        limpar_zoom(zoom, forcado, seg_f0, F_FALA)
    for f in range(F_FALA):
        if estado[f] == "dividida":
            zoom[f] = "dividida"
            escala[f] = 1.0

    # ---------------- planos do Clailton (cortes: segmento, zoom, visibilidade)
    seg_de = [0] * F_FALA
    for k, f0 in enumerate(seg_f0):
        fim = seg_f0[k + 1] if k + 1 < len(seg_f0) else F_FALA
        for f in range(f0, fim):
            seg_de[f] = k
    planos = []
    f0 = 0
    for f in range(1, F_FALA + 1):
        if f == F_FALA or seg_de[f] != seg_de[f0] or zoom[f] != zoom[f0] or (estado[f] == "coberto") != (estado[f0] == "coberto"):
            planos.append({"f0": f0, "f1": f, "seg": seg_de[f0], "zoom": zoom[f0], "visivel": estado[f0] != "coberto"})
            f0 = f
    for p in planos:                            # zoom animado: escala quadro a quadro no plano inteiro
        esc = escala[p["f0"]:p["f1"]]
        if p["zoom"] == "aberto" and max(esc) > 1.0005:
            p["escala"] = [round(v, 4) for v in esc]

    # ---------------- legenda
    quebras_forcadas = {c["i0"] for c in camadas if not c["id"].startswith("t")} | {ab["i1"] + 1}
    quebras_forcadas |= {n["i0"] for n in pl["numeros"]} | {n["i1"] + 1 for n in pl["numeros"]}
    telas = legenda(pal, ini, F_FALA, quebras_forcadas, ab["i1"])
    numeros = []
    for nu in pl["numeros"]:
        numeros.append({"f0": f_ini(nu["i0"]), "f1": fim_item(nu["i1"]), "texto": nu["texto"] or txt(nu["i0"], nu["i1"]).upper()})
        for t in telas:                          # a legenda some enquanto o número está na tela
            if t["i0"] >= nu["i0"] and t["i1"] <= nu["i1"]:
                t["oculta"] = True

    # ---------------- estatística (para o orquestrador conferir o ritmo)
    dur = F_FALA / FPS
    cob = sum(1 for e in estado if e == "coberto") / max(1, F_FALA)
    div = sum(1 for e in estado if e == "dividida") / max(1, F_FALA)
    vis = [p for p in planos if p["visivel"] and p["zoom"] in ("aberto", "fechado")]
    t_fech = sum(p["f1"] - p["f0"] for p in vis if p["zoom"] == "fechado")
    t_vis = sum(p["f1"] - p["f0"] for p in vis) or 1
    n_img = sum(1 for c in camadas if not c["id"].startswith("t"))
    stats = {"duracao_fala": round(dur, 2), "imagem_tela_cheia": round(cob, 3), "dividida": round(div, 3),
             "clailton_cheio": round(1 - cob - div, 3), "fechado_do_clailton": round(t_fech / t_vis, 3),
             "zoom_animado": sum(1 for p in vis if p.get("escala")), "trocas_de_zoom": sum(
                 1 for a_, b_ in zip(vis, vis[1:]) if a_["f1"] == b_["f0"] and a_["zoom"] != b_["zoom"]),
             "imagens": n_img, "imagens_por_min": round(60 * n_img / dur, 1), "telas_legenda": len(telas)}
    if cob > 0.45:
        avisos.append(f"imagem em {cob:.0%} do tempo: o melhor reel tem ~1/3 (o pior tinha 58%)")
    if cob < 0.15 and n_img < 5 and not pl.get("sem_abertura"):
        avisos.append(f"pouca imagem ({cob:.0%}): tela dividida sem imagem rende 0,48x")
    tl = {"fps": FPS, "frames_fala": F_FALA, "cta": pl["cta"], "estilo": pl.get("estilo"), "abertura": {"f0": 0, "f1": ab_f1, "i1": ab["i1"],
          "etiqueta": pl["etiqueta"], "saida": "flash"}, "segmentos_f0": seg_f0, "planos": planos,
          "camadas": camadas, "legendas": telas, "numeros": numeros, "stats": stats, "avisos": avisos}
    return tl


def impor_minimos(camadas: list[dict], ab_f1: int, F_FALA: int, seg_f0: list[int], avisos: list[str]) -> None:
    """Tempo mínimo na tela. Imagem curta cresce: 1) para frente, sobre o Clailton (sem deixar sobra dele
    menor que MIN_CLAILTON); 2) tomando da próxima imagem, se ela tiver sobra; 3) para trás (entra um
    pouco antes da palavra). Clailton espremido entre duas imagens vira emenda direta; lasca do
    Clailton colada numa emenda de tomada (dois cortes em meio segundo) é engolida pela imagem."""
    corpo = sorted([c for c in camadas if not c["id"].startswith("t")], key=lambda c: c["f0"])
    mc = q(MIN_CLAILTON)

    def minimo(c: dict) -> int:
        return q(MIN_RAPIDO if c.get("rapido") else MIN_IMAGEM)

    for k, c in enumerate(corpo):
        falta = minimo(c) - (c["f1"] - c["f0"])
        if falta <= 0:
            continue
        antes = (c["f1"] - c["f0"]) / FPS
        prox = corpo[k + 1]["f0"] if k + 1 < len(corpo) else F_FALA
        folga = prox - c["f1"]
        if folga >= falta + mc:
            c["f1"] += falta
            falta = 0
        elif folga > 0:
            c["f1"] = prox
            falta -= folga
        if falta > 0 and k + 1 < len(corpo) and c["f1"] == corpo[k + 1]["f0"]:
            n = corpo[k + 1]
            d = min(falta, (n["f1"] - n["f0"]) - minimo(n))
            if d > 0:
                c["f1"] += d
                n["f0"] += d
                falta -= d
        if falta > 0:
            ant = corpo[k - 1]["f1"] if k > 0 else ab_f1
            folga = c["f0"] - ant
            if folga >= falta + mc:
                c["f0"] -= falta
                falta = 0
            elif folga > 0:
                c["f0"] = ant
                falta = max(0, falta - folga)
        if falta > 0:
            avisos.append(f"{c['id']} fica só {(c['f1'] - c['f0']) / FPS:.2f}s (mínimo {minimo(c) / FPS:.1f}s): "
                          f"junte com a imagem vizinha ou marque 'rapido'")
        else:
            avisos.append(f"{c['id']}: {antes:.2f}s -> {(c['f1'] - c['f0']) / FPS:.2f}s (tempo mínimo na tela)")
    # Clailton espremido: entre duas imagens, entre a abertura e a 1ª imagem, antes do fim da fala
    for k, c in enumerate(corpo):
        prox = corpo[k + 1]["f0"] if k + 1 < len(corpo) else F_FALA
        if 0 < prox - c["f1"] < mc:
            c["f1"] = prox
    if corpo and 0 < corpo[0]["f0"] - ab_f1 < mc:
        corpo[0]["f0"] = ab_f1
    # lasca do Clailton colada numa emenda de tomada (dois cortes em menos de MIN_LASCA)
    ml = q(MIN_LASCA)
    for k, c in enumerate(corpo):
        prox = corpo[k + 1]["f0"] if k + 1 < len(corpo) else F_FALA
        j = next((j for j in seg_f0[1:] if c["f1"] < j <= min(prox, c["f1"] + ml)), None)
        if j is not None:
            c["f1"] = j
        ant = corpo[k - 1]["f1"] if k > 0 else ab_f1
        j = next((j for j in reversed(seg_f0[1:]) if max(ant, c["f0"] - ml) <= j < c["f0"]), None)
        if j is not None:
            c["f0"] = j


def auto_fechado(pal, ini, F_FALA, estado, zoom, forcado, seg_f0, f_ini) -> None:
    """Fechado (punch-in ~1,5x) como a equipe faz: na frase curta que fecha uma ideia ("a tua.",
    "registre", "e passa a ser sobre você.") — ou no rabo (2-4 últimas palavras) de uma frase longa
    que termina em ponto — e logo depois de emenda de tomada (esconde o pulo). Nunca dois fechados
    seguidos; volta sempre para o aberto; no máximo ~40% do tempo do Clailton em tela cheia."""
    N = len(pal)
    frases = []                                    # (i0, i1) quebradas em pontuação/pausa/tomada
    i0 = 0
    for i in range(N):
        prox_pausa = (pal[i + 1]["inicio"] - pal[i]["fim"]) if i + 1 < N else 9
        if (quebra(pal[i]["texto"]) or prox_pausa >= PAUSA_FRASE or i == N - 1
                or (i + 1 < N and pal[i + 1].get("seg") != pal[i].get("seg"))):
            frases.append((i0, i))
            i0 = i + 1
    juncoes = seg_f0[1:]
    total_vis = sum(1 for e in estado if e == "cheio") or 1
    usados = sum(1 for f in range(F_FALA) if forcado[f] == "fechado")
    gap = q(0.9)

    def livre(f0: int, f1: int) -> bool:
        """Clailton em tela cheia no trecho e 0,9 s de aberto antes; nenhum fechado 0,9 s depois."""
        if f1 <= f0 or f1 > F_FALA or f0 - gap < 0:
            return False
        if any(estado[f] != "cheio" or forcado[f] or zoom[f] == "fechado" for f in range(f0, f1)):
            return False
        return (all(estado[f] == "cheio" and zoom[f] == "aberto" for f in range(f0 - gap, f0))
                and all(zoom[f] != "fechado" for f in range(f1, min(F_FALA, f1 + gap))))

    cands = []                                     # (prioridade, f0, f1)
    for a, b in frases:
        f0, f1 = f_ini(a), f_ini(b + 1)
        d = (f1 - f0) / FPS
        n_pal = b - a + 1
        final = fim_de_frase(pal[b]["texto"])
        if final and n_pal <= PUNCH_MAX_PALAVRAS and PUNCH_MIN <= d <= PUNCH_MAX:
            cands.append((0, f0, f1))              # frase curta de fecho
        elif final and n_pal > 3:
            for k in (3, 2, 4):                    # rabo da frase longa: 2-4 últimas palavras
                s = b - k + 1
                if s <= a:
                    continue
                g0 = f_ini(s)
                if PUNCH_MIN <= (f1 - g0) / FPS <= 2.2 and texto_legenda(pal[s - 1]["texto"]) not in ("DE", "A", "O", "UM", "UMA"):
                    cands.append((1, g0, f1))
                    break
        if any(abs(f0 - j) <= 2 for j in juncoes) and PUNCH_MIN <= d <= PUNCH_MAX:
            cands.append((2, f0, f1))              # logo depois da emenda de tomada
    for _, f0, f1 in sorted(cands):
        if not livre(f0, f1) or (usados + f1 - f0) / total_vis > FECHADO_MAX_FRACAO:
            continue
        for f in range(f0, f1):
            zoom[f] = "fechado"
        usados += f1 - f0


def auto_zoom_cortes(pal, F_FALA, estado, zoom, forcado, seg_f0, segs, f_ini, auto: bool = True) -> list[float]:
    """Zoom padrão (TD e ES) — regras do usuário (28/09/2026, correção do reel "Dirigir uma empresa sem GPS"):
    "o zoom precisa ser entre cortes (zoom seco); se for fazer um zoom que não seja entre cortes,
    precisa ser com keyframes"; "todo zoom mantém a altura dos olhos" (rect_zoom, no render).
    - cada pedaço do corte (entre duas emendas) tem UM zoom: aberto/fechado só troca na emenda;
    - emenda de tomada (trecho novo da decupagem ou pulo >= 1 s no bruto) troca o zoom: esconde o pulo;
    - pedaço que é uma frase curta de fecho ("A rota.", "Pensa comigo.") vai para o fechado;
    - o fechado volta para o aberto na emenda seguinte; aberto por mais de ABERTO_MAX fecha na 1ª
      emenda boa; nenhum plano menor que PLANO_MIN;
    - dentro de pedaço longo que termina em fim de frase: zoom ANIMADO (keyframes, entrada e saída
      suaves) no rabo da frase, segurando até a emenda; só se o pedaço seguinte for aberto.
    Preenche zoom[] e devolve a escala por quadro do zoom animado (1,0 = parado)."""
    b = list(seg_f0) + [F_FALA]
    n = len(seg_f0)
    escala = [1.0] * F_FALA
    dur = [(b[k + 1] - b[k]) / FPS for k in range(n)]
    tomada = [False] + [segs[k]["i0"] != segs[k - 1]["i0"] or segs[k]["src_in"] - segs[k - 1]["src_out"] >= 1.0
                        for k in range(1, n)]
    pal_seg = [[] for _ in range(n)]              # pelo tempo alinhado (o "seg" antigo vinha do Whisper)
    for w in pal:
        f = q(w["inicio"])
        pal_seg[max((k for k in range(n) if b[k] <= f + 1), default=0)].append(w)

    def fecho(k: int) -> bool:
        ws = pal_seg[k]
        return bool(ws) and fim_de_frase(ws[-1]["texto"]) and len(ws) <= PUNCH_MAX_PALAVRAS and PUNCH_MIN <= dur[k] <= PUNCH_MAX

    def forcado_em(k: int):
        fs = [forcado[f] for f in range(b[k], b[k + 1])]
        for z in ("fechado", "aberto"):
            if fs and fs.count(z) >= 0.5 * len(fs):
                return z
        return None

    z, run, t_fech, t_tot = [], 0.0, 0.0, 0.0
    for k in range(n):
        zf = forcado_em(k)
        if zf:
            zk = zf
        elif k == 0 or not auto:
            zk = "aberto"
        else:
            prev = z[-1]
            if dur[k] < PLANO_MIN or run < PLANO_MIN:
                zk = prev                                  # pedaço (ou plano anterior) curto demais: segue
            elif prev == "fechado":
                zk = "aberto"                              # o fechado volta sempre na emenda seguinte
            else:
                folga = (t_fech + dur[k]) / max(1e-6, t_tot + dur[k]) <= 0.5
                quer = tomada[k] or (fecho(k) and run >= 1.5) or (run >= ABERTO_MAX and dur[k] <= FECHADO_MAX)
                zk = "fechado" if quer and (folga or tomada[k]) else "aberto"
        run = run + dur[k] if (z and zk == z[-1]) else dur[k]
        z.append(zk)
        t_tot += dur[k]
        t_fech += dur[k] if zk == "fechado" else 0.0
        for f in range(b[k], b[k + 1]):
            zoom[f] = zk

    # zoom animado (keyframes) dentro do pedaço aberto longo, no rabo da frase que fecha na emenda
    rampa = max(2, int(round(ZOOM_SUAVE_RAMPA * FPS)))
    ult = -1e9
    for k in range(n):
        ws = pal_seg[k]
        if (not auto or z[k] != "aberto" or dur[k] < 3.0 or len(ws) < 6 or not fim_de_frase(ws[-1]["texto"])
                or (k + 1 < n and z[k + 1] != "aberto") or forcado_em(k)):
            continue
        # sem fechado logo depois (zoom animado, volta seca e fechado em 3 s = zoom demais)
        if any(z[j] == "fechado" and b[j] - b[k + 1] < q(3.0) for j in range(k + 1, n)):
            continue
        if any(estado[f] != "cheio" for f in range(b[k], b[k + 1])):
            continue
        g0 = None
        for m in (3, 2, 4):                            # rabo: 2-4 últimas palavras, 0,6-2,2 s até a emenda
            s = len(ws) - m
            if s <= 0:
                continue
            g = f_ini(ws[s]["i"])
            if PUNCH_MIN <= (b[k + 1] - g) / FPS <= 2.2 and texto_legenda(ws[s - 1]["texto"]) not in ("DE", "A", "O", "UM", "UMA"):
                g0 = g
                break
        if g0 is None or g0 / FPS - ult < ZOOM_SUAVE_INTERVALO or b[k + 1] - g0 < rampa + int(0.3 * FPS):
            continue
        for f in range(g0, b[k + 1]):
            escala[f] = 1.0 + (ZOOM_SUAVE - 1.0) * suave((f - g0) / rampa)
        ult = b[k + 1] / FPS
    return escala


def limpar_zoom(zoom, forcado, seg_f0, F_FALA, minimo: int = 6) -> None:
    """Sem plano de zoom menor que `minimo` quadros (pisca); troca de zoom colada numa emenda de
    tomada (até 3 quadros) vai para a emenda."""
    juncoes = set(seg_f0[1:])
    f = 1
    while f < F_FALA:
        if zoom[f] != zoom[f - 1]:
            for j in range(f - 3, f + 4):
                if j in juncoes and j != f and 0 < j < F_FALA:
                    v = zoom[f]
                    rng = range(j, f) if j < f else range(f, j)
                    for g in rng:
                        if not forcado[g]:
                            zoom[g] = v if j < f else zoom[f - 1]
                    break
        f += 1
    # corridas curtas
    f0 = 0
    for f in range(1, F_FALA + 1):
        if f == F_FALA or zoom[f] != zoom[f0]:
            if f - f0 < minimo and f0 > 0 and not any(forcado[g] for g in range(f0, f)):
                for g in range(f0, f):
                    zoom[g] = zoom[f0 - 1]
            f0 = f


def custo_tela(txts: list[str], virgula_fim: bool, virgulas_dentro: int, abertura: bool) -> float:
    """Custo de uma tela de legenda (programação dinâmica): 2-3 palavras, até ~18 letras, quebra na
    vírgula, sem terminar em palavra fraca (de, que, o...), sem palavra fraca sozinha."""
    n = len(txts)
    chars = len(" ".join(txts))
    alvo = 2.0 if abertura else 2.6
    c = (n - alvo) ** 2
    if chars > (16 if abertura else LEG_MAX_CHARS - 2):
        c += (chars - (16 if abertura else LEG_MAX_CHARS - 2)) * 0.8
    base = txts[-1].rstrip("?!")
    if base in FRACAS and not virgula_fim:
        c += 4.0 if n > 1 else 9.0
    if n == 1 and len(base) <= 3:
        c += 3.0
    if virgula_fim:
        c -= 2.5
    c += 2.5 * virgulas_dentro
    return c


def legenda(pal, ini, F_FALA, quebras_forcadas: set, fim_abertura: int) -> list[dict]:
    """Telas de 1-4 palavras por programação dinâmica dentro de cada trecho (quebra obrigatória em
    ponto/interrogação, pausa >= 0,25 s, início de imagem e fim da abertura)."""
    N = len(pal)
    txt = [texto_legenda(w["texto"]) for w in pal]
    trechos, cur = [], []
    for i in range(N):
        if not txt[i]:
            continue
        if cur and (i in quebras_forcadas or fim_de_frase(pal[cur[-1]]["texto"])
                    or pal[i]["inicio"] - pal[cur[-1]]["fim"] >= 0.25 or (cur[0] <= fim_abertura < i)):
            trechos.append(cur)
            cur = []
        cur.append(i)
    if cur:
        trechos.append(cur)
    telas = []
    for tr in trechos:
        n = len(tr)
        ab = tr[-1] <= fim_abertura
        maxp = 3 if ab else LEG_MAX_PALAVRAS
        best = [0.0] + [1e9] * n
        prev = [0] * (n + 1)
        for j in range(1, n + 1):
            for k in range(1, maxp + 1):
                if j - k < 0:
                    break
                grupo = tr[j - k:j]
                ts = [txt[g] for g in grupo]
                if len(" ".join(ts)) > LEG_MAX_CHARS + 4 and k > 1:
                    continue
                dentro = sum(1 for g in grupo[:-1] if quebra(pal[g]["texto"]))
                c = best[j - k] + custo_tela(ts, quebra(pal[grupo[-1]]["texto"]) and j < n, dentro, ab) + 1.5
                if c < best[j]:
                    best[j], prev[j] = c, j - k
        cortes, j = [], n
        while j > 0:
            cortes.append((prev[j], j))
            j = prev[j]
        for a, b in reversed(cortes):
            telas.append(tr[a:b])
    out = []
    for k, grupo in enumerate(telas):
        f0 = ini[grupo[0]]
        f1 = ini[telas[k + 1][0]] if k + 1 < len(telas) else F_FALA
        texto = " ".join(texto_legenda(pal[j]["texto"]) for j in grupo)
        out.append({"i0": grupo[0], "i1": grupo[-1], "f0": f0, "f1": f1, "texto": texto,
                    "estilo": "tarja" if grupo[-1] <= fim_abertura else "normal"})
    return out


def resumo(tl: dict) -> str:
    fps = tl["fps"]
    L = [f"# timeline: {tl['frames_fala'] / fps:.1f}s de fala, CTA {'sim' if tl['cta'] else 'não'}",
         f"# {tl['stats']}", ""]
    ab = tl["abertura"]
    L.append(f"ABERTURA 0.00-{ab['f1'] / fps:.2f}s (até @{ab['i1']})" + (f" etiqueta {ab['etiqueta']}" if ab["etiqueta"] else ""))
    for c in tl["camadas"]:
        L.append(f"{c['id']} {c['f0'] / fps:6.2f}-{c['f1'] / fps:6.2f} ({(c['f1'] - c['f0']) / fps:4.2f}s) {c['layout']:8s} {c['tipo']:7s} "
                 f"\"{c['busca'][:40]}\" | {c['texto'][:60]}")
    L.append("")
    L.append("planos do Clailton visíveis (zoom):")
    L.append("  ".join(f"{p['f0'] / fps:.1f}{'F' if p['zoom'] == 'fechado' else ('D' if p['zoom'] == 'dividida' else ('Z' if p.get('escala') else 'A'))}"
                       for p in tl["planos"] if p["visivel"]) + "   (A aberto, F fechado, Z aberto com zoom animado)")
    L.append("")
    L.append("legenda: " + " / ".join(t["texto"] for t in tl["legendas"][:60]) + (" ..." if len(tl["legendas"]) > 60 else ""))
    if tl["avisos"]:
        L.append("")
        L += ["AVISO: " + a for a in tl["avisos"]]
    return "\n".join(L) + "\n"


def main() -> None:
    T = Path(sys.argv[1])
    tl = montar(T)
    gravar_json(T / "timeline.json", tl)
    r = resumo(tl)
    (T / "timeline.txt").write_text(r, encoding="utf-8")
    print(r)


if __name__ == "__main__":
    main()
