"""Acha tela de legenda que COMEÇA dentro de uma imagem `dividida` (posição alta, na emenda) e continua depois que a
dividida acaba — aí ela fica no meio do rosto do Clailton (Fim do Mundo v3/v4: "a legenda ficou no rosto: E TER UM
KIT"). Também avisa a tela que começa no Clailton e entra numa dividida.
uso: python legenda_no_rosto.py <trabalho>   -> lista; correção: termine a linha da dividida ANTES da 1ª palavra
dessa tela (ex.: @240-244 -> @240-243) ou estique a dividida até o fim dela."""
import json, sys
from pathlib import Path
T = Path(sys.argv[1])
tl = json.load(open(T / "timeline.json", encoding="utf-8"))
fps = tl["fps"]
div = [(c["f0"], c["f1"], c.get("i0"), c.get("i1")) for c in tl["camadas"] if c.get("layout") == "dividida"]
ab = tl.get("abertura") or {}
if ab:
    div.append((ab.get("f0", 0), ab.get("f1", 0), 0, ab.get("i1")))
ruins = 0
for lg in tl["legendas"]:
    for f0, f1, i0, i1 in div:
        dentro_ini = f0 <= lg["f0"] < f1
        dentro_fim = f0 < lg["f1"] <= f1
        if dentro_ini != dentro_fim and min(lg["f1"], f1) - max(lg["f0"], f0) > 0 or (lg["f0"] < f0 < lg["f1"]):
            ruins += 1
            print(f"{lg['f0'] / fps:7.2f}-{lg['f1'] / fps:6.2f}s  '{lg['texto']}' atravessa a dividida "
                  f"{f0 / fps:.2f}-{f1 / fps:.2f}s (palavras {i0}-{i1})")
print("ok: nenhuma legenda atravessa a emenda da dividida" if not ruins else f"{ruins} tela(s) para corrigir")
sys.exit(1 if ruins else 0)
