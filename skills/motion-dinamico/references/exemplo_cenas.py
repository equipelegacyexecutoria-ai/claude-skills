# Motion Dinâmico: "Seu Cérebro Tem Um Defeito De Fábrica" (v7: treinar/estudar/economizar em tela dividida; v6, 21/10/2026): tela dividida com emenda em degradê
# e texto no centro, B-rolls trocados pelo sentido da fala, Clailton no trecho do baú.
# (cabeçalho da v5:): B-roll do acervo B-ROLLS e tela dividida
# com o Clailton nas cenas das notas da v4; o resto como na v4.
# (cabeçalho da v4:) Notas da v3: sem ladrão, texto adiantado,
# sino de fim de round terminando no corte, tudo 70 px acima (gabarito de área segura), sem efeito em 1997,
# VENCE separado do "quase sempre", vermelho no lugar do laranja.
# (cabeçalho da v3:)
# Notas da v2: sem legenda (a fala inteira vira texto animado, sem repetir e sem cobrir elementos), paleta Legacy,
# carimbos preenchidos, sem a etiqueta do topo, flecha no alvo, ladrão no lugar da mão, cabeça do Clailton no fim,
# sons de soco + sino, despertador, ronco e passos.
# uso: python cenas_v3.py <projeto> <palavras_corte.json>
import os, sys
sys.path.insert(0, os.path.join(os.path.expanduser("~"), ".claude", "skills", "motion-dinamico", "scripts"))
from motion_lib import *  # noqa: F401,F403
# fundos de texto sobre B-roll e emenda em degradê da tela dividida
GRAD_BAIXO = "background: linear-gradient(to bottom, rgba(3,6,13,0) 0%, rgba(3,6,13,.82) 100%)"
GRAD_CIMA = "background: linear-gradient(to top, rgba(3,6,13,0) 0%, rgba(3,6,13,.82) 100%)"
EMENDA_GRAD = ("background: linear-gradient(to bottom, rgba(3,6,13,0) 0%, rgba(3,6,13,.94) 30%, "
               "rgba(3,6,13,.94) 70%, rgba(3,6,13,0) 100%)")

AZ, OURO = "23,173,253", "231,170,81"
# palco inteiro 70 px acima: o conteúdo fica no centro da área segura (gabarito do Reels: 250 a 1500)
v = Video(sys.argv[1], sys.argv[2], 73.6, css=".bz, .cena > .palco { top: -70px; bottom: 70px; }")

# ---- 0–3.45 gancho: tela dividida, B-roll em cima (homem aflito, Succession) e Clailton embaixo, texto na emenda
v.video("assets/broll/s1.mp4", 0, 3.45, 0, 0, 1080, 900, zoom=0)
v.expert("assets/dividida_0.mp4", 0, 3.45, cx=540, cy=1410, w=1080, h=1020, moldura=False)
v.cena("s1", 0, 3.45, "tenso", [], "", sobre=[
    caixa("s1-emenda", 540, 970, 1080, 440, "", 0, estilo=EMENDA_GRAD),
    titulo("s1-t1", [(54, [("O", 0.14, "fino"), ("teu", 0.26, "fino"), ("cérebro", 0.52, "ac"), ("está", 1.14, "fino"), ("com", 1.46, "fino"), ("um", 1.58, "fino")])], 540, 840, 0),
    carimbo("s1-car", "DEFEITO DE FÁBRICA", 540, 960, 64, 0, -3),
    titulo("s1-t2", [(62, [("salva", 2.69, "ac"), ("isso.", 2.99, "")])], 540, 1020, 0),
], js_sobre="""
carimbo("#s1-car", 1.67);
""")

# ---- 3.45–5.90 ele prefere aliviar o desconforto de agora: só B-roll (Huell na cama de dinheiro, Breaking Bad)
v.video("assets/broll/s2.mp4", 3.45, 2.45)
v.cena("s2", 3.45, 5.90, "tenso", [], "", sobre=[
    caixa("s2-grad", 540, 420, 1080, 700, "", 0, estilo=GRAD_CIMA),
    titulo("s2-tit", [(56, [("Ele", 3.55, "fino"), ("prefere", 3.73, "fino")]), (140, [("aliviar", 4.21, "hl")]),
                      (64, [("o", 4.59, "fino"), ("desconforto", 4.67, ""), ("de", 5.22, "fino"), ("agora", 5.32, "ac")])], 540, 385, 0),
], js_sobre="")

# ---- 5.90–8.62 mesmo que isso prejudique o teu futuro
CRACK = '<path id="s3-trinca" d="M 300 120 L 255 230 L 320 300 L 240 420 L 300 500 L 250 600" fill="none" stroke="#ff3b3b" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" class="luz"/>'
v.cena("s3", 5.90, 8.62, "tenso", [
    brilho("s3-luz", 540, 960, 500, AZ, .35),
    img("s3-amp", "ampulheta", 540, 960, 440, 0, dentro=f'<svg viewBox="0 0 520 708" style="position:absolute; left:0; top:0; width:100%; height:100%; overflow:visible">{CRACK}</svg>'),
    titulo("s3-t1", [(54, [("mesmo", 5.98, "fino"), ("que", 6.44, "fino"), ("isso", 6.66, "fino"), ("prejudique", 6.94, "rd")])], 540, 400),
    titulo("s3-t2", [(64, [("o", 7.82, "fino"), ("teu", 7.90, "fino")]), (120, [("futuro", 8.04, "ac")])], 470, 1285, w=780),
], """
bz("#s3-bz", 5.90); cam("#s3-mundo", 5.90, 2.72, {y:-20, z:0, rotationY:-2}, {y:0, z:200, rotationY:1.5});
entra("#s3-amp", 5.95, "sobe"); flutua("#s3-amp", 6.5, 2.1, 6, 2.6, 1);
traco("#s3-trinca", 6.94, 0.45); soco("#s3-bz", 6.94, 1.04, 0.3);
tl.to("#s3-amp", {rotation:-7, y:20, duration:0.6, ease:"power2.out"}, 6.94);
""")

# ---- 8.62–10.22 em 1997
DIG = "".join(f'<span class="dg">{d}</span>' for d in "1997")
v.cena("s4", 8.62, 10.22, "escuro", [
    raios("s4-raios", -500, .5),
    img("s4-cal", "calendario", 240, 900, 300, 0),
    etiqueta("s4-em", "EM", 650, 720, 50, cls="tag lin"),
    camada(120, f'<div class="it ctr" id="s4-ano" style="left:330px; top:900px; width:640px; text-align:center">{DIG}</div>'),
], """
bz("#s4-bz", 8.62); cam("#s4-mundo", 8.62, 1.6, {z:0, rotationY:2}, {z:240, rotationY:-2});
entra("#s4-cal", 8.66, "pop", {rot:-14}); entra("#s4-em", 8.69, "pop");
gsap.utils.toArray("#s4-ano .dg").forEach((d, i) => tl.fromTo(d, {opacity:0, y:30, filter:"blur(10px)"}, {opacity:1, y:0, filter:"blur(0px)", duration:0.2, ease:"power3.out", immediateRender:false}, 8.77 + i * 0.12));
soco("#s4-bz", 9.13, 1.05, 0.3); semsom("soco", 9.13);
""")

# ---- 10.22–12.85 o economista David Laibson mostrou isso
v.cena("s5", 10.22, 12.85, "escuro", [
    brilho("s5-luz", 540, 840, 560, AZ, .35),
    titulo("s5-t1", [(70, [("o", 10.27, "fino"), ("economista", 10.33, "ac")])], 540, 390),
    polaroid("s5-foto", "laibson", 540, 845, 520, "DAVID LAIBSON", rot=3),
    titulo("s5-t2", [(64, [("mostrou", 12.01, ""), ("isso", 12.47, "fino")])], 470, 1200, w=780),
], """
bz("#s5-bz", 10.22); cam("#s5-mundo", 10.22, 2.63, {z:0, rotationY:3}, {z:200, rotationY:-2});
entra("#s5-foto", 10.27, "sobe", {rot:8}); flutua("#s5-foto", 10.9, 1.95, 5, 2.6, .6);
digita("#s5-foto .ch", 10.99, 0.05);
""")

# ---- 12.85–16.50 ao estudar o chamado desconforto hiperbólico
GRAF = """
<path d="M 100 70 V 520 H 790" fill="none" stroke="rgba(255,255,255,.85)" stroke-width="5" stroke-linecap="round"/>
<path d="M 87 92 L 100 66 L 113 92 M 766 507 L 792 520 L 766 533" fill="none" stroke="rgba(255,255,255,.85)" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
<text x="60" y="290" transform="rotate(-90 60 290)" text-anchor="middle" class="gtx">valor</text>
<text x="120" y="575" class="gtx">agora</text><text x="790" y="575" text-anchor="end" class="gtx">depois</text>
<path id="s6-curva" class="luz" d="M 122 96 C 160 370, 270 455, 780 494" fill="none" stroke="#17adfd" stroke-width="10" stroke-linecap="round"/>
<circle id="s6-ponto" cx="122" cy="96" r="16" fill="#e7aa51" stroke="#fff" stroke-width="5"/>
"""
v.cena("s6", 12.85, 16.50, "escuro", [
    caixa("s6-graf", 525, 975, 740, 560, f'<div class="card" style="width:740px; height:560px; padding:0"><svg viewBox="0 0 860 640" style="width:100%; height:100%; overflow:visible">{GRAF}</svg></div>', 0),
    titulo("s6-tit", [(52, [("ao", 12.88, "fino"), ("estudar", 13.00, "fino"), ("o", 13.40, "fino"), ("chamado", 13.54, "fino")]),
                      (100, [("desconforto", 14.30, "")]), (88, [("HIPERBÓLICO", 15.42, "hl")])], 540, 385),
], """
bz("#s6-bz", 12.85); cam("#s6-mundo", 12.85, 3.65, {x:20, z:0, rotationY:2}, {x:-20, z:180, rotationY:-2});
entra("#s6-graf", 12.95, "sobe");
traco("#s6-curva", 13.54, 1.0);
gsap.set("#s6-ponto", {opacity:0}); tl.fromTo("#s6-ponto", {opacity:0}, {opacity:1, duration:0.15, immediateRender:false}, 13.54);
corre("#s6-curva", "#s6-ponto", 15.42, 0.9);
""")

# ---- 16.50–21.12 nós tendemos a dar mais valor ao que sentimos no presente
v.cena("s7", 16.50, 21.12, "escuro", [
    cartao("s7-a", "despertador", 300, 820, "PRESENTE", -2, w=380, h=420),
    cartao("s7-b", "ampulheta", 780, 820, "FUTURO", 2, w=380, h=420),
    titulo("s7-t1", [(56, [("Nós", 16.55, "fino"), ("tendemos", 16.77, "fino"), ("a", 17.55, "fino"), ("dar", 17.67, "fino")]),
                     (120, [("mais", 18.07, ""), ("valor", 18.43, "hl")])], 540, 385),
    titulo("s7-t2", [(56, [("ao", 19.14, "fino"), ("que", 19.26, "fino"), ("sentimos", 19.44, "fino")]),
                     (104, [("no", 20.10, "fino"), ("presente", 20.26, "ac")])], 470, 1110, w=780),
], """
bz("#s7-bz", 16.50); cam("#s7-mundo", 16.50, 4.62, {x:-20, z:0, rotationY:-2}, {x:20, z:160, rotationY:2});
entra("#s7-a", 16.77, "pop", {rot:-8}); entra("#s7-b", 17.00, "pop", {rot:8});
tl.to("#s7-a", {scale:1.12, duration:0.5, ease:"back.out(1.8)"}, 18.07);
tl.to("#s7-b", {scale:0.86, opacity:0.4, duration:0.5, ease:"power2.out"}, 18.43);
pulsa("#s7-a .card", 20.26, 0.6, 1.04); soco("#s7-bz", 20.26, 1.04, 0.3);
""")

# ---- 21.12–24.98 do que o benefício que só receberemos no futuro: B-roll (Kendall olhando o horizonte, Succession)
v.video("assets/broll/s8b.mp4", 21.12, 3.86)
v.cena("s8", 21.12, 24.98, "escuro", [], "", sobre=[
    caixa("s8-grad1", 540, 420, 1080, 700, "", 0, estilo=GRAD_CIMA),
    caixa("s8-grad2", 540, 1520, 1080, 1100, "", 0, estilo=GRAD_BAIXO),
    titulo("s8-t1", [(56, [("do", 21.18, "fino"), ("que", 21.34, "fino"), ("o", 21.72, "fino")]), (130, [("benefício", 21.82, "hl")])], 540, 385, 0),
    titulo("s8-t2", [(56, [("que", 22.66, "fino"), ("só", 22.86, "fino"), ("receberemos", 23.17, "fino")]),
                     (96, [("no", 24.49, "fino"), ("futuro", 24.61, "ac")])], 470, 1250, 0, w=780),
], js_sobre="")

# ---- 24.98–27.12 é por isso que você sabe que precisa
PENS = "".join(f'<circle class="bolha" cx="{x}" cy="{y}" r="{r}" fill="#17adfd" stroke="#031022" stroke-width="4"/>' for x, y, r in [(560, 520, 12), (515, 468, 18), (455, 405, 26)])
v.cena("s9", 24.98, 27.12, "escuro", [
    brilho("s9-luz", 700, 1000, 500, AZ, .35),
    boneco("s9-homem", "pensativo", 710, 1080, 540, 0),
    svg("s9-bolhas", PENS, 40),
    titulo("s9-tit", [(54, [("É", 25.15, "fino"), ("por", 25.23, "fino"), ("isso", 25.35, "fino"), ("que", 25.49, "fino")]),
                      (150, [("você", 25.59, "")]), (150, [("sabe", 25.89, "hl")]), (56, [("que", 26.54, "fino"), ("precisa", 26.70, "fino")])],
           290, 540, w=480),
], """
bz("#s9-bz", 24.98); cam("#s9-mundo", 24.98, 2.14, {x:20, z:0, rotationY:2}, {x:-10, z:150, rotationY:-1});
entra("#s9-homem", 25.02, "dir", {dist:260, rot:3});
gsap.utils.toArray("#s9-bolhas .bolha").forEach((b, i) => { gsap.set(b, {opacity:0}); tl.fromTo(b, {opacity:0, scale:0, transformOrigin:"50% 50%"}, {opacity:1, scale:1, duration:0.25, ease:"back.out(2)", immediateRender:false}, 26.54 + i * 0.12); });
sfx("pop", 26.54);
""")

# ---- 27.12–29.35 treinar, estudar, economizar: tela dividida, um B-roll por palavra em cima, Clailton embaixo
v.video("assets/broll/treinar_topo.mp4", 27.12, 0.73, 0, 0, 1080, 900, zoom=0)
v.video("assets/broll/estudar_topo.mp4", 27.85, 0.70, 0, 0, 1080, 900, zoom=0)
v.video("assets/broll/economizar_topo.mp4", 28.55, 0.80, 0, 0, 1080, 900, zoom=0)
v.expert("assets/treinodiv_0.mp4", 27.12, 2.23, cx=540, cy=1410, w=1080, h=1020, moldura=False)
v.cena("s10", 27.12, 29.35, "escuro", [], "", sobre=[
    caixa("s10-emenda", 540, 970, 1080, 440, "", 0, estilo=EMENDA_GRAD),
    titulo("s10-a", [(120, [("treinar,", 27.19, "hl")])], 540, 898, 0),
    titulo("s10-b", [(120, [("estudar,", 27.89, "hl")])], 540, 898, 0),
    titulo("s10-c", [(120, [("economizar", 28.61, "hl")])], 540, 898, 0),
], js_sobre="""
sai("#s10-a", 27.66, 0.08); sai("#s10-b", 28.38, 0.08);
sfx("sobe", 27.85); sfx("sobe", 28.55);
""")

# ---- 29.35–31.22 ou começar aquele projeto: B-roll em tela cheia (reunião)
v.video("assets/broll/projeto.mp4", 29.35, 1.88)
v.cena("s10p", 29.35, 31.22, "escuro", [], "", sobre=[
    caixa("s10p-grad", 540, 1520, 1080, 1100, "", 0, estilo=GRAD_BAIXO),
    titulo("s10p-d", [(56, [("ou", 29.27, "fino"), ("começar", 29.41, "fino"), ("aquele", 29.94, "fino")]), (110, [("projeto", 30.34, "ac")])], 470, 1230, 0, w=780),
], js_sobre="""
sfx("sobe", 29.35);
""")

# ---- 31.22–33.60 mas continua adiando (ronco)
ZZ = "".join(f'<text class="zz" x="{x}" y="{y}" style="font-size:{s}px">z</text>' for x, y, s in [(700, 900, 56), (755, 830, 76), (820, 745, 98)])
v.cena("s11", 31.22, 33.60, "tenso", [
    img("s11-cal", "calendario", 270, 770, 300, -120, dentro='<div class="calpag"><span id="s11-hoje">HOJE</span><span id="s11-amanha">AMANHÃ</span></div>'),
    img("s11-exec", "executivo", 500, 1090, 850, 0),
    svg("s11-zz", ZZ, 60),
    titulo("s11-tit", [(56, [("mas", 31.26, "fino"), ("continua", 31.48, "fino")]), (130, [("adiando...", 32.54, "ac")])], 540, 385),
], """
bz("#s11-bz", 31.22); cam("#s11-mundo", 31.22, 2.38, {x:20, z:0, rotationY:2}, {x:-20, z:160, rotationY:-2});
entra("#s11-exec", 31.25, "sobe"); entra("#s11-cal", 31.3, "pop", {rot:8});
tl.fromTo("#s11-exec > .fl", {scaleY:1}, {scaleY:1.018, transformOrigin:"50% 100%", duration:1.1, ease:"sine.inOut", yoyo:true, repeat:2, immediateRender:false}, 31.3);
gsap.set("#s11-amanha", {opacity:0, rotationX:-90});
tl.to("#s11-hoje", {rotationX:90, opacity:0, duration:0.22, ease:"power2.in"}, 31.48);
tl.fromTo("#s11-amanha", {rotationX:-90, opacity:0}, {rotationX:0, opacity:1, duration:0.26, ease:"power2.out", immediateRender:false}, 31.70);
gsap.utils.toArray("#s11-zz .zz").forEach((z, i) => tl.fromTo(z, {opacity:0, y:30}, {opacity:1, y:0, duration:0.5, ease:"sine.out", immediateRender:false}, 31.6 + i * 0.35));
sfx("ronco", 31.35);
""")

# ---- 33.60–35.50 o benefício está lá na frente (passos)
v.cena("s12", 33.60, 35.50, "escuro", [
    brilho("s12-luz", 840, 800, 330, OURO, .5, -800),
    selo("s12-trofeu", "trofeu", 840, 800, 200, z=-800),
    linha("s12-cam", "M 360 1250 C 520 1160, 620 1000, 800 900", z=-100, tracejada=True),
    linha("s12-seta", "M 640 640 H 860 M 815 595 L 865 640 L 815 685", z=60, cor="#ffffff", larg=11),
    img("s12-homem", "caminhante", 240, 1030, 280, 0),
    titulo("s12-tit", [(56, [("O", 33.65, "fino"), ("benefício", 33.73, "ac"), ("está", 34.33, "fino")]),
                       (130, [("lá", 34.53, ""), ("na", 34.67, ""), ("frente", 34.89, "hl")])], 430, 385, w=700, alinha="left"),
], """
bz("#s12-bz", 33.60); cam("#s12-mundo", 33.60, 1.9, {x:-30, z:0, rotationY:-2}, {x:30, z:160, rotationY:2});
tl.fromTo("#s12-homem", {x:-60}, {x:150, duration:1.9, ease:"none", immediateRender:false}, 33.60);
tl.fromTo("#s12-homem > .fl", {y:0}, {y:-7, duration:0.28, ease:"sine.inOut", yoyo:true, repeat:6, immediateRender:false}, 33.60);
entra("#s12-trofeu", 33.62, "fade", {d:0.6});
traco("#s12-cam", 33.7, 1.0); traco("#s12-seta", 35.0, 0.35);
sfx("passos", 33.62);
""")

# ---- 35.50–38.05 mas o desconforto está no aqui
SETA13 = '<path id="s13-seta" class="luz" d="M 540 545 V 640 M 500 605 L 540 645 L 580 605" fill="none" stroke="#17adfd" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>'
v.cena("s13", 35.50, 38.05, "tenso", [
    brilho("s13-luz", 540, 1030, 520, AZ, .35),
    img("s13-homem", "cansado", 540, 1040, 800, 0),
    titulo("s13-tit", [(56, [("mas", 35.54, "fino"), ("o", 35.76, "fino")]), (120, [("desconforto", 35.82, "rd")]), (56, [("está", 36.72, "fino"), ("no", 37.36, "fino")])], 540, 385),
    carimbo("s13-aqui", "AQUI", 540, 455, 150, 150, -3),
    svg("s13-svg", SETA13, 120),
], """
bz("#s13-bz", 35.50); cam("#s13-mundo", 35.50, 2.55, {z:0, rotationY:-2}, {z:160, rotationY:2});
entra("#s13-homem", 35.52, "sobe");
tl.fromTo("#s13-homem > .fl", {rotation:-1.2}, {rotation:1.2, transformOrigin:"50% 100%", duration:1.2, ease:"sine.inOut", yoyo:true, repeat:2, immediateRender:false}, 35.52);
sai("#s13-tit", 37.25, 0.15);
carimbo("#s13-aqui", 37.52); traco("#s13-seta", 37.62, 0.25);
""")

# ---- 38.05–40.62 e o aqui e agora quase sempre vence: tela dividida, boxe (Touro Indomável) num trecho só, sem cortes
v.video("assets/broll/agora2.mp4", 38.05, 2.57, 0, 0, 1080, 900, zoom=0)
v.expert("assets/dividida_1.mp4", 38.05, 2.57, cx=540, cy=1410, w=1080, h=1020, moldura=False)
v.cena("s14", 38.05, 40.62, "tenso", [], "", sobre=[
    caixa("s14-emenda", 540, 970, 1080, 440, "", 0, estilo=EMENDA_GRAD),
    titulo("s14-t1", [(84, [("E", 38.10, "fino"), ("o", 38.20, "fino"), ("aqui", 38.30, ""), ("e", 38.66, "fino"), ("agora", 38.72, "hl")])], 540, 765, 0),
    titulo("s14-t2", [(54, [("quase", 39.23, "fino"), ("sempre", 39.63, "fino")])], 540, 868, 0),
    carimbo("s14-vence", "VENCE", 540, 1030, 88, 0, -5),
], js_sobre="""
sfx("punch", 39.97); sfx("sinofim", 40.02);
carimbo("#s14-vence", 40.11); semsom("carimbo", 40.11);
""")

# ---- 40.62–43.10 virada: só o Clailton em tela cheia, com os textos
v.expert("assets/cheia_0.mp4", 40.62, 2.48, cx=540, cy=960, w=1080, h=1920, moldura=False)
v.cena("s15", 40.62, 43.10, "quente", [], """
sfx("bz", 40.62);
""", sobre=[
    caixa("s15-grad", 540, 1520, 1080, 1100, "", 0, estilo=GRAD_BAIXO),
    titulo("s15-tit", [(52, [("Então", 40.73, "fino"), ("se", 40.95, "fino"), ("você", 41.05, "fino"), ("quiser", 41.25, "fino")]),
                       (84, [("corrigir", 41.53, "hl"), ("esse", 41.97, "fino"), ("defeito", 42.21, "ac")])], 470, 1290, 0, w=780),
], js_sobre="")

# ---- 43.10–49.85 pare de deixar toda a recompensa para o futuro / traga uma parte dela agora, para o presente
# tela dividida: baú em cima, Clailton embaixo, texto na emenda
MOEDAS = "".join(f'<circle class="moeda" cx="{x}" cy="{y}" r="{r}" fill="#e7aa51" stroke="#8a5d1e" stroke-width="4"/>' for x, y, r in
                 [(430, 570, 16), (660, 530, 13), (380, 710, 11), (720, 670, 18), (560, 460, 12), (300, 630, 9), (790, 570, 10)])
v.expert("assets/baudiv_0.mp4", 43.10, 6.75, cx=540, cy=1410, w=1080, h=1020, moldura=False)
v.cena("s16", 43.10, 49.85, "quente", [
    raios("s16-raios", -1600, .45),
    brilho("s16-luz", 540, 590, 380, OURO, .55),
    camada(0, '<div class="it" id="s16-bauw" style="left:360px; top:416px; width:360px; height:348px">'
              '<div class="fl"><img class="rec" src="assets/img/bau.png" alt="" style="width:100%; height:100%" /></div></div>', nocomp=True, ident="s16-bauz"),
    carimbo("s16-pare", "PARE", 540, 520, 110, 160, -4),
    svg("s16-moedas", MOEDAS, 120),
], """
bz("#s16-bz", 43.10); cam("#s16-mundo", 43.10, 6.75, {z:0}, {z:60});
entra("#s16-bauw", 43.15, "fade", {d:0.8}); flutua("#s16-bauw", 43.2, 6.6, 8, 2.6, 1.2);
gsap.set("#s16-luz", {opacity:0}); tl.fromTo("#s16-luz", {opacity:0}, {opacity:1, duration:1, immediateRender:false}, 43.3);
carimbo("#s16-pare", 43.17); sai("#s16-pare", 44.5, 0.2);
gsap.utils.toArray("#s16-moedas .moeda").forEach((m, i) => { gsap.set(m, {opacity:0}); tl.fromTo(m, {opacity:0, y:60, scale:0.3, transformOrigin:"50% 50%"}, {opacity:1, y:-40 - (i % 3) * 30, scale:1, duration:0.6, ease:"power2.out", immediateRender:false}, 48.48 + i * 0.05); });
sfx("brilho", 48.48); soco("#s16-bz", 48.48, 1.05, 0.3);
""", sobre=[
    caixa("s16-emenda", 540, 970, 1080, 440, "", 0, estilo=EMENDA_GRAD),
    titulo("s16-t1", [(56, [("de", 43.64, "fino"), ("deixar", 43.78, "fino"), ("toda", 44.68, "fino"), ("a", 45.00, "fino")]), (110, [("recompensa", 45.06, "hl")]),
                      (64, [("para", 45.89, "fino"), ("o", 46.09, "fino"), ("futuro", 46.19, "ac")])], 540, 833, 0),
    titulo("s16-t3", [(60, [("Traga", 46.99, ""), ("uma", 47.29, "fino"), ("parte", 47.49, "fino"), ("dela", 47.84, "fino")]), (110, [("agora,", 48.48, "ac")])], 540, 870, 0),
    titulo("s16-t4", [(60, [("para", 49.04, "fino"), ("o", 49.16, "fino")]), (140, [("presente", 49.24, "hl")])], 540, 852, 0),
], js_sobre="""
sai("#s16-t1", 46.6, 0.18); sai("#s16-t3", 48.6, 0.15);
""")

# ---- 49.85–54.58 quer treinar? então só assista a tua série favorita depois do treino
v.cena("s17", 49.85, 54.58, "quente", [
    boneco("s17-homem", "halter", 290, 1010, 460, 0),
    img("s17-tv", "tv", 740, 960, 340, 0),
    linha("s17-seta", "M 450 640 C 510 600, 580 600, 630 635 M 596 611 L 634 637 L 598 665", z=30, larg=9),
    etiqueta("s17-n1", "1º", 290, 640, 52), etiqueta("s17-n2", "2º", 740, 640, 52),
    titulo("s17-t1", [(130, [("Quer", 49.89, "fino"), ("treinar?", 50.13, "ac")])], 540, 390),
    titulo("s17-t2", [(56, [("Então", 50.87, "fino"), ("só", 51.23, "fino"), ("assista", 51.39, "fino")]),
                      (84, [("a", 52.04, "fino"), ("tua", 52.12, "fino"), ("série", 52.38, "ac"), ("favorita", 52.62, "ac")])], 540, 385),
    titulo("s17-t3", [(84, [("depois", 53.46, ""), ("do", 53.96, "fino"), ("treino", 54.10, "hl")])], 540, 400),
], """
bz("#s17-bz", 49.85); cam("#s17-mundo", 49.85, 4.73, {x:-30, z:0, rotationY:-2}, {x:30, z:150, rotationY:2});
entra("#s17-homem", 49.9, "esq", {dist:300}); entra("#s17-n1", 50.13, "pop");
sai("#s17-t1", 50.55, 0.15); sai("#s17-t2", 53.15, 0.15);
entra("#s17-tv", 52.38, "dir", {dist:400}); flutua("#s17-tv", 53.0, 1.55, 6, 2.4, 1);
entra("#s17-n2", 52.62, "pop"); traco("#s17-seta", 53.46, 0.4);
""")

# ---- 54.58–59.42 precisa estudar? café delicioso depois de cumprir a meta: tela dividida, texto na emenda
v.video("assets/broll/estudo3.mp4", 54.58, 2.12, 0, 0, 1080, 900, zoom=0)
v.video("assets/broll/cafe2.mp4", 56.70, 1.55, 0, 0, 1080, 900, zoom=0)
v.video("assets/broll/meta.mp4", 58.25, 1.17, 0, 0, 1080, 900, zoom=0)
v.expert("assets/dividida_2.mp4", 54.58, 4.84, cx=540, cy=1410, w=1080, h=1020, moldura=False)
v.cena("s18", 54.58, 59.42, "quente", [], "", sobre=[
    caixa("s18-emenda", 540, 970, 1080, 440, "", 0, estilo=EMENDA_GRAD),
    titulo("s18-t1", [(100, [("Precisa", 54.63, "fino"), ("estudar?", 54.99, "ac")])], 540, 910, 0),
    titulo("s18-t2", [(56, [("Tome", 56.01, "fino"), ("aquele", 56.45, "fino")]), (92, [("café", 56.79, "ac"), ("delicioso", 57.15, "ac")])], 540, 882, 0),
    titulo("s18-t3", [(56, [("depois", 57.81, "fino"), ("de", 58.17, "fino")]), (92, [("cumprir", 58.30, ""), ("essa", 58.68, "fino"), ("meta", 58.94, "hl")])], 540, 882, 0),
], js_sobre="""
sai("#s18-t1", 55.7, 0.15); sai("#s18-t2", 57.5, 0.15);
sfx("sobe", 56.70); sfx("ok", 58.94);
""")

# ---- 59.42–65.52 faça o teu cérebro sentir agora uma parte do benefício que só viria muito tempo depois
v.cena("s19", 59.42, 65.52, "quente", [
    brilho("s19-luz", 540, 900, 560, OURO, .55),
    img("s19-cerebro", "cerebro", 540, 900, 540, 0),
    selo("s19-trofeu", "trofeu", 860, 760, 170, z=120),
    img("s19-amp", "ampulheta", 220, 760, 250, -800, cls="rec longe"),
    titulo("s19-t1", [(60, [("Faça", 59.46, "fino"), ("o", 59.80, "fino"), ("teu", 59.90, "fino"), ("cérebro", 60.12, "fino")]),
                      (130, [("sentir", 60.60, ""), ("agora", 61.20, "hl")])], 540, 385),
    titulo("s19-t2", [(80, [("uma", 62.02, "fino"), ("parte", 62.28, "ac"), ("do", 62.56, "fino")]), (120, [("benefício", 62.69, "hl")])], 540, 385),
    titulo("s19-t3", [(56, [("que", 63.35, "fino"), ("só", 63.61, "fino"), ("viria", 63.73, "fino")]),
                      (72, [("muito", 64.37, ""), ("tempo", 64.63, ""), ("depois", 64.85, "ac")])], 470, 1200, 160, w=780),
], """
bz("#s19-bz", 59.42); cam("#s19-mundo", 59.42, 6.1, {x:-20, z:0, rotationY:-2}, {x:20, z:200, rotationY:2});
entra("#s19-cerebro", 59.46, "pop"); flutua("#s19-cerebro", 60.0, 5.5, 7, 2.8, 1);
gsap.set("#s19-luz", {opacity:0}); tl.fromTo("#s19-luz", {opacity:0, scale:.6}, {opacity:1, scale:1, duration:0.6, ease:"power2.out", immediateRender:false}, 60.60);
tl.fromTo("#s19-luz", {scale:1}, {scale:1.12, duration:0.5, ease:"sine.inOut", yoyo:true, repeat:7, immediateRender:false}, 61.2);
soco("#s19-bz", 61.20, 1.05, 0.3); sfx("brilho", 60.6);
sai("#s19-t1", 61.68, 0.15);
entra("#s19-trofeu", 62.69, "dir", {dist:300}); flutua("#s19-trofeu", 63.2, 2.3, 6, 2.2, 2);
entra("#s19-amp", 64.37, "fade", {d:0.6});
""")

# ---- 65.52–68.52 dê ao presente uma pequena recompensa
BRILHOS = "".join(f'<path class="faisca" d="M {x} {y - s} L {x + s * .25} {y - s * .25} L {x + s} {y} L {x + s * .25} {y + s * .25} L {x} {y + s} L {x - s * .25} {y + s * .25} L {x - s} {y} L {x - s * .25} {y - s * .25} Z" fill="#e7aa51"/>'
                  for x, y, s in [(300, 760, 34), (790, 720, 28), (250, 1090, 22), (840, 1060, 36), (560, 640, 20)])
v.cena("s20", 65.52, 68.52, "quente", [
    raios("s20-raios", -500, .5),
    brilho("s20-luz", 540, 930, 480, OURO, .5),
    img("s20-presente", "presente", 540, 930, 480, 0),
    svg("s20-faiscas", BRILHOS, 80),
    titulo("s20-tit", [(56, [("Dê", 65.57, "fino"), ("ao", 65.89, "fino"), ("presente", 66.03, "ac")]),
                       (62, [("uma", 66.70, "fino"), ("pequena", 66.92, ""), ("recompensa", 67.48, "hl")])], 540, 385),
], """
bz("#s20-bz", 65.52); cam("#s20-mundo", 65.52, 3.0, {x:20, z:0, rotationY:2}, {x:-20, z:160, rotationY:-2});
entra("#s20-presente", 65.57, "pop", {rot:-10}); flutua("#s20-presente", 66.2, 2.3, 7, 2.4, 1.5);
tl.to("#s20-presente", {scale:0.78, duration:0.5, ease:"power2.inOut"}, 66.92);
gsap.utils.toArray("#s20-faiscas .faisca").forEach((f, i) => { gsap.set(f, {opacity:0}); tl.fromTo(f, {opacity:0, scale:0, rotation:-40, transformOrigin:"50% 50%"}, {opacity:1, scale:1, rotation:0, duration:0.3, ease:"back.out(2)", immediateRender:false}, 67.48 + i * 0.07); });
sfx("brilho", 67.48);
""")

# ---- 68.52–71.05 sem deixar que ele roube o teu futuro (ladrão caracterizado)
ESCUDO = '<circle id="s21-escudo" class="luz" cx="540" cy="1000" r="320" fill="none" stroke="#17adfd" stroke-width="12" stroke-dasharray="40 22"/>'
v.cena("s21", 68.52, 71.05, "quente", [
    brilho("s21-luz", 540, 1000, 520, AZ, .45),
    img("s21-amp", "ampulheta", 540, 1000, 400, 0),
    svg("s21-svg", ESCUDO, 30),
    titulo("s21-t1", [(56, [("sem", 68.56, "fino"), ("deixar", 68.73, "fino"), ("que", 69.15, "fino"), ("ele", 69.33, "fino")]), (100, [("roube", 69.92, "rd")])], 540, 385),
    titulo("s21-t2", [(96, [("o", 70.25, "fino"), ("teu", 70.31, "fino"), ("futuro", 70.47, "hl")])], 470, 1350, w=780),
], """
bz("#s21-bz", 68.52); cam("#s21-mundo", 68.52, 2.53, {z:0, rotationY:-2}, {z:150, rotationY:2});
entra("#s21-amp", 68.55, "sobe"); flutua("#s21-amp", 69.0, 2.0, 6, 2.6, 1);
traco("#s21-escudo", 69.92, 0.4);
tl.fromTo("#s21-amp > .fl", {x:0}, {x:8, duration:0.05, yoyo:true, repeat:5, ease:"none", immediateRender:false}, 69.92);
tl.fromTo("#s21-escudo", {strokeDashoffset:0}, {strokeDashoffset:-310, duration:1.1, ease:"none", immediateRender:false}, 69.92);
soco("#s21-bz", 69.95, 1.04, 0.3);
""")

# ---- 71.05–73.60 CTA digitada (sem a cabeça do Clailton)
v.cena("s22", 71.05, 73.60, "quente", [
    raios("s22-raios", -500, .5),
    brilho("s22-luz", 540, 960, 420, AZ, .4),
    camada(120, f'<div class="it ctr cta" id="s22-cta" style="left:80px; top:960px; width:920px"><div>{letras("ME SIGA PARA MAIS")}</div><div class="ac">{letras("CONTEÚDOS COMO ESTE")}</div></div>'),
], """
bz("#s22-bz", 71.05); cam("#s22-mundo", 71.05, 2.55, {z:0}, {z:120});
sfx("teclado", 71.30); digita("#s22-cta .ch", 71.32, 0.03);
""")

v.gerar()
