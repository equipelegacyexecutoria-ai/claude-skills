"""Monta a página de revisão (Artifact) de uma aula: prévias curtas, títulos, thumbs, descrição e links do Drive.

Pré-requisitos: render + metadados.py + thumbs exportadas. Links do Drive em <trabalho>/drive.json:
  {"pasta": "<link da pasta da aula>", "EP01 - ...": "<link do mp4>", ...}   (o que faltar fica "subindo")

Gera em <trabalho>/pagina/:
  index.html                  a página (publicar com a ferramenta Artifact, files = o resto da pasta)
  media/epNN_inicio.mp4       abertura + ~45 s do começo (540p, ~4 MB)
  media/epNN_qr.mp4           a 1ª entrada do QR (10 s, 720p, para ver o card no celular)
  media/epNN_thumbK.jpg       os 3 recortes escolhidos para a thumb

Uso: python pagina.py <trabalho> [--sem-media]
"""
from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import ler_json  # noqa: E402

CSS = """
/* Layout: uma coluna de leitura; cada episódio é uma ficha com prévia à esquerda e o pacote do YouTube à direita */
:root{
  --bg:#f3f5f9; --surface:#ffffff; --ink:#0f1b2d; --muted:#5b6b82; --line:#d9e0ea;
  --accent:#1c6fd2; --accent-ink:#ffffff; --go:#1f9d48; --warn:#a15c00; --warn-bg:#fff4e0;
  --display:"Barlow Condensed","Arial Narrow",sans-serif; --body:"Source Sans 3","Segoe UI",sans-serif;
  --mono:"JetBrains Mono",ui-monospace,Consolas,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#0b1220; --surface:#121c2e; --ink:#e7edf6; --muted:#9aabc3; --line:#24324a;
  --accent:#5aa2ff; --accent-ink:#0b1220; --go:#46c46e; --warn:#ffb54d; --warn-bg:#2a2112; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#0b1220; --surface:#121c2e; --ink:#e7edf6; --muted:#9aabc3; --line:#24324a;
  --accent:#5aa2ff; --accent-ink:#0b1220; --go:#46c46e; --warn:#ffb54d; --warn-bg:#2a2112; color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font:16px/1.5 var(--body);margin:0}
.wrap{max-width:1180px;margin:0 auto;padding-inline:16px;padding-block:28px 64px;display:grid;gap:28px}
header h1{font:700 clamp(32px,6vw,52px)/1 var(--display);letter-spacing:.01em;margin:0;text-wrap:balance}
header p{color:var(--muted);margin:.4em 0 0;max-width:70ch}
.resumo{display:flex;flex-wrap:wrap;gap:10px;margin-top:14px}
.chip{border:1px solid var(--line);background:var(--surface);border-radius:999px;padding:4px 12px;font-size:14px}
.chip b{font-family:var(--mono);font-weight:600}
.ep{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:20px;display:grid;
    grid-template-columns:minmax(0,1fr) minmax(0,1.15fr);gap:24px}
@media (max-width:860px){.ep{grid-template-columns:minmax(0,1fr)}}
.ep h2{font:700 30px/1.05 var(--display);margin:0 0 4px;text-wrap:balance}
.rot{font:600 12px/1 var(--body);letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:18px 0 8px}
.rot:first-child{margin-top:0}
video{width:100%;border-radius:10px;background:#000;display:block}
.meta{font-family:var(--mono);font-size:13px;color:var(--muted)}
.lista{display:grid;gap:8px;margin:0;padding:0;list-style:none}
.item{display:flex;gap:10px;align-items:flex-start;border:1px solid var(--line);border-radius:10px;padding:10px 12px}
.item span{flex:1;min-width:0}
.item.rec{border-color:var(--accent)}
.tag{font:600 11px/1.6 var(--body);letter-spacing:.08em;text-transform:uppercase;color:var(--accent-ink);
     background:var(--accent);border-radius:4px;padding:0 6px;white-space:nowrap}
button.cp{font:600 13px var(--body);border:1px solid var(--line);background:transparent;color:var(--ink);
          border-radius:8px;padding:4px 10px;cursor:pointer;white-space:nowrap}
button.cp:focus-visible,a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.thumbs{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
.thumbs figure{margin:0}.thumbs img{border-radius:8px;display:block;width:100%;aspect-ratio:16/9;object-fit:cover}
.thumbs figcaption{font-size:12px;color:var(--muted);margin-top:4px}
pre{white-space:pre-wrap;word-break:break-word;font:13px/1.5 var(--mono);background:var(--bg);border:1px solid var(--line);
    border-radius:10px;padding:12px;max-height:340px;overflow:auto;margin:0}
.links{display:flex;flex-wrap:wrap;gap:8px}
.links a{font-weight:600;color:var(--accent-ink);background:var(--accent);text-decoration:none;border-radius:8px;padding:8px 14px}
.links a.sec{background:transparent;color:var(--accent);border:1px solid var(--accent)}
.links .pend{color:var(--muted);font-size:14px;padding:8px 0}
.aviso{background:var(--warn-bg);color:var(--ink);border-left:3px solid var(--warn);border-radius:6px;padding:10px 12px;font-size:14px}
.aviso ul{margin:6px 0 0;padding-left:18px}
.qrs{display:flex;flex-wrap:wrap;gap:6px}
.qrs .chip{font-family:var(--mono);font-size:13px}
details summary{cursor:pointer;color:var(--accent);font-weight:600}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""

JS = """
document.querySelectorAll('button.cp').forEach(b=>b.addEventListener('click',async()=>{
  const alvo=document.getElementById(b.dataset.alvo); const txt=alvo.innerText;
  try{await navigator.clipboard.writeText(txt); b.textContent='Copiado';}
  catch(e){const r=document.createRange(); r.selectNodeContents(alvo); const s=getSelection(); s.removeAllRanges(); s.addRange(r); b.textContent='Selecionado: copie';}
  setTimeout(()=>b.textContent='Copiar',1800);
}));
"""


def e(x) -> str:
    return html.escape(str(x))


def mmss(t: float) -> str:
    t = int(round(t))
    h, r = divmod(t, 3600)
    m, s = divmod(r, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def cortar(video: Path, ini: float, dur: float, saida: Path, altura: int, crf: int) -> None:
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{ini:.2f}", "-i", str(video), "-t", f"{dur:.2f}",
                    "-vf", f"scale=-2:{altura}", "-c:v", "libx264", "-preset", "slow", "-crf", str(crf),
                    "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(saida)], check=True)


def descricao_do_txt(txt: str) -> tuple[str, str]:
    m = re.search(r"DESCRIÇÃO \(copiar e colar\):\n=+\n(.*?)\n=+\n", txt, re.S)
    c = re.search(r"COMENTÁRIO FIXADO:\n(.*?)\n", txt)
    return (m.group(1) if m else ""), (c.group(1) if c else "")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("trabalho")
    ap.add_argument("--sem-media", action="store_true")
    a = ap.parse_args()
    trab = Path(a.trabalho)
    plano = ler_json(trab / "plano.json")
    drive = ler_json(trab / "drive.json") if (trab / "drive.json").exists() else {}
    out = trab / "pagina"
    (out / "media").mkdir(parents=True, exist_ok=True)
    fichas, total = [], 0.0
    for ep in plano["episodios"]:
        n, nome, mt = ep["n"], ep["arquivo"], ep["meta"]
        if not (trab / "render" / f"{nome} - YOUTUBE.txt").exists():
            print(f"pulado (sem render/metadados): {nome}")
            continue
        info = ler_json(trab / "render" / f"{nome}.json")
        video = trab / "render" / f"{nome}.mp4"
        total += info["duracao"]
        tag = f"ep{n:02d}"
        if not a.sem_media:
            cortar(video, 0, info["abertura_dur"] + 45, out / "media" / f"{tag}_inicio.mp4", 540, 30)
            t0 = info["card"]["posicoes"][0]["t"]
            cortar(video, max(0, t0 - 2), 10, out / "media" / f"{tag}_qr.mp4", 720, 27)
            for k in (1, 2, 3):
                png = trab / "thumbs" / f"{nome} - thumb {k} (recorte rosto).png"
                if png.exists():
                    Image.open(png).convert("RGB").resize((640, 360), Image.LANCZOS).save(
                        out / "media" / f"{tag}_thumb{k}.jpg", quality=84)
        txt = (trab / "render" / f"{nome} - YOUTUBE.txt").read_text(encoding="utf-8")
        desc, coment = descricao_do_txt(txt)
        titulos = "".join(
            f'<li class="item{" rec" if i == 0 else ""}"><span id="{tag}t{i}">{e(t)}</span>'
            f'{"<em class=tag>recomendado</em>" if i == 0 else ""}'
            f'<button class="cp" data-alvo="{tag}t{i}">Copiar</button></li>' for i, t in enumerate(mt["titulos"]))
        thumbs_txt = "".join(
            f'<li class="item{" rec" if i == 0 else ""}"><span id="{tag}x{i}"><b>{e(t)}</b></span>'
            f'{"<em class=tag>recomendado</em>" if i == 0 else ""}'
            f'<button class="cp" data-alvo="{tag}x{i}">Copiar</button></li>' for i, t in enumerate(mt["thumbs"]))
        imgs = "".join(f'<figure><img src="media/{tag}_thumb{k}.jpg" alt="Opção {k} de imagem para a thumb do '
                       f'episódio {n}" loading="lazy"><figcaption>Imagem {k}</figcaption></figure>'
                       for k in (1, 2, 3) if (out / "media" / f"{tag}_thumb{k}.jpg").exists())
        qrs = "".join(f'<span class="chip">{mmss(p["t"])}</span>' for p in info["card"]["posicoes"])
        link = drive.get(nome)
        links = (f'<a href="{e(link)}" target="_blank" rel="noopener">Assistir o episódio inteiro</a>' if link
                 else '<span class="pend">Vídeo inteiro: subindo para o Drive…</span>')
        if drive.get("pasta"):
            links += f'<a class="sec" href="{e(drive["pasta"])}" target="_blank" rel="noopener">Pasta no Drive</a>'
        fatos = ""
        if mt.get("fatos"):
            fatos = ('<div class="aviso"><b>Dados falados de cabeça que estão imprecisos</b> (o vídeo fica como está; '
                     'só não repita no título, na thumb nem na descrição):<ul>' +
                     "".join(f"<li>{e(f)}</li>" for f in mt["fatos"]) + "</ul></div>")
        fichas.append(f"""
<section class="ep" id="{tag}">
  <div>
    <p class="rot">Episódio {n} · {mmss(info['duracao'])}</p>
    <h2>{e(mt['titulos'][0].split(' | ')[0])}</h2>
    <p class="meta">{e(nome)}.mp4</p>
    <p class="rot">Começo do episódio (abertura + primeiros 45 s)</p>
    <video controls playsinline preload="metadata" src="media/{tag}_inicio.mp4"></video>
    <p class="rot">Como o QR aparece</p>
    <video controls playsinline muted preload="metadata" src="media/{tag}_qr.mp4"></video>
    <p class="rot">QR da sessão estratégica na tela (30 s cada)</p>
    <div class="qrs">{qrs}</div>
    <p class="rot">Arquivos</p>
    <div class="links">{links}</div>
  </div>
  <div>
    <p class="rot">Título</p><ul class="lista">{titulos}</ul>
    <p class="rot">Texto da thumb</p><ul class="lista">{thumbs_txt}</ul>
    <p class="rot">Imagens para a arte da thumb</p><div class="thumbs">{imgs}</div>
    <p class="rot">Descrição <button class="cp" data-alvo="{tag}d">Copiar</button></p>
    <pre id="{tag}d">{e(desc)}</pre>
    <p class="rot">Comentário fixado <button class="cp" data-alvo="{tag}c">Copiar</button></p>
    <pre id="{tag}c">{e(coment)}</pre>
    <details><summary>Tags</summary><p id="{tag}g">{e(", ".join(mt["tags"]))}</p></details>
    {fatos}
  </div>
</section>""")
    aula = plano.get("aula", "")
    pagina = f"""<title>Legado no YouTube</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=JetBrains+Mono:wght@400;600&family=Source+Sans+3:wght@400;600;700&display=swap">
<style>{CSS}</style>
<main class="wrap">
<header>
  <h1>Legado no YouTube</h1>
  <p>{e(aula)} virou {len(fichas)} episódios com começo, meio e fim. Cada um abre com o trecho mais forte, mostra o QR da
  sessão estratégica 3 vezes e já tem título, texto da thumb e descrição prontos para colar.</p>
  <div class="resumo"><span class="chip"><b>{len(fichas)}</b> episódios</span><span class="chip"><b>{mmss(total)}</b> no total</span>
  <span class="chip">link da sessão: <b>formulario.legacyexecutoria.com.br</b></span></div>
</header>
{''.join(fichas)}
</main>
<script>{JS}</script>
"""
    (out / "index.html").write_text(pagina, encoding="utf-8")
    arquivos = {f"media/{p.name}": str(p) for p in sorted((out / "media").glob("*"))}
    (out / "arquivos.json").write_text(json.dumps(arquivos, ensure_ascii=False, indent=1), encoding="utf-8")
    tam = sum(Path(v).stat().st_size for v in arquivos.values()) / 1e6
    print(f"ok: {out / 'index.html'} · {len(arquivos)} arquivos de mídia, {tam:.1f} MB")


if __name__ == "__main__":
    main()
