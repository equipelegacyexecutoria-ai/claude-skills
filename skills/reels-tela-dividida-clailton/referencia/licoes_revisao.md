# Lições das revisões (a skill aprende com cada nota)

Regra do usuário (16/11/2026): "a skill tem que se auto aprimorar de acordo com as alterações que vou pedindo, para
a cada edição ficar mais completa e com cada vez menos revisões". **Leia este arquivo inteiro antes de escrever o
plano.txt** e confira o vídeo contra ele antes de entregar. Depois de cada rodada de correções, acrescente aqui o que
virou regra (formato abaixo). Lição que já virou código (script/constante) fica registrada com o nome do ajuste.

Formato: `- **Regra curta** (vídeo, data, nota original resumida) → o que fazer.`

## Zoom (Clailton)

- **Zoom entre os cortes SEMPRE, no vídeo inteiro** (Fim do Mundo, 16/11/2026; 6 notas "tem que estar com zoom",
  "zoom entre cortes que nem já fizemos") → nas emendas o Clailton alterna aberto/fechado. Código: `ZOOM_SEM_FOLGA`
  (td_comum.py): com bruto fechado (careca no topo do quadro) o fechado usa 1,25x e corta o alto da cabeça em vez de
  desligar o zoom. Antes do render confira no `timeline.txt`: `fechado_do_clailton` perto de 0,4–0,5 e
  `trocas_de_zoom` > 0. Se vier 0%, o zoom foi desligado: não entregue assim.
- Frases de fecho, pergunta ao espectador, provocação e a frase final ("é passar a vida inteira...") pedem fechado:
  ponha `FECHADO @a-b` nelas se o automático não pegou.
- Imagem tirada por nota ("retirar e deixar só o Clailton") → no lugar dela, `FECHADO` naquele trecho.
- **Zoom não fica preso por várias frases** ("após esse corte volte o enquadramento para o original") → o fechado
  dura até a emenda seguinte; `FECHADO @a-b` só na frase curta, e `ABERTO @a-b` onde ele pediu o original.

## Imagem certa para a fala

- **Abertura com notícia = recorte de jornal animado** (Fim do Mundo, nota em 0:00: "recorte de uma notícia e uma
  animação destacando os textos importantes") → manchete REAL (texto e fonte) num papel, marca-texto amarelo passando
  nas palavras-chave no tempo da fala. Modelo: `_trabalho/Reels_Clailton_TD_Fim_Do_Mundo/recorte_noticia.py`
  (gera mp4 1080x768 para `TOPO @0 arquivo "..."`). Site com anúncio por cima da manchete: monte o recorte em vez do print.
- **Cena que o espectador reconhece na hora vale mais que vídeo genérico.** Quando a fala cita algo (Simpsons,
  alarme falso, reserva de dinheiro), procure A CENA exata/icônica: alarme falso → "O menino que gritava lobo";
  reserva financeira → Breaking Bad, Walter diante da pilha de dinheiro no depósito; teorias malucas → o "cara dos
  aliens" (Ancient Aliens); ler/estudar → Matilda com pilha de livros; dinheiro na mão → Jordan esticando a nota de
  dólar (WOLF-03 ~85 s). Pergunte "que cena do consciente coletivo é essa?" antes de aceitar um vídeo de banco.
- **Imagem sem relação clara com a frase sai** (notas: "nada a ver com nada", "não entendi essa imagem",
  "entrou no momento errado e sem contexto") → se você não consegue dizer em 3 palavras por que a imagem está ali,
  deixe o Clailton (com zoom).
- **Sequência de exemplos = uma imagem por exemplo** (nota "tem gente passando horas... usar mais imagens") → lista
  falada (podcasts, vídeos, teorias / correr, academia, comer bem) ganha uma cena por item.
- **Saúde = gente se cuidando** (nota "galerinha correndo, se exercitando, comendo bem"), não hospital.
- **Não use imagem que mostra o contrário ou o problema quando a fala é sobre a solução.**

## Enquadramento do B-roll

- **O momento icônico da cena tem que estar no quadro e no tempo** (Jordan: "corta exatamente no momento mais
  icônico, quando ele mostra a nota de dólar") → escolha `t=` para a ação principal cair dentro do trecho usado e
  prefira `cheia` com o assunto centrado; não entre na dividida antes da hora.
- **Cena larga (navio, multidão) em `dividida`**, com o trecho em que a ação aparece inteira (navio vindo na praia).
- **Notícia/print em `dividida` corta o texto** → TV/celular com alerta: use o close do celular em tela cheia.
- Nota "desenquadrado" = recorte pegou parede/canto/meio de rosto. Olhe a folha de candidatos pensando no 9:16 final.
- **ENQUADRAMENTO É O ERRO Nº 1 (v2 do Fim do Mundo: 9 notas "desenquadrado", "ficou uma merda")** → NÃO confie
  no reenquadramento automático nem em `foco=` no escuro (o `foco=0.2` estragou uma cena que estava boa na v1).
  Para toda cena que não é vertical nativa: monte a folha do QUADRO INTEIRO com régua (`scripts/quadros_inteiros.py`),
  decida o centro x do assunto e o segundo exato da ação, e corte com `scripts/recorte_manual.py` (sai já 1080x1920
  ou 1080x768; no plano vira `arquivo "..."`). Regra de largura: na `cheia` cabem só ~32% da largura de um 16:9 —
  assunto mais largo que isso (celular + mão + texto, duas pessoas, mesa com dinheiro, carteira nas duas mãos,
  Forrest + corredores) vai em `dividida` (cabem ~79%). Fonte abaixo de 720p em cheia fica borrada: use dividida.
  Cena com corte no meio (troca de plano) → encurte a linha do plano para caber no plano bom.
- **O momento icônico tem que cair DENTRO do trecho** (Jordan: 2 versões sem mostrar a nota) → olhe o quadro em
  10/50/90% do trecho usado; se a ação está depois, mude o início.
- **Cena que já foi aprovada numa versão não muda na seguinte** ("na v1 estava bem enquadrada, agora você cagou") →
  só mexa no que tem nota.
- **Simpsons = família/Homer reconhecível**, não a usina ("não fez sentido"; "nenhuma imagem com o Homer?").

## Corte e legenda

- **Pausa antes de frase que começa com silêncio** ("depois de melhorar suas vidas demorou a cortar") → meça a onda e
  use `INICIO n i@t` com t no começo real da voz; `FIM n i@t` no fim real da palavra anterior.
- **Estalo/respiro no começo do corte** ("o começo desse corte ficou estranho") → `INICIO n i@t` depois do estalo.
- **Pontuação errada na legenda** ("Rotina. Não foi uma pergunta") → confira `?` nas telas que não são pergunta.

## Som e final

- **TD sai COM música já na v1** (16/11/2026: "quero que você já coloque a música") → trilha da biblioteca Spotclai,
  `C:/Render/_trabalho/_trilhas/escolher_ini.py` para a virada cair no "mas" forte, `trilha.py` (voz até -0,1 dBTP,
  música 10 dB abaixo, continua na CTA).
- **Trilha de TENSÃO/MISTÉRIO/SUSPENSE e DUAS músicas** (Fim do Mundo v2: "a música não casou bem") → 1ª metade com
  uma faixa tensa (ex.: SoLaTiDo - Suspenseful and Tense Orchestra, Bravokod) até a virada que o usuário marcar,
  transição SONORA logo depois da palavra da virada (whoosh-cinematic do media-use a partir do pico, 2,0 s), e a 2ª
  faixa segue até o fim. Monte um único wav (cada parte em -20 LUFS, `amix normalize=0`) e passe para `trilha.py`
  com início 0; o `trocar_cta.py --musica` usa o mesmo wav. Modelo: `_trabalho/Reels_Clailton_TD_Fim_Do_Mundo/trilha_duas.wav`.
- **CTA antiga (digitada) não vale mais** ("aqui está a cta antiga") → depois da trilha, troque pela CTA "me segue"
  (`reels-novela-clailton/scripts/trocar_cta.py`), como nas novelas.
