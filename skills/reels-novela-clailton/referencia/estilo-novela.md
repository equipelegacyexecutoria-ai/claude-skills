# Estilo NOVELA (Clailton) — decupagem da referência

Referência: reel "Você quer ficar rico? Então torna-te um PHD" (720×1280, 62 s, Instagram),
analisada quadro a quadro em 2026-09-26. Confirmado por mais duas edições da equipe no mesmo
estilo ("Parar hábito V2", "Soltar gases"). Todos os números abaixo estão em 1080×1920.
Imagem das 38 telas: `telas-referencia.jpg`. CTA: `cta-referencia.png`.

## 1. Quadro

| Item | Valor |
| --- | --- |
| Tela | 1080×1920, 29,97 fps |
| Faixa de imagem | **1080×864 (5:4)**, centrada: y 528 → 1392. Barras pretas puras em cima e embaixo |
| Enquadramento | **fixo** o vídeo todo (sem punch-in, sem zoom entre cortes) |
| Rosto | centro a ~54% da largura (levemente à direita). Na referência o rosto tinha ~23% da largura e ficava a ~32% da altura, mas isso **não é alvo**: a faixa usa a altura cheia do bruto e nunca corta em cima nem embaixo (usuário, 30/09/2026) |
| Cor | sem color grading (a equipe entrega com a cor do bruto) |
| Cortes | secos, entre frases; a imagem "pula" (jump cut) e ninguém disfarça |

## 2. Ritmo do corte

- Fala corrida: entre uma frase e outra ficam só **0,10–0,26 s** de silêncio.
- Pausas internas acima de 0,30 s são encurtadas para ~0,20 s; tomadas repetidas, falsos
  começos e comentários ("vamos lá de novo", "calma", "muito bem") saem.
- **Nada de pausa dramática**: o usuário reprovou 0,45 s de silêncio depois de "Talvez seja,"
  ("um tempo sem nada, estranho"). Nenhum silêncio interno acima de ~0,3 s.
- **Início e fim de trecho colados na voz**: o usuário reprovou "demorou para ele começar a
  falar" (a respiração depois da frase anterior ficava no corte). Corte a ~0,05 s da voz dos
  dois lados; respiração/expiração entre frases sai.
- Depois da última palavra: **~0,45 s** de imagem e corte seco para a CTA.

## 3. Legenda

**Fonte:** SF Pro Text Black (`fonts/SF-Pro-Text-Black.otf`, PostScript `SFProText-Black`),
caixa-alta, branca pura. Kerning da fonte ligado + espaçamento apertado:

| Linha | Tamanho | Maiúscula | Espaçamento |
| --- | --- | --- | --- |
| Normal | fs 75 | ~44 px | −0,075 × fs por letra |
| Destaque d1 | largura-alvo ~640 px | 60–90 px | −0,10 × fs |
| Destaque d2 (forte) | largura-alvo ~780 px | 95–120 px | −0,10 × fs |
| Destaque d3 (impacto) | palavra sozinha, ~720 px | 150–205 px | −0,10 × fs |
| Âncora (P/PH/PHD) | fixa | ~100 px | −0,10 × fs |

**Empilhamento:** linhas coladas — **11 px** entre a base de uma e o topo da maiúscula da
seguinte. O vão só abre onde um acento da linha de baixo (ou a cedilha/rabo do Q da de cima)
bateria numa letra da outra linha: aí abre o mínimo para o acento respirar (senão "HÁBITO"
embaixo de "TALVEZ O" perde o acento dentro do L). Calculado letra a letra no script.

**Sombra:** medido pixel a pixel no miolo das letras: a linha de CIMA é branco chapado
(252–254); a de BAIXO escurece ~20–25% no topo e volta ao branco na base, e só onde há letra
da linha de cima (o lado livre fica branco). É o halo difuso da linha de cima caindo sobre a
de baixo — não é degradê no preenchimento. Padrão do usuário (sombra v3, obrigatório):
halo difuso (0,3) bord 10 blur 22 ~45% + contato (1,4) bord 2 blur 4 ~72%. Sem contorno,
sem tarja. Camadas: o CONTATO de todas as linhas fica embaixo de todos os textos (ele é forte
e apagaria acentos); só o HALO de cada linha fica por cima da linha de baixo.

**Posição:** centro vertical do bloco em **y ≈ 1120** (~69% da faixa: peito, abaixo do queixo).
Horizontal, por bloco:
- `centro` — cada linha centrada (linhas únicas, frases de efeito);
- `esquerda` — linhas alinhadas pela tinta em x ≈ 165 (texto do lado esquerdo do corpo);
- `escada` — cada linha ~100 px mais à direita que a anterior (progressão);
- `direita` — a última linha alinhada pela direita com a de cima (fecho).
Margens: tinta entre x 95 e 985.

**Entrada de cada linha (medida quadro a quadro):** aparece já opaca, desfocada (blur ~4,
~6 nas gigantes) e ~23 px acima; desce e fica nítida em ~8 quadros (curva: segura 1 quadro,
cai rápido, assenta). Sem escala, sem movimento lateral.

**Ritmo do texto:** cada linha NORMAL entra inteira quando a primeira palavra dela é falada.
O DESTAQUE entra sozinho, maior, na hora exata da palavra. O bloco fica na tela até o
próximo começar — troca = **corte seco**, sem animação de saída.

**Tempo:** a tela troca no ataque real da palavra (ver `ATRASO_FALA_CORRIDA` no script).

**Âncora:** em enumerações (acrônimo, "3 coisas"), um título fixo no alto à esquerda
(x ≈ 97, topo y ≈ 852) que cresce ("P" → "PH" → "PHD") enquanto as telas de baixo trocam.
As linhas sob a âncora começam logo abaixo dela, alinhadas à esquerda ou em escada.

## 4. Texto da legenda (não é literal)

- Português escrito: "tô" → ESTOU, "pra" → PARA, "tá" → ESTÁ, "cê" → VOCÊ, "três" → 3.
- Tira muleta e sujeito redundante no começo ("Eu não tô falando" → NÃO ESTOU FALANDO).
- Pode ajustar artigo para a frase fechar ("no tipo de pessoa" → UM TIPO DE PESSOA;
  "PHD que eu estou falando" → O PHD QUE ESTOU FALANDO). Nunca inventa conteúdo.
- Pontuação: só "?" em pergunta e "..." em suspense (SÓ QUE...). Sem vírgula/ponto.
- Linha normal: 1–4 palavras, até ~18 caracteres. Destaque: 1–3 palavras (a ideia-chave).
- Bloco = uma unidade de sentido de 1–3 linhas; ~1 tela a cada 1,5 s; ~80% das telas têm destaque.

## 5. As 38 telas da referência (fala → legenda)

`[d1]` `[d2]` `[d3]` = destaque; demais linhas normais. Layout entre parênteses.

| # | Fala | Legenda |
| --- | --- | --- |
| 1 | Você quer ficar rico? | VOCÊ QUER / FICAR RICO? [d1] (esquerda) |
| 2 | Torne-se um PHD. | TORNE-SE UM / PHD [d2] (esquerda) |
| 3 | Eu não tô falando aqui de diploma. | NÃO ESTOU / FALANDO AQUI / DE DIPLOMA (esquerda) |
| 4 | PHD que eu estou falando | O PHD QUE ESTOU / FALANDO [d1] (centro) |
| 5 | precisa de três coisas importantes. | PRECISA DE / 3 COISAS [d1] / IMPORTANTES (esquerda) |
| 6 | Primeiro, | PRIMEIRO [d1] (centro) |
| 7 | o P de pressão suficiente | âncora P + DE PRESSÃO / SUFICIENTE |
| 8 | pra você não se acomodar. | (P) PARA VOCÊ / NÃO SE ACOMODAR |
| 9 | O H de honestidade suficiente | âncora PH + DE / HONESTIDADE [d1] / SUFICIENTE (escada) |
| 10 | pra você não se perder | (PH) PARA VOCÊ / NÃO SE PERDER [d1] |
| 11 | e D de determinação suficiente | âncora PHD + DE / DETERMINAÇÃO [d1] / SUFICIENTE (escada) |
| 12 | pra você continuar | (PHD) PARA VOCÊ / CONTINUAR [d1] |
| 13 | quando a coisa ficar difícil. | QUANDO / A COISA FICAR / DIFÍCIL [d1] (escada) |
| 14 | Eu tô falando de você se tornar | ESTOU FALANDO / DE VOCÊ / SE TORNAR (escada) |
| 15 | no tipo de pessoa | UM TIPO DE PESSOA (centro) |
| 16 | que ainda tem alguma coisa para provar. | QUE AINDA TEM / ALGUMA COISA [d1] / PARA PROVAR (direita) |
| 17 | Que quer mudar de vida, | QUE QUER / MUDAR DE VIDA [d1] (esquerda) |
| 18 | que quer crescer, | QUE QUER CRESCER (centro) |
| 19 | que quer conquistar. | QUE QUER / CONQUISTAR [d1] (esquerda) |
| 20 | Que ainda não chegou onde quer chegar. | QUE AINDA / NÃO CHEGOU [d1] / ONDE QUER CHEGAR (escada) |
| 21 | Porque existe uma vantagem | PORQUE EXISTE UMA / VANTAGEM [d2] (centro) |
| 22 | enorme em ainda não ter vencido | ENORME EM / AINDA NÃO / TER VENCIDO (escada) |
| 23 | tudo. | TUDO [d3] (centro) |
| 24 | Você ainda tem fome. | VOCÊ AINDA TEM / FOME [d2] (centro) |
| 25 | Você tem um motivo pra acordar todos os dias | VOCÊ TEM UM MOTIVO / PARA ACORDAR [d1] / TODOS OS DIAS (escada) |
| 26 | e fazer a coisa acontecer. | E FAZER A COISA / ACONTECER [d1] (centro) |
| 27 | Só que | SÓ QUE... [d1] (centro) |
| 28 | fome sem honestidade | FOME [d1] / SEM HONESTIDADE (esquerda) |
| 29 | vira atalho. | VIRA ATALHO [d1] (centro) |
| 30 | Pressão sem determinação | PRESSÃO [d2] / SEM DETERMINAÇÃO (centro) |
| 31 | vira desculpa. | VIRA DESCULPA [d1] (centro) |
| 32 | Porque no fim, | PORQUE NO FIM [d1] (centro) |
| 33 | você não precisa parecer bem sucedido | VOCÊ NÃO PRECISA / PARECER BEM / SUCEDIDO [d1] (escada) |
| 34 | antes de vencer. | ANTES DE VENCER (centro) |
| 35 | Você precisa apenas se tornar | VOCÊ PRECISA / APENAS SE TORNAR [d1] (centro) |
| 36 | o tipo de pessoa | O TIPO / DE PESSOA [d1] (esquerda) |
| 37 | que não para | QUE NÃO PARA (centro) |
| 38 | até vencer. Um PHD. | ATÉ VENCER [d1] / UM PHD [d1] (escada) |

Distribuição: 11 telas de 1 linha, 15 de 2, 12 de 3. Layouts ~40% centro, ~30% esquerda,
~25% escada, ~5% direita — nunca o mesmo layout mais de 3 vezes seguidas.

## 6. CTA final (igual em todos os reels novela)

- Corte seco para **tela preta cheia** (sem faixa), 2,9 s até o fim do vídeo.
- "ME SIGA PARA MAIS / CONTEÚDOS COMO ESTE", 2 linhas centradas, branco, peso Bold,
  espaçamento normal. Na referência é SF Pro Display Bold; aqui **Inter 28pt ExtraBold**
  (casou em largura, altura e peso), maiúscula ~55 px, topos das linhas em y 811 e 902.
- Máquina de escrever: começa 1 quadro depois do corte, ~47 letras/s (tudo em ~0,78 s),
  cada letra acende em ~2 quadros; depois fica parada até o fim.
- Sem música/voz (a música entra depois, na mão do usuário).

## 7. Entrega

H.264 High, CRF 10, preset slow, yuv420p BT.709, 1080×1920, 29,97 fps; AAC 320k 48 kHz;
voz em −14 LUFS / −1 dBTP; recorte feito direto do 4K (só redução, nunca ampliação);
uma única compressão com perda (intermediários sem perda).
