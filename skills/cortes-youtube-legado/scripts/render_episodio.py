"""Renderiza os episódios do plano (plano.json) em 1920×1080, com o card do QR nas CTAs e o som tratado.

plano.json (na pasta de trabalho):
{
  "fonte": "C:/Render/brutos/<slug>/<aula>.mp4",
  "codigo": "t12a10",                       # vai na UTM: utm_campaign=<codigo>e<n>
  "episodios": [
    {"n": 1, "arquivo": "01 - Título legível",
     "abertura": [["00:10:47.3", "00:11:04.9"]],   # opcional: 15–40 s do trecho mais forte do episódio; entra
                                                   #   antes, com um mergulho rápido no preto até o começo
     "segmentos": [["00:01:12.3", "00:11:33.4"], ["00:26:04.2", "00:34:23.3"]],  # trechos da aula, em ordem
     "ctas_aula": ["00:09:14", "00:36:44"]  # opcional: instantes DA AULA em que o QR entra (cai no começo de
                                            #   frase mais próximo); "ctas" = tempos no episódio; sem nada, automático
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import gravar_json, hms, ler_json, seg  # noqa: E402

BASE_URL = "https://formulario.legacyexecutoria.com.br/"
CTA_DUR = 30.0                      # segundos na tela (igual ao Executoria Cast)
CTA_POSICOES = (0.25, 0.70, None)   # automático: ~25%, ~70% e perto do fim (pesquisa: máx. 3 por vídeo)
CTA_FOLGA_FIM = 25                  # o QR sai pelo menos 25 s antes do fim (tela final: últimos 5–20 s)
MAX_PAUSA, FOLGA_PAUSA = 2.5, 0.45  # pausa sem fala > 2,5 s vira 0,9 s (0,45 s de cada lado)
DIP = 0.30                          # mergulho no preto entre a abertura e o começo do episódio
FADE_IN, FADE_OUT, DESLIZE = 0.35, 0.30, 26   # card: aparece + desliza 26 px da esquerda; some
MARGEM_X, MARGEM_Y = 34, 28         # posição do card (canto superior esquerdo, em 1080p)
ESCALA_CARD = 1.65                  # card ~500×250 em 1080p, QR ~185 px (5 px por módulo)
AUDIO_PRE = "highpass=f=70,acompressor=threshold=-21dB:ratio=2.5:attack=15:release=250:makeup=2"


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


def srt(pal: list[dict], caminho: Path) -> None:
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
        txt = " ".join(x["t"] for x in b)
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
    cmd = ["ffmpeg", "-hide_banner", "-nostats"]
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


def montar(trab: Path, ep: dict) -> dict:
    """Trechos finais, duração, palavras e CTAs de um episódio (sem renderizar)."""
    todas = ler_json(trab / "transcricao.json")["palavras"]
    abertura = tirar_pausas([(seg(a), seg(b)) for a, b in ep.get("abertura", [])], todas, 1.2, 0.3)
    corpo = tirar_pausas([(seg(a), seg(b)) for a, b in ep["segmentos"]], todas)
    segs = abertura + corpo
    _, dur = mapa_tempo(segs)
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
    return {"segs": segs, "n_ab": len(abertura), "dur": dur, "dur_ab": dur_ab, "pal": pal, "ctas": ctas,
            "conv_corpo": conv_corpo}


def render(trab: Path, plano: dict, ep: dict, rapido: bool, so_mapa: bool = False) -> Path | None:
    fonte = plano["fonte"]
    m = montar(trab, ep)
    segs, n_ab, dur, ctas, pal = m["segs"], m["n_ab"], m["dur"], m["ctas"], m["pal"]
    print(f"[ep {ep['n']}] {hms(dur)} (abertura {m['dur_ab']:.0f}s) · {len(segs)} trechos · "
          f"CTAs {[hms(t) for t in ctas]} = {[f'{t / dur:.0%}' for t in ctas]}", flush=True)
    if so_mapa:
        return None
    saida_dir = trab / ("previa" if rapido else "render")
    saida_dir.mkdir(exist_ok=True)
    nome = ep["arquivo"]
    url = url_qr(plano["codigo"], ep["n"])
    altura = 540 if rapido else 1080
    s = altura / 1080

    card = saida_dir / f"_card_e{ep['n']}.png"
    subprocess.run([sys.executable, str(Path(__file__).parent / "qr_card.py"), url, str(card),
                    "--altura-video", str(altura), "--escala", str(ESCALA_CARD)], check=True)

    ln = loudnorm_medir(fonte, segs)
    print(f"[ep {ep['n']}] áudio de entrada {ln['input_i']} LUFS, pico {ln['input_tp']} dBTP", flush=True)

    cmd = ["ffmpeg", "-hide_banner", "-y", "-stats_period", "30"]
    for a, b in segs:
        cmd += ["-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", fonte]
    k_card, n = len(segs), len(segs)
    cmd += ["-loop", "1", "-framerate", "30", "-i", str(card)]
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
        if dip_fim:
            fv.append(f"fade=t=out:st={max(0.0, d - DIP):.3f}:d={DIP}")
        if dip_ini:
            fv.append(f"fade=t=in:st=0:d={DIP}")
        extra = ("," + ",".join(fv)) if fv else ""
        fc.append(f"[{k}:v]{escala}fps=30,setpts=PTS-STARTPTS,format=yuv420p{extra}[v{k}]")
        fc.append(f"[{k}:a]aresample=48000,asetpts=PTS-STARTPTS{(',' + ','.join(fa)) if fa else ''}[a{k}]")
    fc.append("".join(f"[v{k}][a{k}]" for k in range(n)) + f"concat=n={n}:v=1:a=1[vc][ac]")
    nc = max(1, len(ctas))
    fc.append(f"[{k_card}:v]format=rgba,split={nc}" + "".join(f"[c{i}]" for i in range(nc)))
    atual = "vc"
    for i, t in enumerate(ctas):
        fim = t + CTA_DUR
        fc.append(f"[c{i}]fade=t=in:st={t:.2f}:d={FADE_IN}:alpha=1,"
                  f"fade=t=out:st={fim - FADE_OUT:.2f}:d={FADE_OUT}:alpha=1[k{i}]")
        x = f"'{MARGEM_X * s:.0f}-{DESLIZE * s:.0f}*pow(max(0,1-(t-{t:.2f})/{FADE_IN}),2)'"
        fc.append(f"[{atual}][k{i}]overlay=x={x}:y={MARGEM_Y * s:.0f}:enable='between(t,{t:.2f},{fim:.2f})'"
                  f":eof_action=pass[o{i}]")
        atual = f"o{i}"
    if not ctas:
        fc.append("[c0]nullsink")
    fc.append(f"[ac]{AUDIO_PRE},loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={ln['input_i']}:"
              f"measured_TP={ln['input_tp']}:measured_LRA={ln['input_lra']}:measured_thresh={ln['input_thresh']}:"
              f"offset={ln['target_offset']}:linear=true,aresample=48000[aout]")
    cmd += ["-filter_complex", ";".join(fc), "-map", f"[{atual}]", "-map", "[aout]", "-t", f"{dur:.3f}"]
    if rapido:
        cmd += ["-c:v", "h264_nvenc", "-preset", "p4", "-cq", "30", "-b:v", "0"]
    else:
        cmd += ["-c:v", "h264_nvenc", "-preset", "p7", "-tune", "hq", "-rc", "vbr", "-cq", "19",
                "-b:v", "0", "-maxrate", "20M", "-bufsize", "40M", "-profile:v", "high", "-spatial-aq", "1",
                "-temporal-aq", "1", "-bf", "3", "-g", "60"]
    cmd += ["-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart",
            str(saida_dir / f"{nome}.mp4")]
    (saida_dir / f"_cmd_e{ep['n']}.txt").write_text(subprocess.list2cmdline(cmd), encoding="utf-8")
    subprocess.run(cmd, check=True)

    srt(pal, saida_dir / f"{nome}.srt")
    gravar_json(saida_dir / f"{nome}.json", {
        "n": ep["n"], "arquivo": nome, "duracao": round(dur, 2), "abertura_dur": round(m["dur_ab"], 2),
        "trechos_finais": segs, "segmentos": ep["segmentos"], "abertura": ep.get("abertura", []),
        "ctas": [round(t, 2) for t in ctas], "cta_dur": CTA_DUR, "url_qr": url,
        "url_descricao": url_descricao(plano["codigo"], ep["n"]),
        "url_comentario": url_descricao(plano["codigo"], ep["n"], "comentario"),
        "card": {"x": round(MARGEM_X * s), "y": round(MARGEM_Y * s), "png": card.name},
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
    main()
