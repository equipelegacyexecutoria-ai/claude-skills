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


# Pausa justa (usuário, 09/10/2026: "pausa extensa sem conexão"; a pausa natural é só da novela). O corte mede a
# voz pelo volume e fôlego/ruído de boca colado na fala passa como voz; o ALINHAMENTO das palavras é preciso
# (~1 quadro): todo silêncio entre palavras maior que GAP_MAX vira silêncio forçado e o corte é refeito.
GAP_MAX = 0.40          # s: maior silêncio aceito entre duas palavras
FOLGA_PALAVRA = 0.06    # s: o que fica de cada lado da palavra (a cauda da vogal o corte acha sozinho)
PASSADAS_APERTAR = 2
FALA_MIN = 0.12         # s de palavra do bruto dentro do "silêncio" = é fala que o Whisper do corte perdeu


def _energia_db(T: Path):
    """Palavras faladas do bruto (transcricao.json, s do bruto): [(inicio, fim)]; None se não houver."""
    import json
    arq = T / "transcricao.json"
    if not arq.exists():
        return None
    pal = json.loads(arq.read_text(encoding="utf-8"))
    pal = pal["palavras"] if isinstance(pal, dict) else pal
    return [(w["inicio"], w["fim"]) for w in pal if not w.get("sem_voz")]


def _tem_voz(som, p: float, q: float) -> bool:
    """O trecho [p, q] do bruto contém palavra transcrita (fôlego e ruído não contam)?"""
    if not som:
        return False
    return any(min(q, b) - max(p, a) >= FALA_MIN for a, b in som)


def apertar(T: Path) -> int:
    """Grava em T/apertar.json (s do bruto) os silêncios longos entre palavras do corte. Devolve quantos novos."""
    import json
    pal = json.loads((T / "palavras_corte.json").read_text(encoding="utf-8"))
    pal = pal["palavras"] if isinstance(pal, dict) else pal
    segs = json.loads((T / "corte.json").read_text(encoding="utf-8"))["segmentos"]
    arq = T / "apertar.json"
    sil = json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else []

    def src(w: dict, t: float) -> tuple[dict, float]:
        s = segs[w["seg"]]
        return s, s["src_in"] + (t - s["dst_in"])

    novos = []
    for w, w1 in zip(pal, pal[1:]):
        if w1["inicio"] - w["fim"] <= GAP_MAX:
            continue
        s, fim = src(w, w["fim"])
        s1, ini = src(w1, w1["inicio"])
        if s is s1:
            novos.append([fim + FOLGA_PALAVRA, ini - FOLGA_PALAVRA])
        else:                                     # silêncio dividido pela emenda: rabo de um, cabeça do outro
            if s["src_out"] - fim > 2 * FOLGA_PALAVRA:
                novos.append([fim + FOLGA_PALAVRA, s["src_out"] + 0.05])
            if ini - s1["src_in"] > 2 * FOLGA_PALAVRA:
                novos.append([s1["src_in"] - 0.05, ini - FOLGA_PALAVRA])
    # só aperta o que é silêncio DE VERDADE: quando o Whisper do corte "perde" palavras (16/10/2026, 0800 Salão:
    # "não sei aonde" e o "DRE" sumiram), o buraco parecia pausa e a fala real era cortada.
    som = _energia_db(T)
    novos = [[round(p, 3), round(q, 3)] for p, q in novos if q - p > 0.05 and [round(p, 3), round(q, 3)] not in sil
             and not _tem_voz(som, p, q)]
    if novos:
        arq.write_text(json.dumps(sil + novos), encoding="utf-8")
        print(f"   pausa justa: {len(novos)} silêncio(s) acima de {GAP_MAX:.2f}s entre palavras -> corte refeito", flush=True)
    return len(novos)


def emendas(T: Path) -> int:
    """Palavra repetida colada na emenda ("E... e você sabe"): o Whisper engole gaguejo e o corte emenda
    os dois pedaços. Transcrição literal de cada emenda (skill novela) + ajuste de decupagem sugerido."""
    rc = etapa(NOVELA / "emendas_literal.py", [str(T)])
    if rc:
        print(f"\n⚠ REPETIÇÃO NA EMENDA: leia {T / 'emendas_literal.txt'}, junte o ajuste sugerido ao "
              "decupagem_ajustes.txt, --aplicar e rode o montar de novo (intencional -> repeticoes_ok.txt)")
    return rc


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
        (T / "apertar.json").unlink(missing_ok=True)
        for passada in range(1, PASSADAS_APERTAR + 2):
            antes = corte.stat().st_mtime if corte.exists() else 0.0
            t0 = time.time()
            mc = subprocess.Popen([PY, str(NOVELA / "montar_corte.py"), str(T), "--ritmo-justo"], env=ENV)
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
            if passada > PASSADAS_APERTAR or not apertar(T):
                break
        if tem_roteiro(T):
            etapa(NOVELA / "roteiro.py", [str(T)])
        emendas(T)
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
        if emendas(T):                                   # repetição na emenda reprova antes do render
            sys.exit(3)
        if etapa(AQUI / "legenda_td.py", [str(T)]) or etapa(AQUI / "render_td.py", [str(T), str(saida)]):
            sys.exit(1)
        rc = etapa(AQUI / "conferir_td.py", [str(T), str(saida)] + (["--geral"] if "--geral" in a else []))
        etapa(AQUI / "olhos_qa.py", [str(T), str(saida)])   # olhos na mesma altura nas trocas de zoom
        try:                                                # cenas do acervo usadas (para não repetir)
            sys.path.insert(0, str(AQUI))
            import acervo_td
            acervo_td.registrar_uso(T, saida.stem)
        except Exception as e:  # noqa: BLE001
            print(f"   (registro de uso do acervo falhou: {e!r})"[:160])
        if "--premiere" in a:
            etapa(AQUI / "premiere_td.py", [str(T), str(saida)])
        print("CONFERÊNCIA:", "APROVADA" if rc == 0 else "REPROVADA — ver qa/relatorio.txt")
        sys.exit(rc)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
