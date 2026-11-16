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

## Corte e legenda

- **Pausa antes de frase que começa com silêncio** ("depois de melhorar suas vidas demorou a cortar") → meça a onda e
  use `INICIO n i@t` com t no começo real da voz; `FIM n i@t` no fim real da palavra anterior.
- **Estalo/respiro no começo do corte** ("o começo desse corte ficou estranho") → `INICIO n i@t` depois do estalo.
- **Pontuação errada na legenda** ("Rotina. Não foi uma pergunta") → confira `?` nas telas que não são pergunta.

## Som e final

- **TD sai COM música já na v1** (16/11/2026: "quero que você já coloque a música") → trilha da biblioteca Spotclai,
  `C:/Render/_trabalho/_trilhas/escolher_ini.py` para a virada cair no "mas" forte, `trilha.py` (voz até -0,1 dBTP,
  música 10 dB abaixo, continua na CTA).
- **CTA antiga (digitada) não vale mais** ("aqui está a cta antiga") → depois da trilha, troque pela CTA "me segue"
  (`reels-novela-clailton/scripts/trocar_cta.py`), como nas novelas.
