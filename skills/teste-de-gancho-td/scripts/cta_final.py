"""CTA falada no FIM de um reel já publicado: corta o original no ponto da task e emenda o Clailton real
(trecho do bruto com a boca sincronizada à fala nova do HeyGen), no mesmo enquadramento, cor, som e legenda
do fim do original.

Uso: python cta_final.py <W> <reel>          (lê <W>/<reel>/cta.json)
cta.json:
{
  "pauta": "Reels_Clailton_TD_TESTE_CTA_Plano_Porco_E_O_Urso",   nome do arquivo final (TESTE depois do formato)
  "corte": 114.33,          segundo do original onde a CTA entra (tudo depois sai)
  "nome": "porco",          fala em <W>/vozes/<nome>.wav (+ frases.json) e boca em <W>/ls/<nome>.mp4
  "boca": "heygen/porco.mp4",  (opcional) vídeo do Clailton falando a CTA; padrão ls/<nome>.mp4
  "estilo": "cheio",        "cheio" = Clailton em tela cheia (TD/ES); "novela" = faixa com barras pretas
  "trocas": [9, 25],        índices de palavra onde o plano troca aberto <-> fechado (zoom seco)
  "comeca": "fechado",      plano da 1ª tela da CTA (padrão: o contrário do último plano antes do corte)
  "cauda": 0.6,             segundos de imagem depois da última palavra
  "legenda_y": 1128, "legenda_px": 37   (opcional) centro e altura da maiúscula da legenda do original, se a medida automática errar
}
Grava <W>/<reel>/<pauta>.mp4 e <reel>_qa.jpg (fim do original x CTA, quadro a quadro).
"""
import json, statistics, subprocess, sys, tempfile
from pathlib import Path

import cv2
import numpy as np

S = Path(__file__).parent
sys.path.insert(0, str(S))
from comum import FPS, MOD, W, H, ler_json, lufs, palavras, quadro  # noqa: E402
from montar_gancho import legenda_ass  # noqa: E402
from medir_original import caixa_legenda  # noqa: E402

R, reel = Path(sys.argv[1]), sys.argv[2]
P = R / reel
C = ler_json(P / "cta.json")
FR = ler_json(R / "vozes/frases.json")[C["nome"]]
orig = P / "original.mp4"
t_c = round(C["corte"] * FPS) / FPS          # corte no quadro exato
tmp = Path(tempfile.mkdtemp())


def rodar(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        sys.exit(r.stderr[-3000:])
    return r


def rostos(vid, t0, t1, passo=0.2):
    cap = cv2.VideoCapture(str(vid))
    w, h = int(cap.get(3)), int(cap.get(4))
    k = 540 / max(w, h) if max(w, h) > 960 else 1.0   # reduzido: o detector perde rosto muito perto (selfie)
    dw, dh = round(w * k), round(h * k)
    det = cv2.FaceDetectorYN.create(MOD, "", (dw, dh), 0.6, 0.3, 5000)
    out = []
    for t in np.arange(t0, t1, passo):
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, fr = cap.read()
        if not ok:
            continue
        _, f = det.detect(cv2.resize(fr, (dw, dh), interpolation=cv2.INTER_AREA) if k != 1.0 else fr)
        if f is not None and len(f):
            f = max(f, key=lambda r: r[2] * r[3]) / k
            out.append(dict(t=round(t, 2), larg=f[2], cx=(f[4] + f[6]) / 2, olhos=(f[5] + f[7]) / 2))
    return out


# 1) fim do original: os dois planos (aberto/fechado) do Clailton e a legenda
fim = rostos(orig, max(0, t_c - 25), t_c)
if fim:   # só o Clailton: B-roll com outras pessoas tem rosto bem menor que o dele
    maior = np.percentile([r["larg"] for r in fim], 90)
    fim = [r for r in fim if r["larg"] >= 0.55 * maior]
if len(fim) < 5:
    sys.exit("rosto do Clailton não achado nos 25 s antes do corte")
largs = sorted(r["larg"] for r in fim)
corte_l = max(range(1, len(largs)), key=lambda k: largs[k] / largs[k - 1])
if largs[corte_l] / largs[corte_l - 1] > 1.12:
    ab = [r for r in fim if r["larg"] < largs[corte_l]]
    fe = [r for r in fim if r["larg"] >= largs[corte_l]]
else:   # um plano só no fim: fechado = 1,3x
    ab = fe = fim
med = lambda lst, k: statistics.median(r[k] for r in lst)  # noqa: E731
PLANOS = {"aberto": dict(larg=med(ab, "larg"), cx=med(ab, "cx"), olhos=med(ab, "olhos")),
          "fechado": dict(larg=med(fe, "larg"), cx=med(fe, "cx"), olhos=med(fe, "olhos"))}
if ab is fe:
    PLANOS["fechado"] = dict(PLANOS["aberto"], larg=PLANOS["aberto"]["larg"] * 1.3)
# fechado no máximo 1,3x o aberto e olhos na mesma altura dos dois (regra dos reels: zoom seco sem pular o olhar)
PLANOS["fechado"] = dict(PLANOS["aberto"], larg=min(PLANOS["fechado"]["larg"], PLANOS["aberto"]["larg"] * 1.3))
ultimo = "fechado" if fim[-1]["larg"] >= largs[corte_l] and ab is not fe else "aberto"
print("planos do fim:", {k: {a: round(b) for a, b in v.items()} for k, v in PLANOS.items()}, "| último:", ultimo)

NOVELA = C.get("estilo") == "novela"
if NOVELA:   # faixa de imagem entre as barras pretas (cada novela foi enquadrada de um jeito)
    fx = []
    for t in np.linspace(t_c - 8, t_c - 0.2, 9):
        r = np.where(quadro(orig, t).astype(float).mean(axis=(1, 2)) > 6)[0]
        fx.append((r.min(), r.max()))
    BY0, BY1 = int(statistics.median(a for a, _ in fx)), int(statistics.median(b for _, b in fx))
else:
    BY0, BY1 = 0, H - 1
BH = (BY1 - BY0 + 1) // 2 * 2
print(f"faixa de imagem: y {BY0}..{BY0 + BH}")

caixas = [c for c in (caixa_legenda(quadro(orig, t), 300, 1600) for t in np.linspace(t_c - 12, t_c - 0.2, 24)) if c]
if not caixas:
    sys.exit("legenda do original não achada no fim")
alturas = sorted(b - a for a, b in caixas)
cap_px = int(np.percentile(alturas, 25))
cap_y = int(statistics.median((a + b) / 2 for a, b in caixas if b - a <= 1.6 * alturas[len(alturas) // 2]))
# medida à mão quando o detector pega mão/roupa clara no lugar da legenda (Pedro: mãos juntas no peito)
cap_y, cap_px = C.get("legenda_y", cap_y), C.get("legenda_px", cap_px)
print(f"legenda do original: centro y {cap_y}, maiúscula {cap_px} px")

# 2) boca sincronizada: enquadra no plano de cada tela (rosto no mesmo tamanho, olhos na mesma altura)
boca = R / C.get("boca", f"ls/{C['nome']}.mp4")   # HeyGen (look do próprio bruto) ou boca sincronizada
rb = rostos(boca, 0.1, min(FR["dur"], 6), 0.25)
b_larg, b_cx, b_olhos = med(rb, "larg"), med(rb, "cx"), med(rb, "olhos")
dur = FR["dur"] + C.get("cauda", 0.6)
ws = [dict(w) for w in FR["palavras"]]
texto = (ler_json(R / "ganchos.json", {}).get("variacoes", {}).get(C["nome"], {}).get("texto") or "").split()
if len(texto) == len(ws):          # legenda com o texto da task ("bio", não "Bill" do transcritor)
    for w, t in zip(ws, texto):
        w["p"] = t
else:
    print(f"AVISO: a fala tem {len(ws)} palavras e o texto {len(texto)}; legenda pela transcrição, confira")
plano = C.get("comeca") or ("aberto" if ultimo == "fechado" else "fechado")
trechos, ini = [], 0.0
for k in sorted(C.get("trocas", [])) + [None]:
    t_fim = dur if k is None else ws[k]["i"] - 0.04
    trechos.append((ini, t_fim, plano))
    ini, plano = t_fim, ("aberto" if plano == "fechado" else "fechado")


BW_, BH_ = [int(v) for v in rodar(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                   "stream=width,height", "-of", "csv=p=0", str(boca)]).stdout.split(",")]


def geo(pl):
    """Escala e recorte da fonte para o rosto ficar do tamanho e na altura do plano, dentro da faixa."""
    alvo = PLANOS[pl]
    s = max(alvo["larg"] / b_larg, W / BW_, BH / BH_)
    sw, sh = round(BW_ * s / 2) * 2, round(BH_ * s / 2) * 2
    s = sw / BW_
    x = int(np.clip(b_cx * s - alvo["cx"], 0, sw - W))
    y = int(np.clip(b_olhos * s - (alvo["olhos"] - BY0), 0, sh - BH))
    return sw, sh, x, y


def montar_quadro(im, sw, sh, x, y):
    tela = np.zeros((H, W, 3), np.uint8)
    tela[BY0:BY0 + BH] = cv2.resize(im, (sw, sh), interpolation=cv2.INTER_LANCZOS4)[y:y + BH, x:x + W]
    return tela


# cor: curvas por canal do Clailton da CTA -> Clailton do fim do original (só a região do rosto/corpo)
ref = [quadro(orig, r["t"]) for r in fim[-12:]]
sw, sh, x, y = geo(ultimo)
nov = []
for t in np.linspace(0.3, FR["dur"] - 0.3, 10):
    im = quadro(boca, t)
    nov.append(montar_quadro(im, sw, sh, x, y))
if NOVELA:   # parte de cima da faixa (a legenda fica embaixo)
    zona = lambda a: np.concatenate([q[BY0 + 20:BY0 + int(0.55 * BH), 40:1040].reshape(-1, 3) for q in a])  # noqa: E731
else:
    zona = lambda a: np.concatenate([q[int(cap_y + 80):, 100:980].reshape(-1, 3) for q in a])  # noqa: E731
r_, n_ = zona(ref).astype(np.uint8), zona(nov).astype(np.uint8)
curvas = []
for ch in range(3):
    hr = np.cumsum(np.bincount(r_[:, ch], minlength=256)).astype(float); hr /= hr[-1]
    hn = np.cumsum(np.bincount(n_[:, ch], minlength=256)).astype(float); hn /= hn[-1]
    m = 0.8 * np.interp(hn, hr, np.arange(256)) + 0.2 * np.arange(256)
    m = np.clip(m, np.arange(256) - 35, np.arange(256) + 35)    # casa a cor sem estourar (máx. 35 níveis)
    curvas.append(np.clip(np.convolve(np.pad(m, 4, mode="edge"), np.ones(9) / 9, mode="valid") / 255, 0, 1))
cube = tmp / "cor.cube"
cube.write_text("LUT_1D_SIZE 256\n" + "".join(f"{curvas[0][i]:.6f} {curvas[1][i]:.6f} {curvas[2][i]:.6f}\n"
                                               for i in range(256)))
lut = str(cube).replace("\\", "/").replace(":", "\\:")

# 3) legenda: telas de até 4 palavras / 16 letras, quebra em pontuação (igual aos ganchos)
grupos, g = [], []
for k, w in enumerate(ws):
    g.append(w)
    txt = " ".join(x["p"] for x in g)
    prox = ws[k + 1]["p"] if k + 1 < len(ws) else ""
    if w["p"][-1] in ",.?!" or len(g) == 4 or len(txt + " " + prox) > 16:
        grupos.append(g)
        g = []
if g:
    grupos.append(g)
for k in range(len(grupos) - 1, 0, -1):    # palavra curta sozinha ("BIO") volta para a tela de antes
    if len(grupos[k]) == 1 and len(grupos[k][0]["p"]) <= 5 and             len(" ".join(x["p"] for x in grupos[k - 1] + grupos[k])) <= 22 and grupos[k - 1][-1]["p"][-1] not in ",.?!":
        grupos[k - 1] += grupos.pop(k)
legs = []
for k, g in enumerate(grupos):
    a = 0.0 if k == 0 else g[0]["i"]
    b = grupos[k + 1][0]["i"] if k + 1 < len(grupos) else dur
    legs.append(dict(txt=" ".join(x["p"] for x in g).rstrip(",."), ini=round(a, 3), fim=round(b, 3)))
ass = tmp / "cta.ass"
if NOVELA:
    # legenda no estilo da novela (skill reels-novela-clailton): telas de até 2 linhas, "CLICA NO LINK DA BIO"
    # sozinho e em destaque
    low = [w["p"].lower().strip(",.?!") for w in ws]
    ic = low.index("clica") if "clica" in low else -1
    ib = low.index("bio", max(ic, 0)) if "bio" in low[max(ic, 0):] else -1
    telas, linha, tela = [], [], []
    def fecha_linha():
        global linha
        if linha:
            tela.append(linha)
            linha = []
    def fecha_tela():
        global tela
        fecha_linha()
        if tela:
            telas.append(tela)
            tela = []
    k = 0
    while k < len(ws):
        if k == ic and ib >= ic:
            fecha_tela()
            telas.append([[*range(ic, ib + 1)], "d2"])
            k = ib + 1
            continue
        txt = " ".join(ws[j]["p"] for j in linha + [k])
        if linha and len(txt) > 18:
            fecha_linha()
            if len(tela) == 2:
                fecha_tela()
        linha.append(k)
        if ws[k]["p"][-1] in ",.?!":
            fecha_linha()
            fecha_tela() if ws[k]["p"][-1] in ".?!" or len(tela) == 2 else None
        k += 1
    fecha_tela()
    out = []
    for t in telas:
        if len(t) == 2 and t[1] == "d2":
            out.append("centro | **" + " ".join(ws[j]["p"] for j in t[0]).upper().rstrip(",.") + f" @{t[0][0]}")
        else:
            out.append("centro | " + " / ".join(" ".join(ws[j]["p"] for j in l).upper().rstrip(",") + f" @{l[0]}" for l in t))
    (P / "cta_legenda.txt").write_text(chr(10).join(out) + chr(10), encoding="utf-8")
    import json as _j
    (tmp / "pal.json").write_text(_j.dumps({"alinhado": True, "palavras": [
        dict(texto=w["p"], inicio=w["i"], fim=w["f"]) for w in ws]}, ensure_ascii=False), encoding="utf-8")
    nov_py = Path.home() / ".claude/skills/reels-novela-clailton/scripts/legenda_novela.py"
    r = rodar([sys.executable, str(nov_py), "--plano", str(P / "cta_legenda.txt"), "--palavras", str(tmp / "pal.json"),
               "--out", str(ass), "--sem-cta", "--y-centro", f"{BY0 + 0.69 * BH:.0f}",
               "--topo-min", f"{BY0 + 0.41 * BH:.0f}", "--base-max", f"{BY0 + BH - 30:.0f}"])
    print("legenda novela:", (r.stdout + r.stderr).strip()[-600:])
else:
    legenda_ass(legs, ass, cap_y, cap_px)
fdir = str(Path.home() / ".claude/skills/reels-novela-clailton/fonts").replace("\\", "/").replace(":", "\\:")
ass_f = str(ass).replace("\\", "/").replace(":", "\\:")

# 4) vídeo da CTA: cada trecho no seu plano (zoom seco na troca), cor casada, legenda
partes = []
for i, (a, b, pl) in enumerate(trechos):
    sw, sh, x, y = geo(pl)
    partes.append(f"[0:v]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS,scale={sw}:{sh}:flags=lanczos,"
                  f"crop={W}:{BH}:{x}:{y},pad={W}:{H}:0:{BY0}:black,setsar=1[p{i}]")
# look do HeyGen feito com o próprio bruto já tem a cor do reel; a curva só estragava a pele (15/10/2026)
cor = "" if C.get("cor") is False or (C.get("cor") is None and "heygen" in str(boca)) else f"lut1d=file='{lut}',"
cadeia = ";".join(partes) + ";" + "".join(f"[p{i}]" for i in range(len(trechos))) + \
    f"concat=n={len(trechos)}:v=1:a=0,{cor}ass='{ass_f}':fontsdir='{fdir}',format=yuv420p[v]"
cta_v = tmp / "cta.mp4"
rodar(["ffmpeg", "-v", "error", "-y", "-stream_loop", "1", "-i", str(boca), "-filter_complex", cadeia,
       "-map", "[v]", "-t", f"{dur:.3f}", "-r", "30000/1001", "-c:v", "libx264", "-crf", "16", "-preset", "slow",
       str(cta_v)])

# 5) som: voz casada com o fim do original (timbre, volume e ambiente/música por baixo)
casada = R / "vozes" / f"{C['nome']}_casada.wav"
rodar([sys.executable, str(S / "casar_voz.py"), str(R / "vozes" / f"{C['nome']}.wav"), str(orig),
       str(round(t_c * FPS)), str(casada), "antes"])

# volume da CTA = volume do fim do original (16/10/2026: a CTA ficava ~2 dB mais baixa)
g_cta = float(np.clip(lufs(orig, max(0, t_c - 8), min(8, t_c)) - lufs(casada), -6, 6))
print(f"volume da CTA ajustado em {g_cta:+.1f} dB")

# 6) emenda: original até o corte + CTA (corte seco no vídeo, 30 ms de cruzamento no som)
saida = P / f"{C['pauta']}.mp4"
rodar(["ffmpeg", "-v", "error", "-y", "-i", str(orig), "-i", str(cta_v), "-i", str(casada), "-filter_complex",
       f"[0:v]trim=0:{t_c:.4f},setpts=PTS-STARTPTS,fps=30000/1001,setsar=1,format=yuv420p[a];"
       f"[1:v]fps=30000/1001,setsar=1,format=yuv420p[b];[a][b]concat=n=2:v=1:a=0[v];"
       f"[0:a]atrim=0:{t_c + 0.03:.4f},asetpts=PTS-STARTPTS,aresample=48000,afade=t=out:st={t_c - 0.03:.4f}:d=0.06[x];"
       f"[2:a]aresample=48000,volume={g_cta:.2f}dB,apad=whole_dur={dur:.3f},afade=t=out:st={dur - 0.35:.3f}:d=0.35[y];"
       f"[x][y]acrossfade=d=0.03:c1=tri:c2=tri[s]",
       "-map", "[v]", "-map", "[s]", "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", str(saida)])

# 7) conferência: 6 quadros antes do corte x 6 da CTA + volume antes/depois
d_tot = float(rodar(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                     str(saida)]).stdout)
ts = list(np.linspace(t_c - 3, t_c - 0.05, 6)) + list(np.linspace(t_c + 0.05, d_tot - 0.1, 6))
qa = np.hstack([cv2.resize(quadro(saida, t)[:, :, ::-1], (216, 384)) for t in ts])
cv2.line(qa, (216 * 6, 0), (216 * 6, 384), (0, 0, 255), 3)
cv2.imwrite(str(P / f"{reel}_qa.jpg"), qa)
print(f"volume: fim do original {lufs(saida, t_c - 8, 8):.1f} LUFS | CTA {lufs(saida, t_c, d_tot - t_c):.1f} LUFS")
print("pronto:", saida, f"({d_tot:.1f} s; CTA {dur:.1f} s a partir de {t_c:.2f} s)")
