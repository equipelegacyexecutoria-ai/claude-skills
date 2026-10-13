"""Monta um gancho novo de tela dividida (imagem em cima, Clailton embaixo, legenda na emenda)
e emenda no reel original a partir do quadro de corte, sem mexer no resto.

Uso: python montar_gancho.py config.json
config: {
  "original": "original.mp4", "corte_quadro": 92,
  "avatar": "lipsync.mp4", "avatar_ini": 0.0, "avatar_fim": 4.8, "ganho_db": -3.2,
  "emenda": 806,                       # y da divisão imagem/Clailton
  "cap_y": 820, "cap_px": 62,          # centro e altura da maiúscula da legenda (medidos no original)
  "flash_quadros": 0,                  # >0: o gancho sai clareando para branco (o original tem flash)
  "rosto": {"larg": 320, "olhos_y": 1060, "cx": 590},
  "imagens": [                          (tempo do gancho)
     {"arq": "img/caixao.png", "ini": 0.0, "fim": 1.6},                       foto/desenho parado (zoom lento)
     {"clip": "original.mp4", "src": 0.2, "y0": 0, "y1": 830, "ini": 1.6, "fim": 3.0},   trecho de vídeo
  ],
  "legendas": [{"txt": "SE VOCÊ", "ini": 0.0, "fim": 0.5, "grande": false}, ...],
  "saida": "saida.mp4"
}
"""
import json, subprocess, sys, statistics
from pathlib import Path

import cv2

W, H = 1080, 1920
FPS = "30000/1001"
FONTES = Path.home() / ".claude/skills/reels-novela-clailton/fonts"
FONTE = "Inter 28pt ExtraBold"
FONTE_ARQ = FONTES / "Inter_28pt-ExtraBold.ttf"
MOD = str(Path.home() / ".claude/skills/reels-novela-clailton/models/face_detection_yunet_2023mar.onnx")
CAP_FS = 0.601         # libass: maiúscula da Inter ExtraBold = 0,601 x fs
CAP_GRANDE = 180       # palavra de destaque ("VIVO" do Padre: maiúscula ~180 px)
LARG_MAX = 960
SOMBRA = [dict(dx=0, dy=3, bord=10, blur=22, alpha="8C"),   # sombra v3: halo difuso ~45%
          dict(dx=1, dy=4, bord=2, blur=4, alpha="48")]     # contato ~72%


def fs_que_cabe(txt, fs):
    """libass: fs = altura da caixa (asc+desc = 1.21 em); mede a largura com o PIL e encolhe se passar."""
    from PIL import ImageFont
    larg = ImageFont.truetype(str(FONTE_ARQ), max(1, round(fs / 1.2104))).getlength(txt)
    return fs * min(1.0, LARG_MAX / larg) if larg else fs


def rodar(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        sys.exit(r.stderr[-3000:])
    return r


def rosto_medio(vid, ini, fim):
    cap = cv2.VideoCapture(vid)
    fps = cap.get(cv2.CAP_PROP_FPS)
    w, h = int(cap.get(3)), int(cap.get(4))
    det = cv2.FaceDetectorYN.create(MOD, "", (w, h), 0.6, 0.3, 5000)
    medidas, i = [], 0
    while True:
        ok, fr = cap.read()
        if not ok or i / fps > fim:
            break
        if i / fps >= ini and i % 3 == 0:
            _, f = det.detect(fr)
            if f is not None and len(f):
                f = max(f, key=lambda r: r[2] * r[3])
                medidas.append((f[2], (f[4] + f[6]) / 2, (f[5] + f[7]) / 2))
        i += 1
    if not medidas:
        sys.exit("rosto não encontrado")
    return w, h, [statistics.median(m[k] for m in medidas) for k in range(3)]


def quadros(vid, t0, t1, n, tam=None):
    import numpy as np
    out = []
    for t in np.linspace(t0, t1, n):
        cap = cv2.VideoCapture(vid)
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, fr = cap.read()
        if ok:
            out.append(fr if tam is None else tam(fr))
    return out


def casar_cor(original, t_c, emenda, avatar, dur, geo, base):
    """Cor e nitidez do Clailton do gancho = as do Clailton no gancho original (que já tem a cor do editor).
    Cor: casamento de histograma por canal (curvas 1D, .cube). Nitidez: compara o detalhe do rosto."""
    import numpy as np
    sw, sh, cx, cy, alt = geo
    ref = quadros(original, 0.15, max(0.3, t_c - 0.15), 8, lambda f: f[emenda:])
    nov = quadros(avatar, 0.2, max(0.4, dur - 0.2), 8,
                  lambda f: cv2.resize(f, (sw, sh), interpolation=cv2.INTER_LANCZOS4)[cy:cy + alt, cx:cx + W])
    if not ref or not nov:
        return ""
    # sem a faixa da legenda colada na emenda (texto branco puxaria a cor)
    r = np.concatenate([x[130:].reshape(-1, 3) for x in ref]); n_ = np.concatenate([x[130:].reshape(-1, 3) for x in nov])
    curvas = []
    for ch in (2, 1, 0):  # R, G, B (OpenCV é BGR)
        hr = np.cumsum(np.bincount(r[:, ch], minlength=256)).astype(float); hr /= hr[-1]
        hn = np.cumsum(np.bincount(n_[:, ch], minlength=256)).astype(float); hn /= hn[-1]
        m = np.interp(hn, hr, np.arange(256))            # valor novo -> valor do original
        m = 0.8 * m + 0.2 * np.arange(256)                 # 80%: não força demais
        m = np.convolve(np.pad(m, 4, mode="edge"), np.ones(9) / 9, mode="valid")
        curvas.append(np.clip(m / 255, 0, 1))
    cube = base / "cor.cube"
    with open(cube, "w") as f:
        f.write("LUT_1D_SIZE 256\n")
        for i in range(256):
            f.write(f"{curvas[0][i]:.6f} {curvas[1][i]:.6f} {curvas[2][i]:.6f}\n")
    # nitidez: detalhe (laplaciano) só no rosto: pula a faixa da legenda colada na emenda
    def det(lst):
        return np.median([cv2.Laplacian(cv2.cvtColor(x[150: 150 + alt // 3, W // 3: 2 * W // 3], cv2.COLOR_BGR2GRAY),
                                        cv2.CV_64F).var() for x in lst])
    d_ref, d_nov = det(ref), det(nov)
    filtro = f"lut1d=file='{str(cube).replace(chr(92), '/').replace(':', chr(92) + ':')}',"
    if d_nov < d_ref * 0.8:     # mais mole que o original: realça um pouco
        filtro += f"unsharp=5:5:{min(1.6, 0.55 * (d_ref / d_nov - 1)):.2f}:5:5:0,"
    elif d_nov > d_ref * 1.3:   # mais duro que o original: suaviza de leve
        filtro += "gblur=sigma=0.6,"
    print(f"cor casada; detalhe original {d_ref:.0f} x gancho {d_nov:.0f}")
    return filtro


def caixa_da_foto(vid, t):
    """Caixa da foto dentro de um quadro com fundo branco (ignora a faixa da legenda, y 1050-1250)."""
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", vid, "-frames:v", "1",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    im = np.frombuffer(raw, np.uint8).reshape(H, W, 3)
    m = im.min(axis=2) < 225
    m[1050:1250] = False
    ys = np.where(m.sum(axis=1) > W * 0.2)[0]
    xs = np.where(m.sum(axis=0) > 40)[0]
    c = dict(y0=int(ys.min()) + 6, y1=int(ys.max()) - 6, x0=int(xs.min()) + 6, x1=int(xs.max()) - 6)
    print("foto recortada:", c)
    return c


def t_ass(s):
    cs = round(s * 100)
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def legenda_ass(legs, arq, cap_y, cap_px):
    ev = []
    for lg in legs:
        txt = lg["txt"].upper()
        grande = lg.get("grande")
        fs = fs_que_cabe(txt, (CAP_GRANDE if grande else cap_px) / CAP_FS)
        y = cap_y + (16 if grande else 0)
        a, b = t_ass(lg["ini"]), t_ass(lg["fim"])
        for sh in SOMBRA:
            ev.append(f"Dialogue: 0,{a},{b},Cap,,0,0,0,,{{\\an5\\pos({540 + sh['dx']},{y + sh['dy']})\\fs{fs:.1f}"
                      f"\\1c&H000000&\\3c&H000000&\\bord{sh['bord']}\\shad0\\blur{sh['blur']}\\alpha&H{sh['alpha']}&}}{txt}")
        ev.append(f"Dialogue: 1,{a},{b},Cap,,0,0,0,,{{\\an5\\pos(540,{y})\\fs{fs:.1f}\\1c&HFFFFFF&\\bord0\\shad0}}{txt}")
    cab = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{FONTE},100,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,-1,0,1,0,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    Path(arq).write_text(cab + "\n".join(ev) + "\n", encoding="utf-8")


def main():
    cfg = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    base = Path(sys.argv[1]).parent
    p = lambda x: str((base / x).resolve())
    dur = cfg["avatar_fim"] - cfg["avatar_ini"]
    emenda = cfg["emenda"]
    alt_baixo = H - emenda

    # Clailton: escala para o rosto ter a mesma largura do original e olhos na mesma altura
    aw, ah, (fl, ex, ey) = rosto_medio(p(cfg["avatar"]), cfg["avatar_ini"], cfg["avatar_fim"])
    alvo = cfg["rosto"]
    s = max(alvo["larg"] / fl, (W + 2) / aw, (alt_baixo + 2) / ah)   # nunca menor que o quadro
    sw, sh = round(aw * s / 2) * 2, round(ah * s / 2) * 2
    cx = max(0, min(sw - W, round(ex * s - alvo["cx"])))
    cy = max(0, min(sh - alt_baixo, round(ey * s - (alvo["olhos_y"] - emenda))))
    print(f"Clailton {aw}x{ah} rosto {fl:.0f}px -> escala {s:.3f}, recorte x{cx} y{cy}")

    ass = base / (Path(cfg["saida"]).stem + ".ass")
    legenda_ass(cfg["legendas"], ass, cfg["cap_y"], cfg["cap_px"])

    entradas = ["-ss", f"{cfg['avatar_ini']:.3f}", "-t", f"{dur:.3f}", "-i", p(cfg["avatar"])]
    t_c = cfg["corte_quadro"] * 1001 / 30000
    cor = casar_cor(p(cfg["original"]), t_c, emenda, p(cfg["avatar"]), dur, (sw, sh, cx, cy, alt_baixo), base)
    filtros = [f"[0:v]fps={FPS},scale={sw}:{sh}:flags=lanczos,crop={W}:{alt_baixo}:{cx}:{cy},{cor}setsar=1[baixo]"]
    tops = []
    for k, im in enumerate(cfg["imagens"]):
        d = im["fim"] - im["ini"]
        n = max(1, round(d * 30000 / 1001))
        if "clip" in im:   # trecho de vídeo do próprio reel (faixa de cima ou quadro cheio)
            entradas += ["-ss", f"{im['src']:.3f}", "-t", f"{d:.3f}", "-i", p(im["clip"])]
            if im.get("auto"):   # foto com margem branca: recorta só a foto
                im.update(caixa_da_foto(p(im["clip"]), im["src"] + 0.2))
            y0, y1 = im.get("y0", 0), im.get("y1", H)
            x0, x1 = im.get("x0", 0), im.get("x1", W)
            filtros.append(f"[{k + 1}:v]fps={FPS},crop={x1 - x0}:{y1 - y0}:{x0}:{y0},"
                           f"scale={W}:{emenda}:force_original_aspect_ratio=increase:flags=lanczos,"
                           f"crop={W}:{emenda},setsar=1,trim=duration={d:.3f},setpts=PTS-STARTPTS[t{k}]")
        else:              # foto/desenho parado com zoom lento (3%)
            entradas += ["-loop", "1", "-framerate", FPS, "-t", f"{d:.3f}", "-i", p(im["arq"])]
            filtros.append(f"[{k + 1}:v]scale={W * 2}:{emenda * 2}:force_original_aspect_ratio=increase,"
                           f"crop={W * 2}:{emenda * 2},zoompan=z='1+0.03*on/{n}':x='iw/2-(iw/zoom/2)':"
                           f"y='ih/2-(ih/zoom/2)':d=1:s={W}x{emenda}:fps={FPS},setsar=1[t{k}]")
        tops.append(f"[t{k}]")
    filtros.append(f"{''.join(tops)}concat=n={len(tops)}:v=1:a=0,trim=duration={dur:.3f}[topo]")
    ass_f = str(ass).replace("\\", "/").replace(":", "\\:")
    fdir = str(FONTES).replace("\\", "/").replace(":", "\\:")
    fim_v = f"[topo][baixo]vstack,format=yuv420p,subtitles='{ass_f}':fontsdir='{fdir}'"
    nf = cfg.get("flash_quadros", 0)
    if nf:
        d_fl = nf * 1001 / 30000
        fim_v += f",fade=t=out:st={dur - d_fl:.4f}:d={d_fl:.4f}:color=white"
    filtros.append(fim_v + "[v]")
    if cfg.get("voz"):   # voz já casada com o som do original (casar_voz.py): entra como está, sem fade no fim
        n_v = sum(1 for a in entradas if a == "-i")
        entradas += ["-i", p(cfg["voz"])]
        filtros.append(f"[{n_v}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=duration={dur:.4f},"
                       f"afade=t=in:d=0.01[a]")
    else:
        ganho = cfg.get("ganho_db", 0.0)
        filtros.append(f"[0:a]aresample=48000,aformat=channel_layouts=stereo,volume={ganho}dB,alimiter=limit=0.97:level=false,"
                       f"afade=t=in:d=0.01,afade=t=out:st={dur - 0.03:.3f}:d=0.03[a]")
    # efeito sonoro do flash: o original tem um "shhh" que começa antes do quadro de corte; copia esse pedaço
    sfx = cfg.get("sfx_fim", 0)
    if sfx:
        t_c = cfg["corte_quadro"] * 1001 / 30000
        n_in = sum(1 for a in entradas if a == "-i")
        entradas += ["-ss", f"{t_c - sfx:.4f}", "-t", f"{sfx:.4f}", "-i", p(cfg["original"])]
        filtros[-1] = filtros[-1].replace("[a]", "[voz]")
        filtros.append(f"[{n_in}:a]aresample=48000,aformat=channel_layouts=stereo,"
                       f"adelay={round((dur - sfx) * 1000)}:all=1[fx];"
                       f"[voz][fx]amix=inputs=2:duration=first:normalize=0[a]")
    gancho = base / (Path(cfg["saida"]).stem + "_gancho.mov")
    rodar(["ffmpeg", "-v", "error", "-y", *entradas, "-filter_complex", ";".join(filtros),
           "-map", "[v]", "-map", "[a]", "-r", FPS, "-c:v", "libx264", "-crf", "12", "-preset", "slow",
           "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-c:a", "pcm_s16le", "-t", f"{dur:.3f}", str(gancho)])

    # emenda: gancho novo + original a partir do quadro de corte (o resto fica idêntico)
    t_corte = cfg["corte_quadro"] * 1001 / 30000
    rodar(["ffmpeg", "-v", "error", "-y", "-i", str(gancho), "-i", p(cfg["original"]),
           "-filter_complex",
           f"[1:v]trim=start={t_corte:.6f},setpts=PTS-STARTPTS[v1];"
           f"[1:a]atrim=start={t_corte:.6f},asetpts=PTS-STARTPTS,afade=t=in:d=0.01[a1];"
           f"[0:v]setpts=PTS-STARTPTS[v0];[0:a]asetpts=PTS-STARTPTS[a0];"
           f"[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]",
           "-map", "[v]", "-map", "[a]", "-r", FPS, "-c:v", "libx264", "-crf", "18", "-preset", "slow",
           "-profile:v", "high", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709",
           "-color_trc", "bt709", "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", p(cfg["saida"])])
    print("pronto:", p(cfg["saida"]))


if __name__ == "__main__":
    main()
