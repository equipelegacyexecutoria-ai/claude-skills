"""Ranking texto x imagem com CLIP ViT-L/14 na GPU (roda na venv do alinhador: torch CUDA + transformers).

Entrada: JSON {"pedidos": [{"id": "...", "texto": "english description", "imagens": ["a.jpg", ...]}]}
Saída:   JSON {"id": [score, ...]}  (similaridade de cosseno x 100, na ordem das imagens)
         + {"id#marca": [m, ...]} quando o pedido tem "marca": true — "cara de banco com marca"
           zero-shot do CLIP (sozinho erra: foto de banco LIMPA também pontua alto)
         + {"id#wm": [p, ...]} probabilidade de marca d'água do detector da LAION (EfficientNet-B3,
           models/watermark_model_v1.pt): stablediffusionweb 0,80 · dreamstime 0,47 · limpas 0,1-0,35
         + {"id#iqa": [q, ...]} quando o pedido tem "iqa": true — qualidade CLIP-IQA (Wang et al. 2023):
           P("boa") média dos pares boa/ruim, nítida/borrada, clara/escura (0-1)

Uso: python clip_rank.py entrada.json saida.json
"""
from __future__ import annotations

import json
import sys
import time
import warnings

warnings.filterwarnings("ignore")
MODELO = "openai/clip-vit-large-patch14"
LOTE = 48
WM = __import__("pathlib").Path(__file__).resolve().parent.parent / "models" / "watermark_model_v1.pt"
WM_URL = "https://github.com/LAION-AI/LAION-5B-WatermarkDetection/raw/main/models/watermark_model_v1.pt"


def detector_marca(dev):
    """Detector de marca d'água da LAION (precisa de timm; baixa os pesos na 1ª vez)."""
    try:
        import timm
        import torch
        import torch.nn as nn
        import torchvision.transforms as T
        if not WM.exists():
            import urllib.request
            WM.parent.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(WM_URL, WM)
        m = timm.create_model("efficientnet_b3a", pretrained=False, num_classes=2)
        m.classifier = nn.Sequential(nn.Linear(1536, 625), nn.ReLU(), nn.Dropout(p=0.3), nn.Linear(625, 256),
                                     nn.ReLU(), nn.Linear(256, 2))
        m.load_state_dict(torch.load(str(WM), map_location="cpu"))
        tf = T.Compose([T.Resize((256, 256)), T.ToTensor(), T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
        return m.to(dev).eval(), tf
    except Exception as e:  # noqa: BLE001
        print(f"[clip] detector de marca d'água indisponível: {e!r}"[:160], flush=True)
        return None, None


def lotes_gpu(caminhos: list[str], dev, dt, lote: int = 64):
    """Lotes de pixel_values do CLIP (lado menor 224 bicúbico + recorte central + normalização) feitos na
    GPU; a decodificação dos JPEG roda em 8 threads e o lote seguinte é lido enquanto a GPU trabalha."""
    from concurrent.futures import ThreadPoolExecutor

    import numpy as np
    import torch
    import torch.nn.functional as F
    from torchvision.io import ImageReadMode, decode_jpeg
    media = torch.tensor([0.48145466, 0.4578275, 0.40821073], device=dev).view(1, 3, 1, 1)
    desvio = torch.tensor([0.26862954, 0.26130258, 0.27577711], device=dev).view(1, 3, 1, 1)

    def ler(f: str):
        with open(f, "rb") as fh:                                          # open(): caminho com acento
            return torch.frombuffer(bytearray(fh.read()), dtype=torch.uint8)

    def decodificar(dados):
        """JPEG decodificado na GPU (nvjpeg); se falhar, na CPU pelo PIL."""
        try:
            return decode_jpeg(dados, mode=ImageReadMode.RGB, device=dev)
        except Exception:  # noqa: BLE001
            import io
            from PIL import Image
            out = []
            for d in dados:
                try:
                    a = np.asarray(Image.open(io.BytesIO(d.numpy().tobytes())).convert("RGB"))
                except Exception:  # noqa: BLE001
                    a = np.zeros((224, 224, 3), np.uint8)
                out.append(torch.from_numpy(a.copy()).permute(2, 0, 1).to(dev))
            return out

    def preparar(dados):
        out = []
        for t in decodificar(dados):
            t = t.unsqueeze(0).float() / 255
            h, w = t.shape[2:]
            s = 224 / min(h, w)
            t = F.interpolate(t, size=(max(224, round(h * s)), max(224, round(w * s))), mode="bicubic",
                              align_corners=False, antialias=True)
            h, w = t.shape[2:]
            y0, x0 = (h - 224) // 2, (w - 224) // 2
            out.append(t[:, :, y0:y0 + 224, x0:x0 + 224])
        return ((torch.cat(out).clamp(0, 1) - media) / desvio).to(dt)

    grupos = [caminhos[k:k + lote] for k in range(0, len(caminhos), lote)]
    with ThreadPoolExecutor(8) as leitura, ThreadPoolExecutor(1) as adiante:
        futuro = adiante.submit(lambda g: list(leitura.map(ler, g)), grupos[0]) if grupos else None
        for k in range(len(grupos)):
            arrs = futuro.result()
            if k + 1 < len(grupos):
                futuro = adiante.submit(lambda g: list(leitura.map(ler, g)), grupos[k + 1])
            yield preparar(arrs)


def main() -> None:
    import torch
    from PIL import Image
    from transformers import CLIPModel, CLIPProcessor

    ent = json.load(open(sys.argv[1], encoding="utf-8"))
    t0 = time.time()
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    dt = torch.float16 if dev == "cuda" else torch.float32
    try:
        model = CLIPModel.from_pretrained(MODELO, dtype=dt, use_safetensors=True, local_files_only=True,
                                          attn_implementation="sdpa")        # +25% no laptop
    except Exception:
        model = CLIPModel.from_pretrained(MODELO, dtype=dt, use_safetensors=True)
    model = model.to(dev).eval()
    try:
        proc = CLIPProcessor.from_pretrained(MODELO, use_fast=True)
    except Exception:
        proc = CLIPProcessor.from_pretrained(MODELO)
    wm_model, wm_tf = detector_marca(dev) if any(p.get("marca") for p in ent["pedidos"]) else (None, None)
    print(f"[clip] modelo em {time.time() - t0:.1f}s ({dev})", flush=True)
    out = {}
    with torch.no_grad():
        tm = proc(text=["a stock photo covered with a repeated watermark logo text",
                        "a clean photo without any watermark or text"], return_tensors="pt", padding=True).to(dev)
        tme = model.get_text_features(**tm)
        tme = tme / tme.norm(dim=-1, keepdim=True)
        pares = [("Good photo.", "Bad photo."), ("Sharp photo.", "Blurry photo."), ("Bright photo.", "Dark photo.")]
        tq = proc(text=[t for par in pares for t in par], return_tensors="pt", padding=True).to(dev)
        tqe = model.get_text_features(**tq)
        tqe = tqe / tqe.norm(dim=-1, keepdim=True)
        for p in ent["pedidos"]:
            textos = [t[:300] for t in (p.get("textos") or [p["texto"]])]
            tx = proc(text=textos, return_tensors="pt", padding=True, truncation=True).to(dev)
            te_todos = model.get_text_features(**tx)
            te_todos = te_todos / te_todos.norm(dim=-1, keepdim=True)
            te = te_todos[:1]
            extras = {k: [] for k in range(1, len(textos))}
            scores, marcas, iqas = [], [], []
            if not p.get("marca"):
                # quadros de vídeo (milhares): decodifica em 8 threads e prepara na GPU (antes: PIL + CPU, ~50/s)
                for px in lotes_gpu(p["imagens"], dev, dt):
                    ie = model.get_image_features(pixel_values=px)
                    ie = ie / ie.norm(dim=-1, keepdim=True)
                    scores += (ie @ te.T).squeeze(-1).float().mul(100).cpu().tolist()
                    for k in extras:                                    # outros textos, mesmas imagens
                        extras[k] += (ie @ te_todos[k:k + 1].T).squeeze(-1).float().mul(100).cpu().tolist()
                    if p.get("iqa"):
                        lg = (ie @ tqe.T).float().mul(100).view(-1, 3, 2)
                        iqas += torch.softmax(lg, -1)[..., 0].mean(-1).cpu().tolist()
                out[p["id"]] = [round(s, 2) for s in scores]
                if p.get("iqa"):
                    out[p["id"] + "#iqa"] = [round(v, 3) for v in iqas]
                for k, v in extras.items():
                    out[f"{p['id']}#t{k}"] = [round(s, 2) for s in v]
                continue
            for k in range(0, len(p["imagens"]), LOTE):
                ims = []
                for f in p["imagens"][k:k + LOTE]:
                    try:
                        ims.append(Image.open(f).convert("RGB"))
                    except Exception:
                        ims.append(Image.new("RGB", (224, 224)))
                px = proc(images=ims, return_tensors="pt")["pixel_values"].to(dev, dt)
                ie = model.get_image_features(pixel_values=px)
                ie = ie / ie.norm(dim=-1, keepdim=True)
                scores += (ie @ te.T).squeeze(-1).float().mul(100).cpu().tolist()
                if p.get("marca"):
                    mm = (ie @ tme.T).float().mul(100).cpu()
                    marcas += (mm[:, 0] + 0.5 * (mm[:, 0] - mm[:, 1])).tolist()
                    if wm_model is not None:
                        xb = torch.stack([wm_tf(im) for im in ims]).to(dev)
                        wms = torch.softmax(wm_model(xb).float(), 1)[:, 0].cpu().tolist()
                        out.setdefault(p["id"] + "#wm", []).extend(round(v, 3) for v in wms)
            out[p["id"]] = [round(s, 2) for s in scores]
            if p.get("marca"):
                out[p["id"] + "#marca"] = [round(v, 2) for v in marcas]
    json.dump(out, open(sys.argv[2], "w", encoding="utf-8"))
    print(f"[clip] {sum(len(p['imagens']) for p in ent['pedidos'])} imagens em {time.time() - t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()
