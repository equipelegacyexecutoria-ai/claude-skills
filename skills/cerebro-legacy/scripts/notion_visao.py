"""Resume o resultado de uma visão do Notion (notion-query-data-sources, modo "view").

A resposta do modo "view" traz todas as colunas do card (IDEIA, CORREÇÕES, arquivos...) e
costuma passar do limite, indo para um arquivo. Este script lê esse arquivo e imprime uma
linha curta por card, com as datas já no horário de Brasília (UTC-3):

    python -I scripts/notion_visao.py <arquivo1> [<arquivo2> ...]

Saída: pauta | andamento | responsável | prioridade | perfil | formato | publicação | conclusão | url
"""
import json
import sys
from datetime import datetime, timedelta

CAMPOS = [
    ("pauta", ["PAUTA", "Tarefa"]),
    ("andamento", ["ANDAMENTO", "Andamento"]),
    ("resp", ["RESPONSÁVEL", "Responsável"]),
    ("prio", ["PRIORIDADE", "Prioridade"]),
    ("perfil", ["PERFIL"]),
    ("formato", ["FORMATO", "Formato"]),
]
PUB = ["date:DATA D/ PUBLICACÃO:start", "date:Data D/ Publicação:start"]
CONC = ["date:DATA D/ CONCLUSÃO:start", "date:Data D/ Conclusão:start"]


def carregar(caminho):
    d = json.loads(open(caminho, encoding="utf-8").read())
    if isinstance(d, list) and d and isinstance(d[0], dict) and "text" in d[0]:
        d = json.loads(d[0]["text"])
    if isinstance(d, dict) and isinstance(d.get("text"), str):
        try:
            d = json.loads(d["text"])
        except ValueError:
            pass
    return d


def primeiro(p, nomes):
    for n in nomes:
        v = p.get(n)
        if v not in (None, "", "[]"):
            return v
    return ""


def limpar(v):
    if isinstance(v, str) and v.startswith("["):
        try:
            v = ", ".join(json.loads(v))
        except ValueError:
            pass
    if isinstance(v, list):
        v = ", ".join(map(str, v))
    v = str(v).replace("**", "").replace("\\$", "$").replace("\n", " ").strip()
    return v[:80]


def data_brt(v):
    if not v:
        return "-"
    if "T" not in v:
        return v
    t = datetime.fromisoformat(v.replace("Z", "+00:00")) - timedelta(hours=3)
    return t.strftime("%Y-%m-%d %H:%M")


def main():
    for caminho in sys.argv[1:]:
        d = carregar(caminho)
        linhas = d.get("results", []) if isinstance(d, dict) else []
        print(f"# {caminho}: {len(linhas)} cards; has_more={d.get('has_more')}"
              + (f"; next_cursor={d.get('next_cursor')}" if d.get("has_more") else ""))
        for r in linhas:
            p = r.get("properties", r)
            partes = [limpar(primeiro(p, nomes)) or "-" for _, nomes in CAMPOS]
            partes += [data_brt(primeiro(p, PUB)), data_brt(primeiro(p, CONC)), p.get("url", "")]
            print(" | ".join(partes))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
