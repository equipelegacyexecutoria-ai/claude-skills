"""Utilidades de mídia: rostos na imagem, recorte 'cover' no assunto, miniaturas por layout."""
from __future__ import annotations

import threading
from pathlib import Path

import numpy as np
from PIL import Image

from td_comum import EMENDA, H, MODELO_ROSTO, SKILL, W, wh_video

_local = threading.local()
LAYOUT_WH = {"cheia": (W, H), "topo": (W, EMENDA), "dividida": (W, EMENDA), "cartao": (W, H)}


def rostos(img: Image.Image) -> list[list[float]]:
    """Rostos (YuNet) em coordenadas normalizadas [x, y, w, h, score]."""
    import cv2
    im = img.convert("RGB")
    esc = 640 / max(im.size)
    if esc < 1:
        im = im.resize((max(1, int(im.width * esc)), max(1, int(im.height * esc))))
    arr = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2BGR)
    h, w = arr.shape[:2]
    if getattr(_local, "wh", None) != (w, h):
        _local.det = cv2.FaceDetectorYN.create(str(MODELO_ROSTO), "", (w, h), 0.7, 0.3, 50)
        _local.wh = (w, h)
    _, fs = _local.det.detect(arr)
    if fs is None:
        return []
    return [[float(f[0] / w), float(f[1] / h), float(f[2] / w), float(f[3] / h), float(f[14])] for f in fs
            if f[2] / w > 0.03]


def area_util(video: str) -> tuple[int, int, int, int]:
    """Área sem as tarjas pretas (letterbox/pillarbox) do trecho: (x, y, w, h). Cena de filme no
    YouTube costuma vir 2,39:1 dentro de 16:9 (ex.: 1920x792 dentro de 1920x1080)."""
    import re as _re
    import subprocess
    from collections import Counter
    vw, vh = wh_video(video)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", video, "-vf", "cropdetect=24:2:0", "-frames:v", "60",
                        "-f", "null", "-"], capture_output=True, text=True)
    achados = Counter(_re.findall(r"crop=(\d+):(\d+):(\d+):(\d+)", r.stderr))
    if not achados:
        return 0, 0, vw, vh
    w, h, x, y = (int(v) for v in achados.most_common(1)[0][0])
    y, h = _sem_logo_na_tarja(video, y, h)
    if w < vw * 0.5 or h < vh * 0.4 or (w > vw * 0.96 and h > vh * 0.96):
        return 0, 0, vw, vh
    # borda escura e macia logo depois da tarja (filme antigo/desenho: Popeye ficou com 22 px de preto): 1% a mais
    if h < vh - 2:
        d = max(2, int(round(h * 0.01)))
        y, h = y + d, h - 2 * d
    if w < vw - 2:
        d = max(2, int(round(w * 0.01)))
        x, w = x + d, w - 2 * d
    return x, y, w, h


def _sem_logo_na_tarja(video: str, y: int, h: int) -> tuple[int, int]:
    """O cropdetect inclui logo escrito DENTRO da tarja ("MOVIECLIPS.COM" na faixa de baixo) e a tarja ficava
    na tela (09/10/2026). Linha a linha (máximo em 12 quadros): fica o maior bloco contínuo com imagem."""
    import cv2
    c = cv2.VideoCapture(video)
    n = int(c.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
    acc = None
    for i in np.linspace(0, n - 1, 12).astype(int):
        c.set(cv2.CAP_PROP_POS_FRAMES, int(i))
        ok, f = c.read()
        if ok:
            g = f.mean(2)
            acc = g if acc is None else np.maximum(acc, g)
    c.release()
    if acc is None:
        return y, h
    linhas = np.percentile(acc[y:y + h], 90, axis=1) > 12
    melhor, ini = (0, 0), None
    for k, v in enumerate(list(linhas) + [False]):
        if v and ini is None:
            ini = k
        elif not v and ini is not None:
            if k - ini > melhor[1] - melhor[0]:
                melhor = (ini, k)
            ini = None
    if h - 6 > melhor[1] - melhor[0] > 0.3 * h:
        return y + melhor[0], melhor[1] - melhor[0]
    return y, h


def caixa_cover(iw: int, ih: int, ow: int, oh: int, foco: tuple[float, float] | None = None,
                faces: list | None = None) -> tuple[float, float, float, float]:
    """Maior recorte com o aspecto ow:oh dentro da imagem, centrado no foco (rostos > foco dado > centro).
    Devolve (x, y, w, h) em pixels da imagem."""
    alvo = ow / oh
    if iw / ih > alvo:
        ch, cw = ih, ih * alvo
    else:
        cw, ch = iw, iw / alvo
    fx, fy = 0.5, 0.45
    if faces:
        grande = [f for f in faces if f[2] >= 0.6 * max(g[2] for g in faces)]
        x0 = min(f[0] for f in grande)
        x1 = max(f[0] + f[2] for f in grande)
        y0 = min(f[1] for f in grande)
        y1 = max(f[1] + f[3] for f in grande)
        fx, fy = (x0 + x1) / 2, (y0 + y1) / 2 + 0.05     # um pouco abaixo do centro do rosto (queixo/peito)
    if foco:
        fx = foco[0] if foco[0] is not None else fx
        fy = foco[1] if len(foco) > 1 and foco[1] is not None else fy
    x = min(max(fx * iw - cw / 2, 0), iw - cw)
    y = min(max(fy * ih - ch / 2, 0), ih - ch)
    return x, y, cw, ch


def miniatura(caminho: Path, layout: str, tw: int, th: int, faces=None, foco=None) -> Image.Image:
    """Como a imagem vai aparecer no quadro (recortada no layout), reduzida para tw x th (9:16)."""
    img = Image.open(caminho).convert("RGB")
    cel = Image.new("RGB", (tw, th), (70, 70, 70))
    if layout in ("topo", "dividida"):
        bw, bh = tw, int(round(th * EMENDA / H))
        x, y, w, h = caixa_cover(img.width, img.height, bw, bh, foco, faces)
        cel.paste(img.crop((int(x), int(y), int(x + w), int(y + h))).resize((bw, bh)), (0, 0))
        cel.paste((40, 60, 90), (0, bh, tw, th))                 # onde fica o Clailton
    elif layout == "cartao":
        cel.paste((236, 236, 236), (0, 0, tw, th))
        cw = int(tw * 0.86)
        ch = int(cw * img.height / img.width)
        if ch > th * 0.6:
            ch = int(th * 0.6)
            cw = int(ch * img.width / img.height)
        cel.paste(img.resize((cw, ch)), ((tw - cw) // 2, int(th * 0.40 - ch / 2)))
    else:
        x, y, w, h = caixa_cover(img.width, img.height, tw, th, foco, faces)
        cel.paste(img.crop((int(x), int(y), int(x + w), int(y + h))).resize((tw, th)), (0, 0))
    return cel


def dhash(img: Image.Image) -> int:
    g = np.asarray(img.convert("L").resize((9, 8)), dtype=np.int16)
    bits = (g[:, 1:] > g[:, :-1]).flatten()
    return int("".join("1" if b else "0" for b in bits), 2)


def hamming(a: int, b: int) -> int:
    return bin(a ^ b).count("1")


MODELO_TEXTO = SKILL / "models" / "text_detection_en_ppocrv3_2023may.onnx"
MODELO_TEXTO_URL = ("https://github.com/opencv/opencv_zoo/raw/main/models/text_detection_ppocr/"
                    "text_detection_en_ppocrv3_2023may.onnx")


def _detector_texto():
    """PP-OCRv3 DB (um por thread: o cv2.dnn não é seguro entre threads)."""
    import cv2
    if not hasattr(_local, "txt"):
        if not MODELO_TEXTO.exists():
            import urllib.request
            MODELO_TEXTO.parent.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(MODELO_TEXTO_URL, MODELO_TEXTO)
        m = cv2.dnn_TextDetectionModel_DB(str(MODELO_TEXTO))
        m.setBinaryThreshold(0.3).setPolygonThreshold(0.5).setMaxCandidates(200).setUnclipRatio(2.0)
        m.setInputParams(1.0 / 255.0, (736, 736), (122.67891434, 116.66876762, 104.00698793), True)
        _local.txt = m
    return _local.txt


def caixas_texto(rgb: np.ndarray, layout: str | None = None) -> list[tuple[float, float, float, float]]:
    """Caixas de texto (x, y, w, h), em fração do recorte VISÍVEL do layout (só o que aparece no reel)."""
    import cv2
    h, w = rgb.shape[:2]
    if layout in LAYOUT_WH and layout != "cartao":
        cx, cy, cw, ch = (int(round(v)) for v in caixa_cover(w, h, *LAYOUT_WH[layout]))
    else:
        cx, cy, cw, ch = 0, 0, w, h
    rec = np.ascontiguousarray(rgb[cy:cy + ch, cx:cx + cw, ::-1])        # recorte em BGR: mais resolução no que importa
    boxes, _ = _detector_texto().detect(rec)
    out = []
    for b in boxes:
        bx, by, bw, bh = cv2.boundingRect(np.array(b, np.int32))
        out.append((bx / cw, by / ch, bw / cw, bh / ch))
    return out


def logo_fixo(quadros: list[np.ndarray], layout: str | None = None) -> bool:
    """Logo de canal/streaming (hulu, Netflix, canal do YouTube, emissora) no recorte visível: texto pequeno,
    perto da borda e no MESMO lugar em todos os quadros da amostra (legenda muda; logo fica)."""
    cxs = [caixas_texto(q, layout) for q in quadros]
    if len(cxs) < 2 or not cxs[0]:
        return False

    def iou(a, b) -> float:
        ix = max(0.0, min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0]))
        iy = max(0.0, min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1]))
        i = ix * iy
        return i / max(1e-9, a[2] * a[3] + b[2] * b[3] - i)

    for b in cxs[0]:
        x, y, w, h = b
        if w * h > 0.03 or min(x, y, 1 - x - w, 1 - y - h) > 0.2:      # grande (legenda/crédito) ou no meio
            continue
        if all(any(iou(b, o) > 0.35 for o in outros) for outros in cxs[1:]):
            return True
    return False


def texto_pct(caminho, layout: str | None = None) -> float:
    """% do quadro VISÍVEL coberto por texto (detector PP-OCRv3 DB do OpenCV Zoo, 2,4 MB). Com layout,
    só conta o texto dentro do recorte daquele layout (crédito de filme no canto some no 9:16).
    Legenda queimada, legenda de TikTok e miniatura de YouTube dão 1,8-13%; quadro limpo 0-0,9%."""
    import cv2
    im = cv2.cvtColor(np.asarray(Image.open(caminho).convert("RGB")), cv2.COLOR_RGB2BGR)   # PIL: caminho com acento
    boxes, _ = _detector_texto().detect(im)
    h, w = im.shape[:2]
    if layout in LAYOUT_WH and layout != "cartao":
        cx, cy, cw, ch = caixa_cover(w, h, *LAYOUT_WH[layout])
    else:
        cx, cy, cw, ch = 0, 0, w, h
    tot = 0.0
    for b in boxes:
        bx, by, bw, bh = cv2.boundingRect(np.array(b, np.int32))
        ix = max(0, min(bx + bw, cx + cw) - max(bx, cx))
        iy = max(0, min(by + bh, cy + ch) - max(by, cy))
        tot += ix * iy
    return round(100.0 * tot / (cw * ch), 2)
