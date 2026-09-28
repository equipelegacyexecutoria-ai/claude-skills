"""Legenda no estilo da referência (vídeo "Você já viu alguém reclamar da empresa...").

Caixa-alta branca, SF Pro Text Black, sombra suave sem contorno, blocos de 1-4
palavras em até duas linhas (linha pequena + linha grande de destaque), palavras
entrando uma a uma com desfoque -> nítido e leve deslize.

Uso:
  python legenda_ref.py --transcript 02-transcript.json --timeline tl.json --out clip.ass
  (tl.json = lista de {source_start, source_end, order} na ordem do clipe)
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from PIL import ImageFont

W, H = 1080, 1920
FONT_FILE = Path(__file__).parent / "fonts" / "SF-Pro-Text-Black.otf"
FONT_NAME = "SFProText-Black"
BIG, SMALL = 100, 54            # tamanho ASS (calibrado contra a referência)
PIL_SCALE = 0.83               # em do PIL = tamanho ASS * 0,83 (medido: 692/835 px)
MAX_W = 860                    # largura máxima da linha, dentro da zona segura
Y_CENTER = 1150                # centro do bloco (~60% da altura: peito, abaixo do rosto)
GAP = 20

# Sombra, de trás para a frente. alpha em hex ASS (00 = opaco, FF = invisível).
#  v1 (aprovada na 1a entrega): uma cópia preta muito desfocada -> sumia em fundo claro
#  v2: halo difuso (escurece só o entorno das letras) + sombra de contato curta (desenha a borda)
SOMBRAS = {
    "v1": [dict(dx=0, dy=6, bord=0, blur=14, alpha="6E")],
    "v2": [dict(dx=0, dy=2, bord=6, blur=16, alpha="A8"),     # halo: ~34% de opacidade
           dict(dx=1, dy=4, bord=1, blur=3, alpha="60")],     # contato: ~62%
    "v3": [dict(dx=0, dy=3, bord=10, blur=22, alpha="8C"),    # halo mais largo: ~45%
           dict(dx=1, dy=4, bord=2, blur=4, alpha="48")],     # contato: ~72%
}
SOMBRA = SOMBRAS["v3"]   # aprovada pelo usuário em 2026-09-26 (teste no corte 10, blusa branca)

STOP = set("""a o as os e é de da do das dos em no na nos nas um uma uns umas que se
pra pro pras pros por para com sem ao aos à às ou mas mais eu tu ele ela eles elas
me te lhe nos vos isso isto aquilo esse essa este esta já né lá aí cara então assim
tá tô ter tem foi ser vai vou não sim só também até quando como onde porque porquê""".split())

# correções de reconhecimento de fala: só entram depois de conferidas no áudio
# (Whisper no clipe renderizado — assets/conferencia-palavras.json)
FIX: dict[str, str] = {"EMEX": "AMEX"}

# correções por clipe: (texto na transcrição, texto certo). Casam a sequência de
# palavras normalizada; a primeira palavra herda o tempo, as demais o tempo da última.
CORRECOES: dict[str, list[tuple[str, str]]] = {
    # números por extenso -> algarismo (mesmas palavras ditas, só formatação)
    "02": [("vinte, vinte e cinco milhões", "20, 25 milhões"), ("vinte e cinco milhões", "25 milhões")],
    "10": [("duzentos e trinta e nove por cento,", "239%,"),
           ("Destocagem,", "Estocagem,")],                      # Whisper; "destocagem" não existe
    # Whisper ouviu diferente e a leitura dele fecha a frase
    "05": [("Só porque a gente mais vê", "Só que o que a gente mais vê")],
    "06": [("minha mudança de vida foi gigante", "A minha mudança de vida foi gigante"),  # "A" audível no corte
           ("todo estressado", "toda estressada")],             # ela fala de si: "uma mãe doida"
}

DESTAQUES: dict[str, list[str]] = {
    k: v for k, v in json.loads((Path(__file__).parent / "destaques.json").read_text(encoding="utf-8")).items()
    if not k.startswith("_")
}
# não podem terminar bloco/linha: pedem a palavra seguinte
ARTIGO_PREP = set("""a o as os da do das dos de em no na nos nas com pra pro por um uma ao à e que
eu tu ele ela eles elas se me te lhe meu minha meus minhas teu tua seu sua nosso nossa
esse essa este esta aquele aquela isso muito mais tão bem todo toda""".split())


def _n(t: str) -> str:
    return re.sub(r"[^\wÀ-ÿ%]", "", t.lower())


def corrigir(ws: list[dict], slug: str) -> list[dict]:
    regras = [r for k, rs in CORRECOES.items() if slug.startswith(k) for r in rs]
    for antigo, novo in regras:
        alvo = [_n(x) for x in antigo.split()]
        i = 0
        while i + len(alvo) <= len(ws):
            if [_n(w["text"]) for w in ws[i:i + len(alvo)]] == alvo:
                novas = novo.split()
                s0, e0 = ws[i]["start"], ws[i + len(alvo) - 1]["end"]
                step = (e0 - s0) / max(1, len(novas))
                repl = [{"text": t, "start": s0 + k * step, "end": s0 + (k + 1) * step} for k, t in enumerate(novas)]
                ws = ws[:i] + repl + ws[i + len(alvo):]
                i += len(repl)
            else:
                i += 1
    return ws


def load_words(transcript: dict) -> list[dict]:
    return [w for s in transcript["segments"] for w in s.get("words", [])]


def map_words(words: list[dict], timeline: list[dict]) -> list[dict]:
    """Palavras no tempo do clipe. Palavra que fica menos da metade dentro do
    trecho é descartada: é vizinha cortada, não fala do clipe."""
    out, offset = [], 0.0
    for part in sorted(timeline, key=lambda p: p.get("order", 0)):
        ps, pe = float(part["source_start"]), float(part["source_end"])
        for w in words:
            s, e = float(w["start"]), float(w["end"])
            ov = min(e, pe) - max(s, ps)
            if ov <= 0 or ov < 0.7 * (e - s):     # rabo de palavra cortada na borda não vira legenda
                continue
            out.append({"text": str(w["word"]).strip(),
                        "start": offset + max(s, ps) - ps,
                        "end": offset + min(e, pe) - ps})
        offset += pe - ps
    out.sort(key=lambda w: w["start"])
    return merge_tokens(out)


def merge_tokens(ws: list[dict]) -> list[dict]:
    """'100' + '%' -> '100%'; 'guarda' + '-corpo' -> 'guarda-corpo'."""
    res: list[dict] = []
    for w in ws:
        t = w["text"]
        if res and (t in {"%", "%,", "%.", "%?"} or t.startswith("-")):
            res[-1]["text"] += t
            res[-1]["end"] = w["end"]
            continue
        if not t:
            continue
        res.append(dict(w))
    return res


def clean(t: str) -> str:
    t = t.upper().replace("...", "").replace("…", "")
    core = re.sub(r"[^\wÀ-ÿ%-]", "", t)
    if core in FIX:
        t = t.replace(core, FIX[core])
    return t


def weight(t: str) -> float:
    core = re.sub(r"[^\wÀ-ÿ%]", "", t).lower()
    if not core:
        return 0
    if re.search(r"\d", core):
        return 4
    if core in STOP:
        return 0
    if len(core) >= 7:
        return 2
    if len(core) >= 4:
        return 1
    return 0.3


def marcar_destaques(ws: list[dict], slug: str) -> None:
    """Marca w['dest']=True nas palavras dos termos de destaque do clipe e em números."""
    termos = DESTAQUES.get(slug[:2], [])
    toks = [_n(w["text"]) for w in ws]
    for w, t in zip(ws, toks):
        w["dest"] = bool(re.search(r"\d", t))
        w["termo"] = None
    tid = 0
    for termo in termos:
        alvo = [_n(x) for x in termo.split()]
        for i in range(len(toks) - len(alvo) + 1):
            if toks[i:i + len(alvo)] == alvo and all(ws[k]["termo"] is None for k in range(i, i + len(alvo))):
                tid += 1
                for k in range(i, i + len(alvo)):
                    ws[k]["dest"] = True
                    ws[k]["termo"] = tid if len(alvo) > 1 else None


def _pendura(t: str) -> bool:
    """Palavra que não pode ficar no fim de bloco/linha (artigo, preposição, conectivo)."""
    return _n(t) in ARTIGO_PREP and not re.search(r"[.,?!;:]$", t)


def chunk(ws: list[dict]) -> list[list[dict]]:
    chunks, cur = [], []
    for w in ws:
        if cur:
            prev = cur[-1]
            txt = " ".join(x["text"] for x in cur + [w])
            mesmo_termo = prev.get("termo") is not None and prev.get("termo") == w.get("termo")
            forte = (w["start"] - prev["end"] > 0.35
                     or re.search(r"[.?!…:;]$", prev["text"])
                     or (prev["text"].endswith(",") and len(cur) >= 2 and len(_n(prev["text"])) > 3))
            # bloco de 1-2 palavras pode durar mais (ex.: "239%" substitui 7 palavras faladas)
            cheio = len(cur) >= 4 or len(txt) > 24 or w["end"] - cur[0]["start"] > (3.0 if len(cur) <= 1 else 2.2)
            if mesmo_termo and len(cur) < 6 and len(txt) <= 30:
                cheio = False                      # termo de destaque não se parte
            if forte or cheio:
                carry = []
                if not forte:
                    # não deixar palavra pendurada nem partir termo de destaque: leva o rabo pro próximo
                    while len(cur) - len(carry) >= 2:
                        last = cur[-1 - len(carry)]
                        nxt = cur[len(cur) - len(carry)] if carry else w
                        partindo = last.get("termo") is not None and last.get("termo") == nxt.get("termo")
                        if not (_pendura(last["text"]) or partindo):
                            break
                        carry.insert(0, last)
                        if len(carry) >= 3:
                            break
                keep = cur[:len(cur) - len(carry)]
                chunks.append(keep)
                cur = carry
        cur.append(w)
    if cur:
        chunks.append(cur)
    return chunks


_font_cache: dict[int, ImageFont.FreeTypeFont] = {}


def text_w(text: str, size: int) -> float:
    s = max(8, round(size * PIL_SCALE))
    if s not in _font_cache:
        _font_cache[s] = ImageFont.truetype(str(FONT_FILE), s)
    return _font_cache[s].getlength(text)


def strip_end(text: str) -> str:
    return re.sub(r"[,.;:]+$", "", text)


def _quebra_bonus(words: list[str], k: int) -> float:
    """Qualidade sintática de quebrar a linha antes de words[k]."""
    b = 0.0
    if re.search(r"[.,?!;:]$", words[k - 1]):
        b += 1.5
    if _pendura(words[k - 1]):
        b -= 2.5                      # "ASSIM, A / GENTE" — artigo pendurado
    return b


def layout(words: list[str], dest: list[bool] | None = None) -> list[tuple[list[int], int]]:
    """Devolve linhas como (índices das palavras, tamanho).

    Linha GRANDE só para termo de destaque do clipe ou número (como na referência,
    onde o destaque cai na ideia forte); o resto fica na linha pequena."""
    n = len(words)
    dest = dest or [False] * n
    total = " ".join(words)
    nd = sum(dest)
    if nd == 0:
        if text_w(total, SMALL) <= MAX_W * 0.8 or n == 1:
            return [(list(range(n)), SMALL)]
        k = max(range(1, n), key=lambda k: _quebra_bonus(words, k) - 0.1 * abs(k - n / 2))
        return [(list(range(k)), SMALL), (list(range(k, n)), SMALL)]
    # bloco inteiro é destaque e curto: uma linha grande só
    if nd == n and len(total) <= 16:
        return [(list(range(n)), fit(list(range(n)), words, BIG))]
    best = None
    for k in range(1, n):
        a, b = list(range(k)), list(range(k, n))
        da, db = sum(dest[i] for i in a), sum(dest[i] for i in b)
        big, small = (b, a) if db >= da else (a, b)
        dbig, dsmall = max(da, db), min(da, db)
        big_txt = " ".join(words[i] for i in big)
        score = (2.0 * dbig - 1.5 * dsmall
                 - 1.2 * sum(1 for i in big if not dest[i])       # palavra comum na linha grande
                 + _quebra_bonus(words, k)
                 - 0.25 * max(0, len(big_txt) - 16))
        if best is None or score > best[0]:
            best = (score, a, b, big)
    _, a, b, big = best
    return [(a, fit(a, words, BIG if a is big else SMALL)), (b, fit(b, words, BIG if b is big else SMALL))]


def fit(idx: list[int], words: list[str], size: int) -> int:
    t = " ".join(words[i] for i in idx)
    while size > SMALL and text_w(t, size) > MAX_W:
        size -= 2
    return size


def ass_time(t: float) -> str:
    t = max(0.0, t)
    cs = int(round(t * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def line_heights(size: int) -> float:
    return size * 0.62   # altura de caixa-alta medida (62 px em tamanho 100)


def build(ws: list[dict], clip_end: float, slug: str = "") -> list[str]:
    events = []
    marcar_destaques(ws, slug)
    chunks = chunk(ws)
    for ci, ch in enumerate(chunks):
        texts = [clean(w["text"]) for w in ch]
        texts[-1] = strip_end(texts[-1]) or texts[-1]
        start = ch[0]["start"]
        nxt = chunks[ci + 1][0]["start"] if ci + 1 < len(chunks) else clip_end
        end = min(nxt, ch[-1]["end"] + 0.7)
        end = max(end, start + 0.45) if ci + 1 >= len(chunks) else min(max(end, start + 0.45), nxt)
        lines = layout(texts, [bool(w.get("dest")) for w in ch])
        hs = [line_heights(sz) for _, sz in lines]
        total = sum(hs) + GAP * (len(lines) - 1)
        y = Y_CENTER - total / 2
        for (idx, size), hgt in zip(lines, hs):
            cy = y + hgt / 2
            y += hgt + GAP
            l_start = ch[idx[0]]["start"]
            spans_txt = []
            spans_sh = {k: [] for k in range(len(SOMBRA))}
            for i in idx:
                r = int(round((ch[i]["start"] - l_start) * 1000))
                word = texts[i]
                if i != idx[-1]:
                    word += " "
                spans_txt.append(f"{{\\alpha&HFF&\\blur7\\t({r},{r + 170},\\alpha&H00&\\blur0)}}{word}")
                for k, sh in enumerate(SOMBRA):
                    spans_sh[k].append(f"{{\\alpha&HFF&\\t({r},{r + 170},\\alpha&H{sh['alpha']}&)}}{word}")
            y0 = cy - 14
            t0, t1 = ass_time(l_start), ass_time(end)
            for k, sh in enumerate(SOMBRA):
                dx, dy = sh["dx"], sh["dy"]
                head_sh = (f"\\an5\\fs{size}\\move({540 + dx},{y0 + dy:.0f},{540 + dx},{cy + dy:.0f},0,220)"
                           f"\\1c&H000000&\\3c&H000000&\\bord{sh['bord']}\\blur{sh['blur']}")
                events.append(f"Dialogue: {k},{t0},{t1},Cap,,0,0,0,,{{{head_sh}}}" + "".join(spans_sh[k]))
            head = f"\\an5\\fs{size}\\move(540,{y0:.0f},540,{cy:.0f},0,220)"
            events.append(f"Dialogue: {len(SOMBRA)},{t0},{t1},Cap,,0,0,0,,{{{head}}}" + "".join(spans_txt))
    return events


HEADER = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{FONT_NAME},{BIG},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,-1,0,1,0,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--transcript", required=True)
    ap.add_argument("--timeline", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--words-out")
    a = ap.parse_args()
    tr = json.loads(Path(a.transcript).read_text(encoding="utf-8"))
    tl = json.loads(Path(a.timeline).read_text(encoding="utf-8"))
    ws = map_words(load_words(tr), tl)
    clip_end = sum(float(p["source_end"]) - float(p["source_start"]) for p in tl)
    ev = build(ws, clip_end)
    Path(a.out).write_text(HEADER + "\n".join(ev) + "\n", encoding="utf-8")
    if a.words_out:
        Path(a.words_out).write_text(json.dumps(ws, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"palavras": len(ws), "blocos": len(chunk(ws)), "eventos": len(ev)}))


if __name__ == "__main__":
    main()
