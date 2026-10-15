"""Gera o conteúdo do card do Notion (notion_card_epNN.md) de cada episódio.
Uso: python cards_notion.py <trabalho> <cards_cfg.json>
cards_cfg.json: {"1": {"pauta", "origem", "drive", "thumbA", "thumbB", "previa"?}, ...}; precisa de render/<arquivo> - YOUTUBE.txt e crivo.json.
"""
import json, re, sys, unicodedata
from pathlib import Path
trab = Path(sys.argv[1]); cfg = json.load(open(sys.argv[2], encoding="utf-8"))
p = json.load(open(trab / "plano.json", encoding="utf-8"))
crivo = json.load(open(trab / "crivo.json", encoding="utf-8"))
def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")[:120]
for e in p["episodios"]:
    n = str(e["n"]); c = cfg[n]; mt = e["meta"]; cr = crivo[n]
    yt = (trab / "render" / f"{e['arquivo']} - YOUTUBE.txt").read_text(encoding="utf-8")
    desc = yt.split("DESCRIÇÃO (copiar e colar):")[1].split("=" * 60)[1].strip()
    coment = yt.split("COMENTÁRIO FIXADO:")[1].split("TAGS:")[0].strip()
    tags = yt.split("TAGS:")[1].split("QR na tela")[0].strip()
    qr = "QR na tela" + yt.split("QR na tela")[1].split("\n")[0]
    dur = json.load(open(trab / "render" / f"{e['arquivo']}.json", encoding="utf-8"))["duracao_total"]
    mm = f"{int(dur // 60)}:{int(dur % 60):02d}"
    sala = f"https://claude.ai/artifact/HAcqomJqf9NXRNtyYbkX6v#{slug(c['pauta'])}"
    notas = ", ".join(f"{k.replace('_', ' ')} {v}" for k, v in cr["notas"].items())
    fatos = "\n".join(f"  - {f}" for f in mt.get("fatos", [])) or "  - Nenhum."
    md = f"""## Tema
{mt['resumo']}

{c['origem']} · episódio {n} · {mm}

## Crivo do Claude: {cr['media']} / 10 · {cr['veredito']}
{cr['porque']}

Notas por ponto: {notas}

## Assistir e corrigir
- {c.get('previa', 'Episódio completo para assistir')}, com notas no tempo do vídeo: [Sala de Revisão]({sala})
- Arquivo final em alta (o que sobe no YouTube): [Drive]({c['drive']})
- Para pedir correção: deixe as notas na Sala de Revisão (ou escreva no campo CORREÇÕES (Claude)) e mova o card para Correções (Claude).

## Título (recomendado primeiro, os outros para o teste A/B do YouTube)
""" + "\n".join(f"{i}. {t}" for i, t in enumerate(mt["titulos"][:3], 1)) + f"""

## Thumbs (anexadas em MATERIAL FINALIZADO)
- **A · ROI Legacy:** {c['thumbA']}
- **B · Palestrante:** {c['thumbB']}

Subir as duas no "Testar e comparar" do YouTube.

## Descrição (copiar e colar)
```plain text
{desc}
```

## Comentário fixado
```plain text
{coment}
```

## Tags
```plain text
{tags}
```

## Outros
- {qr}
- Legenda para subir no YouTube: {e['arquivo']}.srt (na pasta do Drive)
- Dados falados que pedem cuidado:
{fatos}
"""
    (trab / f"notion_card_ep{int(n):02d}.md").write_text(md, encoding="utf-8")
print("ok")
