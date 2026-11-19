"""Cria as pastas de um tutorial novo a partir do molde da skill.

uso: python novo_tutorial.py <pasta_do_trabalho> [computador|celular|ambos]

Para cada versão cria:
  <pasta>/<versao>/modelo.html      (cópia do molde: telas, passos e câmera; é aqui que se edita)
  <pasta>/<versao>/k.json            (palavras-chave da narração -> índice; preencher depois da voz)
  <pasta>/<versao>/audio/            (voz_bruta.mp3, voz.wav, mix.json)
  <pasta>/<versao>/projeto/          (projeto HyperFrames: assets, hyperframes.json; index.html sai do montar.py)
"""
import json, os, shutil, sys

SK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pasta = os.path.abspath(sys.argv[1])
qual = sys.argv[2] if len(sys.argv) > 2 else "ambos"
versoes = ["computador", "celular"] if qual == "ambos" else [qual]
for v in versoes:
    d = os.path.join(pasta, v)
    if os.path.exists(os.path.join(d, "modelo.html")):
        sys.exit(f"{d} já tem modelo.html; escolha outra pasta")
    os.makedirs(os.path.join(d, "audio"), exist_ok=True)
    os.makedirs(os.path.join(d, "qa"), exist_ok=True)
    proj = os.path.join(d, "projeto")
    shutil.copytree(os.path.join(SK, "molde", "assets"), os.path.join(proj, "assets"), dirs_exist_ok=True)
    os.makedirs(os.path.join(proj, "renders"), exist_ok=True)
    shutil.copy(os.path.join(SK, "molde", "hyperframes.json"), proj)
    shutil.copy(os.path.join(SK, "molde", v, "modelo.html"), os.path.join(d, "modelo.html"))
    with open(os.path.join(SK, "exemplo", f"k_{v}.json"), encoding="utf-8") as f:
        k = json.load(f)
    with open(os.path.join(d, "k.json"), "w", encoding="utf-8") as f:
        json.dump(k, f, ensure_ascii=False, indent=1)
    print("ok", d)
