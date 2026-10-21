# B-roll do acervo (pasta B-ROLLS da tela dividida) para o Motion Dinâmico: corta o trecho exato, tira a tarja preta
# (cropdetect), enquadra no tamanho do lugar (tela cheia 1080x1920 ou metade de cima da tela dividida) e tira o som.
# uso: python preparar_broll.py <projeto> trechos.json
#   trechos.json = [{"nome": "s2", "acervo": "BB-06" (ou "arquivo": "<caminho de um vídeo fora do acervo>"), "t": 80.2, "dur": 2.45, "fonte_dur": 1.0, "lugar": "cheia"|"topo",
#                    "x": 0.5, "y": 0.5}]   fonte_dur < dur = câmera lenta (trecho curto esticado); x/y = centro do recorte (0–1);
#   y vale quando a fonte é mais alta que o lugar (vídeo vertical no topo da tela dividida: suba para não cortar a cabeça)
import json, os, re, subprocess, sys

PROJ, TRECHOS = sys.argv[1], json.load(open(sys.argv[2], encoding="utf-8"))
TOPO_H = int(os.environ.get("TOPO_H", 900))
LUGAR = {"cheia": (1080, 1920), "topo": (1080, TOPO_H)}
CFG = os.path.join(os.environ.get("LOCALAPPDATA", ""), "reels-novela", "acervo.txt")
R = open(CFG, encoding="utf-8").read().strip().strip('"') if os.path.exists(CFG) else os.path.join(os.path.expanduser("~"), "Desktop", "B-ROLLS")
A = {v["codigo"]: v for v in json.load(open(os.path.join(R, "acervo.json"), encoding="utf-8"))["videos"]}
OUT = os.path.join(PROJ, "assets", "broll"); os.makedirs(OUT, exist_ok=True)


def tarja(f, t, d):
    """Área útil sem tarja preta (maior caixa vista pelo cropdetect no trecho)."""
    r = subprocess.run(["ffmpeg", "-ss", f"{t:.3f}", "-t", f"{max(d, 0.5):.3f}", "-i", f, "-vf", "cropdetect=24:2:0", "-f", "null", "-"],
                       capture_output=True, text=True)
    cs = [tuple(map(int, m)) for m in re.findall(r"crop=(\d+):(\d+):(\d+):(\d+)", r.stderr)]
    return max(cs, key=lambda c: c[0] * c[1]) if cs else None


for tr in TRECHOS:
    if "arquivo" in tr:  # vídeo fora do acervo (ex.: baixado pelo usuário)
        f = tr["arquivo"]
        w, h = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                                        "-of", "csv=p=0", f], capture_output=True, text=True).stdout.strip().split(",")[:2])
        v = {"w": w, "h": h}; tr.setdefault("acervo", os.path.basename(f)[:20])
    else:
        v = A[tr["acervo"]]; f = os.path.join(R, v["arquivo"])
    W, H = LUGAR[tr["lugar"]]; fd = tr.get("fonte_dur", tr["dur"])
    cw, ch, cx, cy = tarja(f, tr["t"], fd) or (v["w"], v["h"], 0, 0)
    # recorte "cobrir" com a proporção do lugar, centrado em x (padrão meio)
    if cw / ch > W / H:
        nw = int(ch * W / H) // 2 * 2; nh = ch // 2 * 2
        x0 = cx + int(max(0, min(cw - nw, tr.get("x", 0.5) * cw - nw / 2))); y0 = cy
    else:
        nw = cw // 2 * 2; nh = int(cw * H / W) // 2 * 2
        x0 = cx; y0 = cy + int(max(0, min(ch - nh, tr.get("y", 0.5) * ch - nh / 2)))
    vel = tr["dur"] / fd
    vf = f"crop={nw}:{nh}:{x0}:{y0},scale={W}:{H}:flags=lanczos,setpts={vel:.4f}*(PTS-STARTPTS),fps=30,format=yuv420p"
    o = os.path.join(OUT, f"{tr['nome']}.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{tr['t']:.3f}", "-i", f, "-t", f"{fd:.3f}", "-an", "-vf", vf,
                    "-c:v", "libx264", "-crf", "15", "-preset", "medium", "-g", "15", "-t", f"{tr['dur']:.3f}", o], check=True)
    print(tr["nome"], tr["acervo"], f"tarja {cw}x{ch}+{cx}+{cy}", f"-> {W}x{H}", f"vel x{1 / vel:.2f}" if vel != 1 else "")
