"""Conferência do reel renderizado — barreira antes de mostrar ao usuário.

Gera em <trabalho>/qa/:
  folha_blocos_NN.jpg  um quadro por tela de legenda, no momento em que o bloco está completo
  folha_cta.jpg        o último quadro da imagem + a CTA digitando e completa
  fala_final.txt       (--whisper) a fala do vídeo final, palavra a palavra, com as emendas marcadas
  fundo_mais_claro.png a tela cuja legenda está sobre o fundo mais claro (regra: aprovar essa)
  relatorio.json       formato, duração, loudness/pico, sincronia da CTA, pausas longas,
                       e (--whisper) palavras da legenda sem fala correspondente

Sai com código 3 quando há problema (não entregar assim).
Uso: python conferir.py <pasta_trabalho> <final.mp4> [--whisper]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import FAIXA_H, FAIXA_Y0, FPS, LUFS, TRUE_PEAK, W, gravar_json, ler_json, sonda  # noqa: E402

PARALELO = 8     # extrações de quadro ao mesmo tempo (NVDEC/CPU livres para isso)

FONTE_ROTULO = "C:/Windows/Fonts/arialbd.ttf"
EQUIV = {"ESTOU": {"TO", "ESTOU"}, "PARA": {"PRA", "PARA", "PRO"}, "ESTA": {"TA", "ESTA"},
         "VOCE": {"CE", "VOCE", "OCE"}, "ESTAMOS": {"TAMO", "TAMOS", "ESTAMOS"}}
PAUSA_LONGA = 0.46      # pausas naturais até 0,40 s ficam (09/10/2026); 0,45-0,5 s parado já foi reprovado


def quadro(video: Path, t: float) -> Image.Image:
    # legenda já queimada: a busca antes do -i dá o MESMO quadro (md5 conferido) e não decodifica o
    # vídeo desde o início a cada folha (8x mais rápido). Com ASS aplicado na extração, seria -ss depois.
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(0.0, t):.3f}", "-i", str(video), "-frames:v", "1",
                        "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True, check=True)
    return Image.open(BytesIO(p.stdout)).convert("RGB")


def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s.upper())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^A-Z0-9%]", "", s)


def folha(imagens: list[tuple[Image.Image, str]], cols: int, esc: float, saida: Path, faixa: bool = True) -> None:
    fnt = ImageFont.truetype(FONTE_ROTULO, 18)
    y0, hh = (FAIXA_Y0, FAIXA_H) if faixa else (0, 1920)
    cw, ch = int(W * esc), int(hh * esc)
    rows = (len(imagens) + cols - 1) // cols
    sh = Image.new("RGB", (cols * cw + (cols - 1) * 8, rows * (ch + 48)), (28, 28, 28))
    d = ImageDraw.Draw(sh)
    for k, (im, rot) in enumerate(imagens):
        x, y = (k % cols) * (cw + 8), (k // cols) * (ch + 48)
        sh.paste(im.crop((0, y0, W, y0 + hh)).resize((cw, ch), Image.LANCZOS), (x, y + 48))
        for li, txt in enumerate(rot.split("\n")[:2]):
            d.text((x + 4, y + 3 + li * 21), txt[:48], fill=(255, 230, 0), font=fnt)
    sh.save(saida, quality=88)


def pausas_longas(video: Path, ate: float, limite: float = 0.0) -> list[dict]:
    r = subprocess.run(["ffmpeg", "-hide_banner", "-t", f"{ate:.3f}", "-i", str(video), "-map", "0:a:0",
                        "-af", f"silencedetect=noise=-45dB:d={max(PAUSA_LONGA, limite)}", "-f", "null", "-"],
                       capture_output=True, text=True)
    ini = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", r.stderr)]
    fim = [(float(a), float(b)) for a, b in re.findall(r"silence_end: (-?[\d.]+) \| silence_duration: ([\d.]+)", r.stderr)]
    return [{"inicio": round(s, 2), "dur": round(d, 2)} for s, (e, d) in zip(ini, fim)]


def fundo_sob_legenda(trabalho: Path, lay: dict, corte: dict) -> list[dict]:
    """Luminância do vídeo SEM legenda por baixo de cada tela (lido do bruto, no mesmo recorte).
    Regra do usuário: aprovar a legenda no trecho de fundo mais claro antes do lote."""
    import numpy as np
    enq = ler_json(trabalho / "enquadramento.json")
    por_seg = enq.get("crops_segmento", {})
    segs = corte["segmentos"]
    out = []

    def extrai(b):
        ult = max(ln["t_in"] for ln in b["linhas"])
        t = min(b["t_out"] - 0.10, max(ult + 0.35, b["t_in"] + 0.45))
        k = max(i for i, s in enumerate(segs) if s["dst_in"] <= t + 1e-6)
        src = segs[k]["src_in"] + (t - segs[k]["dst_in"])
        cw, ch, x, y = por_seg.get(str(k), enq["crop"])
        return t, subprocess.run(["ffmpeg", "-v", "error", "-hwaccel", "cuda", "-ss", f"{src:.3f}", "-i", corte["fonte"],
                                  "-frames:v", "1", "-vf", f"crop={cw}:{ch}:{x}:{y},scale={W}:{FAIXA_H}",
                                  "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True)

    with ThreadPoolExecutor(PARALELO) as ex:
        extraidos = list(ex.map(extrai, lay["blocos"]))
    for b, (t, p) in zip(lay["blocos"], extraidos):
        if len(p.stdout) < W * FAIXA_H:
            continue
        g = np.frombuffer(p.stdout[:W * FAIXA_H], np.uint8).reshape(FAIXA_H, W)
        vals = []
        for ln in b["linhas"]:
            y0 = int(ln["cap_top"] - FAIXA_Y0)
            y1 = int(y0 + ln["cap"])
            x0, x1 = int(ln["x"]), int(ln["x"] + ln["largura"])
            reg = g[max(0, y0):max(0, y1), max(0, x0):max(0, x1)]
            if reg.size:
                vals.append(float(np.percentile(reg, 75)))
        if vals:
            out.append({"bloco": b["bloco"], "t": round(t, 2), "lum_p75": round(max(vals), 1)})
    return out


def sincronia(trabalho: Path, video: Path, corte: dict) -> list[dict]:
    """Imagem x áudio, quadro a quadro: o 2o e o penúltimo quadro de alguns segmentos do final
    têm que ser exatamente o quadro esperado do bruto (o áudio é cortado nesse quadro).
    Pegou um bug real: quadro duplicado no início do segmento = imagem 33 ms atrás do áudio."""
    import numpy as np
    enq = ler_json(trabalho / "enquadramento.json")
    segs = corte["segmentos"]

    def cinza(cmd):
        p = subprocess.run(cmd, capture_output=True, check=True)
        return np.frombuffer(p.stdout, np.uint8).reshape(108, 135).astype(float)[:45]

    escolhidos = sorted({1, len(segs) // 3, 2 * len(segs) // 3, len(segs) - 1} & set(range(len(segs))))
    base = {k: sum(s["frames"] for s in segs[:k]) for k in escolhidos}
    out = []
    for k in escolhidos:
        s = segs[k]
        cw, ch, x, y = enq.get("crops_segmento", {}).get(str(k), enq["crop"])
        for rel in (1, s["frames"] - 2):
            if rel < 0:
                continue
            # quadro n do final por busca em (n - 0,5)/fps: idêntico ao select=eq(n,...) (md5), 7x mais rápido
            f = cinza(["ffmpeg", "-v", "error", "-ss", f"{(base[k] + rel - 0.5) / FPS:.5f}", "-i", str(video),
                       "-frames:v", "1", "-vf", f"crop={W}:{FAIXA_H}:0:{FAIXA_Y0},scale=135:108",
                       "-f", "rawvideo", "-pix_fmt", "gray", "-"])
            difs = {}
            for o in (-1, 0, 1):
                n = s["frame_in"] + rel + o
                b = cinza(["ffmpeg", "-v", "error", "-ss", f"{(n - 0.5) / FPS:.5f}", "-i", corte["fonte"],
                           "-frames:v", "1", "-vf", f"crop={cw}:{ch}:{x}:{y},scale=135:108",
                           "-f", "rawvideo", "-pix_fmt", "gray", "-"])
                difs[o] = float(np.abs(f - b).mean())
            melhor = min(difs, key=difs.get)
            out.append({"seg": k, "quadro_rel": rel, "deslocamento": melhor})
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("trabalho")
    ap.add_argument("video")
    ap.add_argument("--whisper", action="store_true")
    a = ap.parse_args()
    trabalho, video = Path(a.trabalho), Path(a.video)
    qa = trabalho / "qa"
    qa.mkdir(exist_ok=True)
    lay = ler_json(trabalho / "layout.json")
    corte = ler_json(trabalho / "corte.json")
    rel: dict = {"video": str(video), "sha256": hashlib.sha256(video.read_bytes()).hexdigest(),
                 "avisos_layout": lay.get("avisos", []), "avisos_corte": corte.get("avisos", [])}
    problemas = []

    # ---- formato
    info = sonda(video)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    au = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    prof = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=profile",
                           "-of", "csv=p=0", str(video)], capture_output=True, text=True).stdout.strip()
    dur = float(info["format"]["duration"])
    rel["formato"] = {"w": v["width"], "h": v["height"], "fps": v["r_frame_rate"], "codec": v["codec_name"],
                      "perfil": prof, "pix_fmt": v["pix_fmt"], "duracao": round(dur, 3),
                      "duracao_esperada": lay["duracao_total"], "tamanho_mb": round(video.stat().st_size / 1e6, 1),
                      "audio": au and {"codec": au["codec_name"], "sr": au["sample_rate"], "canais": au["channels"]}}
    esperado = {"w": 1080, "h": 1920, "fps": "30000/1001", "codec": "h264", "pix_fmt": "yuv420p"}
    for k, val in esperado.items():
        if rel["formato"][k] != val:
            problemas.append(f"{k} = {rel['formato'][k]} (esperado {val})")
    if prof != "High":
        problemas.append(f"perfil H.264 {prof} (esperado High)")
    if not au or au["codec_name"] != "aac" or au["sample_rate"] != "48000" or int(au["channels"]) != 2:
        problemas.append(f"áudio fora do padrão (AAC 48 kHz estéreo): {rel['formato']['audio']}")
    if abs(dur - float(lay["duracao_total"])) > 0.15:
        problemas.append(f"duração {dur:.2f}s difere da esperada {lay['duracao_total']}s")
    if video.stat().st_size < 1e6:
        problemas.append("arquivo pequeno demais")

    # ---- CTA colada no fim da imagem
    fim_imagem = sum(s["frames"] for s in corte["segmentos"]) / FPS
    rel["cta"] = {"fim_imagem": round(fim_imagem, 3), "cta_inicio": lay["cta_inicio"]}
    if abs(fim_imagem - float(lay["cta_inicio"])) > 1.01 / FPS:
        problemas.append(f"CTA em {lay['cta_inicio']}s mas a imagem termina em {fim_imagem:.3f}s")
    # som de teclado padrão: 1o toque no quadro da 1a letra (±1 quadro)
    info_r = ler_json(trabalho / "render_info.json") if (trabalho / "render_info.json").exists() else {}
    if float(lay["duracao_total"]) - fim_imagem > 0.5 and info_r.get("teclado_cta", True):
        from legenda_novela import CTA_ATRASO
        from render_final import medir_teclado
        tq = medir_teclado(video, fim_imagem + CTA_ATRASO / FPS)
        rel["cta"]["teclado"] = tq
        if not tq["ok"]:
            problemas.append("som de teclado da CTA: " + (tq.get("motivo") or
                             f"1o toque {tq['desvio_ms']:+.0f} ms fora da 1a letra"))

    # ---- loudness e pico real
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(video), "-map", "0:a:0",
                        "-af", "ebur128=framelog=quiet:peak=true", "-f", "null", "-"], capture_output=True, text=True)
    m = re.search(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    tp = re.search(r"Peak:\s+(-?[\d.]+) dBFS", r.stderr)
    rel["loudness"] = {"I": float(m.group(1)) if m else None, "pico_real": float(tp.group(1)) if tp else None}
    if not m or abs(float(m.group(1)) - LUFS) > 1.0:
        problemas.append(f"loudness {m.group(1) if m else '?'} LUFS (alvo {LUFS})")
    if not tp or float(tp.group(1)) > TRUE_PEAK + 0.5:
        problemas.append(f"pico real {tp.group(1) if tp else '?'} dBTP (teto {TRUE_PEAK})")

    # ---- sincronia imagem x áudio (quadro exato)
    rel["sincronia"] = sincronia(trabalho, video, corte)
    for sc in rel["sincronia"]:
        if sc["deslocamento"] != 0:
            problemas.append(f"imagem fora de sincronia no seg{sc['seg']:02d} ({sc['deslocamento']:+d} quadro)")

    # ---- pausas longas na fala: o respiro final antes da CTA é o único silêncio longo permitido
    # o teto da pausa normal é medido em cada vídeo (corte.json "ritmo"); acima dele + 0,1 s é pausa que quebra o ritmo
    lim_pausa = float(corte.get("ritmo", {}).get("teto", 0.36)) + 0.10
    rel["pausas_longas"] = pausas_longas(video, fim_imagem, lim_pausa)
    for pz in rel["pausas_longas"]:
        if pz["inicio"] + pz["dur"] < fim_imagem - 0.05:
            problemas.append(f"silêncio de {pz['dur']}s em {pz['inicio']}s (máximo ~{lim_pausa:.2f} s, ritmo do vídeo)")

    # ---- palavra atravessando emenda (alinhamento forçado): o aligner "estica" a palavra por cima do corte quando
    #      há um FALSO COMEÇO escondido na pausa ("populi-... popularidade", +0,73 s, 09/10/2026) ou quando o fim
    #      dela foi cortado. Olhe/ouça o trecho e corrija com INICIO/PARTE na decupagem.
    pc_path = trabalho / "palavras_corte.json"
    if pc_path.exists():
        pal_c = ler_json(pc_path)
        pal_c = pal_c["palavras"] if isinstance(pal_c, dict) else pal_c
        t_em = [s["dst_in"] for s in corte["segmentos"][1:]]
        rel["palavras_na_emenda"] = []
        for w in pal_c:
            for e in t_em:
                if float(w["inicio"]) < e - 0.05 and float(w["fim"]) > e + 0.40:
                    rel["palavras_na_emenda"].append({"palavra": w["texto"], "emenda": round(e, 2),
                                                      "passa_ms": round((float(w["fim"]) - e) * 1000)})
                    problemas.append(f"palavra '{w['texto']}' atravessa a emenda de {e:.2f}s "
                                     f"(+{(float(w['fim']) - e) * 1000:.0f} ms): falso começo escondido ou fim cortado?")
        # pedaço do corte SEM NENHUMA PALAVRA (09/10/2026: 0,5 s de vento no "Existe mais gente feia" e um "vo-" de
        # falso começo antes de "Você tenta" no "As pessoas tratam você"): só ruído/respiro/começo errado
        for sg in corte["segmentos"]:
            fim_sg = sg["dst_in"] + sg["frames"] / FPS
            if sg["frames"] / FPS >= 0.2 and not any(sg["dst_in"] - 0.02 <= float(w["inicio"]) < fim_sg - 0.05
                                                     for w in pal_c):
                problemas.append(f"trecho sem palavra de {sg['dst_in']:.2f}s a {fim_sg:.2f}s (ruído ou começo "
                                 f"errado?): tire com INICIO/FIM na decupagem")

    # ---- fundo mais claro por baixo da legenda
    fundos = fundo_sob_legenda(trabalho, lay, corte)
    claro = max(fundos, key=lambda f: f["lum_p75"]) if fundos else None
    rel["fundo_mais_claro"] = claro
    rel["fundos"] = sorted(fundos, key=lambda f: -f["lum_p75"])[:5]

    # ---- folhas de quadros
    pedidos = []
    for b in lay["blocos"]:
        ult = max(ln["t_in"] for ln in b["linhas"])
        t = min(b["t_out"] - 0.10, max(ult + 0.35, b["t_in"] + 0.45))
        marca = "  << FUNDO MAIS CLARO" if claro and claro["bloco"] == b["bloco"] else ""
        rot = f"#{b['bloco']} {b['t_in']:.2f}s [{b['layout']}]{marca}\n" + " / ".join(ln["texto"] for ln in b["linhas"])
        pedidos.append((t, rot))
    with ThreadPoolExecutor(PARALELO) as ex:
        imgs = list(zip(ex.map(lambda pr: quadro(video, pr[0]), pedidos), (r for _, r in pedidos)))
    if claro:
        quadro(video, claro["t"]).crop((0, FAIXA_Y0, W, FAIXA_Y0 + FAIXA_H)).save(qa / "fundo_mais_claro.png")
    pag = 16
    for p in range(0, len(imgs), pag):
        folha(imgs[p:p + pag], 4, 0.40, qa / f"folha_blocos_{p // pag + 1:02d}.jpg")
    cta0 = float(lay["cta_inicio"])
    marcas = [(cta0 - 0.15, "ÚLTIMO QUADRO -0,15s")] + [(cta0 + dt, f"CTA +{dt:.2f}s") for dt in (0.03, 0.2, 0.5, 2.0)]
    with ThreadPoolExecutor(PARALELO) as ex:
        ctas = list(zip(ex.map(lambda m: quadro(video, m[0]), marcas), (r for _, r in marcas)))
    folha(ctas, 5, 0.22, qa / "folha_cta.jpg", faixa=False)

    # ---- fala x legenda (Whisper só na parte falada, com VAD: silêncio da CTA não vira texto)
    if a.whisper:
        wav = qa / "final16k.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-t", f"{fim_imagem:.3f}", "-i", str(video),
                        "-ac", "1", "-ar", "16000", str(wav)], check=True)
        from comum import whisper
        model = whisper()
        segs, _ = model.transcribe(str(wav), language="pt", word_timestamps=True, vad_filter=True,
                                   condition_on_previous_text=False)
        fala = [(w.start, w.end, w.word.strip(), w.probability) for s in segs for w in (s.words or [])]
        emendas = [s["dst_in"] for s in corte["segmentos"][1:]]
        linhas_txt, e_i = [], 0
        for (s0, s1, txt, pr) in fala:
            while e_i < len(emendas) and emendas[e_i] <= s0:
                linhas_txt.append(f"   ------ emenda {emendas[e_i]:.2f}s ------")
                e_i += 1
            linhas_txt.append(f"{s0:7.2f}  {txt:18s} p={pr:.2f}" + ("   <-- baixa confiança" if pr < 0.6 else ""))
        (qa / "fala_final.txt").write_text("\n".join(linhas_txt) + "\n", encoding="utf-8")
        ditos = [(s0, s1, norm(t)) for (s0, s1, t, _) in fala]
        diverg = []
        for b in lay["blocos"]:
            janela = {x for (s0, s1, x) in ditos if s1 >= b["t_in"] - 0.35 and s0 <= b["t_out"] + 0.35}
            for ln in b["linhas"]:
                for pal in ln["texto"].split():
                    n = norm(pal)
                    if not n or n.isdigit() or n in janela or (n in EQUIV and EQUIV[n] & janela):
                        continue
                    diverg.append({"bloco": b["bloco"], "t": b["t_in"], "legenda": pal, "linha": ln["texto"],
                                   "fala": " ".join(x for (s0, s1, x) in ditos
                                                    if s1 >= b["t_in"] - 0.35 and s0 <= b["t_out"] + 0.35)})
        rel["legenda_x_fala"] = diverg
        rel["fala_baixa_confianca"] = [{"t": round(s0, 2), "palavra": t, "p": round(pr, 2)}
                                       for (s0, s1, t, pr) in fala if pr < 0.6]
        # emendas em modo LITERAL, uma a uma (+-3,5 s): o Whisper normal "engole" repetição
        # ("dá aquela... dá aquela") e o prompt literal só vale na 1a janela — por isso janela curta
        import wave as _wave
        import numpy as _np
        with _wave.open(str(wav), "rb") as w_:
            aud = _np.frombuffer(w_.readframes(w_.getnframes()), _np.int16).astype(_np.float32) / 32768
        # exemplos neutros: exemplo tirado do próprio vídeo induz o Whisper a "ouvir" a frase
        prompt = ("Transcrição literal, palavra por palavra, mantendo repetições, gaguejos e hesitações: "
                  "é... é, eu, eu acho que, que o... o problema.")
        reps, lit_txt = [], []
        for e in emendas:
            a_, b_ = int(max(0.0, e - 3.5) * 16000), int(min(fim_imagem, e + 3.5) * 16000)
            sg, _ = model.transcribe(aud[a_:b_], language="pt", word_timestamps=True, vad_filter=False,
                                     condition_on_previous_text=False, initial_prompt=prompt)
            lit = [norm(w.word) for s in sg for w in (s.words or []) if norm(w.word)]
            lit_txt.append(f"emenda {e:7.2f}s: " + " ".join(lit))
            for n_ in (1, 2):
                for k in range(len(lit) - 2 * n_ + 1):
                    if lit[k:k + n_] == lit[k + n_:k + 2 * n_]:
                        reps.append({"emenda": round(e, 2), "repetido": " ".join(lit[k:k + n_])})
        # repetição INTENCIONAL decidida na revisão (anáfora: "só continue, continue trabalhando,
        # continue aparecendo"): uma palavra/expressão por linha em <trabalho>/repeticoes_ok.txt
        arq_ok = trabalho / "repeticoes_ok.txt"
        ok = {norm(x.split("#")[0]) for x in arq_ok.read_text(encoding="utf-8").splitlines()} if arq_ok.exists() else set()
        ok.discard("")
        ok.add("E")   # "e é aí", "quem ela é e...": o Whisper literal tira o acento e vira "E E" (3 falsos alarmes em 09/10/2026)
        for r_ in reps:
            r_["intencional"] = r_["repetido"].replace(" ", "") in {o.replace(" ", "") for o in ok}
        rel["repeticoes_nas_emendas"] = reps
        (qa / "emendas_literal.txt").write_text("\n".join(lit_txt) + "\n", encoding="utf-8")
        for r_ in reps:
            if not r_["intencional"]:
                problemas.append(f"repetição '{r_['repetido']}' na emenda de {r_['emenda']}s")
    rel["problemas"] = problemas
    gravar_json(qa / "relatorio.json", rel)
    print(json.dumps({"problemas": problemas, "loudness": rel["loudness"], "cta": rel["cta"],
                      "pausas_longas": rel["pausas_longas"], "formato": rel["formato"],
                      "divergencias": len(rel.get("legenda_x_fala", []))}, ensure_ascii=False))
    sys.exit(3 if problemas else 0)


if __name__ == "__main__":
    main()
