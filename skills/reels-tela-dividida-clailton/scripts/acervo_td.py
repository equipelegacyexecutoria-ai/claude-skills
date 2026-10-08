"""Acervo local de B-roll (cenas de filme/série já baixadas): onde está neste PC, índice CLIP e consulta.

O acervo é uma pasta com `acervo.json` na raiz (catálogo: código, arquivo, obra, cenas com tempo e
descrição). A pasta muda de lugar em cada PC: o caminho fica em %LOCALAPPDATA%\\reels-novela\\acervo.txt
(fora da sincronia das skills). Sem esse arquivo, procura `acervo.json` nas raízes dos discos (2 níveis).

  python acervo_td.py onde                       mostra a pasta do acervo neste PC
  python acervo_td.py definir "E:\\ACERVO B-ROLLS"   grava o caminho deste PC
  python acervo_td.py indexar                    quadros 1/s + CLIP de cada vídeo novo (venv-align, GPU)
  python acervo_td.py consultar ent.json sai.json   (uso interno do buscar_td.py; venv-align)
  python acervo_td.py novos                      vídeos da pasta que não estão no catálogo -> folhas de
                                                 cenas em _catalogo/novos/ (para catalogar; ver SKILL.md)
  python acervo_td.py catalogo                   refaz CATALOGO.md a partir do acervo.json (+ cópia na skill)

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
    vids = [v for v in catalogo(r)["videos"] if v["codigo"] not in feitos and (r / v["arquivo"]).exists()
            and Path(v["arquivo"]).suffix.lower() in (".mp4", ".mov", ".mkv", ".webm", ".m4v")]
    if not vids:
        print("índice em dia")
        return
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(6) as ex:                    # quadros antes do modelo (memória e tempo)
        todos_fr = list(ex.map(lambda v: quadros(r, v), vids))
    print(f"   quadros ok ({time.time() - t0:.0f}s)", flush=True)
    model, _, dev, dt = _modelo()
    embs, cods, ts = [], [], []
    for v, fr in zip(vids, todos_fr):
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
    recentes = usadas_recentes()
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
            if any(rc == c and abs(rt - float(tt[idx[k]])) < 8 for rc, rt in recentes):
                val -= 3.0                      # mesma cena num dos últimos reels: não repetir
            melhores.append({"codigo": c, "t": float(tt[idx[k]]), "score": round(val, 2)})
        melhores.sort(key=lambda x: -x["score"])
        out[p["id"]] = melhores[:K_VIDEOS]
    sai.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")


VIDEO = (".mp4", ".mov", ".mkv", ".webm", ".m4v")
USO = Path(__file__).resolve().parent.parent / "referencia" / "acervo_uso.tsv"   # sincroniza entre os PCs
USO_CAB = "data\treel\tcodigo\tt\titem\tfala"
RECENTES = 10                     # cena usada nos últimos N reels perde nota na consulta (não repetir)


def ler_uso() -> list[dict]:
    if not USO.exists():
        return []
    linhas = USO.read_text(encoding="utf-8").splitlines()
    cab = linhas[0].split("\t")
    return [dict(zip(cab, l.split("\t"))) for l in linhas[1:] if l.strip()]


def registrar_uso(T: Path, reel: str) -> None:
    """Cenas do acervo que entraram no reel (escolhas.json) -> referencia/acervo_uso.tsv. Refazer o mesmo
    reel (v2, v3) troca as linhas dele."""
    import datetime
    import re
    esc_p, tl_p = T / "midia" / "escolhas.json", T / "timeline.json"
    if not esc_p.exists() or not tl_p.exists():
        return
    esc = json.loads(esc_p.read_text(encoding="utf-8"))
    camadas = {c["id"]: c for c in json.loads(tl_p.read_text(encoding="utf-8"))["camadas"]}
    base = re.sub(r"\s*-\s*EDITADO.*$|_v\d+$", "", reel, flags=re.I).strip()
    novas = []
    for i, e in esc.items():
        m = re.match(r"acervo (\S+) t=(\d+)", e.get("url", ""))
        if m:
            fala = " ".join((camadas.get(i, {}).get("texto") or "").split())[:120]
            novas.append({"data": datetime.date.today().isoformat(), "reel": base, "codigo": m.group(1),
                          "t": m.group(2), "item": i, "fala": fala})
    velhas = [u for u in ler_uso() if u.get("reel") != base]
    USO.write_text(USO_CAB + "\n" + "".join("\t".join(u.get(k, "") for k in USO_CAB.split("\t")) + "\n"
                                           for u in velhas + novas), encoding="utf-8")
    if novas:
        print(f"acervo: {len(novas)} cena(s) registradas no uso ({', '.join(n['codigo'] for n in novas)})")


def usadas_recentes() -> list[tuple[str, float]]:
    uso = ler_uso()
    reels = list(dict.fromkeys(u["reel"] for u in reversed(uso)))[:RECENTES]
    return [(u["codigo"], float(u["t"] or 0)) for u in uso if u["reel"] in reels]


def tc(t) -> str:
    t = float(t or 0)
    return f"{int(t // 60)}:{int(t % 60):02d}"


def folha_cenas(src: Path, destino: Path, nome: str) -> dict:
    """Toda troca de cena do vídeo inteiro -> 1 miniatura do meio de cada plano, com o tempo (páginas de 6
    linhas). Devolve {dur, w, h, fps, planos, paginas}."""
    import re
    import shutil
    from PIL import Image, ImageDraw, ImageFont
    pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                         "stream=width,height,r_frame_rate:format=duration", "-of", "json", str(src)],
                        capture_output=True, text=True, encoding="utf-8")
    j = json.loads(pr.stdout or "{}")
    s = (j.get("streams") or [{}])[0]
    n, d = (s.get("r_frame_rate") or "0/1").split("/")
    dur = float(j.get("format", {}).get("duration") or 0)
    tmp = destino / f"_tmp_{nome}"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    fc = "[0:v]scale=-2:150,split=2[a][b];[a]select='gt(scene,0.28)',showinfo[s];[b]fps=4[t]"
    r = subprocess.run(["ffmpeg", "-v", "info", "-nostats", "-i", str(src), "-filter_complex", fc, "-map", "[s]", "-f",
                        "null", "-", "-map", "[t]", "-q:v", "5", str(tmp / "t_%06d.jpg")],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    bordas = [0.0] + [float(x) for x in re.findall(r"pts_time:([\d.]+)", r.stderr) if 0.3 < float(x) < dur - 0.3] + [dur]
    planos: list[list[float]] = []
    for a, b in zip(bordas[:-1], bordas[1:]):
        if planos and b - a < 0.4:
            planos[-1][1] = b
        else:
            planos.append([a, b])
    thumbs = sorted(tmp.glob("t_*.jpg"))
    mostrar = planos if len(planos) <= 120 else [planos[int(i * len(planos) / 120)] for i in range(120)]
    fonte = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 15)
    tiles = []
    for a, b in mostrar:
        im = Image.open(thumbs[min(len(thumbs) - 1, int((a + b) / 2 * 4))]).convert("RGB")
        dr = ImageDraw.Draw(im)
        txt = f"{int(a // 60)}:{a % 60:04.1f} ({b - a:.1f}s)"
        dr.rectangle([0, 0, dr.textlength(txt, font=fonte) + 6, 19], fill=(0, 0, 0))
        dr.text((3, 1), txt, font=fonte, fill=(255, 255, 0))
        tiles.append(im)
    tw = max(t.width for t in tiles)
    cols = max(1, 1600 // (tw + 4))
    por = cols * 6
    pags = [tiles[i:i + por] for i in range(0, len(tiles), por)]
    for p, grupo in enumerate(pags, 1):
        rows = (len(grupo) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * (tw + 4), 26 + rows * 154), (40, 40, 40))
        ImageDraw.Draw(sheet).text((4, 4), f"{nome}  {src.name[:90]}  [{tc(dur)}]  pág {p}/{len(pags)}", font=fonte,
                                   fill=(255, 255, 255))
        for k, t in enumerate(grupo):
            sheet.paste(t, ((k % cols) * (tw + 4), 26 + (k // cols) * 154))
        sheet.save(destino / f"{nome}_p{p}.jpg", quality=82)
    shutil.rmtree(tmp, ignore_errors=True)
    return {"dur": round(dur, 1), "w": s.get("width"), "h": s.get("height"), "fps": round(int(n) / max(1, int(d)), 2),
            "planos": [[round(a, 2), round(b, 2)] for a, b in planos], "paginas": len(pags)}


def novos() -> None:
    r = raiz()
    if not r:
        sys.exit("acervo não encontrado neste PC")
    conhecidos = {v["arquivo"].replace("\\", "/") for v in catalogo(r)["videos"]}
    dest = r / "_catalogo" / "novos"
    dest.mkdir(parents=True, exist_ok=True)
    achados = []
    for f in sorted(r.rglob("*")):
        rel = str(f.relative_to(r)).replace("\\", "/")
        if f.suffix.lower() in VIDEO and not rel.startswith(("_extras/", "_catalogo/")) and rel not in conhecidos:
            nome = f"N{len(achados) + 1:03d}"
            info = folha_cenas(f, dest, nome)
            achados.append({"novo": nome, "arquivo": rel, **info})
            print(f"{nome}: {rel} ({info['paginas']} pág, {len(info['planos'])} planos)")
    (dest / "novos.json").write_text(json.dumps(achados, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(achados)} vídeo(s) novo(s); folhas e novos.json em {dest}")


def catalogo_md() -> None:
    """CATALOGO.md (para ler e procurar por tema) a partir do acervo.json; cópia em referencia/ da skill."""
    r = raiz()
    vs = sorted(catalogo(r)["videos"], key=lambda v: v["arquivo"])
    L = ["# Acervo de B-roll — catálogo", "",
         f"{len(vs)} vídeos · cada cena com tempo (min:seg), o que aparece e [temas].",
         "Código no plano da tela dividida: `acervo=SUC-01 t=95` (t em segundos). Folhas de cenas: "
         "`_catalogo/folhas/<código>_p1.jpg`.",
         "Nota 1–5 = utilidade para os reels do Clailton. ⚠ = problema (marca d'água, texto em inglês, tarja...).", ""]
    atual = None
    for v in vs:
        sec = v["arquivo"].rsplit("/", 1)[0]
        if sec != atual:
            L += ["", f"## {sec}", ""]
            atual = sec
        L.append(f"### {v['codigo']} — {v['nome']}")
        obra = (f"{v['obra_pt']} ({v['obra']})" if v.get("obra") and v.get("obra_pt") and v["obra_pt"] != v["obra"]
                else (v.get("obra") or "genérico"))
        L.append(f"{obra} · {v.get('formato')} · {tc(v.get('dur'))} · {v.get('w')}x{v.get('h')} · nota {v.get('nota')}"
                 + (" · **NÃO USAR**" if v.get("evitar") else "") + f" · temas: {', '.join(v.get('temas', []))}")
        L.append(v.get("resumo", ""))
        if v.get("problemas"):
            L.append("⚠ " + "; ".join(v["problemas"]))
        for c in v.get("cenas", []):
            obs = f" ⚠ {c['obs']}" if c.get("obs") else ""
            L.append(f"- {tc(c.get('ini'))}–{tc(c.get('fim'))} {c.get('o_que_aparece', '')} "
                     f"[{', '.join(c.get('temas', []))}] ({c.get('enquadramento', '')}){obs}")
        L.append("")
    txt = "\n".join(L)
    (r / "CATALOGO.md").write_text(txt, encoding="utf-8")
    (Path(__file__).resolve().parent.parent / "referencia" / "acervo_catalogo.md").write_text(txt, encoding="utf-8")
    print(f"CATALOGO.md: {len(vs)} vídeos")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "onde"
    if cmd == "novos":
        novos()
    elif cmd == "catalogo":
        catalogo_md()
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
