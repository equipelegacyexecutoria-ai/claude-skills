"""Monta o pacote de publicação de cada episódio (o que vai no YouTube), a partir do plano + render.

No plano.json, cada episódio ganha "meta":
  "meta": {
    "titulos": ["recomendado", "alternativa 2", "alternativa 3"],      # ≤ 70 caracteres (máx. 100)
    "thumbs": ["TEXTO 1", "TEXTO 2", "TEXTO 3"],                     # 2–4 palavras, sem repetir o título
    "resumo": "1–2 frases com a palavra-chave e a promessa (vai logo abaixo do link)",
    "bullets": ["o que a pessoa leva 1", "..."],                     # 3–5
    "capitulos": [["abertura", "Título do 1º capítulo"], ["00:26:04", "Outro capítulo"], ...],  # tempo DA AULA
    "tags": ["..."], "hashtags": ["#gestaoempresarial", "..."],      # 5–10 tags, 3–5 hashtags
    "fatos": ["dado dito na aula que está impreciso -> como está certo"]   # opcional, vai no relatório
  }

Gera <trabalho>/<pasta>/<arquivo> - YOUTUBE.txt (copiar e colar) e confere: tamanho do título, 2–4 palavras
na thumb, capítulos (00:00, ≥ 3, crescentes, ≥ 10 s), link com UTM na 1ª linha.

Uso: python metadados.py <trabalho> [--pasta render]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import hms, ler_json, seg  # noqa: E402
from render_episodio import montar  # noqa: E402

SERIE = "Legado Empresarial"
RODAPE = """NO QUE NÓS ACREDITAMOS?
Acreditamos em negócios extraordinários, que dependam de pessoas comuns, e não em negócios comuns que dependam de pessoas extraordinárias.
Para isso, desenvolvemos uma metodologia exclusiva, para que empresas possam funcionar como um relógio suíço, isto é, como um sistema previsível, mesmo sem a presença constante de seu dono.

Conecte-se com a gente!
Instagram: https://www.instagram.com/legacyexecutoria
Facebook: https://www.facebook.com/legacyexecutoria
Linkedin: https://www.linkedin.com/company/legacyexecutoria"""


def mmss(t: float) -> str:
    t = int(round(t))
    h, r = divmod(t, 3600)
    m, s = divmod(r, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def capitulos(trab: Path, ep: dict, problemas: list[str]) -> list[tuple[float, str]]:
    m = montar(trab, ep)
    out = []
    for quando, titulo in ep["meta"]["capitulos"]:
        if quando == "abertura":
            out.append((0.0, titulo))
            continue
        x = m["conv_corpo"](seg(quando))
        if x is None:   # caiu numa pausa cortada: pega o trecho seguinte
            x = min((m["conv_corpo"](a) for a, _ in m["segs"][m["n_ab"]:] if a >= seg(quando)), default=None)
        if x is None:
            problemas.append(f"capítulo '{titulo}' ({quando}) fora do episódio")
            continue
        out.append((x + m["dur_ab"], titulo))
    if not out or out[0][0] != 0.0:
        problemas.append("1º capítulo precisa ser 00:00")
    if len(out) < 3:
        problemas.append("mínimo 3 capítulos")
    for (a, _), (b, t2) in zip(out, out[1:]):
        if b - a < 10:
            problemas.append(f"capítulo '{t2}' a menos de 10 s do anterior")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("trabalho")
    ap.add_argument("--pasta", default="render")
    a = ap.parse_args()
    trab = Path(a.trabalho)
    plano = ler_json(trab / "plano.json")
    for ep in plano["episodios"]:
        if "meta" not in ep:
            continue
        mt, problemas = ep["meta"], []
        info = ler_json(trab / a.pasta / f"{ep['arquivo']}.json")
        for t in mt["titulos"]:
            if len(t) > 100:
                problemas.append(f"título com {len(t)} caracteres (máx. 100): {t}")
            elif len(t) > 70:
                problemas.append(f"aviso: título com {len(t)} caracteres (ideal ≤ 70): {t}")
        for t in mt["thumbs"]:
            if not 2 <= len(t.split()) <= 4:
                problemas.append(f"texto de thumb com {len(t.split())} palavras (2–4): {t}")
        caps = capitulos(trab, ep, problemas)
        link = info["url_descricao"]
        desc = [f"🔹 AGENDE SUA SESSÃO ESTRATÉGICA GRATUITA: {link}", "", mt["resumo"], "",
                "Neste episódio:"] + [f"• {b}" for b in mt["bullets"]] + [
                "", "Na sessão estratégica, um especialista da Legacy olha a sua empresa com você e mostra por onde "
                "começar. É gratuita e sem compromisso: " + link, "", "CAPÍTULOS"] + [
                f"{mmss(t)} {nome}" for t, nome in caps] + ["", RODAPE, "", " ".join(mt["hashtags"])]
        descricao = "\n".join(desc)
        if len(descricao) > 5000:
            problemas.append(f"descrição com {len(descricao)} caracteres (máx. 5000)")
        comentario = (f"📌 Quer aplicar isso na sua empresa? Agende sua sessão estratégica gratuita com a Legacy: "
                      f"{info['url_comentario']}")
        ctas = ", ".join(f"{mmss(p['t'])} ({p['canto']})" for p in info["card"]["posicoes"])
        txt = [f"EPISÓDIO {ep['n']} · {mmss(info['duracao'])} · arquivo: {ep['arquivo']}.mp4", "",
               "TÍTULO (recomendado):", mt["titulos"][0], "", "Outros títulos (para o teste A/B do YouTube):"] + [
               f"- {t}" for t in mt["titulos"][1:]] + [
               "", "TEXTO DA THUMB (recomendado):", mt["thumbs"][0], "", "Outros textos de thumb:"] + [
               f"- {t}" for t in mt["thumbs"][1:]] + [
               "", "=" * 60, "DESCRIÇÃO (copiar e colar):", "=" * 60, descricao, "=" * 60, "",
               "COMENTÁRIO FIXADO:", comentario, "", "TAGS:", ", ".join(mt["tags"]), "",
               f"QR na tela (30 s cada): {ctas}", f"Link do QR: {info['url_qr']}",
               "Legenda para subir no YouTube (Português): " + f"{ep['arquivo']}.srt"]
        if mt.get("fatos"):
            txt += ["", "ATENÇÃO, dados falados na aula que estão imprecisos (não citar no título/descrição):"] + [
                f"- {f}" for f in mt["fatos"]]
        saida = trab / a.pasta / f"{ep['arquivo']} - YOUTUBE.txt"
        saida.write_text("\n".join(txt) + "\n", encoding="utf-8")
        print(f"ok: {saida.name}")
        for p in problemas:
            print(f"   {'AVISO' if p.startswith('aviso') else 'PROBLEMA'}: {p}")


if __name__ == "__main__":
    main()
