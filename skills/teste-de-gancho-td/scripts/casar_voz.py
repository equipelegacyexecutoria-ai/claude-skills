"""Deixa a voz do gancho (voz clonada) com o mesmo som da gravação do reel original:
1) separa voz e ambiente do original logo depois do corte (Demucs);
2) equaliza a voz clonada para o timbre médio da voz original (curva por bandas, +-9 dB);
3) iguala o volume da voz original;
4) põe por baixo o ambiente real do original (o "ar" do escritório), para a emenda não abrir.
Uso: python casar_voz.py <voz.wav> <original.mp4> <corte_quadro> <saida.wav> [antes]
     antes = a fala nova entra DEPOIS do trecho de referência (CTA no fim): tudo é medido nos segundos antes
     do corte; o fundo continua para a frente (com música) ou é o ambiente invertido (só sala).
"""
import subprocess, sys, tempfile
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from comum import py_com  # noqa: E402

voz, original, corte, saida = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
ANTES = len(sys.argv) > 5 and sys.argv[5] == "antes"
PY_SEP = py_com("demucs")   # separador de voz e ambiente (normalmente a venv-align)
SR = 44100
t_c = corte * 1001 / 30000


def ler(arq, ss=0.0, t=None, sr=SR, ch=1):
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{ss:.4f}"] + (["-t", f"{t:.4f}"] if t else []) + \
          ["-i", str(arq), "-ac", str(ch), "-ar", str(sr), "-f", "f32le", "-"]
    a = np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32)
    return a.reshape(-1, ch) if ch > 1 else a


def lufs(arq):
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", str(arq), "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    return float([l for l in r.splitlines() if l.strip().startswith("I:")][-1].split()[1])


def espectro(a):
    """Espectro médio (dB) só dos trechos com fala, em bandas de 1/6 de oitava."""
    n = 4096
    fr = np.fft.rfftfreq(n, 1 / SR)
    quad = [a[i:i + n] for i in range(0, len(a) - n, n // 2)]
    en = np.array([np.sqrt((q ** 2).mean()) for q in quad])
    ativos = [q for q, e in zip(quad, en) if e > np.percentile(en, 60)]
    mag = np.mean([np.abs(np.fft.rfft(q * np.hanning(n))) ** 2 for q in ativos], axis=0)
    centros = 80 * 2 ** (np.arange(0, 7.3, 1 / 6))   # 80 Hz .. ~12 kHz
    out = []
    for c in centros:
        m = (fr >= c / 2 ** (1 / 12)) & (fr < c * 2 ** (1 / 12))
        v = mag[m].mean() if m.any() else mag[np.argmin(np.abs(fr - c))]
        out.append(10 * np.log10(v + 1e-12))
    return centros, np.array(out)


tmp = Path(tempfile.mkdtemp())
dur_voz = len(ler(voz)) / SR
# 1) original logo depois do corte: separa voz e ambiente
t_sep = max(0.0, t_c - 40) if ANTES else t_c
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t_sep:.4f}", "-t", f"{(t_c - t_sep) if ANTES else 40:.4f}", "-i", original, "-vn",
                "-ac", "2", "-ar", str(SR), str(tmp / "corpo.wav")], check=True)
subprocess.run([PY_SEP, "-m", "demucs", "--two-stems=vocals", "-n", "htdemucs", "-o", str(tmp), str(tmp / "corpo.wav")],
               check=True, capture_output=True)
sep = tmp / "htdemucs" / "corpo"
# 2) curva de equalização (em passadas): som do original (voz + sala, sem música) / voz clonada
# referência: a voz real em volta da emenda (gancho original + 12 s depois do corte); mais longe o som muda
c, ref = espectro(ler(original, t_c - 12, 12) if ANTES else ler(original, t_c, 12))
ref = ref - ref.mean()
eq = tmp / "eq.wav"
g_tot = np.zeros_like(ref)
atual = voz
for passada in range(4):
    _, hk = espectro(ler(atual))
    g = ref - (hk - hk.mean())
    g = np.convolve(np.pad(g, 1, mode="edge"), np.ones(3) / 3, mode="valid")
    g_tot = np.clip(g_tot + g, -12, 12)
    g_tot[c < 130] = np.clip(g_tot[c < 130], -6, 3)   # grave bem baixo: só um toque (evita embolar)
    entradas = ";".join(f"entry({f:.0f},{v:.2f})" for f, v in zip(c, g_tot))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", voz, "-af",
                    f"aresample={SR},firequalizer=gain_entry='{entradas}',aecho=0.85:0.75:23|41:0.13|0.07",
                    "-ac", "1", str(eq)], check=True)
    atual = str(eq)
    _, chk = espectro(ler(atual))
    resto = np.abs((chk - chk.mean()) - ref)[(c > 150) & (c < 9000)].mean()
    print(f"passada {passada + 1}: diferença média de timbre {resto:.1f} dB")
    if resto < 1.0:
        break
print("EQ (Hz:dB):", " ".join(f"{f:.0f}:{v:+.1f}" for f, v in zip(c[::3], g_tot[::3])))
# 3) volume igual ao da voz original
ganho = lufs(sep / "vocals.wav") - lufs(eq)


def piso(a, pct):
    w = int(0.02 * SR)
    db = np.array([20 * np.log10(np.sqrt((a[i:i + w] ** 2).mean()) + 1e-9) for i in range(0, len(a) - w, w)])
    return np.percentile(db, pct)


# 4) ambiente: o ambiente do original logo depois do corte, invertido no tempo (termina exatamente onde o
#    original continua, sem pulo na emenda), no mesmo nível do "fundo" do original entre as palavras
amb = tmp / "amb.wav"
if ANTES:
    # fim do reel: o fundo que estava tocando antes do corte. Com música (fundo forte), repete os últimos
    # segundos para a frente (música invertida soa errada); só sala, inverte (começa igual ao corte).
    musica = lufs(sep / "no_vocals.wav") - lufs(sep / "vocals.wav") > -18
    fundo = ler(sep / "no_vocals.wav")
    seg = fundo[-int(min(dur_voz, len(fundo) / SR - 0.05) * SR):]
    if not musica:
        seg = seg[::-1]
    n = int(dur_voz * SR)
    bed = np.tile(seg, n // len(seg) + 1)[:n].astype(np.float32)
    print("fundo:", "música (segue para a frente)" if musica else "só ambiente (invertido)")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                    str(amb)], input=bed.tobytes(), check=True)
else:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(sep / "no_vocals.wav"), "-t", f"{dur_voz:.4f}",
                    "-af", "areverse", "-ac", "1", str(amb)], check=True)
alvo_piso = piso(ler(original, t_c - 10, 10) if ANTES else ler(original, t_c, 10), 10) - 2
g_amb = float(np.clip(alvo_piso - piso(ler(amb), 50), -6, 18))
if ANTES and musica:
    g_amb = 0.0   # música no mesmo volume em que já tocava
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(eq), "-i", str(amb), "-filter_complex",
                f"[0:a]volume={ganho:.2f}dB[v];[1:a]volume={g_amb:.2f}dB[b];[v][b]amix=inputs=2:duration=first:normalize=0,"
                f"alimiter=limit=0.97:level=false", "-ar", "48000", "-ac", "2", saida], check=True)
print(f"voz casada: ganho {ganho:+.1f} dB, ambiente {g_amb:+.1f} dB -> {saida}")
