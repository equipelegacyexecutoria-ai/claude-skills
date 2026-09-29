"""Constantes e utilitários do pipeline Reels TELA DIVIDIDA (Clailton).

Reaproveita a skill reels-novela-clailton (transcrição, decupagem, corte colado na voz,
alinhamento, texto/kerning do libass, CTA, áudio). Tudo o que é específico da tela dividida
(medido nos 6 reels da equipe: referencia/estilo-tela-dividida.md) está aqui.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
NOVELA = Path.home() / ".claude" / "skills" / "reels-novela-clailton"
NOVELA_S = NOVELA / "scripts"
if str(NOVELA_S) not in sys.path:
    sys.path.insert(0, str(NOVELA_S))

from comum import FPS, FPS_DEN, FPS_NUM, MODELO_ROSTO, gravar_json, ler_json, sonda  # noqa: E402,F401

W, H = 1080, 1920

# ---------------- quadro (medido) ----------------
EMENDA = 768                 # tela dividida: imagem em y 0..EMENDA (medido 32-50%, mediana ~40%)
ROSTO_ABERTO = 0.30          # largura do rosto / largura do quadro no plano aberto
ROSTO_CY_ABERTO = 0.30       # centro do rosto (fração da altura) no plano aberto
FECHADO_FATOR = 1.50         # punch-in do fechado sobre o aberto (medido 1,45-1,6)
FECHADO_FATOR_MIN = 1.25     # quando o bruto já vem fechado demais
ROSTO_MAX = 0.62             # rosto nunca maior que isso
# o fechado NÃO recentra o rosto: é o aberto ampliado em volta do ponto entre os olhos (rect_zoom),
# que fica na mesma altura (regra do usuário, 28/09/2026: "todo zoom mantém a altura dos olhos")
DIVIDIDA_ROSTO_CY = 0.62     # na tela dividida o rosto desce para ~62% da altura do quadro
UPSCALE_MAX = 1.40           # recorte nunca ampliado mais que isso (qualidade)

# ---------------- imagem ----------------
ZOOM_FOTO = 0.05             # foto/ilustração: zoom-out constante ~5%/s (medido 4,2-6,5%/s)
ZOOM_FOTO_MAX = 0.18         # teto do zoom inicial (imagem longa)
ZOOM_CARTAO = 0.015          # cartão: quase parado (1,5%/s de zoom-in)
CARTAO_LARG = 0.86           # cartão ocupa 86% da largura
CARTAO_CY = 0.47             # centro do cartão (Duty Free: ~0,5; a legenda cai na parte de baixo do cartão)

# ---------------- legenda (medido) ----------------
LEG_CAP = 34.0               # altura da maiúscula da legenda (px)
LEG_TRACK = -0.085           # * fs, por letra (kerning aplicado à mão)
LEG_Y = 1175.0               # centro vertical da linha (61%)
LEG_MAX_LARG = 760.0         # linha maior que isso encolhe
LEG_MAX_CHARS = 20
LEG_MAX_PALAVRAS = 4
TARJA_CAP = 52.0             # abertura: texto branco em caixa preta colada na emenda
TARJA_PAD_X, TARJA_PAD_Y = 22.0, 22.0
NUMERO_CAP = 135.0           # número grande (opcional)
NUMERO_Y = 960.0
ETIQUETA_CAP = 44.0          # etiqueta fixa da abertura (opcional)
ETIQUETA_LEG_Y = 1460.0      # com etiqueta, a legenda da abertura fica no peito dele (Fórmula: ~76%)
ETIQUETA_CORES = {"vermelha": "0000C3", "azul": "B5561E", "branca": "FFFFFF", "preta": "000000"}  # BGR do ASS
LEAD = 1.0 / FPS             # corte e legenda entram 1 quadro antes do início da palavra

# ---------------- estilo "película" (estilo_td.py; referência: reel da história do Clailton) ----------------
ESTILO_FORCA = 1.0           # 0 desliga; a linha "ESTILO 0.7" no plano.txt muda só aquele vídeo

# ---------------- zoom (regras do usuário, 28/09/2026; TD e edição simples) ----------------
# 1) zoom SECO (aberto <-> fechado) só na emenda (corte); 2) zoom fora do corte só ANIMADO (keyframes),
# com entrada e saída suaves; 3) todo zoom mantém os olhos na mesma altura (ancorado nos olhos).
# Padrão do plano_td.py; a linha ZOOMLIVRE no plano.txt volta ao fechado antigo (no meio da fala).
ZOOM_SUAVE = 1.18            # zoom animado: escala final sobre o aberto
ZOOM_SUAVE_RAMPA = 0.55      # s: duração da animação (entrada e saída suaves)
ZOOM_SUAVE_INTERVALO = 6.0   # s: no mínimo isso entre dois zooms animados
PLANO_MIN = 0.6              # s: nenhum plano (aberto/fechado) menor que isso
FECHADO_MAX = 4.0            # s: fechado mais longo que isso volta ao aberto na 1ª emenda possível
ABERTO_MAX = 7.0             # s: aberto mais longo que isso fecha na 1ª emenda boa
OLHO_MIN_FECHADO = 0.20      # no fechado, os olhos nunca acima de 20% da altura (testa no quadro)

# ---------------- transições ----------------
FLASH_ANTES = [1.35, 1.6, 1.75]   # ganho de brilho nos 3 quadros antes do corte (saída da abertura)
FLASH_DEPOIS = [1.75, 0.38, 0.55, 0.85]  # 1º quadro do plano novo claro, depois escuro, normal

# ---------------- ambiente ----------------
LOCAL = Path(os.environ.get("LOCALAPPDATA", ""))


def python_principal() -> str:
    for p in (LOCAL / "reels-novela" / "venv" / "Scripts" / "python.exe",
              LOCAL / "corte-viral" / "venv" / "Scripts" / "python.exe"):
        if p.exists():
            return str(p)
    return sys.executable


def python_align() -> str:
    """venv com torch CUDA + transformers (a do alinhador da novela): roda o CLIP."""
    p = LOCAL / "reels-novela" / "venv-align" / "Scripts" / "python.exe"
    return str(p) if p.exists() else python_principal()


def ff(args: list[str], cwd: Path | None = None, silencioso: bool = True) -> None:
    base = ["ffmpeg", "-hide_banner", "-y"] + (["-v", "error"] if silencioso else [])
    subprocess.run(base + args, check=True, cwd=cwd)


def dur_video(p: Path | str) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def wh_video(p: Path | str) -> tuple[int, int]:
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                        "-of", "csv=p=0", str(p)], capture_output=True, text=True)
    w, h = r.stdout.strip().split("\n")[0].split(",")[:2]
    return int(w), int(h)


# ---------------- rotação do bruto (câmera deitada) ----------------
def transpose_filtro(rot: int) -> str:
    """rot = graus no sentido horário para deixar o Clailton em pé."""
    return {0: "", 90: "transpose=1", 180: "transpose=1,transpose=1", 270: "transpose=2"}[rot % 360]


def rect_original(r: list[float], rot: int, w0: int, h0: int) -> list[int]:
    """Retângulo [x, y, w, h] no quadro GIRADO -> retângulo no quadro original (para cortar antes de girar)."""
    x, y, w, h = r
    rot %= 360
    if rot == 0:
        o = [x, y, w, h]
    elif rot == 90:        # horário: x_rot = h0 - 1 - y_o ; y_rot = x_o
        o = [y, h0 - x - w, h, w]
    elif rot == 270:       # anti-horário: x_rot = y_o ; y_rot = w0 - 1 - x_o
        o = [w0 - y - h, x, h, w]
    else:
        o = [w0 - x - w, h0 - y - h, w, h]
    o = [int(round(v)) for v in o]
    # dimensões pares (yuv420)
    o[2] -= o[2] % 2
    o[3] -= o[3] % 2
    o[0] = max(0, min(o[0], w0 - o[2]))
    o[1] = max(0, min(o[1], h0 - o[3]))
    return o


def filtro_recorte(rect_rot: list[float], rot: int, w0: int, h0: int, out_w: int, out_h: int, rgb: bool = False) -> str:
    """crop no original -> gira -> escala (lanczos). Recortar antes de girar é mais barato.
    rgb=True: a mesma escala já converte para RGB com a matriz BT.709 (sem 2ª passada)."""
    x, y, w, h = rect_original(rect_rot, rot, w0, h0)
    t = transpose_filtro(rot)
    cor = ":in_color_matrix=bt709:in_range=tv" if rgb else ""
    return (f"crop={w}:{h}:{x}:{y}" + (f",{t}" if t else "")
            + f",scale={out_w}:{out_h}:flags=lanczos+accurate_rnd+full_chroma_int{cor},setsar=1"
            + (",format=rgb24" if rgb else ""))


def rect_zoom(ab: list[float], olhos: list[float] | None, s: float) -> list[float]:
    """Recorte do aberto ampliado s vezes em volta do ponto entre os olhos: os olhos ficam parados no
    quadro (mesma altura e mesma posição). Sempre dentro do aberto (logo, dentro do bruto)."""
    x, y, w, h = ab
    ox, oy = olhos if olhos else (x + w / 2, y + 0.3 * h)
    ox, oy = min(max(ox, x), x + w), min(max(oy, y), y + h)
    return [ox - (ox - x) / s, oy - (oy - y) / s, w / s, h / s]


def suave(u: float) -> float:
    """Curva de keyframe com entrada e saída suaves (smootherstep), u em 0..1."""
    u = min(max(u, 0.0), 1.0)
    return u * u * u * (u * (6 * u - 15) + 10)


def movel(p: dict) -> bool:
    """Plano cujo recorte muda quadro a quadro (zoom animado). O fechado é sempre parado."""
    return bool(p.get("escala"))


def rect_plano(p: dict, s: dict, k: int) -> list[float]:
    """Recorte (px do bruto girado) do quadro k do plano p (s = segmento do enquadramento_td)."""
    if p.get("escala"):
        return rect_zoom(s["aberto"], p.get("ancora") or s.get("olhos"), p["escala"][k])
    return p.get("rect") or s["fechado" if p["zoom"] == "fechado" else ("dividida" if p["zoom"] == "dividida" else "aberto")]


def regiao_plano(p: dict, s: dict) -> tuple[list[float], int, int]:
    """Zoom animado: região do bruto a decodificar (cobre todos os recortes) e o tamanho do quadro
    decodificado (na escala do recorte mais fechado, para o render nunca ampliar depois)."""
    n = p["f1"] - p["f0"]
    rs = [rect_plano(p, s, k) for k in range(n)]
    x0, y0 = min(r[0] for r in rs), min(r[1] for r in rs)
    x1, y1 = max(r[0] + r[2] for r in rs), max(r[1] + r[3] for r in rs)
    q = W / min(r[2] for r in rs)
    reg = [x0, y0, x1 - x0, y1 - y0]
    return reg, int(round(reg[2] * q / 2)) * 2, int(round(reg[3] * q / 2)) * 2


def carregar_json(p: Path, padrao=None):
    return json.loads(Path(p).read_text(encoding="utf-8")) if Path(p).exists() else padrao
