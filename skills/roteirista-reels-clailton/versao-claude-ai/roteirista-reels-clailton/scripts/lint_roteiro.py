"""Revisão automática de um roteiro de reel do Clailton (novela ou tela dividida).

Lê a seção "## ROTEIRO FALADO" do arquivo (ou o texto inteiro, se não houver a seção) e imprime:
  FALHA  reprova (código de saída 1)
  AVISO  não reprova, mas tira ponto de voz
  INFO   números de referência (palavras, segundos, possessivos)

Uso:
  python lint_roteiro.py roteiro.md --formato novela
  python lint_roteiro.py roteiro.md --formato tela --objetivo conversao --referencia fala-do-outro.txt
"""
import argparse
import re
import sys

SECOES_FALA = ["ROTEIRO FALADO", "Roteiro falado", "Fala"]
SECOES_REF = ["Fala", "ROTEIRO FALADO", "Transcrição"]


def secao(txt, titulos):
    for t in titulos:
        m = re.search(r"(?ms)^##\s*" + re.escape(t) + r"\s*$(.*?)(?=^##\s|\Z)", txt)
        if m:
            return m.group(1)
    return txt


def limpa(t):
    t = re.sub(r"(?m)^\s*>\s?", "", t)
    t = re.sub(r"\[(VERIFICAR|BANCO|CONFERIDO)[^\]]*\]", "", t)
    return re.sub(r"\s+", " ", t).strip()


def palavras(t):
    return [w for w in re.sub(r"[^\w\s]", " ", t.lower()).split() if w]


def ngramas(w, n=8):
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}


def cnt(t, pat):
    return len(re.findall(pat, t, flags=re.IGNORECASE))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivo")
    ap.add_argument("--formato", required=True, choices=["novela", "tela", "tela_dividida"])
    ap.add_argument("--objetivo", default="alcance", choices=["alcance", "envio", "salvamento", "conversao"])
    ap.add_argument("--referencia", help="arquivo com a fala do vídeo de outro criador")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    formato = "novela" if a.formato == "novela" else "tela"

    bruto = open(a.arquivo, encoding="utf-8").read()
    fala = limpa(secao(bruto, SECOES_FALA))
    frases = [f for f in re.split(r"(?<=[\.\!\?…])\s+", fala) if f.strip()]
    w = palavras(fala)
    falhas, avisos, infos = [], [], []

    # FALHAS
    primeira = frases[0] if frases else ""
    if re.search(r"\btalvez\b|\bpode ser\b|\bàs vezes\b", primeira, re.I):
        falhas.append(f"1ª frase com hesitação ('talvez', 'pode ser', 'às vezes'): \"{primeira}\"")
    if re.match(r"\s*(oi|olá|ola|fala|e aí|bom dia|boa tarde|boa noite)\b", fala, re.I) or re.search(
            r"hoje eu (quero|vou) (falar|conversar)", fala[:120], re.I):
        falhas.append('Abertura de apresentador ("oi gente", "fala pessoal", "hoje eu quero falar sobre").')
    trav_fala, trav = cnt(fala, "[—–]"), cnt(bruto, "[—–]")
    if trav_fala:
        falhas.append(f"Travessão na fala: {trav_fala}. Troque por ponto, vírgula ou dois-pontos.")
    elif trav:
        avisos.append(f"Travessão fora da fala: {trav}. Não afeta a gravação, mas evite.")
    if re.search(r"\bPMEs?\b", fala):
        falhas.append("'PME' na fala. Diga 'dono de empresa', 'empresário' ou o porte em número.")
    if re.search(r"\bfa(z|ça|zer)\s+(a|as)\s+contas?\s+comigo\b|\bvamos (fazer|às) (a |as )?contas?\b", fala, re.I):
        falhas.append("Conta no vídeo ('faz a conta comigo'): o Clailton vetou em 16/10/2026.")
    elif re.search(r"\bfa(z|ça|zendo|zer)\s+(a|as)\s+contas?\b|\bmultiplica\b|\bvezes\s+\d|\d+\s*%.*\d+\s*%", fala, re.I):
        avisos.append("Parece haver conta no vídeo (multiplicação, 'faz as contas', porcentagens encadeadas). O Clailton vetou conta em 16/10/2026; confira.")

    nao_e = re.findall(r"\b(?:o problema|o erro|a quest[ãa]o)?\s*não (?:é|está) (?:só |apenas |sobre )?[^.!?;:]{1,60}?[,;.]\s*(?:mas |e sim )?(?:é|está)\b", fala, re.I)
    if nao_e:
        falhas.append(f"'Não é X, é Y' ({len(nao_e)}): vetado pelo usuário em 28/10/2026. Diga direto o que é.")

    link_bio = cnt(fala, r"link\s+(da|na)\s+bio")
    kw_pat = (r"\b(comenta|comente|digita|digite|escreve|escreva)\b(\s+aqui:?)?(\s+embaixo:?)?(\s+a\s+palavra)?"
              r"\s+[\"“']?(\w+)[\"”']?(?=\s*[\.\!,;]|\s*$|\s+(aqui|que\s+eu|e\s+eu|embaixo|no\s+coment|nos\s+coment|pra\s+mim|para\s+mim))")
    kw = [m.group(5) for m in re.finditer(kw_pat, fala, re.I)
          if not re.fullmatch(r"o|a|os|as|qual|quais|como|se|sua|tua|seu|teu|aí|ai", m.group(5), re.I)]
    if a.objetivo != "conversao":
        if link_bio:
            falhas.append(f"'Link da bio' com objetivo {a.objetivo} (7 roteiros assim, nenhum passou de 150 mil).")
        if kw:
            falhas.append(f"CTA de palavra-chave ({', '.join(kw)}) com objetivo {a.objetivo}. Só em conversão.")
        envio = cnt(fala, r"\b(manda|mande|envia|envie|compartilha|compartilhe) (este|esse) v[íi]deo")
        if envio and a.objetivo != "envio":
            avisos.append(f"Pedido de envio ('manda este vídeo') com objetivo {a.objetivo}. Use --objetivo envio ou tire a linha.")
        if a.objetivo == "envio" and not envio:
            avisos.append("Objetivo envio sem o pedido 'Manda este vídeo para [quem]...'.")
        if a.objetivo == "salvamento" and not re.search(r"salva", " ".join(frases[:3]), re.I):
            avisos.append("Objetivo salvamento sem 'Já salva esse vídeo' no começo.")
    else:
        if not kw and not link_bio:
            avisos.append("Objetivo conversão sem CTA (palavra-chave ou link da bio do quiz), depois do fecho.")
        if len(kw) > 1:
            avisos.append(f"Mais de 1 CTA de palavra-chave ({len(kw)}). Use um só.")
    if a.referencia:
        ref = limpa(secao(open(a.referencia, encoding="utf-8").read(), SECOES_REF))
        ref_set = ngramas(palavras(ref))
        copiadas = [" ".join(w[i:i + 8]) for i in range(len(w) - 7) if " ".join(w[i:i + 8]) in ref_set]
        if copiadas:
            falhas.append(f"Sequência de 8+ palavras copiada da referência ({len(copiadas)}): \"{copiadas[0]}\"...")

    # AVISOS
    n = len(w)
    seg = round(n / 2.8)
    alvo = (170, 260) if formato == "novela" else (280, 460)
    if n < alvo[0] or n > alvo[1]:
        avisos.append(f"Tamanho: {n} palavras (~{seg} s). Faixa dos vencedores de {formato}: {alvo[0]} a {alvo[1]}.")
    longas = [f for f in frases if len(palavras(f)) > 18]
    if len(longas) > 2:
        ex = " | ".join((f.strip()[:70] + "…") if len(f.strip()) > 70 else f.strip() for f in longas[:2])
        avisos.append(f"{len(longas)} frases com mais de 18 palavras (ex.: {ex}).")
    pra, ta = cnt(fala, r"\bpra\b"), cnt(fala, r"\btá\b(?!\s*\?)")
    ce, to = cnt(fala, r"\bcê\b"), cnt(fala, r"\btô\b")
    if pra + ta + ce + to:
        avisos.append(f"Fora da voz medida: 'pra' {pra} · 'tá' {ta} · 'cê' {ce} · 'tô' {to} (ele fala 'para' e 'está').")
    teu, seu = cnt(fala, r"\b(teu|tua|teus|tuas)\b"), cnt(fala, r"\b(seu|sua|seus|suas)\b")
    infos.append(f"Possessivo: teu/tua {teu} · seu/sua {seu} (voz medida: ~3 teu para 1 seu).")
    if seu > teu and seu >= 3:
        avisos.append(f"Possessivo 'seu/sua' ({seu}) acima de 'teu/tua' ({teu}). Prefira 'teu/tua'.")
    ultima = frases[-1] if frases else ""
    fecho = ultima
    if len(frases) >= 2 and re.search(r"comenta|comente|digite|digita|me siga|link|salva|envie|manda", ultima, re.I):
        fecho = frases[-2]
    if len(palavras(fecho)) > 15:
        avisos.append(f"Fecho com {len(palavras(fecho))} palavras (alvo até 15): \"{fecho.strip()}\"")
    if re.search(r"\btalvez\b|\bpode ser\b", fecho, re.I):
        avisos.append('Fecho com "talvez/pode ser": enfraquece a frase citável.')
    pa, os_ = cnt(fala, r"preste atenção|presta atenção"), cnt(fala, r"olha só")
    max_pa = 1 if formato == "novela" else 2
    if pa > max_pa:
        avisos.append(f"'Preste atenção' {pa} vezes (máximo {max_pa}).")
    if os_ > 2:
        avisos.append(f"'Olha só' {os_} vezes.")
    palavrao = cnt(fala, r"\bmaldit\w*|\bporcaria\b|\bdroga\b|\bmerda\b|\bcaralho\b|\bporra\b")
    if palavrao > 1:
        avisos.append(f"Palavrão {palavrao} vezes (máximo 1, leve).")
    if cnt(fala, r"\bmerda\b|\bcaralho\b|\bporra\b"):
        avisos.append("Palavrão pesado: fora da voz dele.")
    if re.search(r"\bme sig(a|am)\b", fala, re.I):
        avisos.append("'Me siga' falado: a edição já põe na tela. Tire, salvo no teste da assinatura.")
    if formato == "novela" and re.search(r"(nessas|essas|nesta|esta|essa|nessa) imagens?|olha (essa|esta) imagem|na tela aqui", fala, re.I):
        avisos.append('Novela não tem imagens de apoio: tire as menções a "imagem".')
    if formato == "tela":
        mapa = secao(bruto, ["MAPA DE ÂNCORAS", "MAPA DE ANCORAS"])
        if mapa == bruto:
            avisos.append('Tela dividida sem a seção "## MAPA DE ÂNCORAS".')
        else:
            linhas = [l for l in mapa.splitlines() if re.match(r"^\|\s*\d+", l)]
            if len(linhas) < 3:
                avisos.append(f"Mapa de âncoras com {len(linhas)} linha(s); o mínimo é 3.")

    print(f"INFO: {n} palavras · ~{seg} s a 2,8 palavras/s · {len(frases)} frases")
    for x in infos:
        print("INFO:", x)
    for x in falhas:
        print("FALHA:", x)
    for x in avisos:
        print("AVISO:", x)
    print(f"RESULTADO: {'REPROVADO' if falhas else 'OK'} · FALHA {len(falhas)} · AVISO {len(avisos)}")
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
