"""Reels CAIXINHA (CX) da Executoria 0800: edição simples + caixinha de pergunta + destaque azul.

Reaproveita a edição simples (es.py: corte na voz, aberto/fechado, legenda da novela) e a tela
dividida (imagens de apoio pelo plano.txt, render, conferência). O que é só daqui:
- a caixinha de pergunta do Instagram (faixa azul + pergunta azul no branco), desenhada em ASS
  dentro da própria legenda.ass (sem segunda passada de render);
- destaques da legenda em azul (--cor-destaque do legenda_novela.py);
- sem CTA e sem a camada película.

  python cx.py preparar  <bruto> <trabalho>      transcrição + decupagem (igual à novela)
  python cx.py montar    <trabalho>              corte na voz + alinhamento + aberto/fechado
      -> você escreve <trabalho>/legenda.txt, <trabalho>/caixinha.txt e (opcional) <trabalho>/plano.txt
  python cx.py buscar    <trabalho> [--so b03]   imagens do plano (td.py plano + buscar)
  python cx.py finalizar <trabalho> <saida.mp4> [--geral]

caixinha.txt:
  CABECALHO EXECUTORIA 0800                          (opcional; esse é o padrão)
  PERGUNTA 3 clientes são 70% do que entra. Se um sair, eu estou no vermelho. O que fazer?
  @28-45                                             palavras em que ele lê a pergunta
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SKILL = AQUI.parent
SKILLS = SKILL.parent
ES = SKILLS / "reels-edicao-simples-clailton" / "scripts"
TD = SKILLS / "reels-tela-dividida-clailton" / "scripts"
NOVELA = SKILLS / "reels-novela-clailton" / "scripts"
PY = sys.executable
# bruto do Lucas = celular 1080p: com o limite padrão (1,4x) o aberto fica largo demais e não sobra
# espaço para o fechado; a referência é bem mais fechada (peito para cima)
os.environ.setdefault("TD_UPSCALE_MAX", "1.8")
os.environ.setdefault("TD_ROSTO_ABERTO", "0.31")
ENV = {**os.environ, "PYTHONUTF8": "1"}
sys.path.insert(0, str(NOVELA))
sys.path.insert(0, str(TD))
sys.path.insert(0, str(ES))
import es  # noqa: E402

# ---- cores e medidas tiradas da referência (1080x1920; referencia/caixinha_ref.png) ----
AZUL = "03C6FA"                    # faixa da caixinha, texto da pergunta e destaque da legenda
CABECALHO_PADRAO = "EXECUTORIA 0800"      # usuário 01/10/2026: sem "Aniversário Legacy" (aquela caixinha era especial)
CX_W, CX_Y = 672, 210              # largura e topo da caixinha (centrada na horizontal)
CX_FAIXA = 82                      # altura da faixa azul
CX_RAIO = 22                       # canto arredondado
CX_PAD_V = 34                      # respiro em cima/embaixo da pergunta
CX_LARG_TEXTO = 600                # largura máxima de uma linha da pergunta
FS_CAB, FS_PERG = 27, 34           # corpo do cabeçalho e da pergunta (px)
ENTRADA, SAIDA_FADE, SOBRA = 0.5, 0.12, 0.30   # entrada (desfoque + fade), saída e quanto fica depois da pergunta
FONTE_CAB = ("SF-Pro-Display-Bold.otf", "SFProDisplay-Bold")        # nome PostScript (o nome completo cai em Arial no libass)
FONTE_PERG = ("SF-Pro-Display-Medium.otf", "SFProDisplay-Medium")

# legenda: centro do bloco no peito (como a ES)
PLANO_PADRAO = ("# caixinha 0800: começa direto no Lucas em tela cheia, sem CTA, sem película\n"
                "SEMABERTURA\nSEMCTA\nESTILO 0\n")


def etapa(script: Path, args: list[str]) -> int:
    return es.etapa(script, args)


def ler(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def ass_t(s: float) -> str:
    s = max(0.0, s)
    h, r = divmod(s, 3600)
    m, r = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{r:05.2f}"


def ler_caixinha(T: Path) -> dict | None:
    p = T / "caixinha.txt"
    if not p.exists():
        return None
    cx = {"cab": CABECALHO_PADRAO, "perg": "", "i0": None, "i1": None}
    if any(l.strip().upper() == "SEM CAIXINHA" for l in p.read_text(encoding="utf-8").splitlines()):
        return {"sem": True}       # vídeo sem pergunta (ex.: CTA da sessão estratégica, 15/10/2026)
    for ln in p.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        if ln.upper().startswith("CABECALHO"):
            cx["cab"] = ln[9:].strip()
        elif ln.upper().startswith("PERGUNTA"):
            cx["perg"] = ln[8:].strip()
        elif m := re.match(r"@(\d+)\s*-\s*(\d+)", ln):
            cx["i0"], cx["i1"] = int(m.group(1)), int(m.group(2))
    if not cx["perg"] or cx["i0"] is None:
        raise SystemExit(f"caixinha.txt incompleto (precisa de PERGUNTA e @a-b): {p}")
    return cx


def quebrar(texto: str, fonte, larg: int) -> list[str]:
    linhas, atual = [], ""
    for w in texto.split():
        teste = (atual + " " + w).strip()
        if fonte.getlength(teste) <= larg or not atual:
            atual = teste
        else:
            linhas.append(atual)
            atual = w
    if atual:
        linhas.append(atual)
    # equilibra 2 linhas (evita uma palavra sozinha embaixo)
    if len(linhas) == 2:
        ws = texto.split()
        melhor = min(range(1, len(ws)), key=lambda k: abs(fonte.getlength(" ".join(ws[:k]))
                                                        - fonte.getlength(" ".join(ws[k:]))))
        a, b = " ".join(ws[:melhor]), " ".join(ws[melhor:])
        if max(fonte.getlength(a), fonte.getlength(b)) <= larg:
            linhas = [a, b]
    return linhas


def ret_arredondado(w: float, h: float, r_cima: float, r_baixo: float) -> str:
    """Caminho ASS (\\p1) de um retângulo com cantos arredondados (origem no canto de cima à esquerda)."""
    k = 0.4477                       # bezier que aproxima o quarto de círculo
    a, b = r_cima, r_baixo
    p = [f"m {a:.1f} 0", f"l {w - a:.1f} 0",
         f"b {w - a * k:.1f} 0 {w:.1f} {a * k:.1f} {w:.1f} {a:.1f}" if a else "",
         f"l {w:.1f} {h - b:.1f}",
         f"b {w:.1f} {h - b * k:.1f} {w - b * k:.1f} {h:.1f} {w - b:.1f} {h:.1f}" if b else "",
         f"l {b:.1f} {h:.1f}",
         f"b {b * k:.1f} {h:.1f} 0 {h - b * k:.1f} 0 {h - b:.1f}" if b else "",
         f"l 0 {a:.1f}",
         f"b 0 {a * k:.1f} {a * k:.1f} 0 {a:.1f} 0" if a else ""]
    return " ".join(x for x in p if x)


def eventos_caixinha(T: Path, cx: dict) -> tuple[list[str], dict]:
    from PIL import ImageFont
    pal = ler(T / "palavras_corte.json")["palavras"]
    t0 = pal[cx["i0"]]["inicio"]
    t1 = pal[cx["i1"]]["fim"] + SOBRA
    f_perg = ImageFont.truetype(str(SKILL / "fonts" / FONTE_PERG[0]), FS_PERG)
    linhas = quebrar(cx["perg"], f_perg, CX_LARG_TEXTO)
    alt_linha = round(FS_PERG * 1.25)
    corpo_h = CX_PAD_V * 2 + alt_linha * len(linhas) - round(FS_PERG * 0.25)
    H = CX_FAIXA + corpo_h
    x0 = (1080 - CX_W) / 2
    y0 = CX_Y
    cor = f"&H{AZUL[4:6]}{AZUL[2:4]}{AZUL[0:2]}&"
    # entrada: desfoque forte -> nítido com fade (como a referência); saída: fade curto
    anim = (f"\\fad({int(ENTRADA * 1000 * 0.6)},{int(SAIDA_FADE * 1000)})"
            f"\\blur18\\t(0,{int(ENTRADA * 1000)},0.7,\\blur0)")
    ini, fim = ass_t(t0), ass_t(t1)
    ev = []
    # sombra bem leve embaixo (separa do teto claro; a referência quase não tem)
    ev.append(f"Dialogue: 60,{ini},{fim},Cap,,0,0,0,,{{\\an7\\pos({x0:.1f},{y0 + 6:.1f})\\p1\\bord0\\shad0"
              f"\\1c&H000000&\\1a&HC8&{anim.replace('blur18', 'blur24').replace('blur0)', 'blur14)')}}}"
              f"{ret_arredondado(CX_W, H, CX_RAIO, CX_RAIO)}")
    ev.append(f"Dialogue: 61,{ini},{fim},Cap,,0,0,0,,{{\\an7\\pos({x0:.1f},{y0:.1f})\\p1\\bord0\\shad0"
              f"\\1c&HFFFFFF&{anim}}}{ret_arredondado(CX_W, H, CX_RAIO, CX_RAIO)}")
    ev.append(f"Dialogue: 62,{ini},{fim},Cap,,0,0,0,,{{\\an7\\pos({x0:.1f},{y0:.1f})\\p1\\bord0\\shad0"
              f"\\1c{cor}{anim}}}{ret_arredondado(CX_W, CX_FAIXA + 1, CX_RAIO, 0)}")
    ev.append(f"Dialogue: 63,{ini},{fim},Cap,,0,0,0,,{{\\an5\\pos(540,{y0 + CX_FAIXA / 2 + 1:.1f})"
              f"\\fn{FONTE_CAB[1]}\\fs{FS_CAB}\\1c&HFFFFFF&\\bord0\\shad0{anim}}}{cx['cab']}")
    yc = y0 + CX_FAIXA + corpo_h / 2 + 1
    ev.append(f"Dialogue: 63,{ini},{fim},Cap,,0,0,0,,{{\\an5\\pos(540,{yc:.1f})\\fn{FONTE_PERG[1]}"
              f"\\fs{FS_PERG}\\1c{cor}\\bord0\\shad0\\q2{anim}}}" + "\\N".join(linhas))
    return ev, {"t0": round(t0, 2), "t1": round(t1, 2), "linhas": linhas, "altura": H}


def bruto_em_pe(bruto: Path, T: Path) -> Path:
    """Vídeo de celular guarda o "em pé" como metadado (display matrix): o enquadramento da tela dividida
    lê o quadro deitado em uma etapa e em pé na outra e não acha o rosto. Grava uma cópia já girada."""
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream_side_data=rotation", "-of", "csv=p=0", str(bruto)], capture_output=True, text=True)
    if not r.stdout.strip().strip(",").lstrip("-").replace("0", ""):
        return bruto
    T.mkdir(parents=True, exist_ok=True)
    saida = T / "bruto_em_pe.mp4"
    if not saida.exists():
        print(f"bruto com rotação de celular ({r.stdout.strip()}): gravando cópia em pé", flush=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(bruto), "-c:v", "libx264", "-crf", "10",
                        "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "copy", str(saida)], check=True)
    return saida


# ---- câmera centrada (usuário, 20/10/2026, "Negócio Sazonal"): "retire os reenquadramentos" e, na v2, "os zooms de
# pulo podemos continuar; o que não podemos são os deslizes laterais desses zooms; se for dar zoom, que seja centralizado
# no rosto do Lucas". Padrão da caixinha: UM aberto para o vídeo inteiro, centrado na horizontal nos olhos do Lucas;
# zoom seco (aberto <-> fechado) nas emendas continua, e todo fechado e todo zoom animado aproximam em volta do MESMO
# ponto (centro do quadro na horizontal, altura dos olhos): nada desliza de lado. REENQUADRAR no plano volta ao antigo.
CF_FECHADO = 1.30          # fechado sobre o aberto (o plano_td reduz se cortar a cabeça)


def camera_fixa(T: Path) -> bool:
    p = T / "plano.txt"
    return not (p.exists() and "REENQUADRAR" in p.read_text(encoding="utf-8").upper())


def enquadramento_fixo(T: Path) -> None:
    """Grava enquadramento_td.json com o MESMO aberto/fechado/olhos em todos os trechos (aberto centrado na
    horizontal nos olhos); o original fica em enquadramento_td_orig.json (refeito pelo montar)."""
    import statistics as st
    sys.path.insert(0, str(TD))
    from td_comum import rect_zoom  # noqa: E402
    atual, orig = T / "enquadramento_td.json", T / "enquadramento_td_orig.json"
    if "camera_fixa" not in ler(atual):
        shutil.copyfile(atual, orig)          # ainda não fixado (ou montar novo): o atual é o original
    e = ler(orig)
    segs = e["segmentos"]
    W0, H0 = e["wh_rot"]
    ox = st.median(s["olhos"][0] for s in segs if s.get("olhos"))
    oy = st.median(s["olhos"][1] for s in segs if s.get("olhos"))
    w = st.median(s["aberto"][2] for s in segs)
    h = w * 16 / 9
    cy = st.median(s["aberto"][1] + s["aberto"][3] / 2 for s in segs)
    x = min(max(ox - w / 2, 0), W0 - w)
    y = min(max(cy - h / 2, 0), H0 - h)
    ab = [round(x, 1), round(y, 1), round(w, 1), round(h, 1)]
    olhos = [round(x + w / 2, 1), round(oy, 1)]          # âncora: centro horizontal do quadro, altura dos olhos
    fe = [round(v, 1) for v in rect_zoom(ab, olhos, CF_FECHADO)]
    for s in segs:
        s["aberto"], s["fechado"], s["olhos"] = ab, fe, olhos
    e["camera_fixa"] = {"aberto": ab, "fechado": fe, "olhos": olhos}
    atual.write_text(json.dumps(e, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"câmera centrada: aberto {ab}, fechado {fe}, âncora {olhos}", flush=True)


def centrar_zooms(T: Path) -> None:
    """Depois do plano_td: tira qualquer deslocamento lateral — aberto sempre o fixo; fechado com o centro
    horizontal no centro do aberto (o plano_td só mexe na altura dele); zoom animado ancorado no ponto fixo."""
    tl = ler(T / "timeline.json")
    cf = ler(T / "enquadramento_td.json")["camera_fixa"]
    ab, olhos = cf["aberto"], cf["olhos"]
    cxa = ab[0] + ab[2] / 2
    n = {"aberto": 0, "fechado": 0, "animado": 0}
    for p in tl["planos"]:
        if p["zoom"] not in ("aberto", "fechado"):
            continue
        if p["zoom"] == "fechado" and (p["f1"] - p["f0"]) / tl["fps"] < 1.0:
            p["zoom"] = "aberto"               # pulo de menos de 1 s pisca: fica no aberto
        if p.get("escala"):
            p["ancora"] = olhos
            n["animado"] += 1
        if p["zoom"] == "aberto":
            p.pop("rect", None)
            n["aberto"] += 1
        elif p.get("rect"):
            r = p["rect"]
            r[0] = round(min(max(cxa - r[2] / 2, ab[0]), ab[0] + ab[2] - r[2]), 1)
            n["fechado"] += 1
    (T / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False), encoding="utf-8")
    print(f"zooms centrados: {n}", flush=True)


def finalizar(T: Path, saida: Path, geral: bool) -> int:
    if etapa(NOVELA / "emendas_literal.py", [str(T)]):
        print(f"REPETIÇÃO NA EMENDA: leia {T / 'emendas_literal.txt'}")
        return 3
    plano = T / "plano.txt"
    if not plano.exists():
        plano.write_text(PLANO_PADRAO, encoding="utf-8")
    fixa = camera_fixa(T)
    if fixa:
        enquadramento_fixo(T)
    if etapa(TD / "plano_td.py", [str(T)]):
        return 1
    if fixa:
        centrar_zooms(T)
    esc = T / "midia" / "escolhas.json"
    if not esc.exists():
        esc.parent.mkdir(parents=True, exist_ok=True)
        esc.write_text("{}", encoding="utf-8")
    (T / "rosto_es.json").write_text(json.dumps(es.rosto_no_quadro(T)), encoding="utf-8")
    leg = T / ("legenda.txt" if (T / "legenda.txt").exists() else "legenda.json")
    if not leg.exists():
        print(f"FALTA a legenda: escreva {T / 'legenda.txt'} (formato compacto da novela)")
        return 1
    if etapa(NOVELA / "legenda_novela.py", ["--plano", str(leg), "--palavras", str(T / "palavras_corte.json"),
                                            "--rosto", str(T / "rosto_es.json"), "--corte", str(T / "corte.json"),
                                            "--out", str(T / "legenda.ass"), "--layout-out", str(T / "layout_novela.json"),
                                            "--y-centro", str(es.Y_CENTRO), "--topo-min", str(es.TOPO_MIN),
                                            "--base-max", str(es.BASE_MAX), "--sem-cta", "--cor-destaque", AZUL]):
        return 1
    cx = ler_caixinha(T)
    if cx is None:
        print(f"FALTA a caixinha: escreva {T / 'caixinha.txt'} (PERGUNTA ... e @a-b)")
        return 1
    info_cx = None
    if not cx.get("sem"):
        ev, info_cx = eventos_caixinha(T, cx)
        ass = (T / "legenda.ass").read_text(encoding="utf-8").rstrip("\n") + "\n" + "\n".join(ev) + "\n"
        (T / "legenda.ass").write_text(ass, encoding="utf-8")
        print("caixinha:", json.dumps(info_cx, ensure_ascii=False))

    from comum import preparar_fontes  # noqa: E402
    dest = preparar_fontes(T)
    for f in (SKILL / "fonts").iterdir():
        if not (dest / f.name).exists():
            shutil.copyfile(f, dest / f.name)      # copyfile: a fonte do Windows vem só-leitura
    info, tl = ler(T / "layout_novela.json"), ler(T / "timeline.json")
    total = info["duracao_total"]
    (T / "layout.json").write_text(json.dumps({
        "fim_fala": info["fim_fala"], "cta_inicio": info["cta_inicio"], "duracao_total": total,
        "cta": tl["cta"], "frames_total": int(round(total * tl["fps"])) if tl["cta"] else tl["frames_fala"],
        "palavras_sha256": info.get("palavras_sha256")}, ensure_ascii=False, indent=1), encoding="utf-8")
    saida.parent.mkdir(parents=True, exist_ok=True)
    if etapa(TD / "render_td.py", [str(T), str(saida), "--estilo", "0"]):
        return 1
    rc = etapa(TD / "conferir_td.py", [str(T), str(saida)] + (["--geral"] if geral else []))
    etapa(TD / "olhos_qa.py", [str(T), str(saida)])
    # quadro da caixinha para conferir (meio da pergunta)
    qa = T / "qa"
    qa.mkdir(exist_ok=True)
    meio = (info_cx["t0"] + info_cx["t1"]) / 2 if info_cx else 1.0
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{meio:.2f}", "-i", str(saida), "-frames:v", "1",
                    str(qa / "caixinha.png")])
    print(f"folhas: {qa} (caixinha.png, fundo_mais_claro.png, zoom_olhos.jpg, relatorio.txt)")
    print("CONFERÊNCIA:", "APROVADA" if rc == 0 else "REPROVADA — ver qa/relatorio.txt")
    return rc


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    a = sys.argv[2:]
    t0 = time.time()
    if cmd == "preparar":
        a = [str(bruto_em_pe(Path(a[0]), Path(a[1])))] + a[1:]
    if cmd in ("preparar", "montar"):
        rc = etapa(ES / "es.py", [cmd] + a)
        if cmd == "montar" and rc == 0:
            print(f"\nPRÓXIMO (CX): {Path(a[0]) / 'legenda.txt'}, caixinha.txt e plano.txt (imagens)")
        sys.exit(rc)
    elif cmd == "buscar":
        T = Path(a[0])
        if etapa(TD / "plano_td.py", [str(T)]):
            sys.exit(1)
        sys.exit(etapa(TD / "td.py", ["buscar"] + a))
    elif cmd == "finalizar":
        rc = finalizar(Path(a[0]), Path(a[1]), "--geral" in a)
        print(f"[cx finalizar: {time.time() - t0:.0f}s]")
        sys.exit(rc)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
