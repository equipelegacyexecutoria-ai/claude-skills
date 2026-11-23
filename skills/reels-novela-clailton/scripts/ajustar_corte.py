"""Ajuste cirúrgico do corte de um NV já entregue, sem refazer decupagem/legenda/B-roll.
uso: ajustar_corte.py <trabalho> estender <k> <quadros>     (fim do segmento k avança N quadros no bruto)
     ajustar_corte.py <trabalho> juntar <k>                 (segmento k vai até o fim do k+1, sem o corte entre eles)
Empurra tudo o que vem depois (legenda.ass, broll.json, palavras_corte.json, dst_in) pelo mesmo tempo.
Guarda cópia dos arquivos em <trabalho>/antes_ajuste_<n>/ antes de mexer.
Depois: render_final.py <trabalho> <saida sem música>.
"""
import json, os, re, shutil, sys

T, op, k = sys.argv[1], sys.argv[2], int(sys.argv[3])
cj = os.path.join(T, "corte.json")
c = json.load(open(cj, encoding="utf-8"))
fps = c["fps"]
segs = c["segmentos"]
n = 1
while os.path.exists(os.path.join(T, f"antes_ajuste_{n}")):
    n += 1
bk = os.path.join(T, f"antes_ajuste_{n}")
os.makedirs(bk)
for f in ["corte.json", "legenda.ass", "broll.json", "palavras_corte.json"]:
    if os.path.exists(os.path.join(T, f)):
        shutil.copy(os.path.join(T, f), bk)
t_corte = sum(s["frames"] for s in segs[:k + 1]) / fps      # fim do segmento k na linha do tempo
if op == "estender":
    q = int(sys.argv[4])
    segs[k]["frames"] += q
    segs[k]["src_out"] = round(segs[k]["src_out"] + q / fps, 4)
elif op == "juntar":
    a, b = segs[k], segs[k + 1]
    q = (b["frame_in"] + b["frames"]) - (a["frame_in"] + a["frames"]) - b["frames"]   # quadros do buraco entre eles
    a["frames"] = b["frame_in"] + b["frames"] - a["frame_in"]
    a["src_out"] = b["src_out"]
    a["i1"] = max(a.get("i1", 0), b.get("i1", 0))
    for key in ("fala_out", "voz_out", "db_out"):
        if key in b:
            a[key] = b[key]
    del segs[k + 1]
else:
    sys.exit("op: estender | juntar")
d = q / fps
acc = 0.0
for s in segs:
    s["dst_in"] = round(acc, 4)
    acc += s["frames"] / fps
if "duracao_fala" in c:
    c["duracao_fala"] = round(c["duracao_fala"] + d, 4)
json.dump(c, open(cj, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def desloca(t):
    return t + d if t >= t_corte - 1e-3 else t


def seg_ass(s):
    h, m, x = s.split(":")
    return int(h) * 3600 + int(m) * 60 + float(x)


def fmt(t):
    h = int(t // 3600); m = int(t % 3600 // 60); x = t - h * 3600 - m * 60
    return f"{h}:{m:02d}:{x:05.2f}"


la = os.path.join(T, "legenda.ass")
out = []
for ln in open(la, encoding="utf-8").read().splitlines():
    if ln.startswith("Dialogue:"):
        p = ln.split(",", 9)
        a0, b0 = seg_ass(p[1]), seg_ass(p[2])
        p[1] = fmt(desloca(a0)); p[2] = fmt(b0 + d if b0 > t_corte - 1e-3 else b0)
        ln = ",".join(p)
    out.append(ln)
open(la, "w", encoding="utf-8").write("\n".join(out) + "\n")
bj = os.path.join(T, "broll.json")
if os.path.exists(bj):
    br = json.load(open(bj, encoding="utf-8"))
    for b in br:
        fim0 = b["fim"]
        b["inicio"] = round(desloca(b["inicio"]), 4)
        b["fim"] = round(fim0 + d if fim0 > t_corte - 1e-3 else fim0, 4)
    json.dump(br, open(bj, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
pj = os.path.join(T, "palavras_corte.json")
if os.path.exists(pj):
    pc = json.load(open(pj, encoding="utf-8"))
    for w in pc["palavras"]:
        w["inicio"] = round(desloca(w["inicio"]), 4); w["fim"] = round(desloca(w["fim"]), 4)
    json.dump(pc, open(pj, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"ok: {op} seg {k}, +{q} quadros ({d:.3f} s) a partir de {t_corte:.2f} s; cópia em {bk}")
# layout.json da legenda: CTA começa no novo fim da fala e o hash das palavras confere (o render_final cobra)
lj = os.path.join(T, "layout.json")
if os.path.exists(lj):
    import hashlib
    shutil.copy(lj, bk)
    L = json.load(open(lj, encoding="utf-8"))
    L["cta_inicio"] = round(float(L["cta_inicio"]) + d, 4)
    L["duracao_total"] = round(float(L["duracao_total"]) + d, 4)
    if os.path.exists(pj):
        L["palavras_sha256"] = hashlib.sha256(open(pj, "rb").read()).hexdigest()
    json.dump(L, open(lj, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
