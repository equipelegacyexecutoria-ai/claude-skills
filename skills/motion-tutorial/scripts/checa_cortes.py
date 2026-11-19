import sys, numpy as np, subprocess
src = sys.argv[1]; cuts = [float(x) for x in sys.argv[2:]]
raw = subprocess.run(["ffmpeg","-v","error","-i",src,"-ac","1","-ar","16000","-f","f32le","-"],capture_output=True).stdout
a = np.frombuffer(raw, np.float32); sr=16000
ref = np.sqrt(np.mean(a**2))
for c in cuts:
    i=int(c*sr); w=a[max(0,i-480):i+480]
    r=np.sqrt(np.mean(w**2))/ref
    # acha o ponto mais silencioso em ±0,25 s
    best=None
    for d in range(-4000,4001,160):
        j=i+d; ww=a[max(0,j-480):j+480]; rr=np.sqrt(np.mean(ww**2))/ref
        if best is None or rr<best[0]: best=(rr,(j)/sr)
    print(f"{c:.2f}: nivel {r:.2f}  | mais quieto {best[0]:.2f} em {best[1]:.2f}" + ("   <<< ATENCAO" if r>0.15 else ""))
