"""CTA final dos NV_CTA no estilo da skill motion-legacy (pedido do Igor, 16/11/2026).
Fundo claro com azul, letreiro palavra a palavra no tempo da voz do Clailton, cena do tema (cartão/plataforma),
câmera viaja até o fecho: chip "link na bio", botão clicado pelo cursor, logo Legacy Executoria e assinatura.

  python gerar.py <slug> [--render]
Projeto em <trabalho>/cta_legacy/ ; motion.json com início, duração e efeitos (para compor.py).
"""
import json, shutil, subprocess, sys
from pathlib import Path

B = Path(r"C:\Render\_trabalho")
SKILL = Path.home() / ".claude/skills/motion-legacy"
SEGURA = 2.0   # fecho parado depois da última palavra

# grupos: (topo_px, linhas, saida) ; palavra = [indice, classes, texto_opcional]; saida None = fica até o fim
SPEC = {
 "Reels_Clailton_NV_CTA_Por_Que_Voce_Nao_Cumpre_Suas_Metas": dict(
    ini=293,
    grupos=[
        (330, [[[293, "sm dim"], [294, "sm dim"], [295, "sm dim"], [296, "sm dim"]], [[297], [298, "big hl"]], [[299, "sm dim"], [300], [301, "big"]]], 302),
        (330, [[[302, "", "a bater"], [303, "big hl"]], [[304, "dim"], [305, "xl"]]], 306),
        (330, [[[306, "big"], [307, "big dim"]], [[308, "big hl"], [309, "big"], [310, "big", "bio."]]], None),
    ],
    cena="metas", bater=302, ok=305, viagem=306, tap=308,
    botao=("🎯 Quero bater as metas", "✓ Vamos juntos")),
 "Reels_Clailton_NV_CTA_Quem_Tem_Um_Negocio_Tem_Mais_Fe": dict(
    ini=226,
    grupos=[
        (330, [[[226, "sm dim"], [227, "sm dim"], [228, "sm dim"]], [[229, "xl hl"]], [[230, "sm dim"], [231], [232, "big"]]], 233),
        (330, [[[233, "sm dim"], [234, "sm dim"], [235, "sm dim"], [236, "big hl"]], [[237, "sm dim"], [238, "sm dim", "torná-lo"]], [[240], [241, "big", "grandioso"]]], 242),
        (330, [[[242, "big"], [243, "big dim"]], [[244, "big hl"], [245, "big"], [246, "big", "bio"]]], 247),
        (330, [[[247, "sm dim"], [248, "sm dim"], [249, "sm dim"]], [[250, "big hl"]], [[251, "sm dim"], [252, "sm dim"], [253, "big"]]], 254),
        (330, [[[254, "sm dim"], [255], [256, "sm dim"], [257, "sm dim"]], [[258, "xl hl", "fé"]], [[259, "sm dim"], [260, "sm dim"], [261, "", "extraordinária."]]], None),
    ],
    cena="crescer", ajuda=236, grande=241, ok=241, viagem=242, tap=244, logo=254,
    botao=("🚀 Quero algo grandioso", "✓ Vamos juntos")),
 "Reels_Clailton_NV_CTA_Nao_Deixam_De_Comprar_Pelo_Preco": dict(
    ini=292,
    grupos=[
        (330, [[[292, "sm dim"], [293, "sm dim"], [294, "sm dim"], [295, "sm dim"]], [[296, "sm dim"], [297, "big"], [298, "big hl"]]], 299),
        (330, [[[299, "sm dim"], [300, "big"]], [[301, "xl hl", "mais"]]], 302),
        (330, [[[302, "big"], [303, "big dim"]], [[304, "sm dim"], [305, "sm dim"], [306, "big hl"], [307, "big"], [308, "big", "bio."]]], None),
    ],
    cena="caixa", linhas=[("Vendas · este mês", 180, 420, "mil", 297, "▲ +133%"), ("Lucro no caixa", 12, 96, "mil", 300, "▲ 8x")],
    ok=300, viagem=302, tap=306,
    botao=("💰 Quero vender mais", "✓ Vamos juntos")),
 "Reels_Clailton_NV_CTA_O_Nadador_Que_Olhou_Para_Phelps": dict(
    ini=310,
    grupos=[
        (330, [[[310, "sm dim"], [311, "sm dim"], [312, "sm dim"], [313, "sm dim"]], [[314, "sm dim"], [315, "big"], [316, "big hl", "mais"]]], 317),
        (330, [[[317, "big"], [318, "xl hl", "mais"]]], 319),
        (330, [[[319, "sm dim"], [320], [321, "sm dim"]], [[322, "big hl"]], [[323, "sm dim"], [324, "big"]]], 325),
        (330, [[[325, "sm dim"], [326, "sm dim"], [327, "big", "cliente"]], [[328, "sm dim"], [329, "sm dim"], [330, "sm dim"], [331, "sm dim"], [332, "sm dim"]], [[333, "big", "vende"]]], 334),
        (330, [[[334, "big"], [335, "big dim"]], [[336, "sm dim"], [337], [338, "dim"]], [[339, "big hl"], [340, "big"], [341, "big", "bio."]]], None),
    ],
    cena="caixa", linhas=[("Vendas · este mês", 180, 420, "mil", 315, "▲ +133%"), ("Lucro no caixa", 12, 96, "mil", 317, "▲ 8x"),
                          ("Ticket médio · valor percebido", 1900, 3400, "rs", 322, "▲ +79%")],
    ok=324, viagem=334, tap=339,
    botao=("💰 Quero vender mais", "✓ Vamos juntos")),
}

CENA_METAS = """
  <div id="s1" class="cena palco">
    <div id="win1" class="win p3" style="left:100px; top:730px; width:760px; height:640px;">
      <div class="side"><img src="assets/img/plan_logo.svg"/><div class="it on" style="top:110px"></div><div class="it" style="top:160px"></div><div class="it" style="top:210px"></div></div>
      <div class="topo"><div class="t">PAINEL DE METAS</div></div>
      <div class="corpo"><div class="h1">Metas do mês</div><div class="h2">Cada meta com um responsável</div>
        ROWS
      </div>
    </div>
  </div>"""
METAS = [("Faturamento", "R$ 1,2 mi no mês", 38, "AL"), ("Novos clientes", "40 contratos", 55, "RM"), ("Margem", "22% de lucro", 30, "JP")]
ROW = """<div class="card meta" id="mt{k}" style="top:{top}px"><div class="n">{n}</div><div class="o">{o}</div>
          <div class="trilho"><div class="ench" id="en{k}"></div></div><div class="pct" id="pc{k}">{p}%</div>
          <div class="qav" style="position:absolute; right:24px; top:38px; background:#e3edff; color:#2f7bff; font-size:26px;">{av}</div></div>"""

CSS_EXTRA = """
.meta { left:22px; width:640px; height:150px; }
.meta .trilho { width:300px; }
.meta .pct { left:340px; }
#cur3 { left:0; top:0; }
#tag .w.hl { padding:0 16px; }
"""

FECHO = """
  <div id="s2" class="cena palco">
    <div id="bio" class="abs chipv" style="left:400px; top:700px; background:#fff; color:#0a1a33; font-size:26px; box-shadow:0 14px 34px rgba(20,50,110,.18);">🔗 link na bio</div>
    <div id="botao" class="p3" style="top:790px;"><span id="bt-tx">BT0</span></div>
    <svg id="cur3" class="cursor" viewBox="0 0 58 70"><path d="M4 4 L4 56 L18 44 L28 66 L38 61 L28 40 L50 40 Z" fill="#2f7bff" stroke="#fff" stroke-width="4" stroke-linejoin="round"/></svg>
    <img id="logo-fim" src="assets/img/logo_navy.svg" style="left:290px; top:1010px; width:500px;" />
    <div id="tag" style="top:1180px; font-size:42px;"><span>Enquanto todo mundo ensina,</span><br/><span>a gente </span><span class="w hl" style="font-size:56px; margin:0;"><span class="marca"></span><span class="tx">executa.</span></span></div>
  </div>"""


def cena_metas(sp, t, via):
    bat, ok = t(sp["bater"]), t(sp["ok"])
    rows = "".join(ROW.format(k=k, top=100 + 160 * k, n=n, o=o, p=p, av=av) for k, (n, o, p, av) in enumerate(METAS))
    html = CENA_METAS.replace("ROWS", rows)
    js = ['mostra("#win1", 0.4, { z: -900, rotationX: 38, rotationY: -18, filter: "blur(18px)" }, 0.9);',
          f'tl.to("#win1", {{ rotationY: 6, rotationX: 4, duration: {via:.2f}, ease: "sine.inOut" }}, 1.3);']
    for k, (_, _, p, _) in enumerate(METAS):
        js.append(f'tl.set("#en{k}", {{ scaleX: {p / 100} }}, 0);')
        js.append(f'mostra("#mt{k}", {0.75 + 0.12 * k:.2f}, {{ y: 40, filter: "blur(10px)" }}, 0.5);')
        js.append(f'tl.to("#en{k}", {{ scaleX: 1, duration: 0.8, ease: "power2.inOut" }}, {bat + 0.15 * k:.3f});')
        js.append(f'contar($("#pc{k}"), {p}, 100, {bat + 0.15 * k:.3f}, 0.8, (v) => Math.round(v) + "%", "power2.inOut");')
        js.append(f'tl.to("#en{k}", {{ background: "#10b981", duration: 0.2 }}, {ok + 0.08 * k:.3f});')
        js.append(f'tl.to("#pc{k}", {{ color: "#10b981", duration: 0.2 }}, {ok + 0.08 * k:.3f});')
    return html, js


FMT = {"mil": '(v) => "R$ " + br(v) + " mil"', "rs": '(v) => "R$ " + br(v)'}


def cena_caixa(sp, t, via):
    """cartão de vidro com linhas (vendas, lucro, ticket) que sobem na palavra falada"""
    L = sp["linhas"]
    h = 120 + 170 * len(L)
    top = 1440 - h if 1440 - h < 760 else 760
    rows, js = "", [f'mostra("#c-cx", 0.4, {{ y: 260, z: -500, rotationX: 48, scale: 0.8, filter: "blur(20px)" }}, 0.8);',
                    f'tl.to("#c-cx", {{ rotationY: 6, rotationX: 4, duration: {via:.2f}, ease: "sine.inOut" }}, 1.3);']
    for k, (rot, de, ate, fmt, i, chip) in enumerate(L):
        y = 40 + 170 * k
        rows += (f'<div class="abs rot" style="left:44px; top:{y}px;">{rot}</div>'
                 f'<div id="cn{k}" class="abs num" style="left:40px; top:{y + 30}px; font-size:68px;"></div>'
                 f'<div id="cc{k}" class="abs chipv" style="right:40px; top:{y + 44}px; background:#e8f7ef; color:#047857;">{chip}</div>'
                 f'<div class="abs" style="left:44px; top:{y + 124}px; width:672px; height:16px; border-radius:8px; background:#eef1f6; overflow:hidden;">'
                 f'<div id="cb{k}" style="position:absolute; inset:0; border-radius:8px; background:linear-gradient(90deg,#2f7bff,#5aa9ff); transform-origin:0 50%;"></div></div>')
        ti = t(i)
        js += [f'contar($("#cn{k}"), {de}, {de}, 0, 0.01, {FMT[fmt]});',
               f'tl.set("#cb{k}", {{ scaleX: {0.92 * de / ate:.3f} }}, 0); tl.set("#cc{k}", {{ autoAlpha: 0 }}, 0);',
               f'contar($("#cn{k}"), {de}, {ate}, {ti:.3f}, 0.9, {FMT[fmt]});',
               f'tl.to("#cb{k}", {{ scaleX: 0.92, duration: 0.9, ease: "power2.out" }}, {ti:.3f});',
               f'mostra("#cc{k}", {ti + 0.6:.3f}, {{ scale: 0.6, y: 10 }}, 0.4);']
    html = f'\n  <div id="s1" class="cena palco"><div id="c-cx" class="vidro p3" style="left:110px; top:{top}px; width:760px; height:{h}px;">{rows}</div></div>'
    return html, js


def cena_crescer(sp, t, via):
    """faturamento do negócio: barras dos meses crescem e o número conta até o valor grande"""
    a, g = t(sp["ajuda"]), t(sp["grande"])
    meses = ["JUN", "JUL", "AGO", "SET", "OUT", "NOV"]
    h0 = [60, 72, 66, 84, 92, 104]
    h1 = [80, 96, 104, 120, 136, 150]
    h2 = [110, 150, 190, 245, 310, 380]
    bars = "".join(f'<div id="bc{k}" class="abs" style="left:{60 + 112 * k}px; bottom:70px; width:76px; height:400px; border-radius:14px 14px 4px 4px;'
                   f' background:linear-gradient(180deg,#5aa9ff,#2f7bff); transform-origin:50% 100%;"></div>'
                   f'<div class="abs" style="left:{48 + 112 * k}px; bottom:26px; width:100px; text-align:center; font-weight:700; font-size:20px; letter-spacing:2px; color:#94a3b8;">{m}</div>'
                   for k, m in enumerate(meses))
    html = ('\n  <div id="s1" class="cena palco"><div id="c-cx" class="vidro p3" style="left:110px; top:740px; width:760px; height:640px;">'
            '<div class="abs rot" style="left:44px; top:40px;">Teu negócio · faturamento</div>'
            '<div id="cn0" class="abs num" style="left:40px; top:72px; font-size:96px;"></div>'
            '<div id="cc0" class="abs chipv" style="right:40px; top:52px; background:#e8f7ef; color:#047857;">▲ 3,6x</div>'
            f'{bars}</div></div>')
    fmt = '(v) => "R$ " + (v / 1000).toFixed(1).replace(".", ",") + " mi"'
    js = ['mostra("#c-cx", 0.4, { y: 260, z: -500, rotationX: 48, scale: 0.8, filter: "blur(20px)" }, 0.8);',
          f'tl.to("#c-cx", {{ rotationY: 6, rotationX: 4, duration: {via:.2f}, ease: "sine.inOut" }}, 1.3);',
          f'contar($("#cn0"), 0, 0, 0, 0.01, {fmt});', 'tl.set("#cc0", { autoAlpha: 0 }, 0);',
          f'contar($("#cn0"), 0, 480, 0.9, 0.9, {fmt});',
          f'contar($("#cn0"), 480, 690, {a:.3f}, 0.8, {fmt});',
          f'contar($("#cn0"), 690, 2400, {g:.3f}, 1.0, {fmt});',
          f'mostra("#cc0", {g + 0.7:.3f}, {{ scale: 0.6, y: 10 }}, 0.4);']
    for k in range(6):
        js += [f'tl.fromTo("#bc{k}", {{ scaleY: 0 }}, {{ scaleY: {h0[k] / 400:.3f}, duration: 0.6, ease: "expo.out" }}, {0.9 + 0.06 * k:.2f});',
               f'tl.to("#bc{k}", {{ scaleY: {h1[k] / 400:.3f}, duration: 0.6, ease: "power2.out" }}, {a + 0.05 * k:.3f});',
               f'tl.to("#bc{k}", {{ scaleY: {h2[k] / 400:.3f}, duration: 0.9, ease: "power3.out" }}, {g + 0.06 * k:.3f});']
    return html, js


CENAS = {"metas": cena_metas, "caixa": cena_caixa, "crescer": cena_crescer}


def main():
    slug = sys.argv[1]
    sp = SPEC[slug]
    T = B / slug
    P = T / "cta_legacy"
    if P.exists():   # refazendo: só volta o index.html do molde (as fontes ficam travadas para apagar no Windows)
        shutil.copyfile(SKILL / "molde/index.html", P / "index.html")
    else:
        subprocess.run([sys.executable, str(SKILL / "scripts/novo_projeto.py"), str(P), "8"], check=True)
    w = json.load(open(T / "palavras_corte.json", encoding="utf-8"))["palavras"]
    fim_fala = json.load(open(T / "corte.json", encoding="utf-8"))["duracao_fala"]
    O = round(w[sp["ini"]]["inicio"] - 0.12, 3)
    D = round(fim_fala + SEGURA - O, 3)
    t = lambda i: round(w[i]["inicio"] - O, 3)  # noqa: E731
    TX = [x.get("palavra") or x.get("texto") for x in w]
    TT = [round(x["inicio"] - O, 3) for x in w]

    js = []
    for top, linhas, saida in sp["grupos"]:
        sai = t(saida) if saida is not None else 99
        js.append(f"grupo({top}, {json.dumps(linhas, ensure_ascii=False)}, {sai});")
    ok, via, tap = t(sp["ok"]), t(sp["viagem"]), t(sp["tap"]) + 0.15
    # cena do tema
    html, jsc = CENAS[sp["cena"]](sp, t, via)
    js += jsc
    # fecho
    b0, b1 = sp["botao"]
    html += FECHO.replace("BT0", b0)
    # logo entra logo depois da última palavra (ou numa palavra escolhida, quando a fala depois do clique é longa)
    fx = round(t(sp["logo"]) if sp.get("logo") else fim_fala - O + 0.15, 3)
    js.append('tl.set(["#bio", "#botao", "#cur3", "#logo-fim", "#tag"], { autoAlpha: 0 }, 0);')
    js.append(f'mostra("#botao", {via - 0.05:.3f}, {{ z: -600, y: 200, rotationX: 40, filter: "blur(16px)" }}, 0.7);')
    js.append(f'mostra("#bio", {via + 0.25:.3f}, {{ y: 40, scale: 0.8 }}, 0.5);')
    js.append('tl.set("#cur3", { x: 880, y: 1150 }, 0);')
    js.append(f'tl.to("#curT", {{ autoAlpha: 0, duration: 0.1 }}, {tap - 0.5:.3f});')   # some a setinha da viagem
    js.append(f'tl.to("#cur3", {{ autoAlpha: 1, duration: 0.2 }}, {tap - 0.45:.3f});')
    js.append(f'tl.to("#cur3", {{ x: 640, y: 890, duration: 0.42, ease: "power3.out" }}, {tap - 0.45:.3f});')
    js.append(f'tl.to("#cur3", {{ scale: 0.82, duration: 0.08, yoyo: true, repeat: 1 }}, {tap:.3f});')
    js.append(f'tl.to("#botao", {{ scale: 0.94, duration: 0.08, yoyo: true, repeat: 1 }}, {tap:.3f});')
    js.append(f'(function () {{ const b = $("#bt-tx"); const o = {{ v: 0 }}; tl.fromTo(o, {{ v: 0 }}, {{ v: 1, duration: 0.01, onUpdate: () => {{ b.textContent = o.v >= 1 ? {json.dumps(b1, ensure_ascii=False)} : {json.dumps(b0, ensure_ascii=False)}; }} }}, {tap + 0.25:.3f}); }})();')
    js.append(f'tl.to("#botao", {{ background: "linear-gradient(110deg,#10b981,#34d399)", boxShadow: "0 30px 70px rgba(16,185,129,.4)", duration: 0.25 }}, {tap + 0.25:.3f});')
    js.append(f'tl.to("#cur3", {{ autoAlpha: 0, duration: 0.25 }}, {tap + 0.6:.3f});')
    js.append(f'mostra("#logo-fim", {fx:.3f}, {{ y: 60, scale: 0.9, filter: "blur(14px)" }}, 0.8);')
    js.append(f'mostra("#tag", {fx + 0.4:.3f}, {{ y: 40, filter: "blur(10px)" }}, 0.7);')
    js.append(f'tl.fromTo("#tag .marca", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.35, ease: "power3.out" }}, {fx + 0.8:.3f});')
    js.append(f'tl.fromTo("#tag .tx", {{ color: "#0a1a33" }}, {{ color: "#ffffff", duration: 0.2 }}, {fx + 0.85:.3f});')
    # flash branco na passagem da novela para a animação
    js.append('tl.fromTo("#flash", { opacity: 1 }, { opacity: 0, duration: 0.25, ease: "power1.out", immediateRender: false }, 0);')
    cam = f"""chega({ok:.3f}, 1.06, 0.5, 0, 150, 0.3);
    viagem({via - 0.2:.3f}, "s2", 0.55);
    chega({fx + 0.2:.3f}, 1.04, 1.2, 0, 0, 0);"""

    p = P / "index.html"
    s = p.read_text(encoding="utf-8")
    a = s.index('<div id="lente"><div id="camera">') + len('<div id="lente"><div id="camera">')
    b = s.index("  </div></div>\n\n  <div id=\"lente2\">")
    s = s[:a] + "\n" + html + "\n" + s[b:]
    s = s.replace("</style>", CSS_EXTRA + "</style>", 1)
    s = s.replace('  <audio id="mix" src="assets/audio/mix.wav" data-start="0" data-duration="8" data-track-index="40"></audio>\n', "")
    s = s.replace('const TX = ["Sua","empresa","fatura,"];', "const TX = " + json.dumps(TX, ensure_ascii=False) + ";")
    s = s.replace("const TT = [0.25,0.43,0.71];", "const TT = " + json.dumps(TT) + ";")
    a = s.index("  // ======== CENAS")
    b = s.index("  // ======== câmera")
    s = s[:a] + "  // ======== CENAS (CTA)\n  " + "\n  ".join(js) + "\n\n" + s[b:]
    s = s.replace('const P = { s1: [0, 0], s2: [0, 2300], s3: [1700, 2300] };', 'const P = { s1: [0, 0], s2: [0, 2300] };')
    s = s.replace('const lugar = { "#s1": "s1", "#s2": "s2", "#s3": "s3" };', 'const lugar = { "#s1": "s1", "#s2": "s2" };')
    a = s.index("    chega(0.9, 1.06")
    b = s.index("    CAM = { viagem, chega };")
    s = s[:a] + "    " + cam + "\n" + s[b:]
    s = s.replace('data-duration="8"', f'data-duration="{D}"').replace("const DUR = 8;", f"const DUR = {D};")
    p.write_text(s, encoding="utf-8")

    sx = str(SKILL / "molde/assets/audio/sfx").replace("\\", "/")
    sfx = [[O, f"{sx}/air_motion_whoosh.wav", -22], [O + ok, f"{sx}/data_point_click.wav", -18],
           [O + via - 0.2, f"{sx}/air_motion_whoosh.wav", -22], [O + tap, f"{sx}/soft_ui_click.wav", -19],
           [O + fx, f"{sx}/logo.wav", -14]]
    json.dump({"inicio": O, "duracao": D, "fim_fala": fim_fala, "sfx": sfx}, open(P / "motion.json", "w"), indent=1)
    print(f"{slug}: CTA {O:.2f}-{O + D:.2f}s  ok {ok} viagem {via} clique {tap} logo {fx}")
    if "--render" in sys.argv:
        subprocess.run("npx --yes hyperframes@0.8.162 render --quality high --fps 30 -o render/cta.mp4", cwd=P, shell=True, check=True)


if __name__ == "__main__":
    main()
