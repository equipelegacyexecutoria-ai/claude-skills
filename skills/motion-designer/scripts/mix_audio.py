"""Mixa narração + trilhas + efeitos num WAV com a duração exata do vídeo (-14 LUFS).

Uso: python mix_audio.py config.json   (formato do JSON em references/audio.md)

- voz: acelerada (atempo) e atrasada (inicio);
- trilhas: cada uma toca do 'inicio_no_arquivo', entra em 'entra' e termina em 'sai' (com fade);
- música abaixa sozinha sob a voz (sidechain) e vai até o fim do vídeo;
- efeitos: posicionados pelo PICO ('momento' = onde o pico cai no vídeo; 'pico' = onde ele está no arquivo).
"""
import json, os, subprocess, sys

cfg = json.load(open(sys.argv[1], encoding="utf-8"))
base_dir = os.path.dirname(os.path.abspath(sys.argv[1]))
caminho = lambda p: p if os.path.isabs(p) else os.path.join(base_dir, p)

DUR = float(cfg["duracao"])
voz = cfg.get("voz")
trilhas = cfg.get("trilhas", [])
efeitos = cfg.get("efeitos", [])
saida = caminho(cfg.get("saida", "mix_final.wav"))

entradas, fc, idx = [], [], 0
rot_mus = []
if voz:
    entradas += ["-i", caminho(voz["arquivo"])]
    fc.append(f"[{idx}:a]atempo={voz.get('atempo', 1.0)},adelay={int(voz.get('inicio', 0)*1000)}:all=1,"
              f"aresample=48000,pan=stereo|c0=c0|c1=c0,volume={voz.get('volume', 1.0)},asplit=2[voz1][vozsc]")
    idx += 1
for i, t in enumerate(trilhas):
    entradas += ["-i", caminho(t["arquivo"])]
    entra, sai = float(t.get("entra", 0)), float(t.get("sai", DUR))
    dur_t = sai - entra
    fo = float(t.get("fade_saida", 1.0))
    fi = float(t.get("fade_entrada", 0.05))
    fc.append(f"[{idx}:a]atrim=start={t.get('inicio_no_arquivo', 0)}:duration={dur_t + 0.3},asetpts=PTS-STARTPTS,"
              f"aresample=48000,aformat=channel_layouts=stereo,volume={t.get('volume', 0.6)},"
              f"afade=t=in:d={fi},afade=t=out:st={max(0, dur_t - fo)}:d={fo},"
              f"adelay={int(entra*1000)}:all=1[m{i}]")
    rot_mus.append(f"[m{i}]")
    idx += 1
fc.append(f"anullsrc=r=48000:cl=stereo,atrim=duration={DUR}[mbase]")
fc.append(f"[mbase]{''.join(rot_mus)}amix=inputs={len(rot_mus)+1}:normalize=0:duration=first[mus0]")
if voz:
    sc = cfg.get("abaixar_musica_sob_voz", {"threshold": 0.05, "ratio": 3})
    fc.append(f"[vozsc]apad=whole_dur={DUR}[vozpad]")
    fc.append(f"[mus0][vozpad]sidechaincompress=threshold={sc['threshold']}:ratio={sc['ratio']}:attack=20:release=300[mus]")
else:
    fc.append("[mus0]anull[mus]")
rot = []
for j, e in enumerate(efeitos):
    entradas += ["-i", caminho(e["arquivo"])]
    atraso = max(0, int(round((float(e["momento"]) - float(e.get("pico", 0))) * 1000)))
    fc.append(f"[{idx}:a]aresample=48000,aformat=channel_layouts=stereo,volume={e.get('volume', 0.5)},adelay={atraso}:all=1[s{j}]")
    rot.append(f"[s{j}]")
    idx += 1
fc.append(f"anullsrc=r=48000:cl=stereo,atrim=duration={DUR}[base]")
mistura = "[base]" + ("[voz1]" if voz else "") + "[mus]" + "".join(rot)
n = 2 + (1 if voz else 0) + len(rot)
fc.append(f"{mistura}amix=inputs={n}:normalize=0:duration=first,alimiter=limit=0.89[pre]")
fc.append(f"[pre]loudnorm=I={cfg.get('loudness', -14)}:TP=-1.5:LRA=11[out]")

os.makedirs(os.path.dirname(saida) or ".", exist_ok=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", *entradas, "-filter_complex", ";".join(fc),
                "-map", "[out]", "-ar", "48000", "-c:a", "pcm_s16le", saida], check=True)
print("ok", saida)
