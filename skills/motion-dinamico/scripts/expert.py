# Clailton (expert) para o Motion Dinâmico, a partir do corte já feito pela skill de reels (corte.json + enquadramento.json):
#  - voz.wav: o áudio do corte inteiro (48 kHz, emendas suaves), de audio_tratado.wav quando existir;
#  - expert_<n>.mp4: só as janelas em que ele aparece, em retrato 4:5 com o rosto no terço de cima (regra: ~10% do vídeo).
# uso: python expert.py <trabalho> <projeto> 0-3.40 40.62-43.10 [--realce]
#   --realce: curva que diminui os realces (gravação estourada).
#   O rosto é medido no próprio bruto (OpenCV), não no enquadramento.json.
import json, os, subprocess, sys

_opc = {"--wh", "--rosto-y", "--prefixo"}
args = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith("--") and sys.argv[i - 1] not in _opc]
T, PROJ, janelas = args[0], args[1], [tuple(map(float, j.split("-"))) for j in args[2:]]
REALCE = "--realce" in sys.argv
# --wh 1080x1020: outro formato (ex.: metade de baixo da tela dividida, 1080x1920 = tela cheia) com o rosto em --rosto-y
WH = tuple(map(int, sys.argv[sys.argv.index("--wh") + 1].split("x"))) if "--wh" in sys.argv else None
RY = float(sys.argv[sys.argv.index("--rosto-y") + 1]) if "--rosto-y" in sys.argv else 0.40
PREF = sys.argv[sys.argv.index("--prefixo") + 1] if "--prefixo" in sys.argv else "expert"
SEM_VOZ = "--sem-voz" in sys.argv
c = json.load(open(os.path.join(T, "corte.json"), encoding="utf-8"))
e = json.load(open(os.path.join(T, "enquadramento.json"), encoding="utf-8"))
FPS = 30000 / 1001
fonte = c["fonte"]


def medidas(arq):
    """Largura x altura do quadro como ele aparece (com a rotação gravada no arquivo). Celular em pé grava 3840x2160
    com rotação -90: o quadro real é 2160x3840 (20/10/2026: usar o 3840x2160 desenquadrou o Clailton na v1)."""
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:stream_side_data=rotation",
                        "-of", "json", arq], capture_output=True, text=True)
    st = json.loads(r.stdout)["streams"][0]
    rot = next((abs(int(float(d.get("rotation", 0)))) for d in st.get("side_data_list", []) if "rotation" in d), 0)
    return (st["height"], st["width"]) if rot in (90, 270) else (st["width"], st["height"])


FW, FH = medidas(fonte)
segs, t = [], 0.0
for s in c["segmentos"]:
    d = s["frames"] / FPS; segs.append((t, t + d, s)); t += d


def rosto_no_video():
    """Mede o rosto direto no bruto (mediana de vários quadros das janelas): o enquadramento.json da skill de reels
    nem sempre bate com o quadro inteiro (20/10/2026: rosto anotado em 37% da altura, real em ~60%)."""
    import cv2, numpy as np
    det = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    achados = []
    for a, b in janelas:
        for f in np.linspace(a + 0.2, b - 0.2, 6):
            for t0, t1, s in segs:
                if t0 <= f < t1:
                    ss = s["frame_in"] / FPS + (f - t0)
                    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{ss:.3f}", "-i", fonte, "-frames:v", "1", "-vf", "scale=960:-2", "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True)
                    g = np.frombuffer(r.stdout, np.uint8)
                    if g.size:
                        g = g.reshape(-1, 960); k = FW / 960
                        fs = det.detectMultiScale(g, 1.1, 6, minSize=(80, 80))
                        if len(fs):
                            x, y, w, h = max(fs, key=lambda q: q[2] * q[3])
                            achados.append(((x + w / 2) * k, (y + h / 2) * k, h * k))
    if not achados:
        r = e["rosto"]; return r["cx"], r["cy"], r["h"]
    m = np.median(np.array(achados), 0); return float(m[0]), float(m[1]), float(m[2])


cx, cy, fh = rosto_no_video()
# retrato 4:5: do alto da cabeça (com folga de 10%) até um pouco abaixo do queixo ou a base do quadro.
# Gravação com o rosto baixo no quadro (comum no Clailton): o recorte fica mais justo e o rosto vai para o centro.
topo_cab = cy - fh / 2 - 0.42 * fh
base = min(FH, cy + fh / 2 + 1.2 * fh)
ch = (base - topo_cab) / 0.90
y = max(0.0, topo_cab - 0.10 * ch); ch = int(min(ch, FH - y)) // 2 * 2; y = int(y)
cw = round(ch * 4 / 5 / 2) * 2
if cw > FW: cw = FW // 2 * 2
x = int(max(0, min(FW - cw, cx - cw / 2)))
if WH:  # maior recorte com a proporção pedida, rosto na altura RY
    ow, oh = WH
    cw, ch = (FW, int(FW * oh / ow)) if FW / FH < ow / oh else (int(FH * ow / oh), FH)
    cw, ch = cw // 2 * 2, ch // 2 * 2
    x = int(max(0, min(FW - cw, cx - cw / 2))); y = int(max(0, min(FH - ch, cy - RY * ch)))
print("rosto", round(cx), round(cy), round(fh))
os.makedirs(os.path.join(PROJ, "assets", "audio"), exist_ok=True)
tmp = os.path.join(PROJ, ".expert_tmp"); os.makedirs(tmp, exist_ok=True)
CUR = "0/0 0.5/0.5 0.7/0.67 0.85/0.79 1/0.93"
vf = f"crop={cw}:{ch}:{x}:{y},scale={WH[0] if WH else 1080}:{WH[1] if WH else 1350}:flags=lanczos" + (f",format=gbrp10le,curves=all='{CUR}'" if REALCE else "") + ",format=yuv420p"
for n, (a, b) in enumerate(janelas):
    partes = []
    for k, (t0, t1, s) in enumerate(segs):
        lo, hi = max(a, t0), min(b, t1)
        if hi - lo < 0.02:
            continue
        ss = (s["frame_in"] - 0.5) / FPS + (lo - t0)
        o = os.path.join(tmp, f"j{n}_{k:03d}.mkv")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss:.6f}", "-i", fonte, "-t", f"{hi - lo:.6f}", "-an", "-vf", vf,
                        "-c:v", "libx264", "-crf", "14", "-preset", "fast", o], check=True)
        partes.append(o)
    lista = os.path.join(tmp, f"j{n}.txt")
    open(lista, "w").write("".join(f"file '{p}'\n" for p in partes))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-vf", "setpts=N*1001/30000/TB", "-r", "30000/1001",
                    "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p", "-g", "15",
                    os.path.join(PROJ, "assets", f"{PREF}_{n}.mp4")], check=True)
    print(f"{PREF}_{n}.mp4", a, b)
if SEM_VOZ:
    print("ok (sem refazer a voz) | recorte", cw, ch, x, y); sys.exit(0)
aud = os.path.join(T, "audio_tratado.wav") if os.path.exists(os.path.join(T, "audio_tratado.wav")) else os.path.join(T, "audio48k.wav")
fc = ";".join(f"[0:a]atrim={s['frame_in'] / FPS:.6f}:{(s['frame_in'] + s['frames']) / FPS:.6f},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,"
              f"afade=t=out:st={max(0, s['frames'] / FPS - 0.025):.4f}:d=0.025[a{k}]" for k, s in enumerate(c["segmentos"]))
fc += ";" + "".join(f"[a{k}]" for k in range(len(c["segmentos"]))) + f"concat=n={len(c['segmentos'])}:v=0:a=1,acompressor=threshold=-20dB:ratio=2:attack=10:release=200:makeup=1,deesser=i=0.5:m=0.5:f=0.5[out]"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", aud, "-filter_complex", fc, "-map", "[out]", "-ac", "1", "-ar", "48000",
                os.path.join(PROJ, "assets", "audio", "voz.wav")], check=True)
print("ok voz.wav de", os.path.basename(aud), "| recorte", cw, ch, x, y)
