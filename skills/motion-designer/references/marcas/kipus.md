# Kipus (gestão comercial para distribuidoras de alumínio)

Projeto no PC de render: `Desktop/RENDER/Kipus Motions` (kit em `_shared`, ferramentas em `_tools`, finais em `_entregas`).

## Motions para tela dividida (série "QUEM USA", nov/2026)

O editor coloca o motion ao lado do vídeo, em tela dividida, e às vezes amplia.
- **Formato 1:1** (1080×1080), elementos 2D ilustrados (personagens, ícones, cartões), só a paleta do Kipus:
  sem fundo da marca e sem logo.
- **Área de respiro** (regra do usuário, 27/11/2026): nada fora de x 150–930 e y 150–850; o editor põe texto
  por cima nas bordas. Conferir com `sh _tools/rev_q.sh <pasta> "t1,t2"` (máscara amarela em `_ref/mask-<pasta>.jpg`).
- **Transição entre cenas animada** (mesma regra): sem desfoque e sem dissolver; o fim de uma cena começa a
  outra. Use `_shared/kq.js`: `KT.push` (a cena nova empurra a antiga), `KT.disc` (um círculo da cena antiga
  cresce, cobre a tela e encolhe virando um círculo da nova) ou um objeto que continua de uma cena para a outra.
- **CTAs:** entre a 1ª CTA e a 2ª versão (trecho repetido + CTA da bio), **corte seco**, sem animação
  (`KT.cut`). O trecho repetido é cópia da cena (`KT.clone`) animada de novo no novo tempo.
- Nome do arquivo final = título do vídeo, com "IG-FB" no lugar de "IG/FB".
- Modelos: `K23-duvida-1x1`, `K24-perfil-1x1`, `K25-gestor-1x1`.
