"""Separa os melhores quadros do Clailton para a thumb de cada episódio (a arte é do designer).

Passo 1 — candidatos:  python thumbs.py <trabalho> candidatos [--so 1]
  Varre os trechos do episódio a cada 3 s, acha o rosto (YuNet) e dá nota: rosto grande, nítido, de frente,
  olhos visíveis. Guarda os 12 melhores (≥ 25 s de distância) numa folha numerada:
  <trabalho>/thumbs/epNN_candidatos.jpg  (+ epNN_candidatos.json)
  -> olhar a folha e escolher 3 com expressão que casa com o tema (preocupação = erro, firmeza = método,
     surpresa = revelação), olhos abertos, boca em posição boa.

Passo 2 — exportar:  python thumbs.py <trabalho> exportar --ep 1 --escolha 3,7,11
  Salva para cada escolha: quadro inteiro 1920×1080 (PNG) e um recorte 16:9 com o rosto em ~40% da altura
  (ampliado para 1920×1080; a nitidez é a do original — se precisar, o designer amplia com IA).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import SKILL, gravar_json, hms, ler_json  # noqa: E402
from render_episodio import montar, quadro, rostos  # noqa: E402


def nota_rosto(img, r) -> tuple[float, dict]:
    fx, fy, fw, fh = r
    H, W = img.shape[:2]
    x0, y0, x1, y1 = int(max(0, fx)), int(max(0, fy)), int(min(W, fx + fw)), int(min(H, fy + fh))
    cara = cv2.cvtColor(img[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY)
    if cara.size == 0:
        return 0.0, {}
    nitidez = cv2.Laplacian(cara, cv2.CV_64F).var()
    return fh * min(1.0, nitidez / 120), {"altura_rosto": round(fh), "nitidez": round(nitidez)}


def parece_clailton(img, r) -> bool:
    """Descarta rosto de foto no slide (Stallone, Grant Cardone...): o Clailton é careca e aparece em cor.
    Pele com cor (não P&B) e o topo da cabeça com a mesma cor/brilho da pele (sem cabelo, sem chapéu)."""
    fx, fy, fw, fh = map(int, r[:4])
    H, W = img.shape[:2]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    cx0, cx1 = max(0, fx + fw // 4), min(W, fx + 3 * fw // 4)
    pele = hsv[max(0, fy + fh // 3):min(H, fy + 2 * fh // 3), cx0:cx1].reshape(-1, 3).astype(float)
    topo = hsv[max(0, fy - int(fh * 0.15)):max(1, fy), cx0:cx1].reshape(-1, 3).astype(float)   # testa/careca
    if len(pele) < 20 or len(topo) < 20:
        return False
    sp, vp, ht = pele[:, 1].mean(), pele[:, 2].mean(), topo
    if sp < 35:                                   # foto preto e branco
        return False
    dh = abs(np.median(ht[:, 0]) - np.median(pele[:, 0]))
    return ht[:, 2].mean() >= 0.8 * vp and ht[:, 1].mean() >= 0.4 * sp and min(dh, 180 - dh) <= 12


def candidatos(trab: Path, plano: dict, ep: dict) -> None:
    m = montar(trab, ep)
    pontos = []
    for a, b in m["segs"][m["n_ab"]:]:
        t = a + 1.0
        while t < b - 0.5:
            pontos.append(t)
            t += 3.0
    ach = []
    det = cv2.FaceDetectorYN.create(str(SKILL / "models" / "face_detection_yunet_2023mar.onnx"), "", (1920, 1080),
                                    0.75, 0.3, 50)
    for k, t in enumerate(pontos):
        img = quadro(plano["fonte"], t, 1920)
        if img is None:
            continue
        det.setInputSize((img.shape[1], img.shape[0]))
        _, f = det.detect(img)
        if f is None:
            continue
        f = [z for z in f if parece_clailton(img, z)]
        if not f:
            continue
        r = max(f, key=lambda z: z[3])           # maior rosto = quem está mais perto da câmera
        fx, fy, fw, fh = map(float, r[:4])
        le, re_ = r[4:6], r[6:8]
        nariz = r[8:10]
        meio = (le[0] + re_[0]) / 2
        frontal = 1 - min(1.0, abs(nariz[0] - meio) / max(1.0, abs(le[0] - re_[0])))   # 1 = de frente
        nota, extra = nota_rosto(img, (fx, fy, fw, fh))
        nota *= 0.4 + 0.6 * frontal * float(r[14])
        ach.append({"t": round(float(t), 2), "nota": round(float(nota), 2), "rosto": [round(v) for v in (fx, fy, fw, fh)],
                    "frontal": round(float(frontal), 2), **{k: float(v) for k, v in extra.items()}})
        if k % 60 == 0:
            print(f"  {k}/{len(pontos)} quadros", flush=True)
    ach.sort(key=lambda x: -x["nota"])
    esc = []
    for c in ach:
        if all(abs(c["t"] - e["t"]) >= 25 for e in esc):
            esc.append(c)
        if len(esc) == 12:
            break
    pasta = trab / "thumbs"
    pasta.mkdir(exist_ok=True)
    w, h = 480, 270
    folha = Image.new("RGB", (4 * w, 3 * (h + 24)), "black")
    dr = ImageDraw.Draw(folha)
    fnt = ImageFont.truetype(str(SKILL / "fonts" / "SF-Pro-Display-Bold.otf"), 18)
    for i, c in enumerate(esc, 1):
        img = quadro(plano["fonte"], c["t"], 1920)
        fx, fy, fw, fh = c["rosto"]
        ch = int(min(1080, max(270, fh / 0.40)))      # recorte com o rosto em ~40% da altura
        cw = int(ch * 16 / 9)
        cx, cy = fx + fw / 2, fy + fh / 2
        x0 = int(np.clip(cx - cw / 2, 0, 1920 - cw))
        y0 = int(np.clip(cy - ch * 0.42, 0, 1080 - ch))
        c["recorte"] = [x0, y0, cw, ch]
        rec = cv2.resize(img[y0:y0 + ch, x0:x0 + cw], (w, h), interpolation=cv2.INTER_AREA)
        x, y = ((i - 1) % 4) * w, ((i - 1) // 4) * (h + 24)
        folha.paste(Image.fromarray(cv2.cvtColor(rec, cv2.COLOR_BGR2RGB)), (x, y))
        dr.text((x + 6, y + h + 2), f"{i}) aula {hms(c['t'])} · rosto {fh}px", fill="yellow", font=fnt)
    nome = f"ep{ep['n']:02d}_candidatos"
    folha.save(pasta / f"{nome}.jpg", quality=88)
    gravar_json(pasta / f"{nome}.json", esc)
    print(f"ok: {pasta / (nome + '.jpg')} ({len(ach)} quadros com rosto)")


def exportar(trab: Path, plano: dict, ep: dict, escolha: list[int]) -> None:
    pasta = trab / "thumbs"
    cand = ler_json(pasta / f"ep{ep['n']:02d}_candidatos.json")
    for k, i in enumerate(escolha, 1):
        c = cand[i - 1]
        img = quadro(plano["fonte"], c["t"], 1920)
        base = f"{ep['arquivo']} - thumb {k}"
        # cv2.imwrite estraga nome com acento no Windows: grava os bytes pelo Python
        cv2.imencode(".png", img)[1].tofile(str(pasta / f"{base} (quadro inteiro).png"))
        x0, y0, cw, ch = c["recorte"]
        rec = cv2.resize(img[y0:y0 + ch, x0:x0 + cw], (1920, 1080), interpolation=cv2.INTER_LANCZOS4)
        cv2.imencode(".png", rec)[1].tofile(str(pasta / f"{base} (recorte rosto).png"))
        print(f"ok: {base} · aula {hms(c['t'])}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("trabalho")
    ap.add_argument("acao", choices=["candidatos", "exportar"])
    ap.add_argument("--so", default="")
    ap.add_argument("--ep", type=int)
    ap.add_argument("--escolha", default="")
    a = ap.parse_args()
    trab = Path(a.trabalho)
    plano = ler_json(trab / "plano.json")
    if a.acao == "candidatos":
        so = {int(x) for x in a.so.split(",") if x.strip()}
        for ep in plano["episodios"]:
            if not so or ep["n"] in so:
                candidatos(trab, plano, ep)
    else:
        ep = next(e for e in plano["episodios"] if e["n"] == a.ep)
        exportar(trab, plano, ep, [int(x) for x in a.escolha.split(",")])


if __name__ == "__main__":
    main()
