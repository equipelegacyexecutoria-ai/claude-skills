"""Renderiza os episódios do plano (plano.json) em 1920×1080, com o card do QR nas CTAs e o som tratado.

plano.json (na pasta de trabalho):
{
  "fonte": "C:/Render/brutos/<slug>/<aula>.mp4",
  "codigo": "t12a10",                       # vai na UTM: utm_campaign=<codigo>e<n>
  "episodios": [
    {"n": 1, "arquivo": "01 - Título legível",
     "segmentos": [["00:03:10.4", "00:21:55.0"], ["00:22:40.1", "00:41:12.8"]],   # trechos da aula, em ordem
     "ctas": ["05:40", "17:30"]             # opcional: tempos NO EPISÓDIO; sem isso calcula sozinho
    }
  ]
}

Saídas em <trabalho>/render/: <arquivo>.mp4, <arquivo>.srt (legenda para subir no YouTube, não queimada),
e <trabalho>/render/<arquivo>.json (mapa episódio→aula, CTAs, URL do QR, loudness).

Uso: python render_episodio.py <trabalho> [--so 1,3] [--rapido]   (--rapido = prévia 540p, para conferir)
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
CTA_DUR = 30.0           # segundos na tela (igual ao Executoria Cast)
CTA_PRIMEIRA = (300, 420)  # 1ª CTA entre 5:00 e 7:00
CTA_INTERVALO = 720      # depois, a cada ~12 min
CTA_FOLGA_FIM = 75       # nada de CTA nos últimos 75 s (tela final do YouTube)
FADE_IN, FADE_OUT, DESLIZE = 0.35, 0.30, 26   # entrada: some/aparece + desliza 26 px da esquerda
MARGEM_X, MARGEM_Y = 34, 28                  # posição do card (canto superior esquerdo, em 1080p)
AUDIO_PRE = "highpass=f=70,acompressor=threshold=-21dB:ratio=2.5:attack=15:release=250:makeup=2"


def url_qr(codigo: str, n: int) -> str:
    return f"{BASE_URL}?utm_source=organico&utm_medium=youtube&utm_campaign={codigo}e{n}"


def url_descricao(codigo: str, n: int) -> str:
    return f"{BASE_URL}?utm_source=organico&utm_medium=youtube&utm_campaign={codigo}e{n}&utm_content=descricao"


def mapa_tempo(segs: list[tuple[float, float]]):
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


def palavras_do_episodio(trab: Path, segs) -> list[dict]:
    tr = ler_json(trab / "transcricao.json")
    conv, _ = mapa_tempo(segs)
    out = []
    for w in tr["palavras"]:
        a, b = conv(w["ini"]), conv(w["fim"])
        if a is not None and b is not None:
            out.append({"t": w["t"], "ini": a, "fim": b})
    return out


def escolher_ctas(pal: list[dict], dur: float) -> list[float]:
    """Começo de frase (depois de pausa ≥ 0,45 s) mais perto de cada alvo: ~6:00, depois +12 min."""
    inicios = [pal[0]["ini"]] + [pal[k]["ini"] for k in range(1, len(pal))
                                 if pal[k]["ini"] - pal[k - 1]["fim"] >= 0.45]
    alvo, ctas = sum(CTA_PRIMEIRA) / 2, []
    while alvo <= dur - CTA_FOLGA_FIM - CTA_DUR:
        lo, hi = (CTA_PRIMEIRA if not ctas else (alvo - 90, alvo + 90))
        cand = [t for t in inicios if lo <= t <= min(hi, dur - CTA_FOLGA_FIM - CTA_DUR)]
        t = min(cand, key=lambda x: abs(x - alvo)) if cand else alvo
        ctas.append(round(t, 2))
        alvo = t + CTA_INTERVALO
    return ctas


def srt(pal: list[dict], caminho: Path) -> None:
    """Legenda para subir no YouTube: blocos de até 42 caracteres × 2 linhas, quebra em pausa/pontuação."""
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
    lin = []
    for i, b in enumerate(blocos, 1):
        txt = " ".join(x["t"] for x in b)
        if len(txt) > 42:
            meio = len(txt) // 2
            corte = txt.rfind(" ", 0, meio + 8)
            txt = txt[:corte] + "\n" + txt[corte + 1:]
        a, z = b[0]["ini"], max(b[-1]["fim"], b[0]["ini"] + 0.8)
        lin += [str(i), f"{hms(a, True).replace('.', ',')} --> {hms(z, True).replace('.', ',')}", txt, ""]
    caminho.write_text("\n".join(lin), encoding="utf-8")


def loudnorm_medir(fonte: str, segs, tmp: Path) -> dict:
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


def render(trab: Path, plano: dict, ep: dict, rapido: bool) -> Path:
    fonte = plano["fonte"]
    segs = [(seg(a), seg(b)) for a, b in ep["segmentos"]]
    _, dur = mapa_tempo(segs)
    pal = palavras_do_episodio(trab, segs)
    ctas = [seg(t) for t in ep["ctas"]] if ep.get("ctas") else escolher_ctas(pal, dur)
    saida_dir = trab / ("previa" if rapido else "render")
    saida_dir.mkdir(exist_ok=True)
    nome = ep["arquivo"]
    url = url_qr(plano["codigo"], ep["n"])

    card = saida_dir / f"_card_e{ep['n']}.png"
    altura = 540 if rapido else 1080
    subprocess.run([sys.executable, str(Path(__file__).parent / "qr_card.py"), url, str(card),
                    "--altura-video", str(altura)], check=True)

    ln = loudnorm_medir(fonte, segs, trab)
    print(f"[ep {ep['n']}] {hms(dur)} · {len(segs)} trechos · CTAs {[hms(t) for t in ctas]} · "
          f"áudio {ln['input_i']} LUFS", flush=True)

    cmd = ["ffmpeg", "-hide_banner", "-y", "-stats_period", "30"]
    for a, b in segs:
        cmd += ["-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", fonte]
    k_card = len(segs)
    cmd += ["-loop", "1", "-framerate", "30", "-i", str(card)]
    fc, n = [], len(segs)
    escala = "scale=960:540," if rapido else ""
    for k, (a, b) in enumerate(segs):
        d = b - a
        fa = []
        if k > 0:
            fa.append("afade=t=in:d=0.04")
        if k < n - 1:
            fa.append(f"afade=t=out:st={max(0, d - 0.04):.3f}:d=0.04")
        fc.append(f"[{k}:v]{escala}fps=30,setpts=PTS-STARTPTS,format=yuv420p[v{k}]")
        fc.append(f"[{k}:a]asetpts=PTS-STARTPTS{(',' + ','.join(fa)) if fa else ''}[a{k}]")
    fc.append("".join(f"[v{k}][a{k}]" for k in range(n)) + f"concat=n={n}:v=1:a=1[vc][ac]")
    # card: uma cópia por CTA, cada uma com o próprio fade
    fc.append(f"[{k_card}:v]format=rgba,split={max(1, len(ctas))}" + "".join(f"[c{i}]" for i in range(max(1, len(ctas)))))
    atual = "vc"
    s = altura / 1080
    for i, t in enumerate(ctas):
        fim = t + CTA_DUR
        fc.append(f"[c{i}]fade=t=in:st={t:.2f}:d={FADE_IN}:alpha=1,"
                  f"fade=t=out:st={fim - FADE_OUT:.2f}:d={FADE_OUT}:alpha=1[k{i}]")
        x = (f"'{MARGEM_X * s:.0f}-{DESLIZE * s:.0f}*pow(max(0,1-(t-{t:.2f})/{FADE_IN}),2)'")
        fc.append(f"[{atual}][k{i}]overlay=x={x}:y={MARGEM_Y * s:.0f}:enable='between(t,{t:.2f},{fim:.2f})'"
                  f":eof_action=pass:shortest=0[o{i}]")
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
    (saida_dir / f"_cmd_e{ep['n']}.txt").write_text(" ".join(f'"{c}"' if " " in c else c for c in cmd), encoding="utf-8")
    subprocess.run(cmd, check=True)

    srt(pal, saida_dir / f"{nome}.srt")
    gravar_json(saida_dir / f"{nome}.json", {
        "n": ep["n"], "arquivo": nome, "duracao": round(dur, 2), "segmentos": ep["segmentos"],
        "ctas": [round(t, 2) for t in ctas], "cta_dur": CTA_DUR, "url_qr": url,
        "url_descricao": url_descricao(plano["codigo"], ep["n"]),
        "card": {"x": round(MARGEM_X * s), "y": round(MARGEM_Y * s)}, "loudnorm_entrada": ln})
    return saida_dir / f"{nome}.mp4"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("trabalho")
    ap.add_argument("--so", default="")
    ap.add_argument("--rapido", action="store_true")
    a = ap.parse_args()
    trab = Path(a.trabalho)
    plano = ler_json(trab / "plano.json")
    so = {int(x) for x in a.so.split(",") if x.strip()}
    for ep in plano["episodios"]:
        if so and ep["n"] not in so:
            continue
        out = render(trab, plano, ep, a.rapido)
        print(f"ok: {out}", flush=True)


if __name__ == "__main__":
    main()
