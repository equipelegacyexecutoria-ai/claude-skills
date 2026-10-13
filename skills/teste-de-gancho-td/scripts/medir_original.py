"""Mede o gancho do reel editado (original.mp4) para o gancho novo entrar igual.

Uso (pasta do reel = <W>/<reel>, com original.mp4 dentro):
  python medir_original.py palavras <pasta>            fala dos primeiros 20 s com o tempo de cada palavra
  python medir_original.py medir <pasta> <fim_frase>   fim_frase = segundo em que termina a frase que sai
  python medir_original.py cheio <pasta> <t>           mede a faixa útil de um B-roll em tela cheia no tempo t

`medir` grava <pasta>/medidas.json (quadro do corte, emenda, legenda, rosto, flash, volume) e
<pasta>/medidas.jpg (quadro com as linhas medidas + quadros em volta do corte) para conferir a olho.
"""
import statistics, sys
from collections import Counter
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from comum import FPS, MOD, W, H, gravar_json, ler_json, lufs, palavras, quadro, rodar  # noqa: E402


def cmd_palavras(pasta):
    ws = palavras(pasta / "original.mp4", 0, 20)
    gravar_json(pasta / "palavras_inicio.json", ws)
    for w in ws:
        print(f"{w['i']:6.2f}-{w['f']:5.2f}  {w['p']}")


def achar_corte(orig, t_fim):
    """Quadro do corte (1º quadro da cena que continua): a maior mudança de imagem entre t_fim-0,3 e
    t_fim+0,8. Lê do início do vídeo, quadro a quadro, para o número do quadro ser exato."""
    f = quadros_cinza(orig, t_fim + 0.9).astype(float)
    a, b = max(1, round((t_fim - 0.3) * FPS)), min(len(f), round((t_fim + 0.8) * FPS))
    difs = {i: np.abs(f[i] - f[i - 1]).mean() for i in range(a, b)}
    q = max(difs, key=difs.get)
    brilho = f.mean(axis=(1, 2))
    brancos, k = 0, q - 1
    while k >= 0 and brilho[k] > 200:   # o gancho sai clareando para branco
        brancos += 1
        k -= 1
    flash = brancos + 1 if brancos else 0   # o fade chega ao branco em (brancos + 1) quadros
    return q, flash, sorted(((round(d, 1), i) for i, d in difs.items()), reverse=True)[:3]


def quadros_cinza(vid, ate, w=108, h=192):
    import subprocess
    raw = subprocess.run(["ffmpeg", "-v", "error", "-t", f"{ate:.3f}", "-i", str(vid),
                          "-vf", f"scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w)


def achar_emenda(frs):
    """Divisão imagem/Clailton: em cima a imagem muda ao longo do gancho, embaixo (fundo do escritório) quase
    não muda. Mede a variação no tempo só nas bordas (fora da legenda) e pega onde ela cai 30% do caminho."""
    g = np.array([im.mean(axis=2) for im in frs])
    sd = np.concatenate([g[:, :, :50], g[:, :, -50:]], axis=2).std(axis=0).mean(axis=1)
    r0 = max(range(600, 1150), key=lambda r: sd[r - 30:r].mean() - sd[r:r + 30].mean())
    alto, baixo = np.median(sd[r0 - 60:r0 - 30]), np.median(sd[r0 + 30:r0 + 60])
    limite = alto - 0.3 * (alto - baixo)
    for r in range(r0 - 40, r0 + 40):
        if sd[r] < limite:
            return r, alto - baixo
    return r0, alto - baixo


def caixa_legenda(im, y_ini, y_fim):
    """Topo e base da linha de legenda (texto branco) mais perto do meio da faixa. Linha com branco em mais
    de 60% da largura é fundo claro da imagem, não texto."""
    m = im.min(axis=2) > 243
    n = m[y_ini:y_fim, 60:1020].sum(axis=1)
    ok = (n > 25) & (n < 0.6 * 960)
    runs, ini, buraco = [], None, 0
    for r, v in enumerate(ok):
        if v:
            ini = r if ini is None else ini
            fim, buraco = r, 0
        elif ini is not None:
            buraco += 1
            if buraco > 4:
                runs.append((ini, fim))
                ini = None
    if ini is not None:
        runs.append((ini, fim))
    runs = [(a, b) for a, b in runs if 20 <= b - a <= 140]
    if not runs:
        return None
    meio = (y_fim - y_ini) / 2
    a, b = min(runs, key=lambda x: abs((x[0] + x[1]) / 2 - meio))
    return int(a + y_ini), int(b + y_ini)


def cmd_medir(pasta, t_fim):
    orig = pasta / "original.mp4"
    q, flash, top3 = achar_corte(orig, t_fim)
    t_c = q / FPS
    print(f"corte no quadro {q} ({t_c:.3f} s); maiores mudanças {top3}; flash {flash} quadros")

    frs = [quadro(orig, t) for t in np.linspace(0.15, max(0.4, t_c - 0.15), 16)]
    emenda, contraste = achar_emenda(frs)
    if contraste < 10:
        print(f"AVISO: emenda incerta (a imagem de cima quase não muda): confira a linha vermelha em medidas.jpg")

    caixas = [c for c in (caixa_legenda(im, emenda - 90, emenda + 90) for im in frs) if c]
    if caixas:
        m_alt = statistics.median(b - a for a, b in caixas)
        caixas = [(a, b) for a, b in caixas if b - a <= 1.6 * m_alt]
        alturas = sorted(b - a for a, b in caixas)
        cap_px = int(np.percentile(alturas, 25))          # sem acento / cedilha
        cap_y = int(statistics.median((a + b) / 2 for a, b in caixas))
        cap_topo = int(statistics.median(a for a, _ in caixas))
    else:
        print("AVISO: legenda não achada perto da emenda; usei o padrão (54 px na emenda)")
        cap_px, cap_y, cap_topo = 54, emenda + 5, emenda - 22

    # rosto do Clailton embaixo da emenda
    det = None
    med = []
    cap = cv2.VideoCapture(str(orig))
    for t in np.linspace(0.2, max(0.4, t_c - 0.2), 12):
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, fr = cap.read()
        if not ok:
            continue
        sub = fr[emenda:]
        h, w = sub.shape[:2]
        if det is None:
            det = cv2.FaceDetectorYN.create(MOD, "", (w, h), 0.6, 0.3, 5000)
        _, f = det.detect(sub)
        if f is not None and len(f):
            f = max(f, key=lambda r: r[2] * r[3])
            med.append((f[2], f[0] + f[2] / 2, (f[5] + f[7]) / 2 + emenda))
    if not med:
        sys.exit("rosto não encontrado embaixo da emenda: confira o fim_frase e a emenda")
    rosto = dict(larg=round(statistics.median(m[0] for m in med)), cx=round(statistics.median(m[1] for m in med)),
                 olhos_y=round(statistics.median(m[2] for m in med)))

    ant = ler_json(pasta / "medidas.json", {})
    med_json = dict(original="original.mp4", corte_quadro=q, emenda=emenda, cap_y=cap_y, cap_px=cap_px,
                    flash_quadros=flash, sfx_fim=ant.get("sfx_fim", 0.10 if flash else 0), rosto=rosto,
                    alvo_lufs=round(lufs(orig, 0, t_c), 1),
                    topo_y1=min(emenda, cap_topo - 30), cheio=ant.get("cheio"), fim_frase=t_fim)
    gravar_json(pasta / "medidas.json", med_json)
    print(med_json)

    # folha de conferência: quadro do gancho com as linhas + 6 quadros em volta do corte
    im = quadro(orig, min(0.6, t_c / 2)).astype(np.uint8)[:, :, ::-1].copy()
    cv2.line(im, (0, emenda), (W, emenda), (0, 0, 255), 3)
    cv2.rectangle(im, (60, cap_y - cap_px // 2), (1020, cap_y + cap_px // 2), (0, 255, 255), 2)
    cv2.line(im, (0, med_json["topo_y1"]), (W, med_json["topo_y1"]), (255, 0, 0), 2)
    cv2.circle(im, (rosto["cx"], rosto["olhos_y"]), 10, (0, 255, 0), -1)
    import subprocess
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(orig), "-vf",
                          f"select='between(n\\,{q - 3}\\,{q + 2})',scale=270:480", "-fps_mode", "passthrough",
                          "-frames:v", "6", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
    tira = []
    for k, fr in zip(range(q - 3, q + 3), np.frombuffer(raw, np.uint8).reshape(-1, 480, 270, 3)):
        fr = fr.copy()
        cv2.putText(fr, str(k) + (" <CORTE" if k == q else ""), (8, 30), 0, 0.8, (0, 255, 255), 2)
        tira.append(fr)
    tira = np.hstack(tira)
    lado = cv2.resize(im, (int(480 * W / H), 480))
    folha = np.hstack([lado, tira])
    cv2.imwrite(str(pasta / "medidas.jpg"), folha)
    print("conferir:", pasta / "medidas.jpg", "(vermelho = emenda, azul = fim da faixa de cima limpa, "
          "amarelo = legenda, verde = olhos)")


def cmd_cheio(pasta, t):
    im = quadro(pasta / "original.mp4", t)
    c = caixa_legenda(im, 900, 1500)
    y1 = (c[0] - 12) if c else 1150
    med = ler_json(pasta / "medidas.json", {})
    med["cheio"] = [120, int(y1)]
    gravar_json(pasta / "medidas.json", med)
    print("faixa útil do B-roll em tela cheia:", med["cheio"], "(legenda em", c, ")")


if __name__ == "__main__":
    modo, pasta = sys.argv[1], Path(sys.argv[2])
    if modo == "palavras":
        cmd_palavras(pasta)
    elif modo == "medir":
        cmd_medir(pasta, float(sys.argv[3]))
    elif modo == "cheio":
        cmd_cheio(pasta, float(sys.argv[3]))
    else:
        sys.exit(__doc__)
