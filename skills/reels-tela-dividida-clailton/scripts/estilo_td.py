"""Camada de estilo "película" da tela dividida (referência: reel da história do Clailton,
instagram.com/p/Dc1tvV3sTO-, medida quadro a quadro em 2026-09-27):

  1. cor contida: saturação ~0,85, curva em S suave, sombra levemente fria e luz levemente quente
  2. vinheta radial (escurece os cantos)
  3. TEXTURA FIXA na tela, mais forte nos meios-tons (como "luz suave"): papel (grão + fibras cruzadas
     + linhas fracas de vergê) e uma retícula fina de pontinhos (período 4,43 px, girada 14°). É o que
     dá a cara da referência: extraída pela média de quadros de cenas diferentes (o conteúdo some, a
     textura fica). Nas cenas filmadas, depois do Instagram: papel desvio ~2,4, retícula ~1,0.
     Reproduzida aqui com o mesmo espectro. Fixa = sobrevive à recompressão do Instagram e quase
     não pesa no arquivo.
  4. granulado ANIMADO leve (muda a cada quadro): dá vida no arquivo final; o Instagram apaga quase
     todo (na referência, o resíduo fino tem correlação 0,84-1,00 entre quadros vizinhos: o que
     sobra depois do Instagram é o fixo)
  5. poeira de película: ciscos que duram 1-2 quadros em posição aleatória (claro sobre o escuro,
     escuro sobre o claro) e, raramente, um fio de cabelo

Entra SÓ NO B-ROLL (pedido do usuário, 27/09/2026): na tela cheia de imagem, o quadro todo; na tela
dividida, só a faixa de cima. O Clailton (o bruto) fica sem efeito. Depois da composição e ANTES da
legenda (a legenda fica limpa, como na referência). Cada região tem a sua vinheta.
Intensidade geral em `FORCA` (0 desliga); cada camada tem o seu peso abaixo.

Uso direto (prévia de calibração): python estilo_td.py <entrada.png> <saida.png> [força]
"""
from __future__ import annotations

import sys

import cv2
import numpy as np

W, H = 1080, 1920
FORCA = 1.0             # multiplica tudo (0 = sem estilo)
SATURACAO = 0.85
CONTRASTE = 1.07        # curva em S em torno do meio
SOMBRA_FRIA = 4.0       # níveis de azul somados nas sombras (e tirados do vermelho)
LUZ_QUENTE = 3.0        # níveis de vermelho somados nas altas luzes
VINHETA = 0.20          # escurecimento no canto (fração)
PAPEL = 4.6             # desvio da textura de papel fixa nos meios-tons (0-255); referência ~2,4 pós-Instagram (o nosso perde ~30%)
RETICULA = 2.0          # desvio da retícula de pontinhos (0-255); referência ~1,0 pós-Instagram (o nosso perde ~60%)
RETICULA_PASSO = 4.43   # período (px) e ângulo (graus) medidos na referência
RETICULA_ANG = 14.0
GRAO = 1.5              # desvio do granulado animado nos meios-tons (0-255)
GRAO_TAM = 0.9          # desfoque do grão animado (px)
POEIRA_POR_QUADRO = 1.6  # ciscos novos por quadro (média)
FIO_CHANCE = 0.012      # chance de um fio de cabelo por quadro
BANCO = 8               # campos de grão animado pré-gerados (sorteados com deslocamento)


def _nucleo(theta: float, sl: float, sc: float, r: int = 9) -> np.ndarray:
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1].astype(np.float32)
    u = xx * np.cos(theta) + yy * np.sin(theta)
    v = -xx * np.sin(theta) + yy * np.cos(theta)
    k = np.exp(-0.5 * ((u / sl) ** 2 + (v / sc) ** 2))
    return (k / np.sqrt((k * k).sum())).astype(np.float32)


def textura_papel(w: int, h: int, semente: int = 7) -> np.ndarray:
    """Papel procedural (desvio 1): grão arredondado + grão alongado em direções que variam + ~20 mil
    fibras curtas cruzadas + nuvem + linhas de vergê (período 14,6 px, medido). Espectro igual ao da
    referência nas faixas de 2 a 40 px."""
    rng = np.random.default_rng(semente)
    ruido = rng.standard_normal((h, w)).astype(np.float32)
    angs = np.linspace(0, np.pi, 6, endpoint=False)
    campos = np.stack([cv2.GaussianBlur(rng.standard_normal((h // 4, w // 4)).astype(np.float32), (0, 0), 2.0)
                       for _ in angs])
    campos = np.exp(2.0 * campos / campos.std())
    campos /= campos.sum(0, keepdims=True)
    rua = np.zeros((h, w), np.float32)
    for k, th in enumerate(angs):
        rua += cv2.resize(campos[k], (w, h)) * cv2.filter2D(ruido, -1, _nucleo(th, 1.9, 0.9))
    rua /= rua.std()
    blobs = cv2.GaussianBlur(rng.standard_normal((h, w)).astype(np.float32), (0, 0), 1.0)
    blobs /= blobs.std()
    n = int(20000 * w * h / (1080 * 1920))
    x, y = rng.uniform(-40, w + 40, n), rng.uniform(-40, h + 40, n)
    a, passo, npts = rng.uniform(0, np.pi, n), rng.uniform(3, 6, n), rng.integers(4, 16, n)
    cor = np.where(rng.random(n) < 0.75, -rng.uniform(0.4, 1.2, n), rng.uniform(0.3, 0.8, n))
    pts = np.zeros((n, int(npts.max()), 2), np.float32)
    for s in range(int(npts.max())):
        pts[:, s, 0], pts[:, s, 1] = x, y
        a += rng.normal(0, 0.25, n)
        x, y = x + passo * np.cos(a), y + passo * np.sin(a)
    fio = np.zeros((h, w), np.float32)
    for k in range(n):
        cv2.polylines(fio, [np.round(pts[k, :npts[k]] * 16).astype(np.int32)], False, float(cor[k]), 1,
                      cv2.LINE_AA, shift=4)
    fio = cv2.GaussianBlur(fio, (0, 0), 0.7)
    fio /= max(float(fio.std()), 1e-6)
    nuvem = cv2.GaussianBlur(rng.standard_normal((h // 8, w // 8)).astype(np.float32), (0, 0), 2)
    nuvem = cv2.resize(nuvem / nuvem.std(), (w, h), interpolation=cv2.INTER_CUBIC)
    yy = np.arange(h, dtype=np.float32)[:, None] + 3 * cv2.resize(nuvem[:, :1], (1, h))
    linha = np.sin(2 * np.pi * yy / 14.6) * (0.6 + 0.4 * nuvem)
    t = 0.45 * rua + 0.85 * fio + 0.8 * blobs + 0.3 * nuvem + 0.16 * linha
    t -= t.mean()                                    # média 0: a textura não muda a exposição
    return (t / t.std()).astype(np.float32)


class Estilo:
    def __init__(self, forca: float = FORCA, semente: int = 7, w: int = W, h: int = H):
        self.f = float(forca)
        self.w, self.h = w, h
        self.rng = np.random.default_rng(semente)
        # --- cor: 3 tabelas (canal a canal) com curva em S + divisão de tom
        x = np.arange(256, dtype=np.float32) / 255.0
        s = np.clip(0.5 + (x - 0.5) * (1 + (CONTRASTE - 1) * self.f), 0, 1)
        sombra = np.clip(1 - x / 0.45, 0, 1) ** 1.5
        luz = np.clip((x - 0.55) / 0.45, 0, 1) ** 1.5
        base = s * 255
        self.lut = [np.clip(base - SOMBRA_FRIA * self.f * sombra * 0.6 + LUZ_QUENTE * self.f * luz, 0, 255),   # R
                    np.clip(base + 0.5 * LUZ_QUENTE * self.f * luz * 0.4, 0, 255),                          # G
                    np.clip(base + SOMBRA_FRIA * self.f * sombra - LUZ_QUENTE * self.f * luz * 0.6, 0, 255)]  # B
        self.lut = [l.astype(np.uint8) for l in self.lut]
        # --- vinheta (uma por altura de região: a faixa de cima tem a dela)
        self._vin: dict[int, np.ndarray] = {}
        self._vinheta(h)
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        # --- textura fixa (papel + retícula, já na amplitude final) e banco de grão animado (desvio 1)
        a1, a2 = np.deg2rad(90 - RETICULA_ANG), np.deg2rad(-RETICULA_ANG)
        k = 2 * np.pi / RETICULA_PASSO
        reticula = (np.cos(k * (xx * np.cos(a1) + yy * np.sin(a1))) + np.cos(k * (xx * np.cos(a2) + yy * np.sin(a2))))
        self.papel = (self.f * (PAPEL * textura_papel(w, h, semente) + RETICULA * reticula)).astype(np.float32)
        self.banco = []
        for _ in range(BANCO if GRAO > 0 else 0):
            g = cv2.GaussianBlur(self.rng.standard_normal((h + 64, w + 64)).astype(np.float32), (0, 0), GRAO_TAM)
            self.banco.append(g / (g.std() + 1e-6))
        # peso por luminância (luz suave: forte nos meios-tons, fraco no preto e no branco), tabela de 256
        lu = np.arange(256, dtype=np.float32) / 255.0
        self.peso_lut = (0.25 + 0.75 * np.clip(1 - (2 * lu - 1) ** 2, 0, 1) ** 1.5).astype(np.float32)
        self.semente = int(semente)

    def _vinheta(self, hh: int) -> np.ndarray:
        v3 = self._vin.get(hh)
        if v3 is None:
            yy, xx = np.mgrid[0:hh, 0:self.w].astype(np.float32)
            r = np.sqrt(((xx - self.w / 2) / (self.w / 2)) ** 2 + ((yy - hh / 2) / (hh / 2)) ** 2) / np.sqrt(2)
            v = (1.0 - VINHETA * self.f * np.clip(r, 0, 1) ** 2.2).astype(np.float32)
            v3 = self._vin[hh] = cv2.merge([v, v, v])
        return v3

    # ---------------------------------------------------------------- poeira
    @staticmethod
    def _cisco(rng) -> np.ndarray:
        """Mancha irregular pequena (2-7 px), com borda suave."""
        t = int(rng.integers(5, 12))
        m = np.zeros((t, t), np.float32)
        for _ in range(int(rng.integers(1, 4))):
            cx, cy = rng.uniform(t * 0.3, t * 0.7, 2)
            ax, ay = rng.uniform(0.6, t * 0.28, 2)
            cv2.ellipse(m, (int(cx), int(cy)), (max(1, int(ax)), max(1, int(ay))), float(rng.uniform(0, 180)), 0, 360, 1.0, -1)
        return cv2.GaussianBlur(m, (0, 0), 0.6) * float(rng.uniform(0.35, 0.75))

    @staticmethod
    def _fio(rng) -> np.ndarray:
        """Fio de cabelo/arranhão curvo, fino."""
        t = int(rng.integers(30, 70))
        m = np.zeros((t, t), np.float32)
        pts = np.cumsum(rng.normal(0, 3, (6, 2)), axis=0) + t / 2
        cv2.polylines(m, [np.clip(pts, 0, t - 1).astype(np.int32)], False, 1.0, 1, cv2.LINE_AA)
        return m * float(rng.uniform(0.3, 0.55))

    def _nascidos(self, n: int, hh: int) -> list:
        """Ciscos que nascem no quadro n (sorteio fixo por quadro: sai igual em qualquer ordem)."""
        rng = np.random.default_rng((self.semente, max(0, n), 1))
        out = []
        for _ in range(int(rng.poisson(POEIRA_POR_QUADRO * self.f))):
            out.append((int(rng.integers(0, self.w - 12)), int(rng.integers(0, max(1, hh - 12))), self._cisco(rng),
                        int(rng.integers(1, 3))))
        if rng.random() < FIO_CHANCE * self.f:
            out.append((int(rng.integers(0, self.w - 70)), int(rng.integers(0, max(1, hh - 70))), self._fio(rng), 1))
        return out

    def _poeira(self, fr: np.ndarray, n: int) -> None:
        hh = fr.shape[0]
        vivos = self._nascidos(n, hh) + ([c for c in self._nascidos(n - 1, hh) if c[3] >= 2] if n > 0 else [])
        for x, y, m, _ in vivos:
            th, tw = m.shape
            reg = fr[y:y + th, x:x + tw]
            alvo = 225.0 if float(reg.mean()) < 128 else 35.0      # claro no escuro, escuro no claro
            reg += (alvo - reg) * m[:reg.shape[0], :reg.shape[1], None]

    # ---------------------------------------------------------------- quadro
    def aplicar(self, fr: np.ndarray, n: int = 0, area: tuple[int, int] | None = None) -> np.ndarray:
        """fr: RGB uint8 (h, w, 3), n = número do quadro, area = (y0, y1) linhas do B-roll (None = quadro
        todo) -> RGB uint8 com o estilo só nessa região. Função pura de (fr, n, area): roda em paralelo e
        fora de ordem com o mesmo resultado."""
        if self.f <= 0:
            return fr
        y0, y1 = area if area else (0, fr.shape[0])
        if y1 <= y0:
            return fr
        reg, hh = fr[y0:y1], y1 - y0
        rng = np.random.default_rng((self.semente, n, 0))
        # cor: tabelas por canal + saturação
        c = cv2.merge([cv2.LUT(reg[..., k], self.lut[k]) for k in range(3)])
        cinza = cv2.cvtColor(c, cv2.COLOR_RGB2GRAY)
        sat = 1 - (1 - SATURACAO) * self.f
        c = cv2.addWeighted(c, sat, cv2.cvtColor(cinza, cv2.COLOR_GRAY2RGB), 1 - sat, 0)
        f = cv2.multiply(c.astype(np.float32), self._vinheta(hh))
        # papel fixo + grão animado, pesados pela luminância (em 1/4 da resolução: varia devagar)
        lum = cv2.resize(cinza, (self.w // 4, max(1, hh // 4)), interpolation=cv2.INTER_AREA)
        peso = cv2.resize(self.peso_lut[lum], (self.w, hh), interpolation=cv2.INTER_LINEAR)
        papel = self.papel[y0:y1]
        if self.banco:
            dy, dx = int(rng.integers(0, 64)), int(rng.integers(0, 64))
            g = self.banco[int(rng.integers(0, len(self.banco)))][dy + y0:dy + y1, dx:dx + self.w]
            campo = cv2.multiply(cv2.scaleAdd(np.ascontiguousarray(g), GRAO * self.f, papel), peso)
        else:
            campo = cv2.multiply(papel, peso)
        f = cv2.add(f, cv2.merge([campo, campo, campo]))
        self._poeira(f, n)
        out = np.clip(f, 0, 255).astype(np.uint8)
        if y0 == 0 and y1 == fr.shape[0]:
            return out
        res = fr.copy()
        res[y0:y1] = out
        return res


def main() -> None:
    from PIL import Image
    ent, sai = sys.argv[1], sys.argv[2]
    forca = float(sys.argv[3]) if len(sys.argv) > 3 else FORCA
    im = np.asarray(Image.open(ent).convert("RGB"))
    e = Estilo(forca, w=im.shape[1], h=im.shape[0])
    Image.fromarray(e.aplicar(im, 0)).save(sai)


if __name__ == "__main__":
    main()
