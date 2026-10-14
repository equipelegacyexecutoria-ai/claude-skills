"""Renderiza os episódios do plano (plano.json) em 1920×1080, com o card do QR nas CTAs e o som tratado.

plano.json (na pasta de trabalho):
{
  "fonte": "C:/Render/brutos/<slug>/<aula>.mp4",
  "codigo": "t12a10",                       # vai na UTM: utm_campaign=<codigo>e<n>
  "borrar": [["02:53:36.5", "02:53:48", 0, 0, 1920, 1080]],   # opcional: desfoca área (vídeo de terceiros)
  "episodios": [
    {"n": 1, "arquivo": "01 - Título legível",
     "abertura": [["00:10:47.3", "00:11:04.9"]],   # opcional: 15–40 s do trecho mais forte do episódio; entra
                                                   #   antes, com um mergulho rápido no preto até o começo
     "segmentos": [["00:01:12.3", "00:11:33.4"], ["00:26:04.2", "00:34:23.3"]],  # trechos da aula, em ordem
     "ctas_aula": ["00:09:14", "00:36:44"]  # opcional: instantes DA AULA em que o QR entra (cai no começo de
                                            #   frase mais próximo); "ctas" = tempos no episódio; sem nada, automático
     "cantos": {"2": "topo-d/compacto"},    # opcional: força a posição de uma CTA (senão escolhe sozinho)
     "meta": {...}                          # títulos, thumbs, descrição, capítulos: ver metadados.py
    }
  ]
}

Pausas sem fala maiores que 2,5 s dentro dos trechos viram 0,9 s sozinhas (plateia escrevendo, vídeo mudo).

Saídas em <trabalho>/render/ (ou previa/ com --rapido): <arquivo>.mp4, <arquivo>.srt (legenda para subir no
YouTube, não queimada) e <arquivo>.json (trechos finais, CTAs, URLs, loudness) — o metadados.py usa esse json.

Uso: python render_episodio.py <trabalho> [--so 1,3] [--rapido] [--so-mapa]
  --rapido  prévia 960×540 rápida para conferir
  --so-mapa só calcula trechos, duração e CTAs (não renderiza)
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from achar import achar_frase, resolver_cortes, tirar_intervalos  # noqa: E402
from comum import SKILL, gravar_json, hms, ler_json, seg  # noqa: E402
import letreiro as LT  # noqa: E402

BASE_URL = "https://formulario.legacyexecutoria.com.br/"
CTA_DUR = 30.0                      # segundos na tela (igual ao Executoria Cast)
CTA_POSICOES = (0.25, 0.70, None)   # automático: ~25%, ~70% e perto do fim (pesquisa: máx. 3 por vídeo)
CTA_FOLGA_FIM = 25                  # o QR sai pelo menos 25 s antes do fim (tela final: últimos 5–20 s)
MAX_PAUSA, FOLGA_PAUSA = 2.5, 0.45  # pausa sem fala > 2,5 s vira 0,9 s (0,45 s de cada lado)
DIP = 0.30                          # mergulho no preto entre a abertura e o começo do episódio
RESPIRO = 1.2                       # fim: a última frase termina, a imagem segura 1,2 s e escurece em silêncio
FADE_IN, FADE_OUT, DESLIZE = 0.35, 0.30, 26   # card: aparece + desliza 26 px da esquerda; some
MARGEM_X, MARGEM_Y = 34, 28         # posição do card (canto superior esquerdo, em 1080p)
ESCALA_CARD = 1.65                  # card ~500×250 em 1080p, QR ~185 px (5 px por módulo)
ESCALA_COMPACTO = 1.2               # card compacto ~360×180, QR ~164 px: cabe na faixa acima do slide
AUDIO_PRE = "highpass=f=70,acompressor=threshold=-21dB:ratio=2.5:attack=15:release=250:makeup=2"
# as aulas chegam com pico de +3 dBTP: o loudnorm sozinho deixa passar −0,6; o limitador garante ≤ −1 dBTP
LIMITADOR = "alimiter=limit=0.71:attack=4:release=60:level=disabled"   # −3 dBFS: folga para o AAC


CANTOS = {"se": 0.0, "ie": 0.03, "sd": 0.04, "id": 0.06}   # sup./inf. × esq./dir.; o número desempata (prefere sup. esq.)
_ROSTO = None


def tempo_na_aula(segs, t: float) -> float:
    off = 0.0
    for a, b in segs:
        if t < off + (b - a):
            return a + (t - off)
        off += b - a
    return segs[-1][1]


def quadro(fonte: str, t_aula: float, largura: int = 960):
    p = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{t_aula:.2f}", "-i", fonte, "-frames:v", "1",
                        "-vf", f"scale={largura}:-1", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True)
    return cv2.imdecode(np.frombuffer(p.stdout, np.uint8), cv2.IMREAD_COLOR)


def rostos(img):
    global _ROSTO
    h, w = img.shape[:2]
    if _ROSTO is None:
        _ROSTO = cv2.FaceDetectorYN.create(str(SKILL / "models" / "face_detection_yunet_2023mar.onnx"), "",
                                           (w, h), 0.6, 0.3, 50)
    _ROSTO.setInputSize((w, h))
    _, f = _ROSTO.detect(img)
    return [] if f is None else [tuple(map(float, r[:4])) for r in f]


def caixa_canto(canto: str, vw: float, vh: float, my: float = MARGEM_Y, W: int = 1920, H: int = 1080):
    """Caixa VISÍVEL do card (em 1080p) no canto; embaixo, fica acima dos 15% finais (barra do player)."""
    x = MARGEM_X if canto[1] == "e" else W - MARGEM_X - vw
    y = my if canto[0] == "s" else H * 0.85 - vh
    return x, y


def area_de_conteudo(cinza) -> tuple[int, int, int, int] | None:
    """Retângulo do conteúdo no layout 'slide + janela' (fundo escuro em volta), em px da imagem."""
    col, lin = (cinza > 60).mean(axis=0), (cinza > 60).mean(axis=1)
    xs, ys = np.where(col > 0.15)[0], np.where(lin > 0.15)[0]
    if not len(xs) or not len(ys):
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def candidatos_posicao(tamanhos: dict, faixa_topo: tuple | None):
    """(nome, tamanho, x, y, w, h) visíveis em 1080p: 4 cantos × 2 tamanhos + compacto alinhado no topo livre."""
    out = []
    for tam, (vw, vh) in tamanhos.items():
        for c in CANTOS:
            x, y = caixa_canto(c, vw, vh, MARGEM_Y if tam == "grande" else 12)
            out.append((c, tam, x, y, vw, vh))
    if faixa_topo:
        x0, y0, x1 = faixa_topo                   # conteúdo começa em y0: o compacto cabe em cima, alinhado
        vw, vh = tamanhos["compacto"]
        if y0 - 12 >= vh + 8:
            yy = max(8, (y0 - vh) / 2)
            out += [("topo-e", "compacto", x0, yy, vw, vh), ("topo-d", "compacto", x1 - vw, yy, vw, vh)]
    return out


def escolher_canto(fonte: str, segs, t: float, tamanhos: dict):
    """Posição com menos coisa importante durante os 30 s: sem rosto, sem texto de slide, sem área clara.
    Prefere o card grande; usa o compacto (topo, alinhado com o slide/janela) quando o grande cobriria algo."""
    imgs = []
    for k in range(4):
        img = quadro(fonte, tempo_na_aula(segs, t + 2 + k * (CTA_DUR - 4) / 3))
        if img is not None:
            imgs.append(img)
    f = imgs[0].shape[1] / 1920 if imgs else 0.5
    areas = [area_de_conteudo(cv2.cvtColor(i, cv2.COLOR_BGR2GRAY)) for i in imgs]
    faixa = None
    if areas and all(areas):                      # mesmo layout nos 4 quadros: faixa livre comum em cima
        faixa = (min(a[0] for a in areas) / f, min(a[1] for a in areas) / f, max(a[2] for a in areas) / f)
    layout_janela = faixa is not None and faixa[1] >= 150   # faixa escura em cima = layout slide + janela
    cands = candidatos_posicao(tamanhos, faixa if layout_janela else None)
    notas = {i: 0.0 for i in range(len(cands))}
    for img, area in zip(imgs, areas):
        cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        bordas = cv2.Canny(cinza, 60, 160)
        caras = rostos(img)
        for i, (_, _, x, y, w, h) in enumerate(cands):
            X0, Y0, X1, Y1 = int(x * f), int(max(0, y) * f), int((x + w) * f), int((y + h) * f)
            nota = bordas[Y0:Y1, X0:X1].mean() / 255 * 2 + (cinza[Y0:Y1, X0:X1] > 190).mean() * 0.6
            if layout_janela and area:            # layout slide + janela: encostar no slide/janela custa caro
                ax0, ay0, ax1, ay1 = area
                inter = max(0, min(X1, ax1) - max(X0, ax0)) * max(0, min(Y1, ay1) - max(Y0, ay0))
                nota += 0.8 * inter / max(1, (X1 - X0) * (Y1 - Y0))
            for fx, fy, fw, fh in caras:          # rosto ampliado ~ cabeça e ombros
                ax0, ay0, ax1, ay1 = fx - fw, fy - fh * 0.6, fx + fw * 2, fy + fh * 3
                if max(0.0, min(X1, ax1) - max(X0, ax0)) * max(0.0, min(Y1, ay1) - max(Y0, ay0)) > 0:
                    nota += 5
            notas[i] += nota / max(1, len(imgs))
    for i, (c, tam, *_) in enumerate(cands):
        notas[i] += CANTOS.get(c, -0.02) + (0.0 if tam == "grande" else 0.05)   # topo alinhado: -0,02 (desempata)
    grandes = [i for i, c in enumerate(cands) if c[1] == "grande"]
    melhor_g = min(grandes, key=notas.get)
    melhor = melhor_g if notas[melhor_g] <= 0.12 else min(notas, key=notas.get)
    c = cands[melhor]
    return {"canto": c[0], "tam": c[1], "box": [round(v) for v in c[2:]],
            "notas": {f"{cands[i][0]}/{cands[i][1]}": round(v, 3) for i, v in notas.items()}}


def url_qr(codigo: str, n: int) -> str:
    # curta de propósito (≤ 106 caracteres = QR versão 5): utm_content fica de fora no QR
    return f"{BASE_URL}?utm_source=organico&utm_medium=youtube&utm_campaign={codigo}e{n}"


def url_descricao(codigo: str, n: int, onde: str = "descricao") -> str:
    return f"{BASE_URL}?utm_source=organico&utm_medium=youtube&utm_campaign={codigo}e{n}&utm_content={onde}"


def tirar_pausas(segs, palavras, max_pausa=MAX_PAUSA, folga=FOLGA_PAUSA):
    """Quebra cada trecho nos buracos sem fala maiores que max_pausa."""
    out = []
    for a, b in segs:
        dentro = [w for w in palavras if w["ini"] >= a - 0.05 and w["fim"] <= b + 0.05]
        ini = a
        for w0, w1 in zip(dentro, dentro[1:]):
            if w1["ini"] - w0["fim"] > max_pausa:
                out.append((ini, w0["fim"] + folga))
                ini = w1["ini"] - folga
        out.append((ini, b))
    return [(round(x, 3), round(y, 3)) for x, y in out if y - x > 0.3]


def mapa_tempo(segs):
    """Converte tempo da aula -> tempo do episódio (ou None se o instante foi cortado)."""
    acum, tab = 0.0, []
    for a, b in segs:
        tab.append((a, b, acum))
        acum += b - a

    def conv(t: float):
        for a, b, off in tab:
            if a <= t <= b:
                return off + t - a
        return None
    return conv, acum


def palavras_no_episodio(todas, segs) -> list[dict]:
    """Palavras com tempo no episódio, trecho a trecho (a abertura repete palavras do corpo: tudo bem)."""
    out, off = [], 0.0
    for a, b in segs:
        for w in todas:
            if w["ini"] >= a and w["fim"] <= b:
                out.append({"t": w["t"], "ini": off + w["ini"] - a, "fim": off + w["fim"] - a})
        off += b - a
    return out


def inicio_de_frase(pal: list[dict], alvo: float, raio: float = 45) -> float:
    inicios = [pal[0]["ini"]] + [pal[k]["ini"] for k in range(1, len(pal))
                                 if pal[k]["ini"] - pal[k - 1]["fim"] >= 0.45]
    cand = [t for t in inicios if abs(t - alvo) <= raio]
    return round(min(cand, key=lambda x: abs(x - alvo)) if cand else alvo, 2)


def escolher_ctas(pal: list[dict], dur: float) -> list[float]:
    """Automático: ~25% (nunca antes de 3 min), ~70% e ~1,5 min antes do fim."""
    ctas = []
    for pos in CTA_POSICOES:
        alvo = max(180, dur * pos) if pos is not None else dur - CTA_DUR - CTA_FOLGA_FIM - 60
        t = inicio_de_frase(pal, alvo)
        if t + CTA_DUR <= dur - CTA_FOLGA_FIM and all(abs(t - c) >= 120 for c in ctas):
            ctas.append(t)
    return ctas


def corrigir(txt: str, correcoes: dict) -> str:
    """Troca nomes que o Whisper erra (plano.json "correcoes": {"Cléuto": "Clailton", "Ruas": "ROAS"})."""
    for errado, certo in (correcoes or {}).items():
        txt = re.sub(rf"(?<!\w){re.escape(errado)}(?!\w)", certo, txt)          # maiúscula conta: "Ruas" ≠ "ruas"
    return txt


def srt(pal: list[dict], caminho: Path, correcoes: dict | None = None) -> None:
    """Legenda para subir no YouTube: blocos de até ~70 caracteres em 2 linhas, quebra em pausa/pontuação."""
    blocos, cur = [], []
    for k, w in enumerate(pal):
        cur.append(w)
        txt = " ".join(x["t"] for x in cur)
        prox = pal[k + 1] if k + 1 < len(pal) else None
        fim_frase = re.search(r"[.!?]$", w["t"]) is not None
        pausa = prox is not None and prox["ini"] - w["fim"] > 0.6
        if len(txt) >= 70 or fim_frase or pausa or (cur[-1]["fim"] - cur[0]["ini"]) > 5.5 or prox is None:
            blocos.append(cur)
            cur = []
    lin, fim_ant = [], 0.0
    for i, b in enumerate(blocos, 1):
        txt = corrigir(" ".join(x["t"] for x in b), correcoes)
        if len(txt) > 42:
            corte = txt.rfind(" ", 0, len(txt) // 2 + 8)
            if corte > 0:
                txt = txt[:corte] + "\n" + txt[corte + 1:]
        a = max(b[0]["ini"], fim_ant)
        z = max(b[-1]["fim"], a + 0.8)
        fim_ant = z
        lin += [str(i), f"{hms(a, True).replace('.', ',')} --> {hms(z, True).replace('.', ',')}", txt, ""]
    caminho.write_text("\n".join(lin), encoding="utf-8")


def loudnorm_medir(fonte: str, segs) -> dict:
    """1ª passada do loudnorm (só áudio, rápido)."""
    cmd = ["ffmpeg", "-nostdin", "-hide_banner", "-nostats"]
    for a, b in segs:
        cmd += ["-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", fonte]
    fc = "".join(f"[{k}:a]asetpts=PTS-STARTPTS[a{k}];" for k in range(len(segs)))
    fc += "".join(f"[a{k}]" for k in range(len(segs))) + f"concat=n={len(segs)}:v=0:a=1[ac];"
    fc += f"[ac]{AUDIO_PRE},loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json[out]"
    cmd += ["-filter_complex", fc, "-map", "[out]", "-f", "null", "-"]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", p.stderr, re.S)
    if not m:
        raise RuntimeError("loudnorm não mediu:\n" + p.stderr[-2000:])
    return json.loads(m.group(0))


def pretos_da_fonte(trab: Path, fonte: str) -> list[tuple[float, float]]:
    """Piscares pretos da própria gravação (troca de câmera da transmissão): ~0,5 s a cada ~37 min.
    Mede uma vez (~2 min) e guarda em <trabalho>/pretos_fonte.json."""
    cache = trab / "pretos_fonte.json"
    if cache.exists():
        return [tuple(x) for x in ler_json(cache)]
    p = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-nostats", "-i", fonte, "-an", "-vf",
                        "blackdetect=d=0.05:pix_th=0.08", "-f", "null", "-"], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    pretos = [(float(a), float(b)) for a, b in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", p.stderr)]
    gravar_json(cache, pretos)
    return pretos


def cortes_no_meio_de_palavra(todas, segs) -> list[str]:
    """Ponta de trecho que cai dentro de uma palavra (corta a palavra no áudio)."""
    erros = []
    for a, b in segs:
        for w in todas:
            for ponta, nome in ((a, "início"), (b, "fim")):
                if w["ini"] + 0.03 < ponta < w["fim"] - 0.03:
                    erros.append(f"{nome} {hms(ponta, True)} corta a palavra '{w['t']}' "
                                 f"({hms(w['ini'], True)}–{hms(w['fim'], True)})")
    return erros


def pico_real(mp4: Path) -> float:
    p = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-nostats", "-i", str(mp4), "-map", "0:a:0", "-af",
                        "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    m = re.findall(r"Peak:\s+(-?[\d.]+|-inf) dBFS", p.stderr)
    return float(m[-1]) if m and m[-1] != "-inf" else -99.0


def segurar_pico(mp4: Path, teto: float = -1.2) -> None:
    """Estalo de microfone (plosiva) passa do limitador depois do AAC: mede o pico real do arquivo pronto e,
    se passou de −1 dBTP, refaz só o áudio com o limitador mais baixo (a imagem é copiada, ~20 s)."""
    pk = pico_real(mp4)
    if pk <= -1.0:
        return
    lim = 10 ** ((-3.0 - (pk - teto)) / 20)
    tmp = mp4.with_name(mp4.stem + "_pico.mp4")
    subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-v", "error", "-y", "-i", str(mp4), "-map", "0:v", "-map", "0:a",
                    "-c:v", "copy", "-af", f"alimiter=limit={lim:.3f}:attack=2:release=60:level=disabled",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(tmp)], check=True)
    tmp.replace(mp4)
    print(f"[pico] {mp4.name}: {pk:+.1f} dBTP -> refeito o áudio com limite {lim:.2f} -> {pico_real(mp4):+.1f} dBTP",
          flush=True)


def montar(trab: Path, ep: dict) -> dict:
    """Trechos finais, duração, palavras e CTAs de um episódio (sem renderizar)."""
    todas = ler_json(trab / "transcricao.json")["palavras"]
    erros = cortes_no_meio_de_palavra(todas, [(seg(a), seg(b)) for a, b in ep.get("abertura", []) + ep["segmentos"]])
    if erros:
        raise SystemExit(f"[ep {ep['n']}] corte no meio de palavra:\n  " + "\n  ".join(erros))
    abertura = tirar_pausas([(seg(a), seg(b)) for a, b in ep.get("abertura", [])], todas, 1.2, 0.3)
    corpo = [(seg(a), seg(b)) for a, b in ep["segmentos"]]
    cortes = resolver_cortes(todas, ep.get("cortar", []))          # frases/intervalos a tirar do corpo
    corpo = tirar_pausas(tirar_intervalos(corpo, cortes), todas)
    segs = abertura + corpo
    _, dur = mapa_tempo(segs)
    dur += RESPIRO
    pal = palavras_no_episodio(todas, segs)
    dur_ab = sum(b - a for a, b in abertura)
    conv_corpo, _ = mapa_tempo(corpo)
    if ep.get("ctas_aula"):
        ctas = []
        for t in ep["ctas_aula"]:
            x = conv_corpo(seg(t))
            if x is None:
                raise SystemExit(f"[ep {ep['n']}] CTA em {t} cai num trecho cortado")
            ctas.append(inicio_de_frase(pal, x + dur_ab, 6))
    elif ep.get("ctas"):
        ctas = [seg(t) for t in ep["ctas"]]
    else:
        ctas = escolher_ctas(pal, dur)
    for t in ctas:
        if t + CTA_DUR > dur - CTA_FOLGA_FIM:
            raise SystemExit(f"[ep {ep['n']}] CTA em {hms(t)} termina perto demais do fim ({hms(dur)})")
    conv_ab, _ = mapa_tempo(abertura)
    lets = []
    for L in ep.get("letreiros", []):
        if "frase" in L:
            r = achar_frase(todas, L["frase"], seg(L["perto"]) if L.get("perto") else None, L.get("raio", 120))
            if not r:
                raise SystemExit(f"[ep {ep['n']}] letreiro: não achei a frase {L['frase']!r}")
            ta = todas[r[0]]["ini"]
        else:
            ta = seg(L["aula"])
        x = conv_ab(ta) if L.get("onde") == "abertura" else conv_corpo(ta)
        if x is None:
            raise SystemExit(f"[ep {ep['n']}] letreiro '{L['texto']}' cai num trecho cortado ({hms(ta)})")
        if L.get("onde") != "abertura":
            x += dur_ab
        lets.append({"t": round(x, 2), "dur": float(L.get("dur", 6)), "texto": L["texto"], "tag": L.get("tag")})
    lets.sort(key=lambda z: z["t"])
    for a_, b_ in zip(lets, lets[1:]):                 # um letreiro sai quando o próximo entra
        a_["dur"] = round(max(2.5, min(a_["dur"], b_["t"] - a_["t"] - 0.15)), 2)
    return {"segs": segs, "n_ab": len(abertura), "dur": dur, "dur_ab": dur_ab, "pal": pal, "ctas": ctas,
            "conv_corpo": conv_corpo, "cortes": cortes, "letreiros": lets}


def render(trab: Path, plano: dict, ep: dict, rapido: bool, so_mapa: bool = False) -> Path | None:
    fonte = plano["fonte"]
    m = montar(trab, ep)
    segs, n_ab, dur, ctas, pal = m["segs"], m["n_ab"], m["dur"], m["ctas"], m["pal"]
    print(f"[ep {ep['n']}] {hms(dur)} (abertura {m['dur_ab']:.0f}s) · {len(segs)} trechos · "
          f"CTAs {[hms(t) for t in ctas]} = {[f'{t / dur:.0%}' for t in ctas]}", flush=True)
    for L in m["letreiros"]:
        print(f"[ep {ep['n']}]   letreiro {hms(L['t'])} ({L['dur']:.1f}s) {L['tag'] or ''} {L['texto']}", flush=True)
    if so_mapa:
        return None
    saida_dir = trab / ("previa" if rapido else "render")
    saida_dir.mkdir(exist_ok=True)
    nome = ep["arquivo"]
    url = url_qr(plano["codigo"], ep["n"])
    altura = 540 if rapido else 1080
    s = altura / 1080

    cards, tamanhos, sombras = {}, {}, {}
    for tam, esc, extra in (("grande", ESCALA_CARD, []), ("compacto", ESCALA_COMPACTO, ["--compacto"])):
        png = saida_dir / f"_card_e{ep['n']}_{tam}.png"
        subprocess.run([sys.executable, str(Path(__file__).parent / "qr_card.py"), url, str(png),
                        "--altura-video", str(altura), "--escala", str(esc), *extra], check=True)
        cards[tam] = png
        tamanhos[tam] = (300 * esc, 150 * esc)            # caixa visível em 1080p
        sombras[tam] = (Image.open(png).size[0] / s - 300 * esc) / 2

    pretos = pretos_da_fonte(trab, fonte)
    ln = loudnorm_medir(fonte, segs)
    print(f"[ep {ep['n']}] áudio de entrada {ln['input_i']} LUFS, pico {ln['input_tp']} dBTP", flush=True)

    cmd = ["ffmpeg", "-nostdin", "-hide_banner", "-y", "-stats_period", "30"]
    for a, b in segs:
        cmd += ["-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", fonte]
    k_card, n = len(segs), len(segs)
    cmd += ["-loop", "1", "-framerate", "30", "-i", str(cards["grande"]),
            "-loop", "1", "-framerate", "30", "-i", str(cards["compacto"])]
    lets = []
    for i, L in enumerate(m["letreiros"]):
        img, somb = LT.desenhar(L["texto"], L["tag"], altura)
        png = saida_dir / f"_let_e{ep['n']}_{i + 1}.png"
        img.save(png)
        lets.append((L, LT.posicao(img, somb, altura)))
        cmd += ["-loop", "1", "-framerate", "30", "-t", f"{L['dur']:.2f}", "-i", str(png)]
    fc = []
    escala = "scale=960:540:flags=lanczos," if rapido else ""
    for k, (a, b) in enumerate(segs):
        d = b - a
        fa, fv = [], []
        dip_fim = bool(n_ab) and k == n_ab - 1     # último trecho da abertura: some no preto
        dip_ini = bool(n_ab) and k == n_ab         # 1º trecho do corpo: volta do preto
        if k > 0:
            fa.append(f"afade=t=in:d={DIP if dip_ini else 0.04}")
        if k < n - 1:
            fo = DIP if dip_fim else 0.04
            fa.append(f"afade=t=out:st={max(0.0, d - fo):.3f}:d={fo}")
        else:                                      # fim do episódio: segura o último quadro e escurece em silêncio
            fa += [f"afade=t=out:st={max(0.0, d - 0.12):.3f}:d=0.12", f"apad=pad_dur={RESPIRO}"]
            fv += [f"tpad=stop_mode=clone:stop_duration={RESPIRO}", f"fade=t=out:st={d - 0.2:.3f}:d={RESPIRO + 0.2}"]
        if dip_fim:
            fv.append(f"fade=t=out:st={max(0.0, d - DIP):.3f}:d={DIP}")
        if dip_ini:
            fv.append(f"fade=t=in:st=0:d={DIP}")
        for x, y in pretos:                       # tapa o piscar preto da gravação com o quadro vizinho
            if x < b and y > a:
                f0, f1 = int((max(x, a) - a) * 30), int(np.ceil((min(y, b) - a) * 30))
                troca = f0 - 1 if f0 > 0 else f1 + 1
                fv.insert(0, f"freezeframes=first={f0}:last={f1}:replace={troca}")
        extra = ("," + ",".join(fv)) if fv else ""
        # áreas a desfocar (vídeo de terceiros no telão: luta, trailer, reportagem) — tempos DA AULA, px em 1080p
        zonas = [(max(seg(z[0]), a) - a, min(seg(z[1]), b) - a, *z[2:]) for z in plano.get("borrar", [])
                 if seg(z[0]) < b and seg(z[1]) > a]
        if not zonas:
            fc.append(f"[{k}:v]{escala}fps=30,setpts=PTS-STARTPTS,format=yuv420p{extra}[v{k}]")
        else:
            fc.append(f"[{k}:v]{escala}fps=30,setpts=PTS-STARTPTS,format=yuv420p{extra}[vb{k}_0]")
            for j, (z0, z1, zx, zy, zw, zh) in enumerate(zonas):
                X, Y, Wz, Hz = (int(round(v * s / 2) * 2) for v in (zx, zy, zw, zh))
                fc.append(f"[vb{k}_{j}]split[vb{k}_{j}a][vb{k}_{j}b]")
                fc.append(f"[vb{k}_{j}b]crop={Wz}:{Hz}:{X}:{Y},boxblur=luma_radius=40:luma_power=4[bz{k}_{j}]")
                saida = f"v{k}" if j == len(zonas) - 1 else f"vb{k}_{j + 1}"
                fc.append(f"[vb{k}_{j}a][bz{k}_{j}]overlay={X}:{Y}:enable='between(t,{z0:.2f},{z1:.2f})'[{saida}]")
        fc.append(f"[{k}:a]aresample=48000,asetpts=PTS-STARTPTS{(',' + ','.join(fa)) if fa else ''}[a{k}]")
    fc.append("".join(f"[v{k}][a{k}]" for k in range(n)) + f"concat=n={n}:v=1:a=1[vc][ac]")
    posicoes = []
    for i, t in enumerate(ctas):
        forcado = (ep.get("cantos") or {}).get(str(i + 1))      # ex.: "sd" ou "topo-d/compacto"
        if forcado:
            canto, tam = (forcado.split("/") + ["grande"])[:2]
            vw, vh = tamanhos[tam]
            x, y = caixa_canto(canto, vw, vh, MARGEM_Y if tam == "grande" else 12) if not canto.startswith("topo") \
                else (MARGEM_X if canto.endswith("e") else 1920 - MARGEM_X - vw, 12)
            esc = {"canto": canto, "tam": tam, "box": [round(x), round(y), round(vw), round(vh)], "notas": None}
        else:
            esc = escolher_canto(fonte, segs, t, tamanhos)
        posicoes.append({"cta": i + 1, "t": round(t, 2), **esc})
        print(f"[ep {ep['n']}] CTA {i + 1} {hms(t)} -> {esc['canto']}/{esc['tam']} {esc['box']}", flush=True)
    usos = {tam: [p for p in posicoes if p["tam"] == tam] for tam in cards}
    for j, tam in enumerate(("grande", "compacto")):
        n_uso = len(usos[tam])
        if n_uso:
            fc.append(f"[{k_card + j}:v]format=rgba,split={n_uso}" + "".join(f"[{tam}{q}]" for q in range(n_uso)))
        else:
            fc.append(f"[{k_card + j}:v]nullsink")
    atual, cont = "vc", {"grande": 0, "compacto": 0}
    for i, p in enumerate(posicoes):
        t, tam = p["t"], p["tam"]
        rotulo = f"{tam}{cont[tam]}"
        cont[tam] += 1
        fim = t + CTA_DUR
        fc.append(f"[{rotulo}]fade=t=in:st={t:.2f}:d={FADE_IN}:alpha=1,"
                  f"fade=t=out:st={fim - FADE_OUT:.2f}:d={FADE_OUT}:alpha=1[k{i}]")
        bx, by = p["box"][0] - sombras[tam], p["box"][1] - sombras[tam]     # posição do PNG (com a sombra)
        sinal = "+" if (p["canto"].endswith("d")) else "-"                  # desliza de fora para dentro
        x = f"'{bx * s:.0f}{sinal}{DESLIZE * s:.0f}*pow(max(0,1-(t-{t:.2f})/{FADE_IN}),2)'"
        fc.append(f"[{atual}][k{i}]overlay=x={x}:y={by * s:.0f}:enable='between(t,{t:.2f},{fim:.2f})'"
                  f":eof_action=pass[o{i}]")
        atual = f"o{i}"
    for i, (L, (lx, ly)) in enumerate(lets):           # letreiros: entram e saem com fade, embaixo à esquerda
        d = L["dur"]
        fc.append(f"[{k_card + 2 + i}:v]format=rgba,fade=t=in:st=0:d=0.3:alpha=1,"
                  f"fade=t=out:st={max(0.0, d - 0.3):.2f}:d=0.3:alpha=1,setpts=PTS-STARTPTS+{L['t']:.2f}/TB[lt{i}]")
        fc.append(f"[{atual}][lt{i}]overlay=x={lx}:y={ly}:eof_action=pass[ol{i}]")
        atual = f"ol{i}"
    fc.append(f"[ac]{AUDIO_PRE},loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={ln['input_i']}:"
              f"measured_TP={ln['input_tp']}:measured_LRA={ln['input_lra']}:measured_thresh={ln['input_thresh']}:"
              f"offset={ln['target_offset']}:linear=true,{LIMITADOR},aresample=48000[aout]")
    cmd += ["-filter_complex", ";".join(fc), "-map", f"[{atual}]", "-map", "[aout]", "-t", f"{dur:.3f}"]
    # libx264 (CPU): o h264_nvenc deste ffmpeg pede driver NVIDIA ≥ 610 e o PC de render tem 13.0 da API
    if rapido:
        cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "28"]
    else:
        cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-tune", "film", "-profile:v", "high",
                "-g", "60", "-maxrate", "12M", "-bufsize", "24M"]
    cmd += ["-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart",
            str(saida_dir / f"{nome}.mp4")]
    (saida_dir / f"_cmd_e{ep['n']}.txt").write_text(subprocess.list2cmdline(cmd), encoding="utf-8")
    subprocess.run(cmd, check=True)
    segurar_pico(saida_dir / f"{nome}.mp4")

    srt(pal, saida_dir / f"{nome}.srt", plano.get("correcoes"))
    gravar_json(saida_dir / f"{nome}.json", {
        "n": ep["n"], "arquivo": nome, "duracao": round(dur, 2), "abertura_dur": round(m["dur_ab"], 2),
        "trechos_finais": segs, "segmentos": ep["segmentos"], "abertura": ep.get("abertura", []),
        "ctas": [round(t, 2) for t in ctas], "cta_dur": CTA_DUR, "url_qr": url,
        "url_descricao": url_descricao(plano["codigo"], ep["n"]),
        "url_comentario": url_descricao(plano["codigo"], ep["n"], "comentario"),
        "card": {"png": {k: v.name for k, v in cards.items()}, "posicoes": posicoes},
        "letreiros": m["letreiros"],
        "loudnorm_entrada": ln})
    return saida_dir / f"{nome}.mp4"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("trabalho")
    ap.add_argument("--so", default="")
    ap.add_argument("--rapido", action="store_true")
    ap.add_argument("--so-mapa", action="store_true")
    a = ap.parse_args()
    trab = Path(a.trabalho)
    plano = ler_json(trab / "plano.json")
    so = {int(x) for x in a.so.split(",") if x.strip()}
    for ep in plano["episodios"]:
        if so and ep["n"] not in so:
            continue
        out = render(trab, plano, ep, a.rapido, a.so_mapa)
        if out:
            print(f"ok: {out}", flush=True)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--so-pico":      # corrigir o pico de um mp4 já pronto
        segurar_pico(Path(sys.argv[2]))
    else:
        main()
