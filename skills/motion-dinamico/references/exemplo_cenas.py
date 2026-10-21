# Motion Dinâmico: "Seu Cérebro Tem Um Defeito De Fábrica" (v2, 21/10/2026). Primeiro vídeo da skill motion-dinamico.
# uso: python cenas_v2.py <projeto> <palavras_corte.json>
import os, sys
sys.path.insert(0, os.path.join(os.path.expanduser("~"), ".claude", "skills", "motion-dinamico", "scripts"))
from motion_lib import *  # noqa: F401,F403

v = Video(sys.argv[1], sys.argv[2], 73.6, kicker="DEFEITO DE FÁBRICA")

# ---- 0–3.45 gancho com o Clailton (cartão)
v.expert("assets/expert_0.mp4", 0, 3.45, cx=540, cy=790, w=600, h=750)
BOOK = '<path d="M 18 6 H 102 V 120 L 60 92 L 18 120 Z" fill="#ffc414" stroke="#160a06" stroke-width="6" stroke-linejoin="round"/>'
v.cena("s1", 0, 3.45, "tenso", [brilho("s1-luz", 540, 790, 600, "255,90,30", .45)], """
cam("#s1-mundo", 0, 3.45, {z:0}, {z:100});
""", sobre=[
    img("s1-cerebro", "cerebro", 245, 460, 300, 0),
    svg("s1-salva", BOOK, 0, "0 0 120 126", "left:800px; top:360px; width:120px; height:126px"),
    carimbo("s1-car", "DEFEITO DE FÁBRICA", 540, 1185, 68, 0, -4),
], js_sobre="""
entra("#s1-cerebro", 0.52, "pop", {rot:-12}); flutua("#s1-cerebro", 1.0, 2.5, 7, 2.4, 2);
carimbo("#s1-car", 1.67);
entra("#s1-salva", 2.69, "pop", {de:0.3, rot:14});
""")

# ---- 3.45–5.90 aliviar o desconforto de agora
v.cena("s2", 3.45, 5.90, "tenso", [
    brilho("s2-luz", 560, 990, 560, "255,120,40", .5),
    boneco("s2-mulher", "relaxando", 540, 1000, 920, 0),
    titulo("s2-tit", [(140, [("aliviar", 4.21, "hl")]), (66, [("o", 4.59, ""), ("desconforto", 4.67, ""), ("de", 5.22, ""), ("agora", 5.32, "ac")])], 540, 385),
], """
bz("#s2-bz", 3.45); cam("#s2-mundo", 3.45, 2.45, {x:30, z:0, rotationY:2}, {x:-20, z:170, rotationY:-1.5});
entra("#s2-mulher", 3.5, "sobe");
""")

# ---- 5.90–8.62 prejudica o teu futuro
CRACK = '<path id="s3-trinca" d="M 300 120 L 255 230 L 320 300 L 240 420 L 300 500 L 250 600" fill="none" stroke="#ff4a2a" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" class="luz"/>'
v.cena("s3", 5.90, 8.62, "tenso", [
    brilho("s3-luz", 540, 980, 520, "255,74,42", .4),
    img("s3-amp", "ampulheta", 540, 990, 500, 0, dentro=f'<svg viewBox="0 0 520 708" style="position:absolute; left:0; top:0; width:100%; height:100%; overflow:visible">{CRACK}</svg>'),
    titulo("s3-tit", [(70, [("o", 7.82, ""), ("teu", 7.90, "")]), (160, [("futuro", 8.04, "ac")])], 540, 375),
], """
bz("#s3-bz", 5.90); cam("#s3-mundo", 5.90, 2.72, {y:-20, z:0, rotationY:-2}, {y:0, z:220, rotationY:1.5});
entra("#s3-amp", 5.95, "sobe"); flutua("#s3-amp", 6.5, 2.1, 6, 2.6, 1);
traco("#s3-trinca", 6.94, 0.45); soco("#s3-bz", 6.94, 1.04, 0.3);
tl.to("#s3-amp", {rotation:-7, y:24, duration:0.6, ease:"power2.out"}, 6.94);
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
sfx("tique", 8.77); sfx("tique", 8.89); sfx("tique", 9.01); sfx("tique", 9.13); soco("#s4-bz", 9.13, 1.05, 0.3);
""")

# ---- 10.22–12.85 o economista David Laibson
v.cena("s5", 10.22, 12.85, "escuro", [
    brilho("s5-luz", 540, 820, 560, "255,140,50", .4),
    polaroid("s5-foto", "laibson", 540, 830, 540, "DAVID LAIBSON", rot=3),
    etiqueta("s5-tag", "ECONOMISTA", 540, 410, 50),
], """
bz("#s5-bz", 10.22); cam("#s5-mundo", 10.22, 2.63, {z:0, rotationY:3}, {z:200, rotationY:-2});
entra("#s5-foto", 10.27, "sobe", {rot:8}); flutua("#s5-foto", 10.9, 1.95, 5, 2.6, .6);
entra("#s5-tag", 10.33, "pop");
digita("#s5-foto .ch", 10.99, 0.05);
""")

# ---- 12.85–16.50 desconforto hiperbólico (como ele fala; nota da Sala, 21/10/2026)
GRAF = """
<path d="M 100 70 V 520 H 790" fill="none" stroke="rgba(255,255,255,.85)" stroke-width="5" stroke-linecap="round"/>
<path d="M 87 92 L 100 66 L 113 92 M 766 507 L 792 520 L 766 533" fill="none" stroke="rgba(255,255,255,.85)" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
<text x="60" y="290" transform="rotate(-90 60 290)" text-anchor="middle" class="gtx">valor</text>
<text x="120" y="575" class="gtx">agora</text><text x="790" y="575" text-anchor="end" class="gtx">depois</text>
<path id="s6-curva" class="luz" d="M 122 96 C 160 370, 270 455, 780 494" fill="none" stroke="#ffc414" stroke-width="10" stroke-linecap="round"/>
<circle id="s6-ponto" cx="122" cy="96" r="16" fill="#ff4a2a" stroke="#fff" stroke-width="5"/>
"""
v.cena("s6", 12.85, 16.50, "escuro", [
    caixa("s6-graf", 525, 910, 760, 600, f'<div class="card" style="width:760px; height:600px; padding:0"><svg viewBox="0 0 860 640" style="width:100%; height:100%; overflow:visible">{GRAF}</svg></div>', 0),
    titulo("s6-tit", [(110, [("desconforto", 14.30, "")]), (96, [("HIPERBÓLICO", 15.42, "hl")])], 540, 375),
], """
bz("#s6-bz", 12.85); cam("#s6-mundo", 12.85, 3.65, {x:20, z:0, rotationY:2}, {x:-20, z:200, rotationY:-2});
entra("#s6-graf", 12.95, "sobe");
traco("#s6-curva", 13.54, 1.0);
gsap.set("#s6-ponto", {opacity:0}); tl.fromTo("#s6-ponto", {opacity:0}, {opacity:1, duration:0.15, immediateRender:false}, 13.54);
corre("#s6-curva", "#s6-ponto", 15.42, 0.9);
""")

# ---- 16.50–21.12 mais valor ao presente (cartões presente x futuro)
v.cena("s7", 16.50, 21.12, "escuro", [
    cartao("s7-a", "despertador", 300, 820, "PRESENTE", -2, w=400, h=440),
    cartao("s7-b", "ampulheta", 780, 820, "FUTURO", 2, w=400, h=440),
    img("s7-bal", "balanca", 540, 1170, 260, 60),
    titulo("s7-tit", [(130, [("mais", 18.07, ""), ("valor", 18.43, "hl")])], 540, 385),
], """
bz("#s7-bz", 16.50); cam("#s7-mundo", 16.50, 4.62, {x:-20, z:0, rotationY:-2}, {x:20, z:180, rotationY:2});
entra("#s7-a", 16.77, "pop", {rot:-8}); entra("#s7-b", 17.00, "pop", {rot:8}); entra("#s7-bal", 17.3, "sobe");
tl.to("#s7-a", {scale:1.12, duration:0.5, ease:"back.out(1.8)"}, 18.07);
tl.to("#s7-b", {scale:0.86, opacity:0.4, duration:0.5, ease:"power2.out"}, 18.43);
tl.to("#s7-bal", {rotation:-8, transformOrigin:"50% 92%", duration:0.8, ease:"power2.out"}, 18.07);
pulsa("#s7-a .card", 20.26, 0.6, 1.04); soco("#s7-bz", 20.26, 1.04, 0.3);
""")

# ---- 21.12–24.98 o benefício que só receberemos no futuro (linha do tempo luminosa)
v.cena("s8", 21.12, 24.98, "escuro", [
    linha("s8-linha", "M 170 1180 C 420 1140, 430 860, 820 720", z=0),
    selo("s8-hoje", "despertador", 170, 1180, 150, z=20),
    brilho("s8-luz", 820, 680, 340, "255,196,20", .5, -100),
    selo("s8-trofeu", "trofeu", 820, 680, 230, z=20),
    etiqueta("s8-tag", "NO FUTURO", 820, 860, 42),
    titulo("s8-tit", [(140, [("benefício", 21.82, "hl")])], 540, 385),
], """
bz("#s8-bz", 21.12); cam("#s8-mundo", 21.12, 3.86, {x:40, z:0, rotationY:3}, {x:-40, z:220, rotationY:-2});
entra("#s8-hoje", 21.2, "pop"); traco("#s8-linha", 21.45, 1.2);
entra("#s8-trofeu", 21.82, "pop"); flutua("#s8-trofeu", 22.3, 2.6, 8, 2.6, 1.5);
entra("#s8-tag", 24.49, "pop");
""")

# ---- 24.98–27.12 você sabe que precisa
PENS = "".join(f'<circle class="bolha" cx="{x}" cy="{y}" r="{r}" fill="#ffc414" stroke="#160a06" stroke-width="4"/>' for x, y, r in [(560, 520, 12), (515, 468, 18), (455, 405, 26)])
v.cena("s9", 24.98, 27.12, "escuro", [
    brilho("s9-luz", 700, 1000, 500, "255,120,40", .4),
    boneco("s9-homem", "pensativo", 700, 1080, 540, 0),
    svg("s9-bolhas", PENS, 40),
    titulo("s9-tit", [(150, [("você", 25.59, "")]), (150, [("sabe", 25.89, "hl")])], 290, 560, w=480),
], """
bz("#s9-bz", 24.98); cam("#s9-mundo", 24.98, 2.14, {x:20, z:0, rotationY:2}, {x:-10, z:160, rotationY:-1});
entra("#s9-homem", 25.02, "dir", {dist:260, rot:3});
gsap.utils.toArray("#s9-bolhas .bolha").forEach((b, i) => { gsap.set(b, {opacity:0}); tl.fromTo(b, {opacity:0, scale:0, transformOrigin:"50% 50%"}, {opacity:1, scale:1, duration:0.25, ease:"back.out(2)", immediateRender:false}, 26.54 + i * 0.12); });
sfx("pop", 26.54);
""")

# ---- 27.12–31.22 treinar, estudar, economizar, começar o projeto
v.cena("s10", 27.12, 31.22, "escuro", [
    cartao("s10-a", "halter", 300, 600, "TREINAR", -2, "50% 0%", w=400, h=420),
    cartao("s10-b", "estudante", 770, 600, "ESTUDAR", 2, "50% 0%", w=400, h=420),
    cartao("s10-c", "cofrinho", 300, 1055, "ECONOMIZAR", 2, w=400, h=420),
    cartao("s10-d", "lampada", 770, 1055, "O PROJETO", -2, w=400, h=420),
], """
bz("#s10-bz", 27.12); cam("#s10-mundo", 27.12, 4.1, {x:-30, z:0, rotationY:-2}, {x:30, z:150, rotationY:2});
entra("#s10-a", 27.19, "pop", {rot:-10}); entra("#s10-b", 27.89, "pop", {rot:10}); entra("#s10-c", 28.61, "pop", {rot:-10}); entra("#s10-d", 29.41, "pop", {rot:10});
["#s10-a", "#s10-b", "#s10-c", "#s10-d"].forEach((s, i) => flutua(s, 27.8 + i * 0.7, 3.3 - i * 0.7, 5, 2.4 + i * 0.2, 0.8));
pulsa("#s10-d .card", 30.34, 0.8, 1.05);
""")

# ---- 31.22–33.60 mas continua adiando
ZZ = "".join(f'<text class="zz" x="{x}" y="{y}" style="font-size:{s}px">z</text>' for x, y, s in [(700, 870, 56), (755, 800, 76), (820, 715, 98)])
v.cena("s11", 31.22, 33.60, "tenso", [
    img("s11-cal", "calendario", 270, 700, 320, -120, dentro='<div class="calpag"><span id="s11-hoje">HOJE</span><span id="s11-amanha">AMANHÃ</span></div>'),
    img("s11-exec", "executivo", 500, 1070, 850, 0),
    svg("s11-zz", ZZ, 60),
    titulo("s11-tit", [(140, [("adiando...", 32.54, "ac")])], 540, 385),
], """
bz("#s11-bz", 31.22); cam("#s11-mundo", 31.22, 2.38, {x:20, z:0, rotationY:2}, {x:-20, z:170, rotationY:-2});
entra("#s11-exec", 31.25, "sobe"); entra("#s11-cal", 31.3, "pop", {rot:8});
tl.fromTo("#s11-exec > .fl", {scaleY:1}, {scaleY:1.018, transformOrigin:"50% 100%", duration:1.1, ease:"sine.inOut", yoyo:true, repeat:2, immediateRender:false}, 31.3);
gsap.set("#s11-amanha", {opacity:0, rotationX:-90});
tl.to("#s11-hoje", {rotationX:90, opacity:0, duration:0.22, ease:"power2.in"}, 31.48);
tl.fromTo("#s11-amanha", {rotationX:-90, opacity:0}, {rotationX:0, opacity:1, duration:0.26, ease:"power2.out", immediateRender:false}, 31.70);
sfx("tag", 31.70);
gsap.utils.toArray("#s11-zz .zz").forEach((z, i) => tl.fromTo(z, {opacity:0, y:30}, {opacity:1, y:0, duration:0.5, ease:"sine.out", immediateRender:false}, 31.6 + i * 0.35));
""")

# ---- 33.60–35.50 o benefício está lá na frente
v.cena("s12", 33.60, 35.50, "escuro", [
    brilho("s12-luz", 840, 760, 330, "255,196,20", .5, -800),
    selo("s12-trofeu", "trofeu", 840, 760, 200, z=-800),
    etiqueta("s12-tag", "BENEFÍCIO", 840, 900, 38, z=-780),
    linha("s12-cam", "M 360 1250 C 520 1160, 620 990, 800 860", z=-100, tracejada=True),
    linha("s12-seta", "M 680 590 H 900 M 855 545 L 905 590 L 855 635", z=60, cor="#ffffff", larg=11),
    img("s12-homem", "caminhante", 240, 1010, 280, 0),
    titulo("s12-tit", [(130, [("lá", 34.53, ""), ("na", 34.67, ""), ("frente", 34.89, "hl")])], 430, 385, w=700, alinha="left"),
], """
bz("#s12-bz", 33.60); cam("#s12-mundo", 33.60, 1.9, {x:-30, z:0, rotationY:-2}, {x:30, z:180, rotationY:2});
tl.fromTo("#s12-homem", {x:-60}, {x:150, duration:1.9, ease:"none", immediateRender:false}, 33.60);
tl.fromTo("#s12-homem > .fl", {y:0}, {y:-7, duration:0.28, ease:"sine.inOut", yoyo:true, repeat:6, immediateRender:false}, 33.60);
entra("#s12-trofeu", 33.62, "fade", {d:0.6}); entra("#s12-tag", 33.73, "pop");
traco("#s12-cam", 33.7, 1.0); traco("#s12-seta", 35.0, 0.35);
""")

# ---- 35.50–38.05 o desconforto está no aqui
v.cena("s13", 35.50, 38.05, "tenso", [
    brilho("s13-luz", 540, 1000, 520, "255,74,42", .4),
    img("s13-homem", "cansado", 540, 1010, 800, 0),
    titulo("s13-tit", [(120, [("desconforto", 35.82, "rd")])], 540, 380),
    carimbo("s13-aqui", "AQUI", 540, 450, 180, 150, -3),
    img("s13-mao", "mao", 489 + 350, -242 + 282, 700, 220),
], """
bz("#s13-bz", 35.50); cam("#s13-mundo", 35.50, 2.55, {z:0, rotationY:-2}, {z:180, rotationY:2});
entra("#s13-homem", 35.52, "sobe");
tl.fromTo("#s13-homem > .fl", {rotation:-1.2}, {rotation:1.2, transformOrigin:"50% 100%", duration:1.2, ease:"sine.inOut", yoyo:true, repeat:2, immediateRender:false}, 35.52);
sai("#s13-tit", 37.25, 0.2);
gsap.set("#s13-mao", {x:420, y:-420}); tl.fromTo("#s13-mao", {x:420, y:-420, rotation:8}, {x:0, y:0, rotation:0, duration:0.55, ease:"power3.out", immediateRender:false}, 37.0);
sfx("esq", 37.0); carimbo("#s13-aqui", 37.52);
""")

# ---- 38.05–40.62 o aqui e agora quase sempre vence
ANEIS = '<path id="s14-aneis" d="M 310 560 Q 280 610 310 660 M 270 540 Q 230 610 270 680 M 770 560 Q 800 610 770 660 M 810 540 Q 850 610 810 680" fill="none" stroke="#ffc414" stroke-width="7" stroke-linecap="round" class="luz"/>'
v.cena("s14", 38.05, 40.62, "tenso", [
    brilho("s14-luz", 540, 880, 480, "255,196,20", .35),
    img("s14-relogio", "despertador", 540, 880, 410, 0),
    svg("s14-svg", ANEIS, 20),
    img("s14-luva", "luva", 290, 990, 390, 200),
    titulo("s14-tit", [(116, [("o", 38.20, ""), ("aqui", 38.30, ""), ("e", 38.66, ""), ("agora", 38.72, "hl")])], 540, 385),
    carimbo("s14-vence", "VENCE", 610, 1115, 110, 220, -6),
], """
bz("#s14-bz", 38.05); cam("#s14-mundo", 38.05, 2.57, {x:20, z:0, rotationY:2}, {x:-20, z:180, rotationY:-2});
entra("#s14-relogio", 38.08, "sobe");
tl.fromTo("#s14-relogio > .fl", {rotation:-3.5}, {rotation:3.5, duration:0.05, ease:"none", yoyo:true, repeat:15, immediateRender:false}, 38.72);
gsap.set("#s14-aneis", {opacity:0}); tl.fromTo("#s14-aneis", {opacity:0}, {opacity:1, duration:0.05, yoyo:true, repeat:9, ease:"none", immediateRender:false}, 38.72);
gsap.set("#s14-luva", {x:-760}); tl.fromTo("#s14-luva", {x:-760, rotation:-30}, {x:0, rotation:-8, duration:0.26, ease:"power4.out", immediateRender:false}, 39.88);
sfx("esq", 39.88);
tl.to("#s14-relogio", {x:70, rotation:14, duration:0.3, ease:"power2.out"}, 40.12);
carimbo("#s14-vence", 40.11); soco("#s14-bz", 40.11, 1.06, 0.25);
""")

# ---- 40.62–43.10 virada: Clailton "então se você quiser corrigir esse defeito"
v.expert("assets/expert_1.mp4", 40.62, 2.48, cx=540, cy=760, w=560, h=700)
v.cena("s15", 40.62, 43.10, "quente", [raios("s15-raios", -500, .6), brilho("s15-luz", 540, 760, 620, "255,170,40", .55)], """
cam("#s15-mundo", 40.62, 2.48, {z:0}, {z:140});
gsap.set("#s15-raios", {opacity:0}); tl.fromTo("#s15-raios", {opacity:0, rotation:-4}, {opacity:.6, rotation:4, duration:2.48, ease:"sine.inOut", immediateRender:false}, 40.62);
sfx("virada", 40.2);
""", sobre=[
    img("s15-chave", "chave", 800, 400, 400, 0),
    titulo("s15-tit", [(84, [("corrigir", 41.53, "hl"), ("esse", 41.97, ""), ("defeito", 42.21, "ac")])], 540, 1150, 0),
], js_sobre="""
gsap.set("#s15-chave", {opacity:0}); tl.fromTo("#s15-chave", {x:520, rotation:40, opacity:0}, {x:0, rotation:-14, opacity:1, duration:0.55, ease:"power3.out", immediateRender:false}, 41.40);
sfx("dir", 41.40);
tl.fromTo("#s15-chave > .fl", {rotation:-6}, {rotation:6, transformOrigin:"70% 50%", duration:0.4, ease:"sine.inOut", yoyo:true, repeat:3, immediateRender:false}, 41.95);
""")

# ---- 43.10–49.85 pare de deixar a recompensa no futuro / traga para o presente
MOEDAS = "".join(f'<circle class="moeda" cx="{x}" cy="{y}" r="{r}" fill="#ffc414" stroke="#8a5d00" stroke-width="4"/>' for x, y, r in
                 [(430, 760, 16), (660, 720, 13), (380, 900, 11), (720, 860, 18), (560, 650, 12), (300, 820, 9), (790, 760, 10)])
v.cena("s16", 43.10, 49.85, "quente", [
    raios("s16-raios", -1600, .45),
    camada(-1300, '<div class="it" id="s16-bauw" style="left:550px; top:560px; width:420px; height:406px">'
                  '<div class="fl"><img class="rec" src="assets/img/bau.png" alt="" style="width:100%; height:100%" />'
                  '<div class="bautag"><span class="tag lin" id="s16-fut">FUTURO</span><span class="tag" id="s16-ago">AGORA</span></div></div></div>', nocomp=True, ident="s16-bauz"),
    brilho("s16-luz", 760, 760, 420, "255,196,20", .6, -1350),
    carimbo("s16-pare", "PARE", 540, 420, 120, 160, -5),
    titulo("s16-tit", [(70, [("toda", 44.68, ""), ("a", 45.00, "")]), (140, [("recompensa", 45.06, "hl")])], 540, 375),
    titulo("s16-tit2", [(80, [("para", 49.04, ""), ("o", 49.16, "")]), (150, [("presente", 49.24, "hl")])], 540, 375),
    svg("s16-moedas", MOEDAS, 120),
], """
bz("#s16-bz", 43.10); cam("#s16-mundo", 43.10, 3.9, {x:-20, z:0, rotationY:-2}, {x:20, z:120, rotationY:2});
cam("#s16-mundo", 47.0, 2.85, {x:20, z:120, rotationY:2}, {x:0, z:40, rotationY:0}, "power2.inOut");
entra("#s16-bauw", 43.15, "fade", {d:0.8}); flutua("#s16-bauw", 43.2, 6.6, 8, 2.6, 1.2);
gsap.set("#s16-luz", {opacity:0}); tl.fromTo("#s16-luz", {opacity:0}, {opacity:1, duration:1, immediateRender:false}, 43.3);
carimbo("#s16-pare", 43.17); sai("#s16-pare", 44.45, 0.2);
entra("#s16-fut", 46.19, "pop"); gsap.set("#s16-ago", {opacity:0});
sai("#s16-tit", 46.85, 0.25);
tl.fromTo("#s16-bauz", {z:-1300, x:0, y:0}, {z:0, x:-220, y:140, duration:1.4, ease:"power2.inOut", immediateRender:false}, 46.99);
sfx("doc", 46.99);
tl.to("#s16-luz", {opacity:0, duration:0.6}, 47.0);
tl.to("#s16-fut", {rotationX:90, opacity:0, duration:0.2, ease:"power2.in"}, 48.30);
tl.fromTo("#s16-ago", {rotationX:-90, opacity:0}, {rotationX:0, opacity:1, duration:0.24, ease:"power2.out", immediateRender:false}, 48.48);
gsap.utils.toArray("#s16-moedas .moeda").forEach((m, i) => { gsap.set(m, {opacity:0}); tl.fromTo(m, {opacity:0, y:60, scale:0.3, transformOrigin:"50% 50%"}, {opacity:1, y:-40 - (i % 3) * 30, scale:1, duration:0.6, ease:"power2.out", immediateRender:false}, 48.48 + i * 0.05); });
sfx("brilho", 48.48); soco("#s16-bz", 48.48, 1.05, 0.3);
""")

# ---- 49.85–54.58 quer treinar? série favorita depois do treino
v.cena("s17", 49.85, 54.58, "quente", [
    boneco("s17-homem", "halter", 290, 1000, 460, 0),
    img("s17-tv", "tv", 765, 950, 380, 0),
    linha("s17-seta", "M 450 625 C 510 585, 580 585, 630 620 M 596 596 L 634 622 L 598 650", z=30, larg=9),
    etiqueta("s17-t1", "1. TREINO", 290, 600, 46), etiqueta("s17-t2", "2. SÉRIE", 765, 600, 46),
    titulo("s17-tit", [(130, [("Quer", 49.89, ""), ("treinar?", 50.13, "ac")])], 540, 385),
    titulo("s17-tit2", [(84, [("depois", 53.46, ""), ("do", 53.96, ""), ("treino", 54.10, "hl")])], 540, 395),
], """
bz("#s17-bz", 49.85); cam("#s17-mundo", 49.85, 4.73, {x:-30, z:0, rotationY:-2}, {x:30, z:170, rotationY:2});
entra("#s17-homem", 49.9, "esq", {dist:300}); entra("#s17-t1", 50.13, "pop");
sai("#s17-tit", 52.2, 0.25);
entra("#s17-tv", 52.38, "dir", {dist:400}); flutua("#s17-tv", 53.0, 1.55, 6, 2.4, 1);
entra("#s17-t2", 52.62, "pop"); traco("#s17-seta", 53.46, 0.4);
""")

# ---- 54.58–59.42 precisa estudar? café depois de cumprir a meta
VAPOR = "".join(f'<path class="vapor" d="M {x} 1005 C {x - 16} 985, {x + 16} 965, {x} 945 C {x - 16} 925, {x + 16} 905, {x} 885" fill="none" stroke="#ffffff" stroke-width="9" stroke-linecap="round" opacity=".85"/>' for x in (705, 750, 795))
CHECK = '<path id="s18-check" class="luz" d="M 690 680 L 760 750 L 900 590" fill="none" stroke="#39d36a" stroke-width="22" stroke-linecap="round" stroke-linejoin="round"/>'
v.cena("s18", 54.58, 59.42, "quente", [
    boneco("s18-aluno", "estudante", 290, 1010, 440, 0),
    img("s18-alvo", "alvo", 800, 680, 290, 0),
    img("s18-cafe", "cafe", 750, 1130, 350, 0),
    svg("s18-vapor", VAPOR, 10), svg("s18-ok", CHECK, 40),
    etiqueta("s18-n1", "1. META", 800, 518, 42), etiqueta("s18-n2", "2. CAFÉ", 750, 1255, 42),
    titulo("s18-tit", [(120, [("Precisa", 54.63, ""), ("estudar?", 54.99, "ac")])], 540, 385),
    titulo("s18-tit2", [(100, [("cumprir", 58.30, ""), ("essa", 58.68, ""), ("meta", 58.94, "hl")])], 540, 395),
], """
bz("#s18-bz", 54.58); cam("#s18-mundo", 54.58, 4.84, {x:30, z:0, rotationY:2}, {x:-30, z:170, rotationY:-2});
entra("#s18-aluno", 54.63, "esq", {dist:300});
entra("#s18-cafe", 56.79, "pop"); flutua("#s18-cafe", 57.3, 2.1, 5, 2.4, 1);
gsap.utils.toArray("#s18-vapor .vapor").forEach((p, i) => tl.fromTo(p, {opacity:0, y:30}, {opacity:.85, y:-30, duration:1.2, ease:"sine.out", immediateRender:false}, 57.0 + i * 0.25));
sai("#s18-tit", 57.7, 0.25);
entra("#s18-alvo", 58.30, "pop", {rot:-14}); traco("#s18-check", 58.94, 0.3); sfx("ok", 58.94);
entra("#s18-n1", 59.05, "pop"); entra("#s18-n2", 59.18, "pop");
""")

# ---- 59.42–65.52 faça o teu cérebro sentir agora uma parte do benefício
v.cena("s19", 59.42, 65.52, "quente", [
    brilho("s19-luz", 540, 880, 560, "255,170,40", .7),
    img("s19-cerebro", "cerebro", 540, 880, 560, 0),
    selo("s19-trofeu", "trofeu", 860, 620, 180, z=120),
    img("s19-amp", "ampulheta", 220, 720, 250, -800, cls="rec longe"),
    titulo("s19-tit", [(140, [("sentir", 60.60, ""), ("agora", 61.20, "hl")])], 540, 385),
    titulo("s19-tit2", [(84, [("uma", 62.02, ""), ("parte", 62.28, "ac"), ("do", 62.56, "")]), (120, [("benefício", 62.69, "hl")])], 540, 365),
    titulo("s19-tit3", [(80, [("muito", 64.37, ""), ("tempo", 64.63, ""), ("depois", 64.85, "ac")])], 540, 1150, 160),
], """
bz("#s19-bz", 59.42); cam("#s19-mundo", 59.42, 6.1, {x:-20, z:0, rotationY:-2}, {x:20, z:220, rotationY:2});
entra("#s19-cerebro", 59.46, "pop"); flutua("#s19-cerebro", 60.0, 5.5, 7, 2.8, 1);
gsap.set("#s19-luz", {opacity:0}); tl.fromTo("#s19-luz", {opacity:0, scale:.6}, {opacity:1, scale:1, duration:0.6, ease:"power2.out", immediateRender:false}, 60.60);
tl.fromTo("#s19-luz", {scale:1}, {scale:1.12, duration:0.5, ease:"sine.inOut", yoyo:true, repeat:7, immediateRender:false}, 61.2);
soco("#s19-bz", 61.20, 1.05, 0.3); sfx("brilho", 60.6);
sai("#s19-tit", 61.9, 0.2);
entra("#s19-trofeu", 62.69, "dir", {dist:300}); flutua("#s19-trofeu", 63.2, 2.3, 6, 2.2, 2);
entra("#s19-amp", 64.37, "fade", {d:0.6}); sai("#s19-tit2", 64.25, 0.2);
""")

# ---- 65.52–68.52 dê ao presente uma pequena recompensa
BRILHOS = "".join(f'<path class="faisca" d="M {x} {y - s} L {x + s * .25} {y - s * .25} L {x + s} {y} L {x + s * .25} {y + s * .25} L {x} {y + s} L {x - s * .25} {y + s * .25} L {x - s} {y} L {x - s * .25} {y - s * .25} Z" fill="#ffc414"/>'
                  for x, y, s in [(300, 720, 34), (790, 680, 28), (250, 1050, 22), (840, 1020, 36), (560, 600, 20)])
v.cena("s20", 65.52, 68.52, "quente", [
    raios("s20-raios", -500, .5),
    brilho("s20-luz", 540, 900, 480, "255,170,40", .55),
    img("s20-presente", "presente", 540, 900, 500, 0),
    svg("s20-faiscas", BRILHOS, 80),
    titulo("s20-tit", [(56, [("Dê", 65.57, ""), ("ao", 65.89, ""), ("presente", 66.03, "ac")]), (62, [("uma", 66.70, ""), ("pequena", 66.92, ""), ("recompensa", 67.48, "hl")])], 540, 385),
], """
bz("#s20-bz", 65.52); cam("#s20-mundo", 65.52, 3.0, {x:20, z:0, rotationY:2}, {x:-20, z:180, rotationY:-2});
entra("#s20-presente", 65.57, "pop", {rot:-10}); flutua("#s20-presente", 66.2, 2.3, 7, 2.4, 1.5);
tl.to("#s20-presente", {scale:0.78, duration:0.5, ease:"power2.inOut"}, 66.92);
gsap.utils.toArray("#s20-faiscas .faisca").forEach((f, i) => { gsap.set(f, {opacity:0}); tl.fromTo(f, {opacity:0, scale:0, rotation:-40, transformOrigin:"50% 50%"}, {opacity:1, scale:1, rotation:0, duration:0.3, ease:"back.out(2)", immediateRender:false}, 67.48 + i * 0.07); });
sfx("brilho", 67.48);
""")

# ---- 68.52–71.05 sem deixar que ele roube o teu futuro
ESCUDO = '<circle id="s21-escudo" class="luz" cx="540" cy="1000" r="350" fill="none" stroke="#ffc414" stroke-width="12" stroke-dasharray="40 22"/>'
v.cena("s21", 68.52, 71.05, "quente", [
    brilho("s21-luz", 540, 1000, 540, "255,196,20", .55),
    img("s21-amp", "ampulheta", 540, 1000, 420, 0),
    svg("s21-svg", ESCUDO, 30),
    img("s21-mao", "mao", 529 + 350, 88 + 282, 700, 220),
    titulo("s21-tit", [(80, [("o", 70.25, ""), ("teu", 70.31, "")]), (150, [("futuro", 70.47, "hl")])], 540, 375),
], """
bz("#s21-bz", 68.52); cam("#s21-mundo", 68.52, 2.53, {z:0, rotationY:-2}, {z:160, rotationY:2});
entra("#s21-amp", 68.55, "sobe"); flutua("#s21-amp", 69.0, 2.0, 6, 2.6, 1);
gsap.set("#s21-mao", {x:520, y:-520}); tl.fromTo("#s21-mao", {x:520, y:-520, rotation:10}, {x:30, y:-30, rotation:2, duration:1.1, ease:"power2.inOut", immediateRender:false}, 68.85);
sfx("esq", 68.85);
tl.to("#s21-mao", {x:600, y:-600, rotation:14, duration:0.45, ease:"power3.in"}, 70.0);
traco("#s21-escudo", 69.92, 0.45); sfx("soco", 69.95);
tl.fromTo("#s21-escudo", {strokeDashoffset:0}, {strokeDashoffset:-310, duration:1.1, ease:"none", immediateRender:false}, 69.92);
soco("#s21-bz", 69.95, 1.04, 0.3);
""")

# ---- 71.05–73.60 CTA digitada
v.cena("s22", 71.05, 73.60, "quente", [
    raios("s22-raios", -500, .5),
    img("s22-cerebro", "cerebro", 540, 640, 300, 0),
    camada(120, f'<div class="it ctr cta" id="s22-cta" style="left:80px; top:960px; width:920px"><div>{letras("ME SIGA PARA MAIS")}</div><div class="ac">{letras("CONTEÚDOS COMO ESTE")}</div></div>'),
], """
bz("#s22-bz", 71.05); cam("#s22-mundo", 71.05, 2.55, {z:0}, {z:140});
entra("#s22-cerebro", 71.08, "pop"); flutua("#s22-cerebro", 71.6, 2.0, 6, 2.4, 2);
sfx("teclado", 71.30); digita("#s22-cta .ch", 71.32, 0.03);
""")

v.legenda(troca={30: "Laibson"},
          destaque={2, 6, 7, 8, 13, 24, 29, 30, 37, 38, 49, 53, 58, 67, 68, 69, 73, 76, 80, 81, 82, 88, 91, 93, 96, 101, 103, 109, 117, 120, 122,
                    128, 129, 134, 137, 143, 148, 149, 153, 157, 158, 159, 162, 164, 165, 170, 173},
          fora={25, 26})
v.gerar()
