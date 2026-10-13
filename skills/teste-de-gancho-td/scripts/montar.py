"""Monta as variações de gancho: voz casada com o som do original -> config -> montagem -> conferência.

Uso: python montar.py <W> <nome> [<nome> ...]      (nome = <reel>_v2, <reel>_v3 ...)

Lê <W>/ganchos.json (plano), <W>/<reel>/medidas.json (medir_original.py), <W>/vozes/frases.json
(separar_falas.py / cortar_pausas.py), a boca sincronizada em <W>/ls/<nome>.mp4 e a voz em <W>/vozes/<nome>.wav.
Grava <W>/<reel>/<PAUTA com TESTE>_V2.mp4 e o _qa.jpg da conferência.

ganchos.json:
{
 "reels": {"chegada": {"pauta": "Reels_Clailton_TD_A_Pessoa_Que_Você_Quer_Na_Chegada",
                       "titulo": "A Pessoa Que Você Quer Na Chegada", "bruto": "G:/.../X.MP4"}},
 "variacoes": {
   "chegada_v2": {"texto": "Se você trabalha muito ...", "grande_final": false,
                  "imagens": [{"topo": 9.2, "ate": 5}, {"cheio": 5.1, "ate": 9},
                              {"foto": "img/casal.png", "ate": 12}, {"topo": 63.0}]}
 }
}
Imagens de cima, em ordem; cada uma vai até o início da palavra de índice "ate" (0 = 1ª palavra da fala;
veja os índices com `montar.py <W> --palavras <nome>`); a última vai até o fim do gancho:
  {"topo": s}   faixa de cima do próprio reel (sem a legenda antiga) a partir do segundo s do original
  {"cheio": s}  B-roll de tela cheia do reel (precisa de "cheio" nas medidas: medir_original.py cheio)
  {"foto": "img/x.png"}  imagem parada (desenho novo, foto), com zoom lento; caminho relativo a <W>/<reel>
  {"clip": "outro.mp4", "src": s, "y0": 0, "y1": 900}  qualquer trecho de vídeo (avançado)
"grande_final": true deixa a última palavra sozinha e grande (como o "VIVO" do Padre Antônio).
"""
import subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from comum import gravar_json, ler_json, lufs, pauta_teste  # noqa: E402

S = Path(__file__).parent
R = Path(sys.argv[1])
G = ler_json(R / "ganchos.json")
FR = ler_json(R / "vozes/frases.json", {})
if G is None:
    sys.exit(f"falta {R / 'ganchos.json'} (veja o formato no topo deste script)")

if len(sys.argv) > 3 and sys.argv[2] == "--palavras":
    for nome in sys.argv[3:]:
        print(nome, " ".join(f"[{k}]{w['p']}" for k, w in enumerate(FR[nome]["palavras"])))
    sys.exit()


def plano(nome, M):
    ws, D = FR[nome]["palavras"], FR[nome]["dur"]
    ims = G["variacoes"][nome]["imagens"]
    out, ini = [], 0.0
    for k, im in enumerate(ims):
        if "ate" in im:
            fim = ws[im["ate"]]["i"]
        elif k == len(ims) - 1:
            fim = D
        else:
            sys.exit(f"{nome}: imagem {k + 1} sem 'ate' (só a última pode ficar sem)")
        if "topo" in im:
            d = dict(clip=M["original"], src=im["topo"], y0=0, y1=M["topo_y1"])
        elif "cheio" in im:
            if not M.get("cheio"):
                sys.exit(f"{nome}: falta medir o B-roll de tela cheia (medir_original.py cheio <pasta> <t>)")
            d = dict(clip=M["original"], src=im["cheio"], y0=M["cheio"][0], y1=M["cheio"][1])
        elif "foto" in im:
            d = dict(arq=im["foto"])
        else:
            d = {k2: v for k2, v in im.items() if k2 != "ate"}
        d.update(ini=round(ini, 3), fim=round(fim, 3))
        out.append(d)
        ini = fim
    return out


def legendas(nome, grande_final=False):
    """Telas de até 4 palavras / 16 letras (como nos originais: "CUIDADO PARA NÃO"), quebra em pontuação;
    cada tela fica até a próxima."""
    ws = []
    for w in FR[nome]["palavras"]:          # junta pedaços que o transcritor separa ("segunda" + "-feira?")
        if w["p"].startswith("-") and ws:
            ws[-1] = dict(ws[-1], p=ws[-1]["p"] + w["p"], f=w["f"])
        else:
            ws.append(dict(w))
    grupos, g = [], []
    for k, w in enumerate(ws):
        g.append(w)
        txt = " ".join(x["p"] for x in g)
        prox = ws[k + 1]["p"] if k + 1 < len(ws) else ""
        if w["p"][-1] in ",.?!" or len(g) == 4 or len(txt + " " + prox) > 16:
            grupos.append(g)
            g = []
    if g:
        grupos.append(g)
    if grande_final and len(grupos[-1]) > 1:   # palavra final sozinha e grande
        grupos.append([grupos[-1].pop()])
    out = []
    for k, g in enumerate(grupos):
        ini = 0.0 if k == 0 else g[0]["i"]
        fim = grupos[k + 1][0]["i"] if k + 1 < len(grupos) else FR[nome]["dur"]
        out.append(dict(txt=" ".join(x["p"] for x in g), ini=round(ini, 3), fim=round(fim, 3)))
    if grande_final:
        out[-1]["grande"] = True
    return out


def py():
    return sys.executable


for nome in sys.argv[2:]:
    reel, v = nome.rsplit("_", 1)
    M = ler_json(R / reel / "medidas.json")
    if M is None:
        sys.exit(f"falta {R / reel / 'medidas.json'} (medir_original.py medir)")
    info, var = G["reels"][reel], G["variacoes"][nome]
    cfg = {k: M[k] for k in ("original", "corte_quadro", "emenda", "cap_y", "cap_px", "flash_quadros", "rosto")}
    if M.get("sfx_fim"):
        cfg["sfx_fim"] = M["sfx_fim"]
    cfg.update(avatar=f"../ls/{nome}.mp4", avatar_ini=0.0, avatar_fim=FR[nome]["dur"],
               ganho_db=round(M["alvo_lufs"] - lufs(R / f"vozes/{nome}.wav"), 1),
               imagens=plano(nome, M), legendas=legendas(nome, var.get("grande_final", False)),
               saida=f"{pauta_teste(info['pauta'])}_{v.upper()}.mp4")
    casada = R / "vozes" / f"{nome}_casada.wav"
    r = subprocess.run([py(), str(S / "casar_voz.py"), str(R / f"vozes/{nome}.wav"), str(R / reel / M["original"]),
                        str(M["corte_quadro"]), str(casada)], capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    print(r.stdout.strip(), r.stderr.strip()[-800:])
    if r.returncode:
        sys.exit(f"{nome}: casar_voz falhou")
    cfg["voz"] = f"../vozes/{nome}_casada.wav"
    arq = R / reel / f"{nome}.json"
    gravar_json(arq, cfg)
    print(nome, "| telas:", " / ".join(l["txt"] for l in cfg["legendas"]))
    for s in ("montar_gancho.py", "conferir.py"):
        r = subprocess.run([py(), str(S / s), str(arq)], capture_output=True, text=True, encoding="utf-8",
                           errors="replace")
        print(r.stdout.strip(), r.stderr.strip()[-1500:])
        if r.returncode:
            sys.exit(f"{nome}: {s} falhou")
