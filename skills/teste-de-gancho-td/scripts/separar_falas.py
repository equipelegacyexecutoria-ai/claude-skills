"""Separa o vídeo do HeyGen (todas as frases de gancho numa gravação só, separadas por " ... ") em uma
fala por variação, com o tempo de cada palavra.

Uso: python separar_falas.py <W> <video_heygen.mp4> <nome1> <nome2> ...
     nomes na MESMA ordem em que as frases foram digitadas no HeyGen (ex.: padre_v2 padre_v3 chegada_v2).
Grava <W>/vozes/<nome>.wav e junta em <W>/vozes/frases.json: {nome: {dur, palavras: [{i, f, p}]}}.
Confere cada fala com o texto de <W>/ganchos.json (se existir) e avisa quando não bater.
"""
import difflib, re, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from comum import gravar_json, ler_json, palavras, rodar  # noqa: E402

R, video, nomes = Path(sys.argv[1]), sys.argv[2], sys.argv[3:]
voz = R / "vozes"
voz.mkdir(parents=True, exist_ok=True)
wav = voz / (Path(video).stem + ".wav")
rodar(["ffmpeg", "-v", "error", "-y", "-i", video, "-vn", "-ac", "1", "-ar", "48000", str(wav)])
ws = palavras(wav)
G = ler_json(R / "ganchos.json", {}).get("variacoes", {})
FR = ler_json(voz / "frases.json", {})


def norm(s):
    return re.sub(r"[^\w ]", "", s.lower())


def tokens(s):
    return [t for t in norm(s.replace("-", " ")).split() if t]


if all(G.get(n, {}).get("texto") for n in nomes):
    # fronteiras pelo texto: alinha as palavras ouvidas com as frases digitadas, em ordem
    esperado, dono = [], []
    for k, n in enumerate(nomes):
        tk = tokens(G[n]["texto"])
        esperado += tk
        dono += [k] * len(tk)
    ouvido, idx = [], []
    for j, w in enumerate(ws):
        for t in tokens(w["p"]):
            ouvido.append(t)
            idx.append(j)
    sm = difflib.SequenceMatcher(None, esperado, ouvido, autojunk=False)
    mapa = {}
    for a, b, size in sm.get_matching_blocks():
        for d in range(size):
            mapa[a + d] = idx[b + d]
    cortes = [0]
    for k in range(1, len(nomes)):
        primeiros = [i for i, o in enumerate(dono) if o == k and i in mapa]
        if not primeiros:
            sys.exit(f"não achei a fala de {nomes[k]} no áudio: confira a ordem dos nomes")
        i0 = primeiros[0]
        j = mapa[i0] - (i0 - dono.index(k))   # volta as palavras da frase que não casaram
        cortes.append(max(cortes[-1] + 1, j))
    cortes.append(len(ws))
else:
    # sem os textos: as (n-1) maiores pausas ("..." no HeyGen vira pausa longa; pode errar em frase com vírgula)
    print("AVISO: sem os textos em ganchos.json; separei pelas maiores pausas")
    gaps = sorted(range(1, len(ws)), key=lambda k: ws[k]["i"] - ws[k - 1]["f"], reverse=True)[:len(nomes) - 1]
    cortes = [0] + sorted(gaps) + [len(ws)]


for k, nome in enumerate(nomes):
    pal = ws[cortes[k]:cortes[k + 1]]
    a = max(0.0, pal[0]["i"] - 0.06)
    if cortes[k] > 0:
        a = max(a, ws[cortes[k] - 1]["f"] + 0.02)
    b = pal[-1]["f"] + 0.15
    if cortes[k + 1] < len(ws):
        b = min(b, ws[cortes[k + 1]]["i"] - 0.02)
    rodar(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", str(wav),
           "-c:a", "pcm_s16le", str(voz / f"{nome}.wav")])
    FR[nome] = dict(dur=round(b - a, 3), palavras=[dict(i=round(w["i"] - a, 2), f=round(w["f"] - a, 2), p=w["p"])
                                                   for w in pal])
    texto = " ".join(w["p"] for w in pal)
    aviso = ""
    if nome in G and G[nome].get("texto"):
        r = difflib.SequenceMatcher(None, norm(texto), norm(G[nome]["texto"])).ratio()
        aviso = "" if r > 0.85 else f"   <-- NÃO BATE com ganchos.json ({r:.0%}): confira a ordem dos nomes"
    print(f"{nome}: {b - a:.2f} s | {texto}{aviso}")
gravar_json(voz / "frases.json", FR)
