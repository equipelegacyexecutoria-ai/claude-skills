"""Confere um episódio renderizado antes de entregar (reprova o que não passa).

Checa: 1920×1080/30 fps/H.264/AAC 48 kHz · duração 15–45 min e igual ao plano · volume −14 LUFS (±1) e pico
≤ −1 dBTP · tela preta (só o mergulho da abertura pode) · silêncio > 3 s · o QR de CADA CTA lê a URL certa no
vídeo final (3 momentos por CTA, em 1080p e reduzido para 720p) · card em cima de rosto · e monta a folha de
conferência (quadros antes/depois de cada emenda e de cada CTA) + começo e fim do texto do episódio.

Uso: python conferir.py <trabalho> <arquivo do episódio sem .mp4> [--pasta render]
Saída: <trabalho>/qa/<arquivo>_qa.json e <arquivo>_folha.jpg; código de saída 1 se reprovar.
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
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import SKILL, gravar_json, hms, ler_json, sonda  # noqa: E402
from render_episodio import palavras_no_episodio, rostos  # noqa: E402


def quadro_video(video: Path, t: float, largura: int | None = None):
    vf = ["-vf", f"scale={largura}:-1"] if largura else []
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1", *vf,
                        "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True)
    return cv2.imdecode(np.frombuffer(p.stdout, np.uint8), cv2.IMREAD_COLOR)


def ler_qr(img) -> set[str]:
    return {d.detectAndDecode(img)[0] for d in (cv2.QRCodeDetector(), cv2.QRCodeDetectorAruco())} - {""}


def ffmpeg_log(args: list[str]) -> str:
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.stderr


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("trabalho")
    ap.add_argument("arquivo")
    ap.add_argument("--pasta", default="render")
    a = ap.parse_args()
    trab = Path(a.trabalho)
    pasta = trab / a.pasta
    video = pasta / f"{a.arquivo}.mp4"
    info = ler_json(pasta / f"{a.arquivo}.json")
    qa = trab / "qa"
    qa.mkdir(exist_ok=True)
    falhas, avisos, ok = [], [], []

    # 1–2. formato e duração
    s = sonda(video)
    v = next(x for x in s["streams"] if x["codec_type"] == "video")
    au = next(x for x in s["streams"] if x["codec_type"] == "audio")
    dur = float(s["format"]["duration"])
    if a.pasta == "render" and (v["width"], v["height"]) != (1920, 1080):
        falhas.append(f"resolução {v['width']}×{v['height']}")
    if v["codec_name"] != "h264" or au["codec_name"] != "aac" or au.get("sample_rate") != "48000":
        falhas.append(f"codecs {v['codec_name']}/{au['codec_name']}/{au.get('sample_rate')}")
    if abs(dur - info["duracao"]) > 1.0:
        falhas.append(f"duração {hms(dur)} ≠ plano {hms(info['duracao'])}")
    if not 15 * 60 <= dur <= 45 * 60:
        falhas.append(f"duração {hms(dur)} fora de 15–45 min")
    ok.append(f"formato {v['width']}×{v['height']} {v['r_frame_rate']} · {hms(dur)}")

    # 3. volume
    log = ffmpeg_log(["-i", str(video), "-map", "0:a:0", "-af", "ebur128=peak=true", "-f", "null", "-"])
    I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", log)[-1])
    tp = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", log)[-1])
    if not -15.0 <= I <= -13.0:
        falhas.append(f"volume {I} LUFS (alvo −14)")
    if tp > -0.9:
        falhas.append(f"pico {tp} dBTP (máx. −1)")
    ok.append(f"volume {I} LUFS, pico {tp} dBTP")

    # 4. tela preta (o mergulho da abertura é esperado)
    log = ffmpeg_log(["-i", str(video), "-vf", "blackdetect=d=0.4:pix_th=0.08", "-an", "-f", "null", "-"])
    pretos = [(float(x), float(y)) for x, y in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", log)]
    ab = info.get("abertura_dur", 0)
    ruins = [p for p in pretos if not (ab and abs(p[0] - (ab - 0.3)) < 1.0) and p[1] - p[0] > 0.4]
    if ruins:
        falhas.append("tela preta em " + ", ".join(f"{hms(x)}–{hms(y)}" for x, y in ruins))

    # 5. silêncio longo
    log = ffmpeg_log(["-i", str(video), "-map", "0:a:0", "-af", "silencedetect=noise=-42dB:d=3", "-f", "null", "-"])
    sil = re.findall(r"silence_end: ([\d.]+) \| silence_duration: ([\d.]+)", log)
    if sil:
        avisos.append("silêncio > 3 s em " + ", ".join(f"{hms(float(e) - float(d))} ({float(d):.1f}s)" for e, d in sil))

    # 6–7. QR e rosto sob o card
    url = info["url_qr"]
    cw, ch = info["card"]["w"], info["card"]["h"]
    quadros_cta = []
    for pos in info["card"]["posicoes"]:
        t = pos["t"]
        for dt in (3, 15, 27):
            img = quadro_video(video, t + dt)
            lidos = ler_qr(img)
            if url not in lidos:
                falhas.append(f"QR da CTA {pos['cta']} não leu em {hms(t + dt)} (leu {lidos or 'nada'})")
            peq = cv2.resize(img, (1280, 720), interpolation=cv2.INTER_AREA)
            if url not in ler_qr(peq):
                avisos.append(f"QR da CTA {pos['cta']} não lê em 720p ({hms(t + dt)})")
            X0, Y0, X1, Y1 = pos["x"], pos["y"], pos["x"] + cw, pos["y"] + ch
            for fx, fy, fw, fh in rostos(img):
                if fx < X1 and fx + fw > X0 and fy < Y1 and fy + fh > Y0:
                    falhas.append(f"card da CTA {pos['cta']} cobre um rosto em {hms(t + dt)}")
            if dt == 15:
                quadros_cta.append((f"CTA {pos['cta']} {hms(t + dt)} ({pos['canto']})", img))
    if not any("QR" in f for f in falhas):
        ok.append(f"QR lido nas {len(info['card']['posicoes'])} CTAs -> {url}")

    # 8. folha: antes/depois de cada emenda + CTAs
    itens, off = [], 0.0
    trechos = info["trechos_finais"]
    for k, (x, y) in enumerate(trechos[:-1]):
        off += y - x
        itens.append((f"emenda {k + 1} antes {hms(off - 0.5)}", quadro_video(video, off - 0.5, 480)))
        itens.append((f"emenda {k + 1} depois {hms(off + 0.4)}", quadro_video(video, off + 0.4, 480)))
    itens += [(r, cv2.resize(i, (480, 270))) for r, i in quadros_cta]
    cols, w, h = 4, 480, 270
    linhas = (len(itens) + cols - 1) // cols
    folha = Image.new("RGB", (cols * w, linhas * (h + 22)), "black")
    dr = ImageDraw.Draw(folha)
    fnt = ImageFont.truetype(str(SKILL / "fonts" / "SF-Pro-Display-Medium.otf"), 16)
    for i, (rot, img) in enumerate(itens):
        if img is None:
            continue
        x, y = (i % cols) * w, (i // cols) * (h + 22)
        folha.paste(Image.fromarray(cv2.cvtColor(cv2.resize(img, (w, h)), cv2.COLOR_BGR2RGB)), (x, y))
        dr.text((x + 6, y + h + 2), rot, fill="yellow", font=fnt)
    folha.save(qa / f"{a.arquivo}_folha.jpg", quality=85)

    # 9. começo e fim do texto
    todas = ler_json(trab / "transcricao.json")["palavras"]
    pal = palavras_no_episodio(todas, trechos)
    corpo = [w for w in pal if w["ini"] >= ab]
    comeco = " ".join(w["t"] for w in corpo[:90])
    fim = " ".join(w["t"] for w in pal[-90:])
    abertura = " ".join(w["t"] for w in pal if w["ini"] < ab)

    veredito = "APROVADO" if not falhas else "REPROVADO"
    rel = {"arquivo": a.arquivo, "veredito": veredito, "falhas": falhas, "avisos": avisos, "ok": ok,
           "abertura": abertura, "comeco": comeco, "fim": fim, "folha": str(qa / f"{a.arquivo}_folha.jpg")}
    gravar_json(qa / f"{a.arquivo}_qa.json", rel)
    print(f"== {a.arquivo}: {veredito}")
    for x in ok:
        print("  ok   ", x)
    for x in avisos:
        print("  aviso", x)
    for x in falhas:
        print("  FALHA", x)
    print(f"  abertura: {abertura}\n  começo: {comeco[:400]}\n  fim: …{fim[-400:]}")
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
