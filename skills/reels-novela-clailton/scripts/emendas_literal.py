"""Palavra repetida nas emendas do corte, ANTES do render (pedido do usuário, 28/09/2026: "tem
momentos que ele repete palavras e fica cortado e errado").

O Whisper normal engole gaguejo ("sem... sem GPS" vira "sem GPS"), tanto no bruto quanto na
retranscrição do corte, e o encurtamento de pausa emenda os dois pedaços: a repetição fica colada
na emenda e ninguém vê. Aqui cada emenda do áudio cortado é transcrita em modo LITERAL, numa janela
curta (+-2 s), e toda palavra/expressão repetida que atravessa a emenda vira problema, com o ajuste
de decupagem sugerido (INICIO/PARTE/FIM/SAI), já no bruto.

Entrada (<trabalho>/): corte.json, audio_corte16k.wav, transcricao.json, decupagem_frases.json
Saída: emendas_literal.txt (uma linha por emenda + problemas + ajustes sugeridos)
Repetição intencional (anáfora) aprovada na revisão: <trabalho>/repeticoes_ok.txt, uma por linha.
Uso: python emendas_literal.py <trabalho>        código 0 = limpo, 3 = repetição na emenda
"""
from __future__ import annotations

import re
import sys
import unicodedata
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import ler_json, whisper  # noqa: E402

JANELA = 2.0
# exemplos neutros: exemplo tirado do próprio vídeo induz o Whisper a "ouvir" a frase
PROMPT = ("Transcrição literal, palavra por palavra, mantendo repetições, gaguejos e hesitações: "
          "é... é, eu, eu acho que, que o... o problema.")


def norm(t: str) -> str:
    """Minúscula sem pontuação, COM acento: "E é exatamente" não é repetição ("e" x "é")."""
    t = unicodedata.normalize("NFC", t.lower())
    return re.sub(r"[^\wà-ü%]", "", t).replace("_", "")


def fragmentos(segs: list[dict], pal: list[dict]) -> list[tuple[int, dict]]:
    """Gaguejo que a transcrição não vê: pedaço curto (<= 0,7 s) cuja voz cabe numa palavra só do
    bruto, e essa MESMA palavra continua no pedaço seguinte. O Whisper esticou a palavra por cima da
    pausa ("E... E você sabe" virou um "E" de 0,86 s); o corte encurtou a pausa e emendou os dois."""
    out = []
    for k in range(len(segs) - 1):
        s, prox = segs[k], segs[k + 1]
        a, b = s.get("fala_in", s["src_in"]), s.get("fala_out", s["src_out"])
        if b - a > 0.7:
            continue
        dentro = [w for w in pal if min(w["fim"], b) - max(w["inicio"], a) > 0.02]
        if len(dentro) == 1 and dentro[0]["fim"] > prox["src_in"] + 0.03:
            out.append((k, dentro[0]))
    return out


def para_bruto(segs: list[dict], k: int, t: float) -> float:
    s = segs[k]
    return s["src_in"] + (t - s["dst_in"])


def sugestao(t1b: float, t2b: float, pal: list[dict], frases: list[dict]) -> str:
    """Ajuste de decupagem que tira do bruto o trecho [t1b, t2b): a 1ª ocorrência sai, a fala
    retoma na 2ª (o recomeço é o que vale)."""
    def frase_de(t: float) -> int | None:
        for n, f in enumerate(frases):
            if f.get("estado") == "FICA" and pal[f["i0"]]["inicio"] - 0.3 <= t <= pal[f["i1"]]["fim"] + 0.3:
                return n
        return None
    n1, n2 = frase_de(t1b + 0.02), frase_de(t2b + 0.02)
    desde = round(t2b - 0.05, 2)
    ret = next((w["i"] for w in pal if w["fim"] > t2b + 0.03), pal[-1]["i"])       # palavra que contém o recomeço
    antes = max((w["i"] for w in pal if w["fim"] <= t1b + 0.05), default=-1)       # última palavra inteira antes
    if n2 is None:
        return f"# ? repetição em {t1b:.2f}-{t2b:.2f}s do bruto: confira à mão"
    f2 = frases[n2]
    if n1 == n2:
        if antes < f2["i0"]:
            return f"INICIO {n2} {ret}@{desde}"
        return f"PARTE {n2} {antes} {ret}@{desde}"
    if n1 is not None:                                   # a 1ª ocorrência é o rabo da frase anterior
        f1 = frases[n1]
        return f"SAI {n1}" if antes < f1["i0"] else f"FIM {n1} {antes}"
    return f"INICIO {n2} {ret}@{desde}"


def main() -> None:
    T = Path(sys.argv[1])
    corte = ler_json(T / "corte.json")
    segs = corte["segmentos"]
    pal = ler_json(T / "transcricao.json")["palavras"]
    frases = ler_json(T / "decupagem_frases.json") if (T / "decupagem_frases.json").exists() else []
    arq_ok = T / "repeticoes_ok.txt"
    ok = {norm(x.split("#")[0]) for x in arq_ok.read_text(encoding="utf-8").splitlines()} if arq_ok.exists() else set()
    ok.discard("")
    with wave.open(str(T / "audio_corte16k.wav"), "rb") as w_:
        aud = np.frombuffer(w_.readframes(w_.getnframes()), np.int16).astype(np.float32) / 32768
    dur = len(aud) / 16000
    model = whisper()
    linhas, problemas, ajustes = [], [], []
    for k in range(1, len(segs)):
        e = segs[k]["dst_in"]
        t0 = max(0.0, e - JANELA)
        sg, _ = model.transcribe(aud[int(t0 * 16000):int(min(dur, e + JANELA) * 16000)], language="pt",
                                 word_timestamps=True, vad_filter=False, condition_on_previous_text=False,
                                 initial_prompt=PROMPT)
        ws = [(norm(w.word), t0 + w.start, t0 + w.end) for s in sg for w in (s.words or []) if norm(w.word)]
        lit = [x for x, _, _ in ws]
        marca = next((j for j, (_, a, _) in enumerate(ws) if a >= e - 0.08), len(ws))
        linhas.append(f"emenda {k:02d} {e:7.2f}s: " + " ".join(lit[:marca]) + " | " + " ".join(lit[marca:]))
        achou = False
        for n in (3, 2, 1):
            for a in range(len(ws) - 2 * n + 1):
                if lit[a:a + n] != lit[a + n:a + 2 * n] or achou:
                    continue
                b = a + n                                   # 1ª ocorrência: a..b-1 ; 2ª: b..b+n-1
                if not (ws[a][1] < e + 0.05 and ws[b][1] >= e - 0.25):
                    continue                                # não atravessa esta emenda
                rep = " ".join(lit[a:b])
                if rep.replace(" ", "") in {o.replace(" ", "") for o in ok}:
                    linhas.append(f"      (repetição '{rep}' aprovada em repeticoes_ok.txt)")
                    achou = True
                    continue
                t1b = para_bruto(segs, k - 1 if ws[a][1] < e else k, ws[a][1])
                t2b = para_bruto(segs, k if ws[b][1] >= e - 0.08 else k - 1, ws[b][1])
                sug = sugestao(t1b, t2b, pal, frases) if frases else "# sem decupagem_frases.json"
                problemas.append(f"emenda {k:02d} ({e:.2f}s): '{rep}' repetido | bruto {t1b:.2f}s e {t2b:.2f}s")
                ajustes.append(f"{sug}   # '{rep}' repetido na emenda {k:02d} ({e:.2f}s do corte)")
                achou = True
    for k, w in fragmentos(segs, pal):
        prox = segs[k + 1]
        rep = norm(w["texto"])
        if rep in ok:
            continue
        t2b = prox.get("fala_in", prox["src_in"])
        sug = sugestao(segs[k].get("fala_in", segs[k]["src_in"]), t2b, pal, frases) if frases else "#"
        problemas.append(f"emenda {k + 1:02d} ({prox['dst_in']:.2f}s): pedaço de {segs[k]['frames'] / 29.97:.2f}s "
                         f"dentro de '{w['texto']}' (i={w['i']}), que continua no pedaço seguinte: gaguejo")
        ajustes.append(f"{sug}   # gaguejo '{w['texto']}' antes da emenda {k + 1:02d} ({prox['dst_in']:.2f}s do corte)")
    txt = linhas + ["", f"# {len(problemas)} repetição(ões) atravessando emenda"] + problemas
    if ajustes:
        txt += ["", "# ajustes sugeridos (confira e junte ao decupagem_ajustes.txt; depois --aplicar e montar de novo):"]
        txt += ajustes
    (T / "emendas_literal.txt").write_text("\n".join(txt) + "\n", encoding="utf-8")
    print("\n".join(txt[-(len(problemas) + len(ajustes) + 4):]))
    sys.exit(3 if problemas else 0)


if __name__ == "__main__":
    main()
