# Margens e área segura por formato

Medidas em pixels do quadro final. "Zona coberta" = onde a interface da rede fica por cima do vídeo:
nada importante (texto, logo, botão, número) pode ficar ali. Margem lateral mínima em todos: 80 px
(1080 de largura) — escalar proporcionalmente em outras resoluções.

| Formato | Quadro | Zonas cobertas |
| --- | --- | --- |
| Reels / Stories / TikTok / Shorts 9:16 | 1080×1920 | gabarito do usuário (21/10/2026): topo 0–250; base 1500–1920 (nome, legenda, áudio); esquerda 0–70; direita 55 px até y 1110 e x ≥ 887 de y 1110 a 1500 (botões) |
| Feed 4:5 | 1080×1350 | sem interface por cima; margem 80 em volta |
| Feed 1:1 | 1080×1080 | sem interface por cima; margem 80 em volta |
| YouTube / site 16:9 | 1920×1080 | base 960–1080 (barra do player) quando for para YouTube; margem 96 |

O `scripts/area_segura.py --formato 9x16` pinta essas zonas em vermelho e as margens em amarelo sobre os
snapshots e monta uma folha para conferir.

Texto grande que não cabe: diminuir ou quebrar linha (`max-width`), nunca deixar cortar. Elemento
decorativo (etiqueta, partícula) pode cruzar a zona coberta; informação não.
