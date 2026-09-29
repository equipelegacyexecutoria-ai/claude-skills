"""Exporta o reel tela dividida como projeto para o Premiere (XML do Final Cut 7 / xmeml v5).

Pasta "<nome> - PREMIERE/" ao lado do vídeo final:
  <nome>.xml            File > Import no Premiere: cria a sequência 1080x1920 29,97
  midia/                imagens e trechos já recortados no layout (troque à vontade)
  legenda_alpha.mov     legenda + tarjas + números + CTA com transparência (QuickTime Animation)
  legenda.srt           a mesma legenda como texto editável (Premiere: importar como legenda)
  audio_final.wav       o áudio final (referência; a trilha A3 vem desligada)
  estilo_textura.png    a textura FIXA da camada película (papel + retícula, sobre cinza 128): arraste para
                        uma trilha acima de tudo e use o modo de mesclagem "Sobrepor" (Overlay). A cor
                        contida, a vinheta, o grão animado e a poeira ficam só no MP4 (Lumetri: saturação
                        85, curva em S leve, vinheta -0,2 chega perto)

Trilhas:
  V1  Clailton: o BRUTO 4K, um clipe por plano (entrada/saída exatas, com sobra para ajustar
      o corte), Movimento com escala/posição/rotação reproduzindo aberto, fechado e dividida;
      plano com zoom animado (keyframes, ancorado nos olhos) vai já pronto: midia/clailton_zoom_NNN.mp4
  V2  imagens e vídeos (já no recorte do layout; foto com zoom-out em quadros-chave)
  V3  legenda_alpha.mov
  A1/A2  áudio do bruto por trecho (canais 1 e 2) com o ganho da normalização
  A3  audio_final.wav (desligada)
Não vai para o XML: o flash de saída da abertura, o limitador de pico e a camada película (ficam só no
MP4; a textura fixa vai à parte em estilo_textura.png).

Uso: python premiere_td.py <trabalho> <final.mp4>
"""
from __future__ import annotations

import html
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from td_comum import (EMENDA, FPS, FPS_DEN, FPS_NUM, H, W, ZOOM_FOTO, ZOOM_FOTO_MAX, ler_json,  # noqa: E402
                      wh_video)
from render_td import GPU, Cartao, Imagem, area_util, cmd_bruto, filtro_trecho, quadro_rect  # noqa: E402
from td_comum import filtro_recorte, movel, rect_plano, regiao_plano  # noqa: E402
from midia_util import caixa_cover  # noqa: E402


def exportar_zoom(fonte: Path, entrada: int, p: dict, e: dict, rot: int, w0: int, h0: int, dest: Path) -> None:
    """Plano móvel (zoom animado ou ajuste dos olhos, em keyframes): sai já pronto em 1080x1920, igual ao
    render (o Movimento do Premiere não reproduz a mesma curva em volta dos olhos)."""
    n = p["f1"] - p["f0"]
    reg, ow, oh = regiao_plano(p, e)
    dec = subprocess.Popen(cmd_bruto(str(fonte), entrada, n, filtro_recorte(reg, rot, w0, h0, ow, oh, rgb=True), GPU),
                           stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", f"{FPS_NUM}/{FPS_DEN}", "-i", "-", "-vf",
                            "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p", "-c:v", "libx264", "-crf", "14",
                            "-preset", "medium", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                            str(dest)], stdin=subprocess.PIPE)
    ult = None
    for k in range(n):
        b = dec.stdout.read(ow * oh * 3)
        if len(b) == ow * oh * 3:
            ult = np.frombuffer(b, np.uint8).reshape(oh, ow, 3)
        if ult is not None:
            enc.stdin.write(np.ascontiguousarray(quadro_rect(ult, reg, rect_plano(p, e, k))).tobytes())
    enc.stdin.close()
    enc.wait()
    dec.wait()


GRANDE = 1.25                    # foto exportada 25% maior (o zoom no Premiere não amplia)


def url(p: Path) -> str:
    s = str(Path(p).resolve()).replace("\\", "/")
    return "file://localhost/" + quote(s, safe="/:")


def esc(s: str) -> str:
    return html.escape(str(s), quote=False)


RATE = "<rate><timebase>30</timebase><ntsc>TRUE</ntsc></rate>"


class Arquivos:
    def __init__(self):
        self.ids: dict[str, str] = {}

    def ref(self, p: Path, dur: int, w: int | None, h: int | None, audio_ch: int = 0, video: bool = True) -> str:
        k = str(Path(p).resolve())
        if k in self.ids:
            return f'<file id="{self.ids[k]}"/>'
        fid = f"file-{len(self.ids) + 1}"
        self.ids[k] = fid
        media = ""
        if video and w:
            media += (f"<video><samplecharacteristics>{RATE}<width>{w}</width><height>{h}</height>"
                      f"<pixelaspectratio>square</pixelaspectratio></samplecharacteristics></video>")
        if audio_ch:
            media += (f"<audio><samplecharacteristics><depth>16</depth><samplerate>48000</samplerate></samplecharacteristics>"
                      f"<channelcount>{audio_ch}</channelcount></audio>")
        return (f'<file id="{fid}"><name>{esc(Path(p).name)}</name><pathurl>{url(p)}</pathurl>{RATE}'
                f"<duration>{dur}</duration><media>{media}</media></file>")


def movimento(escala, rot: float = 0.0, cx: float = 0.0, cy: float = 0.0) -> str:
    """Basic Motion. escala: número ou [(quadro, valor), ...]. Centro normalizado pelo tamanho da
    sequência, (0,0) = meio do quadro, y para baixo."""
    if isinstance(escala, (int, float)):
        esc_xml = f"<value>{escala:.3f}</value>"
    else:
        esc_xml = "".join(f"<keyframe><when>{q}</when><value>{v:.3f}</value></keyframe>" for q, v in escala)
    return ("<filter><effect><name>Basic Motion</name><effectid>basic</effectid><effectcategory>motion</effectcategory>"
            "<effecttype>motion</effecttype><mediatype>video</mediatype>"
            f"<parameter authoringApp=\"PremierePro\"><parameterid>scale</parameterid><name>Scale</name><valuemin>0</valuemin>"
            f"<valuemax>1000</valuemax>{esc_xml}</parameter>"
            f"<parameter authoringApp=\"PremierePro\"><parameterid>rotation</parameterid><name>Rotation</name>"
            f"<valuemin>-8640</valuemin><valuemax>8640</valuemax><value>{rot:.2f}</value></parameter>"
            f"<parameter authoringApp=\"PremierePro\"><parameterid>center</parameterid><name>Center</name>"
            f"<value><horiz>{cx:.6f}</horiz><vert>{cy:.6f}</vert></value></parameter>"
            "</effect></filter>")


def nivel(db: float) -> str:
    lin = 10 ** (db / 20)
    return ("<filter><effect><name>Audio Levels</name><effectid>audiolevels</effectid><effectcategory>audiolevels"
            "</effectcategory><effecttype>audiolevels</effecttype><mediatype>audio</mediatype><parameter>"
            f"<parameterid>level</parameterid><name>Level</name><valuemin>0</valuemin><valuemax>3.98109</valuemax>"
            f"<value>{lin:.5f}</value></parameter></effect></filter>")


def clip(cid: str, nome: str, ini: int, fim: int, entrada: int, saida: int, arquivo: str, extra: str = "",
         ligado: bool = True, trilha_fonte: tuple[str, int] | None = None, dur_fonte: int | None = None) -> str:
    st = ""
    if trilha_fonte:
        st = f"<sourcetrack><mediatype>{trilha_fonte[0]}</mediatype><trackindex>{trilha_fonte[1]}</trackindex></sourcetrack>"
    return (f'<clipitem id="{cid}"><name>{esc(nome)}</name><enabled>{"TRUE" if ligado else "FALSE"}</enabled>'
            f"<duration>{dur_fonte or (saida - entrada)}</duration>{RATE}<start>{ini}</start><end>{fim}</end>"
            f"<in>{entrada}</in><out>{saida}</out>{arquivo}{st}{extra}</clipitem>")


def srt(tl: dict, destino: Path) -> None:
    def ts(n: int) -> str:
        ms = int(round(n / FPS * 1000))
        h, ms = divmod(ms, 3600000)
        m, ms = divmod(ms, 60000)
        s, ms = divmod(ms, 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    linhas = []
    for k, t in enumerate(tl["legendas"], 1):
        linhas += [str(k), f"{ts(t['f0'])} --> {ts(min(t['f1'], tl['frames_fala']))}", t["texto"], ""]
    destino.write_text("\n".join(linhas), encoding="utf-8")


def main() -> None:
    T = Path(sys.argv[1]).resolve()
    final = Path(sys.argv[2]).resolve()
    nome = final.stem.replace(" - EDITADO", "")
    P = final.parent / f"{nome} - PREMIERE"
    M = P / "midia"
    M.mkdir(parents=True, exist_ok=True)
    tl = ler_json(T / "timeline.json")
    corte = ler_json(T / "corte.json")
    enq = ler_json(T / "enquadramento_td.json")
    escs = ler_json(T / "midia" / "escolhas.json")
    lay = ler_json(T / "layout.json")
    loud = json.loads((T / "render_info.json").read_text(encoding="utf-8")).get("loudness", {}) \
        if (T / "render_info.json").exists() else {}
    ganho = float(loud.get("ganho_db", 0.0))
    fonte = Path(corte["fonte"])
    rot, (w0, h0) = enq["rot"], enq["wh0"]
    rw, rh = enq["wh_rot"]
    F_FALA, F_TOTAL = tl["frames_fala"], lay["frames_total"]
    seg_f0 = tl["segmentos_f0"]
    segs = corte["segmentos"]
    dur_bruto = int(float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                          str(fonte)], capture_output=True, text=True).stdout.strip()) * FPS)
    A = Arquivos()

    # ---------------- V1: Clailton do bruto
    v1 = []
    for i, p in enumerate(tl["planos"]):
        s, e = segs[p["seg"]], enq["segmentos"][p["seg"]]
        zoom = p["zoom"] if p["visivel"] else "aberto"
        x, y, w, h = rect_plano(p, e, 0) if p["visivel"] else e["aberto"]
        if zoom == "dividida":
            out_w, out_cx, out_cy = W, W / 2, EMENDA + (H - EMENDA) / 2
        else:
            out_w, out_cx, out_cy = W, W / 2, H / 2
        s_ = out_w / w
        X = out_cx + s_ * (rw / 2 - (x + w / 2))
        Y = out_cy + s_ * (rh / 2 - (y + h / 2))
        entrada = s["frame_in"] + (p["f0"] - seg_f0[p["seg"]])
        if movel(p) and p["visivel"]:                       # zoom animado / olhos na linha: pronto em midia/
            n = p["f1"] - p["f0"]
            dest = M / f"clailton_zoom_{i:03d}.mp4"
            if not dest.exists():
                exportar_zoom(fonte, entrada, p, e, rot, w0, h0, dest)
            v1.append(clip(f"v1-{i}", "Clailton zoom animado", p["f0"], p["f1"], 0, n, A.ref(dest, n, W, H),
                           movimento(100.0), dur_fonte=n))
            continue
        v1.append(clip(f"v1-{i}", f"Clailton {zoom}", p["f0"], p["f1"], entrada, entrada + p["f1"] - p["f0"],
                       A.ref(fonte, dur_bruto, w0, h0, audio_ch=2), movimento(100 * s_, rot, (X - W / 2) / W, (Y - H / 2) / H),
                       dur_fonte=dur_bruto))

    # ---------------- V2: imagens e vídeos já recortados
    v2 = []
    for c in sorted(tl["camadas"], key=lambda c: c["f0"]):
        m = escs[c["igual"] if c["tipo"] == "igual" else c["id"]]
        n = c["f1"] - c["f0"]
        band = c["layout"] in ("topo", "dividida")
        if m["midia"] == "video":
            dest = M / f"{c['id']}.mov" if band else M / f"{c['id']}.mp4"
            if not dest.exists():
                ss, vf, ow, oh = filtro_trecho(m, c)            # mesmo recorte e entrada do render
                vf += ",tpad=stop_mode=clone:stop_duration=5"
                if band:
                    vf += f",format=rgba,pad={W}:{H}:0:0:color=black@0.0"
                    enc = ["-c:v", "qtrle", "-pix_fmt", "argb"]
                else:
                    enc = ["-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p"]
                subprocess.run(["ffmpeg", "-v", "error", "-y"] + ss + ["-i", m["arquivo"], "-frames:v", str(n + 15), "-an",
                                                                     "-vf", vf] + enc + [str(dest)], check=True)
            v2.append(clip(f"v2-{c['id']}", f"{c['id']} {c['texto'][:30]}", c["f0"], c["f1"], 0, n,
                           A.ref(dest, n + 15, W, H), movimento(100.0), dur_fonte=n + 15))
            continue
        # imagem parada
        if c["layout"] == "cartao":
            dest = M / f"{c['id']}.jpg"
            Image.fromarray(Cartao(m["arquivo"]).quadro(1.0)).save(dest, quality=95)
            esc_kf = 100.0
        elif band:
            dest = M / f"{c['id']}.png"
            bw, bh = int(W * GRANDE), int(EMENDA * GRANDE)
            faixa = Imagem(m["arquivo"], bw, bh, m.get("rostos"), None, 0.0).quadro(1.0)
            tela = np.zeros((int(H * GRANDE), bw, 4), np.uint8)
            tela[:bh, :, :3] = faixa
            tela[:bh, :, 3] = 255
            Image.fromarray(tela, "RGBA").save(dest)
            esc_kf = 100.0 / GRANDE
        else:
            dest = M / f"{c['id']}.jpg"
            d = n / FPS
            z = min(ZOOM_FOTO_MAX, ZOOM_FOTO * d) if c.get("zoom") not in ("0", "nao") else 0.0
            Image.fromarray(Imagem(m["arquivo"], int(W * GRANDE), int(H * GRANDE), m.get("rostos"), None, z).quadro(1.0)
                            ).save(dest, quality=95)
            base = 100.0 / GRANDE
            esc_kf = [(0, base * (1 + z)), (n, base)] if z > 0 else base
        wimg, himg = Image.open(dest).size
        v2.append(clip(f"v2-{c['id']}", f"{c['id']} {c['texto'][:30]}", c["f0"], c["f1"], 0, n,
                       A.ref(dest, 108000, wimg, himg), movimento(esc_kf), dur_fonte=108000))

    # ---------------- V3: legenda com transparência (+ SRT)
    leg = P / "legenda_alpha.mov"
    ass_rgb = T / "_legenda_rgb.ass"
    ass_rgb.write_text((T / "legenda.ass").read_text(encoding="utf-8").replace("YCbCr Matrix: TV.709", "YCbCr Matrix: None"),
                       encoding="utf-8")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    f"color=c=black@0.0:s={W}x{H}:r={FPS_NUM}/{FPS_DEN}:d={F_TOTAL / FPS:.3f},format=rgba",
                    "-vf", "ass=_legenda_rgb.ass:fontsdir=fonts:alpha=1", "-c:v", "qtrle", "-pix_fmt", "argb", str(leg)],
                   check=True, cwd=T)
    ass_rgb.unlink(missing_ok=True)
    v3 = [clip("v3-leg", "legenda", 0, F_TOTAL, 0, F_TOTAL, A.ref(leg, F_TOTAL, W, H), dur_fonte=F_TOTAL)]
    srt(tl, P / "legenda.srt")
    # textura fixa da camada película (no modo Sobrepor, cinza 128 = neutro e o desvio passa 1:1 nos meios-tons)
    from td_comum import ESTILO_FORCA
    forca = tl.get("estilo") if tl.get("estilo") is not None else ESTILO_FORCA
    if forca > 0:
        from estilo_td import Estilo
        tex = np.clip(128 + Estilo(forca).papel, 0, 255).astype(np.uint8)
        Image.fromarray(np.dstack([tex] * 3)).save(P / "estilo_textura.png")

    # ---------------- áudio
    a1, a2 = [], []
    for k, s in enumerate(segs):
        ini, fim = seg_f0[k], seg_f0[k] + s["frames"]
        for lista, ch in ((a1, 1), (a2, 2)):
            lista.append(clip(f"a{ch}-{k}", f"voz {k:02d}", ini, fim, s["frame_in"], s["frame_in"] + s["frames"],
                              A.ref(fonte, dur_bruto, w0, h0, audio_ch=2), nivel(ganho), trilha_fonte=("audio", ch),
                              dur_fonte=dur_bruto))
    af = P / "audio_final.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(final), "-vn", "-c:a", "pcm_s16le", str(af)], check=True)
    a3 = [clip("a3-final", "audio final (referência)", 0, F_TOTAL, 0, F_TOTAL,
               A.ref(af, F_TOTAL, None, None, audio_ch=2, video=False), ligado=False, trilha_fonte=("audio", 1),
               dur_fonte=F_TOTAL)]

    def trilha(itens: list[str]) -> str:
        return "<track>" + "".join(itens) + "</track>"

    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>\n<xmeml version="5">'
           f'<sequence id="sequence-1"><name>{esc(nome)} TD</name><duration>{F_TOTAL}</duration>{RATE}'
           "<timecode><rate><timebase>30</timebase><ntsc>TRUE</ntsc></rate><string>00:00:00;00</string><frame>0</frame>"
           "<displayformat>DF</displayformat></timecode><media><video><format><samplecharacteristics>"
           f"{RATE}<width>{W}</width><height>{H}</height><anamorphic>FALSE</anamorphic>"
           "<pixelaspectratio>square</pixelaspectratio><fielddominance>none</fielddominance></samplecharacteristics>"
           "</format>" + trilha(v1) + trilha(v2) + trilha(v3) + "</video><audio>"
           "<format><samplecharacteristics><depth>16</depth><samplerate>48000</samplerate></samplecharacteristics></format>"
           + trilha(a1) + trilha(a2) + trilha(a3) + "</audio></media></sequence></xmeml>\n")
    (P / f"{nome}.xml").write_text(xml, encoding="utf-8")
    import xml.dom.minidom as md
    md.parseString(xml.encode("utf-8"))                       # confere se o XML é válido
    print(f"ok: {P / (nome + '.xml')} · V1 {len(v1)} planos do bruto · V2 {len(v2)} imagens · A1/A2 {len(a1)} trechos "
          f"(+{ganho:.1f} dB) · legenda_alpha.mov + legenda.srt")


if __name__ == "__main__":
    main()
