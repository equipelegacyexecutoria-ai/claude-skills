"""Troca a CTA digitada ("ME SIGA PARA MAIS CONTEÚDOS COMO ESTE", tela preta + teclado) pela CTA nova em
motion "me segue" (aprovada pelo usuário em 12/11/2026: assets/cta_me_segue.mp4, voz gravada do Clailton +
botão Seguir + mouse + clique).

Funciona em cima do vídeo FINAL (já com música), então serve para:
  - vídeos já entregues (Aprovação / Correções) e
  - vídeos novos: render_final.py -> trilha.py -> trocar_cta.py.

O que faz:
  1. acha o quadro em que a imagem vira a tela preta da CTA antiga (faixa 5:4 toda preta até o fim);
  2. acha a música que está tocando (biblioteca ~/Music/Spotclai, ou --musica) e o ponto exato dela, pela
     correlação do trecho da CTA antiga com cada faixa;
  3. corta o vídeo no quadro da CTA antiga e emenda a CTA nova (sem os primeiros CORTE_INI s de fundo vazio);
  4. som da emenda: a mesma música continua do ponto exato, no mesmo volume, por baixo da voz da CTA, e some
     num fade de 1,5 s no fim; a voz da CTA fica no mesmo volume da voz do vídeo; limitador em -0,1 dBTP.

Uso: python trocar_cta.py <final.mp4> <saida.mp4> [--musica <arquivo>] [--cta-inicio <s>] [--sem-musica]
Imprime um JSON com o que achou (quadro da CTA, música, ponto, ganho, loudness final).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
CTA = AQUI.parent / "assets" / "cta_me_segue.mp4"
BIBLIOTECA = Path(os.path.expanduser("~")) / "Music" / "Spotclai"
# lotes antigos (até 10/11/2026) usaram faixas baixadas do YouTube; ficam como 2a fonte da busca
EXTRAS = [Path(r"C:\Render\_trabalho\_musicas_yt")]
CACHE = Path(os.environ.get("TROCAR_CTA_CACHE", r"C:\Render\_trabalho\_trilhas\cache8k"))
CORTE_INI = 0.20      # s de fundo vazio tirados do começo da CTA (a 1a palavra entra em ~0,43 s)
FADE_FIM = 1.5        # fade-out da música no fim (igual ao mixar_alto.py)
TETO = -0.1           # dBTP
SR = 48000
SR_BUSCA = 8000
FPS_NUM, FPS_DEN = 30000, 1001
CRF = 17


def run(args, **kw):
    return subprocess.run(args, check=True, **kw)


def duracao(p) -> float:
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True).stdout)


def ler_audio(p, sr, mono=False, ss=None, t=None) -> np.ndarray:
    args = ["ffmpeg", "-v", "error"]
    if ss is not None:
        args += ["-ss", f"{ss:.4f}"]
    args += ["-i", str(p)]
    if t is not None:
        args += ["-t", f"{t:.4f}"]
    args += ["-vn", "-ac", "1" if mono else "2", "-ar", str(sr), "-f", "f32le", "-"]
    x = np.frombuffer(subprocess.run(args, capture_output=True, check=True).stdout, dtype=np.float32)
    return x if mono else x.reshape(-1, 2)


def gravar_wav(p, x: np.ndarray, sr=SR):
    y = np.clip(x, -1, 1)
    with wave.open(str(p), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((y * 32767).astype(np.int16).tobytes())


def medir(p, extra=()) -> tuple[float, float]:
    r = subprocess.run(["ffmpeg", "-hide_banner", *extra, "-i", str(p), "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    s = r[r.rfind("Summary"):]
    return float(re.search(r"I:\s+(-?[\d.]+) LUFS", s).group(1)), float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", s).group(1))


def achar_cta(video: Path) -> int:
    """Quadro em que a faixa 5:4 fica preta até o fim (a CTA antiga). Mede a parte de cima da faixa
    (y 560-860), acima do texto digitado."""
    dur = duracao(video)
    ss = max(0.0, dur - 8.0)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{ss:.3f}", "-i", str(video), "-vf",
                          "crop=1080:300:0:560,scale=108:30,format=gray", "-f", "rawvideo", "-"],
                         capture_output=True, check=True).stdout
    q = np.frombuffer(raw, np.uint8).reshape(-1, 30 * 108).astype(np.float32)
    media = q.mean(axis=1)
    # corte seco para o preto: a maior queda de um quadro para o outro, caindo para quase preto
    # (o texto digitado vai acendendo depois, por isso não dá para exigir "preto até o fim")
    queda = media[:-1] - media[1:]
    cand = [i + 1 for i in range(len(queda)) if media[i + 1] < 3.0 and media[i] > 15.0]
    if not cand:
        raise SystemExit("não achei o corte para a tela preta da CTA antiga (use --cta-inicio)")
    k = max(cand, key=lambda i: queda[i - 1])
    if len(media) - k < 45:
        raise SystemExit(f"corte para o preto muito perto do fim ({len(media) - k} quadros): confira (use --cta-inicio)")
    # índice absoluto: o -ss cai num quadro; converte pelo tempo
    q0 = round(ss * FPS_NUM / FPS_DEN)
    return q0 + k


def faixa_8k(m: Path) -> np.ndarray:
    CACHE.mkdir(parents=True, exist_ok=True)
    c = CACHE / (re.sub(r"[^\w.-]+", "_", m.stem)[:80] + f"_{m.stat().st_size}.npy")
    if c.exists():
        return np.load(c).astype(np.float32)
    x = ler_audio(m, SR_BUSCA, mono=True)
    np.save(c, x.astype(np.float16))
    return x


def correlacao(trecho: np.ndarray, faixa: np.ndarray) -> tuple[float, int]:
    n = len(trecho)
    if len(faixa) < n + 1:
        return 0.0, 0
    s = trecho - trecho.mean()
    s /= (np.linalg.norm(s) + 1e-9)
    L = 1 << int(np.ceil(np.log2(len(faixa) + n)))
    c = np.fft.irfft(np.fft.rfft(faixa, L) * np.conj(np.fft.rfft(s, L)), L)[:len(faixa) - n + 1]
    e = np.concatenate([[0.0], np.cumsum(faixa.astype(np.float64) ** 2)])
    w = e[n:] - e[:-n]
    en = np.sqrt(np.maximum(w, 0.05 * w.mean() + 1e-12))[:len(c)]   # trecho quase mudo da faixa não vira falso positivo
    r = c / en
    k = int(np.argmax(r))
    return float(r[k]), k


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("final")
    ap.add_argument("saida")
    ap.add_argument("--musica", help="arquivo da música (pula a busca na biblioteca)")
    ap.add_argument("--cta-inicio", type=float, help="tempo (s) em que começa a CTA antiga")
    ap.add_argument("--sem-musica", action="store_true")
    a = ap.parse_args()
    final, saida = Path(a.final), Path(a.saida)
    info: dict = {"final": str(final)}

    q_c = round(a.cta_inicio * FPS_NUM / FPS_DEN) if a.cta_inicio is not None else achar_cta(final)
    t_c = q_c * FPS_DEN / FPS_NUM
    dur_old = duracao(final)
    info.update(quadro_cta=q_c, t_cta=round(t_c, 3), cta_antiga_s=round(dur_old - t_c, 2))

    dur_cta = duracao(CTA) - CORTE_INI
    n_tail = int(round(dur_cta * SR))

    # ---- música: qual é e onde está ----
    musica = None
    musica_tail = np.zeros((n_tail, 2), np.float32)
    if not a.sem_musica:
        a0, a1 = t_c + 0.05, min(t_c + 1.30, dur_old - FADE_FIM - 0.1)
        trecho = ler_audio(final, SR_BUSCA, mono=True, ss=a0, t=a1 - a0)
        candidatos = [Path(a.musica)] if a.musica else sorted(
            p for raiz in [BIBLIOTECA, *EXTRAS] if raiz.exists() for p in raiz.rglob("*")
            if p.suffix.lower() in (".mp3", ".wav", ".m4a", ".flac", ".opus", ".webm"))
        ranking = []
        for m in candidatos:
            r, k = correlacao(trecho, faixa_8k(m))
            ranking.append((r, k, m))
        ranking.sort(key=lambda x: -x[0])
        # confirmação: com o ponto achado, a faixa tem que bater também nos 12 s ANTES da CTA (música por baixo
        # da voz; voz não correlaciona com a música). Faixa errada dá ~0; a certa, 0,2-0,5.
        antes = ler_audio(final, SR_BUSCA, mono=True, ss=t_c - 12.0, t=12.0)
        melhor = (0.0, 0, None, 0.0)
        for r, k, m in ranking[:6]:
            f8 = faixa_8k(m)
            ini = k - int((a0 - (t_c - 12.0)) * SR_BUSCA)
            if ini < 0:
                continue
            seg = f8[ini:ini + len(antes)]
            n = min(len(seg), len(antes))
            if n < SR_BUSCA * 4:
                continue
            best = 0.0
            for d in range(-8, 9):           # +-1 ms de folga
                x = antes[max(0, d):n + min(0, d)]
                y = seg[max(0, -d):n - max(0, d)]
                mm = min(len(x), len(y))
                v = float(np.dot(x[:mm], y[:mm]) / (np.linalg.norm(x[:mm]) * np.linalg.norm(y[:mm]) + 1e-9))
                best = max(best, v)
            if best > melhor[3]:
                melhor = (r, k, m, best)
        info["busca"] = {"faixa": str(melhor[2]) if melhor[2] else None, "score_cta": round(melhor[0], 3),
                         "confirmacao_12s": round(melhor[3], 3),
                         "top3": [(round(r, 3), m.name) for r, _, m in ranking[:3]]}
        if melhor[2] is not None and melhor[3] >= 0.08:
            musica = melhor[2]
            # ponto fino em 48 kHz: correlação em +-30 ms em volta do achado
            p8 = melhor[1] / SR_BUSCA
            trecho48 = ler_audio(final, SR, ss=a0, t=a1 - a0).mean(axis=1)
            janela = ler_audio(musica, SR, ss=max(0.0, p8 - 0.03), t=(a1 - a0) + 0.06).mean(axis=1)
            r48, k48 = correlacao(trecho48, janela)
            p_a0 = max(0.0, p8 - 0.03) + k48 / SR          # posição da faixa no instante a0 do vídeo
            p_c = p_a0 - (a0 - t_c)                          # ... no instante da CTA
            # ganho por canal (mínimos quadrados) no trecho antes do fade
            fx = ler_audio(final, SR, ss=a0, t=a1 - a0)
            mx = ler_audio(musica, SR, ss=p_a0, t=a1 - a0)
            n = min(len(fx), len(mx))
            g = [float(np.dot(fx[:n, c], mx[:n, c]) / (np.dot(mx[:n, c], mx[:n, c]) + 1e-12)) for c in (0, 1)]
            # trecho do começo (rampa de volta da música, MUS_ATE): ganho nos primeiros 0,3 s
            f0 = ler_audio(final, SR, ss=t_c, t=0.3).mean(axis=1)
            m0 = ler_audio(musica, SR, ss=p_c, t=0.3).mean(axis=1)
            n0 = min(len(f0), len(m0))
            g0 = float(np.dot(f0[:n0], m0[:n0]) / (np.dot(m0[:n0], m0[:n0]) + 1e-12))
            info["musica"] = {"arquivo": str(musica), "ponto_na_cta_s": round(p_c, 4), "corr_48k": round(r48, 3),
                              "ganho_db": [round(20 * np.log10(max(x, 1e-6)), 2) for x in g],
                              "rampa_no_inicio": bool(g0 < 0.7 * np.mean(g))}
            dur_m = duracao(musica)
            pos = p_c % dur_m
            mt = ler_audio(musica, SR, ss=pos, t=dur_cta + 0.1)
            while len(mt) < n_tail:        # faixa acabou: volta ao começo (o mixar_alto usa -stream_loop -1)
                mt = np.vstack([mt, ler_audio(musica, SR, t=dur_cta + 0.1)])
            mt = mt[:n_tail] * np.array(g, np.float32)[None, :]
            env = np.ones(n_tail, np.float32)
            nf = int(FADE_FIM * SR)
            fim = n_tail - int(0.05 * SR)
            env[fim - nf:fim] = np.linspace(1, 0, nf)
            env[fim:] = 0
            if info["musica"]["rampa_no_inicio"]:
                nr = int(0.4 * SR)
                env[:nr] *= np.linspace(max(g0 / np.mean(g), 0), 1, nr)
            musica_tail = mt * env[:, None]
        else:
            info["musica"] = None

    # ---- voz da CTA no mesmo volume da voz do vídeo ----
    I_fala, _ = medir(final, ["-t", f"{t_c:.3f}"])
    I_cta, _ = medir(CTA, ["-ss", f"{CORTE_INI:.3f}"])
    alvo = I_fala - (0.4 if musica is not None else 0.0)   # a música 10 dB abaixo soma ~0,4 dB no vídeo
    g_cta = 10 ** ((alvo - I_cta) / 20)
    voz = ler_audio(CTA, SR, ss=CORTE_INI)[:n_tail]
    if len(voz) < n_tail:
        voz = np.vstack([voz, np.zeros((n_tail - len(voz), 2), np.float32)])
    tail = voz * g_cta + musica_tail
    info["voz_cta"] = {"I_fala_video": I_fala, "I_cta": I_cta, "ganho_db": round(20 * np.log10(g_cta), 2)}

    head = ler_audio(final, SR, t=t_c)
    n_head = int(round(t_c * SR))
    head = head[:n_head]
    if len(head) < n_head:
        head = np.vstack([head, np.zeros((n_head - len(head), 2), np.float32)])
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        bruto = td / "audio_bruto.wav"
        gravar_wav(bruto, np.vstack([head, tail]))
        audio = td / "audio.wav"
        lim = TETO - 0.1
        for _ in range(4):
            run(["ffmpeg", "-v", "error", "-y", "-i", str(bruto), "-af",
                 f"aresample=192000,alimiter=limit={10 ** (lim / 20):.5f}:attack=1:release=60:level=false,aresample={SR}",
                 "-c:a", "pcm_s24le", str(audio)])
            _, tp = medir(audio)
            if tp <= TETO - 0.1:
                break
            lim -= (tp - (TETO - 0.1)) + 0.1
        # ---- vídeo: até o quadro da CTA antiga + CTA nova ----
        fc = (f"[0:v]trim=end_frame={q_c},setpts=N*{FPS_DEN}/{FPS_NUM}/TB,format=yuv420p,setsar=1[a];"
              f"[1:v]trim=start={CORTE_INI},fps={FPS_NUM}/{FPS_DEN},setpts=N*{FPS_DEN}/{FPS_NUM}/TB,"
              f"scale=1080:1920,format=yuv420p,setsar=1[b];[a][b]concat=n=2:v=1:a=0,"
              f"setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv[v]")
        tmp_out = saida.with_name(saida.stem + ".tmp.mp4")
        saida.parent.mkdir(parents=True, exist_ok=True)
        run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-i", str(final), "-i", str(CTA), "-i", str(audio),
             "-filter_complex", fc, "-map", "[v]", "-map", "2:a", "-c:v", "libx264", "-preset", "slow", "-crf", str(CRF),
             "-profile:v", "high", "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
             "-colorspace", "bt709", "-color_range", "tv", "-r", f"{FPS_NUM}/{FPS_DEN}", "-c:a", "aac", "-b:a", "320k",
             "-ar", str(SR), "-movflags", "+faststart", "-shortest", str(tmp_out)])
        os.replace(tmp_out, saida)
    I_f, tp_f = medir(saida)
    info.update(saida=str(saida), duracao=round(duracao(saida), 3), final={"I": I_f, "pico_real": tp_f})
    print(json.dumps(info, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
