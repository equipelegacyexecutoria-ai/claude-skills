"""Reels TELA DIVIDIDA: um comando por etapa (o orquestrador só entra nas decisões de julgamento).

  python td.py roteiro   <roteiro.md|.txt|.docx> <T>   separa a fala (roteiro.txt) e o mapa de
                                               âncoras/1º frame (ancoras.txt) do roteiro do roteirista
  python td.py preparar  <video> <T>          transcrição (GPU) + decupagem automática (da novela)
      -> revisão curta de T/decupagem_proposta.txt (+ roteiro_x_fala.txt) -> decupagem_ajustes.txt
         e P S_NOVELA/decupar_auto.py T --aplicar T/decupagem_ajustes.txt
  python td.py montar    <T>                   corte colado na voz + alinhamento (novela) e, junto,
                                               rotação + enquadramento 9:16 (aberto/fechado/dividida)
      -> o orquestrador escreve T/plano.txt (plano visual) a partir de palavras_legenda.txt
  python td.py plano     <T>                   plano.txt -> timeline.json + timeline.txt (avisos/ritmo)
  python td.py buscar    <T> [--so b03,b07]    imagens/vídeos: busca, baixa, ranqueia (CLIP) e monta
                                               qa/candidatos_NN.jpg; escolha padrão = 1º do ranking
  python td.py escolher  <T>                   aplica T/escolhas.txt ("b03 2", "b14 igual b07")
  python td.py finalizar <T> <saida.mp4> [--premiere] [--geral]
                                               legenda + render (CRF 10) + conferência (+ pacote Premiere)
  python td.py previa    <T> [segundos]        render rápido (veryfast) para olhar antes do final

Roteiro: salve em T/roteiro.txt (ou .md/.docx) ANTES do preparar.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
NOVELA = Path.home() / ".claude" / "skills" / "reels-novela-clailton" / "scripts"
PY = sys.executable
ENV = {**os.environ, "PYTHONUTF8": "1"}


def etapa(script: Path, args: list[str]) -> int:
    t0 = time.time()
    r = subprocess.run([PY, str(script)] + args, env=ENV)
    print(f"   [{script.name}: {time.time() - t0:.0f}s]", flush=True)
    return r.returncode


def tem_roteiro(t: Path) -> bool:
    return any((t / n).exists() for n in ("roteiro.txt", "roteiro.md", "roteiro.docx"))


def separar_roteiro(arq: Path, T: Path) -> None:
    """Roteiro do roteirista (.md) -> roteiro.txt (só a fala, para a decupagem comparar),
    ancoras.txt (MAPA DE ÂNCORAS + 1º FRAME + objetos de set, para o plano visual)."""
    import re
    if arq.suffix.lower() == ".docx":
        from docx import Document  # noqa: PLC0415
        texto = "\n".join(p.text for p in Document(str(arq)).paragraphs)
    else:
        texto = arq.read_text(encoding="utf-8")
    T.mkdir(parents=True, exist_ok=True)
    secoes = {m.group(1).strip().upper(): m.start() for m in re.finditer(r"^##\s+(.+)$", texto, re.M)}
    if not secoes:
        (T / "roteiro.txt").write_text(texto, encoding="utf-8")
        print("roteiro sem seções: tudo em roteiro.txt")
        return
    ordem = sorted(secoes.items(), key=lambda kv: kv[1])

    def secao(nome: str) -> str:
        for k, (titulo, ini) in enumerate(ordem):
            if titulo.startswith(nome):
                fim = ordem[k + 1][1] if k + 1 < len(ordem) else len(texto)
                return texto[ini:fim].split("\n", 1)[1].strip()
        return ""
    fala = secao("ROTEIRO FALADO")
    (T / "roteiro.txt").write_text(fala or texto, encoding="utf-8")
    anc = "\n\n".join(f"## {n}\n{secao(n)}" for n in ("1º FRAME", "MAPA DE ÂNCORAS", "OBJETOS DE SET") if secao(n))
    if anc:
        (T / "ancoras.txt").write_text(anc + "\n", encoding="utf-8")
    print(f"roteiro.txt ({len(fala.split())} palavras de fala)" + (" + ancoras.txt" if anc else ""))


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    a = sys.argv[2:]
    if cmd == "roteiro":
        separar_roteiro(Path(a[0]), Path(a[1]))
    elif cmd == "preparar":
        rc = etapa(NOVELA / "editar.py", ["preparar"] + a)
        sys.exit(rc)
    elif cmd == "montar":
        T = Path(a[0])
        corte = T / "corte.json"
        antes = corte.stat().st_mtime if corte.exists() else 0.0
        t0 = time.time()
        mc = subprocess.Popen([PY, str(NOVELA / "montar_corte.py"), str(T)], env=ENV)
        # o enquadramento só precisa do corte.json (gravado antes da retranscrição/alinhamento)
        while mc.poll() is None and not (corte.exists() and corte.stat().st_mtime > antes):
            time.sleep(0.3)
        rc_enq = 1
        if corte.exists() and corte.stat().st_mtime > antes:
            time.sleep(0.3)
            rc_enq = etapa(AQUI / "enquadrar_td.py", [str(T)])
        rc = mc.wait()
        print(f"   [montar (corte + enquadramento juntos): {time.time() - t0:.0f}s]", flush=True)
        if rc or rc_enq:
            sys.exit(1)
        if tem_roteiro(T):
            etapa(NOVELA / "roteiro.py", [str(T)])
        print(f"\nPRÓXIMO: plano visual em {T / 'plano.txt'} a partir de {T / 'palavras_legenda.txt'}")
    elif cmd == "plano":
        sys.exit(etapa(AQUI / "plano_td.py", a))
    elif cmd == "buscar":
        sys.exit(etapa(AQUI / "buscar_td.py", a))
    elif cmd == "escolher":
        sys.exit(etapa(AQUI / "buscar_td.py", a + ["--aplicar"]))
    elif cmd == "previa":
        T = Path(a[0])
        seg = a[1] if len(a) > 1 else None
        if etapa(AQUI / "legenda_td.py", [str(T)]):
            sys.exit(1)
        extra = ["--rapido"] + (["--ate", seg] if seg else [])
        sys.exit(etapa(AQUI / "render_td.py", [str(T), str(T / "previa.mp4")] + extra))
    elif cmd == "finalizar":
        T, saida = Path(a[0]), Path(a[1])
        if etapa(AQUI / "legenda_td.py", [str(T)]) or etapa(AQUI / "render_td.py", [str(T), str(saida)]):
            sys.exit(1)
        rc = etapa(AQUI / "conferir_td.py", [str(T), str(saida)] + (["--geral"] if "--geral" in a else []))
        if "--premiere" in a:
            etapa(AQUI / "premiere_td.py", [str(T), str(saida)])
        print("CONFERÊNCIA:", "APROVADA" if rc == 0 else "REPROVADA — ver qa/relatorio.txt")
        sys.exit(rc)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
