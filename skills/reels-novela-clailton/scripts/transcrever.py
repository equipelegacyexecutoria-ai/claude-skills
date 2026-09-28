"""Transcrição palavra a palavra do bruto (Whisper large-v3-turbo, CPU int8).

Gera em <trabalho>/:
  transcricao.json  -> {"arquivo", "duracao", "palavras": [{i, texto, inicio, fim, prob}]}
  transcricao.txt   -> leitura para o agente decupador: frases numeradas, pausas, tomadas

Uso: python transcrever.py <video_bruto> <pasta_trabalho>
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import gravar_json, rodar, sonda  # noqa: E402

PAUSA_FRASE = 0.45     # quebra de linha no .txt


def main() -> None:
    video, trabalho = Path(sys.argv[1]), Path(sys.argv[2])
    trabalho.mkdir(parents=True, exist_ok=True)
    wav = trabalho / "audio16k.wav"
    rodar(["ffmpeg", "-y", "-i", str(video), "-map", "0:a:0", "-ac", "1", "-ar", "16000", str(wav)])

    from comum import whisper
    model = whisper()          # GPU (float16) com volta para CPU
    # condition_on_previous_text=False: com tomadas repetidas o modelo não "pula" a repetição
    segs, _ = model.transcribe(str(wav), language="pt", word_timestamps=True, vad_filter=False,
                               beam_size=5, condition_on_previous_text=False)
    palavras = []
    for s in segs:
        for w in s.words or []:
            t = w.word.strip()
            if not t:
                continue
            palavras.append({"i": len(palavras), "texto": t, "inicio": round(w.start, 3),
                             "fim": round(w.end, 3), "prob": round(w.probability, 2)})
        print(f"{s.start:7.2f}-{s.end:7.2f} {s.text.strip()}", flush=True)
    dur = float(sonda(video)["format"]["duration"])
    # palavra sem energia de voz no próprio intervalo = provável invenção do Whisper no silêncio
    from montar_corte import Energia, ler_wav
    en = Energia(*ler_wav(wav))
    for w in palavras:
        a, b = int(w["inicio"] / 0.01), max(int(w["inicio"] / 0.01) + 1, int(w["fim"] / 0.01))
        w["sem_voz"] = bool(en.db[a:b].size == 0 or en.db[a:b].max() < en.voz)
    gravar_json(trabalho / "transcricao.json", {"arquivo": str(video.resolve()), "duracao": dur, "palavras": palavras})

    # leitura para o decupador
    linhas = []
    cur = []
    for k, w in enumerate(palavras):
        if cur and w["inicio"] - cur[-1]["fim"] >= PAUSA_FRASE:
            linhas.append(cur)
            cur = []
        cur.append(w)
    if cur:
        linhas.append(cur)
    out = [f"# {video.name} — {dur:.1f}s — {len(palavras)} palavras",
           "# [i0-i1] início-fim | texto   (palavra? = baixa confiança; palavra[sem voz] = provável invenção)", ""]
    ant = None
    for ln in linhas:
        if ant is not None:
            out.append(f"      (pausa {ln[0]['inicio'] - ant['fim']:.2f}s)")
        txt = " ".join(w["texto"] + ("?" if w["prob"] < 0.5 else "") + ("[sem voz]" if w["sem_voz"] else "")
                       for w in ln)
        out.append(f"[{ln[0]['i']:04d}-{ln[-1]['i']:04d}] {ln[0]['inicio']:7.2f}-{ln[-1]['fim']:7.2f} | {txt}")
        ant = ln[-1]
    (trabalho / "transcricao.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"ok: {len(palavras)} palavras, {len(linhas)} frases -> {trabalho}")


if __name__ == "__main__":
    main()
