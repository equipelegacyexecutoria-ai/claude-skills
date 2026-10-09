"""Reenquadramento dos trechos de vídeo (B-roll) no layout: decide o recorte que APARECE no reel.

O recorte "cover" 9:16 de uma cena 16:9 mostra só 32% da largura; no centro, cena aberta vira um pedaço
que não se entende (O Lobo de Wall Street no 1º teste). A equipe recorta no assunto. Por trecho em HD:

  1. cortes de cena em todos os quadros (miniatura 64 px) -> planos do trecho
  2. ponto de entrada dentro da margem baixada: a duração usada sem plano de menos de MIN_PLANO
     colado no começo/fim (senão a cena "pisca")
  3. por plano, 1-2 amostras: rostos (YuNet) e os recortes dos DOIS formatos — vertical (tela cheia
     9:16, 9 posições) e faixa (topo/dividida 1080x768, 5 posições) — ao longo da folga
  4. CLIP em cada recorte com dois textos — a AÇÃO (descrição 'en:') e a IDENTIDADE da cena (a busca,
     com o nome do filme/personagem: cultura pop tem que ser reconhecível) —, qualidade CLIP-IQA
     (boa/ruim, nítida/borrada, clara/escura) e rosto inteiro (cortar rosto ao meio perde nota)
  5. posição por plano -> 'recortes' {vertical|faixa: [{t, p}]} que o render segue; nota do candidato
     pelo que aparece no formato do item; LARGA = no vertical a cena perde o sentido (o personagem
     principal fica fora ou o recorte vale bem menos que a cena inteira): troque o candidato ou passe o
     item para `dividida` (o recorte da faixa já está pronto); ESCURO = pouca luz no recorte

Uso direto (teste): python reenquadrar_td.py <trecho.mp4> <layout> "<ação em inglês>" ["<busca>"]
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from midia_util import area_util, rostos  # noqa: E402
from td_comum import EMENDA, W  # noqa: E402

ASPECTOS = {"vertical": 9 / 16, "faixa": W / EMENDA}   # tela cheia 9:16 · topo/dividida 1080x768
N_POS = {"vertical": 9, "faixa": 5}                     # posições ao longo da folga (0 = esq./topo, 1 = dir./baixo)
MIN_PLANO = 1.0         # s: plano (entre cortes de cena) menor que isso no começo/fim do uso = pisca (09/10: era 0,6)
MIN_INTERNO = 1.0       # s: plano inteiro no meio do uso menor que isso = corte rápido demais (edição de fã)
MARGEM = 1.0            # s: margem baixada antes e depois da janela (buscar_td) para achar a entrada
LARG = 640              # px das amostras analisadas
CINZA = (123, 117, 104)  # média do CLIP: fundo neutro no quadrado
ESCURO = 55             # luz média (0-255) abaixo disso = cena escura no recorte


def aspecto_do_layout(layout: str) -> str:
    return "faixa" if layout in ("topo", "dividida") else "vertical"


def _fps(arq: str) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=avg_frame_rate",
                        "-of", "csv=p=0", arq], capture_output=True, text=True).stdout.strip()
    try:
        a, b = r.split("/")
        return float(a) / float(b) if float(b) else 30.0
    except ValueError:
        return 30.0


def cortes(arq: str, area: tuple[int, int, int, int]) -> tuple[list[float], float, int]:
    """Tempos (s) dos cortes de cena, fps e nº de quadros. Diferença média entre quadros vizinhos
    (64 px, cinza) bem acima da mediana = corte."""
    bx, by, bw, bh = area
    fps = _fps(arq)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", arq, "-vf", f"crop={bw}:{bh}:{bx}:{by},scale=64:36,format=gray",
                          "-fps_mode", "passthrough", "-f", "rawvideo", "-"], capture_output=True).stdout
    q = np.frombuffer(raw, np.uint8).reshape(-1, 36, 64).astype(np.float32)
    if len(q) < 2:
        return [], fps, len(q)
    d = np.abs(q[1:] - q[:-1]).mean((1, 2))
    lim = max(22.0, 4 * float(np.median(d)) + 8)
    idx = [k + 1 for k in range(len(d)) if d[k] > lim]
    return [k / fps for k in idx], fps, len(q)


def _pena_uso(cs: list[float], e: float, d: float) -> float:
    """Quanto um uso de d segundos a partir de e "pisca": plano curto nas pontas ou no meio."""
    pts = [e] + [c for c in cs if e < c < e + d] + [e + d]
    lens = np.diff(pts)
    if len(lens) < 2:
        return 0.0
    return (max(0.0, MIN_PLANO - lens[0]) + max(0.0, MIN_PLANO - lens[-1])
            + sum(max(0.0, MIN_INTERNO - v) for v in lens[1:-1]))


def escolher_entrada(cs: list[float], dur_clip: float, duracoes: list[float], entrada0: float) -> float:
    """Início comum a TODOS os usos da mídia (o item e as repetições 'igual', que começam no mesmo ponto):
    nenhum uso termina/começa num pedaço de cena de menos de MIN_PLANO; o mais perto da janela do CLIP."""
    lo, hi = 0.0, max(0.0, dur_clip - max(duracoes))
    melhor, custo_m = min(max(entrada0, lo), hi), 1e9
    for e in np.arange(lo, hi + 1e-6, 1 / 30):
        custo = 20 * sum(_pena_uso(cs, e, d) for d in duracoes) + abs(e - entrada0) * 0.6
        if custo < custo_m:
            melhor, custo_m = float(e), custo
    return melhor


def _quadros(arq: str, area, tempos: list[float]) -> list[np.ndarray | None]:
    bx, by, bw, bh = area
    out = []
    for t in tempos:
        r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", arq, "-frames:v", "1", "-vf",
                            f"crop={bw}:{bh}:{bx}:{by},scale={LARG}:-2", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           capture_output=True).stdout
        h = len(r) // (LARG * 3)
        out.append(np.frombuffer(r, np.uint8).reshape(h, LARG, 3) if h else None)
    return out


def _quadrado(im: np.ndarray, lado: int = 224) -> Image.Image:
    """Recorte inteiro dentro de um quadrado (o CLIP recorta o centro: sem isso veria só o meio do 9:16)."""
    p = Image.fromarray(im)
    s = lado / max(p.size)
    p = p.resize((max(1, round(p.width * s)), max(1, round(p.height * s))), Image.BICUBIC)
    q = Image.new("RGB", (lado, lado), CINZA)
    q.paste(p, ((lado - p.width) // 2, (lado - p.height) // 2))
    return q


def _geo(w: int, h: int, alvo: float) -> dict:
    if w / h > alvo:
        return {"cw": h * alvo, "ch": float(h), "eixo": "x", "folga": w - h * alvo, "w": w, "h": h}
    return {"cw": float(w), "ch": w / alvo, "eixo": "y", "folga": h - w / alvo, "w": w, "h": h}


def analisar(arq: str, layout: str, duracoes: list[float] | float, entrada0: float, pasta: Path,
             tag: str) -> dict | None:
    """Prepara os recortes candidatos (imagens para o CLIP) de um trecho. `duracoes` = de cada uso da
    mídia (o item e as repetições). Devolve None se não der."""
    try:
        area = area_util(arq)
        cs, fps, nq = cortes(arq, area)
        dur_clip = nq / fps
        if dur_clip < 0.3:
            return None
        duracoes = [min(d, dur_clip) for d in (duracoes if isinstance(duracoes, list) else [duracoes])]
        dur_uso = max(duracoes)
        e = escolher_entrada(cs, dur_clip, duracoes, entrada0)
        # pisca: algum uso com pedaço de cena curto, ou corte a cada < 0,9 s (edição de fã / trailer)
        dentro = [c for c in cs if e < c < e + dur_uso]
        pisca = any(_pena_uso(cs, e, d) > 0.05 for d in duracoes) or len(dentro) / max(dur_uso, 0.1) > 1 / 0.9
        pts = [e] + [c for c in cs if e < c < e + dur_uso] + [e + dur_uso]
        planos = [(a, b) for a, b in zip(pts, pts[1:]) if b - a > 0.05]
        tempos, dono = [], []
        for pi, (a, b) in enumerate(planos):
            for f in ((0.5,) if b - a < 1.2 else (0.3, 0.7)):
                tempos.append(a + (b - a) * f)
                dono.append(pi)
        qs = _quadros(arq, area, tempos)
        if not qs or any(x is None for x in qs):
            return None
        h, w = qs[0].shape[:2]
        geo = {k: _geo(w, h, a) for k, a in ASPECTOS.items()}
        pos = {k: ([j / (N_POS[k] - 1) for j in range(N_POS[k])] if g["folga"] > 0.03 * max(w, h) else [0.5])
               for k, g in geo.items()}
        pasta.mkdir(parents=True, exist_ok=True)
        imagens, mapa, amostras, luz = [], [], [], {}
        for si, (im, pi) in enumerate(zip(qs, dono)):
            lum = (0.2126 * im[..., 0] + 0.7152 * im[..., 1] + 0.0722 * im[..., 2]).astype(np.float32)
            for asp, g in geo.items():
                for pk, p in enumerate(pos[asp]):
                    x0 = p * g["folga"] if g["eixo"] == "x" else 0.0
                    y0 = p * g["folga"] if g["eixo"] == "y" else 0.0
                    sl = (slice(int(y0), int(y0 + g["ch"])), slice(int(x0), int(x0 + g["cw"])))
                    luz[(si, asp, pk)] = float(lum[sl].mean())
                    f = pasta / f"{tag}_{si}_{asp[0]}{pk}.jpg"
                    _quadrado(im[sl]).save(f, quality=92)
                    imagens.append(str(f))
                    mapa.append((si, asp, pk))
            f = pasta / f"{tag}_{si}_inteira.jpg"                  # a cena inteira: referência para LARGA
            _quadrado(im).save(f, quality=92)
            imagens.append(str(f))
            mapa.append((si, "inteira", 0))
            amostras.append({"plano": pi, "t": tempos[si], "rostos": rostos(Image.fromarray(im))})
        thumb = pasta.parent / f"{Path(arq).stem}_thumb.jpg"
        meio = max(range(len(planos)), key=lambda k: planos[k][1] - planos[k][0])
        Image.fromarray(qs[next(si for si, pi in enumerate(dono) if pi == meio)]).save(thumb, quality=90)
        return {"arquivo": arq, "entrada": round(e, 3), "planos": planos, "amostras": amostras, "imagens": imagens,
                "mapa": mapa, "pos": pos, "geo": geo, "luz": luz, "thumb": str(thumb), "dur_uso": dur_uso,
                "cortes": cs, "layout": layout, "pisca": bool(pisca)}
    except Exception as ex:  # noqa: BLE001
        print(f"   reenquadrar {Path(arq).name}: {ex!r}"[:160], flush=True)
        return None


def _dentro(f: list, p: float, g: dict) -> float:
    """Fração do rosto f que fica dentro do recorte na posição p."""
    if g["eixo"] == "x":
        a, b, c0, tam = f[0] * g["w"], (f[0] + f[2]) * g["w"], p * g["folga"], g["cw"]
    else:
        a, b, c0, tam = f[1] * g["h"], (f[1] + f[3]) * g["h"], p * g["folga"], g["ch"]
    return max(0.0, min(b, c0 + tam) - max(a, c0)) / max(1e-6, b - a)


def _rosto(fs: list, p: float, g: dict) -> float:
    """Rosto grande inteiro no recorte ganha; rosto grande cortado ao meio perde."""
    if not fs:
        return 0.0
    grande = max(f[2] * f[3] for f in fs)
    nota = 0.0
    for f in fs:
        if f[2] * f[3] < 0.45 * grande or f[2] < 0.03:
            continue
        d = _dentro(f, p, g)
        nota += -3.0 if 0.2 < d < 0.85 else (1.5 if d >= 0.85 else 0.0)
    return max(-6.0, min(3.0, nota))


def _fora(fs: list, p: float, g: dict) -> bool:
    """O rosto principal (grande) ficou FORA do recorte?"""
    if not fs:
        return False
    f = max(fs, key=lambda x: x[2] * x[3])
    return f[2] * f[3] >= 0.012 and _dentro(f, p, g) < 0.2


def _decidir_aspecto(an: dict, val: dict, asp: str) -> dict | None:
    g, pos = an["geo"][asp], an["pos"][asp]
    recorte, vis, qual, luz, inteira, pesos, fora = [], [], [], [], [], [], []
    for pi, (a, b) in enumerate(an["planos"]):
        sis = [si for si, am in enumerate(an["amostras"]) if am["plano"] == pi]
        if not sis:
            continue
        notas = []
        for pk, p in enumerate(pos):
            s = float(np.mean([val[(si, asp, pk)][0] for si in sis]))
            q = float(np.mean([val[(si, asp, pk)][1] for si in sis]))
            r = float(np.mean([_rosto(an["amostras"][si]["rostos"], p, g) for si in sis]))
            notas.append((s + 4.0 * (q - 0.5) + r, s, q, pk))
        _, s, q, pk = max(notas)
        recorte.append({"t": round(a - an["entrada"], 3), "p": pos[pk]})
        vis.append(s)
        qual.append(q)
        luz.append(float(np.mean([an["luz"][(si, asp, pk)] for si in sis])))
        inteira.append(float(np.mean([val[(si, "inteira", 0)][0] for si in sis])))
        fora.append(float(np.mean([_fora(an["amostras"][si]["rostos"], pos[pk], g) for si in sis])) > 0.5)
        pesos.append(b - a)
    if not recorte:
        return None
    pw = np.array(pesos) / sum(pesos)
    r = {"visivel": float(np.dot(pw, vis)), "iqa": float(np.dot(pw, qual)), "luz": float(np.dot(pw, luz)),
         "inteira": float(np.dot(pw, inteira)), "sem_rosto": bool(np.dot(pw, fora) > 0.5)}
    r["larga"] = bool((r["inteira"] - r["visivel"] > 1.5 or r["sem_rosto"]) and g["folga"] > 0)
    r["recorte"] = [recorte[0]] + [x for k, x in enumerate(recorte[1:], 1) if x["p"] != recorte[k - 1]["p"]]
    longo = max(range(len(recorte)), key=lambda k: pesos[k])
    p = recorte[longo]["p"]
    r["foco"] = ([(p * g["folga"] + g["cw"] / 2) / g["w"], None] if g["eixo"] == "x"
                 else [None, (p * g["folga"] + g["ch"] / 2) / g["h"]])
    return r


def decidir(c: dict, an: dict, clip: list[float], iqa: list[float], clip2: list[float] | None = None) -> None:
    """Escolhe a posição por plano nos dois formatos e reescreve a nota do candidato pelo que aparece
    no formato do item. clip = ação (en), clip2 = identidade (busca); nota do recorte = média dos dois."""
    if not an or len(clip) != len(an["mapa"]):
        return
    if clip2 and len(clip2) == len(clip):
        clip = [(a + b) / 2 for a, b in zip(clip, clip2)]
    val = {m: (s, q) for m, s, q in zip(an["mapa"], clip, iqa or [0.5] * len(clip))}
    res = {asp: _decidir_aspecto(an, val, asp) for asp in ASPECTOS}
    res = {k: v for k, v in res.items() if v}
    if not res:
        return
    asp = aspecto_do_layout(an["layout"])
    r = res.get(asp) or next(iter(res.values()))
    curto = an.get("pisca", False)
    ajuste = ((r["visivel"] - c.get("clip", 0.0)) + 4.0 * (r["iqa"] - 0.5) - (2.0 if r["larga"] else 0.0)
              - max(0.0, (ESCURO - r["luz"]) / 6) - (4.0 if curto else 0.0))
    c["score"] = round(c["score"] + ajuste, 2)
    c.update({"recortes": {k: v["recorte"] for k, v in res.items()}, "focos": {k: v["foco"] for k, v in res.items()},
              "foco": r["foco"], "entrada": an["entrada"], "visivel": round(r["visivel"], 2),
              "cena_inteira": round(r["inteira"], 2), "iqa": round(r["iqa"], 3), "luz": round(r["luz"], 1),
              "larga": r["larga"], "sem_rosto": r["sem_rosto"], "escuro": r["luz"] < ESCURO, "pisca": bool(curto),
              "faixa_ok": bool("faixa" in res and not res["faixa"]["larga"]), "thumb": an["thumb"], "rostos": []})


def main() -> None:
    """Teste isolado: analisa, roda o CLIP e imprime a decisão."""
    from td_comum import SKILL, python_align
    arq, layout, texto = sys.argv[1], sys.argv[2], sys.argv[3]
    busca = sys.argv[4] if len(sys.argv) > 4 else texto
    tmp = Path(arq).parent / "_reenq_teste"
    an = analisar(arq, layout, 99.0, 0.0, tmp, "t")
    ent, sai = tmp / "in.json", tmp / "out.json"
    ent.write_text(json.dumps({"pedidos": [{"id": "r", "textos": [texto, busca], "texto": texto,
                                            "imagens": an["imagens"], "iqa": True}]}), encoding="utf-8")
    subprocess.run([python_align(), str(SKILL / "scripts" / "clip_rank.py"), str(ent), str(sai)], check=True)
    sc = json.loads(sai.read_text(encoding="utf-8"))
    c = {"score": 0.0, "clip": 0.0}
    decidir(c, an, sc["r"], sc.get("r#iqa", []), sc.get("r#t1"))
    print(json.dumps({k: v for k, v in c.items() if k != "thumb"}, ensure_ascii=False))
    print("planos:", [(round(a, 2), round(b, 2)) for a, b in an["planos"]], "cortes:", [round(x, 2) for x in an["cortes"]])


if __name__ == "__main__":
    main()
