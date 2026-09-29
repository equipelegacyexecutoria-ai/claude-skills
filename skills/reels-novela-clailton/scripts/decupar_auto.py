"""Proposta AUTOMÁTICA de decupagem (economiza o agente): acha as tomadas e fica com a última
completa de cada frase. A IA só confere a listagem anotada (uma passada, barata).

Regras (as mesmas que o decupador humano/IA usava no vídeo 1):
- frase = palavras entre pausas >= 0,45 s, partida também em ponto final/interrogação;
- tomada repetida: uma frase cujo começo reaparece numa frase posterior (até 90 s depois)
  é substituída pela posterior (a última tomada vence); vale também para frase que é o
  começo de outra (falso começo: "a torcida contra começa... a torcida contra começa quando...");
- continuação de tomada descartada: frase curta logo depois de uma descartada, cujo texto
  aparece em seguida dentro da tomada que a substituiu, também sai ("..., mais água.");
- fala para a equipe ("vamos lá de novo", "calma", "muito bem", "gravando"...) sai;
- palavra sem energia de voz ([sem voz] = invenção do Whisper) sai;
- frase curta e isolada (<= 8 palavras, pausa > 2 s dos dois lados) que não é tomada de nada
  fica marcada como DÚVIDA e fora do corte até a revisão (pode ser conversa com a equipe);
- passada LITERAL (Whisper com prompt de gaguejo) em cada frase que fica: repetição escondida
  ("dá aquela... dá aquela") vira aviso na proposta.

Saída (<trabalho>/): decupagem.json (proposta) + decupagem_frases.json + decupagem_proposta.txt
Uso: python decupar_auto.py <trabalho> [--sem-literal]
     python decupar_auto.py <trabalho> --aplicar <trabalho>/decupagem_ajustes.txt
         (linhas SAI n | FICA n | INICIO n i | FIM n i; regrava decupagem.json)
"""
from __future__ import annotations

import difflib
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import gravar_json, ler_json  # noqa: E402

PAUSA_FRASE = 0.45
JANELA_TOMADA = 90.0
META = ["vamos la", "de novo", "mais uma vez", "calma", "muito bem", "gravando", "gravou", "corta", "pode ir",
        "valeu", "obrigado", "obrigada", "ok", "beleza", "de novo ai", "vou de novo", "espera",
        "pera", "desculpa", "errei", "repete", "repetir", "deu certo", "ficou bom", "tudo certo"]
SIMIL = 0.70
SIMIL_CONTEUDO = 0.50
# palavras de função: frases PARALELAS do roteiro ("não adianta você X se você tem o hábito de Y")
# repetem essas; tomada refeita repete as de CONTEÚDO (dinheiro x livro não é retomada)
FUNCAO = set("""o a os as um uma uns umas de do da dos das em no na nos nas por pra pro para com sem e ou que se
ao aos voce voces eu ele ela eles elas nos me te lhe seu sua meu minha tu teu tua isso isto esse essa este esta
aquele aquela aquilo nao mais muito tem ter tenho foi ser e esta estao so ja entao""".split())
PROMPT_LITERAL = ("Transcrição literal, palavra por palavra, mantendo repetições, gaguejos e hesitações: "
                  "é... é, eu, eu acho que, que o... o problema.")
MULETAS = {"e", "entao", "ne", "tipo", "assim", "ai", "eh", "hum", "ah"}


def norm(t: str) -> str:
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9%]", "", t)


def frases(pal: list[dict]) -> list[list[dict]]:
    out, cur = [], []
    for k, w in enumerate(pal):
        if w.get("sem_voz"):
            if cur:
                out.append(cur)
                cur = []
            continue
        if cur and (w["inicio"] - cur[-1]["fim"] >= PAUSA_FRASE
                    or (re.search(r"[.?!]$", cur[-1]["texto"]) and w["inicio"] - cur[-1]["fim"] >= 0.25)):
            out.append(cur)
            cur = []
        cur.append(w)
    if cur:
        out.append(cur)
    return out


def toks(fr: list[dict]) -> list[str]:
    return [n for n in (norm(w["texto"]) for w in fr) if n]


def parecido(a: list[str], b: list[str]) -> float:
    return difflib.SequenceMatcher(a=a, b=b, autojunk=False).ratio()


def palavra_tempo(v: str) -> tuple[int, float | None]:
    """'290' -> (290, None); '290@156.30' -> (290, 156.3): a fala retomada não começa antes de t."""
    i, _, t = v.partition("@")
    return int(i), (float(t) if t else None)


def aplicar(trabalho: Path, ajustes: Path) -> None:
    """Aplica a revisão (curta) sobre a proposta ORIGINAL (reaplicar não acumula). Linhas:
         SAI 2      FICA 7      FIM 29 320
         INICIO 25 290[@156.30]      frase começa na palavra 290 (e a fala não antes de 156,30 s)
         PARTE 12 140 144[@80.12]    falso começo no meio: fica 140 e antes, retoma na 144 (@t)
    (n = frase da decupagem_proposta.txt; os números são índices de palavra do bruto)."""
    fr = ler_json(trabalho / "decupagem_frases.json")
    for f in fr:
        f["estado"] = "FICA" if f["proposta"] == "FICA" else "SAI"
        f["i0"], f["i1"] = f.setdefault("i0_prop", f["i0"]), f.setdefault("i1_prop", f["i1"])
        f.pop("desde", None)
        f.pop("parte", None)
    for ln in ajustes.read_text(encoding="utf-8").splitlines():
        p = ln.split("#")[0].split()
        if not p:
            continue
        cmd, n = p[0].upper(), int(p[1])
        if cmd in ("SAI", "FICA"):
            fr[n]["estado"] = cmd
        elif cmd == "INICIO":
            fr[n]["i0"], t = palavra_tempo(p[2])
            if t is not None:
                fr[n]["desde"] = t
        elif cmd == "FIM":
            fr[n]["i1"] = int(p[2])
        elif cmd == "PARTE":
            j, t = palavra_tempo(p[3])
            fr[n]["parte"] = {"ate": int(p[2]), "retoma": j, "desde": t}
        else:
            raise SystemExit(f"ajuste desconhecido: {ln}")
    gravar_json(trabalho / "decupagem_frases.json", fr)
    gravar_json(trabalho / "decupagem.json", {"trechos": trechos_de(fr), "origem": "decupar_auto.py + revisão"})
    print(f"ok: {sum(f['estado'] == 'FICA' for f in fr)} frases ficam -> decupagem.json")


def trechos_de(fr: list[dict]) -> list[dict]:
    out = []
    for n, f in enumerate(fr):
        if f["estado"] != "FICA":
            continue
        pedacos = [(f["i0"], f["i1"], f.get("desde"))]
        if f.get("parte"):
            pt = f["parte"]
            pedacos = [(f["i0"], pt["ate"], f.get("desde")), (pt["retoma"], f["i1"], pt["desde"])]
        for k, (a, b, desde) in enumerate(pedacos):
            if k == 0 and desde is None and out and out[-1]["_n"] == n - 1 and out[-1]["ate"] + 1 == a:
                out[-1]["ate"], out[-1]["_n"] = b, n
            else:
                out.append({"de": a, "ate": b, "_n": n} | ({"desde": desde} if desde is not None else {}))
    for t in out:
        t.pop("_n")
    return out


def main() -> None:
    trabalho = Path(sys.argv[1])
    if "--aplicar" in sys.argv:
        aplicar(trabalho, Path(sys.argv[sys.argv.index("--aplicar") + 1]))
        return
    tr = ler_json(trabalho / "transcricao.json")
    pal = tr["palavras"]
    fs = frases(pal)
    tk = [toks(f) for f in fs]
    estado = [["FICA", ""] for _ in fs]

    # fala para a equipe / invenção
    for i, t in enumerate(tk):
        txt = " ".join(t)
        if len(t) <= 6 and any(re.search(rf"\b{m}\b", txt) for m in META):
            estado[i] = ["SAI", "fala para a equipe"]

    # tomadas: a última completa vence (a tomada nova pode vir partida em várias frases)
    def seguida(j: int, n: int) -> list[str]:
        out, k = [], j
        while k < len(fs) and len(out) < n:
            if k > j and fs[k][0]["inicio"] - fs[k - 1][-1]["fim"] > 1.5:
                break
            out += [x for x in tk[k] if x not in MULETAS] or tk[k]
            k += 1
        return out

    for i, a in enumerate(tk):
        if estado[i][0] == "SAI" or not a:
            continue
        a_sem = [x for x in a if x not in MULETAS] or a
        n = len(a_sem)
        for j in range(i + 1, len(fs)):
            if fs[j][0]["inicio"] - fs[i][-1]["fim"] > JANELA_TOMADA:
                break
            if estado[j][0] == "SAI" or not tk[j]:
                continue
            b = seguida(j, max(n, 8) + 2)
            if n <= 2:                                   # curtíssima: só se a repetição é logo em seguida
                if j == i + 1 and b[:n] == a_sem:
                    estado[i] = ["SAI", f"repetida em seguida (frase {j})"]
                break
            if not b or b[0] != a_sem[0]:                # tomada nova começa pela mesma palavra
                continue
            m = min(n, 8)
            ac = [x for x in a_sem if x not in FUNCAO][:6]
            bc = [x for x in b if x not in FUNCAO][:len(ac) + 2]
            conteudo = parecido(ac, bc) if ac else 1.0
            # tropeço curto ("dá aquela impressão de água" -> "...de agora vai"): 4 primeiras palavras iguais
            exato4 = n >= 4 and a_sem[:4] == b[:4] and any(x not in FUNCAO for x in a_sem[:4])
            semelhante = (max(parecido(a_sem[:m], b[:L]) for L in (m, m + 1, m + 2)) >= SIMIL
                          and conteudo >= SIMIL_CONTEUDO)
            # frase PARALELA (não é tomada): completa, começa igual e segue diferente — "Você sabe
            # exatamente onde ela está hoje?" x "E você sabe exatamente onde você quer chegar?"
            # (28/09/2026: a proposta tirou a 1ª e o corte ficou sem sentido)
            pref = next((p for p in range(min(n, len(b))) if a_sem[p] != b[p]), min(n, len(b)))
            resto_a, resto_b = a_sem[pref:], b[pref:pref + len(a_sem) - pref + 2]
            ult = fs[i][-1]["texto"].strip()
            completa = bool(re.search(r"[.?!]$", ult)) and not re.search(r"(\.\.\.|…)$", ult)   # "..." = parou no meio
            if (exato4 and not semelhante and completa and len(resto_a) >= 2 and a_sem[0] not in resto_a
                    and parecido(resto_a, resto_b) < 0.34):
                estado[i] = ["DÚVIDA", f"começa igual à frase {j} e segue diferente: frase paralela? (se for, FICA)"]
                break
            if exato4 or semelhante:
                estado[i] = ["SAI", f"tomada refeita adiante (frase {j})"]
                # continuação curta da tomada descartada ("..., mais água.")
                k = i + 1
                while k < j and len(tk[k]) <= 4 and fs[k][0]["inicio"] - fs[k - 1][-1]["fim"] < 1.2:
                    alvo = tk[j] + (tk[j + 1] if j + 1 < len(fs) else [])
                    if " ".join(tk[k]) in " ".join(alvo):
                        estado[k] = ["SAI", f"continuação da tomada descartada (refeita na frase {j})"]
                    k += 1
                break

    # frase curta e isolada que sobrou: dúvida (conversa com a equipe?)
    for i, t in enumerate(tk):
        if estado[i][0] != "FICA" or len(t) > 8:
            continue
        antes = fs[i][0]["inicio"] - (fs[i - 1][-1]["fim"] if i else 0)
        depois = (fs[i + 1][0]["inicio"] if i + 1 < len(fs) else 1e9) - fs[i][-1]["fim"]
        if antes > 2.0 and depois > 2.0:
            estado[i] = ["DÚVIDA", "frase curta isolada: conversa com a equipe?"]

    # passada LITERAL no bruto (GPU): o Whisper normal esconde repetição dentro de uma palavra
    # esticada ("dá aquela... dá aquela impressão"); aqui ela aparece e vira aviso
    literal, escondido = {}, {}
    if "--sem-literal" not in sys.argv:
        import wave
        import numpy as np
        from comum import whisper
        with wave.open(str(trabalho / "audio16k.wav"), "rb") as w_:
            aud = np.frombuffer(w_.readframes(w_.getnframes()), np.int16).astype(np.float32) / 32768
        model = whisper()
        for i, f in enumerate(fs):
            if estado[i][0] == "SAI":
                continue
            a_, b_ = int(max(0.0, f[0]["inicio"] - 0.4) * 16000), int((f[-1]["fim"] + 0.3) * 16000)
            sg, _ = model.transcribe(aud[a_:b_], language="pt", condition_on_previous_text=False,
                                     initial_prompt=PROMPT_LITERAL)
            lt = [norm(x) for s in sg for x in s.text.split() if norm(x)]
            reps = [" ".join(lt[k:k + n]) for n in (1, 2, 3) for k in range(len(lt) - 2 * n + 1)
                    if lt[k:k + n] == lt[k + n:k + 2 * n]]
            if reps or len(lt) > len(tk[i]) + 1:
                literal[i] = (" ".join(lt), sorted(set(reps)))

        # FALSO COMEÇO atrás de pausa escondida: silêncio >= 0,25 s dentro do intervalo de uma
        # palavra (o Whisper estica a palavra por cima). "parar... Parar alguma coisa" saiu como
        # "Parar alguma coisa" e nem a passada literal da frase inteira viu. Transcreve cada lado.
        from montar_corte import HOP, Energia
        en = Energia(aud, 16000)

        def fala(t0: float, t1: float) -> tuple[list[str], list[float]]:
            t0 = max(0.0, t0)
            sg, _ = model.transcribe(aud[int(t0 * 16000):int(t1 * 16000)], language="pt", word_timestamps=True,
                                     condition_on_previous_text=False, initial_prompt=PROMPT_LITERAL)
            ws = [(norm(w.word), t0 + w.start) for s in sg for w in (s.words or []) if norm(w.word)]
            return [w for w, _ in ws], [t for _, t in ws]

        for i, f in enumerate(fs):
            if estado[i][0] == "SAI":
                continue
            a0, b0 = int(f[0]["inicio"] / HOP), min(len(en.db), int(f[-1]["fim"] / HOP))
            voz = en.db[a0:b0] >= en.voz
            k = 0
            while k < len(voz):
                if voz[k]:
                    k += 1
                    continue
                ks = k
                while k < len(voz) and not voz[k]:
                    k += 1
                t_s, t_e = (a0 + ks) * HOP, (a0 + k) * HOP
                if t_e - t_s < 0.25 or voz[:ks].sum() < 15 or voz[k:].sum() < 15:
                    continue                       # curto ou na ponta da frase (1ª palavra esticada)
                if any(min(f[j + 1]["inicio"], t_e) - max(f[j]["fim"], t_s) >= 0.5 * (t_e - t_s)
                       for j in range(len(f) - 1)):
                    continue                       # já é vão entre palavras: o corte encurta sozinho
                (antes, t_antes), (depois, _) = fala(f[0]["inicio"] - 0.1, t_s + 0.05), fala(t_e - 0.05, f[-1]["fim"] + 0.3)
                # recomeço: a 1ª palavra (de conteúdo) de depois já estava no fim de antes ("parar al-...
                # Parar alguma"), ou um par de palavras se repete ("eu acho... eu acho que")
                q = None
                if depois and len(depois[0]) >= 4 and depois[0] in antes[-3:]:
                    q = len(antes) - 1 - antes[::-1].index(depois[0])
                else:
                    q = next((len(antes) - 4 + r for r in range(3) if len(antes) >= 4 - r
                              and antes[len(antes) - 4 + r:len(antes) - 2 + r] == depois[:2]), None)
                    q = None if q is None or q < 0 else q
                if q is None and depois and 0 < len(antes) <= 3 and antes[0] == depois[0]:
                    q = 0                          # começou a frase, parou em <= 3 palavras e recomeçou
                    #                                com a mesma palavra, mesmo curta ("Mas que... mas talvez")
                if q is None:
                    continue
                # retoma na palavra (do Whisper) que termina depois do silêncio: ela contém o recomeço
                prox = next((w["i"] for w in f if w["fim"] > t_e), f[-1]["i"])
                desde = round(t_e - 0.05, 2)
                n_rep = sum(norm(w["texto"]) == antes[q] for w in f)
                if n_rep >= 3:                     # "só continue... continue trabalhando, continue aparecendo":
                    sug = None                     # anáfora (repetição intencional), não é tropeço
                elif q <= 1:                       # a frase começa pelo falso começo
                    sug = f"INICIO {i} {prox}@{desde}"
                else:                              # no meio: fica o que vem antes do falso começo
                    a = min(f, key=lambda w: abs(w["inicio"] - t_antes[q]))
                    sug = (f"PARTE {i} {a['i'] - 1} {prox}@{desde}" if abs(a["inicio"] - t_antes[q]) <= 0.3
                           and a["i"] > f[0]["i"] else f"PARTE {i} ? {prox}@{desde}")
                escondido.setdefault(i, []).append((t_s, t_e, " ".join(antes[-6:]), " ".join(depois[:8]), sug,
                                                    antes[q], n_rep))

    # trechos: frases que ficam (DÚVIDA fica de fora até a revisão), fundidas quando contíguas
    fr = [{"i0": f[0]["i"], "i1": f[-1]["i"], "i0_prop": f[0]["i"], "i1_prop": f[-1]["i"],
           "estado": "FICA" if estado[i][0] == "FICA" else "SAI",
           "proposta": estado[i][0], "motivo": estado[i][1]} for i, f in enumerate(fs)]
    gravar_json(trabalho / "decupagem_frases.json", fr)
    gravar_json(trabalho / "decupagem.json", {"trechos": trechos_de(fr), "origem": "decupar_auto.py (proposta)"})

    linhas = [f"# proposta automática: {sum(e[0] == 'FICA' for e in estado)} frases ficam, "
              f"{sum(e[0] == 'SAI' for e in estado)} saem, {sum(e[0] == 'DÚVIDA' for e in estado)} dúvidas",
              "# frase n | [i0-i1] tempo | ESTADO (motivo) | texto", ""]
    for i, f in enumerate(fs):
        est, mot = estado[i]
        txt = " ".join(w["texto"] for w in f)
        linhas.append(f"{i:3d} [{f[0]['i']:04d}-{f[-1]['i']:04d}] {f[0]['inicio']:6.1f}s  {est:6s}"
                      f"{' (' + mot + ')' if mot else ''} | {txt}")
        if i in literal:
            lt, reps = literal[i]
            linhas.append(f"      ⚠ bruto literal: \"{lt}\"" + (f"  — repetição: {', '.join(reps)}" if reps else ""))
        for t_s, t_e, antes, depois, sug, palavra, n_rep in escondido.get(i, []):
            if sug is None:
                linhas.append(f"      ⚠ repetição com pausa: \"...{antes}\" | silêncio {t_s:.2f}-{t_e:.2f}s | "
                              f"\"{depois}...\"  — \"{palavra}\" aparece {n_rep}x na frase: parece anáfora "
                              f"(intencional), não corte sem conferir")
            else:
                linhas.append(f"      ⚠ falso começo escondido: \"...{antes}\" | silêncio {t_s:.2f}-{t_e:.2f}s | "
                              f"\"{depois}...\"  — provável: {sug}")
    linhas += ["", "# roteiro proposto:", " ".join(" ".join(w["texto"] for w in f)
                                                 for i, f in enumerate(fs) if estado[i][0] == "FICA")]
    (trabalho / "decupagem_proposta.txt").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print("\n".join(linhas[:2]))


if __name__ == "__main__":
    main()
