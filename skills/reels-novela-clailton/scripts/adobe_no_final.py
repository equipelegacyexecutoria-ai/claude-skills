"""Adobe Podcast no vídeo PRONTO (sem bruto e sem pasta de trabalho).

Usado quando só o áudio precisa de tratamento (ruído, ganho alto) e o corte/legenda já estão aprovados,
ou quando a pasta de trabalho ficou em outro PC (Mounjaro, 11/10/2026). A CTA (últimos 2,9 s, com o som
de teclado) fica fora do Adobe: ele apagaria o teclado como ruído.

  exportar <video> <saida.mp3>              fala (até o início da CTA) em MP3 mono 320k para o Adobe
  juntar   <video> <adobe.mp3> <saida.mp4>  confere atraso/correlação, volume -16 LUFS + limitador suave,
                                            junta com a cauda original da CTA e troca o áudio (imagem copiada)
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

CTA = 2.9          # duração da CTA digitada no fim (legenda_novela / render_final)
LUFS = -16.0


def dur(video):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(video)], capture_output=True, text=True, check=True).stdout)


def ff(*a):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *map(str, a)], check=True)


def ler_pcm(arq, sr=16000):
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", str(arq), "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(out, np.int16).astype(np.float32)


def exportar(video, mp3):
    corte = dur(video) - CTA
    ff("-i", video, "-t", f"{corte:.3f}", "-vn", "-ac", "1", "-ar", "48000", "-c:a", "libmp3lame", "-b:a", "320k", mp3)
    print(json.dumps({"fala_s": round(corte, 3), "mp3": str(mp3), "mb": round(Path(mp3).stat().st_size / 2**20, 1)}))


def juntar(video, adobe, saida):
    corte = dur(video) - CTA
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        ff("-i", video, "-t", f"{corte:.3f}", "-vn", "-ac", "1", "-ar", "48000", t / "orig.wav")
        ff("-i", adobe, "-ac", "1", "-ar", "48000", t / "limpo.wav")
        a, b = ler_pcm(t / "orig.wav"), ler_pcm(t / "limpo.wav")
        n = min(len(a), len(b), 16000 * 30)
        s = min(16000 * 5, max(0, min(len(a), len(b)) - n))
        A, B = a[s:s + n], b[s:s + n]
        c = np.fft.irfft(np.fft.rfft(A, 2 * n) * np.conj(np.fft.rfft(B, 2 * n)))
        k = int(np.argmax(c))
        k = k if k < n else k - 2 * n
        corr = float(np.corrcoef(A, B)[0, 1])
        if abs(k) > 16 or corr < 0.85:
            sys.exit(f"REPROVADO: o áudio do Adobe não casa com o vídeo (atraso {k / 16:.1f} ms, correlação {corr:.2f})")
        m = re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(
            ["ffmpeg", "-hide_banner", "-nostats", "-i", str(t / "limpo.wav"), "-af", "ebur128", "-f", "null", "-"],
            capture_output=True, text=True).stderr)
        ganho = LUFS - float(m[-1])
        ff("-i", t / "limpo.wav", "-af",
           f"volume={ganho:.2f}dB,alimiter=limit=0.832:attack=7:release=200:level=false:latency=true",
           "-ac", "2", "-ar", "48000", t / "fala.wav")
        ff("-ss", f"{corte:.3f}", "-i", video, "-vn", "-ac", "2", "-ar", "48000", t / "cauda.wav")
        ff("-i", t / "fala.wav", "-i", t / "cauda.wav", "-filter_complex", "[0:a][1:a]concat=n=2:v=0:a=1[a]",
           "-map", "[a]", t / "audio.wav")
        ff("-i", video, "-i", t / "audio.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
           "-b:a", "320k", "-movflags", "+faststart", saida)
    print(json.dumps({"atraso_ms": round(k / 16, 1), "correlacao": round(corr, 3), "ganho_db": round(ganho, 1),
                      "saida": str(saida)}))


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "exportar":
        exportar(sys.argv[2], sys.argv[3])
    elif len(sys.argv) >= 5 and sys.argv[1] == "juntar":
        juntar(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        sys.exit(__doc__)
