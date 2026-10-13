"""Corta o silêncio nas pausas do gancho e alterna o enquadramento (aberto/fechado) a cada corte,
como nos TDs editados: zoom seco no corte, olhos na mesma altura. Mexe no vídeo da boca sincronizada
(ls/<nome>.mp4), na voz (vozes/<nome>.wav) e nos tempos das palavras (vozes/frases.json); guarda os originais.
Uso: python cortar_pausas.py <W> <nome> <pausa1_ini>:<pausa1_fim>:<zoom> [...]
     cada pausa: trecho de silêncio (s) procurado; corta o miolo e deixa ~0,08 s de respiro de cada lado.
"""
import json, shutil, subprocess, sys
from pathlib import Path
import cv2, numpy as np

R = Path(sys.argv[1])
nome = sys.argv[2]
pausas = [tuple(float(x) for x in a.split(":")) for a in sys.argv[3:]]
FPS = 30000 / 1001
MOD = str(Path.home() / ".claude/skills/reels-novela-clailton/models/face_detection_yunet_2023mar.onnx")
vid, voz, frs = R / f"ls/{nome}.mp4", R / f"vozes/{nome}.wav", R / "vozes/frases.json"
for f in (vid, voz):
    bk = f.with_name(f.stem + "_semcorte" + f.suffix)
    if not bk.exists():
        shutil.copy(f, bk)
vid_o, voz_o = vid.with_name(vid.stem + "_semcorte.mp4"), voz.with_name(voz.stem + "_semcorte.wav")
FR = json.loads(frs.read_text(encoding="utf-8"))
if f"{nome}_semcorte" not in FR:
    FR[f"{nome}_semcorte"] = FR[nome]
base = FR[f"{nome}_semcorte"]
D = base["dur"]

# energia da voz para achar o ponto mais quieto de cada pausa
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(voz_o), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                     capture_output=True).stdout
a = np.frombuffer(raw, np.int16).astype(float) / 32768
def db(t0, t1):
    s = a[int(t0 * 16000):int(t1 * 16000)]; return 20 * np.log10(np.sqrt((s ** 2).mean()) + 1e-9)

cortes = []   # (ini, fim) removidos, alinhados ao quadro
for p0, p1, z in pausas:
    ts = np.arange(p0, p1, 0.01)
    quietos = [t for t in ts if db(t - 0.01, t + 0.01) < -42]
    if len(quietos) < 2:
        quietos = list(ts)
    q0, q1 = min(quietos) + 0.08, max(quietos) - 0.08
    q0, q1 = round(q0 * FPS) / FPS, round(q1 * FPS) / FPS
    if q1 - q0 >= 2 / FPS:
        cortes.append((q0, q1, z))
print("cortes:", [(round(x, 3), round(y, 3), z) for x, y, z in cortes])

# trechos mantidos e zoom de cada um
trechos, t, z_atual = [], 0.0, 1.0
for q0, q1, z in cortes:
    trechos.append((t, q0, z_atual)); t, z_atual = q1, z
trechos.append((t, round(D * FPS) / FPS, z_atual))

cap = cv2.VideoCapture(str(vid_o)); W, H = int(cap.get(3)), int(cap.get(4))
det = cv2.FaceDetectorYN.create(MOD, "", (W, H), 0.5, 0.3, 5000)
def olhos(t0, t1):
    pts = []
    for t in np.linspace(t0, t1, 6):
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000); ok, fr = cap.read()
        if not ok: continue
        _, g = det.detect(fr)
        if g is not None and len(g):
            g = max(g, key=lambda r: r[14]); pts.append(((g[4] + g[6]) / 2, (g[5] + g[7]) / 2))
    return np.median(pts, axis=0)

fil, partes_v, partes_a = [], [], []
for k, (t0, t1, z) in enumerate(trechos):
    v = f"[0:v]trim=start={t0:.5f}:end={t1:.5f},setpts=PTS-STARTPTS"
    if z > 1.0:   # fechado: punch-in com os olhos na mesma altura do aberto
        ex, ey = olhos(t0, t1)
        cw, ch = round(W / z / 2) * 2, round(H / z / 2) * 2
        x = int(np.clip(ex - cw / 2, 0, W - cw)); y = int(np.clip(ey * (1 - 1 / z), 0, H - ch))
        v += f",crop={cw}:{ch}:{x}:{y},scale={W}:{H}:flags=lanczos"
    fil.append(v + f"[v{k}]"); partes_v.append(f"[v{k}]")
    fil.append(f"[1:a]atrim=start={t0:.5f}:end={t1:.5f},asetpts=PTS-STARTPTS,afade=t=in:d=0.004,"
               f"afade=t=out:st={max(0, t1 - t0 - 0.004):.4f}:d=0.004[a{k}]"); partes_a.append(f"[a{k}]")
n = len(trechos)
fil.append("".join(partes_v) + f"concat=n={n}:v=1:a=0[v]")
fil.append("".join(partes_a) + f"concat=n={n}:v=0:a=1[a]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(vid_o), "-i", str(voz_o), "-filter_complex", ";".join(fil),
                "-map", "[v]", "-r", "30000/1001", "-c:v", "libx264", "-crf", "12", "-preset", "slow", "-pix_fmt", "yuv420p",
                str(vid), "-map", "[a]", "-c:a", "pcm_s16le", str(voz)], check=True)

# palavras com os tempos novos
def novo_t(t):
    menos = sum(q1 - q0 for q0, q1, _ in cortes if q1 <= t)
    return round(t - menos, 3)
FR[nome] = dict(dur=round(sum(t1 - t0 for t0, t1, _ in trechos), 3),
                palavras=[dict(w, i=novo_t(w["i"]), f=novo_t(w["f"])) for w in base["palavras"]],
                trechos=[[round(novo_t(t0) if k else 0, 3), z] for k, (t0, _, z) in enumerate(trechos)])
frs.write_text(json.dumps(FR, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{nome}: {D:.2f} s -> {FR[nome]['dur']:.2f} s, enquadramentos {[z for *_, z in trechos]}")
