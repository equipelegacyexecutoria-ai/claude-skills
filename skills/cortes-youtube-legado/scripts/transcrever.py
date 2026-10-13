"""Transcreve a aula inteira palavra a palavra (faster-whisper large-v3-turbo na GPU, volta para CPU).

Gera em <trabalho>/:
  audio16k.wav       áudio mono 16 kHz (reaproveitado pelos outros scripts)
  transcricao.json   {"arquivo", "duracao", "palavras": [{i, t, ini, fim, p}], "segmentos": [{ini, fim, texto, i0, i1}]}
  transcricao.txt    leitura para o mapa de temas: um bloco por frase, com [hh:mm:ss] e índice da 1ª palavra

Uso: python transcrever.py <video> <pasta_trabalho>
Leva ~6–10 min por hora de aula na GPU (RTX 5070).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import hms, gravar_json, rodar, sonda, whisper  # noqa: E402


def main() -> None:
    video, trab = Path(sys.argv[1]), Path(sys.argv[2])
    trab.mkdir(parents=True, exist_ok=True)
    wav = trab / "audio16k.wav"
    if not wav.exists():
        rodar(["ffmpeg", "-y", "-i", str(video), "-map", "0:a:0", "-ac", "1", "-ar", "16000", str(wav)])

    model = whisper()
    print(f"[whisper] {model.dispositivo}", flush=True)
    # aula longa: VAD ligado (sem ele o Whisper inventa texto nos silêncios e intervalos);
    # condition_on_previous_text=False evita o "loop" de frase repetida em gravação de 2–3 h.
    segs, _ = model.transcribe(
        str(wav), language="pt", word_timestamps=True, beam_size=5,
        vad_filter=True, vad_parameters={"min_silence_duration_ms": 700, "speech_pad_ms": 200},
        condition_on_previous_text=False,
        initial_prompt="Aula do Legado Empresarial, Legacy Executoria, com o Clailton. Empresa, empresário, gestão, "
                       "faturamento, lucro, DRE, organograma, processos, equipe, vendas, marketing.",
    )
    palavras, segmentos = [], []
    for s in segs:
        i0 = len(palavras)
        for w in s.words or []:
            t = w.word.strip()
            if t:
                palavras.append({"i": len(palavras), "t": t, "ini": round(w.start, 2),
                                 "fim": round(w.end, 2), "p": round(w.probability, 2)})
        if len(palavras) > i0:
            segmentos.append({"ini": round(s.start, 2), "fim": round(s.end, 2), "texto": s.text.strip(),
                              "i0": i0, "i1": len(palavras) - 1})
            if len(segmentos) % 50 == 0:
                print(f"  {hms(s.end)}  {len(palavras)} palavras", flush=True)
    dur = float(sonda(video)["format"]["duration"])
    gravar_json(trab / "transcricao.json", {"arquivo": str(video.resolve()), "duracao": dur,
                                            "palavras": palavras, "segmentos": segmentos})

    out = [f"# {video.name} — {hms(dur)} — {len(palavras)} palavras",
           "# [hh:mm:ss] (#índice da 1ª palavra) texto   — linha '~~ silêncio Ns ~~' = buraco sem fala ≥ 8 s", ""]
    ant = 0.0
    for s in segmentos:
        if s["ini"] - ant >= 8:
            out.append(f"~~ silêncio {s['ini'] - ant:.0f}s ~~")
        out.append(f"[{hms(s['ini'])}] (#{s['i0']}) {s['texto']}")
        ant = s["fim"]
    (trab / "transcricao.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"ok: {len(palavras)} palavras, {len(segmentos)} frases -> {trab}")


if __name__ == "__main__":
    main()
