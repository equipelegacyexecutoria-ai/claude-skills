"""Exporta um Motion Dinâmico como projeto para o Premiere (XML do Final Cut 7 / xmeml v5), em camadas editáveis.

Pasta <saida>/ (ex.: "Reels Editados/<nome> - PREMIERE"):
  <nome>.xml           Arquivo > Importar no Premiere: cria a sequência 1080x1920 30 fps
  midia/fundo.mp4      V1: fundo, elementos, Clailton e animações, SEM os textos
  midia/textos.mov     V2: textos, carimbos, etiquetas, números e CTA com transparência (ProRes 4444)
  midia/final.mp4      V3 (desligada): o vídeo final aprovado, para comparar
  midia/audio/...      voz, cada trilha e cada efeito sonoro, como clipes separados
  LEIA-ME.txt          o que está em cada trilha

Trilhas de áudio: A1 voz · A2/A3 trilhas (alternadas para cruzar) · A4+ efeitos sonoros · última: mix final (desligada).
Os volumes e fades vêm do mix.json (montar_mix.py). No Premiere ficam fora: o abaixar da música sob a voz (use
Som Essencial > Música > Redução automática) e a normalização final a -14 LUFS (Normalizar volume de pico/sonoridade).

Uso: python premiere_motion.py <projeto> <saida> [--nome NOME] [--sem-render]
"""
import html, json, os, re, shutil, subprocess, sys
from pathlib import Path
from urllib.parse import quote

args = [a for a in sys.argv[1:] if not a.startswith("--")]
PROJ, SAIDA = Path(args[0]).resolve(), Path(args[1]).resolve()
NOME = sys.argv[sys.argv.index("--nome") + 1] if "--nome" in sys.argv else SAIDA.name.replace(" - PREMIERE", "")
SEM_RENDER = "--sem-render" in sys.argv
FPS, W, H = 30, 1080, 1920
RATE = "<rate><timebase>30</timebase><ntsc>FALSE</ntsc></rate>"
MID = SAIDA / "midia"; AUD = MID / "audio"
AUD.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- camadas de vídeo (render separado)
CSS_FUNDO = ".tit, .ctr, .cta { visibility: hidden !important; }"
CSS_TEXTOS = ("html, body, #root { background: transparent !important; } "
              ".fundo, .pontos, #acab, .raios, .moldura, .expert { display: none !important; } "
              ".z > .it:not(.tit):not(.ctr) { visibility: hidden !important; } .boneco img { visibility: hidden !important; }")


def variante(nome, css):
    src = (PROJ / "index.html").read_text(encoding="utf-8")
    assert "</style>" in src
    (PROJ / nome).write_text(src.replace("</style>", "  " + css + "\n    </style>", 1), encoding="utf-8")
    return nome


def render(comp, saida, fmt):
    cmd = f'npx hyperframes render -c {comp} --quality high --fps {FPS} --quiet --format {fmt} -o "{saida}"'
    subprocess.run(cmd, cwd=PROJ, shell=True, check=True)


if not SEM_RENDER:
    tmp = MID / "_fundo_com_audio.mp4"
    render(variante("camada_fundo.html", CSS_FUNDO), tmp, "mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-an", "-c:v", "copy", str(MID / "fundo.mp4")], check=True)
    tmp.unlink()
    render(variante("camada_textos.html", CSS_TEXTOS), MID / "textos.mov", "mov")
    for f in ("camada_fundo.html", "camada_textos.html"):
        (PROJ / f).unlink(missing_ok=True)


def dur_s(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True)
    return float(r.stdout.strip())


# ---------------------------------------------------------------- XML
def url(p):
    return "file://localhost/" + quote(str(Path(p).resolve()).replace("\\", "/"), safe="/:")


esc = lambda s: html.escape(str(s), quote=False)
ids = {}


def ref(p, n, video=True, ch=2):
    k = str(Path(p).resolve())
    if k in ids:
        return f'<file id="{ids[k]}"/>'
    ids[k] = f"file-{len(ids) + 1}"
    m = (f"<video><samplecharacteristics>{RATE}<width>{W}</width><height>{H}</height><pixelaspectratio>square</pixelaspectratio>"
         "</samplecharacteristics></video>") if video else ""
    m += (f"<audio><samplecharacteristics><depth>16</depth><samplerate>48000</samplerate></samplecharacteristics>"
          f"<channelcount>{ch}</channelcount></audio>") if ch else ""
    return f'<file id="{ids[k]}"><name>{esc(Path(p).name)}</name><pathurl>{url(p)}</pathurl>{RATE}<duration>{n}</duration><media>{m}</media></file>'


def nivel(pontos):
    """pontos: [(quadro, ganho linear)] -> Audio Levels com quadros-chave (fades)."""
    if len(pontos) == 1:
        v = f"<value>{min(pontos[0][1], 3.98):.5f}</value>"
    else:
        v = "".join(f"<keyframe><when>{q}</when><value>{min(g, 3.98):.5f}</value></keyframe>" for q, g in pontos)
    return ("<filter><effect><name>Audio Levels</name><effectid>audiolevels</effectid><effectcategory>audiolevels</effectcategory>"
            "<effecttype>audiolevels</effecttype><mediatype>audio</mediatype><parameter><parameterid>level</parameterid>"
            f"<name>Level</name><valuemin>0</valuemin><valuemax>3.98109</valuemax>{v}</parameter></effect></filter>")


def clip(cid, nome, ini, fim, ent, sai, arq, extra="", ligado=True, tipo="video", dur=None):
    st = f"<sourcetrack><mediatype>{tipo}</mediatype><trackindex>1</trackindex></sourcetrack>"
    return (f'<clipitem id="{cid}"><name>{esc(nome)}</name><enabled>{"TRUE" if ligado else "FALSE"}</enabled>'
            f"<duration>{dur or (sai - ent)}</duration>{RATE}<start>{ini}</start><end>{fim}</end><in>{ent}</in><out>{sai}</out>"
            f"{arq}{st}{extra}</clipitem>")


q = lambda s: int(round(s * FPS))
mix = json.load(open(PROJ / "assets" / "audio" / "mix.json", encoding="utf-8"))
TOT = q(mix["duracao"])
final = MID / "final.mp4"
if not final.exists():
    renders = sorted((PROJ / "renders").glob("*.mp4"), key=os.path.getmtime)
    if renders:
        shutil.copy2(renders[-1], final)

v1 = [clip("v1-fundo", "fundo e animações", 0, TOT, 0, TOT, ref(MID / "fundo.mp4", TOT, ch=0))]
v2 = [clip("v2-textos", "textos (transparente)", 0, TOT, 0, TOT, ref(MID / "textos.mov", TOT, ch=0))]
v3 = [clip("v3-final", "referência: final aprovado", 0, TOT, 0, TOT, ref(final, TOT, ch=2), ligado=False)] if final.exists() else []


def copia(rel):
    src = PROJ / "assets" / "audio" / rel
    dst = AUD / rel.replace("/", "_")
    if not dst.exists():
        shutil.copy2(src, dst)
    return dst


# voz
vz = copia(mix["voz"]["arquivo"]); nv = q(dur_s(vz))
a1 = [clip("a1-voz", "voz", 0, min(nv, TOT), 0, min(nv, TOT), ref(vz, nv, video=False, ch=1), nivel([(0, mix["voz"].get("volume", 1))]), tipo="audio", dur=nv)]
# trilhas (alternando A2/A3 para poderem cruzar)
a2, a3 = [], []
for k, t in enumerate(mix["trilhas"]):
    f = copia(t["arquivo"]); nf = q(dur_s(f))
    ini, fim = q(t["entra"]), q(t["sai"]); ent = q(t.get("inicio_no_arquivo", 0)); sai = ent + (fim - ini)
    vol = t.get("volume", 0.6); fi, fo = q(t.get("fade_entrada", 0.05)), q(t.get("fade_saida", 1.0))
    pts = [(ent, 0.0), (ent + max(1, fi), vol), (sai - max(1, fo), vol), (sai, 0.0)]
    (a2 if k % 2 == 0 else a3).append(clip(f"musica-{k}", Path(t["arquivo"]).stem, ini, fim, ent, sai, ref(f, nf, video=False, ch=2),
                                           nivel(pts), tipo="audio", dur=nf))
# efeitos: cada um numa trilha livre (sem sobrepor)
trilhas_fx = []
for k, e in enumerate(sorted(mix["efeitos"], key=lambda e: e["momento"] - e.get("pico", 0))):
    f = copia(e["arquivo"]); nf = q(dur_s(f))
    ini = max(0, q(e["momento"] - e.get("pico", 0))); fim = min(TOT, ini + nf)
    if fim <= ini:
        continue
    c = clip(f"fx-{k}", Path(e["arquivo"]).stem, ini, fim, 0, fim - ini, ref(f, nf, video=False, ch=2), nivel([(0, e.get("volume", 0.5))]), tipo="audio", dur=nf)
    for tr in trilhas_fx:
        if tr[-1][0] <= ini:
            tr.append((fim, c)); break
    else:
        trilhas_fx.append([(fim, c)])
mx = PROJ / "assets" / "audio" / "mix.wav"
shutil.copy2(mx, AUD / "mix_final.wav")
am = [clip("mix-final", "referência: mix final", 0, TOT, 0, TOT, ref(AUD / "mix_final.wav", TOT, video=False, ch=2), ligado=False, tipo="audio")]

trilha = lambda itens: "<track>" + "".join(itens) + "</track>"
audio = [a1, a2, a3] + [[c for _, c in tr] for tr in trilhas_fx] + [am]
xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>\n<xmeml version="5">'
       f'<sequence id="sequence-1"><name>{esc(NOME)}</name><duration>{TOT}</duration>{RATE}'
       f"<timecode>{RATE}<string>00:00:00:00</string><frame>0</frame><displayformat>NDF</displayformat></timecode>"
       f"<media><video><format><samplecharacteristics>{RATE}<width>{W}</width><height>{H}</height><anamorphic>FALSE</anamorphic>"
       "<pixelaspectratio>square</pixelaspectratio><fielddominance>none</fielddominance></samplecharacteristics></format>"
       + trilha(v1) + trilha(v2) + (trilha(v3) if v3 else "") + "</video><audio>"
       "<format><samplecharacteristics><depth>16</depth><samplerate>48000</samplerate></samplecharacteristics></format>"
       + "".join(trilha(a) for a in audio if a) + "</audio></media></sequence></xmeml>\n")
import xml.dom.minidom as md
md.parseString(xml.encode("utf-8"))
(SAIDA / f"{NOME}.xml").write_text(xml, encoding="utf-8")
(SAIDA / "LEIA-ME.txt").write_text(f"""Projeto do Premiere: {NOME}

Como abrir: Premiere > Arquivo > Importar > {NOME}.xml (deixe a pasta "midia" ao lado do XML).
Se o Premiere pedir para localizar mídia, aponte para a pasta "midia".

Vídeo
  V1  fundo.mp4     fundo, elementos, Clailton e animações (sem os textos)
  V2  textos.mov    textos, carimbos, etiquetas, números e chamada final, com fundo transparente
                    (para mudar um texto: esconda o trecho com uma máscara e escreva por cima no Premiere)
  V3  final.mp4     o vídeo final aprovado, desligado, só para comparar

Áudio
  A1     voz do Clailton (já tratada)
  A2/A3  trilhas do Artlist, uma por emoção, alternadas para poderem se cruzar (fades em quadros-chave)
  A4+    efeitos sonoros, cada um no momento da animação
  último mix final aprovado, desligado, para comparar

No mix final a música abaixa sozinha sob a voz e tudo é normalizado a -14 LUFS.
No Premiere: Som Essencial > Música > Redução automática, e Normalizar sonoridade para -14 LUFS na exportação.
""", encoding="utf-8")
print("ok", SAIDA / f"{NOME}.xml", "| A:", len(audio), "trilhas de áudio |", len([c for tr in trilhas_fx for c in tr]), "efeitos")
