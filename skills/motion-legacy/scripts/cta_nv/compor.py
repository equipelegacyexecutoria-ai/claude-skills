"""Encaixa a CTA motion-legacy (cta_legacy/render/cta.mp4) no fim da novela NV_CTA e soma os efeitos (sem música).
Depois: mixar_alto.py <cta_legacy/composto_sem_musica.mov> <musica> <saida> <ini_musica> 10 cta <inicio_cta>

  python compor.py <slug>
Base: sem_motion.mp4 (ou v1_sem_musica.mp4) da pasta do trabalho.
"""
import json, subprocess, sys
from pathlib import Path

slug = sys.argv[1]
T = Path(r"C:\Render\_trabalho") / slug
M = T / "cta_legacy"
base = T / "sem_motion.mp4"
if not base.exists():
    base = T / "v1_sem_musica.mp4"
m = json.load(open(M / "motion.json"))
O, D, fim = m["inicio"], m["duracao"], m["fim_fala"]
TOT = O + D
ins = ["-i", str(base), "-itsoffset", f"{O:.3f}", "-i", str(M / "render/cta.mp4")]
# corte da decupagem pouco antes do flash: congela o último quadro antes do corte até o início da animação
c = json.load(open(T / "corte.json", encoding="utf-8"))
cortes, t = [], 0.0
for sg in c["segmentos"]:
    cortes.append(t)
    t += sg["frames"] * 1001 / 30000
cc = [x for x in cortes if O - 0.6 < x < O - 0.01]
if cc:
    c0 = cc[-1] - 1001 / 30000 / 2
    vb = (f"[0:v]split=2[x0][y0];[x0]trim=0:{c0:.4f},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={O - c0:.4f}[p1];"
          f"[y0]trim=start={O:.4f},setpts=PTS-STARTPTS[p2];[p1][p2]concat=n=2:v=1:a=0,"
          f"tpad=stop_mode=clone:stop_duration=8,trim=0:{TOT:.3f},setpts=PTS-STARTPTS[b]")
else:
    vb = f"[0:v]tpad=stop_mode=clone:stop_duration=8,trim=0:{TOT:.3f},setpts=PTS-STARTPTS[b]"
f = [vb,
     f"[b][1:v]overlay=eof_action=repeat:enable='gte(t,{O:.3f})',format=yuv420p[v]",
     f"[0:a]aresample=48000,atrim=0:{fim + 0.12:.3f},afade=t=out:st={fim + 0.04:.3f}:d=0.08,apad=whole_dur={TOT:.3f}[voz]"]
labs = []
for k, (tt, arq, g) in enumerate(m["sfx"]):
    ins += ["-i", arq]
    f.append(f"[{k + 2}:a]asetpts=N/SR/TB,aresample=48000,aformat=channel_layouts=stereo,volume={g}dB,adelay={int(tt * 1000)}:all=1[s{k}]")
    labs.append(f"[s{k}]")
f.append(f"[voz]{''.join(labs)}amix=inputs={len(labs) + 1}:duration=first:normalize=0,atrim=0:{TOT:.3f}[a]")
out = M / "composto_sem_musica.mov"
subprocess.run(["ffmpeg", "-v", "error", "-y"] + ins + ["-filter_complex", ";".join(f), "-map", "[v]", "-map", "[a]",
                "-t", f"{TOT:.3f}", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high", "-colorspace", "bt709",
                "-color_primaries", "bt709", "-color_trc", "bt709", "-r", "30000/1001", "-c:a", "pcm_s16le", str(out)], check=True)
print("ok", out, f"{TOT:.2f}s", "base", base.name)
