"""Edição Simples (ES) do Clailton: tela cheia 9:16 + legenda da NOVELA + CTA.

Reaproveita as outras duas skills:
- corte, alinhamento, rotação da câmera deitada e aberto/fechado: tela dividida (td.py, sem imagens);
- legenda: novela (legenda_novela.py, telas de 1-3 linhas com destaque), subida para o peito;
- render: render_td.py sem a camada película; conferência: conferir_td.py.

  python es.py preparar  <bruto> <trabalho>      transcrição + decupagem (igual à novela)
      -> revisão curta da decupagem (regras da novela)
  python es.py montar    <trabalho>              corte na voz + alinhamento + rotação + aberto/fechado
      -> legenda: o orquestrador escreve <trabalho>/legenda.txt (formato compacto da novela)
  python es.py finalizar <trabalho> <saida.mp4> [--geral]
      plano sem imagens (ou o plano.txt que existir) + legenda + render + conferência
Roteiro: salve em <trabalho>/roteiro.txt (ou .docx / .md) ANTES do preparar.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SKILLS = AQUI.parent.parent
TD = SKILLS / "reels-tela-dividida-clailton" / "scripts"
NOVELA = SKILLS / "reels-novela-clailton" / "scripts"
PY = sys.executable
ENV = {**os.environ, "PYTHONUTF8": "1"}
sys.path.insert(0, str(NOVELA))

# posição da legenda medida na referência (instagram.com/p/DdHziJUhn0N): centro do bloco a ~52,5%
# da altura (peito), nunca em cima do queixo
Y_CENTRO, TOPO_MIN, BASE_MAX = 1010.0, 700.0, 1650.0
QUEIXO_FATOR = 0.62        # queixo ~ centro da caixa do rosto + 0,62 x largura (caixa do YuNet ~1,25 x mais alta)
PLANO_PADRAO = ("# edição simples: sem imagens; começa direto no Clailton em tela cheia,\n"
                "# só o aberto/fechado automático (FECHADO/ABERTO @a-b forçam um trecho)\n"
                "SEMABERTURA\n")


def etapa(script: Path, args: list[str]) -> int:
    t0 = time.time()
    r = subprocess.run([PY, str(script)] + args, env=ENV)
    print(f"   [{script.name}: {time.time() - t0:.0f}s]", flush=True)
    return r.returncode


def ler(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def rosto_no_quadro(T: Path) -> list[dict]:
    """Queixo (y no quadro final 1080x1920) a cada plano do Clailton, para a legenda não subir no rosto."""
    tl, enq = ler(T / "timeline.json"), ler(T / "enquadramento_td.json")
    fps = tl["fps"]
    segs = {s["k"]: s for s in enq["segmentos"]}
    out = []
    for p in tl["planos"]:
        s = segs.get(p["seg"])
        if not s or p["zoom"] not in ("aberto", "fechado"):
            continue
        cx, cy, fw = s["rosto"]
        x, y, w, h = s[p["zoom"]]
        q = (cy + QUEIXO_FATOR * fw - y) / h * 1920
        f = p["f0"]
        while f < p["f1"]:
            out.append({"t": round(f / fps, 3), "queixo": round(q, 1)})
            f += max(1, int(fps / 2))
    return out


def finalizar(T: Path, saida: Path, geral: bool) -> int:
    plano = T / "plano.txt"
    if not plano.exists():
        plano.write_text(PLANO_PADRAO, encoding="utf-8")
    if etapa(TD / "plano_td.py", [str(T)]):
        return 1
    esc = T / "midia" / "escolhas.json"
    if not esc.exists():
        esc.parent.mkdir(parents=True, exist_ok=True)
        esc.write_text("{}", encoding="utf-8")
    (T / "rosto_es.json").write_text(json.dumps(rosto_no_quadro(T)), encoding="utf-8")

    leg = T / ("legenda.txt" if (T / "legenda.txt").exists() else "legenda.json")
    if not leg.exists():
        print(f"FALTA a legenda: escreva {T / 'legenda.txt'} (formato compacto da novela)")
        return 1
    if etapa(NOVELA / "legenda_novela.py", ["--plano", str(leg), "--palavras", str(T / "palavras_corte.json"),
                                            "--rosto", str(T / "rosto_es.json"), "--corte", str(T / "corte.json"),
                                            "--out", str(T / "legenda.ass"), "--layout-out", str(T / "layout_novela.json"),
                                            "--y-centro", str(Y_CENTRO), "--topo-min", str(TOPO_MIN),
                                            "--base-max", str(BASE_MAX)]):
        return 1
    from comum import preparar_fontes  # noqa: E402
    preparar_fontes(T)
    info, tl = ler(T / "layout_novela.json"), ler(T / "timeline.json")
    total = info["duracao_total"]
    # o render e a conferência da tela dividida leem o layout.json no formato deles
    (T / "layout.json").write_text(json.dumps({
        "fim_fala": info["fim_fala"], "cta_inicio": info["cta_inicio"], "duracao_total": total,
        "cta": tl["cta"], "frames_total": int(round(total * tl["fps"])) if tl["cta"] else tl["frames_fala"],
        "palavras_sha256": info.get("palavras_sha256")}, ensure_ascii=False, indent=1), encoding="utf-8")

    saida.parent.mkdir(parents=True, exist_ok=True)
    if etapa(TD / "render_td.py", [str(T), str(saida), "--estilo", "0"]):
        return 1
    rc = etapa(TD / "conferir_td.py", [str(T), str(saida)] + (["--geral"] if geral else []))
    print(f"folhas: {T / 'qa'} (fundo_mais_claro.png, relatorio.txt" + (", folha_geral_NN.jpg)" if geral else ")"))
    print("CONFERÊNCIA:", "APROVADA" if rc == 0 else "REPROVADA — ver qa/relatorio.txt")
    return rc


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    a = sys.argv[2:]
    if cmd in ("preparar", "montar"):
        rc = etapa(TD / "td.py", [cmd] + a)
        if cmd == "montar" and rc == 0:
            print(f"\nPRÓXIMO (ES): legenda em {Path(a[0]) / 'legenda.txt'} a partir de palavras_legenda.txt"
                  " (formato compacto da novela); o plano visual NÃO é preciso")
        sys.exit(rc)
    elif cmd == "finalizar":
        sys.exit(finalizar(Path(a[0]), Path(a[1]), "--geral" in a))
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
