"""Conferência do reel tela dividida já renderizado.

Confere: formato (1080x1920, 29,97, duração), loudness (LUFS de comum.py, pico <= -1 dBTP), sincronia do
Clailton com o bruto (quadro a quadro em planos amostrados), trecho de vídeo congelado, tarja preta
de filme sobrando, e acha o FUNDO MAIS CLARO atrás da legenda (regra do usuário: mostrar antes do lote).
Gera em <trabalho>/qa/:
  folha_imagens.jpg    um quadro de cada imagem/trecho, com a fala e a fonte (confere a correlação)
  folha_geral_NN.jpg   o vídeo a cada 1,5 s (só se --geral; 1º vídeo do lote)
  fundo_mais_claro.png a legenda sobre o fundo mais claro do vídeo
  relatorio.txt / relatorio.json   números + fontes das imagens (créditos/direitos)
Código de saída: 0 = aprovado, 3 = reprovado.

Uso: python conferir_td.py <trabalho> <final.mp4> [--geral]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from td_comum import (FPS, H, LEG_Y, W, filtro_recorte, gravar_json, ler_json, movel, rect_plano)  # noqa: E402

import render_final as RN  # noqa: E402


def quadro(video: str, t: float, vf: str | None = None, w: int = W, h: int = H) -> np.ndarray:
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{max(0, t):.4f}", "-i", video, "-frames:v", "1"]
    if vf:
        cmd += ["-vf", vf]
    cmd += ["-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    b = subprocess.run(cmd, capture_output=True).stdout
    if len(b) < w * h * 3:
        return np.zeros((h, w, 3), np.uint8)
    return np.frombuffer(b[: w * h * 3], np.uint8).reshape(h, w, 3)


def fonte_txt(tam: int, negrito: bool = False):
    try:
        return ImageFont.truetype("arialbd.ttf" if negrito else "arial.ttf", tam)
    except OSError:
        return ImageFont.load_default()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("trabalho")
    ap.add_argument("final")
    ap.add_argument("--geral", action="store_true")
    a = ap.parse_args()
    T = Path(a.trabalho)
    V = str(Path(a.final).resolve())
    qa = T / "qa"
    qa.mkdir(exist_ok=True)
    tl = ler_json(T / "timeline.json")
    lay = ler_json(T / "layout.json")
    esc = ler_json(T / "midia" / "escolhas.json")
    corte = ler_json(T / "corte.json")
    enq = ler_json(T / "enquadramento_td.json")
    problemas, avisos = [], []

    # ---------------- formato e som
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate:format=duration",
                        "-of", "json", V], capture_output=True, text=True)
    info = json.loads(r.stdout)
    vs = next(s for s in info["streams"] if s["codec_type"] == "video")
    dur = float(info["format"]["duration"])
    if (vs["width"], vs["height"]) != (W, H):
        problemas.append(f"resolução {vs['width']}x{vs['height']}")
    if vs["r_frame_rate"] != "30000/1001":
        problemas.append(f"fps {vs['r_frame_rate']}")
    if abs(dur - lay["duracao_total"]) > 0.15:
        problemas.append(f"duração {dur:.2f}s (esperado {lay['duracao_total']:.2f}s)")
    lu = RN.medir(Path(V))
    if lu["I"] is None or abs(lu["I"] - RN.LUFS) > 0.7:
        problemas.append(f"loudness {lu['I']} LUFS")
    if lu["TP"] is not None and lu["TP"] > -0.9:
        problemas.append(f"pico {lu['TP']} dBTP")
    teclado = None                                           # som de teclado da CTA: 1o toque na 1a letra (±1 quadro)
    info_r = ler_json(T / "render_info.json") if (T / "render_info.json").exists() else {}
    if tl["cta"] and info_r.get("teclado_cta", True):
        import legenda_novela as LN
        teclado = RN.medir_teclado(Path(V), (tl["frames_fala"] + LN.CTA_ATRASO) / FPS)
        if not teclado["ok"]:
            problemas.append("som de teclado da CTA: " + (teclado.get("motivo") or
                             f"1o toque {teclado['desvio_ms']:+.0f} ms fora da 1a letra"))

    # ---------------- sincronia do Clailton (planos amostrados, quadro a quadro)
    segs, seg_f0 = corte["segmentos"], tl["segmentos_f0"]
    vis = [p for p in tl["planos"] if p["visivel"] and p["zoom"] in ("aberto", "fechado") and p["f1"] - p["f0"] >= 20
           and not movel(p)]                                # plano que se mexe não compara com recorte fixo
    amostra = [vis[int(i)] for i in np.linspace(0, len(vis) - 1, min(6, len(vis)))] if vis else []
    desvios = []
    for p in amostra:
        n = (p["f0"] + p["f1"]) // 2
        s = segs[p["seg"]]
        e = enq["segmentos"][p["seg"]]
        final = quadro(V, (n - 0.5) / FPS)                         # -ss meio quadro antes = quadro n exato
        vf = filtro_recorte(rect_plano(p, e, 0), enq["rot"], *enq["wh0"], W, H, rgb=True)
        difs = []
        for off in (-1, 0, 1):
            src = s["frame_in"] + (n - seg_f0[p["seg"]]) + off
            bruto = quadro(corte["fonte"], (src - 0.5) / FPS, vf)
            regiao = slice(0, int(H * 0.55))                       # acima da legenda
            difs.append(float(np.abs(final[regiao].astype(np.int16) - bruto[regiao].astype(np.int16)).mean()))
        melhor = int(np.argmin(difs)) - 1
        desvios.append(melhor)
        if melhor != 0 and difs[1] - min(difs) > 1.5 and min(difs) < 0.6 * difs[1]:
            problemas.append(f"sincronia: plano em {n / FPS:.2f}s casa com o quadro {melhor:+d} do bruto")

    # ---------------- imagens: folha, congelado, tarja preta
    tw, th = 216, 384
    camadas = sorted(tl["camadas"], key=lambda c: c["f0"])
    cols = 5
    rows = (len(camadas) + cols - 1) // cols
    folha = Image.new("RGB", (cols * tw, rows * (th + 58)), (25, 25, 25))
    d = ImageDraw.Draw(folha)
    f1, f2 = fonte_txt(14, True), fonte_txt(12)
    creditos = []
    for k, c in enumerate(camadas):
        tm = (c["f0"] + c["f1"]) / 2 / FPS
        fr = quadro(V, tm)
        m = esc.get(c["igual"] if c["tipo"] == "igual" else c["id"], {})
        if m.get("midia") == "video" and (c["f1"] - c["f0"]) > 20:
            # comparação em miniatura (o grão animado da película muda todo quadro); começo e fim do trecho
            def mini(a: np.ndarray) -> np.ndarray:
                return np.asarray(Image.fromarray(a).resize((135, 240), Image.BOX), dtype=np.float32)
            ini2 = mini(quadro(V, min(c["f1"] - 2, c["f0"] + 3) / FPS))
            fim1, fim2 = mini(quadro(V, (c["f1"] - 2) / FPS)), mini(quadro(V, (c["f1"] - 9) / FPS))
            if np.abs(mini(fr) - ini2).mean() < 0.5:
                avisos.append(f"{c['id']}: trecho de vídeo parece congelado")
            elif np.abs(fim1 - fim2).mean() < 0.5:
                avisos.append(f"{c['id']}: trecho congela no fim (vídeo mais curto que o uso)")
        area = fr[:EMENDA_TOPO(c)] if c["layout"] in ("topo", "dividida") else fr
        # tarja de verdade tem degrau: preto na borda e imagem logo depois (cortina escura não é tarja)
        lum = area.reshape(area.shape[0], -1).mean(1)
        if (lum[:40].max() < 8 and lum[40:120].mean() > lum[:40].mean() + 12) or \
                (lum[-40:].max() < 8 and lum[-120:-40].mean() > lum[-40:].mean() + 12):
            avisos.append(f"{c['id']}: faixa preta na borda da imagem (tarja de filme?)")
        r_, c_ = divmod(k, cols)
        folha.paste(Image.fromarray(fr).resize((tw, th)), (c_ * tw, r_ * (th + 58) + 58))
        d.text((c_ * tw + 3, r_ * (th + 58) + 2), f"{c['id']} {c['f0'] / FPS:.1f}s {c['layout']}", fill=(255, 220, 0), font=f1)
        d.text((c_ * tw + 3, r_ * (th + 58) + 20), c["texto"][:34], fill=(235, 235, 235), font=f2)
        d.text((c_ * tw + 3, r_ * (th + 58) + 37), (m.get("url") or "")[8:44], fill=(150, 150, 150), font=f2)
        if c["tipo"] != "igual":
            creditos.append({"id": c["id"], "tempo": round(c["f0"] / FPS, 2), "fala": c["texto"], "fonte": m.get("url", ""),
                             "titulo": m.get("titulo", "")})
            if m.get("marca_flag"):
                avisos.append(f"{c['id']}: possível marca d'água (detector {m.get('marca', 0):.2f}): conferir em tamanho real")
            if m.get("logo"):
                avisos.append(f"{c['id']}: logo de canal/streaming no canto do trecho (LOGO?): troque ou aceite")
    if folha.width and folha.height:          # edição simples (sem imagens): não há folha de imagens
        folha.save(qa / "folha_imagens.jpg", quality=86)

    # ---------------- fundo mais claro atrás da legenda (regra do usuário)
    piores = []
    for t in tl["legendas"][::2]:
        tm = (t["f0"] + min(t["f1"], tl["frames_fala"])) / 2 / FPS
        fr = quadro(V, tm)
        caixa = fr[int(LEG_Y) - 30:int(LEG_Y) + 30, 240:840].astype(np.float32).mean(2)
        fundo = float(np.percentile(caixa, 35))                    # o texto é branco: pega o fundo
        piores.append((fundo, tm, t["texto"]))
    piores.sort(reverse=True)
    if piores:
        fundo, tm, texto = piores[0]
        fr = quadro(V, tm)
        crop = Image.fromarray(fr[int(LEG_Y) - 160:int(LEG_Y) + 160, 90:990])
        crop.save(qa / "fundo_mais_claro.png")
        if fundo > 200:
            avisos.append(f"legenda sobre fundo muito claro em {tm:.1f}s (\"{texto}\", fundo {fundo:.0f}): conferir qa/fundo_mais_claro.png")

    # ---------------- folha geral
    if a.geral:
        passo, cols_g, tg, hg = 1.5, 10, 162, 288
        ts = np.arange(0, dur - 0.05, passo)
        por = 60
        for fi in range(0, len(ts), por):
            grupo = ts[fi:fi + por]
            rows_g = (len(grupo) + cols_g - 1) // cols_g
            fg = Image.new("RGB", (cols_g * tg, rows_g * (hg + 16)), (30, 30, 30))
            dg = ImageDraw.Draw(fg)
            for k, t in enumerate(grupo):
                rr, cc = divmod(k, cols_g)
                fg.paste(Image.fromarray(quadro(V, t)).resize((tg, hg)), (cc * tg, rr * (hg + 16) + 16))
                dg.text((cc * tg + 3, rr * (hg + 16) + 1), f"{t:.1f}s", fill=(255, 255, 0), font=f2)
            fg.save(qa / f"folha_geral_{fi // por + 1:02d}.jpg", quality=84)

    st = tl["stats"]
    rel = {"video": V, "duracao": round(dur, 2), "loudness": lu, "teclado_cta": teclado, "sincronia_desvios": desvios, "stats": st,
           "problemas": problemas, "avisos": avisos + [x for x in tl.get("avisos", []) if "tempo mínimo" not in x],
           "ajustes": [x for x in tl.get("avisos", []) if "tempo mínimo" in x], "creditos": creditos}
    gravar_json(qa / "relatorio.json", rel)
    L = [f"{Path(V).name}: {dur:.1f}s · {lu['I']} LUFS · pico {lu['TP']} dBTP · sincronia {desvios}",
         f"imagem em tela cheia {st['imagem_tela_cheia']:.0%} · dividida {st['dividida']:.0%} · Clailton {st['clailton_cheio']:.0%} "
         f"(fechado {st['fechado_do_clailton']:.0%}) · {st['imagens']} imagens ({st['imagens_por_min']}/min)",
         "PROBLEMAS: " + ("; ".join(problemas) if problemas else "nenhum"),
         "AVISOS: " + ("; ".join(rel["avisos"]) if rel["avisos"] else "nenhum"),
         "AJUSTES AUTOMÁTICOS (tempo mínimo na tela): " + ("; ".join(rel["ajustes"]) if rel["ajustes"] else "nenhum"),
         "", "FONTES DAS IMAGENS:"]
    L += [f"  {c['id']} {c['tempo']:6.1f}s | {c['fala'][:40]:40s} | {c['fonte']}" for c in creditos]
    (qa / "relatorio.txt").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[:5]))
    print(f"folhas: {qa / 'folha_imagens.jpg'}, {qa / 'fundo_mais_claro.png'}" + (" + folha_geral_NN.jpg" if a.geral else ""))
    sys.exit(3 if problemas else 0)


def EMENDA_TOPO(c: dict) -> int:
    from td_comum import EMENDA
    return EMENDA


if __name__ == "__main__":
    main()
