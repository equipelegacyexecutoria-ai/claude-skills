"""Transforma a decupagem (trechos de palavras escolhidos pelo agente) em segmentos de corte
precisos, monta o áudio do corte e retranscreve só o que ficou (para a legenda).

Entrada (<trabalho>/):
  transcricao.json, audio16k.wav   (transcrever.py)
  decupagem.json                   (agente novela-decupador)
     {"trechos": [{"de": 48, "ate": 120, "pausa_depois": 0.35?, "obs": "..."}, ...]}
Saída:
  corte.json           segmentos (quadros exatos do bruto) + linha do tempo editada
  audio_corte16k.wav   o áudio do corte (conferência e legenda)
  palavras_corte.json  palavras DO CORTE (Whisper no áudio cortado) — índices do legendista
  roteiro_corte.txt    o texto do corte, segmento a segmento, com tempos e índices

Regras de corte (medidas na referência):
- a fala é achada pela ENERGIA do áudio (o Whisper erra o começo das frases em até 0,5 s
  e às vezes estica uma palavra por cima do silêncio);
- corte colado na voz: no máximo 0,05 s antes do ataque e depois do fim, na fronteira de
  quadro mais silenciosa (o usuário reprovou início folgado e pausa longa);
- entre trechos ficam ~0,16 s de silêncio; silêncio interno > 0,30 s vira ~0,16 s;
- trecho com "desde" (recomeço depois de falso começo escondido) não começa antes desse tempo;
- no fim: retranscreve o áudio cortado, alinha as palavras (WhisperX, venv-align) e gera
  palavras_legenda.txt.

Uso: python montar_corte.py <trabalho> [--sem-whisper] [--manter-palavras] [--sem-alinhar]
"""
from __future__ import annotations

import math
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import (FIM_RESPIRO, FPS, PAUSA_ALVO, PAUSA_MAX, PAUSA_TETO_MAX, PAUSA_TETO_MIN,  # noqa: E402
                   gravar_json, ler_json)

HOP = 0.01
MARGEM_INI = 0.10        # usuário (28/09): "mais próximo nos inícios"; 09/10: sem comer a palavra -> folga natural
MARGEM_FIM = 0.12        # e nos fins
SIL_MIN = 0.10          # silêncio mínimo que separa fala (fechamento de oclusiva é mais curto)
BUSCA_ANTES = 0.35      # quanto antes da marca do Whisper a fala pode começar
BUSCA_DEPOIS = 0.70     # quanto depois da marca do Whisper a fala pode começar (ele adianta)
RITMO = {"teto": PAUSA_MAX, "tipica": PAUSA_ALVO}   # medido em cada vídeo por medir_ritmo()
# Ritmo JUSTO (padrão de todos os formatos): pausa acima de 0,30 s vira 0,22 s. Na TD o usuário reprovou os
# respiros naturais ("pausa extensa sem conexão", 09/10/2026) e na novela também (11/10/2026, notas na Sala de
# Revisão: "demorou a cortar, ficou um gap" em pausas de 0,46-0,56 s; "ficou certinho" numa de 0,24 s). As
# proteções de borda (cauda, estende, quieto) continuam: o corte não come o fim da palavra.
# --ritmo-natural volta à regra de 09/10 (pausa normal medida até 0,55-0,90 s fica inteira).
RITMO_JUSTO = {"teto": 0.30, "tipica": 0.22}
# Silêncios forçados (s do bruto) que a tela dividida mede pelo ALINHAMENTO das palavras (td.py montar ->
# T/apertar.json): fôlego/ruído de boca colado na fala passa como voz pelo volume e a pausa ficava 0,6-0,8 s.
SILENCIOS: list[tuple[float, float]] = []


def tirar_silencios(rs: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Recorta das regiões de voz os silêncios forçados (SILENCIOS)."""
    for p, q in SILENCIOS:
        novo = []
        for a, b in rs:
            if q <= a or p >= b:
                novo.append((a, b))
                continue
            if p - a >= 0.02:
                novo.append((a, p))
            if b - q >= 0.02:
                novo.append((q, b))
        rs = novo
    return rs


def medir_ritmo(vf, dec: dict, pal: list[dict]) -> dict:
    """Ritmo de fala DESTE vídeo. Usuário, 09/10/2026: "medir as pausas e entender qual é uma pausa normal da fala e
    qual é uma pausa acentuada que quebra o ritmo" (pelo roteiro/pontuação não acerta). Mede as pausas voz a voz
    dentro dos trechos que ficam. Nos 11 vídeos de 08/10: ~720 pausas normais (quase todas < 0,6 s) x ~115 de 1 a 6 s
    (espera do teleprompter), quase nada entre 0,8 e 1 s. teto = 90% das pausas abaixo de 1,2 s (limitado a
    0,55-0,90 s): até ele a pausa FICA intacta; acima, vira a pausa típica (mediana das normais acima de 0,2 s)."""
    g = []
    for tre in dec["trechos"]:
        a, b = float(pal[int(tre["de"])]["inicio"]), float(pal[int(tre["ate"])]["fim"])
        rs = vf.regioes(a - 0.05, b + 0.3)
        g += [y0 - x1 for (x0, x1), (y0, y1) in zip(rs, rs[1:]) if y0 - x1 > 0.05]
    g = np.array(g)
    if len(g) < 10 or (g < 1.2).sum() < 5:
        return dict(RITMO)
    teto = float(np.clip(np.percentile(g[g < 1.2], 90), PAUSA_TETO_MIN, PAUSA_TETO_MAX))
    normais = g[(g > 0.2) & (g <= teto)]
    tipica = float(np.clip(np.median(normais), 0.28, 0.50)) if len(normais) else PAUSA_ALVO
    return {"teto": round(teto, 3), "tipica": round(tipica, 3), "pausas_medidas": int(len(g)),
            "quebram_ritmo": int((g > teto).sum())}


# ---------------------------------------------------------------- energia
def ler_wav(p: Path) -> tuple[np.ndarray, int]:
    with wave.open(str(p), "rb") as w:
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    return x, sr


class Energia:
    """Envelope em dB (janela 30 ms, passo 10 ms) com duas faixas:
    VOZ  (alto - 24 dB): acha onde a fala começa/termina — respiração e estalo não chegam lá;
    BAIXA (piso + 6 dB): só estende a borda da fala (o "s" final, o ataque de fricativa)."""

    def __init__(self, x: np.ndarray, sr: int):
        hop, win = int(sr * HOP), int(sr * 0.03)
        n = max(1, (len(x) - win) // hop)
        idx = np.arange(n)[:, None] * hop + np.arange(win)[None, :]
        self.db = 20 * np.log10(np.sqrt((x[idx] ** 2).mean(axis=1) + 1e-12) + 1e-9)
        piso, alto = np.percentile(self.db, 8), np.percentile(self.db, 90)
        self.voz = float(min(max(alto - 24, -52), -35))
        self.pico = alto - 12                      # uma fala de verdade passa disso
        self.baixa = float(max(piso + 6, self.voz - 14))

    def falas(self, t0: float, t1: float) -> list[list[float]]:
        """Trechos de fala em [t0, t1]: núcleo de voz + bordas na faixa baixa."""
        db = self.db
        a, b = max(0, int(t0 / HOP)), min(len(db), int(math.ceil(t1 / HOP)))
        on = db[a:b] >= self.voz
        runs, ini = [], None
        for k, v in enumerate(on):
            if v and ini is None:
                ini = k
            if not v and ini is not None:
                runs.append([a + ini, a + k])
                ini = None
        if ini is not None:
            runs.append([a + ini, b])
        fund = []                                   # fechamento de oclusiva não separa
        for r in runs:
            if fund and r[0] - fund[-1][1] < int(SIL_MIN / HOP):
                fund[-1][1] = r[1]
            else:
                fund.append(r)
        fund = [r for r in fund if r[1] - r[0] >= 4 and db[r[0]:r[1]].max() >= self.pico]
        out = []
        for k, (s, e) in enumerate(fund):
            lim_ant = fund[k - 1][1] if k else a
            lim_seg = fund[k + 1][0] if k + 1 < len(fund) else b
            s2 = s
            while s2 - 1 >= max(lim_ant, s - 10) and db[s2 - 1] >= self.baixa:
                s2 -= 1
            e2 = e
            while e2 < min(lim_seg, e + 10) and db[e2] >= self.baixa:   # 0,10 s: cauda do "s" sim, respiração não
                e2 += 1
            out.append([s2 * HOP, e2 * HOP, s * HOP, e * HOP])   # borda ini/fim, núcleo ini/fim
        return out


def energia_em(en: Energia, t: float) -> float:
    """Maior nível (dB) em +-10 ms do instante t."""
    k = int(round(t / HOP))
    return float(en.db[max(0, k - 1):min(len(en.db), k + 2)].max())


def fronteira(en: Energia, lo: float, hi: float, alvo: float) -> int:
    """Quadro n (corte em n/FPS) dentro de [lo, hi] para cortar no silêncio.

    Entre os candidatos silenciosos (abaixo da faixa baixa - 3 dB) fica o mais perto do alvo;
    se nenhum for silencioso, o de menor energia."""
    n0, n1 = math.ceil(lo * FPS), math.floor(hi * FPS)
    if n1 < n0:
        return int(round(alvo * FPS))
    cand = [(n, energia_em(en, n / FPS)) for n in range(n0, n1 + 1)]
    quietos = [c for c in cand if c[1] <= en.baixa - 3]
    if quietos:
        return min(quietos, key=lambda c: abs(c[0] / FPS - alvo))[0]
    return min(cand, key=lambda c: (c[1], abs(c[0] / FPS - alvo)))[0]


def remapear(palavras: list[dict], corte_velho: dict, segs_novos: list[dict]) -> list[dict]:
    """Leva as palavras do corte antigo para o novo pelo tempo do BRUTO (mesmos índices).
    Serve para ajuste fino de pontos de corte sem refazer a legenda."""
    velhos = corte_velho["segmentos"]

    def conv(t: float) -> float:
        k = max((i for i, s in enumerate(velhos) if s["dst_in"] <= t + 1e-6), default=0)
        src = velhos[k]["src_in"] + (t - velhos[k]["dst_in"])
        j = min(range(len(segs_novos)), key=lambda i: 0 if segs_novos[i]["src_in"] <= src <= segs_novos[i]["src_out"]
                else min(abs(src - segs_novos[i]["src_in"]), abs(src - segs_novos[i]["src_out"])))
        s = segs_novos[j]
        if src < s["src_in"]:                       # palavra que saiu do corte: vai para o ataque da fala
            src = max(s["src_in"], s.get("fala_in", s["src_in"]) - 0.02)
        src = min(max(src, s["src_in"]), s["src_out"])
        return s["dst_in"] + (src - s["src_in"])

    out = []
    for w in palavras:
        w2 = dict(w)
        w2["inicio"], w2["fim"] = round(conv(w["inicio"]), 3), round(conv(w["fim"]), 3)
        w2["seg"] = max(i for i, s in enumerate(segs_novos) if s["dst_in"] <= w2["inicio"] + 1e-3)
        out.append(w2)
    return out


def refinar_inicios(palavras: list[dict], en: Energia) -> int:
    """O Whisper às vezes 'estica' a palavra por cima da pausa anterior (começa no silêncio).
    Se os primeiros 150 ms da palavra não têm voz, o início vai para o 1o ataque de voz dentro
    dela (e a pausa_antes cresce: a legenda não soma o atraso de fala corrida). Devolve quantas mudou."""
    n = 0
    for k, w in enumerate(palavras):
        a, b = int(w["inicio"] / HOP), int(w["fim"] / HOP)
        if b - a < 15:
            continue
        # silêncio de >= 0,12 s começando na 1a metade da palavra = pausa que o Whisper engoliu
        sil = en.db[a:b] < en.baixa
        fim_sil, run = None, 0
        for j, s_ in enumerate(sil):
            run = run + 1 if s_ else 0
            if run >= 12 and (j - run + 1) <= 0.6 * (b - a):
                fim_sil = j
        if fim_sil is None:
            continue
        depois = np.where(en.db[a + fim_sil:b] >= en.voz)[0]
        if len(depois) == 0:
            continue
        novo = round((a + fim_sil + depois[0]) * HOP - 0.02, 3)
        if novo - w["inicio"] >= 0.12 and novo < w["fim"] - 0.05:
            w["inicio"] = novo
            if k > 0:
                w["pausa_antes"] = round(novo - palavras[k - 1]["fim"], 3)
            n += 1
    return n


def acha_fala(en: Energia, pal, i0, i1, dur, desde: float | None = None):
    """Início e fim reais da fala do trecho de palavras i0..i1 (por energia). `desde`: a fala não
    começa antes disso (recomeço depois de falso começo escondido dentro da palavra esticada)."""
    w0, w1 = pal[i0]["inicio"], pal[i1]["fim"]
    lo = max(0.0, w0 - BUSCA_ANTES)
    hi_lim = dur                    # limite duro: a próxima palavra do bruto (descartada ou não)
    if i0 > 0:                      # não invadir a palavra anterior (descartada)
        lo = max(lo, min(pal[i0 - 1]["fim"], w0) + 0.02)
    if desde is not None:
        lo, w0 = max(lo, desde), max(w0, desde)
    if i1 + 1 < len(pal):
        hi_lim = min(hi_lim, max(pal[i1 + 1]["inicio"], w1) - 0.02)
    hi = min(hi_lim, w1 + 0.45)
    rs = en.falas(lo, hi)
    # 1a fala que começa depois de lo (não herdada da palavra anterior) e perto de w0
    cand = [r for r in rs if r[2] > lo + 0.03 and r[2] <= w0 + BUSCA_DEPOIS]
    ini = cand[0][0] if cand else w0
    # última fala que termina antes de hi e cujo núcleo começa até o fim da última palavra
    fim_c = [r for r in rs if r[3] < hi - 0.03 and r[2] <= w1 + 0.05 and r[1] > ini]
    fim = fim_c[-1][1] if fim_c else w1
    # a última fala passou da janela porque o Whisper marcou o fim da frase CEDO ("comenta GPS" some):
    # procura o fim real até 1,2 s depois, sem invadir a próxima palavra do bruto
    cortada = [r for r in rs if r[3] >= hi - 0.03 and r[2] <= w1 + 0.05 and r[1] > ini]
    if cortada and hi < hi_lim - 0.05:
        hi2 = min(hi_lim, w1 + 1.2)
        ext = [r for r in en.falas(lo, hi2) if abs(r[2] - cortada[-1][2]) < 0.03 and r[3] < hi2 - 0.03]
        if ext:
            fim = max(fim, ext[-1][1])
    # a voz emenda sem pausa na próxima palavra do bruto (descartada pelo FIM): o fim é a fronteira entre
    # as palavras, não a fala anterior (09/10/2026: "ignorar o que ainda funciona", "tudo bem", "de vida" sumiam)
    elif cortada and i1 + 1 < len(pal):
        fim = max(fim, hi_lim)
    if fim <= ini:
        ini, fim = w0, w1
    return ini, fim


MARGEM_VOZ_INI = 0.02   # s: folga mínima antes do ataque da voz (a pausa encurtada usa RITMO["tipica"])
FIM_EXTRA = 0.40        # s: quanto o fim da frase pode passar do corte original se a voz continua
ONDA_FRACA_ANTES = 0.10 # s: o começo pode recuar até isso se houver sussurro ("e" quase mudo de "e talvez")
ONDA_FRACA_DEPOIS = 0.12 # s: o fim pode avançar até isso se houver soltura/"s" fraco ("escolhid-o", -43 dB)
CAUDA_MAX = 0.10        # s: a vogal final ("circ-o", "mand-a", "escut-a", "grup-o") segue até cair no silêncio
FADE_CAUDA = 0.025      # s: folga para a saída suave (render_final.FADE_FIM) depois da cauda
# (09/10/2026: 4 palavras "cortadas" no fim antes de emenda; o corte parava a ~-37 dB do pico e a soltura sumia)


def aparar(segs: list[dict], trabalho: Path, fonte: str, avisos: list[str], pal: list[dict]) -> list[dict]:
    """Cada segmento é recortado nos trechos de voz exatos (borda_voz.VozFina); pausa interna >=
    SIL_CORTE vira emenda. Nunca passa dos limites do segmento original (não invade fala vizinha);
    o último segmento mantém o respiro final antes da CTA."""
    from borda_voz import VozFina
    vf = VozFina(trabalho, fonte)
    novos, cortes, antes = [], 0, sum(s["frames"] for s in segs)
    for k, s in enumerate(segs):
        f0, f1 = s["frame_in"], s["frame_in"] + s["frames"]
        # o fim da frase pode passar do corte original se a voz ainda continua ("rot-a" e o "s" final
        # cortados na v3): até FIM_EXTRA, sem chegar na próxima palavra do bruto nem no próximo pedaço
        f1_max = f1
        prox_src = segs[k + 1]["frame_in"] if k + 1 < len(segs) else None
        if prox_src != f1 and k + 1 < len(segs) or k + 1 == len(segs):
            lim = f1 / FPS + FIM_EXTRA
            if s["i1"] + 1 < len(pal):
                lim = min(lim, pal[s["i1"] + 1]["inicio"] - 0.05)
            if prox_src is not None and prox_src > f1:
                lim = min(lim, prox_src / FPS)
            f1_max = max(f1, int(math.floor(lim * FPS)))
        rs = tirar_silencios(vf.regioes(f0 / FPS, f1_max / FPS))
        rs = [r for r in rs if r[0] < f1 / FPS + 0.25]       # além do corte original, só o que emenda na frase
        blocos = []                       # [ini, fim, pausa natural depois?]
        for a, b in rs:
            if blocos and a - blocos[-1][1] < RITMO["teto"]:    # pausa normal da fala: fica
                blocos[-1][1] = b
            else:
                blocos.append([a, b, False])
        if not blocos:
            novos.append(s)
            continue
        for j, (a, b, _) in enumerate(blocos):
            # as bordas seguem a onda FRACA da própria palavra (sussurro, soltura, "s"), senão ficam coladas
            # ...mas nunca além da METADE da pausa até o bloco vizinho (v3: em 0:15 as duas bordas se cruzaram e o
            # trecho do meio tocou duas vezes — a pausa ficou MAIOR que a original)
            meio_ant = (blocos[j - 1][1] + a) / 2 if j else -1e9
            meio_prox = (b + blocos[j + 1][0]) / 2 if j + 1 < len(blocos) else 1e9
            a2 = max(vf.estende(a, -1, ONDA_FRACA_ANTES), meio_ant)
            # + a soltura TARDIA da última vogal (depois de um vão de ~0,1 s; 13/10/2026: "crescimento", "certo",
            # "escuta", "grupo" 3x, "desrespeito" cortados) — borda_voz.soltura
            b2 = min(max(vf.estende(b, +1, ONDA_FRACA_DEPOIS), vf.soltura(b)), meio_prox)
            b3 = min(vf.cauda(b, CAUDA_MAX), meio_prox)          # a vogal final morrendo até o silêncio
            meia = RITMO["tipica"] / 2                    # pausa encurtada = pausa típica do vídeo
            n_in = max(f0, int(math.floor(max(min(a, a2) - meia, meio_ant) * FPS)))
            n_out = min(max(f1_max, f1), int(math.ceil(min(max(b + meia, b2 + MARGEM_VOZ_INI,
                                                               b3 + FADE_CAUDA), meio_prox) * FPS)))
            # a borda nunca cai em cima de um som solto (estalo de boca, respiro): escolhe o quadro mais silencioso
            # entre o fim da voz e a borda calculada ("feito" do Palhaço, 09/10/2026: o corte caía no meio de um
            # estalo 150 ms depois da palavra e soava como a palavra cortada)
            lim_som = vf.piso + 12
            q_voz = int(math.ceil(max(b, b2, b3) * FPS))
            if n_out - q_voz >= 2 and vf.nivel(n_out / FPS - 0.03, n_out / FPS) > lim_som:
                n_out = min(range(q_voz, n_out + 1), key=lambda q: (vf.nivel(q / FPS - 0.03, q / FPS), -q))
            q_voz = int(math.floor(min(a, a2) * FPS))
            if q_voz - n_in >= 2 and vf.nivel(n_in / FPS, n_in / FPS + 0.03) > lim_som:
                n_in = min(range(n_in, q_voz + 1), key=lambda q: (vf.nivel(q / FPS, q / FPS + 0.03), q))
            if novos and novos[-1].get("_k") == k and n_in <= novos[-1]["frame_in"] + novos[-1]["frames"] + 1:
                ult = novos[-1]                               # encostou no bloco anterior: sem corte aqui
                ult["frames"] = max(ult["frames"], n_out - ult["frame_in"])
                ult["src_out"] = round((ult["frame_in"] + ult["frames"]) / FPS, 4)
                ult["voz_out"] = round(b, 3)
                cortes -= 1
                continue
            if k == len(segs) - 1 and j == len(blocos) - 1:
                n_out = f1                                   # respiro final antes da CTA
            if n_out - n_in < 3:
                continue
            novos.append({**s, "frame_in": n_in, "frames": n_out - n_in, "src_in": round(n_in / FPS, 4),
                          "src_out": round(n_out / FPS, 4), "voz_in": round(a, 3), "voz_out": round(b, 3), "_k": k})
        cortes += len(blocos) - 1
    for s in novos:
        s.pop("_k", None)
    depois = sum(s["frames"] for s in novos)
    avisos.append(f"aparar: {cortes} pausas internas cortadas, {(antes - depois) / FPS:.1f}s de silêncio a menos")
    print(f"  aparar na borda da onda: {cortes} pausas internas cortadas, {(antes - depois) / FPS:.1f}s a menos",
          flush=True)
    return novos


# ---------------------------------------------------------------- principal
def main() -> None:
    trabalho = Path(sys.argv[1])
    usar_whisper = "--sem-whisper" not in sys.argv
    manter = "--manter-palavras" in sys.argv       # ajuste fino: não retranscreve, remapeia
    corte_velho = None
    if (trabalho / "corte.json").exists():
        corte_velho = ler_json(trabalho / "corte.json")
        gravar_json(trabalho / "corte_anterior.json", corte_velho)
    if manter and not (corte_velho and (trabalho / "palavras_corte.json").exists()):
        raise SystemExit("--manter-palavras precisa de um corte.json e palavras_corte.json anteriores")
    tr = ler_json(trabalho / "transcricao.json")
    pal = tr["palavras"]
    dec = ler_json(trabalho / "decupagem.json")
    from borda_voz import VozFina
    RITMO.update(medir_ritmo(VozFina(trabalho, tr["arquivo"]), dec, pal))
    if "--ritmo-natural" not in sys.argv:   # justo é o padrão (TD 09/10, novela 11/10/2026); --ritmo-justo segue aceito
        RITMO.update(teto=min(RITMO["teto"], RITMO_JUSTO["teto"]), tipica=min(RITMO["tipica"], RITMO_JUSTO["tipica"]))
        if (trabalho / "apertar.json").exists():
            SILENCIOS[:] = [tuple(x) for x in ler_json(trabalho / "apertar.json")]
            print(f"  silêncios forçados (alinhamento): {len(SILENCIOS)}", flush=True)
    print(f"  ritmo da fala: pausa normal até {RITMO['teto']:.2f}s (fica); maiores quebram o ritmo -> "
          f"{RITMO['tipica']:.2f}s ({RITMO.get('quebram_ritmo', '?')} de {RITMO.get('pausas_medidas', '?')})", flush=True)
    x16, sr16 = ler_wav(trabalho / "audio16k.wav")
    en = Energia(x16, sr16)
    dur_src = float(tr["duracao"])

    # 1) cada trecho -> fala real -> sub-trechos (silêncio interno longo sai)
    pedacos = []   # (ini_fala, fim_fala, i0, i1, cauda)
    for tre in dec["trechos"]:
        i0, i1 = int(tre["de"]), int(tre["ate"])
        if not (0 <= i0 <= i1 < len(pal)):
            raise SystemExit(f"trecho inválido: {tre}")
        ini, fim = acha_fala(en, pal, i0, i1, dur_src, tre.get("desde"))
        rs = [r for r in en.falas(ini - 0.001, fim + 0.001) if r[1] > ini and r[0] < fim]
        blocos = [[rs[0][0], rs[0][1], False]] if rs else [[ini, fim, False]]
        for r in rs[1:]:
            if r[0] - blocos[-1][1] > RITMO["teto"]:          # pausa que quebra o ritmo: vira emenda
                blocos.append([r[0], r[1], False])
            else:
                blocos[-1][1] = r[1]
        for k, (a, b, nat) in enumerate(blocos):
            ultimo = k == len(blocos) - 1
            cauda = MARGEM_FIM
            if ultimo and tre.get("pausa_depois"):
                cauda = max(MARGEM_FIM, float(tre["pausa_depois"]))
            pedacos.append((a, b, i0, i1, cauda, not ultimo, nat))

    # 2) pontos de corte: a fronteira de quadro mais silenciosa perto do alvo, sem invadir
    #    a fala que fica nem a fala vizinha (o áudio é cortado exatamente no quadro)
    segs = []
    avisos = []
    for k, (a, b, i0, i1, cauda, interno, nat) in enumerate(pedacos):
        cab = MARGEM_INI
        # pausa encurtada (quebrava o ritmo) fica com a pausa típica do vídeo; entre frases seguidas da MESMA tomada a
        # pausa natural fica inteira até o teto (o 2b encurta as maiores)
        seguido = k + 1 < len(pedacos) and pedacos[k + 1][2] == i1 + 1
        if interno:
            cauda = RITMO["tipica"] / 2
        elif seguido:
            cauda = max(cauda, RITMO["teto"] / 2)
        ant_seguido = k > 0 and not pedacos[k - 1][5] and pedacos[k - 1][3] + 1 == i0
        if k > 0 and pedacos[k - 1][5]:
            cab = RITMO["tipica"] / 2
        elif ant_seguido:
            cab = RITMO["teto"] / 2
        if k == len(pedacos) - 1:
            cauda = max(cauda, FIM_RESPIRO)  # a imagem segue ~0,45 s e corta seco para a CTA
        nucleo = [r for r in en.falas(a - 0.001, b + 0.001) if r[1] > a and r[0] < b]
        c_ini = nucleo[0][2] if nucleo else a
        c_fim = nucleo[-1][3] if nucleo else b
        antes = [r for r in en.falas(max(0.0, a - 1.5), a - 0.001) if r[1] <= a]
        depois = [r for r in en.falas(b + 0.001, min(dur_src, b + 1.5)) if r[0] >= b]
        fim_viz = antes[-1][1] if antes else 0.0
        ini_viz = depois[0][0] if depois else dur_src
        n_in = fronteira(en, max(fim_viz + 0.02, a - cab - 0.10), min(a - 0.01, c_ini - 0.03), a - cab)
        n_out = fronteira(en, max(b + 0.01, c_fim + 0.03), min(ini_viz - 0.02, b + cauda + 0.10), b + cauda)
        if segs and segs[-1]["frame_in"] < n_in < segs[-1]["frame_in"] + segs[-1]["frames"]:
            n_in = segs[-1]["frame_in"] + segs[-1]["frames"]
        n_in = max(0, n_in)
        n_out = min(int(dur_src * FPS), max(n_out, n_in + 1))
        s = {"i0": i0, "i1": i1, "frame_in": n_in, "frames": n_out - n_in,
             "src_in": round(n_in / FPS, 4), "src_out": round(n_out / FPS, 4),
             "fala_in": round(a, 3), "fala_out": round(b, 3), "voz_in": round(c_ini, 3), "voz_out": round(c_fim, 3)}
        segs.append(s)

    # 2b) silêncio na emenda medido de VOZ a VOZ (sem o respiro da borda): nenhuma emenda com mais de
    #     PAUSA_MAX — o usuário reprovou 0,5 s parado entre "resolvendo problemas" e "acelerando" (28/09/2026)
    for k in range(1, len(segs)):
        ant, s = segs[k - 1], segs[k]
        cauda = ant["src_out"] - ant["voz_out"]
        cabeca = s["voz_in"] - s["src_in"]
        sobra = cauda + cabeca - RITMO["tipica"]
        if cauda + cabeca <= RITMO["teto"] or sobra <= 0:
            continue
        max_c, max_h = max(0.0, cauda - 0.07), max(0.0, cabeca - 0.05)   # sem comer o fim/ataque da voz
        tira_c = min(max_c, sobra / 2)
        tira_h = min(max_h, sobra - tira_c)
        tira_c = min(max_c, sobra - tira_h)
        fc, fh = int(round(tira_c * FPS)), int(round(tira_h * FPS))
        if fc:
            ant["frames"] -= fc
            ant["src_out"] = round((ant["frame_in"] + ant["frames"]) / FPS, 4)
        if fh:
            s["frame_in"] += fh
            s["frames"] -= fh
            s["src_in"] = round(s["frame_in"] / FPS, 4)
        avisos.append(f"emenda seg{k - 1:02d}/seg{k:02d}: silêncio de voz a voz {cauda + cabeca:.2f}s -> "
                      f"{cauda + cabeca - (fc + fh) / FPS:.2f}s")

    # 2c) APARAR na borda exata da onda (48 kHz, 5 ms; borda_voz.py): toda pausa >= SIL_CORTE sai, dentro
    #     da frase ou na emenda; ficam só ~MARGEM_VOZ antes/depois da voz (usuário, 28/09/2026: "cortes
    #     certeiros, sem espacinho em branco — dá para deduzir que ele está lendo")
    if "--sem-aparar" not in sys.argv:
        segs = aparar(segs, trabalho, tr["arquivo"], avisos, pal)

    for k, s in enumerate(segs):
        n_in, n_out = s["frame_in"], s["frame_in"] + s["frames"]
        for nome, t in (("entrada", n_in / FPS), ("saída", n_out / FPS)):
            e = energia_em(en, t)
            s[f"db_{'in' if nome == 'entrada' else 'out'}"] = round(e, 1)
            if e > en.baixa:
                avisos.append(f"seg{k:02d} {nome} em {t:.2f}s do bruto corta som de {e:.0f} dB")

    # 3) linha do tempo editada
    t = 0.0
    for s in segs:
        s["dst_in"] = round(t, 4)
        t += s["frames"] / FPS
    dur = round(t, 4)
    gravar_json(trabalho / "corte.json", {"fonte": tr["arquivo"], "fps": FPS, "duracao_fala": dur,
                                          "segmentos": segs, "avisos": avisos, "ritmo": RITMO})

    # 4) áudio do corte (16 kHz, para conferência/legenda)
    partes = []
    for s in segs:
        a = int(round(s["frame_in"] / FPS * sr16))
        n = int(round(s["frames"] / FPS * sr16))
        partes.append(x16[a:a + n])
    y = np.concatenate(partes)
    with wave.open(str(trabalho / "audio_corte16k.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr16)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())

    # 5) roteiro legível (texto do bruto por segmento)
    out = [f"# corte: {len(segs)} segmentos, {dur:.2f}s de fala", ""]
    for k, s in enumerate(segs):
        ws = [w for w in pal[s["i0"]:s["i1"] + 1] if w["fim"] > s["src_in"] + 0.03 and w["inicio"] < s["src_out"] - 0.03]
        txt = " ".join(w["texto"] for w in ws)
        out.append(f"{s['dst_in']:7.2f}s  seg{k:02d}  bruto {s['src_in']:7.2f}-{s['src_out']:7.2f}  | {txt}")

    # 6) palavras do corte: Whisper no áudio cortado (o que a legenda vai mostrar)
    novas = []
    en_corte = Energia(y, sr16)
    en_corte.voz, en_corte.baixa, en_corte.pico = en.voz, en.baixa, en.pico   # mesmos limiares do bruto
    if manter:
        velhas = ler_json(trabalho / "palavras_corte.json")
        novas = remapear(velhas["palavras"], corte_velho, segs)
        refinadas = refinar_inicios(novas, en_corte)
        gravar_json(trabalho / "palavras_corte.json", {"fonte": velhas.get("fonte", "") + " (remapeado)",
                                                       "palavras": novas, "inicios_refinados": refinadas})
        usar_whisper = False
    if usar_whisper:
        from comum import whisper
        model = whisper()
        sgs, _ = model.transcribe(str(trabalho / "audio_corte16k.wav"), language="pt", word_timestamps=True,
                                  vad_filter=False, beam_size=5, condition_on_previous_text=False)
        novas = []
        for sg in sgs:
            for w in sg.words or []:
                txt = w.word.strip()
                if not txt:
                    continue
                gap = (w.start - novas[-1]["fim"]) if novas else 9.0
                seg = max(k for k, s in enumerate(segs) if s["dst_in"] <= w.start + 1e-3)
                novas.append({"i": len(novas), "texto": txt, "inicio": round(w.start, 3), "fim": round(w.end, 3),
                              "pausa_antes": round(gap, 3), "seg": seg, "prob": round(w.probability, 2)})
        refinadas = refinar_inicios(novas, en_corte)
        gravar_json(trabalho / "palavras_corte.json", {"fonte": "whisper no áudio do corte", "palavras": novas,
                                                       "inicios_refinados": refinadas})
        out += ["", "# palavras do corte (índices para a legenda)", ""]
        linha, ant = [], None
        for w in novas:
            if linha and w["inicio"] - ant["fim"] >= 0.3:
                out.append(f"[{linha[0]['i']:03d}-{linha[-1]['i']:03d}] {linha[0]['inicio']:6.2f}s  "
                           + " ".join(f"{x['texto']}" for x in linha))
                linha = []
            linha.append(w)
            ant = w
        if linha:
            out.append(f"[{linha[0]['i']:03d}-{linha[-1]['i']:03d}] {linha[0]['inicio']:6.2f}s  "
                       + " ".join(f"{x['texto']}" for x in linha))
    if manter:
        out += ["", "# palavras do corte: mantidas do corte anterior (índices iguais, tempos remapeados)"]
    if avisos:
        out += ["", "# avisos de corte"] + [f"- {a}" for a in avisos]
    (trabalho / "roteiro_corte.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"ok: {len(segs)} segmentos, {dur:.2f}s de fala, {len(novas)} palavras no corte, "
          f"{len(avisos)} avisos de corte")
    for a in avisos:
        print("  aviso:", a)

    # 7) alinhamento forçado (WhisperX, venv própria com torch CUDA): tempo de palavra ~1 quadro
    import os
    import subprocess
    py_al = Path(os.environ.get("LOCALAPPDATA", "")) / "reels-novela" / "venv-align" / "Scripts" / "python.exe"
    if py_al.exists() and "--sem-alinhar" not in sys.argv:
        r = subprocess.run([str(py_al), str(Path(__file__).with_name("alinhar.py")), str(trabalho)],
                           capture_output=True, text=True, env={**os.environ, "PYTHONUTF8": "1"})
        ult = (r.stdout.strip().splitlines() or [""])[-1]
        print("  alinhamento:", ult if r.returncode == 0 else f"falhou: {r.stderr.strip()[-400:]}")
    # lista compacta para o legendista (formato plano_texto)
    from plano_texto import palavras_legenda
    palavras_legenda(trabalho)


if __name__ == "__main__":
    main()
