# Preferências pessoais (valem em qualquer projeto)

## Legendas queimadas em vídeo: sempre com sombra

Em **qualquer** edição de vídeo com legenda (cortes, reels, anúncios, qualquer ferramenta:
ASS/libass, Pillow, After Effects, CapCut etc.), a legenda leva sombra para não se misturar
com o fundo. O usuário já reprovou legenda que sumia em fundo claro (blusa branca, parede clara).

Padrão aprovado — "sombra v3", duas camadas discretas, sem contorno duro e sem tarja:

| Camada | Deslocamento | Espessura | Desfoque | Opacidade |
| --- | --- | --- | --- | --- |
| Halo difuso (atrás) | x 0, y 3 | borda 10 | 22 | ~45% preto (ASS `\alpha&H8C&`) |
| Sombra de contato | x 1, y 4 | borda 2 | 4 | ~72% preto (ASS `\alpha&H48&`) |

- Valores para 1080×1920; em outra resolução, escalar proporcionalmente.
- Antes de gerar em lote, testar num trecho com o **fundo mais claro** do material e mostrar para aprovação.
- Detalhes, scripts e o restante do padrão de legenda: skill `cortes-podcast-instagram`
  (`C:\Users\NOT - LIVE\.claude\skills\cortes-podcast-instagram`).
