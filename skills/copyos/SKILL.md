---
name: copyos
description: "Atalho do CopyOS. Use SEMPRE que a mensagem tiver 'copyos', 'copy os', 'use copyos', 'usa o CopyOS', '/copyos' ou 'fluxo do CopyOS', em qualquer grafia. Garante que o pedido de copy de venda (anúncio, gancho, página de vendas, VSL, advertorial, e-mail/SMS, sequência, isca, PDP, revisão de copy) passe pelo fluxo completo do CopyOS, na ordem: copy-de-conversao, briefing-inteligente quando faltar o brief, revisor-chefe, checagem-de-alegacoes e checagem-pre-lancamento, e termine com o selo '✅ CopyOS:' mostrando o que rodou. Se a pessoa só perguntar o que é o CopyOS, explique em poucas linhas e dê exemplos de pedido."
---

# CopyOS (atalho)

Esta skill não escreve copy. Ela só garante que o fluxo completo do CopyOS rode, sempre na mesma
ordem, e que a pessoa veja no fim que rodou. Quem escreve é a `copy-de-conversao`.

## Quando a mensagem é só uma pergunta

Se a pessoa perguntar "o que é o CopyOS", "você tem o CopyOS?" ou parecido, sem pedir uma peça:
responda em até 5 linhas que o CopyOS escreve copy de venda já revisada e checada, e dê 3 exemplos de
pedido no formato `use copyos: 3 anúncios para [produto], público [quem]`. Não procure na memória
"copies prontas"; a pergunta é sobre a ferramenta.

## Quando há um pedido de copy: o fluxo, nesta ordem

1. **Abra a skill `copy-de-conversao`** pela ferramenta de skills e siga as instruções dela para a peça
   pedida. Ela é o motor e manda nos detalhes de escrita.
2. **Brief do negócio.** Se no chat, no projeto ou na memória já houver um BUSINESS-MEMORY / brief
   aprovado, use. Se não houver, siga com o que a pessoa deu, marque o que falta com
   `[placeholder]` e ofereça uma vez a entrevista da `briefing-inteligente` (não segure a entrega).
3. **Escreva a peça completa** pela `copy-de-conversao`.
4. **Revisor-chefe.** Abra a skill `revisor-chefe` e faça a passada dela na copy antes de entregar.
5. **Checagem de alegações.** Abra a skill `checagem-de-alegacoes` e confira cada promessa, número,
   depoimento e garantia. Relate como alertas curtos depois da copy.
6. **Pré-lançamento.** Se a peça vai ao ar (anúncio, página, e-mail, VSL), abra a skill
   `checagem-pre-lancamento` e devolva PRONTO ou a lista de correções. Se for rascunho ou ideia, marque
   "pré-lançamento: não se aplica (rascunho)".
7. **Feche com o selo**, numa linha só, depois dos alertas:

   `✅ CopyOS: copy-de-conversao ok · revisor-chefe ok · alegações: N alertas · pré-lançamento: PRONTO | N correções | não se aplica`

   O selo é pedido do dono da conta e é a única exceção à regra da `copy-de-conversao` de não relatar
   o que foi carregado. Ele tem que ser verdadeiro: se alguma etapa não rodou (skill indisponível,
   erro, falta de dado), escreva no selo qual e por quê, por exemplo `revisor-chefe: não rodou (skill
   indisponível; passada feita pelas 25 checagens internas)`.

## Regras

- Não inventar número, depoimento, cliente nem resultado: dado que falta vira `[placeholder]`.
- Flags de modo escritas pela pessoa (`--lite`, `--extreme`, `--unrestricted`) passam direto para a
  `copy-de-conversao`.
- Pedido de oferta (pacote, preço, bônus, garantia, upsell) vai para a skill `ofertaos`, não para este
  fluxo. Se o pedido tiver as duas coisas, faça a oferta primeiro e depois a copy em cima dela.
- Responder em português do Brasil.
