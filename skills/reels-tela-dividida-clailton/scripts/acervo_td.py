"""Acervo local de B-roll (cenas de filme/série já baixadas): onde está neste PC, índice CLIP e consulta.

O acervo é uma pasta com `acervo.json` na raiz (catálogo: código, arquivo, obra, cenas com tempo e
descrição). A pasta muda de lugar em cada PC: o caminho fica em %LOCALAPPDATA%\\reels-novela\\acervo.txt
(fora da sincronia das skills). Sem esse arquivo, procura `acervo.json` nas raízes dos discos (2 níveis).

  python acervo_td.py onde                       mostra a pasta do acervo neste PC
  python acervo_td.py definir "E:\\ACERVO B-ROLLS"   grava o caminho deste PC
  python acervo_td.py indexar                    quadros 1/s + CLIP de cada vídeo novo (venv-align, GPU)
  python acervo_td.py consultar ent.json sai.json   (uso interno do buscar_td.py; venv-align)

consultar: {"pedidos": [{"id", "texto", "dur", "obra": opcional}]} ->
           {"id": [{"codigo", "t", "score"}, ...]} (melhor janela de cada vídeo, os K melhores vídeos)
"""
from __future__ import annotations

import json
import os
import string
import subprocess
import sys
import time
from pathlib import Path

LOCAL = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
CONFIG = LOCAL / "reels-novela" / "acervo.txt"
MARCA = "acervo_brolls"           # chave do acervo.json que identifica a pasta
QPS = 1.0                         # quadros por segundo do índice (o mesmo da prévia do buscar_td)
K_VIDEOS = 2                      # vídeos do acervo que viram candidatos por item


def raiz() -> Path | None:
    """Pasta do acervo neste PC (config; senão procura nas raízes dos discos e grava o achado)."""
    if CONFIG.exists():
        p = Path(CONFIG.read_text(encoding="utf-8").strip().strip('"'))
        if (p / "acervo.json").exists():
            return p
    for letra in string.ascii_uppercase[2:]:
        base = Path(f"{letra}:\\")
        if not base.exists():
            continue
        try:
            nivel1 = [base] + [d for d in base.iterdir() if d.is_dir()]
        except OSError:
            continue
        for d in nivel1:
            try:
                cands = [d] + ([x for x in d.iterdir() if x.is_dir()] if d != base else [])
            except OSError:
                continue
            for c in cands:
                j = c / "acervo.json"
                try:
                    if j.exists() and MARCA in j.read_text(encoding="utf-8")[:300]:
                        definir(c)
                        return c
                except OSError:
                    continue
    return None


def definir(p: Path) -> None:
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(str(Path(p).resolve()), encoding="utf-8")


def catalogo(r: Path | None = None) -> dict:
    r = r or raiz()
    return json.loads((r / "acervo.json").read_text(encoding="utf-8")) if r else {"videos": []}


def caminho(codigo: str, r: Path | None = None) -> Path | None:
    """Arquivo do vídeo `codigo` (ex.: SUC-01) neste PC."""
    r = r or raiz()
    if not r:
        return None
    for v in catalogo(r)["videos"]:
        if v["codigo"].lower() == codigo.lower():
            p = r / v["arquivo"]
            return p if p.exists() else None
    return None


def quadros(r: Path, v: dict) -> list[Path]:
    """Quadros 1/s (256 px) do vídeo, guardados em _catalogo/quadros/<código>/ (feitos uma vez só)."""
    d = r / "_catalogo" / "quadros" / v["codigo"]
    fr = sorted(d.glob("f_*.jpg")) if d.exists() else []
    if not fr:
        d.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-i", str(r / v["arquivo"]), "-vf", f"fps={QPS},scale=256:-2",
                        "-q:v", "4", str(d / "f_%05d.jpg")], check=False)
        fr = sorted(d.glob("f_*.jpg"))
    return fr


def _modelo():
    import torch
    from transformers import CLIPModel, CLIPProcessor
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from clip_rank import MODELO
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    dt = torch.float16 if dev == "cuda" else torch.float32
    try:
        m = CLIPModel.from_pretrained(MODELO, dtype=dt, use_safetensors=True, local_files_only=True)
    except Exception:  # noqa: BLE001
        m = CLIPModel.from_pretrained(MODELO, dtype=dt, use_safetensors=True)
    try:
        proc = CLIPProcessor.from_pretrained(MODELO, use_fast=True)
    except Exception:  # noqa: BLE001
        proc = CLIPProcessor.from_pretrained(MODELO)
    return m.to(dev).eval(), proc, dev, dt


def indexar() -> None:
    import numpy as np
    import torch
    from clip_rank import lotes_gpu
    r = raiz()
    if not r:
        sys.exit("acervo não encontrado neste PC: rode  acervo_td.py definir \"<pasta>\"")
    t0 = time.time()
    arq = r / "_catalogo" / "clip_acervo.npz"
    velho = dict(np.load(arq, allow_pickle=False)) if arq.exists() else {}
    feitos = set(velho.get("cod", np.array([], dtype=str)).tolist())
    vids = [v for v in catalogo(r)["videos"] if v["codigo"] not in feitos and (r / v["arquivo"]).exists()]
    if not vids:
        print("índice em dia")
        return
    model, _, dev, dt = _modelo()
    embs, cods, ts = [], [], []
    for v in vids:
        fr = quadros(r, v)
        with torch.no_grad():
            for px in lotes_gpu([str(f) for f in fr], dev, dt):
                ie = model.get_image_features(pixel_values=px)
                embs.append((ie / ie.norm(dim=-1, keepdim=True)).half().cpu().numpy())
        cods += [v["codigo"]] * len(fr)
        ts += [k / QPS for k in range(len(fr))]
        print(f"   {v['codigo']}: {len(fr)} quadros ({time.time() - t0:.0f}s)", flush=True)
    emb = np.concatenate([velho["emb"], *embs]) if velho else np.concatenate(embs)
    cod = np.concatenate([velho["cod"], np.array(cods)]) if velho else np.array(cods)
    t = np.concatenate([velho["t"], np.array(ts, dtype=np.float32)]) if velho else np.array(ts, dtype=np.float32)
    np.savez(arq, emb=emb, cod=cod, t=t)
    print(f"índice: {len(cod)} quadros de {len(set(cod.tolist()))} vídeos ({time.time() - t0:.0f}s)")


def consultar(ent: Path, sai: Path) -> None:
    import numpy as np
    import torch
    r = raiz()
    arq = r / "_catalogo" / "clip_acervo.npz" if r else None
    if not arq or not arq.exists():
        sai.write_text("{}", encoding="utf-8")
        return
    z = np.load(arq, allow_pickle=False)
    emb, cod, tt = z["emb"].astype(np.float32), z["cod"], z["t"]
    cat = {v["codigo"]: v for v in catalogo(r)["videos"]}
    model, proc, dev, _ = _modelo()
    out = {}
    for p in json.loads(ent.read_text(encoding="utf-8"))["pedidos"]:
        with torch.no_grad():
            tx = proc(text=[p["texto"][:300]], return_tensors="pt", padding=True, truncation=True).to(dev)
            te = model.get_text_features(**tx)
            te = (te / te.norm(dim=-1, keepdim=True)).float().cpu().numpy()[0]
        s = emb @ te * 100
        L = max(1, int(np.ceil(p.get("dur", 2.0) * QPS)))
        obra = (p.get("obra") or "").lower()
        melhores = []
        for c in dict.fromkeys(cod.tolist()):
            v = cat.get(c)
            if not v or v.get("evitar"):
                continue
            idx = np.where(cod == c)[0]
            sv = s[idx]
            if len(sv) > L:
                jan = np.convolve(sv, np.ones(L) / L, mode="valid")
                k = int(jan.argmax())
                val = float(jan[k])
            else:
                k, val = 0, float(sv.mean())
            # a obra citada na busca ("Breaking Bad ...") pesa: é a cena que a pessoa reconhece
            nomes = [v.get("obra", "").lower()] + [a.lower() for a in v.get("apelidos", [])]
            if obra and any(n and n in obra for n in nomes):
                val += 3.0
            melhores.append({"codigo": c, "t": float(tt[idx[k]]), "score": round(val, 2)})
        melhores.sort(key=lambda x: -x["score"])
        out[p["id"]] = melhores[:K_VIDEOS]
    sai.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "onde"
    if cmd == "onde":
        print(raiz() or "acervo não encontrado neste PC")
    elif cmd == "definir":
        p = Path(sys.argv[2])
        if not (p / "acervo.json").exists():
            sys.exit(f"não achei acervo.json em {p}")
        definir(p)
        print("acervo deste PC:", p)
    elif cmd == "indexar":
        indexar()
    elif cmd == "consultar":
        consultar(Path(sys.argv[2]), Path(sys.argv[3]))
