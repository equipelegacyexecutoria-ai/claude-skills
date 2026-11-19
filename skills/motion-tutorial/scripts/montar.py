"""Monta <versao>/projeto/index.html a partir do modelo.html + tempos da narração.

uso: python montar.py <pasta_da_versao>     (ex.: .../Meu_Tutorial/computador)

Lê:
  audio/voz.wav.tx.json   ({TX, TT} gerado pelo palavras_js.py da skill motion-legacy, com --inicio 0.25)
  k.json                  {"K": {"chave": índice_da_palavra, ...},
                           "remover": [[de, ate], ...]   (opcional: palavras inventadas pelo Whisper, índices da lista original),
                           "duracao": 79                  (opcional; sem ela = última palavra + 3 s)}
Troca __TX__, __TT__, __K__ e __DUR__ do modelo e grava projeto/index.html.
Confira a lista de palavras impressa: o Whisper às vezes inventa frase numa pausa (aconteceu duas vezes no tutorial
das aulas). Ouça o trecho isolado (scripts/checa_cortes.py ou transcrição só daquele pedaço) antes de mudar a voz.
"""
import io, json, os, sys

d = os.path.abspath(sys.argv[1])
tx = json.load(io.open(os.path.join(d, "audio", "voz.wav.tx.json"), encoding="utf-8"))
TX, TT = tx["TX"], tx["TT"]
cfg = json.load(io.open(os.path.join(d, "k.json"), encoding="utf-8"))
for a, b in sorted(cfg.get("remover", []), reverse=True):
    del TX[a:b + 1]
    del TT[a:b + 1]
K = cfg["K"]
falta = [k for k, i in K.items() if i is None or i >= len(TX)]
if falta:
    sys.exit("chaves sem palavra: " + ", ".join(falta))
dur = float(cfg.get("duracao") or round(TT[-1] + 3.0))
print(" ".join(f"{k}={TX[i]}@{TT[i]:.2f}" for k, i in K.items()))
s = io.open(os.path.join(d, "modelo.html"), encoding="utf-8").read()
s = (s.replace("__TX__", json.dumps(TX, ensure_ascii=False)).replace("__TT__", json.dumps(TT))
      .replace("__K__", json.dumps(K)).replace("__DUR__", f"{dur:g}"))
io.open(os.path.join(d, "projeto", "index.html"), "w", encoding="utf-8").write(s)
print("ok", len(TX), "palavras,", dur, "s")
