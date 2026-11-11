"""Zoom nos cortes de fala para reels NOVELA (teste de 11/11/2026, cards NV_CTA).

Regra do usuário: vídeo com CTA no título leva cortes com zoom entre as falas, com cara natural.
Como faz (mesma lógica aprovada na edição simples):
  - "plano" = trechos do corte colados por microcorte; um corte VISÍVEL (pulo >= 0,35 s no bruto ou outra tomada)
    abre um plano novo;
  - os planos alternam aberto (recorte aprovado) / fechado (punch-in), começando aberto; plano < 0,6 s não troca;
  - o fechado fica parado o plano inteiro e troca no quadro exato da emenda (zoom seco, sem animação);
  - os OLHOS ficam na mesma altura do aberto e o rosto na mesma posição lateral (quem assiste continua olhando
    para o mesmo ponto); o zoom diminui até o topo da cabeça caber com folga de 3 %; abaixo de 1,12x fica aberto;
  - depois da CTA (--ate) tudo fica aberto (a animação cobre).
Grava crops_segmento no enquadramento.json (o render_final.py já usa) e refaz o rosto_corte.json com o recorte de
cada trecho (o queixo desce no fechado e a legenda precisa saber).

uso: python zoom_cortes.py <trabalho> [--zoom 1.22] [--ate <s>] [--desligar]
  --ate: início da CTA em motion (padrão: motion_cta/motion.json "inicio", se existir); dali em diante fica aberto.
  O editar.py finalizar roda de novo sozinho (com os mesmos parâmetros) quando o corte é refeito numa correção.
Testado e aprovado no "Empresário que montou uma ONG" (11/11/2026): 6 fechados de 1,18-1,22x em 69 s.
"""
import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

S = Path.home() / ".claude/skills/reels-novela-clailton/scripts"
sys.path.insert(0, str(S))
from comum import FAIXA_H, FAIXA_Y0, ler_json, gravar_json, sonda  # noqa: E402
import enquadrar  # noqa: E402

FPS = 30000 / 1001
CORTE_VISIVEL = 0.35
PLANO_MIN = 0.6
OLHO = 0.40          # olhos a ~40 % da caixa do rosto (YuNet: testa ao queixo)
TOPO = 0.30          # topo da cabeça ~30 % da altura do rosto acima da caixa
FOLGA_TOPO = 0.03
FOLGA_LADO = 0.05
ZOOM_MIN = 1.12
OLHO_DESCE = 0.06    # quanto os olhos podem descer no fechado (fração da faixa) para caber o topo da cabeça


def par(v):
    return int(round(v / 2) * 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("trabalho")
    ap.add_argument("--zoom", type=float, default=1.22)
    ap.add_argument("--ate", type=float, default=None)
    ap.add_argument("--desligar", action="store_true")
    a = ap.parse_args()
    T = Path(a.trabalho)
    corte = ler_json(T / "corte.json")
    enq_p = T / "enquadramento.json"
    enq = ler_json(enq_p)
    # recortes "base" (deslize lateral do enquadrar.py) guardados na 1a vez; se o enquadrar.py regravou o
    # enquadramento.json, a chave some e os recortes atuais viram a base de novo
    if "crops_segmento_base" not in enq:
        enq["crops_segmento_base"] = enq.get("crops_segmento", {})
    cw, ch, x0, y0 = enq["crop"]
    por_seg_base = enq["crops_segmento_base"]
    if a.ate is None and (T / "motion_cta" / "motion.json").exists():
        a.ate = float(ler_json(T / "motion_cta" / "motion.json")["inicio"])
    fonte = corte["fonte"]
    v = next(s for s in sonda(Path(fonte))["streams"] if s["codec_type"] == "video")
    SW, SH = int(v["width"]), int(v["height"])
    esc = SW / enquadrar.AMOSTRA_W
    segs = corte["segmentos"]

    with ThreadPoolExecutor(enquadrar.PARALELO) as ex:
        res = list(ex.map(lambda s: enquadrar.detectar(fonte, s["src_in"], s["src_out"], 0.5), segs))
    amostras = []
    for k, (s, r) in enumerate(zip(segs, res)):
        for t, f in r:
            if f:
                f = [f[0] * esc, f[1] * esc, f[2] * esc, f[3] * esc]
            amostras.append((s["dst_in"] + (t - s["src_in"]), f, k))
    faces = np.array([f for _, f, _ in amostras if f])
    gx, gy, gw, gh = np.median(faces, axis=0)
    olho_frac = (gy + OLHO * gh - y0) / ch            # linha dos olhos no aberto
    cx_frac = (gx + gw / 2 - x0) / cw

    # planos
    planos, atual = [], []
    t = 0.0
    for k, s in enumerate(segs):
        d = s["frames"] / FPS
        if k and (s["src_in"] - segs[k - 1]["src_out"] >= CORTE_VISIVEL or s["src_in"] < segs[k - 1]["src_in"]):
            planos.append(atual)
            atual = []
        atual.append((k, t, d))
        t += d
    planos.append(atual)

    crops = dict(por_seg_base)
    plano_txt, estado = [], "A"
    for i, p in enumerate(planos):
        ini, dur = p[0][1], sum(d for _, _, d in p)
        if i == 0:
            estado = "A"
        elif dur >= PLANO_MIN:
            estado = "F" if estado == "A" else "A"
        if a.desligar or (a.ate is not None and ini >= a.ate - 0.05):
            estado = "A"
        ks = [k for k, _, _ in p]
        if estado == "A":
            plano_txt.append(f"{ini:6.2f}s +{dur:4.1f}s  A")
            continue
        fs = np.array([f for _, f, kk in amostras if f and kk in ks])
        if len(fs) == 0:
            plano_txt.append(f"{ini:6.2f}s +{dur:4.1f}s  A (sem rosto)")
            estado = "A"
            continue
        fx, fy, fw, fh = np.median(fs, axis=0)
        topo = float(np.min(fs[:, 1] - TOPO * fs[:, 3]))        # cabeça mais alta do plano
        esq, dir_ = float(np.min(fs[:, 0])), float(np.max(fs[:, 0] + fs[:, 2]))
        escolhido = None
        z = a.zoom
        while z >= ZOOM_MIN - 1e-9:
            chz = par(SH / z if ch == SH else ch / z)
            cwz = par(chz * 1.25)
            # olhos na linha do aberto; se a cabeça não couber, sobe o recorte até o topo ter a folga e os olhos
            # descem um pouco (até OLHO_DESCE da faixa: imperceptível no corte, a cabeça nunca é cortada)
            y_olho = (fy + OLHO * fh) - olho_frac * chz
            yz = min(y_olho, topo - FOLGA_TOPO * chz)
            yz = min(max(yz, 0), SH - chz)
            desce = ((fy + OLHO * fh) - yz) / chz - olho_frac
            xz = (fx + fw / 2) - cx_frac * cwz
            xz = min(max(xz, 0), SW - cwz)
            ok_topo = (topo - yz) / chz >= FOLGA_TOPO - 1e-6 and desce <= OLHO_DESCE
            ok_lado = (esq - xz) / cwz >= FOLGA_LADO and (xz + cwz - dir_) / cwz >= FOLGA_LADO
            if ok_topo and ok_lado:
                escolhido = (cwz, chz, int(round(xz)), int(round(yz)), z, desce)
                break
            z -= 0.02
        if not escolhido:
            plano_txt.append(f"{ini:6.2f}s +{dur:4.1f}s  A (fechado não coube: topo {(topo - 0) / SH:.1%} lado {esq:.0f}-{dir_:.0f})")
            estado = "A"
            continue
        cwz, chz, xz, yz, z, desce = escolhido
        for k in ks:
            crops[str(k)] = [cwz, chz, xz, yz]
        plano_txt.append(f"{ini:6.2f}s +{dur:4.1f}s  F {z:.2f}x  olhos +{desce * 100:.1f}%  segs {ks[0]}-{ks[-1]}")

    enq["crops_segmento"] = crops
    enq["zoom_cortes"] = {"zoom": a.zoom, "ate": a.ate, "desligar": a.desligar, "planos": plano_txt}
    gravar_json(enq_p, enq)
    # queixo com o recorte de cada trecho (a legenda fica abaixo dele)
    queixos = []
    for t, f, k in amostras:
        if f:
            c_w, c_h, c_x, c_y = crops.get(str(k), [cw, ch, x0, y0])
            q = FAIXA_Y0 + (f[1] + f[3] - c_y) / c_h * FAIXA_H
            queixos.append({"t": round(t, 3), "queixo": round(float(q), 1)})
    gravar_json(T / "rosto_corte.json", queixos)
    print("\n".join(plano_txt))
    print(f"ok: {sum(1 for x in plano_txt if '  F ' in x)} planos fechados de {len(planos)}")


if __name__ == "__main__":
    main()
