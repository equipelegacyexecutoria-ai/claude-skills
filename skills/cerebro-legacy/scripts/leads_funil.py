"""Resume os leads orgânicos e do Quiz a partir de respostas salvas do getDeals (Pipedrive).

Uso:
    python -I leads_funil.py --hoje 2026-10-12 ARQUIVO1.json [ARQUIVO2.json ...]
    (acrescente --detalhes para listar os leads parados por nome; só para a página privada do Igor)

Cada arquivo é a resposta crua do getDeals ({"data": [...], ...}); várias páginas são somadas.
Saída: Markdown com chegadas de ontem, avanços de ontem, parados, funil por etapa e comparação com o pago.
Nunca imprime telefone/e-mail; nomes só com --detalhes.
"""
import argparse
import collections
import json
import sys
from datetime import date, datetime, timedelta

UTM_SOURCE = "8edcf78215c52bc6cd4e609bbcc9556e9340d237"
UTM_CAMPAIGN = "ad2d705d02225947afb06abb446e71b45925619a"
UTM_MEDIUM = "e3d3416c2ffc921e46b99ceb5ff1acb7e987b55c"

# Ordem das etapas em cada funil (a etapa seguinte = avançou). Etapas fora da lista = saída.
FUNIS = {
    5: ("SOCIAL SELLING", [44, 47, 51, 52]),
    2: ("FUNIL LEGADO", [6, 7, 8, 9, 10, 20, 11]),
    4: ("FUNIL IMPULSÃO", [41, 24, 43, 42, 25]),
    6: ("FUNIL OUTBOUND", [53, 54, 55, 56]),
}
ETAPAS = {
    6: "Oportunidade (MQL)", 7: "Tentativa de Conexão", 8: "Lead Qualificado", 9: "Agendamento Closer",
    10: "Reunião Realizada", 11: "Vendido", 20: "Forecast",
    24: "Em Atendimento", 25: "Fechado", 39: "Refugo Allbound", 40: "Sem Resposta", 41: "Op Allbound",
    42: "Link de Pagamento Enviado", 43: "Demo Agendada",
    44: "Prospect", 47: "Lead", 51: "Lead Qualificado", 52: "Agendamento",
    53: "Lista de Leads", 54: "Filtro 1", 55: "Filtro 2", 56: "Agendamento Closer",
}
PARADO_DIAS = 3
BR = timedelta(hours=-3)


def quando(txt):
    if not txt:
        return None
    return datetime.fromisoformat(txt.replace("Z", "+00:00")).replace(tzinfo=None) + BR


def origem(d):
    cf = d.get("custom_fields") or {}
    src = str(cf.get(UTM_SOURCE) or "").lower()
    camp = str(cf.get(UTM_CAMPAIGN) or "")
    med = str(cf.get(UTM_MEDIUM) or "")
    labels = [l.get("label") for l in d.get("labels") or [] if isinstance(l, dict)]
    if "QUIZ" in labels or "quiz" in src:
        return "quiz", "Quiz"
    if src in ("organico", "instagram"):
        if med == "automacao-novo-seguidor":
            return "organico", "Automação novo seguidor (Clailton)"
        if med == "tiktok":
            return "organico", f"TikTok ({camp})"
        return "organico", camp or "orgânico"
    if src == "facebook":
        return "pago", "Anúncio"
    return "outro", src or "sem origem"


def carregar(arquivos):
    vistos = {}
    for a in arquivos:
        with open(a, encoding="utf-8") as f:
            for d in json.load(f).get("data") or []:
                vistos[d["id"]] = d
    return list(vistos.values())


def pct(a, b):
    return f"{(100 * a / b):.0f}%" if b else "—"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hoje", required=True)
    ap.add_argument("--janela", type=int, default=15, help="dias para o funil")
    ap.add_argument("--detalhes", action="store_true")
    ap.add_argument("arquivos", nargs="+")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    hoje = date.fromisoformat(a.hoje)
    ontem = hoje - timedelta(days=1)
    if hoje.weekday() == 0:  # segunda: "ontem" cobre sexta a domingo
        ontem_ini = hoje - timedelta(days=3)
    else:
        ontem_ini = ontem
    deals = carregar(a.arquivos)

    alvo = [d for d in deals if origem(d)[0] in ("organico", "quiz")]
    pagos = [d for d in deals if origem(d)[0] == "pago"]
    rot = "ontem" if ontem_ini == ontem else f"de {ontem_ini:%d/%m} a {ontem:%d/%m}"
    out = []

    # 1. Chegaram
    novos = [d for d in alvo if ontem_ini <= quando(d["add_time"]).date() <= ontem]
    por = collections.Counter(origem(d)[1] for d in novos)
    pagos_n = sum(1 for d in pagos if ontem_ini <= quando(d["add_time"]).date() <= ontem)
    out.append(f"### Chegaram {rot}: {len(novos)} orgânicos/Quiz (pago, só referência: {pagos_n})")
    for k, v in por.most_common():
        out.append(f"- {k}: {v}")
    sete = [d for d in alvo if quando(d["add_time"]).date() >= hoje - timedelta(days=7)]
    por_dia = collections.Counter(quando(d["add_time"]).date() for d in sete)
    out.append("- Últimos 7 dias: " + ", ".join(f"{dia:%d/%m} {por_dia.get(dia, 0)}"
               for dia in (hoje - timedelta(days=i) for i in range(7, 0, -1))))

    # 2. Avançaram
    avan = [d for d in alvo if d.get("stage_change_time")
            and ontem_ini <= quando(d["stage_change_time"]).date() <= ontem and d.get("status") != "lost"]
    out.append(f"\n### Avançaram de etapa {rot}: {len(avan)}")
    for (p, s), v in collections.Counter((d["pipeline_id"], d["stage_id"]) for d in avan).most_common():
        out.append(f"- {FUNIS.get(p, (str(p),))[0]} → {ETAPAS.get(s, s)}: {v}")
    ganhos = [d for d in alvo if d.get("status") == "won" and d.get("won_time")
              and ontem_ini <= quando(d["won_time"]).date() <= ontem]
    perdidos = [d for d in alvo if d.get("status") == "lost" and d.get("lost_time")
                and ontem_ini <= quando(d["lost_time"]).date() <= ontem]
    out.append(f"- Vendas: {len(ganhos)} · Perdidos: {len(perdidos)}")
    if perdidos:
        mot = collections.Counter((d.get("lost_reason") or "sem motivo").strip()[:60] for d in perdidos)
        out.append("  - Motivos: " + "; ".join(f"{k} ({v})" for k, v in mot.most_common(5)))

    # 3. Parados
    agora = datetime.combine(hoje, datetime.min.time()) + timedelta(hours=8)
    parados = []
    for d in alvo:
        if d.get("status") != "open":
            continue
        ref = quando(d.get("stage_change_time")) or quando(d["add_time"])
        dias = (agora - ref).days
        if dias >= PARADO_DIAS:
            parados.append((dias, d))
    parados.sort(key=lambda t: -t[0])
    out.append(f"\n### Parados há {PARADO_DIAS}+ dias sem mudar de etapa: {len(parados)}")
    for (p, s), v in collections.Counter((d["pipeline_id"], d["stage_id"]) for _, d in parados).most_common():
        out.append(f"- {FUNIS.get(p, (str(p),))[0]} · {ETAPAS.get(s, s)}: {v}")
    if a.detalhes and parados:
        out.append("- Os 10 parados há mais tempo:")
        for dias, d in parados[:10]:
            out.append(f"  - {d.get('title', '')} — {ETAPAS.get(d['stage_id'], d['stage_id'])}, "
                       f"{dias} dias (negócio {d['id']})")

    # 4. Funil
    ini = hoje - timedelta(days=a.janela)
    jan = [d for d in alvo if quando(d["add_time"]).date() >= ini]
    out.append(f"\n### Funil dos orgânicos/Quiz que entraram nos últimos {a.janela} dias ({len(jan)} leads)")
    out.append("Conta quem chegou em cada etapa ou passou dela (perdido conta na etapa onde parou).")
    for p, (nome, ordem) in FUNIS.items():
        grupo = [d for d in jan if d["pipeline_id"] == p]
        if not grupo:
            continue
        pos = {s: i for i, s in enumerate(ordem)}
        alcan = collections.Counter()
        saida = collections.Counter()
        for d in grupo:
            i = pos.get(d["stage_id"])
            if i is None:
                saida[ETAPAS.get(d["stage_id"], d["stage_id"])] += 1
                i = 0
            if d.get("status") == "won":
                i = len(ordem) - 1
            for k in range(i + 1):
                alcan[ordem[k]] += 1
        linha = []
        for k, s in enumerate(ordem):
            n = alcan[s]
            taxa = "" if k == 0 else f" ({pct(n, alcan[ordem[k - 1]])})"
            linha.append(f"{ETAPAS.get(s, s)} {n}{taxa}")
        out.append(f"- **{nome}** ({len(grupo)}): " + " → ".join(linha))
        if saida:
            out.append("  - Saíram do caminho: " + ", ".join(f"{k} {v}" for k, v in saida.most_common()))
        perd = sum(1 for d in grupo if d.get("status") == "lost")
        out.append(f"  - Abertos {sum(1 for d in grupo if d.get('status') == 'open')} · "
                   f"perdidos {perd} · vendidos {sum(1 for d in grupo if d.get('status') == 'won')}")
    print("\n".join(out))


if __name__ == "__main__":
    main()
