"""Modo rápido: um comando por etapa (o orquestrador só entra nas decisões de julgamento).

  python editar.py preparar  <video> <trabalho>      transcrição (GPU) + decupagem automática
                                                     (+ roteiro_x_fala.txt se houver roteiro)
      -> revisão curta: decupagem_proposta.txt (+ roteiro) -> decupagem_ajustes.txt
  python editar.py montar    <trabalho>              corte na voz + retranscrição + alinhamento
                                                     + enquadramento + palavras_legenda.txt
                                                     (+ corte x roteiro)
      -> legenda: o orquestrador escreve legenda.txt (formato compacto)
  python editar.py finalizar <trabalho> <saida.mp4>  legenda + render + conferência + folhas
      -> conferir saiu 0: olhar as folhas e entregar (revisor completo só se reprovar)

Roteiro: salve o texto em <trabalho>/roteiro.txt (ou .docx / .md) ANTES do preparar.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PY = sys.executable
ENV = {**os.environ, "PYTHONUTF8": "1"}


def etapa(nome: str, args: list[str]) -> int:
    t0 = time.time()
    r = subprocess.run([PY, str(AQUI / nome)] + args, env=ENV)
    print(f"   [{nome}: {time.time() - t0:.0f}s]", flush=True)
    return r.returncode


def tem_roteiro(t: Path) -> bool:
    return any((t / n).exists() for n in ("roteiro.txt", "roteiro.md", "roteiro.docx"))


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "preparar":
        video, trabalho = sys.argv[2], Path(sys.argv[3])
        trabalho.mkdir(parents=True, exist_ok=True)
        if etapa("transcrever.py", [video, str(trabalho)]) or etapa("decupar_auto.py", [str(trabalho)]):
            sys.exit(1)
        if tem_roteiro(trabalho):
            etapa("roteiro.py", [str(trabalho)])
        print(f"\nPRÓXIMO: revisão curta de {trabalho / 'decupagem_proposta.txt'}"
              + (f" + {trabalho / 'roteiro_x_fala.txt'}" if tem_roteiro(trabalho) else ""))
    elif cmd == "montar":
        trabalho = Path(sys.argv[2])
        corte = trabalho / "corte.json"
        antes = corte.stat().st_mtime if corte.exists() else 0.0
        t0 = time.time()
        mc = subprocess.Popen([PY, str(AQUI / "montar_corte.py"), str(trabalho)], env=ENV)
        # o enquadramento só precisa do corte.json, gravado ANTES da retranscrição e do alinhamento:
        # roda junto com eles (decodificação na NVDEC + rosto na CPU enquanto o CUDA faz o resto)
        while mc.poll() is None and not (corte.exists() and corte.stat().st_mtime > antes):
            time.sleep(0.3)
        rc_enq = 1
        if corte.exists() and corte.stat().st_mtime > antes:
            time.sleep(0.3)
            rc_enq = etapa("enquadrar.py", [str(trabalho)])
        rc_mc = mc.wait()
        print(f"   [montar (corte + enquadramento juntos): {time.time() - t0:.0f}s]", flush=True)
        if rc_mc or rc_enq:
            sys.exit(1)
        if tem_roteiro(trabalho):
            etapa("roteiro.py", [str(trabalho)])
        print(f"\nPRÓXIMO: legenda a partir de {trabalho / 'palavras_legenda.txt'}"
              + (f" + {trabalho / 'roteiro_x_fala.txt'}" if tem_roteiro(trabalho) else ""))
    elif cmd == "finalizar":
        trabalho, saida = Path(sys.argv[2]), Path(sys.argv[3])
        plano = trabalho / ("legenda.txt" if (trabalho / "legenda.txt").exists() else "legenda.json")
        # corte refeito depois da última medição do rosto (montar_corte --manter-palavras numa correção): mede o
        # queixo de novo no corte atual, mantendo o recorte aprovado — senão a legenda pode subir no rosto (13/10/2026)
        rosto, corte = trabalho / "rosto_corte.json", trabalho / "corte.json"
        if not rosto.exists() or rosto.stat().st_mtime < corte.stat().st_mtime:
            if etapa("enquadrar.py", [str(trabalho), "--so-rosto"]):
                sys.exit(1)
        if etapa("legenda_novela.py", ["--plano", str(plano), "--palavras", str(trabalho / "palavras_corte.json"),
                                       "--rosto", str(trabalho / "rosto_corte.json"), "--corte",
                                       str(trabalho / "corte.json"), "--out", str(trabalho / "legenda.ass"),
                                       "--layout-out", str(trabalho / "layout.json")]):
            sys.exit(1)
        if etapa("render_final.py", [str(trabalho), str(saida)]):
            sys.exit(1)
        rc = etapa("conferir.py", [str(trabalho), str(saida), "--whisper"])
        print(f"folhas: {trabalho / 'qa'} (folha_blocos_NN.jpg, folha_cta.jpg, fundo_mais_claro.png)")
        print("CONFERÊNCIA:", "APROVADA" if rc == 0 else "REPROVADA — ver qa/relatorio.json (chamar o revisor)")
        sys.exit(rc)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
