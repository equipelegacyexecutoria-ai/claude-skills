"""Render final do reel novela: 1080x1920, qualidade máxima, uma única compressão com perda.

Pipeline (tudo a partir do bruto 4K):
  1. cada segmento do corte -> recorte 5:4 -> 1080x864 (lanczos) -> intermediário SEM PERDA (x264 qp 0)
  2. tela preta da CTA (sem perda)
  3. áudio: fatias exatas do bruto (48 kHz), fade de 8 ms em cada corte, silêncio na CTA,
     ganho até -16 LUFS + limitador suave só nos picos (pico -1 dBTP); depois, o som de teclado
     padrão (assets/cta_teclado.mp3) com o 1o toque no quadro da 1a letra da CTA
  4. concatena -> faixa centrada com barras pretas (pad) -> legenda .ass (libass) ->
     H.264 High CRF 10 preset slow, yuv420p BT.709, AAC 320k, +faststart

Uso: python render_final.py <pasta_trabalho> <saida.mp4> [--manter] [--sem-cuda] [--sem-teclado]
Requer em <trabalho>/: corte.json, enquadramento.json, legenda.ass, layout.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
import wave
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import (AUDIO_BR, CRF, FAIXA_H, FAIXA_W, FAIXA_Y0, FPS, FPS_DEN, FPS_NUM, H, LUFS, PRESET,  # noqa: E402
                   TRUE_PEAK, W, gravar_json, ler_json, preparar_fontes)

SR = 48000
FADE = 0.008
FADE_FIM = 0.025   # saída de cada emenda: 8 ms cortava a cauda da vogal ("circ-o", "mand-a", 09/10/2026)
COR = "setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv"
PARALELO = 6     # intermediários renderizados ao mesmo tempo
# som padrão da CTA (arquivo do usuário, 30/09/2026): rajada de 15 toques de teclado em 0,75 s, o mesmo tempo da
# digitação da frase (CTA_DIGITACAO 0,76 s) -> o 1o toque cai no quadro da 1a letra e o último na última letra.
# Vale para novela, tela dividida e edição simples (as três usam esta função).
TECLADO = Path(__file__).resolve().parent.parent / "assets" / "cta_teclado.mp3"
TECLADO_GANHO_DB = 12.0   # o arquivo vem baixo (pico -17 dBFS, ~-37 LUFS): +12 dB ~ -25 LUFS, bem audível sem brigar com a voz
TECLADO_PRE = 0.002       # s antes do 1o toque que ficam no recorte


def ff(args: list[str], cwd: Path | None = None) -> None:
    subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y"] + args, check=True, cwd=cwd)


def render_segmentos(fonte: str, segs: list[dict], crop: list[int], tmp: Path, cuda: bool,
                     por_seg: dict | None = None) -> list[Path]:
    """Um intermediário sem perda por segmento, PARALELO de cada vez (NVDEC decodifica o 4K; o
    lanczos e o x264 sem perda usam a CPU): 35 segmentos em ~1/4 do tempo de um por um."""

    def um(k: int) -> Path:
        s = segs[k]
        cw, ch, x, y = (por_seg or {}).get(str(k), crop)
        # o bruto Sony vem marcado xvYCC (iec61966-2-4): é a curva do BT.709; marca como BT.709
        vf = (f"crop={cw}:{ch}:{x}:{y},scale={FAIXA_W}:{FAIXA_H}:flags=lanczos+accurate_rnd+full_chroma_int,"
              f"setsar=1,format=yuv420p,{COR}")
        out = tmp / f"seg_{k:03d}.mkv"
        t_seek = (s["frame_in"] - 0.5) / FPS
        args = (["-hwaccel", "cuda"] if cuda else []) + [
            "-ss", f"{max(0.0, t_seek):.6f}", "-i", fonte, "-frames:v", str(s["frames"]), "-an", "-sn", "-dn",
            "-vf", vf, "-fps_mode", "passthrough", "-c:v", "libx264", "-qp", "0", "-preset", "ultrafast",
            str(out)]
        try:
            ff(args)
        except subprocess.CalledProcessError:
            if not cuda:
                raise
            ff(args[2:])          # sem cuda
        n = contar_quadros(out)
        if n != s["frames"]:
            raise SystemExit(f"segmento {k}: {n} quadros, esperado {s['frames']}")
        print(f"  seg {k:02d}: {s['frames']} quadros", flush=True)
        return out

    with ThreadPoolExecutor(PARALELO) as ex:
        return list(ex.map(um, range(len(segs))))


def contar_quadros(p: Path) -> int:
    r = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0",
                        "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True, check=True)
    return int(r.stdout.strip())


def render_preto(n: int, out: Path) -> None:
    ff(["-f", "lavfi", "-i", f"color=black:s={FAIXA_W}x{FAIXA_H}:r={FPS_NUM}/{FPS_DEN}", "-frames:v", str(n),
        "-c:v", "libx264", "-qp", "0", "-preset", "ultrafast", "-pix_fmt", "yuv420p", str(out)])


def montar_audio(fonte: str, segs: list[dict], quadros_cta: int, tmp: Path, tratado: Path | None = None) -> Path:
    """tratado: áudio do bruto inteiro já limpo (Adobe Podcast "Aprimorar fala"), na MESMA linha do tempo do
    bruto (conferido por `tratar_audio.py alinhar`). Sem ele, usa o som do próprio bruto."""
    bruto = tmp / "audio_bruto.wav"
    if tratado is not None:
        ff(["-i", str(tratado), "-ac", "2", "-ar", str(SR), "-c:a", "pcm_s16le", str(bruto)])
    else:
        ff(["-i", fonte, "-map", "0:a:0", "-ac", "2", "-ar", str(SR), "-c:a", "pcm_s16le", str(bruto)])
    with wave.open(str(bruto), "rb") as w:
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).reshape(-1, 2).astype(np.float32) / 32768
    partes = []
    total_q = 0
    total_s = 0
    nf, nf_fim = int(FADE * SR), int(FADE_FIM * SR)
    rampa = np.linspace(0, 1, nf, dtype=np.float32)[:, None]
    rampa_fim = np.linspace(1, 0, nf_fim, dtype=np.float32)[:, None] ** 2     # cauda: cai suave como a voz
    for k, s in enumerate(segs):
        a = int(round(s["frame_in"] / FPS * SR))
        total_q += s["frames"]
        alvo = int(round(total_q / FPS * SR))        # acumulado: sem deriva de arredondamento
        n = alvo - total_s
        pedaco = x[a:a + n].copy()
        if len(pedaco) < n:
            pedaco = np.vstack([pedaco, np.zeros((n - len(pedaco), 2), np.float32)])
        contiguo_antes = k > 0 and segs[k - 1]["frame_in"] + segs[k - 1]["frames"] == s["frame_in"]
        contiguo_depois = k + 1 < len(segs) and s["frame_in"] + s["frames"] == segs[k + 1]["frame_in"]
        if not contiguo_antes:
            pedaco[:nf] *= rampa
        if not contiguo_depois:
            pedaco[-nf_fim:] *= rampa_fim
        partes.append(pedaco)
        total_s += n
    n_cta = int(round((total_q + quadros_cta) / FPS * SR)) - total_s
    partes.append(np.zeros((n_cta, 2), np.float32))
    y = np.vstack(partes)
    montado = tmp / "audio_montado.wav"
    with wave.open(str(montado), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
    return normalizar(montado, tmp / "audio_final.wav")


def medir(p: Path) -> dict:
    """Loudness integrado e pico real (ebur128 precisa de peak=true para imprimir o pico)."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(p), "-af", "ebur128=framelog=quiet:peak=true",
                        "-f", "null", "-"], capture_output=True, text=True)
    i = re.search(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    pk = re.search(r"Peak:\s+(-?[\d.]+|-inf) dBFS", r.stderr)
    return {"I": float(i.group(1)) if i else None,
            "TP": float(pk.group(1)) if pk and pk.group(1) != "-inf" else None}


def normalizar(entrada: Path, saida: Path) -> dict:
    """Ganho linear até LUFS (-16). Se o ganho estourar o teto de pico, um limitador SUAVE só nos picos
    (o loudnorm 'linear' viraria compressor dinâmico sem avisar — ver armadilhas no SKILL.md)."""
    m0 = medir(entrada)
    ganho = LUFS - m0["I"]
    modo = "linear"
    for _ in range(2):
        filtro = f"volume={ganho:.2f}dB"
        if m0["TP"] is not None and m0["TP"] + ganho > TRUE_PEAK - 0.3:
            teto = 10 ** ((TRUE_PEAK - 0.8) / 20)          # teto de amostra com folga p/ o pico real
            filtro += f",alimiter=limit={teto:.4f}:attack=7:release=200:level=false:latency=true"   # suave (3/60 soava duro)
            modo = "ganho+limitador de pico"
        ff(["-i", str(entrada), "-af", filtro, "-ar", str(SR), "-c:a", "pcm_s16le", str(saida)])
        m1 = medir(saida)
        if abs(m1["I"] - LUFS) <= 0.3:
            break
        ganho += LUFS - m1["I"]                            # o limitador tira um pouco de loudness
    info = {"entrada": m0, "saida": m1, "ganho_db": round(ganho, 2), "modo": modo}
    (saida.parent / "loudness.json").write_text(json.dumps(info, indent=1), encoding="utf-8")
    print(f"  loudness: {m0['I']} -> {m1['I']} LUFS, pico {m1['TP']} dBTP ({modo})", flush=True)
    return {"path": saida, **info}


def som_teclado() -> np.ndarray:
    """Som da CTA em float estéreo 48 kHz, já com o ganho, começando TECLADO_PRE antes do 1o toque
    (o mp3 traz ~80 ms de silêncio antes)."""
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(TECLADO), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                       capture_output=True, check=True)
    x = np.frombuffer(r.stdout, np.float32).reshape(-1, 2)
    amp = np.abs(x).max(axis=1)
    i0 = int(np.argmax(amp >= 0.1 * amp.max()))
    return x[max(0, i0 - int(TECLADO_PRE * SR)):] * np.float32(10 ** (TECLADO_GANHO_DB / 20))


def mixar_teclado(audio: Path, t_letra: float) -> None:
    """Soma o som de teclado ao áudio final (wav 48 kHz) com o 1o toque em t_letra = quadro da 1a letra da CTA."""
    with wave.open(str(audio), "rb") as w:
        sr, ch = w.getframerate(), w.getnchannels()
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, ch).astype(np.float32) / 32768
    if sr != SR:
        raise SystemExit(f"áudio a {sr} Hz (esperado {SR})")
    s = som_teclado()
    s = s[:, :ch] if ch <= 2 else np.repeat(s[:, :1], ch, axis=1)
    i = int(round((t_letra - TECLADO_PRE) * SR))
    n = min(len(s), len(x) - i)
    if n <= 0:
        raise SystemExit(f"CTA em {t_letra:.2f}s fora do áudio ({len(x) / SR:.2f}s)")
    x = x.copy()
    x[i:i + n] += s[:n]
    with wave.open(str(audio), "wb") as w:
        w.setnchannels(ch)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
    print(f"  som de teclado da CTA: 1o toque em {t_letra:.3f}s (+{TECLADO_GANHO_DB:.0f} dB)", flush=True)


def medir_teclado(video: Path, t_letra: float) -> dict:
    """Conferência: acha o 1o toque do teclado no vídeo final e compara com o quadro da 1a letra da CTA."""
    t_a = max(0.0, t_letra - 0.3)
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t_a:.3f}", "-t", "1.4", "-i", str(video), "-map", "0:a:0",
                        "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True)
    x = np.abs(np.frombuffer(r.stdout, np.float32))
    j0 = int((t_letra - t_a) * SR)
    pico = float(x[j0:j0 + int(0.9 * SR)].max()) if len(x) > j0 else 0.0
    if pico < 10 ** (-30 / 20):
        return {"ok": False, "motivo": "som de teclado ausente na CTA", "pico_db": round(20 * np.log10(pico + 1e-9), 1)}
    ini = max(0, j0 - int(0.15 * SR))
    toque = ini + int(np.argmax(x[ini:] >= 0.25 * pico))
    desvio = (t_a + toque / SR) - t_letra
    return {"ok": abs(desvio) <= 1 / FPS, "desvio_ms": round(desvio * 1000, 1),
            "pico_db": round(20 * np.log10(pico), 1)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("trabalho")
    ap.add_argument("saida")
    ap.add_argument("--manter", action="store_true", help="não apaga os intermediários")
    ap.add_argument("--sem-cuda", action="store_true")
    ap.add_argument("--sem-teclado", action="store_true", help="CTA sem o som de teclado")
    a = ap.parse_args()
    trabalho = Path(a.trabalho).resolve()
    saida = Path(a.saida).resolve()
    corte = ler_json(trabalho / "corte.json")
    enq = ler_json(trabalho / "enquadramento.json")
    layout = ler_json(trabalho / "layout.json")
    segs = corte["segmentos"]
    tmp = trabalho / "tmp_render"
    tmp.mkdir(exist_ok=True)
    preparar_fontes(trabalho)

    # travas: legenda feita sobre estas palavras do corte e CTA colada no fim da imagem
    pc = trabalho / "palavras_corte.json"
    sha_atual = hashlib.sha256(pc.read_bytes()).hexdigest() if pc.exists() else None
    if layout.get("palavras_sha256") and layout["palavras_sha256"] != sha_atual:
        raise SystemExit("legenda desatualizada: palavras_corte.json mudou depois do legenda_novela.py "
                         "(refaça/remapeie a legenda e rode o legenda_novela.py de novo)")
    q_fala = sum(s["frames"] for s in segs)
    if abs(float(layout["cta_inicio"]) - q_fala / FPS) > 1.01 / FPS:
        raise SystemExit(f"CTA ({layout['cta_inicio']}s) fora do fim da imagem ({q_fala / FPS:.3f}s): "
                         "rode o legenda_novela.py com --corte corte.json")
    q_cta = int(round(float(layout["duracao_total"]) * FPS)) - q_fala
    print(f"vídeo: {len(segs)} segmentos, {q_fala} quadros de fala + {q_cta} de CTA", flush=True)

    t0 = time.time()
    arquivos = render_segmentos(corte["fonte"], segs, enq["crop"], tmp, cuda=not a.sem_cuda,
                                por_seg=enq.get("crops_segmento"))
    print(f"  intermediários: {time.time() - t0:.0f}s", flush=True)
    if q_cta:
        render_preto(q_cta, tmp / "cta.mkv")
        arquivos.append(tmp / "cta.mkv")
    (tmp / "lista.txt").write_text("".join(f"file '{p.name}'\n" for p in arquivos), encoding="utf-8")
    print("áudio...", flush=True)
    # áudio limpo pelo Adobe Podcast (tratar_audio.py), se houver: mesma linha do tempo do bruto
    tratado = trabalho / "audio_tratado.wav"
    if tratado.exists():
        print("  usando audio_tratado.wav (Adobe Podcast)", flush=True)
    aud = montar_audio(corte["fonte"], segs, q_cta, tmp, tratado if tratado.exists() else None)
    audio = aud["path"]
    if q_cta and not a.sem_teclado:
        from legenda_novela import CTA_ATRASO
        mixar_teclado(audio, (q_fala + CTA_ATRASO) / FPS)

    print("encode final...", flush=True)
    t0 = time.time()
    saida.parent.mkdir(parents=True, exist_ok=True)
    tmp_out = trabalho / "final_tmp.mp4"
    # setpts por NÚMERO do quadro: o concat de .mkv (tempo em ms) arredonda e, em 30+ emendas,
    # pulava/repetia 1 quadro (imagem 33 ms fora do áudio). Assim o quadro k fica em k/29,97 exato.
    # balanço de branco do vídeo (balanco_branco.py -> cor.txt), em RGB com a matriz BT.709 dos dois lados
    cor_txt = trabalho / "cor.txt"
    wb = ""
    if cor_txt.exists() and cor_txt.read_text(encoding="utf-8").strip():
        wb = ("scale=in_color_matrix=bt709:in_range=tv,format=gbrp," + cor_txt.read_text(encoding="utf-8").strip()
              + ",scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,")
        print(f"  balanço de branco: {cor_txt.read_text(encoding='utf-8').strip()}", flush=True)
    vf = (f"[0:v]setpts=N*{FPS_DEN}/{FPS_NUM}/TB,{wb}pad={W}:{H}:0:{FAIXA_Y0}:black,"
          f"ass=legenda.ass:fontsdir=fonts,format=yuv420p,{COR}[v]")
    ff(["-f", "concat", "-safe", "0", "-i", str(tmp / "lista.txt"), "-i", str(audio),
        "-filter_complex", vf, "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-preset", PRESET, "-crf", str(CRF), "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
        "-r", f"{FPS_NUM}/{FPS_DEN}", "-c:a", "aac", "-b:a", AUDIO_BR, "-ar", str(SR),
        "-movflags", "+faststart", "-shortest", str(tmp_out)], cwd=trabalho)
    print(f"  encode final: {time.time() - t0:.0f}s", flush=True)
    shutil.move(str(tmp_out), str(saida))
    # registro da entrega (qual versão foi aprovada, com quais parâmetros)
    registro = {"video": str(saida), "sha256": hashlib.sha256(saida.read_bytes()).hexdigest(),
                "gerado_em": datetime.now().isoformat(timespec="seconds"),
                "crf": CRF, "preset": PRESET, "audio_br": AUDIO_BR, "crop": enq["crop"],
                "segmentos": len(segs), "quadros_fala": q_fala, "quadros_cta": q_cta,
                "teclado_cta": bool(q_cta and not a.sem_teclado),
                "audio_tratado": tratado.exists(),
                "loudness": {k: aud[k] for k in ("entrada", "saida", "ganho_db", "modo")},
                "palavras_sha256": sha_atual}
    gravar_json(trabalho / "render_info.json", registro)
    if not a.manter:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"ok: {saida}")


if __name__ == "__main__":
    main()
