#!/usr/bin/env python3
"""Linha editorial: lista as vagas do periodo e monta o documento + a planilha.

Uso:
  python linha_editorial.py vagas  "<pasta>/dados.json"
      Mostra cada vaga do periodo (data, dia, hora, rede, formato, estilo, pilar) e as
      datas especiais que caem nele. Use a saida para escrever as pautas.

  python linha_editorial.py montar "<pasta>/dados.json"
      Confere o dados.json e gera, na mesma pasta:
        Linha Editorial - <Empresa>.html   (documento para ler, imprimir ou mandar)
        Calendario - <Empresa>.xlsx        (planilha de producao, com status)
        Calendario - <Empresa>.csv         (para importar no Notion ou em agendador)
      No fim imprime ERROS (corrigir todos) e AVISOS (corrigir os que fizerem sentido).

O formato do dados.json esta em references/modelo-dados.md.
"""
import csv
import datetime as dt
import html
import json
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

AQUI = os.path.dirname(os.path.abspath(__file__))
DATAS_JSON = os.path.join(AQUI, "..", "assets", "datas.json")

DIAS = ["seg", "ter", "qua", "qui", "sex", "sab", "dom"]
DIAS_NOME = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]
FUNIL = {
    "descoberta": "Descoberta (atrair quem não conhece)",
    "consideracao": "Consideração (gerar confiança)",
    "decisao": "Decisão (levar à compra)",
    "fidelizacao": "Fidelização (fazer voltar e indicar)",
}
CORES = ["#2563eb", "#e11d48", "#059669", "#d97706", "#7c3aed", "#0891b2", "#be185d"]
TOM = [
    ("humor", "Engraçado", "Sério"),
    ("formalidade", "Formal", "Descontraído"),
    ("respeito", "Respeitoso", "Irreverente"),
    ("entusiasmo", "Entusiasmado", "Direto ao ponto"),
]
SINAIS_IA = [
    "—", "crucial", "fundamental", "potencializar", "potencialize", "jornada",
    "vale ressaltar", "além disso", "em resumo", "não é só", "não é apenas",
    "alavancar", "sinergia", "no mundo de hoje", "cada vez mais", "desbloquear",
    "mergulhar", "mergulhe", "imperdível", "transformador", "revolucionário",
]
FONTES = [
    ("Content Marketing Institute / Joe Pulizzi: missão editorial e “content tilt”",
     "https://contentmarketinginstitute.com/author/joe-pulizzi"),
    ("Brain Traffic / Kristina Halvorson: Content Strategy Quad",
     "https://braintraffic.com/blog/new-thinking-brain-traffics-content-strategy-quad"),
    ("Google / Think with Google: modelo Hero, Hub, Help",
     "https://www.thinkwithgoogle.com/intl/en-gb/marketing-strategies/video/programming-and-channel-strategy"),
    ("Nielsen Norman Group: 4 dimensões do tom de voz",
     "https://www.nngroup.com/articles/tone-of-voice-dimensions/"),
    ("Buffer: frequência no Instagram (2 milhões de posts)",
     "https://buffer.com/resources/how-often-to-post-on-instagram/"),
    ("Socialinsider: benchmarks orgânicos do Instagram 2026",
     "https://www.socialinsider.io/blog/instagram-benchmarks/"),
    ("Sprout Social Index 2025: o que o público quer das marcas",
     "https://sproutsocial.com/insights/index/"),
    ("Opinion Box / mLabs: uso do Instagram no Brasil 2026",
     "https://www.mlabs.com.br/blog/melhores-horarios-para-postar-nas-redes-sociais/"),
    ("Adam Mosseri (Instagram): sinais de ranqueamento, jan/2025",
     "https://www.socialmediatoday.com/news/instagram-shares-algorithm-2025/738034/"),
]


# ----------------------------------------------------------------- utilidades
def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", str(s)) if unicodedata.category(c) != "Mn")


def norm_dia(s):
    t = sem_acento(s).lower().strip()[:3]
    if t not in DIAS:
        raise ValueError(f"dia da semana não reconhecido: {s!r}")
    return t


def norm_funil(s):
    if not s:
        return ""
    t = sem_acento(s).lower().strip()
    for k in FUNIL:
        if t.startswith(k[:5]):
            return k
    return t


def data_iso(s):
    s = str(s).strip()
    if re.match(r"^\d{2}/\d{2}/\d{4}$", s):
        d, m, a = s.split("/")
        return dt.date(int(a), int(m), int(d))
    return dt.date.fromisoformat(s)


def br(d):
    return d.strftime("%d/%m/%Y")


def br_curto(d):
    return f"{d.day:02d}/{d.month:02d}"


def hora_norm(h):
    h = str(h or "").strip().lower().replace("h", ":")
    if not h:
        return ""
    if h.endswith(":"):
        h += "00"
    p = h.split(":")
    try:
        return f"{int(p[0]):02d}:{int(p[1] or 0):02d}"
    except Exception:
        return str(h)


def esc(s):
    return html.escape(str(s if s is not None else ""))


def nome_arquivo(s):
    return re.sub(r'[<>:"/\\|?*]+', "", str(s)).strip() or "Empresa"


def lista(x):
    if x is None:
        return []
    return x if isinstance(x, list) else [x]


# ------------------------------------------------------------ datas especiais
def pascoa(ano):
    a = ano % 19
    b, c = divmod(ano, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = ((h + l - 7 * m + 114) % 31) + 1
    return dt.date(ano, mes, dia)


def enesimo(ano, mes, weekday, n):
    d = dt.date(ano, mes, 1)
    while d.weekday() != weekday:
        d += dt.timedelta(days=1)
    return d + dt.timedelta(weeks=n - 1)


def datas_moveis(ano):
    p = pascoa(ano)
    td = dt.timedelta
    acao_de_gracas = enesimo(ano, 11, 3, 4)
    return [
        (p - td(days=47), "Carnaval (ponto facultativo)", "facultativo", ["geral"]),
        (p - td(days=46), "Quarta-feira de Cinzas", "facultativo", ["geral"]),
        (p - td(days=2), "Sexta-feira Santa", "feriado", ["geral"]),
        (p, "Páscoa", "comercial", ["geral"]),
        (p + td(days=60), "Corpus Christi (ponto facultativo)", "facultativo", ["geral"]),
        (enesimo(ano, 5, 6, 2), "Dia das Mães", "comercial", ["geral"]),
        (enesimo(ano, 8, 6, 2), "Dia dos Pais", "comercial", ["geral"]),
        (acao_de_gracas + td(days=1), "Black Friday", "comercial", ["geral"]),
        (acao_de_gracas + td(days=4), "Cyber Monday", "comercial", ["varejo", "tecnologia"]),
        (dt.date(ano, 1, 1) + td(days=255), "Dia do Programador", "comemorativa", ["tecnologia"]),
    ]


def datas_do_periodo(inicio, fim, segmentos):
    with open(DATAS_JSON, encoding="utf-8") as f:
        base = json.load(f)
    segs = {sem_acento(s).lower() for s in lista(segmentos)} | {"geral"}
    todos = "todos" in segs

    def entra(lst):
        return todos or bool(segs & set(lst))

    dias, meses = [], []
    for ano in range(inicio.year, fim.year + 1):
        for it in base["fixas"]:
            m, d = map(int, it["dia"].split("-"))
            dd = dt.date(ano, m, d)
            if inicio <= dd <= fim and entra(it["segmentos"]):
                dias.append({"data": dd, "nome": it["nome"], "tipo": it["tipo"]})
        for dd, nome, tipo, sg in datas_moveis(ano):
            if inicio <= dd <= fim and entra(sg):
                dias.append({"data": dd, "nome": nome, "tipo": tipo})
    vistos = set()
    d = inicio.replace(day=1)
    while d <= fim:
        if (d.year, d.month) not in vistos:
            vistos.add((d.year, d.month))
            for it in base["meses"]:
                if it["mes"] == d.month and entra(it["segmentos"]):
                    meses.append({"mes": f"{MESES[d.month - 1]}/{d.year}", "nome": it["nome"]})
        d = (d.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
    dias.sort(key=lambda x: x["data"])
    return dias, meses


# ---------------------------------------------------------------------- vagas
def periodo(dados):
    p = dados.get("periodo") or {}
    ini = data_iso(p["inicio"])
    if p.get("fim"):
        fim = data_iso(p["fim"])
    else:
        fim = ini + dt.timedelta(days=7 * int(p.get("semanas", 4)) - 1)
    return ini, fim


def gerar_vagas(dados):
    ini, fim = periodo(dados)
    pular = {data_iso(x) for x in lista(dados.get("nao_postar"))}
    grade = []
    for g in lista(dados.get("grade_semanal")):
        g = dict(g)
        g["_dia"] = norm_dia(g["dia"])
        g["hora"] = hora_norm(g.get("hora"))
        grade.append(g)
    vagas = []
    d = ini
    while d <= fim:
        if d not in pular:
            for g in grade:
                if g["_dia"] == DIAS[d.weekday()]:
                    vagas.append({
                        "data": d.isoformat(), "hora": g["hora"], "rede": g.get("rede", ""),
                        "formato": g.get("formato", ""), "estilo": g.get("estilo", ""),
                        "pilar": g.get("pilar", ""), "serie": g.get("serie", ""),
                    })
        d += dt.timedelta(days=1)
    vagas.sort(key=lambda v: (v["data"], v["hora"]))
    return vagas


def cmd_vagas(caminho):
    dados = carregar(caminho)
    ini, fim = periodo(dados)
    vagas = gerar_vagas(dados)
    dias, meses = datas_do_periodo(ini, fim, dados.get("segmentos"))
    por_data = defaultdict(list)
    for e in dias:
        por_data[e["data"].isoformat()].append(e["nome"])
    print(f"Período: {br(ini)} a {br(fim)}  |  {len(vagas)} vagas  |  "
          f"{len(vagas) / max(1, ((fim - ini).days + 1) / 7):.1f} por semana\n")
    print("VAGAS (copie para 'pautas' e preencha tema, gancho, cta, funil):")
    for v in vagas:
        d = dt.date.fromisoformat(v["data"])
        extra = f"   <<< {', '.join(por_data[v['data']])}" if por_data.get(v["data"]) else ""
        print(json.dumps(v, ensure_ascii=False) + f"  # {DIAS[d.weekday()]}{extra}")
    print("\nDATAS ESPECIAIS NO PERÍODO:")
    for e in dias:
        print(f"  {br(e['data'])} {DIAS[e['data'].weekday()]}  {e['nome']}  [{e['tipo']}]")
    for m in meses:
        print(f"  mês {m['mes']}: {m['nome']}")
    alvo = {p["nome"]: p.get("percentual", 0) for p in lista(dados.get("pilares"))}
    if alvo and vagas:
        c = Counter(v["pilar"] for v in vagas if v["pilar"])
        print("\nPILARES NA GRADE (meta x grade):")
        for nome, pct in alvo.items():
            print(f"  {nome}: meta {pct}%  |  grade {100 * c.get(nome, 0) / len(vagas):.0f}%")
        sem = len([v for v in vagas if not v["pilar"]])
        if sem:
            print(f"  sem pilar fixo na grade: {sem} vagas (defina nas pautas)")


# --------------------------------------------------------------------- conferir
def carregar(caminho):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def varrer_textos(obj, caminho=""):
    if isinstance(obj, str):
        yield caminho, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if not str(k).startswith("_"):
                yield from varrer_textos(v, f"{caminho}.{k}" if caminho else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from varrer_textos(v, f"{caminho}[{i}]")


def conferir(dados, vagas, pautas, dias_esp):
    erros, avisos = [], []
    emp = dados.get("empresa") or {}
    if not emp.get("nome"):
        erros.append("empresa.nome está vazio.")
    for chave in ("missao_editorial", "pilares", "grade_semanal", "periodo", "publico", "tom_de_voz"):
        if not dados.get(chave):
            erros.append(f"falta '{chave}'.")
    pil = lista(dados.get("pilares"))
    nomes = [p.get("nome") for p in pil]
    if pil:
        soma = sum(float(p.get("percentual", 0)) for p in pil)
        if abs(soma - 100) > 0.5:
            erros.append(f"os percentuais dos pilares somam {soma:g}%, precisam somar 100%.")
        if not 3 <= len(pil) <= 5:
            avisos.append(f"{len(pil)} pilares. O recomendado é de 3 a 5.")
        for p in pil:
            if not p.get("funil"):
                avisos.append(f"pilar '{p.get('nome')}' sem etapa do funil.")
            if len(lista(p.get("exemplos_temas"))) < 3:
                avisos.append(f"pilar '{p.get('nome')}' com menos de 3 exemplos de tema.")
    ini, fim = periodo(dados)
    chaves_vagas = Counter((v["data"], v["hora"], v["rede"]) for v in vagas)
    for i, pt in enumerate(pautas):
        rot = f"pauta {i + 1} ({pt.get('data')} {pt.get('hora', '')})"
        try:
            d = data_iso(pt.get("data"))
        except Exception:
            erros.append(f"{rot}: data inválida.")
            continue
        if not ini <= d <= fim:
            erros.append(f"{rot}: fora do período {br(ini)} a {br(fim)}.")
        if pt.get("pilar") and pt["pilar"] not in nomes:
            erros.append(f"{rot}: pilar '{pt['pilar']}' não existe em 'pilares'.")
        if not pt.get("pilar"):
            avisos.append(f"{rot}: sem pilar.")
        for campo in ("tema", "gancho", "cta"):
            if not str(pt.get(campo) or "").strip():
                avisos.append(f"{rot}: '{campo}' vazio.")
        k = (d.isoformat(), hora_norm(pt.get("hora")), pt.get("rede", ""))
        if chaves_vagas and k not in chaves_vagas:
            avisos.append(f"{rot}: não bate com nenhuma vaga da grade (tudo bem se for post extra).")
    if pautas and pil:
        c = Counter(p.get("pilar") for p in pautas)
        for p in pil:
            real = 100 * c.get(p["nome"], 0) / len(pautas)
            if abs(real - float(p.get("percentual", 0))) > 10:
                avisos.append(f"pilar '{p['nome']}': meta {p.get('percentual')}%, calendário {real:.0f}%.")
    cap = (dados.get("operacao") or {}).get("capacidade_semanal")
    if cap and vagas:
        sem = ((fim - ini).days + 1) / 7
        por_sem = len([v for v in vagas if "stor" not in sem_acento(v["formato"]).lower()]) / sem
        if por_sem > float(cap) + 0.01:
            avisos.append(f"a grade pede {por_sem:.1f} peças por semana e o time disse que produz {cap}.")
    usadas = " ".join(sem_acento(json.dumps(pautas, ensure_ascii=False)).lower() for _ in [0])
    for e in dias_esp:
        if e["tipo"] in ("comercial",) and sem_acento(e["nome"]).lower().split(" (")[0] not in usadas:
            avisos.append(f"data comercial {br(e['data'])} {e['nome']} não aparece em nenhuma pauta.")
    achados = []
    for cam, txt in varrer_textos({k: v for k, v in dados.items() if k not in ("fontes",)}):
        baixo = txt.lower()
        for s in SINAIS_IA:
            if s in baixo:
                achados.append(f"{cam}: “{s}”")
    if achados:
        avisos.append("texto com cara de IA (trocar): " + "; ".join(achados[:12])
                      + (f" ... e mais {len(achados) - 12}" if len(achados) > 12 else ""))
    return erros, avisos


# ---------------------------------------------------------------------- HTML
CSS = """
:root{--cor:%(cor)s;--tinta:#16181d;--suave:#5b616e;--linha:#e3e6ec;--fundo:#f6f7f9;--papel:#fff}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%%}
body{margin:0;background:var(--fundo);color:var(--tinta);font:16px/1.55 "Segoe UI",system-ui,-apple-system,Roboto,Arial,sans-serif}
.pag{max-width:1080px;margin:0 auto;padding:24px 16px 64px}
.capa{background:var(--cor);color:#fff;border-radius:18px;padding:40px 32px;margin-bottom:24px}
.capa small{text-transform:uppercase;letter-spacing:.12em;opacity:.85;font-weight:600}
.capa h1{font-size:clamp(30px,5vw,48px);line-height:1.08;margin:8px 0 12px}
.capa p{margin:0;opacity:.92}
section{background:var(--papel);border:1px solid var(--linha);border-radius:14px;padding:24px;margin:18px 0;break-inside:avoid-page}
h2{font-size:22px;margin:0 0 4px;display:flex;gap:10px;align-items:baseline}
h2 .n{color:var(--cor);font-weight:800}
.sub{color:var(--suave);margin:0 0 16px;font-size:14px}
h3{font-size:16px;margin:18px 0 6px}
.missao{font-size:clamp(19px,2.6vw,24px);font-weight:600;line-height:1.35;border-left:5px solid var(--cor);padding:4px 0 4px 16px;margin:6px 0 16px}
.grade{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(230px,1fr))}
.card{border:1px solid var(--linha);border-radius:12px;padding:16px;background:#fff}
.card h4{margin:0 0 6px;font-size:16px}
.chip{display:inline-block;font-size:12px;font-weight:600;padding:2px 9px;border-radius:999px;background:var(--fundo);border:1px solid var(--linha);margin:2px 4px 2px 0}
.pct{font-size:28px;font-weight:800}
ul{margin:6px 0 0;padding-left:20px}li{margin:3px 0}
.k{color:var(--suave);font-size:13px;text-transform:uppercase;letter-spacing:.05em;font-weight:600}
.tabela{overflow-x:auto;margin:8px 0}
table{border-collapse:collapse;width:100%%;font-size:14px}
th,td{border-bottom:1px solid var(--linha);padding:8px 10px;text-align:left;vertical-align:top}
th{background:var(--fundo);font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--suave)}
.semana{margin-top:20px;font-weight:700}
.bolinha{display:inline-block;width:10px;height:10px;border-radius:50%%;margin-right:6px;vertical-align:middle}
.tom{display:grid;grid-template-columns:120px 1fr 120px;gap:10px;align-items:center;margin:10px 0;font-size:14px}
.tom .barra{position:relative;height:8px;border-radius:9px;background:var(--linha)}
.tom .ponto{position:absolute;top:50%%;width:18px;height:18px;border-radius:50%%;background:var(--cor);transform:translate(-50%%,-50%%);border:3px solid #fff;box-shadow:0 0 0 1px var(--cor)}
.tom span:last-child{text-align:right}
.duas{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}
.errado{border-left:4px solid #e11d48;padding-left:10px}.certo{border-left:4px solid #059669;padding-left:10px}
.especial{background:#fff7e6}
.nota{font-size:13px;color:var(--suave)}
a{color:var(--cor)}
@media (max-width:640px){.capa{padding:28px 20px}section{padding:18px}.tom{grid-template-columns:90px 1fr 90px}}
@media print{body{background:#fff}.pag{padding:0}section{border:none;padding:8px 0}.capa{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
"""


def ul(itens):
    itens = [i for i in lista(itens) if str(i).strip()]
    return "<ul>" + "".join(f"<li>{esc(i)}</li>" for i in itens) + "</ul>" if itens else ""


def tabela(cab, linhas, classes=None):
    h = "".join(f"<th>{esc(c)}</th>" for c in cab)
    corpo = ""
    for i, l in enumerate(linhas):
        cls = f' class="{classes[i]}"' if classes and classes[i] else ""
        corpo += f"<tr{cls}>" + "".join(f"<td>{c}</td>" for c in l) + "</tr>"
    return f'<div class="tabela"><table><thead><tr>{h}</tr></thead><tbody>{corpo}</tbody></table></div>'


def montar_html(dados, pautas, dias_esp, meses_esp, cor_pilar):
    emp = dados.get("empresa", {})
    ini, fim = periodo(dados)
    secoes = []
    n = [0]

    def sec(titulo, corpo, sub=""):
        if not corpo.strip():
            return
        n[0] += 1
        s = f'<p class="sub">{esc(sub)}</p>' if sub else ""
        secoes.append(f'<section><h2><span class="n">{n[0]:02d}</span>{esc(titulo)}</h2>{s}{corpo}</section>')

    def bolinha(p):
        return f'<span class="bolinha" style="background:{cor_pilar.get(p, "#999")}"></span>'

    # 1. Em uma página
    pil = lista(dados.get("pilares"))
    canais = lista(dados.get("canais"))
    obj = lista(dados.get("objetivos"))
    resumo = f'<div class="missao">{esc(dados.get("missao_editorial"))}</div>'
    if dados.get("diferencial"):
        resumo += f'<p><span class="k">Nosso diferencial</span><br>{esc(dados["diferencial"])}</p>'
    g = '<div class="grade">'
    if obj:
        g += '<div class="card"><div class="k">Objetivo principal</div><h4>' + esc(obj[0].get("objetivo")) + "</h4>"
        if obj[0].get("meta"):
            g += f'<p class="nota">{esc(obj[0]["meta"])}</p>'
        g += "</div>"
    pub = dados.get("publico", {})
    if pub.get("resumo"):
        g += f'<div class="card"><div class="k">Para quem falamos</div><p>{esc(pub["resumo"])}</p></div>'
    if canais:
        g += '<div class="card"><div class="k">Onde e quanto</div><ul>' + "".join(
            f"<li><b>{esc(c.get('rede'))}</b>: {esc(c.get('frequencia'))}</li>" for c in canais) + "</ul></div>"
    g += "</div>"
    chips = "".join(f'<span class="chip">{bolinha(p["nome"])}{esc(p["nome"])} {p.get("percentual", 0):g}%</span>' for p in pil)
    resumo += g + (f'<h3>Pilares</h3><p>{chips}</p>' if chips else "")
    if dados.get("resumo"):
        resumo += f"<p>{esc(dados['resumo'])}</p>"
    sec("Linha editorial em uma página", resumo, "O que todo mundo que cria conteúdo para a marca precisa saber.")

    # 2. Objetivos
    if obj:
        sec("Objetivos e metas", tabela(["Objetivo", "Meta", "Prazo", "Como medir"], [
            [esc(o.get("objetivo")), esc(o.get("meta")), esc(o.get("prazo")), esc(o.get("metrica"))] for o in obj]))

    # 3. Público
    corpo = ""
    pers = pub.get("persona") or {}
    if pers:
        corpo += f'<div class="card"><div class="k">Persona</div><h4>{esc(pers.get("nome"))}</h4><p>{esc(pers.get("descricao"))}</p></div>'
    blocos = [("Dores", "dores"), ("Desejos", "desejos"), ("Objeções antes de comprar", "objecoes"),
              ("Perguntas que mais chegam", "perguntas"), ("Onde consome conteúdo", "onde_consome")]
    cards = "".join(f'<div class="card"><h4>{t}</h4>{ul(pub.get(k))}</div>' for t, k in blocos if lista(pub.get(k)))
    if cards:
        corpo += f'<div class="grade" style="margin-top:14px">{cards}</div>'
    sec("Público", corpo, "Cada post responde a uma dor, um desejo, uma objeção ou uma pergunta desta lista.")

    # 4. Tom de voz
    tom = dados.get("tom_de_voz") or {}
    corpo = f"<p>{esc(tom.get('resumo'))}</p>" if tom.get("resumo") else ""
    dims = tom.get("dimensoes") or {}
    for chave, esq, dirt in TOM:
        if chave in dims:
            v = max(1, min(5, float(dims[chave])))
            corpo += (f'<div class="tom"><span>{esq}</span><div class="barra"><div class="ponto" '
                      f'style="left:{(v - 1) * 25}%"></div></div><span>{dirt}</span></div>')
    duas = ""
    for t, k in (("Somos", "somos"), ("Não somos", "nao_somos"), ("Palavras e jeitos que usamos", "usar"), ("Evitamos", "evitar")):
        if lista(tom.get(k)):
            duas += f'<div class="card"><h4>{t}</h4>{ul(tom.get(k))}</div>'
    if duas:
        corpo += f'<div class="duas" style="margin-top:14px">{duas}</div>'
    for ex in lista(tom.get("exemplos")):
        corpo += (f'<div class="duas" style="margin-top:14px"><div class="errado"><div class="k">Assim não</div>'
                  f'<p>{esc(ex.get("errado"))}</p></div><div class="certo"><div class="k">Assim sim</div>'
                  f'<p>{esc(ex.get("certo"))}</p></div></div>')
    sec("Tom de voz", corpo, "Escala das 4 dimensões de tom da Nielsen Norman Group.")

    # 5. Pilares
    cards = ""
    for p in pil:
        cards += (f'<div class="card" style="border-top:5px solid {cor_pilar[p["nome"]]}">'
                  f'<div class="pct">{p.get("percentual", 0):g}%</div><h4>{esc(p["nome"])}</h4>'
                  f'<p>{esc(p.get("descricao"))}</p>'
                  f'<p><span class="chip">{esc(FUNIL.get(norm_funil(p.get("funil")), p.get("funil", "")))}</span>'
                  + (f'<span class="chip">{esc(p["papel"])}</span>' if p.get("papel") else "") + "</p>"
                  + (f'<p class="nota"><b>Para quê:</b> {esc(p["objetivo"])}</p>' if p.get("objetivo") else "")
                  + (f'<p class="nota"><b>Formatos:</b> {esc(", ".join(lista(p.get("formatos"))))}</p>' if p.get("formatos") else "")
                  + (f'<div class="k" style="margin-top:8px">Exemplos de tema</div>{ul(p.get("exemplos_temas"))}' if p.get("exemplos_temas") else "")
                  + "</div>")
    corpo = f'<div class="grade">{cards}</div>'
    if lista(dados.get("nao_falamos")):
        corpo += f'<h3>Do que a marca não fala</h3>{ul(dados["nao_falamos"])}'
    cad = dados.get("cadencia") or {}
    if cad:
        corpo += "<h3>Ritmo Hero, Hub, Help</h3>" + tabela(["Tipo", "O que é aqui", "Frequência"], [
            [esc(k.capitalize()), esc((cad[k] or {}).get("o_que")), esc((cad[k] or {}).get("frequencia"))]
            for k in ("help", "hub", "hero") if cad.get(k)])
    sec("Pilares de conteúdo", corpo, "Todo post pertence a um pilar. O percentual é a fatia do calendário.")

    # 6. Estilos e séries
    corpo = ""
    series = lista(dados.get("series"))
    if series:
        corpo += "<h3>Quadros fixos</h3>" + tabela(["Quadro", "Formato", "Dia", "Pilar", "Como é"], [
            [f"<b>{esc(s.get('nome'))}</b>", esc(s.get("formato")), esc(s.get("dia")),
             bolinha(s.get("pilar")) + esc(s.get("pilar")), esc(s.get("descricao"))] for s in series])
    est = lista(dados.get("estilos"))
    if est:
        cards = ""
        for e in est:
            estr = lista(e.get("estrutura"))
            cards += (f'<div class="card"><span class="chip">{esc(e.get("formato"))}</span><h4>{esc(e.get("nome"))}</h4>'
                      f'<p>{esc(e.get("objetivo"))}</p>'
                      + (f'<div class="k">Estrutura</div><ol>' + "".join(f"<li>{esc(x)}</li>" for x in estr) + "</ol>" if estr else "")
                      + (f'<p class="nota"><b>Exemplo:</b> {esc(e["exemplo"])}</p>' if e.get("exemplo") else "") + "</div>")
        corpo += f'<h3>Estilos de post</h3><div class="grade">{cards}</div>'
    sec("Formatos, estilos e quadros", corpo)

    # 7. Canais e grade
    corpo = ""
    if canais:
        corpo += tabela(["Rede", "Papel na estratégia", "Frequência", "Horários", "Formatos"], [
            [f"<b>{esc(c.get('rede'))}</b>", esc(c.get("papel")), esc(c.get("frequencia")),
             esc(c.get("horarios")), esc(", ".join(lista(c.get("formatos"))))] for c in canais])
    grade = sorted(lista(dados.get("grade_semanal")), key=lambda x: (DIAS.index(norm_dia(x["dia"])), hora_norm(x.get("hora"))))
    if grade:
        corpo += "<h3>Grade da semana</h3>" + tabela(["Dia", "Hora", "Rede", "Formato", "Estilo", "Pilar"], [
            [DIAS_NOME[DIAS.index(norm_dia(x["dia"]))], esc(hora_norm(x.get("hora"))), esc(x.get("rede")),
             esc(x.get("formato")), esc(x.get("estilo")), bolinha(x.get("pilar")) + esc(x.get("pilar"))] for x in grade])
    if dados.get("nota_horarios"):
        corpo += f'<p class="nota">{esc(dados["nota_horarios"])}</p>'
    sec("Canais, frequência e horários", corpo, "Horários de Brasília. Revisar com os dados do próprio perfil depois de 4 a 6 semanas.")

    # 8. Stories
    st = dados.get("stories") or {}
    if st:
        corpo = f"<p><b>Frequência:</b> {esc(st.get('frequencia'))}</p>" if st.get("frequencia") else ""
        if lista(st.get("rotina")):
            corpo += tabela(["Quando", "Horário", "O que entra"], [
                [esc(r.get("dia")), esc(r.get("horario")), esc(r.get("conteudo"))] for r in st["rotina"]])
        corpo += ul(st.get("regras"))
        sec("Rotina de stories", corpo)

    # 9. Calendário
    por_data = defaultdict(list)
    for e in dias_esp:
        por_data[e["data"]].append(e["nome"])
    linhas, classes, corpo, semana_atual = [], [], "", None
    def fecha():
        nonlocal corpo, linhas, classes
        if linhas:
            corpo += tabela(["Data", "Hora", "Rede / formato", "Pilar", "Tema e gancho", "CTA"], linhas, classes)
        linhas, classes = [], []
    for pt in pautas:
        d = data_iso(pt["data"])
        sem = (d - ini).days // 7
        if sem != semana_atual:
            fecha()
            s_ini = ini + dt.timedelta(days=7 * sem)
            corpo += f'<div class="semana">Semana {sem + 1}: {br_curto(s_ini)} a {br_curto(min(fim, s_ini + dt.timedelta(days=6)))}</div>'
            semana_atual = sem
        esp = por_data.get(d, [])
        tema = f"<b>{esc(pt.get('tema'))}</b>"
        if pt.get("gancho"):
            tema += f"<br><span class='nota'>Gancho: {esc(pt['gancho'])}</span>"
        if pt.get("observacao"):
            tema += f"<br><span class='nota'>{esc(pt['observacao'])}</span>"
        if esp:
            tema += f"<br><span class='chip'>📅 {esc(', '.join(esp))}</span>"
        formato = esc(pt.get("formato"))
        if pt.get("estilo"):
            formato += f"<br><span class='nota'>{esc(pt['estilo'])}</span>"
        linhas.append([f"<b>{DIAS[d.weekday()]}</b> {br_curto(d)}", esc(hora_norm(pt.get("hora"))),
                       f"{esc(pt.get('rede'))}<br>{formato}", bolinha(pt.get("pilar")) + esc(pt.get("pilar")),
                       tema, esc(pt.get("cta"))])
        classes.append("especial" if esp else "")
    fecha()
    sec("Calendário do período", corpo, f"{br(ini)} a {br(fim)}. {len(pautas)} publicações. Linhas em destaque caem em data especial.")

    # 10. Datas especiais
    linhas = [[f"{DIAS[e['data'].weekday()]} {br(e['data'])}", esc(e["nome"]), esc(e["tipo"])] for e in dias_esp]
    linhas += [[esc(x.get("data")), esc(x.get("nome")), esc(x.get("acao") or "da empresa")] for x in lista(dados.get("datas_empresa"))]
    corpo = tabela(["Data", "Data especial", "Tipo / ação"], linhas) if linhas else ""
    if meses_esp:
        corpo += "<h3>Temas do mês</h3>" + ul([f"{m['mes']}: {m['nome']}" for m in meses_esp])
    corpo += '<p class="nota">Só entra data que tem a ver com a marca. Conferir a data antes de publicar.</p>' if corpo else ""
    sec("Datas especiais do período", corpo)

    # 11. Operação
    op = dados.get("operacao") or {}
    corpo = ""
    if op.get("capacidade_semanal"):
        corpo += f"<p><b>Capacidade do time:</b> {esc(op['capacidade_semanal'])} peças por semana (fora stories).</p>"
    if lista(op.get("fluxo")):
        corpo += tabela(["Etapa", "Quem", "Prazo"], [[esc(f.get("etapa")), esc(f.get("responsavel")), esc(f.get("prazo"))] for f in op["fluxo"]])
    if lista(op.get("regras")):
        corpo += "<h3>Combinados</h3>" + ul(op["regras"])
    if lista(dados.get("regras")):
        corpo += "<h3>Cuidados e regras da marca</h3>" + ul(dados["regras"])
    sec("Produção e aprovação", corpo)

    # 12. Métricas
    corpo = ""
    if lista(dados.get("metricas")):
        corpo += tabela(["Para saber se...", "Olhar", "Meta", "Onde ver"], [
            [esc(m.get("objetivo")), esc(m.get("metrica")), esc(m.get("meta")), esc(m.get("onde_ver"))] for m in dados["metricas"]])
    if lista(dados.get("revisao")):
        corpo += "<h3>Rotina de revisão</h3>" + ul(dados["revisao"])
    sec("Métricas e revisão", corpo)

    # 13. Suposições
    if lista(dados.get("suposicoes")):
        sec("O que ainda precisa ser confirmado", ul(dados["suposicoes"]), "Pontos decididos sem resposta do cliente.")

    fontes = "".join(f'<li><a href="{esc(u)}">{esc(t)}</a></li>' for t, u in FONTES)
    secoes.append(f'<section><h2>Base do método</h2><p class="sub">Estudos e referências usados para montar esta linha editorial.</p><ul>{fontes}</ul></section>')

    cor = dados.get("cor_marca") or "#1f4fd1"
    titulo = f"Linha Editorial {emp.get('nome', '')}".strip()
    capa = (f'<div class="capa"><small>Linha editorial</small><h1>{esc(emp.get("nome"))}</h1>'
            f'<p>{esc(emp.get("segmento", ""))}{" · " + esc(emp.get("cidade")) if emp.get("cidade") else ""}</p>'
            f'<p style="margin-top:14px">Período do calendário: {br(ini)} a {br(fim)}'
            f'{" · Feito por " + esc(dados.get("elaborado_por")) if dados.get("elaborado_por") else ""}'
            f' · Versão de {br(dt.date.today())}</p></div>')
    return (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(titulo)}</title>'
            f'<style>{CSS % {"cor": esc(cor)}}</style></head><body><div class="pag">{capa}{"".join(secoes)}</div></body></html>')


# ---------------------------------------------------------------- planilha
def clarear(hexcor, f=0.78):
    hexcor = hexcor.lstrip("#")
    r, g, b = (int(hexcor[i:i + 2], 16) for i in (0, 2, 4))
    r, g, b = (int(c + (255 - c) * f) for c in (r, g, b))
    return f"{r:02X}{g:02X}{b:02X}"


def montar_planilha(dados, pautas, dias_esp, cor_pilar, caminho_xlsx, caminho_csv):
    por_data = defaultdict(list)
    for e in dias_esp:
        por_data[e["data"]].append(e["nome"])
    cab = ["Data", "Dia", "Hora", "Rede", "Formato", "Estilo", "Pilar", "Funil", "Tema", "Gancho",
           "CTA", "Observação", "Data especial", "Status", "Responsável", "Link do material"]
    linhas = []
    for pt in pautas:
        d = data_iso(pt["data"])
        linhas.append([br(d), DIAS_NOME[d.weekday()], hora_norm(pt.get("hora")), pt.get("rede", ""),
                       pt.get("formato", ""), pt.get("estilo", ""), pt.get("pilar", ""),
                       FUNIL.get(norm_funil(pt.get("funil")), pt.get("funil", "")).split(" (")[0],
                       pt.get("tema", ""), pt.get("gancho", ""), pt.get("cta", ""), pt.get("observacao", ""),
                       ", ".join(por_data.get(d, [])), pt.get("status", "A produzir"), pt.get("responsavel", ""), ""])
    with open(caminho_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(cab)
        w.writerows(linhas)
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Alignment, Font, PatternFill
        from openpyxl.worksheet.datavalidation import DataValidation
    except ImportError:
        return "openpyxl não instalado: só o CSV foi gerado (pip install openpyxl)."
    wb = Workbook()
    ws = wb.active
    ws.title = "Calendário"
    cor = (dados.get("cor_marca") or "#1f4fd1").lstrip("#")
    head = PatternFill("solid", fgColor=cor)

    def cabecalho(sheet, colunas, larguras):
        sheet.append(colunas)
        for i, c in enumerate(sheet[1], start=1):
            c.font = Font(bold=True, color="FFFFFF")
            c.fill = head
            c.alignment = Alignment(vertical="center", wrap_text=True)
            sheet.column_dimensions[c.column_letter].width = larguras[i - 1] if i - 1 < len(larguras) else 16
        sheet.freeze_panes = "A2"

    cabecalho(ws, cab, [11, 9, 7, 11, 12, 18, 18, 13, 38, 38, 26, 26, 22, 13, 14, 26])
    for l in linhas:
        ws.append(l)
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(vertical="top", wrap_text=True)
        p = row[6].value
        if p in cor_pilar:
            row[6].fill = PatternFill("solid", fgColor=clarear(cor_pilar[p]))
        if row[12].value:
            row[12].fill = PatternFill("solid", fgColor="FFF2CC")
    dv = DataValidation(type="list", formula1='"A produzir,Em produção,Em aprovação,Ajustes,Aprovado,Agendado,Publicado"', allow_blank=True)
    ws.add_data_validation(dv)
    if linhas:
        dv.add(f"N2:N{len(linhas) + 1}")
        ws.auto_filter.ref = f"A1:P{len(linhas) + 1}"

    ws2 = wb.create_sheet("Grade semanal")
    cabecalho(ws2, ["Dia", "Hora", "Rede", "Formato", "Estilo", "Pilar", "Quadro"], [11, 8, 12, 12, 24, 20, 20])
    for x in sorted(lista(dados.get("grade_semanal")), key=lambda x: (DIAS.index(norm_dia(x["dia"])), hora_norm(x.get("hora")))):
        ws2.append([DIAS_NOME[DIAS.index(norm_dia(x["dia"]))], hora_norm(x.get("hora")), x.get("rede", ""),
                    x.get("formato", ""), x.get("estilo", ""), x.get("pilar", ""), x.get("serie", "")])

    ws3 = wb.create_sheet("Pilares")
    cabecalho(ws3, ["Pilar", "%", "Funil", "Descrição", "Exemplos de tema"], [22, 6, 16, 50, 60])
    for p in lista(dados.get("pilares")):
        ws3.append([p["nome"], p.get("percentual", 0), FUNIL.get(norm_funil(p.get("funil")), p.get("funil", "")).split(" (")[0],
                    p.get("descricao", ""), " | ".join(lista(p.get("exemplos_temas")))])
        ws3.cell(ws3.max_row, 1).fill = PatternFill("solid", fgColor=clarear(cor_pilar[p["nome"]]))

    ws4 = wb.create_sheet("Datas especiais")
    cabecalho(ws4, ["Data", "Dia", "Data especial", "Tipo"], [12, 10, 44, 14])
    for e in dias_esp:
        ws4.append([br(e["data"]), DIAS_NOME[e["data"].weekday()], e["nome"], e["tipo"]])
    for x in lista(dados.get("datas_empresa")):
        ws4.append([x.get("data", ""), "", x.get("nome", ""), x.get("acao") or "da empresa"])

    st = dados.get("stories") or {}
    if lista(st.get("rotina")):
        ws5 = wb.create_sheet("Stories")
        cabecalho(ws5, ["Quando", "Horário", "O que entra"], [18, 10, 70])
        for r in st["rotina"]:
            ws5.append([r.get("dia", ""), r.get("horario", ""), r.get("conteudo", "")])
    for sheet in wb.worksheets[1:]:
        for row in sheet.iter_rows(min_row=2):
            for c in row:
                c.alignment = Alignment(vertical="top", wrap_text=True)
    wb.save(caminho_xlsx)
    return ""


def cmd_montar(caminho):
    dados = carregar(caminho)
    pasta = os.path.dirname(os.path.abspath(caminho))
    ini, fim = periodo(dados)
    vagas = gerar_vagas(dados)
    pautas = lista(dados.get("pautas"))
    if not pautas:
        pautas = [dict(v) for v in vagas]
    pautas.sort(key=lambda p: (str(data_iso(p["data"])), hora_norm(p.get("hora"))))
    dias_esp, meses_esp = datas_do_periodo(ini, fim, dados.get("segmentos"))
    erros, avisos = conferir(dados, vagas, pautas, dias_esp)
    if not dados.get("pautas"):
        avisos.insert(0, "sem 'pautas': o calendário saiu só com as vagas da grade, sem temas.")
    cor_pilar = {}
    for i, p in enumerate(lista(dados.get("pilares"))):
        cor_pilar[p["nome"]] = p.get("cor") or CORES[i % len(CORES)]
    nome = nome_arquivo((dados.get("empresa") or {}).get("nome"))
    if not erros:
        h = os.path.join(pasta, f"Linha Editorial - {nome}.html")
        x = os.path.join(pasta, f"Calendario - {nome}.xlsx")
        c = os.path.join(pasta, f"Calendario - {nome}.csv")
        with open(h, "w", encoding="utf-8") as f:
            f.write(montar_html(dados, pautas, dias_esp, meses_esp, cor_pilar))
        msg = montar_planilha(dados, pautas, dias_esp, cor_pilar, x, c)
        if msg:
            avisos.append(msg)
        print("ARQUIVOS:")
        for a in (h, x, c):
            if os.path.exists(a):
                print("  " + a)
    sem = ((fim - ini).days + 1) / 7
    c = Counter(p.get("formato", "") for p in pautas)
    print(f"\nRESUMO: {br(ini)} a {br(fim)} | {len(pautas)} publicações ({len(pautas) / sem:.1f}/semana) | "
          + ", ".join(f"{k or 'sem formato'} {v}" for k, v in c.most_common()))
    print(f"\nERROS ({len(erros)}):" + ("" if erros else " nenhum"))
    for e in erros:
        print("  - " + e)
    print(f"\nAVISOS ({len(avisos)}):" + ("" if avisos else " nenhum"))
    for a in avisos:
        print("  - " + a)
    return 1 if erros else 0


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("vagas", "montar"):
        print(__doc__)
        sys.exit(2)
    if sys.argv[1] == "vagas":
        cmd_vagas(sys.argv[2])
    else:
        sys.exit(cmd_montar(sys.argv[2]))
