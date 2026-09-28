r"""Roteiro x fala: o que ele disse diferente do roteiro, o que ficou de fora, o que sobrou.

O roteiro é GUIA, não verdade: a legenda segue o que foi FALADO. Ele serve para
  - separar improviso (frase fluente diferente do roteiro: fica) de tropeço (recomeço
    quebrado: sai) e escolher entre tomadas;
  - achar trecho do roteiro sem nenhuma frase que FICA (tomada boa descartada?);
  - grafia de nomes/termos e destaques (palavras em MAIÚSCULAS ou *entre asteriscos*).
Toda diferença entre o corte e o roteiro vai para a entrega ("falou X | roteiro Y"); palavra
duvidosa que muda o sentido -> perguntar ao usuário (conferir antes com ctc_candidatos.py).

Entrada: <trabalho>/roteiro.txt (ou roteiro.md / roteiro.docx)
Uso: python roteiro.py <trabalho>        (o editar.py roda sozinho no preparar e no montar)
Saída: <trabalho>/roteiro_x_fala.txt
  1) com decupagem_frases.json: cada frase do bruto x roteiro, frase que FICA fora do roteiro
     e trecho do roteiro sem frase que FICA
  2) com palavras_corte.json: TROCOU / FALTOU / A MAIS palavra a palavra (@índice do corte) e
     os destaques sugeridos pelo roteiro
"""
from __future__ import annotations

import difflib
import html
import re
import sys
import unicodedata
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import ler_json  # noqa: E402


def norm(t: str) -> str:
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9%]", "", t)


def ler_roteiro(trabalho: Path) -> str:
    for nome in ("roteiro.txt", "roteiro.md"):
        if (trabalho / nome).exists():
            return (trabalho / nome).read_text(encoding="utf-8", errors="replace")
    if (trabalho / "roteiro.docx").exists():
        xml = zipfile.ZipFile(trabalho / "roteiro.docx").read("word/document.xml").decode("utf-8", "replace")
        return html.unescape(re.sub(r"<[^>]+>", "", re.sub(r"</w:p>", "\n", xml)))
    raise SystemExit(f"sem roteiro em {trabalho} (roteiro.txt, roteiro.md ou roteiro.docx)")


def tokens_roteiro(txt: str) -> list[dict]:
    out = []
    for ln in txt.splitlines():
        if ln.strip().startswith("#"):
            continue
        for m in re.finditer(r"\*[^*]+\*|\S+", ln):
            bruto = m.group(0)
            marcado = len(bruto) > 2 and bruto.startswith("*") and bruto.endswith("*")
            for w in bruto.strip("*").split():
                if not norm(w):
                    continue
                letras = re.sub(r"[^A-Za-zÀ-ÖØ-öø-ÿ]", "", w)
                out.append({"texto": w, "n": norm(w), "marcado": marcado,
                            "caixa_alta": len(letras) >= 2 and letras.isupper()})
    # roteiro todo em caixa-alta: maiúscula não marca destaque, só *asterisco*
    so_asterisco = sum(t["caixa_alta"] for t in out) > 0.4 * max(1, len(out))
    for t in out:
        t["destaque"] = t["marcado"] or (t["caixa_alta"] and not so_asterisco)
    return out


def frases_x_roteiro(trabalho: Path, rot: list[dict], linhas: list[str]) -> None:
    if not ((trabalho / "decupagem_frases.json").exists() and (trabalho / "transcricao.json").exists()):
        return
    pal = ler_json(trabalho / "transcricao.json")["palavras"]
    frases = ler_json(trabalho / "decupagem_frases.json")
    rn = [t["n"] for t in rot]
    coberto = [False] * len(rot)
    cobre_sai: dict[int, set] = {}
    linhas += ["# 1) frases do bruto x roteiro (cobre = % das palavras da frase que estão no roteiro)", ""]
    for n, f in enumerate(frases):
        a, b = f.get("i0_prop", f["i0"]), f.get("i1_prop", f["i1"])
        ws = pal[a:b + 1]
        fn = [norm(w["texto"]) for w in ws if norm(w["texto"])]
        if not fn:
            continue
        blocos = [m for m in difflib.SequenceMatcher(a=fn, b=rn, autojunk=False).get_matching_blocks()
                  if m.size >= 2]
        cob = sum(m.size for m in blocos) / len(fn)
        onde = f"roteiro {blocos[0].b}-{blocos[-1].b + blocos[-1].size - 1}" if blocos else "roteiro -"
        aviso = ""
        for m in blocos:
            for k in range(m.b, m.b + m.size):
                if f["estado"] == "FICA":
                    coberto[k] = True
                else:
                    cobre_sai.setdefault(k, set()).add(n)
        if f["estado"] == "FICA" and cob < 0.5:
            aviso = "  ⚠ fora do roteiro: improviso fluente fica; conversa/tropeço sai"
        txt = " ".join(w["texto"] for w in ws)
        linhas.append(f"{n:3d} {f['estado']:4s} cobre {cob:4.0%} {onde:18s} | {txt[:110]}{aviso}")
    linhas += ["", "# trechos do roteiro sem frase que FICA (tomada boa descartada? ele não gravou?)"]
    k, achou = 0, False
    while k < len(rot):
        if coberto[k]:
            k += 1
            continue
        k2 = k
        while k2 < len(rot) and not coberto[k2]:
            k2 += 1
        if k2 - k >= 3:
            sai = sorted(set().union(*(cobre_sai.get(j, set()) for j in range(k, k2))))
            dica = f"  -> aparece na(s) frase(s) SAI {', '.join(map(str, sai))}" if sai else "  -> não foi gravado?"
            linhas.append(f"  roteiro {k}-{k2 - 1}: \"{' '.join(t['texto'] for t in rot[k:k2])[:140]}\"{dica}")
            achou = True
        k = k2
    if not achou:
        linhas.append("  (nenhum: todo o roteiro está coberto por frases que ficam)")


def corte_x_roteiro(trabalho: Path, rot: list[dict], linhas: list[str]) -> None:
    if not (trabalho / "palavras_corte.json").exists():
        return
    pal = ler_json(trabalho / "palavras_corte.json")["palavras"]
    cn = [norm(w["texto"]) for w in pal]
    rn = [t["n"] for t in rot]
    sm = difflib.SequenceMatcher(a=rn, b=cn, autojunk=False)
    iguais = sum(m.size for m in sm.get_matching_blocks())
    linhas += ["", f"# 2) corte x roteiro: {iguais}/{len(rn)} palavras do roteiro batem com a fala "
                   f"({iguais / max(1, len(rn)):.0%}). A legenda segue a FALA; isto vai para a entrega.", ""]
    mapa = {}
    for op, a0, a1, b0, b1 in sm.get_opcodes():
        if op == "equal":
            for d in range(a1 - a0):
                mapa[a0 + d] = b0 + d
            continue
        r_txt = " ".join(t["texto"] for t in rot[a0:a1])
        c_txt = " ".join(w["texto"] for w in pal[b0:b1])
        if op == "replace":
            linhas.append(f"  TROCOU @{b0}: falou \"{c_txt}\" | roteiro \"{r_txt}\"")
        elif op == "delete":
            linhas.append(f"  FALTOU antes de @{b0}: roteiro \"{r_txt}\" não está no corte")
        else:
            linhas.append(f"  A MAIS @{b0}: falou \"{c_txt}\" (fora do roteiro)")
    dest = [f"{t['texto'].strip('*,.;:!?')} @{mapa[k]}" for k, t in enumerate(rot) if t["destaque"] and k in mapa]
    fora = [t["texto"] for k, t in enumerate(rot) if t["destaque"] and k not in mapa]
    linhas += ["", "# destaques sugeridos pelo roteiro (MAIÚSCULAS ou *asteriscos*), com o índice no corte:",
               "  " + (", ".join(dest) if dest else "(nenhum marcado)")]
    if fora:
        linhas.append("  marcados no roteiro, mas não falados assim: " + ", ".join(fora))


def main() -> None:
    trabalho = Path(sys.argv[1])
    rot = tokens_roteiro(ler_roteiro(trabalho))
    if not rot:
        raise SystemExit("roteiro vazio")
    linhas = [f"# roteiro x fala — roteiro com {len(rot)} palavras. O roteiro é GUIA: a legenda segue o que "
              "foi FALADO; diferença que muda o sentido -> perguntar ao usuário", ""]
    frases_x_roteiro(trabalho, rot, linhas)
    corte_x_roteiro(trabalho, rot, linhas)
    (trabalho / "roteiro_x_fala.txt").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"ok: {trabalho / 'roteiro_x_fala.txt'}")


if __name__ == "__main__":
    main()
