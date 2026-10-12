"""Cruza o calendário do Notion com o que realmente saiu no Instagram.

Uso:
    python -I instagram_conferencia.py --hoje 2026-10-12 --cards cards.json \
        --ig clailton=ig_clailton.json --ig legacy=ig_legacy.json --ig allan=ig_allan.json [--json saida.json]

cards.json: lista de cards do calendário (DEMANDAS | TIME DE CRIAÇÃO) com publicação nos últimos dias:
    [{"pauta", "perfil" (LEGACY|CLAILTON|ALLAN), "formato" (texto ou lista), "publicacao" (ISO, UTC),
      "andamento", "url", "legenda" (texto da seção "💬 LEGENDA" do card, se houver)}]
ig_*.json: resposta crua da função instagram-metrics do Insights Hub
    (endpoint=media&with_insights=true&since=...), formato {"data": {"data": [posts]}} ou {"data": [posts]}.

Saída: Markdown (stdout) e, com --json, o bloco "instagram" para o painel.
Status de cada card: no_horario (até 15 min de diferença), atrasado, antecipado, nao_saiu, futuro.
"""
import argparse
import difflib
import json
import re
import sys
import unicodedata
from datetime import date, datetime, timedelta

PERFIS = {"CLAILTON": "clailton", "LEGACY": "legacy", "ALLAN": "allan"}
NOME_PERFIL = {"clailton": "Clailton", "legacy": "Legacy", "allan": "Allan"}
TOLERANCIA_MIN = 15
JANELA_H = 36
BR = timedelta(hours=-3)


def norm(t):
    t = unicodedata.normalize("NFKD", str(t or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9 ]+", " ", t).split()


def parecido(a, b, n=60):
    """0 a 1: quanto o começo de dois textos se parece (palavras)."""
    a, b = norm(a)[:n], norm(b)[:n]
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def quando(txt):
    if not txt:
        return None
    return datetime.fromisoformat(str(txt).replace("Z", "+00:00")).replace(tzinfo=None)


def tipo_card(formato):
    f = " ".join(formato) if isinstance(formato, list) else str(formato or "")
    f = f.lower()
    if "reels" in f or "video" in f or "vídeo" in f:
        return "REELS"
    if "story" in f:
        return "STORY"
    return "FEED"


def carregar_ig(caminho):
    with open(caminho, encoding="utf-8") as f:
        d = json.load(f)
    x = d.get("data", d)
    if isinstance(x, dict):
        x = x.get("data", [])
    return x or []


def metricas(p):
    i = p.get("insights") or {}
    return {
        "views": i.get("views") or i.get("plays"),
        "alcance": i.get("reach"),
        "curtidas": i.get("likes", p.get("like_count")),
        "comentarios": i.get("comments", p.get("comments_count")),
        "salvos": i.get("saved"),
        "compart": i.get("shares"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hoje", required=True)
    ap.add_argument("--cards", required=True)
    ap.add_argument("--ig", action="append", default=[], help="perfil=arquivo.json")
    ap.add_argument("--dias", type=int, default=7)
    ap.add_argument("--json")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    agora = datetime.combine(date.fromisoformat(a.hoje), datetime.min.time()) + timedelta(hours=11)  # 8h BR
    inicio = agora - timedelta(days=a.dias)
    posts = {}
    for par in a.ig:
        perfil, caminho = par.split("=", 1)
        posts[perfil] = [p for p in carregar_ig(caminho) if quando(p.get("timestamp")) and quando(p["timestamp"]) >= inicio - timedelta(hours=JANELA_H)]

    with open(a.cards, encoding="utf-8") as f:
        cards = json.load(f)

    usados = set()
    conferidos = []
    for c in sorted(cards, key=lambda c: c.get("publicacao") or ""):
        perfil = PERFIS.get(str(c.get("perfil") or "").upper())
        plan = quando(c.get("publicacao"))
        if not perfil or not plan or plan < inicio or perfil not in posts:
            continue
        tipo = tipo_card(c.get("formato"))
        if tipo == "STORY":
            continue  # stories não vêm nessa lista do Instagram
        ref = c.get("legenda") or c.get("pauta")
        melhor, nota_melhor = None, 0.0
        for p in posts[perfil]:
            if p["id"] in usados:
                continue
            dt = abs((quando(p["timestamp"]) - plan).total_seconds()) / 3600
            if dt > JANELA_H:
                continue
            sim = parecido(ref, p.get("caption"))
            mesmo_tipo = (p.get("media_product_type") == "REELS") == (tipo == "REELS")
            nota = sim * 0.7 + max(0, 1 - dt / JANELA_H) * 0.3 + (0.15 if mesmo_tipo else -0.2)
            if nota > nota_melhor:
                melhor, nota_melhor = p, nota
        item = {
            "pauta": c.get("pauta"), "url": c.get("url"), "perfil": NOME_PERFIL[perfil],
            "formato": "Reels" if tipo == "REELS" else "Feed", "andamento": c.get("andamento"),
            "planejado": (plan + BR).strftime("%d/%m %H:%M"),
        }
        if melhor and nota_melhor >= 0.35:
            usados.add(melhor["id"])
            pub = quando(melhor["timestamp"])
            dif = round((pub - plan).total_seconds() / 60)
            status = "no_horario" if abs(dif) <= TOLERANCIA_MIN else ("atrasado" if dif > 0 else "antecipado")
            leg = parecido(c.get("legenda"), melhor.get("caption"), n=120) if c.get("legenda") else None
            item.update({
                "status": status, "diferenca_min": dif, "publicado": (pub + BR).strftime("%d/%m %H:%M"),
                "link": melhor.get("permalink"), "legenda_igual": None if leg is None else round(leg, 2),
                **metricas(melhor),
            })
        else:
            item["status"] = "futuro" if plan > agora else "nao_saiu"
        conferidos.append(item)

    fora = []
    for perfil, lista in posts.items():
        for p in lista:
            t = quando(p["timestamp"])
            if p["id"] in usados or t < inicio or p.get("media_product_type") == "STORY":
                continue
            fora.append({"perfil": NOME_PERFIL.get(perfil, perfil), "publicado": (t + BR).strftime("%d/%m %H:%M"),
                         "legenda": (p.get("caption") or "")[:90], "link": p.get("permalink"), **metricas(p)})

    saiu = [c for c in conferidos if c["status"] in ("no_horario", "atrasado", "antecipado")]
    legenda_dif = [c for c in saiu if c.get("legenda_igual") is not None and c["legenda_igual"] < 0.8]
    por_views = sorted([c for c in saiu if c.get("views") is not None], key=lambda c: -c["views"])
    resumo = {
        "no_horario": sum(c["status"] == "no_horario" for c in conferidos),
        "atrasados": sum(c["status"] == "atrasado" for c in conferidos),
        "antecipados": sum(c["status"] == "antecipado" for c in conferidos),
        "nao_sairam": sum(c["status"] == "nao_saiu" for c in conferidos),
        "legenda_diferente": len(legenda_dif),
        "fora_do_notion": len(fora),
    }

    def linha(c):
        m = f"{c.get('views') or 0:,} views · alcance {c.get('alcance') or 0:,} · {c.get('salvos') or 0} salvos · {c.get('compart') or 0} compart.".replace(",", ".")
        return f"{c['perfil']} · {c['pauta']} — {m}"

    out = [f"### Conferência do Instagram (últimos {a.dias} dias)",
           f"- No horário: {resumo['no_horario']} · Atrasados: {resumo['atrasados']} · Antecipados: {resumo['antecipados']} · "
           f"Não saíram: {resumo['nao_sairam']} · Legenda diferente do Notion: {resumo['legenda_diferente']} · "
           f"Postados sem card no Notion: {resumo['fora_do_notion']}"]
    probl = [c for c in conferidos if c["status"] in ("atrasado", "antecipado", "nao_saiu")] + legenda_dif
    if probl:
        out.append("\n**Pontos de atenção**")
        for c in probl:
            if c in legenda_dif and c["status"] == "no_horario":
                out.append(f"- ✏️ {c['perfil']} · {c['pauta']}: legenda publicada diferente da do Notion ({int(c['legenda_igual'] * 100)}% igual).")
            elif c["status"] == "nao_saiu":
                out.append(f"- ❌ {c['perfil']} · {c['pauta']}: marcado para {c['planejado']} e não encontrei no Instagram ({c['andamento']}).")
            else:
                sinal = "atrasou" if c["status"] == "atrasado" else "saiu antes"
                out.append(f"- 🕒 {c['perfil']} · {c['pauta']}: {sinal} {abs(c['diferenca_min'])} min (marcado {c['planejado']}, saiu {c['publicado']}).")
    if fora:
        out.append("\n**Postado sem card no Notion**")
        for p in fora[:8]:
            out.append(f"- {p['perfil']} · {p['publicado']} · \"{p['legenda']}\"")
    if por_views:
        out.append("\n**Melhores da semana (views)**")
        out += [f"{i}. {linha(c)}" for i, c in enumerate(por_views[:3], 1)]
        out.append("\n**Mais fracos da semana (views)**")
        out += [f"- {linha(c)}" for c in por_views[-3:][::-1]]
    print("\n".join(out))

    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump({"resumo": resumo, "conferidos": conferidos, "fora_do_notion": fora[:20],
                       "top": por_views[:3], "fracos": por_views[-3:][::-1]}, f, ensure_ascii=False)


if __name__ == "__main__":
    main()
