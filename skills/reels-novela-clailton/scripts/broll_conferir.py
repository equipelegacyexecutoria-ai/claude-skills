"""Confere os B-rolls de um reel ANTES de entregar (processo de 16/11/2026: as notas de imagem eram 27% de todas
as notas da Sala). Pega sozinho o que não depende de gosto:

  - entra antes de 2 s (o vídeo abre com o Clailton)          - dura menos de 1 s ou mais de 4,5 s
  - entra/sai 0,1-1 s antes/depois de um corte (pulo duplo)     - sobrepõe outro B-roll / deixa "piscar" o Clailton
  - congela (quadro parado >= 0,4 s, ex.: clipe mais curto)     - tem corte de cena dentro (troca de plano)
  - rosto encostado na borda (pessoa cortada)                   - texto/legenda/marca na imagem
  - cena repetida (mesma fonte e trecho, ou imagem quase igual) - trecho longo da fala sem nenhuma imagem (aviso leve)

Gera qa/broll_conferencia.txt e qa/folha_broll.jpg (1º/meio/último quadro de cada B-roll + a fala daquele trecho)
para olhar o enquadramento e se a imagem mostra LITERALMENTE o que ele fala (isso é você que julga na folha).

uso: broll_conferir.py <trabalho> [--fim-fala <s>]      código 0 = ok, 3 = tem problema grave
broll.json: [{"arquivo": "broll/b1.mp4", "inicio": 4.05, "fim": 5.47,
              "origem": "acervo BB-02 t=10" | "YouTube <url> 0:32" | "Pexels 8201570",   (opcional, vai na folha)
              "fonte": "<arquivo/url de origem>", "fonte_t": 32.0}]                       (opcional, p/ repetição)
"""
import io
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, os.path.expanduser("~/.claude/skills/reels-tela-dividida-clailton/scripts"))

FPS = 30000 / 1001
W, H = 1080, 864
INICIO_MIN = 2.0
DUR_MIN, DUR_MAX = 1.0, 4.5
PERTO_CORTE = (0.1, 1.0)
SEM_IMAGEM_MAX = 9.0


def quadros(arq: str, n_max: int = 400) -> np.ndarray:
    """Todos os quadros (cinza 96x77) para corte/congelamento."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", arq, "-vf", "scale=96:77,format=gray", "-frames:v",
                          str(n_max), "-f", "rawvideo", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, 77, 96).astype(np.float32)


def quadro_rgb(arq: str, t: float) -> np.ndarray | None:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(0, t):.3f}", "-i", arq, "-frames:v", "1",
                          "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(H, W, 3) if len(raw) == W * H * 3 else None


def duracao(arq: str) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", arq],
                       capture_output=True, text=True).stdout.strip()
    try:
        return float(r)
    except ValueError:
        return 0.0


_det = None


def rostos(rgb: np.ndarray) -> list:
    global _det
    import cv2
    from comum import MODELO_ROSTO
    if _det is None:
        _det = cv2.FaceDetectorYN.create(str(MODELO_ROSTO), "", (540, 432), 0.7, 0.3, 5000)
    img = cv2.resize(np.ascontiguousarray(rgb[:, :, ::-1]), (540, 432))
    _, f = _det.detect(img)
    return [] if f is None else [r[:4] * 2 for r in f]       # x, y, w, h em 1080x864


def borda(r) -> bool:
    x, y, w, h = r
    m = 6
    return x < m or y < m or x + w > W - m or y + h > H - m


def caixas_linha(rgb: np.ndarray) -> list:
    """Caixas com cara de linha escrita (comprida e baixa, mesmo inclinada), sem o grão do filtro película.
    Volta (x, y, w, h) do retângulo reto em fração do quadro."""
    try:
        import cv2
        from midia_util import _detector_texto
    except Exception:
        return []
    boxes, _ = _detector_texto().detect(np.ascontiguousarray(rgb[:, :, ::-1]))
    out = []
    for poly in boxes:
        pts = np.array(poly, np.float32)
        (_, _), (rw, rh), _ = cv2.minAreaRect(pts)
        lado_l, lado_c = max(rw, rh), max(1.0, min(rw, rh))
        if lado_c < 0.02 * H or lado_c > 0.15 * H or lado_l / lado_c < 1.2 or lado_l * lado_c < 0.0008 * W * H:
            continue
        x, y, w, h = cv2.boundingRect(pts.astype(np.int32))
        out.append((x / W, y / H, w / W, h / H, lado_l / lado_c))
    return out


def texto_fixo(rgbs: list) -> float:
    """% do quadro com texto PARADO no mesmo lugar em pelo menos 2 dos 3 quadros (adesivo, legenda, marca, placa
    em plano parado). Multidão e textura mudam de um quadro para outro e não contam."""
    cx = [caixas_linha(r) for r in rgbs if r is not None]
    if len(cx) < 2:
        return 0.0

    def iou(a, b):
        ix = max(0.0, min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0]))
        iy = max(0.0, min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1]))
        i = ix * iy
        return i / max(1e-9, a[2] * a[3] + b[2] * b[3] - i)

    tot = 0.0
    for i, cs in enumerate(cx):
        for b in cs:
            casa = sum(1 for j, os_ in enumerate(cx) if j != i and any(iou(b, o) > 0.5 for o in os_))
            # linha comprida: basta repetir em mais 1 quadro; palavra curta ("Hello"): tem que estar em todos
            if (b[4] >= 2.0 and casa >= 1) or casa >= len(cx) - 1:
                tot += b[2] * b[3]
    return tot * 100 / len(cx)


def ahash(rgb: np.ndarray) -> int:
    g = np.asarray(Image.fromarray(rgb).convert("L").resize((16, 16)), np.float32)
    bits = (g > g.mean()).flatten()
    return int("".join("1" if b else "0" for b in bits), 2)


def main():
    T = Path(sys.argv[1])
    fim_fala = None
    if "--fim-fala" in sys.argv:
        fim_fala = float(sys.argv[sys.argv.index("--fim-fala") + 1])
    bj = T / "broll.json"
    if not bj.exists():
        sys.exit(f"sem {bj}")
    B = json.load(io.open(bj, encoding="utf-8"))
    corte = json.load(io.open(T / "corte.json", encoding="utf-8"))
    segs = corte["segmentos"]
    emendas = [s["dst_in"] for s in segs[1:]] if all("dst_in" in s for s in segs) else []
    if not emendas:
        acc = 0
        for s in segs[:-1]:
            acc += s["frames"]
            emendas.append(acc / FPS)
    pal = json.load(io.open(T / "palavras_corte.json", encoding="utf-8"))["palavras"]
    if fim_fala is None:
        fim_fala = corte.get("duracao_fala") or (pal[-1]["fim"] if pal else 0)

    (T / "qa").mkdir(exist_ok=True)
    linhas, graves, fichas, hashes = [], 0, [], []
    B = sorted(B, key=lambda b: b["inicio"])
    for k, b in enumerate(B, 1):
        av = []
        ini, fim = float(b["inicio"]), float(b["fim"])
        dur = fim - ini
        arq = str(T / b["arquivo"]) if not os.path.isabs(b["arquivo"]) else b["arquivo"]
        fala = " ".join(w["texto"] for w in pal if ini - 0.05 <= w["inicio"] < fim)
        if ini < INICIO_MIN:
            av.append(("G", f"entra em {ini:.2f}s: o vídeo abre com o Clailton (B-roll só depois de {INICIO_MIN:.0f} s)"))
        if dur < DUR_MIN:
            av.append(("G", f"dura {dur:.2f}s (curto demais, vira piscada)"))
        elif dur > DUR_MAX:
            av.append(("L", f"dura {dur:.1f}s (longo: divida em 2 cenas que ilustrem a mesma fala)"))
        for nome, t in (("entra", ini), ("sai", fim)):
            d = min((abs(t - e) for e in emendas), default=9)
            if PERTO_CORTE[0] < d < PERTO_CORTE[1]:
                av.append(("G", f"{nome} a {d:.2f}s de um corte da decupagem (encoste no corte ou afaste >= 1 s)"))
        if k > 1:
            pf = float(B[k - 2]["fim"])
            if ini < pf - 0.02:
                av.append(("G", f"sobrepõe o B-roll {k-1}"))
            elif 0 < ini - pf < 0.25:
                av.append(("G", f"{ini - pf:.2f}s de Clailton entre o B-roll {k-1} e este (piscada): emende"))
        if not os.path.exists(arq):
            av.append(("G", f"arquivo não existe: {b['arquivo']}"))
            linhas.append((k, ini, fim, fala, b.get("origem", ""), av)); graves += 1
            continue
        dclip = duracao(arq)
        if dclip + 0.05 < dur:
            av.append(("G", f"clipe tem {dclip:.2f}s e a janela {dur:.2f}s: o fim congela"))
        q = quadros(arq, int(dur * FPS) + 2)
        if len(q) > 2:
            d = np.abs(np.diff(q, axis=0)).mean(axis=(1, 2))
            med = float(np.median(d)) + 0.5
            cortes = [i for i, x in enumerate(d) if x > max(22.0, 7 * med)]
            if cortes:
                av.append(("G", f"troca de cena dentro do B-roll em {', '.join(f'{(i+1)/FPS:.1f}s' for i in cortes[:3])} (use 1 take sem cortes)"))
            parado = run = 0
            for x in d:
                run = run + 1 if x < 0.25 else 0
                parado = max(parado, run)
            if parado >= 12:
                av.append(("G", f"imagem parada {parado/FPS:.1f}s (congela)"))
        ts = [0.05, dur / 2, max(0.05, dur - 0.08)]
        rgbs = [quadro_rgb(arq, t) for t in ts]
        cortado = False
        for t, r in zip(ts, rgbs):
            if r is None:
                continue
            for f in rostos(r):
                if borda(f) and f[2] * f[3] > 2500:
                    cortado = True
        if cortado:
            av.append(("G", "rosto encostado na borda (pessoa cortada): reenquadre (fonte_x) ou troque"))
        tp = texto_fixo(rgbs)
        if tp > 0.6:
            av.append(("G", f"texto parado na imagem ({tp:.1f}% do quadro): legenda/adesivo/marca? confira se não é inglês"))
        else:
            soltos = [i for i, r in enumerate(rgbs) if r is not None and caixas_linha(r)]
            if soltos:
                nomes = ["1º", "meio", "último"]
                av.append(("L", "possível texto no quadro " + ", ".join(nomes[i] for i in soltos)
                           + ": olhe na folha (inglês, marca, placa)"))
        if rgbs[1] is not None:
            h = ahash(rgbs[1])
            for j, hh in hashes:
                if bin(h ^ hh).count("1") <= 20:
                    av.append(("L", f"imagem muito parecida com o B-roll {j}"))
            hashes.append((k, h))
        src, st = b.get("fonte"), b.get("fonte_t")
        if src is not None and st is not None:
            for j, o in enumerate(B[:k - 1], 1):
                if o.get("fonte") == src and o.get("fonte_t") is not None and abs(float(o["fonte_t"]) - float(st)) < 3:
                    av.append(("G", f"mesmo trecho da fonte que o B-roll {j} (repetido)"))
        graves += sum(1 for g, _ in av if g == "G")
        linhas.append((k, ini, fim, fala, b.get("origem", ""), av))
        fichas.append((k, ini, fim, fala, b.get("origem", ""), av, rgbs))

    # trechos longos sem imagem (depois dos 2 s, até o fim da fala)
    vaos, t0 = [], INICIO_MIN
    for b in B:
        if b["inicio"] - t0 > SEM_IMAGEM_MAX:
            vaos.append((t0, b["inicio"]))
        t0 = max(t0, b["fim"])
    if fim_fala - t0 > SEM_IMAGEM_MAX:
        vaos.append((t0, fim_fala))

    out = [f"B-rolls: {len(B)} · problemas graves: {graves}", ""]
    for k, ini, fim, fala, orig, av in linhas:
        out.append(f"[{k:02d}] {ini:6.2f}-{fim:6.2f}s ({fim-ini:.1f}s) {orig}")
        out.append(f"     fala: {fala}")
        for g, a in av:
            out.append(f"     {'✗' if g == 'G' else '·'} {a}")
    if vaos:
        out.append("")
        out.append("Trechos sem imagem (> %.0f s): " % SEM_IMAGEM_MAX + ", ".join(f"{a:.1f}-{b:.1f}s" for a, b in vaos)
                   + "  (ok se for de propósito: Clailton falando algo forte)")
    io.open(T / "qa" / "broll_conferencia.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("\n".join(out))

    # folha: uma linha por B-roll
    if fichas:
        tw, th = 300, 240
        try:
            fn = ImageFont.truetype("arial.ttf", 18)
            fb = ImageFont.truetype("arialbd.ttf", 20)
        except Exception:
            fn = fb = ImageFont.load_default()
        folha = Image.new("RGB", (tw * 3 + 620, (th + 10) * len(fichas) + 10), (20, 22, 27))
        dr = ImageDraw.Draw(folha)
        for i, (k, ini, fim, fala, orig, av, rgbs) in enumerate(fichas):
            y = 10 + i * (th + 10)
            for j, r in enumerate(rgbs):
                if r is not None:
                    im = Image.fromarray(r).resize((tw, th))
                    d2 = ImageDraw.Draw(im)
                    for bx, by, bw, bh, _ in caixas_linha(r):          # onde o detector viu texto
                        d2.rectangle([bx * tw - 2, by * th - 2, (bx + bw) * tw + 2, (by + bh) * th + 2], outline=(255, 214, 0), width=2)
                    for fx, fy, fw, fh in rostos(r):                   # rosto na borda em vermelho
                        if borda((fx, fy, fw, fh)) and fw * fh > 2500:
                            d2.rectangle([fx * tw / W, fy * th / H, (fx + fw) * tw / W, (fy + fh) * th / H], outline=(234, 60, 60), width=3)
                    folha.paste(im, (j * tw, y))
            x = tw * 3 + 14
            cor = (234, 107, 96) if any(g == "G" for g, _ in av) else (92, 194, 138)
            dr.text((x, y + 4), f"{k:02d}  {ini:.1f}-{fim:.1f}s  {orig[:40]}", fill=cor, font=fb)
            linha, yy = "", y + 36
            for p in ("“" + fala + "”").split():
                if dr.textlength(linha + " " + p, font=fn) > 590:
                    dr.text((x, yy), linha, fill=(232, 234, 239), font=fn); yy += 22; linha = p
                else:
                    linha = (linha + " " + p).strip()
            dr.text((x, yy), linha, fill=(232, 234, 239), font=fn); yy += 30
            for g, a in av[:4]:
                dr.text((x, yy), ("X " if g == "G" else "- ") + a[:70], fill=(234, 107, 96) if g == "G" else (149, 156, 171), font=fn)
                yy += 22
        folha.save(T / "qa" / "folha_broll.jpg", quality=85)
        print(f"folha: {T / 'qa' / 'folha_broll.jpg'}")
    sys.exit(3 if graves else 0)


if __name__ == "__main__":
    main()
