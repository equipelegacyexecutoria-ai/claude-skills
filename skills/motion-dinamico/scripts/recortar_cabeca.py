# Boneco de papel: separa a cabeça (polígono) do corpo para ela balançar no pescoço.
# As coordenadas são em px da imagem JÁ preparada (assets/img/<nome>.png), lidas na grade (grade/<nome>.jpg).
# uso: python recortar_cabeca.py <projeto> cortes.json
#   cortes.json = {"pensativo": {"poligono": [[x,y],...], "pivo": [x,y], "corte": y}, ...}
#   poligono: contorno da cabeça (suba até y=0 se o cabelo encosta no topo); pivo: ponto do pescoço;
#   corte: no corpo some só o que está acima desta linha (o pescoço fica no corpo).
import json, os, sys
import numpy as np, cv2

PROJ, CORTES = sys.argv[1], json.load(open(sys.argv[2], encoding="utf-8"))
IMG = os.path.join(PROJ, "assets", "img"); OUT = os.path.join(PROJ, "assets", "partes"); os.makedirs(OUT, exist_ok=True)
ler = lambda p: cv2.imdecode(np.fromfile(p, np.uint8), cv2.IMREAD_UNCHANGED)
grava = lambda p, im: cv2.imencode(".png", im)[1].tofile(p)
pj = os.path.join(OUT, "partes.json")
info = json.load(open(pj, encoding="utf-8")) if os.path.exists(pj) else {}
for nome, c in CORTES.items():
    im = ler(os.path.join(IMG, nome + ".png")); H, W = im.shape[:2]
    m = np.zeros((H, W), np.uint8); cv2.fillPoly(m, [np.array(c["poligono"], np.int32)], 255)
    m = cv2.GaussianBlur(m, (0, 0), 1.0)
    part = im.copy(); part[..., 3] = (im[..., 3].astype(np.uint16) * m // 255).astype(np.uint8)
    ys, xs = np.where(part[..., 3] > 8); x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    grava(os.path.join(OUT, f"{nome}_cab.png"), part[y0:y1, x0:x1])
    rm = m.copy(); rm[int(c["corte"]):, :] = 0
    corpo = im.copy(); corpo[..., 3] = (im[..., 3].astype(np.uint16) * (255 - rm) // 255).astype(np.uint8)
    grava(os.path.join(OUT, f"{nome}_corpo.png"), corpo)
    px, py = c["pivo"]
    info[nome] = {"W": W, "H": H, "partes": [{"nome": "cab", "x": int(x0), "y": int(y0), "w": int(x1 - x0), "h": int(y1 - y0), "px": float(px - x0), "py": float(py - y0)}]}
    print(nome, "ok")
json.dump(info, open(pj, "w"), indent=1)
