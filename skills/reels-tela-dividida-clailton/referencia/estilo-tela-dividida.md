# Estilo TELA DIVIDIDA (Clailton): o que foi medido

Análise quadro a quadro (2026-09-27) dos 6 reels da equipe na pasta `Reels Tela Dividida`.
Medido com transcrição palavra a palavra (Whisper), detecção de corte por diferença de quadro,
rosto (YuNet) + reconhecimento do Clailton (SFace), zoom real por SIFT+RANSAC e medição de pixel
da legenda. Scripts da análise: `_trabalho/_analise/` do projeto. Tudo em 1080×1920.

| Reel | Resultado | Duração | Clailton | B-roll | Topo (dividida) |
|---|---|---|---|---|---|
| Não confie no ser humano (#121) | 1,81 mi · 52x | 161 s | 64% | 34% | 2% (só a abertura) |
| Me mostra teu quarto (#133) | 561 mil · 16x | 95 s | 61% | 5% | 34% (filme no topo) |
| Fórmula para conquistar (#118) | 316 mil · 9x | 167 s | 80% | 15% | 5% |
| História Duty Free (Chuck Feeney) | recente | 90 s | 51% | 45% | 5% |
| STF (juiz de futebol) | 0,84x | 75 s | 57% | 35% | 9% |
| 6 tipos de pessoas (#128) | 15 mil · 0,43x | 141 s | 37% | 58% | 5% |

Leitura: o melhor reel tem ~2/3 de Clailton e ~1/3 de imagem. O pior tem imagem demais (58%,
26 trocas/min) e legenda diferente (condensada). Padrão da skill = o do "Não confie" + o do
"Me mostra teu quarto".

## 1. Os 4 layouts de quadro

| Layout | O que é | Geometria medida |
|---|---|---|
| **DIVIDIDA (topo)** | imagem em cima, Clailton embaixo | emenda entre 32% e 50% da altura (mediana ~40%, y≈768). A imagem cobre y 0→emenda (corte "cover"). O Clailton é o MESMO plano aberto da tela cheia, só descido: rosto a ~62% da altura (y≈1190), mesmo tamanho (rosto ≈ 0,31 da largura) |
| **CLAILTON tela cheia** | só ele | plano aberto: rosto ≈ **0,30** da largura, centro do rosto em x≈0,50 e **y≈0,30**. Fechado: rosto ≈ **0,45–0,50** (≈1,5× o aberto), y≈0,33 |
| **B-ROLL tela cheia** | foto, trecho de filme, ilustração | corte "cover" 9:16 no assunto (rosto/objeto) |
| **CARTÃO** | imagem menor sobre fundo claro | print de notícia, WhatsApp, foto de arquivo, logo, cartaz: imagem ~80–90% da largura, centrada, fundo branco/cinza claro em degradê; parada (escala 1,00) |

## 2. Clailton

- **Parado**: nos planos do Clailton a escala medida é 1,000 do começo ao fim (sem zoom lento).
- **Dois enquadramentos** que se alternam por **corte seco**: aberto (≈2/3 dos planos) e fechado
  (≈1/3). Fechado = punch-in de ~1,45–1,6× sobre o aberto.
- O fechado entra em **frase curta de fecho** (1–6 palavras, 0,8–2,6 s): o fim de uma ideia, a
  virada, o imperativo ("Agora você pode gritar." · "a tua." · "e passa a ser sobre você." ·
  "registre" · "saiba como provar" · "daqui a cinco anos."). Nunca dois fechados seguidos.
- A troca aberto↔fechado também **esconde a emenda de tomadas** (jump cut).
- Plano do Clailton dura mediana 1,3–2,5 s entre cortes.
- Gravação: 4K com a **câmera deitada** (o bruto `ES_Parabéns` vem 3840×2160 com ele de lado, sem
  metadado de rotação) → girar 90° e recortar 9:16. Terno azul, escritório desfocado, às vezes
  camiseta preta ou selfie (STF).

## 3. Imagem (B-roll): quando, quanto, como

**Tempo:** todo corte cai no **início de uma palavra** (corte − início da palavra: mediana −0,02 s;
80% entre −0,10 e +0,10 s). A imagem entra na 1ª palavra da frase que ela ilustra e sai na 1ª
palavra do plano seguinte. B-roll dura mediana **1,2–1,7 s** (0,5 a 4 s); em história, 2 a 6
imagens seguidas, uma por ação/frase curta.

**Quanto:** 25–40% do tempo em imagem (14 trocas/min no melhor). Imagem concentrada no gancho, na
história/caso e nos exemplos; o Clailton domina a ponte, a lição e o fecho (último terço).

**Movimento:**
- **Foto/ilustração parada: zoom-out lento e constante, ~5%/s** (medido 4,2–6,5%/s), centrado.
  Ex.: 2 s de imagem = escala 1,10 → 1,00.
- **Trecho de filme/vídeo: sem zoom** (o movimento é o do próprio trecho), sem áudio.
- Cartão: parado.

**Correlação fala × imagem (as regras que a equipe segue):**

| Na fala | Imagem | Exemplos medidos |
|---|---|---|
| Nome de pessoa, marca, lugar, produto | foto/vídeo **daquilo**, entrando **na palavra do nome** | "Thomas Edison" → retrato P&B · "James Dyson" → Dyson com o aspirador · "WD-40" → a lata · "Canva" → logo · "Chuck Feeney" → foto + nome em amarelo |
| Narração de história inventada (ações) | **uma ilustração por ação**, mesmo estilo e mesmos personagens | hotel: homem entra · mulher corre · fecha a porta · senta na cama · bloco de notas · arranca a folha · dobra · bolso (18 esboços a lápis, IA) |
| Comportamento humano abstrato (traição, lealdade, sociedade, briga, ingenuidade) | **cena icônica de filme/série** que dramatiza a ideia | "quem hoje é seu amigo" → Breaking Bad (abraço) · "jura lealdade" → O Poderoso Chefão II (beijo de Michael em Fredo) · "existe sociedade" → O Lobo de Wall Street · "um casamento termina" → História de um Casamento · "disputa por dinheiro" → La Casa de Papel · "só não seja ingênuo" → Better Call Saul |
| Filme citado pelo nome | trechos **do filme**, no topo enquanto ele comenta | "Sem Limites": pílula, arruma o apartamento, bagunça |
| Lista de coisas concretas | 1 imagem por item ou 1 trecho que mostre tudo | "mansões, carros, aviões" → mansão, jatinho · "roupa jogada, papel acumulado, mesa cheia" → apartamento bagunçado |
| Metáfora estendida | o objeto da metáfora, repetido e variando | xadrez: peão, cavalo, bispo, rainha, rei (+ personagens de série) |
| Notícia, fato datado, conversa | **print** em cartão (manchete, TV, WhatsApp, jornal estrangeiro) | GloboNews, Washington Post, Le Monde, WhatsApp |
| Número/dado | **não é imagem**: número grande na tela sobre o Clailton | 3.000 · 0,07% · 5.127 · 2,5% · MENOS DE 1% |
| "você", conselho, lição, fecho | **Clailton** (sem imagem) | ponte, aplicação, virada |

**Fontes (o que a equipe usa):** trechos de filmes e séries famosos (YouTube/TikTok), fotos reais
de pessoas e marcas (busca de imagem), cenas genéricas (xadrez, futebol, mansão, jatinho),
ilustração gerada por IA para história inventada (estilo único do começo ao fim: esboço a lápis
em fundo branco no "Não confie"), prints de notícia. Imagem "orgânica", não cara de banco.

## 4. Legenda

**Corpo (tela cheia e imagem):**
- 1 linha, **1–4 palavras** (mediana 2–3, até ~20 letras), caixa-alta, troca **seca** no início
  da 1ª palavra da tela seguinte (sem animação de entrada, sem fade); ~0,7 s por tela.
- Fonte: sans pesada, espaçamento bem apertado (casou com **SF Pro Text Black**, maiúscula **34 px**,
  espaçamento −0,085 em). Branca. Sombra: padrão v3 do usuário (halo + contato).
- Posição: centro da linha em **y≈1175 (61%)**, centrada. Mesma posição sobre imagem e sobre o
  Clailton (fica no peito dele no plano aberto).
- Texto: português escrito (tô→ESTOU, pra→PARA), sem ponto e vírgula; mantém "?" e aspas de fala.
  Número em algarismo (R$20.000, 5.127, 0,07%). **Palavra sensível censurada**: EST*PRO.

**Abertura (tela dividida, 0 → 3–8 s):** a própria legenda vira **tarja**: caixa **preta**
colada embaixo da emenda, texto branco (maiúscula ~52 px), folga ~22 px, largura do texto, centrada
("NÃO CONFIE" → "NO SER HUMANO" → "VOCÊ VAI QUEBRAR"). Variações vistas: texto grande branco com
sombra sem caixa (Quarto); **etiqueta fixa vermelha** (#C30000) de 2 linhas com a promessa + legenda
pequena embaixo (Fórmula).

**Destaques (opcionais, vistos no Fórmula/6 tipos/Duty):** número gigante (maiúscula ~135 px, y≈50%);
nome da pessoa em amarelo grande sobre a foto; data de morte com cruz; ícone de "salvar" no
"Já salva esse vídeo". O "Não confie" (o melhor) não usa nenhum: tudo na legenda pequena.

## 5. Transições

- **Corte seco** em tudo: imagem, retorno ao Clailton, aberto↔fechado, troca de legenda.
- **Saída da abertura** (tela dividida → tela cheia): efeito de ~0,2 s em 5 de 6 reels:
  **flash de exposição** (2–3 quadros +60–75% de brilho, corte, 1 quadro +75%, 1–2 quadros −65%,
  normal) ou **zoom com desfoque radial** (Fórmula, STF).

## 6. Ritmo, áudio e final

- Fala: 2,3–3,2 palavras/s; pausas mediana 0,16 s, quase nada acima de 0,3 s; a fala começa no
  quadro 0. (Igual à novela: o corte do `montar_corte.py` serve sem mudança.)
- Música de fundo baixa (~12 dB abaixo da voz) nos finalizados: entra depois, na mão do usuário
  (como na novela). Voz −14 LUFS.
- **CTA** igual à da novela (tela preta, "ME SIGA PARA MAIS / CONTEÚDOS COMO ESTE" digitado),
  ~2,5–2,9 s, com **clique de digitação** no "Não confie". Reel de salvamento (Fórmula) e o STF
  terminam sem CTA.

## 7. "Não confie no ser humano": o mapa fala × imagem (exemplo-ouro)

| Tempo | Fala | Tela |
|---|---|---|
| 0,0–2,9 | Não confie no ser humano, você vai quebrar a cara. | DIVIDIDA: ilustração de dois amigos se abraçando com facas nas costas → dois homens de máscara apertando as mãos; tarja preta NÃO CONFIE / NO SER HUMANO / VOCÊ VAI QUEBRAR / A CARA; flash |
| 2,9–6,6 | E antes que você me cancele por falar isso, / deixa eu te contar uma história. | Clailton aberto / **fechado** |
| 6,6–9,2 | Um homem muito rico / entra em um hotel cinco estrelas. | esboço: homem de terno andando / entrando no saguão |
| 9,2–11,6 | Quando ele abre a porta, uma mulher entra | Clailton aberto |
| 11,6–15,0 | correndo atrás dele, / fecha a porta, / senta na cama e / diz: | esboço por ação (4 imagens, 0,5–1,1 s) |
| 15,0–20,9 | "Você tem que me pagar 20 mil reais / ou eu vou te acusar de estupro." E ainda completa: | aberto / **fechado** / aberto |
| 20,9–25,1 | "Não tem câmera aqui dentro, / vai ser a minha palavra contra / a tua." | esboço da mulher / aberto / **fechado** |
| 25,1–29,1 | O homem fica em silêncio, não discute, / só pega um bloco de / notas e escreve: | esboço (3) |
| 29,1–34,1 | "Sou surdo e mudo..." | aberto |
| 34,1–36,7 | Ela então pega o bloco de notas / e coloca no papel: | esboço (2) |
| 40,4–44,9 | Ele lê, / arranca a / folha, dobra, / coloca no bolso, / olha para ela e diz: | esboço (5, 0,6–1,3 s) |
| 44,9–59,3 | "Agora você pode gritar." ... sobre você. | **fechado** / aberto / aberto / **fechado** / aberto / **fechado** |
| 63,6–66,2 | deve passar a vida inteira desconfiando das pessoas. | Barry (Bill Hader desconfiado) |
| 73,1–81,4 | As pessoas mudam. Quem hoje é seu amigo, amanhã pode virar seu adversário. Quem hoje jura lealdade, amanhã pode contar uma versão... | Barry · Breaking Bad (abraço) · cena escura (queda) · O Poderoso Chefão II (beijo) · O Poderoso Chefão (festa) |
| 88,4–93,0 | Hoje existe amizade, / existe sociedade, / está todo mundo de acordo. | O Lobo de Wall Street (3 trechos) |
| 98,6–102,9 | Uma amizade acaba, / um casamento termina, / um sócio vira adversário, | Suits · História de um Casamento · Breaking Bad (pilha de dinheiro) |
| 105,9–107,7 | disputa por dinheiro. | La Casa de Papel |
| 111,8–114,8 | importa o que você consegue provar. | tribunal (criança diante dos juízes) |
| 117–125 | registre / emprestou dinheiro / saiba como provar / ... / faça um bom contrato | **fechado**/aberto/**fechado**/B-roll/**fechado** |
| 120,5–123,7 | abrir uma sociedade até com seu melhor amigo? | Breaking Bad (a "sociedade" no deserto) |
| 134,2–140,9 | Documentar não é desconfiar... à memória, ao caráter ou à versão | escritório (Better Call Saul) · mesa escura · Kim Wexler |
| 147,2–148,8 | Só não seja ingênuo, | Saul Goodman (close) |
| 148,8–158,8 | fecho | Clailton aberto até o fim |
| 158,8–161,6 | — | CTA preta digitada |
