"""Enquadramento 9:16 com o rosto de QUEM FALA centralizado.

Diferença para o autoframe da skill: lá a troca de locutor dentro do mesmo plano
vira um pan lento (150 px/s) depois de ~6s de evidência, e quem fala é decidido
por movimento de boca — que aqui errou: no plano das convidadas, quem escuta bebe
água, olha em volta e "ganha" do locutor.

Aqui:
  - QUEM fala: pela VOZ (voz.py, MFCC+GMM treinado no próprio episódio; 16/16
    frases certas na validação), frase a frase pelo timing por palavra;
  - ONDE está o rosto: YuNet (detector da skill), por plano de câmera;
  - lugar fixo das convidadas: Fernanda à esquerda, Jane à direita (conferido
    nos dois ângulos da câmera delas);
  - troca de pessoa = corte seco no meio da pausa entre as frases.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np

SK = Path.home() / ".claude" / "skills" / "corte-viral"
if not SK.exists():
    SK = next((Path.home() / ".claude" / "skills" / "synced").glob("*/corte-viral"), SK)
sys.path.insert(0, str(SK))
sys.path.insert(0, str(Path(__file__).parent))
from scripts import active_speaker as AS  # noqa: E402
from scripts.framing import detect_cuts  # noqa: E402
from scripts.autoframe import anchor_from_cx  # noqa: E402
from voz import Voz, phrases  # noqa: E402

FPS = 5.0
# OpenCV no Windows não abre caminho com acento ("Edições"): o modelo fica em %LOCALAPPDATA%
MODEL = str(Path(os.environ["LOCALAPPDATA"]) / "corte-viral" / "models" / "face_detection_yunet_2023mar.onnx")
SRC_W, SRC_H = 1920, 1080
DET_W = 960.0
MIN_COVER = 0.35           # rosto precisa aparecer em >=35% das amostras do plano
TARGET_FACE_H = 0.17       # altura do rosto na saída (fração de 1920)
MAX_ZOOM = 1.30            # fonte 1080p: acima disso começa a borrar
MIN_RUN = 1.0              # trecho de locutor mais curto que isso é absorvido pelos vizinhos
MIN_MARGIN = 0.15          # margem mínima de log-verossimilhança para confiar na voz
SEATS = ["fernanda", "jane"]   # plano das convidadas, da esquerda para a direita


def face_box(tr, a=None, b=None):
    fr = [f for f in tr.frames if (a is None or a <= f[0] < b)] or tr.frames
    cx = float(np.median([f[1] for f in fr])) * SRC_W / DET_W
    fh = float(np.median([f[4] for f in fr])) * SRC_W / DET_W
    return cx, fh


def zoom_for(fh):
    frac = fh / SRC_H
    return 1.0 if frac <= 0 else float(min(MAX_ZOOM, max(1.0, TARGET_FACE_H / frac)))


def absorb_short(segs):
    """segs: [[a, b, alvo, motivo]] contíguos. Funde iguais e absorve curtos."""
    def fuse(xs):
        out = []
        for x in xs:
            if out and out[-1][2] == x[2]:
                out[-1][1] = x[1]
            else:
                out.append(list(x))
        return out
    segs = fuse(segs)
    changed = True
    while changed and len(segs) > 1:
        changed = False
        for j, sg in enumerate(segs):
            if sg[1] - sg[0] < MIN_RUN:
                if j == 0:
                    k = 1
                elif j == len(segs) - 1:
                    k = j - 1
                else:
                    k = j - 1 if segs[j - 1][1] - segs[j - 1][0] >= segs[j + 1][1] - segs[j + 1][0] else j + 1
                segs[k][0], segs[k][1] = min(sg[0], segs[k][0]), max(sg[1], segs[k][1])
                segs.pop(j)
                segs = fuse(segs)
                changed = True
                break
    return segs


def analyze(video, a, b, words, voz):
    cuts = detect_cuts(video, a, b)
    bounds = [a] + cuts + [b]
    runs, diag = [], []
    for i in range(len(bounds) - 1):
        s, e = bounds[i], bounds[i + 1]
        if e - s < 0.2:
            continue
        tracks, _ = AS.analyze_shot(video, s, e, MODEL, None)
        n_samples = max(1, int((e - s) * FPS))
        tracks = [t for t in tracks if len(t.frames) >= max(3, MIN_COVER * n_samples)]
        tracks.sort(key=lambda t: face_box(t)[0])
        vozes = []
        for (pa, pb, txt) in phrases(words, s, e):
            quem, marg, _ = voz.who(pa, pb) if pb - pa >= 0.35 else (None, 0.0, {})
            vozes.append((pa, pb, quem if marg >= MIN_MARGIN else None, round(marg, 2), txt))
        d = {"plano": [round(s, 2), round(e, 2)], "rostos": len(tracks),
             "x_rostos": [int(face_box(t)[0]) for t in tracks],
             "vozes": [(round(pa, 2), round(pb, 2), q, m, t[:40]) for pa, pb, q, m, t in vozes]}
        if not tracks:
            runs.append([s, e, SRC_W / 2, 0.0, "centro", "sem rosto detectado"])
            diag.append(d)
            continue
        if len(tracks) == 1:
            cx, fh = face_box(tracks[0])
            falantes = sorted({v[2] for v in vozes if v[2]})
            runs.append([s, e, cx, fh, "único rosto no plano", f"plano com um rosto; vozes: {falantes}"])
            diag.append(d)
            continue
        if len(tracks) > 2:
            d["aviso"] = "mais de 2 rostos: usando os 2 maiores"
            tracks = sorted(sorted(tracks, key=lambda t: -face_box(t)[1])[:2], key=lambda t: face_box(t)[0])
        seat = {SEATS[k]: tracks[k] for k in range(2)}
        # voz PALAVRA A PALAVRA (janela de 1s em volta de cada palavra): pega troca de
        # pessoa dentro de frase corrida ("cresceu duzentos e..." / "É, 239%...")
        ws = [w for w in words if w["end"] > s and w["start"] < e]
        buf = voz.load(s, e)
        rotulo = []
        for w in ws:
            c = (w["start"] + w["end"]) / 2
            q, marg = voz.who_buf(buf, s, max(s, c - 0.5), min(e, c + 0.5))
            rotulo.append(q if (q and marg >= 0.3) else None)
        first_guest = next((q for q in rotulo if q in seat), None)
        segs, prev = [], None
        for w, q in zip(ws, rotulo):
            if q in seat:
                alvo, why = q, f"voz {q}"
            else:
                alvo = prev or first_guest or "jane"
                why = f"voz {q or 'incerta'}: mantém {alvo}"
            if segs and segs[-1][2] == alvo:
                segs[-1][1] = w["end"]
            else:
                segs.append([w["start"], w["end"], alvo, why])
            prev = alvo
        if not segs:
            segs = [[s, e, first_guest or "jane", "sem fala no plano"]]
        for j in range(len(segs) - 1):
            mid = (segs[j][1] + segs[j + 1][0]) / 2
            segs[j][1] = segs[j + 1][0] = mid
        segs[0][0], segs[-1][1] = max(s, segs[0][0]) if False else s, e
        d["palavras"] = [(round(w["start"], 2), w["word"], q) for w, q in zip(ws, rotulo)]
        for (ra, rb, alvo, why) in absorb_short(segs):
            cx, fh = face_box(seat[alvo], ra, rb)
            runs.append([ra, rb, cx, fh, alvo, why])
        diag.append(d)
    return runs, diag


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--transcript", required=True)
    ap.add_argument("--intervals", required=True, help='JSON {"clip_id": [[a,b],...]}')
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    tr = json.loads(Path(a.transcript).read_text(encoding="utf-8"))
    words = [w for s in tr["segments"] for w in s.get("words", [])]
    iv = json.loads(Path(a.intervals).read_text(encoding="utf-8"))
    voz = Voz(a.video)
    out = {}
    for cid, parts in iv.items():
        allruns, alldiag = [], []
        for (s, e) in parts:
            runs, diag = analyze(a.video, float(s), float(e), words, voz)
            allruns += runs
            alldiag += diag
        res = []
        for (s, e, cx, fh, who, why) in allruns:
            z = round(zoom_for(fh), 3) if fh else 1.0
            res.append({"source_start": round(s, 3), "source_end": round(e, 3),
                        "crop_anchor_x": round(anchor_from_cx(cx, z), 4), "zoom": z,
                        "face_cx": round(cx, 1), "quem": who, "motivo": why})
        out[cid] = {"runs": res, "planos": alldiag}
        print(cid, "|", " ; ".join(f"{r['source_start']:.1f}-{r['source_end']:.1f} {r['quem']}" for r in res), flush=True)
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
