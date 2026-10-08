"""Busca, baixa e ranqueia as imagens e trechos de vídeo de cada item da timeline.

  foto / ia (sem arquivo) / cartao  -> busca de imagem (Bing; DuckDuckGo de reserva), 10 baixadas,
                                       filtro de marca d'água/tamanho/duplicata, ranking CLIP + aspecto
  filme / video                     -> YouTube (yt-dlp): 3 vídeos em 360p, quadros a 2/s, CLIP acha a
                                       melhor janela da duração do item, baixa essa janela em até 1080p
  print                             -> url= : captura da página (Edge headless); senão busca de imagem
  arquivo                           -> arquivo local indicado no plano
  acervo (local, acervo_td.py)      -> filme/vídeo: as cenas do acervo do PC entram primeiro (índice CLIP,
                                       sem download); acervo=<código> no plano usa aquele vídeo
  montagens (@theclipof, @TheBeautyOf) -> filme citado na busca que tem montagem "Visuals - <obra>" ou
                                       "The Beauty Of <obra>" (referencia/montagens_youtube.tsv): entra
                                       como candidato, com prévia do vídeo inteiro
  ia com arquivo pronto             -> midia/<id>.png|jpg (gerado fora, ex.: pelo conector de imagem)
  url= em foto/filme                -> baixa direto (sem busca)

Saída (<trabalho>/midia/): cand/<id>_<k>.jpg|mp4, escolhas.json (padrão = 1º do ranking),
qa/candidatos_NN.jpg (4 candidatos por item, já recortados no layout).
Trocar a escolha: escreva <trabalho>/escolhas.txt ("b03 2" = candidato 2) e rode com --aplicar.
Refazer um item (mudou a busca no plano.txt): plano_td.py e depois buscar_td.py <T> --so b05.

Uso: python buscar_td.py <trabalho> [--so b03,b05] [--aplicar] [--n 4]
"""
from __future__ import annotations

import argparse
import html
import io
import json
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import quote_plus, urlparse

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from midia_util import (LAYOUT_WH, area_util, caixas_texto, dhash, hamming, logo_fixo, miniatura, rostos,  # noqa: E402
                        texto_pct)
import acervo_td as ACV  # noqa: E402
import reenquadrar_td as RQ  # noqa: E402
from td_comum import FPS, SKILL, carregar_json, gravar_json, ler_json, python_align, python_principal, wh_video  # noqa: E402

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/140.0.0.0 Safari/537.36")
BLOQUEADOS = ("shutterstock", "istockphoto", "gettyimages", "alamy", "dreamstime", "depositphotos", "123rf",
              "ftcdn.net", "stock.adobe", "canstockphoto", "pond5", "bigstockphoto", "vectorstock", "agefotostock",
              "superstock", "masterfile", "stockfresh", "featurepics", "colourbox", "pixtastock", "storyblocks",
              "cdndsgni", "designi.com", "pngtree", "criativodahora", "vecteezy", "canva.com/", "envato",
              "elements-cover", "motionarray", "pikbest", "lovepik", "90sheji", "ibxk.com.br/2", "wmark",
              "westend61", "imago-images", "photocase", "fotosearch", "clipdealer", "mediastorehouse", "picfair",
              "premium_photo", "plus.unsplash.com")
MARCA_DAGUA = ("premium", "/pro/")        # prévia paga com marca d'água em mosaico (ex.: Freepik premium = "Magnific")
VID_EVITA = ("reaction", "react ", "reacts", "review", "explained", "analysis", "podcast", "tutorial", "#shorts",
             "compilation", "top 10", "ranking")
N_BAIXAR = 10
QPS = 1.0                    # quadros por segundo da prévia de vídeo (CLIP acha a janela)
N_YOUTUBE, N_TIKTOK = 2, 1   # vídeos por item (menos pedidos = menos bloqueio "confirme que não é robô")
ITENS_JUNTOS = 4             # itens de vídeo processados em paralelo
HD_POR_ITEM = 3              # trechos baixados em HD por item (as 3 melhores janelas; o reenquadramento decide)
LIMITE_MARCA = 0.6           # detector da LAION (clip_rank.py): acima disso, provável marca d'água
MIN_LADO = 480


# ------------------------------------------------------------------ busca de imagem
def cliente():
    import httpx
    return httpx.Client(headers={"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"},
                        timeout=15, follow_redirects=True)


def bing(q: str, n: int = 35) -> list[dict]:
    with cliente() as c:
        r = c.get("https://www.bing.com/images/search",
                  params={"q": q, "form": "HDRSC2", "first": "1", "qft": "+filterui:imagesize-large"})
    out = []
    for m in re.findall(r'class="iusc"[^>]*\sm="([^"]+)"', r.text):
        try:
            j = json.loads(html.unescape(m))
        except ValueError:
            continue
        if j.get("murl"):
            out.append({"url": j["murl"], "pagina": j.get("purl", ""), "titulo": j.get("t", "")})
    return out[:n]


BACKENDS = ["auto", "bing", "duckduckgo"]
LIMITE_LIXO = 18.0           # melhor CLIP abaixo disso = a busca devolveu lixo -> tenta outro backend
LIMITE_FRACO = 22.0          # abaixo disso o item vai para a lista "revisar"


def ddg(q: str, n: int = 30, backend: str = "auto") -> list[dict]:
    """Busca de imagem pelo pacote ddgs (DuckDuckGo/Bing por trás). O Bing raspado direto devolve lixo
    depois de algumas buscas ('balde furado' -> jogador Balde do Barcelona); o ddgs às vezes também
    (roupa de praia para 'aperto de mão'): o CLIP acusa e a busca troca de backend."""
    for tentativa in range(3):
        try:
            from ddgs import DDGS
            r = DDGS().images(q, max_results=n, size="Large", backend=backend)
            return [{"url": x["image"], "pagina": x.get("url", ""), "titulo": x.get("title", ""),
                     "w": int(x.get("width") or 0), "h": int(x.get("height") or 0)} for x in r]
        except Exception as e:  # noqa: BLE001
            if tentativa == 2:
                print(f"   ddg falhou ({q[:40]}): {e!r}"[:180])
            time.sleep(1.5 * (tentativa + 1))
    return []


def zip_longest_lista(listas: list[list]) -> list[tuple]:
    from itertools import zip_longest
    return list(zip_longest(*listas))


def bloqueado(url: str) -> bool:
    u = url.lower()
    if any(b in u for b in BLOQUEADOS):
        return True
    return "freepik" in u and any(m in u for m in MARCA_DAGUA)


def xadrez(img: Image.Image) -> bool:
    """PNG 'transparente' falso: o quadriculado cinza/branco veio gravado na imagem."""
    g = np.asarray(img.convert("L"), dtype=np.int16)
    s = max(32, min(g.shape) // 8)
    achados = 0
    for bloco in (g[:s, :s], g[:s, -s:], g[-s:, :s], g[-s:, -s:]):
        lo, hi = np.percentile(bloco, 5), np.percentile(bloco, 95)
        if hi - lo < 12 or hi - lo > 75 or lo < 150:
            continue
        claro = bloco > (lo + hi) / 2                     # dois tons: quadrado claro x quadrado cinza
        m1, m2 = bloco[claro], bloco[~claro]
        if min(m1.size, m2.size) < 0.2 * bloco.size or m1.std() > 8 or m2.std() > 8:
            continue
        trocas = (np.diff(claro.astype(np.int8), axis=1) != 0).mean()
        if 0.008 < trocas < 0.3:
            achados += 1
    return achados >= 2


def baixar_imagem(res: dict, destino: Path) -> dict | None:
    import httpx
    try:
        r = httpx.get(res["url"], headers={"User-Agent": UA, "Referer": res.get("pagina") or "https://www.bing.com/"},
                      timeout=12, follow_redirects=True)
        if r.status_code != 200 or len(r.content) < 8000 or len(r.content) > 25_000_000:
            return None
        img = Image.open(io.BytesIO(r.content))
        img.load()
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGBA")
            fundo = Image.new("RGB", img.size, (255, 255, 255))
            fundo.paste(img, mask=img.split()[-1])
            img = fundo
        img = img.convert("RGB")
        if min(img.size) < MIN_LADO or max(img.size) / min(img.size) > 3.2 or xadrez(img):
            return None
        if max(img.size) > 3000:
            img.thumbnail((3000, 3000))
        img.save(destino, "JPEG", quality=92)
        return {**res, "arquivo": str(destino), "wh": list(img.size), "hash": dhash(img)}
    except Exception:  # noqa: BLE001
        return None


EDGE = [p for p in (Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
                    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
                    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")) if p.exists()]


def captura_pagina(url: str, destino: Path) -> dict | None:
    """Print do topo da página (manchete) com o navegador headless: largura de celular, 4:5, 2x."""
    if not EDGE:
        return None
    perfil = destino.parent / "_perfil_headless"
    subprocess.run([str(EDGE[0]), "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
                    f"--user-data-dir={perfil}", "--window-size=540,675", "--force-device-scale-factor=2",
                    "--virtual-time-budget=9000", f"--screenshot={destino}", url], capture_output=True, timeout=60)
    shutil.rmtree(perfil, ignore_errors=True)
    if not destino.exists():
        return None
    img = Image.open(destino).convert("RGB")
    img.save(destino.with_suffix(".jpg"), quality=92)
    return {"url": url, "pagina": url, "titulo": "print", "arquivo": str(destino.with_suffix(".jpg")),
            "wh": list(img.size), "hash": dhash(img)}


def candidatos_imagem(it: dict, pasta: Path, tentativa: int = 0) -> list[dict]:
    q = it["busca"] or it.get("en") or ""
    if it["tipo"] == "ia" and "ilustra" not in q.lower():
        q += " ilustração"
    if it["tipo"] == "print" and it.get("url") and not re.search(r"\.(jpe?g|png|webp)(\?|$)", it["url"], re.I):
        c = captura_pagina(it["url"], pasta / f"{it['id']}_00.png")
        return [{**c, "midia": "imagem"}] if c else []
    if it.get("url"):
        res = [{"url": it["url"], "pagina": "", "titulo": "url do plano"}]
    else:
        # busca em português e em inglês (a descrição do ranking) e intercala: mais variedade para o CLIP
        bk = BACKENDS[tentativa % len(BACKENDS)]
        listas = [ddg(q, 40, bk)]
        en = (it.get("en") or "").strip()
        if en and en.lower() != q.lower():
            listas.append(ddg(en, 40, bk))
        res = [x for par in zip_longest_lista(listas) for x in par if x]
        if len(res) < 8:
            res += bing(q)
    vistos, filtrados = set(), []
    for r in res:
        if bloqueado(r["url"]) or r["url"] in vistos:
            continue
        if r.get("w") and r.get("h") and min(r["w"], r["h"]) < MIN_LADO:
            continue
        vistos.add(r["url"])
        filtrados.append(r)
    with ThreadPoolExecutor(12) as ex:
        baixados = list(ex.map(lambda kr: baixar_imagem(kr[1], pasta / f"{it['id']}_{tentativa}{kr[0]:02d}.jpg"),
                               enumerate(filtrados[:N_BAIXAR + 6])))
    out, hashes = [], []
    for b in baixados:
        if not b or any(hamming(b["hash"], h) <= 6 for h in hashes):
            continue
        hashes.append(b["hash"])
        out.append({**b, "midia": "imagem"})
        if len(out) >= N_BAIXAR:
            break
    return out


# ------------------------------------------------------------------ vídeo (YouTube)
def ytdlp(args: list[str], timeout: int = 180) -> subprocess.CompletedProcess:
    # TikTok/Instagram bloqueiam pedido "de robô": --impersonate chrome (pacote curl_cffi) resolve
    imp = ["--impersonate", "chrome"] if args and "youtube.com" not in args[-1] and "ytsearch" not in args[-1] else []
    return subprocess.run([python_principal(), "-m", "yt_dlp", "--js-runtimes", "node", "--no-warnings",
                           "--no-playlist", "--no-part"] + imp + args, capture_output=True, text=True, timeout=timeout,
                          encoding="utf-8", errors="replace")


def buscar_tiktok(q: str, n: int = 2) -> list[dict]:
    """Vídeo do TikTok (cena de filme/série já na vertical, muitas vezes da conta oficial) pela busca
    de texto do DuckDuckGo; baixado inteiro pelo yt-dlp."""
    try:
        from ddgs import DDGS
        res = DDGS().text(f"tiktok {q}", max_results=15)
    except Exception:  # noqa: BLE001
        return []
    out = []
    for r in res:
        u = r.get("href", "")
        m = re.search(r"tiktok\.com/@[\w.\-]+/video/(\d+)", u)
        if m and all(o["url_externa"] != u for o in out):
            out.append({"id": "tt" + m.group(1), "duracao": 0, "titulo": (r.get("title") or "")[:80], "bonus": 1,
                        "url_externa": u})
        if len(out) >= n:
            break
    return out


CANAIS_OFICIAIS = ("movieclips", "rotten tomatoes", "hbo", "netflix", "warner bros", "universal pictures",
                   "paramount", "sony pictures", "disney", "pixar", "20th century", "lionsgate", "a24", "amazon mgm",
                   "prime video", "focus features", "mgm", "fox", "nbc", "amc", "the simpsons", "adult swim",
                   "cartoon network", "fandango", "scene city", "filmisnow", "moviefone")


def buscar_youtube(q: str, n: int = 10) -> list[dict]:
    r = ytdlp(["--flat-playlist", "--print", "%(id)s|%(duration)s|%(channel)s|%(title)s", f"ytsearch{n}:{q}"], timeout=60)
    out = []
    for ln in r.stdout.splitlines():
        p = ln.split("|", 3)
        if len(p) < 4:
            continue
        try:
            d = float(p[1])
        except ValueError:
            continue
        t, canal = p[3].lower(), p[2].lower()
        if not (4 <= d <= 900) or any(e in t for e in VID_EVITA):
            continue
        # trecho oficial (Movieclips, estúdio, streaming) primeiro: cena limpa, sem texto de fã, boa resolução
        bonus = ((2 if any(c in canal for c in CANAIS_OFICIAIS) else 0)
                 + (1 if any(k in t for k in ("scene", "cena", "clip", "stock", "footage", "4k", "hd")) else 0))
        out.append({"id": p[0], "duracao": d, "titulo": p[3], "canal": p[2], "bonus": bonus})
    out.sort(key=lambda x: -x["bonus"])            # estável: mantém a ordem do YouTube dentro do grupo
    return out


def montagens() -> list[tuple[str, str, str]]:
    """(obra, id, título) das montagens só de imagem dos canais @theclipof e @TheBeautyOf."""
    arq = SKILL / "referencia" / "montagens_youtube.tsv"
    if not arq.exists():
        return []
    out = []
    for ln in arq.read_text(encoding="utf-8").splitlines()[1:]:
        p = ln.split("\t")
        if len(p) >= 6 and len(p[1]) >= 4 and "teaser" not in p[5].lower():
            out.append((p[1], p[2], p[5]))
    return out


def montagem_da_busca(q: str) -> dict | None:
    """Montagem do filme/série que a busca cita (a de nome mais longo que aparece na busca)."""
    ql = f" {re.sub(r'[^a-z0-9]+', ' ', q.lower())} "
    achados = [(obra, i, t) for obra, i, t in montagens()
               if f" {re.sub(r'[^a-z0-9]+', ' ', obra.lower()).strip()} " in ql]
    if not achados:
        return None
    obra, i, t = max(achados, key=lambda x: len(x[0]))
    return {"id": i, "duracao": 0, "titulo": t, "canal": "montagem", "bonus": 1, "inteiro": True}


def baixar_preview(v: dict, pasta: Path) -> dict | None:
    """YouTube: 360p dos primeiros 4 min (só para achar a janela). Outro site (TikTok, Instagram,
    Pinterest, X, Vimeo...): baixa o vídeo inteiro em até 1080p, que serve de prévia E de fonte.
    Acervo local: o próprio arquivo é a fonte; os quadros 1/s já ficam no acervo (_catalogo/quadros)."""
    if v.get("local"):
        r = ACV.raiz()
        cat = {x["codigo"]: x for x in ACV.catalogo(r)["videos"]} if r else {}
        fr = ACV.quadros(r, cat[v["codigo"]]) if v.get("codigo") in cat else []
        return {**v, "preview": v["local"], "quadros": [str(f) for f in fr]} if fr else None
    dest = pasta / f"prev_{v['id']}.mp4"
    if not dest.exists():
        if v.get("url_externa"):
            r = ytdlp(["-f", "bv*[height<=1080]+ba/b[height<=1080]/bv*/b", "--remux-video", "mp4", "-o", str(dest),
                       v["url_externa"]], timeout=300)
        else:                                    # montagem (vídeo inteiro) ou os primeiros 3 min
            r = ytdlp(["-f", "bv*[height<=360][ext=mp4]/bv*[height<=360]/b[height<=360]", "--download-sections",
                       "*0-900" if v.get("inteiro") else "*0-180", "-o", str(dest),
                       f"https://www.youtube.com/watch?v={v['id']}"], timeout=300 if v.get("inteiro") else 150)
        if not dest.exists():
            alt = list(pasta.glob(f"prev_{v['id']}.*"))
            if not alt:
                print(f"   preview {v['id']} falhou: {r.stderr[-160:]}")
                return None
            dest = alt[0]
    qd = pasta / f"q_{v['id']}"
    qd.mkdir(exist_ok=True)
    if not any(qd.iterdir()):
        subprocess.run(["ffmpeg", "-v", "error", "-t", "900" if v.get("inteiro") else "180", "-i", str(dest),
                        "-vf", f"fps={QPS},scale=256:-2", "-q:v", "4",
                        str(qd / "f_%05d.jpg")], check=False)
    fr = sorted(qd.glob("f_*.jpg"))
    return {**v, "preview": str(dest), "quadros": [str(f) for f in fr]} if fr else None


def quadros_video(arq: Path, n: int = 3, lado: int = 1280) -> list[np.ndarray]:
    """n quadros RGB espalhados pelo trecho (começo, meio, fim), lado maior até `lado` px."""
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                str(arq)], capture_output=True, text=True).stdout.strip() or 0)
    out = []
    for k in range(n):
        t = max(0.0, dur * (0.1 + 0.8 * k / max(1, n - 1)))
        r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(arq), "-frames:v", "1", "-vf",
                            f"scale='min({lado},iw)':-2", "-f", "image2pipe", "-c:v", "png", "-"], capture_output=True)
        if r.stdout:
            out.append(np.asarray(Image.open(io.BytesIO(r.stdout)).convert("RGB")))
    return out


def baixar_trecho(vid: str, t0: float, t1: float, dest: Path, local: str | None = None) -> bool:
    if local:                                            # vídeo de outro site já baixado inteiro: corta aqui
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.3f}", "-i", local, "-t", f"{t1 - t0:.3f}", "-an",
                        "-c:v", "libx264", "-crf", "12", "-preset", "fast", "-pix_fmt", "yuv420p", str(dest)], check=False)
        return dest.exists()
    r = ytdlp(["-f", "bv*[height<=1080][vcodec^=avc1]/bv*[height<=1080][ext=mp4]/bv*[height<=1080]/b",
               "--download-sections", f"*{t0:.2f}-{t1:.2f}", "--force-keyframes-at-cuts",
               "--remux-video", "mp4", "-o", str(dest), f"https://www.youtube.com/watch?v={vid}"], timeout=240)
    if not dest.exists():
        alt = [p for p in dest.parent.glob(dest.stem + ".*") if p.suffix in (".mp4", ".webm", ".mkv")]
        if alt:
            alt[0].rename(dest.with_suffix(alt[0].suffix))
            return True
        print(f"   trecho {vid} falhou: {r.stderr[-200:]}")
        return False
    return True


def cortes_preview(quadros: list[str]) -> np.ndarray:
    """1 onde o quadro k é de outra cena que o k-1 (para a janela não pegar corte de cena)."""
    pequenos = [np.asarray(Image.open(q).convert("L").resize((32, 18)), dtype=np.float32) for q in quadros]
    d = [0.0] + [float(np.abs(a - b).mean()) for a, b in zip(pequenos[1:], pequenos[:-1])]
    d = np.array(d)
    return (d > max(18.0, 3 * np.median(d) + 6)).astype(np.float32)


def melhor_janela(scores: list[float], cortes: np.ndarray, dur: float, fps_q: float = 2.0,
                  quadros: list[str] | None = None, layout: str = "cheia") -> tuple[int, float]:
    """Janela da duração do item com o maior CLIP médio, sem corte de cena. Com os quadros, confere
    texto queimado (legenda, crédito, legenda de TikTok) nas 6 melhores janelas e desconta."""
    L = max(1, int(np.ceil(dur * fps_q)))
    s = np.array(scores)
    if len(s) <= L:
        return 0, float(s.mean())
    vals = np.array([s[k:k + L].mean() - 4.0 * cortes[k + 1:k + L].sum() for k in range(0, len(s) - L + 1)])
    if not quadros:
        k = int(vals.argmax())
        return k, float(vals[k])
    cands = []
    for k in np.argsort(-vals):                        # 6 melhores sem sobreposição
        if all(abs(int(k) - c) >= L for c in cands):
            cands.append(int(k))
        if len(cands) >= 6:
            break
    melhor, k_best = -1e9, cands[0]
    for k in cands:
        amostra = [quadros[min(len(quadros) - 1, k + j)] for j in (0, L // 2, max(0, L - 1))]
        txt = sum(texto_pct(q, layout) for q in amostra) / len(amostra)
        v = float(vals[k]) - min(12.0, 3.0 * max(0.0, txt - 0.8))
        if v > melhor:
            melhor, k_best = v, k
        if txt <= 0.8 and k == cands[0]:
            break                                       # a melhor já está limpa
    return k_best, float(vals[k_best])


# ------------------------------------------------------------------ CLIP
def clip(pedidos: list[dict], T: Path) -> dict:
    if not pedidos:
        return {}
    ent, sai = T / "midia" / "clip_in.json", T / "midia" / "clip_out.json"
    ent.write_text(json.dumps({"pedidos": pedidos}, ensure_ascii=False), encoding="utf-8")
    subprocess.run([python_align(), str(SKILL / "scripts" / "clip_rank.py"), str(ent), str(sai)], check=True,
                   env={**__import__("os").environ, "PYTHONUTF8": "1", "HF_HUB_OFFLINE": "1"})
    return json.loads(sai.read_text(encoding="utf-8"))


def pontuar(cs: list[dict], sc: dict, it: dict) -> None:
    """Relevância (CLIP) + encaixe no layout - marca d'água. Marca = detector da LAION (wm) e, como
    reforço, o 'cara de banco' do CLIP só quando destoa dos outros candidatos do mesmo item (foto de
    banco limpa também pontua alto, então o valor absoluto não serve)."""
    marcas = sc.get(it["id"] + "#marca", [0.0] * len(cs))
    wms = sc.get(it["id"] + "#wm", [0.0] * len(cs))
    med = float(np.median(marcas)) if marcas else 0.0
    for c, s, mk, wm in zip(cs, sc.get(it["id"], []), marcas, wms):
        c["clip"] = s
        c["wm"] = wm
        destoa = mk - med
        c["marca"] = round(wm, 2)
        c["marca_flag"] = bool(wm >= LIMITE_MARCA or (wm >= 0.4 and destoa >= 1.5))
        c["thumb"] = c["arquivo"]
        c["texto"] = 0.0 if it["layout"] == "cartao" or it["tipo"] == "print" else texto_pct(c["arquivo"], it["layout"])
        c["score"] = (s + prior(c, it["layout"]) - 8.0 * max(0.0, wm - 0.35) - 1.5 * max(0.0, destoa - 1.5)
                      - min(12.0, 3.0 * max(0.0, c["texto"] - 0.8)))


def aspecto_alvo(layout: str) -> float:
    return {"cheia": 9 / 16, "topo": 1080 / 768, "dividida": 1080 / 768, "cartao": 1.4}.get(layout, 9 / 16)


def prior(c: dict, layout: str) -> float:
    w, h = c["wh"]
    ri, rt = w / h, aspecto_alvo(layout)
    fit = min(ri / rt, rt / ri)
    if layout == "cartao":
        fit = 1.0 if 0.6 <= ri <= 2.2 else 0.5
    lado = h if layout == "cheia" else w
    res = min(1.0, lado / 1080)
    pena = 3.0 if "ytimg.com" in c.get("url", "") else 0.0      # miniatura do YouTube: texto e cara de youtuber
    return 3.0 * fit + 2.0 * res - pena


# ------------------------------------------------------------------ folha de candidatos
def folha(itens: list[dict], cands: dict, T: Path, n_mostra: int) -> list[Path]:
    tw, th, lab = 150, 267, 34
    por_folha = 12
    pastas = T / "qa"
    pastas.mkdir(exist_ok=True)
    try:
        f1 = ImageFont.truetype("arialbd.ttf", 15)
        f2 = ImageFont.truetype("arial.ttf", 12)
    except OSError:
        f1 = f2 = ImageFont.load_default()
    saidas = []
    for fi in range(0, len(itens), por_folha):
        grupo = itens[fi:fi + por_folha]
        bw = tw * n_mostra + 8
        cols = 2
        rows = (len(grupo) + 1) // 2
        sheet = Image.new("RGB", (cols * bw + 8, rows * (th + lab + 22) + 8), (25, 25, 25))
        d = ImageDraw.Draw(sheet)
        for gi, it in enumerate(grupo):
            r, c = divmod(gi, cols)
            x0, y0 = 8 + c * bw, 8 + r * (th + lab + 22)
            d.text((x0, y0), f"{it['id']} [{it['layout']}] {(it['f1'] - it['f0']) / FPS:.1f}s", fill=(255, 220, 0), font=f1)
            d.text((x0, y0 + 17), it["texto"][:62], fill=(230, 230, 230), font=f2)
            for k, cd in enumerate(cands.get(it["id"], [])[:n_mostra]):
                try:
                    fc = (cd.get("focos") or {}).get(RQ.aspecto_do_layout(it["layout"])) or cd.get("foco")
                    th_img = miniatura(Path(cd["thumb"]), it["layout"], tw - 4, th, cd.get("rostos"), fc)
                except Exception:  # noqa: BLE001
                    continue
                sheet.paste(th_img, (x0 + k * tw, y0 + lab))
                tag = (f"{k} {cd['score']:.0f}" + (" VID" if cd["midia"] == "video" else "")
                       + (" MARCA?" if cd.get("marca_flag") else "") + (" TEXTO" if cd.get("texto", 0) > 1.5 else "")
                       + (" LOGO?" if cd.get("logo") else "")
                       + ((" LARGA" + ("→div" if cd.get("faixa_ok") else "")) if cd.get("larga") and it["layout"] == "cheia" else "")
                       + (" ESCURO" if cd.get("escuro") else "") + (" BAIXA" if cd.get("baixa") else "")
                       + (" PISCA" if cd.get("pisca") else ""))
                alerta = any(x in tag for x in ("MARCA", "TEXTO", "LOGO", "LARGA", "ESCURO", "BAIXA", "PISCA"))
                d.rectangle([x0 + k * tw, y0 + lab, x0 + k * tw + (tw - 6 if alerta else 62), y0 + lab + 18],
                            fill=(160, 0, 0) if alerta else (0, 0, 0))
                d.text((x0 + k * tw + 3, y0 + lab + 2), tag, fill=(255, 255, 255), font=f2)
                dom = urlparse(cd.get("url") or cd.get("pagina") or "").netloc.replace("www.", "")[:22]
                d.text((x0 + k * tw, y0 + lab + th + 2), dom, fill=(160, 160, 160), font=f2)
        p = pastas / f"candidatos_{fi // por_folha + 1:02d}.jpg"
        sheet.save(p, quality=85)
        saidas.append(p)
    return saidas


# ------------------------------------------------------------------ principal
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("trabalho")
    ap.add_argument("--so", help="ids separados por vírgula")
    ap.add_argument("--aplicar", action="store_true", help="só aplica escolhas.txt")
    ap.add_argument("--n", type=int, default=4, help="candidatos por item na folha")
    a = ap.parse_args()
    T = Path(a.trabalho).resolve()
    tl = ler_json(T / "timeline.json")
    pasta = T / "midia" / "cand"
    pasta.mkdir(parents=True, exist_ok=True)
    esc_p = T / "midia" / "escolhas.json"
    esc = carregar_json(esc_p, {})
    cand_p = T / "midia" / "candidatos.json"
    todos = carregar_json(cand_p, {})
    itens = [c for c in tl["camadas"] if c["tipo"] != "igual"]
    so = set(a.so.split(",")) if a.so else None
    t0 = time.time()

    if not a.aplicar:
        fazer = [it for it in itens if (so is None or it["id"] in so)]
        if so is None:
            fazer = [it for it in fazer if it["id"] not in esc]         # retoma de onde parou
        for it in fazer:                                                 # refazer: esquece a escolha antiga
            esc.pop(it["id"], None)
            todos.pop(it["id"], None)
        et = T / "escolhas.txt"                                          # e a escolha manual (o índice muda)
        if et.exists() and fazer:
            ids = {it["id"] for it in fazer}
            linhas = et.read_text(encoding="utf-8").splitlines()
            et.write_text("\n".join(l for l in linhas if l.split()[:1] and l.split()[0] not in ids) + "\n", encoding="utf-8")
        img_itens = [it for it in fazer if it["tipo"] in ("foto", "ia", "print") and not arquivo_pronto(it, T)]
        vid_itens = [it for it in fazer if it["tipo"] in ("filme", "video")]
        for it in fazer:
            pronto = arquivo_pronto(it, T)
            if pronto:
                todos[it["id"]] = [{"arquivo": str(pronto), "thumb": str(pronto), "midia": midia_de(pronto),
                                    "score": 0.0, "url": "arquivo local", "wh": list(Image.open(pronto).size)
                                    if midia_de(pronto) == "imagem" else [0, 0]}]
        print(f"busca: {len(img_itens)} de imagem, {len(vid_itens)} de vídeo", flush=True)
        # imagens: busca + download em paralelo por item
        with ThreadPoolExecutor(4) as ex:
            res_img = dict(zip([it["id"] for it in img_itens], ex.map(lambda it: candidatos_imagem(it, pasta), img_itens)))
        print(f"   imagens baixadas: {sum(len(v) for v in res_img.values())} ({time.time() - t0:.0f}s)", flush=True)
        # vídeos: busca + previews
        # acervo local: as cenas já baixadas entram primeiro (índice CLIP pronto, sem download)
        acv_raiz = ACV.raiz() if vid_itens else None
        acv_cand: dict[str, list] = {}
        if acv_raiz and (acv_raiz / "_catalogo" / "clip_acervo.npz").exists():
            livres = [it for it in vid_itens if not it.get("url") and not it.get("acervo")]
            if livres:
                ent, sai = T / "midia" / "acervo_in.json", T / "midia" / "acervo_out.json"
                ent.write_text(json.dumps({"pedidos": [{"id": it["id"], "texto": it.get("en") or it["busca"],
                                                        "obra": it["busca"], "dur": (it["f1"] - it["f0"]) / FPS}
                                                       for it in livres]}, ensure_ascii=False), encoding="utf-8")
                subprocess.run([python_align(), str(SKILL / "scripts" / "acervo_td.py"), "consultar", str(ent), str(sai)],
                               check=False, env={**__import__("os").environ, "PYTHONUTF8": "1", "HF_HUB_OFFLINE": "1"})
                acv_cand = json.loads(sai.read_text(encoding="utf-8")) if sai.exists() else {}
        elif vid_itens:
            print("   acervo local não encontrado/indexado neste PC: só busca online (acervo_td.py onde)")

        def do_acervo(codigo: str) -> dict | None:
            loc = ACV.caminho(codigo, acv_raiz) if acv_raiz else None
            if not loc:
                print(f"   AVISO: acervo {codigo} não encontrado neste PC")
                return None
            return {"id": f"acv_{codigo}", "duracao": 0, "titulo": f"acervo {codigo}", "bonus": 0,
                    "local": str(loc), "codigo": codigo}

        def previas(it: dict) -> tuple[str, list]:
            if it.get("acervo") and do_acervo(it["acervo"]):
                lista = [do_acervo(it["acervo"])]
            elif it.get("url"):
                vid = re.search(r"(?:v=|youtu\.be/|shorts/)([\w-]{11})", it["url"])
                if vid:
                    lista = [{"id": vid.group(1), "duracao": 0, "titulo": "url do plano", "bonus": 0}]
                else:                                    # TikTok, Instagram, Pinterest, X, Vimeo...
                    import hashlib
                    lista = [{"id": "x" + hashlib.md5(it["url"].encode()).hexdigest()[:10], "duracao": 0,
                              "titulo": "url do plano", "bonus": 0, "url_externa": it["url"]}]
            else:
                q = it["busca"] or it.get("en") or ""
                lista = buscar_youtube(q)[:N_YOUTUBE] + (buscar_tiktok(q, N_TIKTOK) if it["tipo"] == "filme" else [])
                mont = montagem_da_busca(q) if it["tipo"] == "filme" else None
                if mont and all(v["id"] != mont["id"] for v in lista):
                    lista.append(mont)
                lista = [x for x in (do_acervo(c["codigo"]) for c in acv_cand.get(it["id"], [])) if x] + lista
            with ThreadPoolExecutor(4) as ex:
                return it["id"], [p for p in ex.map(lambda v: baixar_preview(v, pasta), lista) if p]

        with ThreadPoolExecutor(ITENS_JUNTOS) as ex:
            res_vid = dict(ex.map(previas, vid_itens))
        print(f"   previews de vídeo: {sum(len(v) for v in res_vid.values())} ({time.time() - t0:.0f}s)", flush=True)
        # ranking CLIP (uma chamada só)
        pedidos = []
        for it in img_itens:
            if res_img.get(it["id"]):
                pedidos.append({"id": it["id"], "texto": it.get("en") or it["busca"], "marca": True,
                                "imagens": [c["arquivo"] for c in res_img[it["id"]]]})
        for it in vid_itens:
            for k, p in enumerate(res_vid.get(it["id"], [])):
                pedidos.append({"id": f"{it['id']}#{k}", "texto": it.get("en") or it["busca"], "imagens": p["quadros"]})
        sc = clip(pedidos, T)
        print(f"   CLIP ok ({time.time() - t0:.0f}s)", flush=True)
        for it in img_itens:
            pontuar(res_img.get(it["id"], []), sc, it)
        # busca que voltou lixo (melhor CLIP < LIMITE_LIXO): outra fonte, até 2 vezes
        for tentativa in (1, 2):
            lixo = [it for it in img_itens if not it.get("url")
                    and max((c.get("clip", 0) for c in res_img.get(it["id"], [])), default=0) < LIMITE_LIXO]
            if not lixo:
                break
            print(f"   busca fraca em {', '.join(i['id'] for i in lixo)}: tentando {BACKENDS[tentativa]}", flush=True)
            with ThreadPoolExecutor(4) as ex:
                novos = dict(zip([i["id"] for i in lixo], ex.map(lambda i: candidatos_imagem(i, pasta, tentativa), lixo)))
            sc2 = clip([{"id": k, "texto": next(i for i in lixo if i["id"] == k).get("en") or
                         next(i for i in lixo if i["id"] == k)["busca"], "marca": True,
                         "imagens": [c["arquivo"] for c in v]} for k, v in novos.items() if v], T)
            for i in lixo:
                pontuar(novos.get(i["id"], []), sc2, i)
                res_img[i["id"]] = res_img.get(i["id"], []) + novos.get(i["id"], [])
        for it in img_itens:
            cs = res_img.get(it["id"], [])
            cs.sort(key=lambda c: -c.get("score", 0))
            for c in cs[:a.n]:
                try:
                    c["rostos"] = rostos(Image.open(c["arquivo"]))
                except Exception:  # noqa: BLE001
                    c["rostos"] = []
            todos[it["id"]] = cs
        # vídeos: melhor janela de cada preview -> trecho em HD
        usos: dict[str, list[float]] = {}                  # duração de cada uso da mídia (item + repetições)
        for c in tl["camadas"]:
            alvo = c["igual"] if c["tipo"] == "igual" else c["id"]
            usos.setdefault(alvo, []).append(round((c["f1"] - c["f0"]) / FPS, 3))
        trabalhos = []
        for it in vid_itens:
            dur = max(usos.get(it["id"], [(it["f1"] - it["f0"]) / FPS])) + 0.4
            for k, p in enumerate(res_vid.get(it["id"], [])):
                s = sc.get(f"{it['id']}#{k}", [])
                if not s:
                    continue
                if it.get("t") is not None and k == 0 and (not p.get("local") or it.get("acervo")):
                    ini_q, val = int(it["t"] * QPS), float(np.mean(s))
                else:
                    ini_q, val = melhor_janela(s, cortes_preview(p["quadros"]), dur, fps_q=QPS, quadros=p["quadros"],
                                               layout=it["layout"])
                t_ini = ini_q / QPS
                trabalhos.append((it, k, p, t_ini, t_ini + dur + 0.3, val))
        # trecho em HD só das 2 melhores janelas de cada item (antes: todas; o download era 1/4 do tempo)
        melhores = []
        for it in vid_itens:
            dele = sorted([t for t in trabalhos if t[0]["id"] == it["id"]], key=lambda t: -t[5])
            melhores += dele[:HD_POR_ITEM]
        trabalhos = melhores
        def baixa(tr):
            it, k, p, ti, tf, val = tr
            dest = pasta / f"{it['id']}_v{k}.mp4"
            for velho in pasta.glob(f"{it['id']}_v{k}.*"):    # trecho de busca anterior: se o download falhar,
                velho.unlink(missing_ok=True)                   # NÃO pode passar como novo (b08 do v3 congelou)
            t_ini = max(0.0, ti - RQ.MARGEM)                  # margem: a entrada certa pode estar antes/depois
            ok = baixar_trecho(p["id"], t_ini, tf + RQ.MARGEM, dest,
                               p["preview"] if (p.get("url_externa") or p.get("local")) else None)
            achado = next((q for q in pasta.glob(f"{it['id']}_v{k}.*") if q.suffix in (".mp4", ".webm", ".mkv")), None)
            if not ok or not achado:
                return None
            mid = p["quadros"][min(len(p["quadros"]) - 1, int((ti + (tf - ti) / 2) * QPS))]
            # legenda queimada / texto de TikTok na janela: média de 3 quadros
            amostra = [p["quadros"][min(len(p["quadros"]) - 1, int(t * QPS))] for t in (ti + 0.2, (ti + tf) / 2, tf - 0.3)]
            txt = sum(texto_pct(q, it["layout"]) for q in amostra) / len(amostra)
            try:
                vw, vh = wh_video(achado)
                _, _, aw, ah = area_util(str(achado))
            except Exception:  # noqa: BLE001
                vw = vh = aw = ah = 0
            # resolução pelo quanto o recorte do layout é ampliado: tela cheia de 1080p = 1,8x (+2);
            # 480p = 4x (-1); 272p = 7x (-6: borrado, "não dá para ver nada"). Na faixa de cima 480p basta.
            ow, oh = LAYOUT_WH.get(it["layout"], LAYOUT_WH["cheia"])
            escala = (oh / (ah if aw / max(ah, 1) > ow / oh else aw * oh / ow)) if aw else 9.0
            bonus_res = max(-8.0, 2.0 - 1.6 * max(0.0, escala - 2.0))
            # logo de canal/streaming fixo no canto (hulu, Netflix...) e texto queimado grande (título de edição
            # de fã): no trecho em HD, que na prévia de 256 px o texto estilizado escapa
            try:
                qv = quadros_video(achado, 3)
                logo = logo_fixo(qv, it["layout"])
                txt = max(txt, 100 * float(np.mean([sum(b[2] * b[3] for b in caixas_texto(q, it["layout"])) for q in qv])))
            except Exception:  # noqa: BLE001
                logo = False
            return it["id"], {"arquivo": str(achado), "thumb": mid, "midia": "video", "clip": round(val, 2),
                              "score": round(val + bonus_res - min(12.0, 3.0 * max(0.0, txt - 0.8)) - (4.0 if logo else 0.0), 2),
                              "texto": round(txt, 2), "logo": logo, "escala": round(escala, 2), "baixa": escala > 3.5,
                              "url": p.get("url_externa") or (f"acervo {p['codigo']} t={int(ti)}" if p.get("local")
                                                              else f"https://youtu.be/{p['id']}?t={int(ti)}"),
                              "titulo": p["titulo"], "t_video": ti, "wh": [vw, vh], "entrada0": round(ti - t_ini, 3),
                              "duracoes": usos.get(it["id"], [round(tf - ti - 0.7, 3)])}
        with ThreadPoolExecutor(6) as ex:
            for r in ex.map(baixa, trabalhos):
                if r:
                    todos.setdefault(r[0], [])
                    todos[r[0]] = [c for c in todos[r[0]] if c.get("arquivo") != r[1]["arquivo"]] + [r[1]]
        print(f"   trechos HD ok ({time.time() - t0:.0f}s)", flush=True)
        # reenquadramento: recorte por plano (vertical e faixa) guiado pelo que APARECE, entrada sem corte
        # de cena colado, nota refeita pelo recorte (ação + identidade + qualidade + rosto inteiro)
        alvos = [(it, c) for it in vid_itens for c in todos.get(it["id"], [])
                 if c["midia"] == "video" and "entrada0" in c and "recortes" not in c]
        rec_dir = pasta / "_recortes"
        with ThreadPoolExecutor(6) as ex:
            ans = list(ex.map(lambda ic: RQ.analisar(ic[1]["arquivo"], ic[0]["layout"], ic[1]["duracoes"],
                                                     ic[1]["entrada0"], rec_dir, Path(ic[1]["arquivo"]).stem), alvos))
        ped = [{"id": f"r{k}", "texto": it.get("en") or it["busca"], "textos": [it.get("en") or it["busca"],
                                                                               it["busca"] or it.get("en") or ""],
                "imagens": an["imagens"], "iqa": True} for k, ((it, c), an) in enumerate(zip(alvos, ans)) if an]
        scr = clip(ped, T) if ped else {}
        for k, ((it, c), an) in enumerate(zip(alvos, ans)):
            if an:
                RQ.decidir(c, an, scr.get(f"r{k}", []), scr.get(f"r{k}#iqa", []), scr.get(f"r{k}#t1"))
        shutil.rmtree(rec_dir, ignore_errors=True)
        print(f"   reenquadramento ok: {sum(1 for a_ in ans if a_)} trechos ({time.time() - t0:.0f}s)", flush=True)
        for it in vid_itens:
            cs = [c for c in todos.get(it["id"], []) if c["midia"] == "video"]
            cs.sort(key=lambda c: -c["score"])
            for c in cs:
                if "recortes" in c:
                    continue
                try:
                    c["rostos"] = rostos(Image.open(c["thumb"]))
                except Exception:  # noqa: BLE001
                    c["rostos"] = []
            todos[it["id"]] = cs
        for prev in pasta.glob("prev_*"):                  # prévia 360p só servia para achar a janela
            prev.unlink(missing_ok=True)
        gravar_json(cand_p, todos)
        for it in fazer:
            if todos.get(it["id"]):
                esc[it["id"]] = escolha(it, todos[it["id"]][0], 0, T)
            else:
                print(f"   AVISO: {it['id']} sem candidato (\"{it['busca']}\")")
    # escolhas manuais
    et = T / "escolhas.txt"
    if et.exists():
        for ln in et.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\s*(\w+)\s+(\d+)", ln)
            g = re.match(r"\s*(\w+)\s+igual\s+(\w+)", ln)          # "b14 igual b07": usa a mídia do b07
            if g and g.group(2) in esc:
                esc[g.group(1)] = dict(esc[g.group(2)])
            elif m and m.group(1) in todos and int(m.group(2)) < len(todos[m.group(1)]):
                it = next(i for i in itens if i["id"] == m.group(1))
                esc[m.group(1)] = escolha(it, todos[m.group(1)][int(m.group(2))], int(m.group(2)), T)
    gravar_json(esc_p, esc)
    faltam = [it["id"] for it in itens if it["id"] not in esc]
    diretos = {it["id"] for it in itens if it["tipo"] in ("print", "arquivo") or it.get("url")}
    fracos = [f"{i} ({max((c.get('clip', 0) for c in todos.get(i, [])), default=0):.0f})" for i in esc
              if i not in diretos and todos.get(i) and todos[i][0]["midia"] == "imagem"
              and max((c.get("clip", 0) for c in todos[i]), default=0) < LIMITE_FRACO]
    if fracos:
        print("REVISAR (nenhum candidato parecido com a descrição): " + ", ".join(fracos))
    folhas = folha([it for it in itens if (so is None or it["id"] in so)], todos, T, a.n) if not a.aplicar else []
    print(f"ok: {len(esc)} itens com mídia, faltam {faltam or 'nenhum'} ({time.time() - t0:.0f}s)")
    for f in folhas:
        print("folha:", f)


def midia_de(p: Path) -> str:
    return "video" if Path(p).suffix.lower() in (".mp4", ".mov", ".webm", ".mkv", ".m4v") else "imagem"


def arquivo_pronto(it: dict, T: Path) -> Path | None:
    if it["tipo"] == "arquivo" and it.get("arquivo"):
        p = Path(it["arquivo"])
        p = p if p.is_absolute() else T / p
        return p if p.exists() else None
    for ext in (".png", ".jpg", ".jpeg", ".webp", ".mp4", ".mov"):
        p = T / "midia" / f"{it['id']}{ext}"
        if it["tipo"] == "ia" and p.exists():
            return p
        if it.get("nome"):
            p2 = T / "midia" / f"{it['nome']}{ext}"
            if it["tipo"] == "ia" and p2.exists():
                return p2
    return None


def escolha(it: dict, c: dict, k: int, T: Path) -> dict:
    e = {"arquivo": str(Path(c["arquivo"]).resolve()), "midia": c["midia"], "k": k, "url": c.get("url", ""),
         "rostos": c.get("rostos", []), "score": c.get("score"), "titulo": c.get("titulo", ""),
         "marca": c.get("marca", 0.0), "marca_flag": c.get("marca_flag", False), "logo": c.get("logo", False)}
    for chave in ("recortes", "entrada", "larga", "faixa_ok", "escuro", "baixa", "pisca", "escala", "visivel", "iqa"):
        if chave in c:
            e[chave] = c[chave]
    return e


if __name__ == "__main__":
    main()
