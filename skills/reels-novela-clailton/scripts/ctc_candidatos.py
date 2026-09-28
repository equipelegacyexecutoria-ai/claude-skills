r"""Qual texto casa melhor com o áudio? Perda CTC do wav2vec2 português (menor = melhor).

Para palavra que o Whisper ouviu estranho: "Peça comigo" x "Pensa comigo" (vídeo 2: o áudio
dizia mesmo "peça" -- perda 14,6 x 43,0; calibrado no "pensando" e "pense" do mesmo falante,
onde o modelo prefere as versões com n). Roda na venv do alinhador:

  %LOCALAPPDATA%\reels-novela\venv-align\Scripts\python.exe ctc_candidatos.py <audio16k.wav> <t0> <t1> "texto 1" "texto 2" ...
"""
import sys
import wave

import numpy as np
import torch
import torch.nn.functional as F
import whisperx

wav, t0, t1 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
cands = sys.argv[4:]
with wave.open(wav) as w:
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
seg = torch.from_numpy(x[int(t0 * 16000):int(t1 * 16000)]).unsqueeze(0)
dev = "cuda" if torch.cuda.is_available() else "cpu"
model, meta = whisperx.load_align_model(language_code="pt", device=dev)
dic = meta["dictionary"]
blank = dic.get("<pad>", dic.get("[pad]", 0))
with torch.inference_mode():
    em = torch.log_softmax(model(seg.to(dev)).logits, dim=-1)[0].cpu()     # (T, C)
for c in cands:
    alvo = [dic[ch] for ch in c.lower().replace(" ", "|") if ch in dic]
    perda = F.ctc_loss(em.unsqueeze(1), torch.tensor([alvo]), torch.tensor([em.shape[0]]),
                       torch.tensor([len(alvo)]), blank=blank, reduction="sum").item()
    print(f"{c:20s} perda {perda:8.2f}   por letra {perda / len(alvo):6.3f}")
