r"""Áudio tratado no Adobe Podcast ("Aprimorar fala") — pedido do usuário (09/10/2026): tirar o ruído externo que
o lapela capta e o som "estourado" de gravação com ganho alto. Vale para novela, tela dividida e edição simples.

Fluxo (detalhes no SKILL.md, seção "Tratar o áudio no Adobe Podcast"):
  0. python tratar_audio.py medir <trabalho>    -> diz se a gravação está QUENTE (ganho alto, satura)
  1. python tratar_audio.py exportar <trabalho>
       -> <trabalho>/adobe/<slug>.mp3  (som do bruto inteiro, mono 48 kHz, MP3 320k: cabe no limite de 10 MB
          do envio pelo navegador até ~4 min; acima disso sai em 192k)
  2. No Chrome (logado no Adobe): podcast.adobe.com/pt/enhance -> envia o MP3 -> espera -> Baixar, com o
     salvar_downloads.ps1 rodando em segundo plano (aperta "Salvar" sozinho, grava em C:\Render\adobe_baixados).
  3. python tratar_audio.py alinhar <trabalho> [arquivo baixado]   (sem arquivo: pega <slug>-esv2*.mp3 dos baixados)
       -> <trabalho>/audio_tratado.wav  (estéreo 48 kHz, MESMA linha do tempo do bruto: o atraso é medido por
          correlação e corrigido; reprova se a correlação for baixa ou a duração não bater)
       -> relatório: atraso, correlação, pico, "planos" no teto (estouro) e ruído nas pausas, antes x depois
  4. editar.py finalizar (render_final.py e render_td.py usam audio_tratado.wav sozinhos quando ele existe).
     Para voltar ao som original: apague/renomeie audio_tratado.wav.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

SR = 48000
LIMITE_MB = 9.5            # envio pelo Claude in Chrome: até 10 MB por arquivo
CORR_MIN = 0.5             # correlação mínima do envelope (tratado x bruto) para aceitar
MAX_ATRASO = 0.5           # s
BAIXADOS = Path(r"C:\Render\adobe_baixados")   # onde o salvar_downloads.ps1 salva o que o Adobe devolve


def ff(args: list[str]) -> None:
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], check=True)


def ler(p: Path, canais: int = 1) -> np.ndarray:
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-map", "0:a:0", "-ac", str(canais), "-ar", str(SR),
                        "-f", "f32le", "-"], capture_output=True, check=True)
    x = np.frombuffer(r.stdout, np.float32)
    return x.reshape(-1, canais) if canais > 1 else x


def fonte(T: Path) -> str:
    for nome in ("corte.json", "transcricao.json"):
        p = T / nome
        if p.exists():
            d = json.loads(p.read_text(encoding="utf-8"))
            f = d.get("fonte") or d.get("arquivo")
            if f:
                return f
    raise SystemExit("não achei o bruto (corte.json/transcricao.json sem 'fonte')")


def exportar(T: Path) -> Path:
    src = fonte(T)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src],
                               capture_output=True, text=True, check=True).stdout.strip())
    br = 320 if dur * 320 / 8 / 1024 < LIMITE_MB else 192
    if dur * br / 8 / 1024 >= LIMITE_MB:
        br = int(LIMITE_MB * 8 * 1024 / dur) // 16 * 16
    out = T / "adobe" / f"{T.name}.mp3"
    out.parent.mkdir(exist_ok=True)
    ff(["-i", src, "-map", "0:a:0", "-ac", "1", "-ar", str(SR), "-c:a", "libmp3lame", "-b:a", f"{br}k", str(out)])
    print(f"ok: {out}  ({out.stat().st_size / 1e6:.1f} MB, {dur:.0f}s, {br}k)")
    return out


def env(x: np.ndarray, hop: int = 240) -> np.ndarray:          # 5 ms
    n = len(x) // hop
    return 20 * np.log10(np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(axis=1)) + 1e-9)


def medidas(x: np.ndarray) -> dict:
    a = np.abs(x)
    e = env(x)
    voz = np.percentile(e, 95)
    return {"pico_db": round(float(20 * np.log10(a.max() + 1e-9)), 1),
            "amostras_no_teto": int((a > 0.89 * a.max()).sum()),          # topo achatado = estouro
            "ruido_pausas_db": round(float(np.percentile(e, 10) - voz), 1)}  # pausas relativas à voz


def alinhar(T: Path, baixado: Path) -> Path:
    orig = ler(Path(fonte(T)))
    trat2 = ler(baixado, 2)
    trat = trat2.mean(axis=1)
    # atraso pelo envelope (robusto a EQ/limpeza), refinado na onda
    eo, et = env(orig), env(trat)
    n = min(len(eo), len(et))
    eo_c, et_c = eo[:n] - eo[:n].mean(), et[:n] - et[:n].mean()
    m = int(MAX_ATRASO / 0.005)
    lags = range(-m, m + 1)
    cs = [float(np.dot(eo_c[max(0, -l):n - max(0, l)], et_c[max(0, l):n - max(0, -l)])) for l in lags]
    best = lags[int(np.argmax(cs))]
    corr = max(cs) / (np.linalg.norm(eo_c) * np.linalg.norm(et_c) + 1e-9)
    atraso = best * 240                                          # amostras: tratado = original atrasado disso
    # refino fino (±5 ms) na própria onda, num trecho de 20 s com voz
    a0 = int(len(orig) * 0.3)
    w = orig[a0:a0 + 20 * SR]
    fino, melhor = 0, -1e18
    for d in range(-240, 241, 4):
        s = a0 + atraso + d
        if s < 0 or s + len(w) > len(trat):
            continue
        v = float(np.dot(w, trat[s:s + len(w)]))
        if v > melhor:
            melhor, fino = v, d
    atraso += fino
    if corr < CORR_MIN or abs(atraso) > MAX_ATRASO * SR:
        raise SystemExit(f"REPROVADO: o arquivo baixado não casa com o bruto (correlação {corr:.2f}, "
                         f"atraso {atraso / SR * 1000:.0f} ms) — é o vídeo certo?")
    if abs(len(trat) - len(orig)) > 0.2 * SR + abs(atraso):
        raise SystemExit(f"REPROVADO: duração diferente (bruto {len(orig) / SR:.2f}s, tratado {len(trat) / SR:.2f}s)")
    # desloca: amostra i do bruto = amostra i+atraso do tratado
    y = np.zeros((len(orig), 2), np.float32)
    s0 = max(0, atraso)
    d0 = max(0, -atraso)
    k = min(len(trat2) - s0, len(orig) - d0)
    y[d0:d0 + k] = trat2[s0:s0 + k]
    out = T / "audio_tratado.wav"
    with wave.open(str(out), "wb") as wv:
        wv.setnchannels(2)
        wv.setsampwidth(2)
        wv.setframerate(SR)
        wv.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
    shutil.copy2(baixado, T / "adobe" / ("baixado" + baixado.suffix.lower()))
    rel = {"atraso_ms": round(float(atraso) / SR * 1000, 2), "correlacao": round(float(corr), 3),
           "bruto": medidas(orig), "tratado": medidas(y.mean(axis=1))}
    (T / "adobe" / "relatorio.json").write_text(json.dumps(rel, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(rel, ensure_ascii=False))
    print(f"ok: {out}")
    return out


def medir(T: Path) -> bool:
    """Gravação QUENTE? (lote de 08/10/2026: RMS -20 dBFS e centenas de amostras a -1 dBFS — o normal do
    Clailton é RMS -30 e quase nenhuma; o usuário ouviu 'áudio estourado' em 5 de 6 vídeos.)"""
    x = ler(Path(fonte(T)))
    rms = float(20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9))
    perto_teto = int((np.abs(x) > 0.89).sum())
    quente = rms > -24 or perto_teto > 100
    print(json.dumps({"rms_db": round(rms, 1), "amostras_acima_-1dB": perto_teto, "quente": quente}))
    if quente:
        print("QUENTE: gravação com ganho alto (satura nos picos). Trate no Adobe Podcast e avise a equipe no "
              "comentário: baixar ~10 dB o ganho do microfone/câmera nas próximas gravações.")
    return quente


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("exportar", "alinhar", "medir"):
        raise SystemExit(__doc__)
    T = Path(sys.argv[2]).resolve()
    if sys.argv[1] == "medir":
        medir(T)
    elif sys.argv[1] == "exportar":
        exportar(T)
    else:
        if len(sys.argv) > 3:
            arq = Path(sys.argv[3]).resolve()
        else:   # o salvar_downloads.ps1 grava em BAIXADOS com o nome que o Adobe dá: <slug>-esv2-....mp3
            achados = sorted(BAIXADOS.glob(f"{T.name}-esv2*.*"), key=lambda q: q.stat().st_mtime)
            if not achados:
                raise SystemExit(f"nenhum arquivo {T.name}-esv2*.mp3 em {BAIXADOS} (rodou o salvar_downloads.ps1?)")
            arq = achados[-1]
        alinhar(T, arq)
