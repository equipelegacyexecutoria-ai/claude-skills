#!/usr/bin/env python3
"""Ajudantes da etapa de imagens (precisa de Python 3 + Pillow e de acesso à internet).

  python3 scripts/imagens.py coletar URL_DA_MATERIA [URL ...] [--pasta imagens]
      Lê cada matéria e baixa as fotos dela (og:image, figuras e imagens do texto), tentando
      o arquivo original sem o sufixo de tamanho (-1200x675). Descarta logo, ícone e foto com
      menos de 500 px. Mostra tamanho, legenda/crédito achado e se precisa ampliar.
  python3 scripts/imagens.py wikimedia "Nome da pessoa ou da marca" [--n 8]
      Busca no Wikimedia Commons: endereço do original, tamanho, autor e licença (crédito pronto).
  python3 scripts/imagens.py folha SAIDA.jpg IMAGEM_OU_URL [...] [--titulo "Card 3"]
      Folha de contato numerada (4 por linha) para escolher olhando.
  python3 scripts/imagens.py escala LARGURA ALTURA
      Quanto a imagem precisa crescer para cobrir cada moldura do LEGACY.
  python3 scripts/imagens.py recortar IMAGEM SAIDA.jpg --centro X,Y --lado L
      Recorte quadrado (ex.: rosto para o círculo da capa), em px da imagem original.

Sem internet na execução de código (claude.ai com a rede bloqueada), use o caminho sem
script descrito em references/imagens.md.
"""
import hashlib
import html
import json
import os
import re
import sys
import tempfile
import urllib.parse
import urllib.request
from io import BytesIO

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover
    sys.exit("Falta o Pillow: pip install pillow")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
UA_WIKI = "carrossel-canva/1.0 (skill do Claude para carrosseis de Instagram)"
MOLDURAS = {"capa": (1104, 1142), "pag2": (1109, 1210), "pag3": (1109, 943), "circulo": (433, 433)}
RUIM = re.compile(r"logo|icon|avatar|badge|sprite|placeholder|banner|/ads?/|pixel|gravatar|emoji|selo|seal|"
                  r"author|autor|colunista|whatsapp|facebook|twitter|instagram|share|default", re.I)
CREDITO = re.compile(r"((?:Fotos?|Cr[eé]dito|Imagem)\s*:\s*[^<>\n|]{3,80}|[A-ZÁÉÍÓÚ][^<>\n|]{2,50}/\s*"
                     r"(?:Divulga[cç][aã]o|Reprodu[cç][aã]o|Folhapress|Estad[aã]o Conte[uú]do|Ag[eê]ncia \w+|"
                     r"VEJA|Reuters|AFP|AP|Getty Images|Shutterstock))")


def baixar(url, ua=UA, limite=15_000_000, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(limite), r.headers.get("Content-Type", "")


def abrir(dados):
    im = Image.open(BytesIO(dados))
    im.load()
    return im


def escala(w, h):
    out = {}
    for nome, (fw, fh) in MOLDURAS.items():
        s = max(fw / w, fh / h)
        out[nome] = {"cresce": round(s, 2), "veredito": "ok" if s <= 1.15 else ("ampliar 2x" if s <= 2.3 else "pequena demais")}
    return out


def original_de(url):
    """Endereço provável do arquivo original (sem o sufixo de tamanho do WordPress/CDN)."""
    u = re.sub(r"-\d{2,4}x\d{2,4}(?=\.(?:jpe?g|png|webp)(?:\?|$))", "", url, flags=re.I)
    m = re.match(r"https?://(?:upload|thumb)\.wikimedia\.org/wikipedia/commons/thumb/(\w/\w\w/[^/]+)/", u)
    if m:
        u = "https://upload.wikimedia.org/wikipedia/commons/" + m.group(1)
    return u if u != url else None


PARE = set("para com sem que uma dos das nos nas por mais como sobre entre apos após depois antes "
           "empresa diz veja saiba entenda noticia notícia noticias notícias hoje".split())


def sem_acento(t):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", t.lower()) if unicodedata.category(c) != "Mn")


def palavras_do_titulo(texto):
    """(nomes próprios, palavras comuns) do título da matéria, sem acento e em minúsculas."""
    m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)', texto, re.I) or \
        re.search(r"<title[^>]*>(.*?)</title>", texto, re.I | re.S)
    toks = re.findall(r"[A-Za-zÀ-ÿ0-9]+", html.unescape(m.group(1))) if m else []
    nomes = set()
    for i, w in enumerate(toks):
        if len(w) >= 3 and w[0].isupper() and (i > 0 or (len(toks) > 1 and toks[1][:1].isupper())):
            nomes.add(sem_acento(w))
    gerais = {sem_acento(w) for w in toks if len(w) >= 4 and sem_acento(w) not in PARE} - nomes
    return nomes, gerais


def relevante_para(chave, url, legenda):
    nomes, gerais = chave
    alvo = " " + " ".join(re.findall(r"[a-z0-9]+", sem_acento(url + " " + legenda))) + " "
    if nomes:
        return any(f" {n} " in alvo for n in nomes)
    return sum(f" {g} " in alvo for g in gerais) >= 2


def sem_tags(t):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", t)).split())


def maior_do_srcset(s):
    maior = sorted(((int(w), u) for u, w in re.findall(r"(\S+)\s+(\d+)w", s)), reverse=True)
    return maior[0][1] if maior else None


def candidatos(pagina, texto):
    """Fotos da página, das mais ligadas ao título da matéria para as menos: (url, legenda, relevante)."""
    achados = []  # (url, legenda)
    for pat in (r'<meta[^>]+property=["\']og:image(?::url)?["\'][^>]+content=["\']([^"\']+)',
                r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image',
                r'<meta[^>]+name=["\']twitter:image(?::src)?["\'][^>]+content=["\']([^"\']+)'):
        achados += [(u, "capa da matéria") for u in re.findall(pat, texto, re.I)]
    corpo = re.sub(r"<(script|style|nav|footer)\b.*?</\1>", " ", texto, flags=re.I | re.S)
    blocos = re.findall(r"<figure.*?</figure>", corpo, re.I | re.S) + \
        re.findall(r"<div[^>]+class=[\"'][^\"']*wp-caption[^\"']*[\"'][^>]*>.*?</div>", corpo, re.I | re.S)
    for b in blocos:  # foto com legenda (figure ou legenda do WordPress): o texto do bloco é a legenda
        leg = sem_tags(b)
        for u in re.findall(r'(?:data-src|data-lazy-src|src)=["\']([^"\']+)', b, re.I):
            achados.append((u, leg))
        for s in re.findall(r'srcset=["\']([^"\']+)', b, re.I):
            if maior_do_srcset(s):
                achados.append((maior_do_srcset(s), leg))
    for tag in re.findall(r"<img[^>]+>", corpo, re.I):
        alt = re.search(r'alt=["\']([^"\']*)', tag, re.I)
        alt = alt.group(1) if alt else ""
        for u in re.findall(r'(?:data-src|data-lazy-src|src)=["\']([^"\']+)', tag, re.I):
            achados.append((u, alt))
        s = re.search(r'srcset=["\']([^"\']+)', tag, re.I)
        if s and maior_do_srcset(s.group(1)):
            achados.append((maior_do_srcset(s.group(1)), alt))
    chave = palavras_do_titulo(texto)
    vistos, out = set(), []
    for u, leg in achados:
        u = html.unescape(u.strip())
        if u.startswith("data:"):
            continue
        u = urllib.parse.urljoin(pagina, u)
        if not re.search(r"\.(jpe?g|png|webp)(\?|$)", u, re.I) and \
                not re.search(r"(image|img|foto|photo|upload|media)", u, re.I):
            continue
        leg = " ".join(html.unescape(leg).split())[:200]
        base = original_de(u) or u
        if RUIM.search(u) or re.search(r"perfil do autor|foto do autor|colunista", leg, re.I) or base in vistos:
            continue
        vistos.add(base)
        out.append((u, leg, leg == "capa da matéria" or relevante_para(chave, u, leg)))
    out.sort(key=lambda x: not x[2])
    return out


def coletar(urls, pasta="imagens", maximo=8):
    os.makedirs(pasta, exist_ok=True)
    res = []
    for pagina in urls:
        try:
            dados, _ = baixar(pagina)
            texto = dados.decode("utf-8", "replace")
        except Exception as e:
            res.append({"pagina": pagina, "erro": str(e)[:120]})
            continue
        limpo = sem_tags(re.sub(r"<(script|style)\b.*?</\1>", " ", texto, flags=re.I | re.S))
        creditos = []
        for c in CREDITO.findall(limpo):
            c = re.split(r"\s{2,}|\. |\s-\s", " ".join(c.split()))[0][:60]
            if c not in creditos:
                creditos.append(c)
        usados, fora, finais = 0, 0, set()
        for url, legenda, relevante in candidatos(pagina, texto):
            if usados >= maximo or (not relevante and fora >= 1):  # no máximo 1 fora do assunto por página
                break
            im, final = None, url
            for tent in filter(None, (original_de(url), url)):
                try:
                    d, _ = baixar(tent)
                    im, final = abrir(d), tent
                    break
                except Exception:
                    continue
            if im is None or im.width < 500 or final in finais:
                continue
            finais.add(final)
            nome = hashlib.md5(final.encode()).hexdigest()[:10] + ".jpg"
            im.convert("RGB").save(os.path.join(pasta, nome), quality=90)
            usados += 1
            fora += 0 if relevante else 1
            na_legenda = CREDITO.search(legenda)
            res.append({"pagina": pagina, "url": final, "w": im.width, "h": im.height,
                        "arquivo": os.path.join(pasta, nome), "legenda": legenda, "relevante": relevante,
                        "credito": na_legenda.group(0).strip() if na_legenda else None,
                        "creditos_na_pagina": creditos[:3],
                        "escala": {k: v["veredito"] for k, v in escala(im.width, im.height).items()}})
    ok = [r for r in res if "arquivo" in r]
    ok.sort(key=lambda r: not r["relevante"])
    for n, r in enumerate(ok, 1):  # o número da lista vai no nome: a folha sai na mesma ordem
        r["n"] = n
        novo = os.path.join(pasta, f"{n:02d}_" + os.path.basename(r["arquivo"]))
        os.replace(r["arquivo"], novo)
        r["arquivo"] = novo
    res = ok + [r for r in res if "erro" in r]
    with open(os.path.join(pasta, "coletadas.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    for r in res:
        if "erro" in r:
            print(f"ERRO {r['pagina'][:70]}: {r['erro']}")
        else:
            marca = "" if r["relevante"] else "  [fora do assunto?]"
            cred = r["credito"] or ("na página: " + "; ".join(r["creditos_na_pagina"])[:120] if r["creditos_na_pagina"] else "-")
            print(f"{r['n']:>2}. {r['w']}x{r['h']}  pag3={r['escala']['pag3']}  capa={r['escala']['capa']}{marca}\n"
                  f"    {r['url'][:110]}\n    legenda: {r['legenda'][:120] or '-'}\n    crédito: {cred}")
    print(f"\n{len([r for r in res if 'arquivo' in r])} imagens em {pasta}/ (lista em {pasta}/coletadas.json)")


def wikimedia(termo, n=8):
    q = urllib.parse.urlencode({
        "action": "query", "format": "json", "generator": "search", "gsrnamespace": 6,
        "gsrsearch": termo + " filetype:bitmap", "gsrlimit": n, "prop": "imageinfo",
        "iiprop": "url|size|extmetadata", "iiurlwidth": 1280})
    dados, _ = baixar("https://commons.wikimedia.org/w/api.php?" + q, ua=UA_WIKI)
    paginas = json.loads(dados).get("query", {}).get("pages", {})
    for p in sorted(paginas.values(), key=lambda p: p.get("index", 0)):
        ii = (p.get("imageinfo") or [{}])[0]
        meta = ii.get("extmetadata", {})
        autor = re.sub(r"<[^>]+>", "", meta.get("Artist", {}).get("value", "")).strip() or "autor não informado"
        lic = meta.get("LicenseShortName", {}).get("value", "?")
        limpa = lambda u: re.sub(r"\?utm_.*$", "", u or "")
        print(f"- {p['title']}  {ii.get('width')}x{ii.get('height')}  licença {lic}\n"
              f"  original: {limpa(ii.get('url'))}\n  1280 px: {limpa(ii.get('thumburl'))}\n"
              f"  crédito: Foto: {autor}/Wikimedia Commons ({lic})\n  página: {ii.get('descriptionurl')}")


def fonte(tam):
    try:
        return ImageFont.load_default(size=tam)
    except TypeError:  # Pillow antigo
        return ImageFont.load_default()


def folha(saida, itens, titulo=""):
    COL, W, H, PAD, TOP = 4, 420, 420, 12, 56
    ims = []
    for it in itens:
        try:
            if re.match(r"https?://", it):
                d, _ = baixar(it)
                im = abrir(d)
            else:
                im = Image.open(it)
            ims.append((im.convert("RGB"), it))
        except Exception as e:
            print(f"pulei {it[:80]}: {e}")
    linhas = (len(ims) + COL - 1) // COL
    fl = Image.new("RGB", (COL * (W + PAD) + PAD, TOP + linhas * (H + 40 + PAD)), (24, 24, 24))
    d = ImageDraw.Draw(fl)
    f1, f2 = fonte(24), fonte(16)
    d.text((PAD, 14), titulo, fill=(255, 255, 255), font=f1)
    for i, (im, nome) in enumerate(ims):
        w0, h0 = im.size
        im.thumbnail((W, H))
        x, y = PAD + (i % COL) * (W + PAD), TOP + (i // COL) * (H + 40 + PAD)
        fl.paste(im, (x + (W - im.width) // 2, y + (H - im.height) // 2))
        d.rectangle([x, y, x + 44, y + 34], fill=(231, 170, 81))
        d.text((x + 10, y + 5), str(i + 1), fill=(0, 0, 0), font=f1)
        d.text((x, y + H + 8), f"{w0}x{h0}  {os.path.basename(nome.split('?')[0])[:30]}", fill=(190, 190, 190), font=f2)
    fl.save(saida, quality=85)
    print(saida, fl.size, f"{len(ims)} imagens")


def recortar(img, saida, centro, lado):
    im = Image.open(img).convert("RGB")
    cx, cy = centro
    x0 = max(0, min(im.width - lado, cx - lado // 2))
    y0 = max(0, min(im.height - lado, cy - lado // 2))
    im.crop((x0, y0, x0 + lado, y0 + lado)).save(saida, quality=94)
    print(saida, f"{lado}x{lado}", f"a partir de ({x0},{y0})")


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd, args = sys.argv[1], sys.argv[2:]
    opts, livres, i = {}, [], 0
    while i < len(args):
        if args[i].startswith("--"):
            opts[args[i]] = args[i + 1]
            i += 2
        else:
            livres.append(args[i])
            i += 1
    if cmd == "coletar":
        coletar(livres, opts.get("--pasta", "imagens"), int(opts.get("--max", 8)))
    elif cmd == "wikimedia":
        wikimedia(" ".join(livres), int(opts.get("--n", 8)))
    elif cmd == "folha":
        folha(livres[0], livres[1:], opts.get("--titulo", ""))
    elif cmd == "escala":
        print(json.dumps(escala(float(livres[0]), float(livres[1])), ensure_ascii=False))
    elif cmd == "recortar":
        cx, cy = (int(float(v)) for v in opts["--centro"].split(","))
        recortar(livres[0], livres[1], (cx, cy), int(float(opts["--lado"])))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
