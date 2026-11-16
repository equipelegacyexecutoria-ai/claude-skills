"""Tempo de cada palavra da narração -> listas TX/TT do molde (index.html).

uso:
  python palavras_js.py <narracao.mp3> [--inicio 0.25] [--projeto <pasta do projeto>]

- transcreve com faster-whisper large-v3 (GPU se tiver), palavra a palavra;
- TT = início de cada palavra + o atraso com que a voz entra na mixagem (--inicio, padrão 0,25 s);
- grava <narracao>.palavras.json e <narracao>.tx.json ({TX, TT});
- com --projeto, troca as linhas "const TX = ...;" e "const TT = ...;" do index.html da pasta.
Confira a lista impressa: o Whisper às vezes junta duas palavras no mesmo tempo (ex.: "focar no que você domina");
corrija à mão no .tx.json e rode de novo com --so-projeto.
"""
import argparse, io, json, os, re, site, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument("audio")
ap.add_argument("--inicio", type=float, default=0.25)
ap.add_argument("--projeto")
ap.add_argument("--so-projeto", action="store_true", help="não transcreve; usa o .tx.json já salvo")
ap.add_argument("--prompt", default="Legacy, Legacy Plan, Legacy Executoria, DRE, executor, Clailton")
a = ap.parse_args()

txj = a.audio + ".tx.json"
if not a.so_projeto:
    for sp in site.getsitepackages() + [site.getusersitepackages()]:
        for sub in ("nvidia/cublas/bin", "nvidia/cudnn/bin"):
            d = os.path.join(sp, sub)
            if os.path.isdir(d):
                os.add_dll_directory(d)
                os.environ["PATH"] = d + os.pathsep + os.environ["PATH"]
    import soundfile as sf
    from faster_whisper import WhisperModel
    try:
        m = WhisperModel("large-v3", device="cuda", compute_type="float16")
    except Exception:
        m = WhisperModel("large-v3", device="cpu", compute_type="int8")
    wav = a.audio + ".16k.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.audio, "-ac", "1", "-ar", "16000", wav], check=True)
    audio, _ = sf.read(wav, dtype="float32")
    segs, _ = m.transcribe(audio, language="pt", word_timestamps=True, initial_prompt=a.prompt)
    ws = [{"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)} for s in segs for w in s.words]
    json.dump(ws, io.open(a.audio + ".palavras.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    TX = [w["w"] for w in ws]
    TT = [round(w["s"] + a.inicio, 2) for w in ws]
    json.dump({"TX": TX, "TT": TT}, io.open(txj, "w", encoding="utf-8"), ensure_ascii=False)
d = json.load(io.open(txj, encoding="utf-8"))
TX, TT = d["TX"], d["TT"]
print(" ".join(f"{i}:{w}[{t:.2f}]" for i, (w, t) in enumerate(zip(TX, TT))))

if a.projeto:
    p = os.path.join(a.projeto, "index.html")
    s = io.open(p, encoding="utf-8").read()
    s = re.sub(r"const TX = .*?;\n", "const TX = " + json.dumps(TX, ensure_ascii=False) + ";\n", s, count=1)
    s = re.sub(r"const TT = .*?;\n", "const TT = " + json.dumps(TT) + ";\n", s, count=1)
    io.open(p, "w", encoding="utf-8").write(s)
    print("index.html atualizado:", len(TX), "palavras")
