"""Põe pausas na narração depois das frases (cadência de tutorial).
uso: pausas.py <voz_bruta.mp3> <saida.wav> idx:seg idx:seg ...  (idx = palavra do .palavras.json; pausa entra no meio do silêncio depois dela)
"""
import io, json, subprocess, sys
src, out = sys.argv[1], sys.argv[2]
ws = json.load(io.open(src + ".palavras.json", encoding="utf-8"))
cuts = []
for a in sys.argv[3:]:
    i, p = a.split(":")
    if i.startswith("t"):
        c = float(i[1:])
    else:
        i = int(i); c = (ws[i]["e"] + ws[i + 1]["s"]) / 2 if i + 1 < len(ws) else ws[i]["e"] + 0.1
    cuts.append((c, float(p)))
import numpy as np
raw = subprocess.run(["ffmpeg","-v","error","-i",src,"-ac","1","-ar","16000","-f","f32le","-"],capture_output=True).stdout
A = np.frombuffer(raw, np.float32); SR=16000; REF=np.sqrt(np.mean(A**2))
H=160; env=np.array([np.sqrt(np.mean(A[i:i+H]**2)) for i in range(0,len(A)-H,H)])/REF  # 10 ms
def snap(c):
    lo=int((c-0.35)*100); hi=int((c+0.55)*100); best=None; i=lo
    while i<hi:
        if 0<=i<len(env) and env[i]<0.03:
            j=i
            while j<len(env) and env[j]<0.03: j+=1
            if best is None or (j-i)>best[1]-best[0]: best=(i,j)
            i=j
        else: i+=1
    if best is None: print("SEM SILENCIO perto de",c); return c
    return (best[0]+best[1])/2/100
cuts=[(snap(c),p) for c,p in cuts]
cuts.sort()
fl, prev, k = [], 0.0, 0
labels = []
for c, p in cuts + [(None, 0)]:
    end = f":end={c:.3f}" if c is not None else ""
    fl.append(f"[0:a]atrim=start={prev:.3f}{end},asetpts=PTS-STARTPTS[a{k}]"); labels.append(f"[a{k}]"); k += 1
    if c is not None:
        fl.append(f"anullsrc=r=44100:cl=mono,atrim=duration={p:.3f}[s{k}]"); labels.append(f"[s{k}]"); k += 1
        prev = c
fl.append("".join(labels) + f"concat=n={len(labels)}:v=0:a=1[o]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", ";".join(fl), "-map", "[o]", "-ac", "1", "-ar", "44100", out], check=True)
print("ok", out, "cortes:", [(round(c, 2), p) for c, p in cuts])
