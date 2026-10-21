# Recorta à mão uma parte do corpo (braço, antebraço, cabeça) de uma ilustração e prepara o fundo por trás dela,
# para animar a parte girando na junta (estilo "marionete" com personagem normal).
# uso: python recortar_parte.py partes.json
#   partes.json = {"base": "cena.jpg", "fundo": "cena_sem_parte.jpg" (opcional), "saida": "<pasta>", "largura": 1080,
#                  "nome": "s01", "partes": [{"nome": "antebraco", "poligono": [[x, y], ...], "pivo": [x, y]}],
#                  "trocar": [[[x, y], ...]]}   (regiões extras do fundo a pegar da imagem "fundo", ex.: fumaça)
#   Coordenadas na imagem original. "fundo" é outra versão da mesma cena (gerada a partir dela) em que a parte está em
#   outro lugar: dentro do polígono (alargado) o fundo vem dela. Sem "fundo", o buraco é preenchido com a cor vizinha.
# Gera <nome>_fundo.png (cena inteira sem as partes), <nome>_<parte>.png (só a parte, transparente, recortada) e
# <nome>.json com posição, tamanho e pivô de cada parte já na escala da largura final.
import json, os, sys
from PIL import Image, ImageDraw, ImageFilter

cfg = json.load(open(sys.argv[1], encoding="utf-8"))
base = Image.open(cfg["base"]).convert("RGB")
W0, H0 = base.size
esc = cfg.get("largura", 1080) / W0
fundo = Image.open(cfg["fundo"]).convert("RGB").resize(base.size) if cfg.get("fundo") else None
os.makedirs(cfg["saida"], exist_ok=True)
plate = base.copy()
info = {"largura": round(W0 * esc), "altura": round(H0 * esc), "partes": []}

troca = Image.new("L", base.size, 0)
for p in cfg["partes"]:
    ImageDraw.Draw(troca).polygon([tuple(v) for v in p["poligono"]], fill=255)
for pol in cfg.get("trocar", []):
    ImageDraw.Draw(troca).polygon([tuple(v) for v in pol], fill=255)
troca = troca.filter(ImageFilter.MaxFilter(31)).filter(ImageFilter.GaussianBlur(6))
if fundo is not None:
    plate.paste(fundo, (0, 0), troca)
else:  # sem segunda versão: borra a região com a vizinhança (só serve para movimento pequeno)
    plate.paste(base.filter(ImageFilter.GaussianBlur(40)), (0, 0), troca)
plate.resize((info["largura"], info["altura"]), Image.LANCZOS).save(os.path.join(cfg["saida"], f'{cfg["nome"]}_fundo.png'))

dif = None
if fundo is not None:  # o que muda entre as duas versões é só a parte: o recorte fica justo nela (sem pedaço do cenário)
    from PIL import ImageChops
    dif = ImageChops.difference(base, fundo).convert("L").point(lambda v: 255 if v > 28 else 0)
    dif = dif.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(9))

for p in cfg["partes"]:
    m = Image.new("L", base.size, 0)
    ImageDraw.Draw(m).polygon([tuple(v) for v in p["poligono"]], fill=255)
    if dif is not None and p.get("justo", True):
        m = ImageChops.multiply(m, dif)
        cheio = m.copy()  # tapa os furos internos (partes da mão iguais nas duas versões)
        ImageDraw.floodfill(cheio, (0, 0), 128)
        m = cheio.point(lambda v: 0 if v == 128 else 255)
        m = m.filter(ImageFilter.MaxFilter(5))
    m = m.filter(ImageFilter.GaussianBlur(1.2))
    x0, y0, x1, y1 = m.getbbox()
    peca = base.crop((x0, y0, x1, y1)).convert("RGBA")
    peca.putalpha(m.crop((x0, y0, x1, y1)))
    w, h = round((x1 - x0) * esc), round((y1 - y0) * esc)
    peca.resize((w, h), Image.LANCZOS).save(os.path.join(cfg["saida"], f'{cfg["nome"]}_{p["nome"]}.png'))
    px, py = p["pivo"]
    info["partes"].append({"nome": p["nome"], "x": round(x0 * esc), "y": round(y0 * esc), "w": w, "h": h,
                           "pivo": [round((px - x0) / (x1 - x0) * 100, 1), round((py - y0) / (y1 - y0) * 100, 1)]})
json.dump(info, open(os.path.join(cfg["saida"], f'{cfg["nome"]}.json'), "w", encoding="utf-8"), indent=1)
print(json.dumps(info))
