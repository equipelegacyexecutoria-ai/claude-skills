"""Conferência de um reel com gancho novo: boca ampliada, cor do Clailton no gancho x original,
timbre e ambiente antes/depois da emenda. Uso: python conferir.py <config.json>  -> grava <saida>_qa.jpg"""
import json, subprocess, sys
from pathlib import Path
import cv2, numpy as np

cfg_arq = Path(sys.argv[1]); cfg = json.loads(cfg_arq.read_text(encoding="utf-8")); base = cfg_arq.parent
saida = base / cfg["saida"]; orig = base / cfg["original"]
D = cfg["avatar_fim"] - cfg["avatar_ini"]; t_c = cfg["corte_quadro"] * 1001 / 30000; E = cfg["emenda"]
MOD = str(Path.home() / ".claude/skills/reels-novela-clailton/models/face_detection_yunet_2023mar.onnx")


def quadro(vid, t):
    c = cv2.VideoCapture(str(vid)); c.set(cv2.CAP_PROP_POS_MSEC, t * 1000); return c.read()[1]


det = cv2.FaceDetectorYN.create(MOD, "", (1080, 1920), 0.5, 0.3, 5000)
bocas, box = [], None
for t in np.linspace(0.2, D - 0.2, 10):
    fr = quadro(saida, t)
    sub = fr[E:].copy(); det.setInputSize((sub.shape[1], sub.shape[0])); _, g = det.detect(sub)
    if g is not None and len(g):
        g = max(g, key=lambda r: r[14]); box = (int((g[10] + g[12]) / 2), int((g[11] + g[13]) / 2) + E, int(g[2] * 0.8))
    mx, my, w = box
    bocas.append(cv2.resize(fr[my - int(w * 0.5):my + int(w * 0.3), mx - w // 2:mx + w // 2], (180, 144)))
linha1 = np.hstack(bocas)


def lab_medio(frs):
    return np.mean([cv2.cvtColor(f, cv2.COLOR_BGR2LAB).reshape(-1, 3).mean(0) for f in frs], axis=0)


novo = [quadro(saida, t)[E:] for t in np.linspace(0.3, D - 0.3, 5)]
velho = [quadro(orig, t)[E:] for t in np.linspace(0.2, t_c - 0.2, 5)]
dl = lab_medio(novo) - lab_medio(velho)
lado = np.hstack([cv2.resize(novo[2], (540, int(540 * novo[2].shape[0] / 1080))),
                  cv2.resize(velho[2], (540, int(540 * velho[2].shape[0] / 1080)))])
lado = cv2.resize(lado, (1800, int(1800 * lado.shape[0] / lado.shape[1])))
cv2.putText(lado, "GANCHO NOVO", (20, 50), 0, 1.4, (0, 255, 255), 3); cv2.putText(lado, "GANCHO ORIGINAL", (920, 50), 0, 1.4, (0, 255, 255), 3)
img = np.vstack([linha1, lado[:, :1800]])
saida.with_name(saida.stem + "_qa.jpg").write_bytes(cv2.imencode(".jpg", img)[1].tobytes())


def aud(ss, t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{ss:.3f}", "-t", f"{t:.3f}", "-i", str(saida), "-ac", "1",
                          "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(float) / 32768


def info(a):
    w = 320; db = np.array([20 * np.log10(np.sqrt((a[i:i + w] ** 2).mean()) + 1e-9) for i in range(0, len(a) - w, w)])
    f = np.abs(np.fft.rfft(a)); fr = np.fft.rfftfreq(len(a), 1 / 16000)
    return np.percentile(db, 10), np.percentile(db, 90), (f * fr).sum() / f.sum()


a1, a2 = aud(max(0, D - 4), min(4, D)), aud(D, 4)
p1 = info(a1); p2 = info(a2)
print(f"{saida.name}\n  cor (Lab gancho-original): L{dl[0]:+.1f} a{dl[1]:+.1f} b{dl[2]:+.1f}\n"
      f"  ambiente (10% mais baixo) antes {p1[0]:.0f} dB / depois {p2[0]:.0f} dB | voz (90%) {p1[1]:.0f} / {p2[1]:.0f} dB"
      f" | brilho do timbre {p1[2]:.0f} / {p2[2]:.0f} Hz")
