---
name: construtor-de-copy-de-conversao
description: "Use ao escrever ou editar copy de conversão estática respaldada por fonte: PDPs, páginas de produto, landing pages, páginas de vendas, advertoriais, listicles, sequências de e-mail, e-mails de ciclo de vida, módulos de oferta, copy de checkout/carrinho, seções de FAQ/objeção, variantes de teste de CRO, reescritas de seção de página ou decks de copy de resposta direta."
---

# Construtor de Copy de Conversão

## Propósito

Escrever copy para os canais que fazem a venda depois do clique: PDPs, landing pages, e-mails, advertoriais, listicles, módulos de oferta, blocos de FAQ/objeção e variantes de teste de CRO.

Este é o método do Motor para tudo o que vem depois do clique. Ele compartilha a lógica com `copy-de-anuncio-meta.md` e `diagnostico-de-oferta.md` (ambos nesta pasta) e com o restante de **copy-de-conversao**, mas sua saída não é um anúncio de Meta nem um roteiro de vídeo. Ele constrói peças de conversão que precisam de estrutura de página ou e-mail, mapeamento de fontes, notas de lançamento e hipóteses de teste.

## Contexto Obrigatório

Carregue `_compartilhado/contexto-obrigatorio.md` primeiro. Depois leia o brief do negócio e os arquivos de produto abaixo que existirem (um que falte vira uma suposição rotulada e um flag, nunca uma parada):

- `offer.md`
- `product-info.md`
- `avatar-research.md`
- `archetypes.md`
- `angle-map.md`
- `reviews.md` ou `voc.md`
- `competitors.md`
- `constraints.md`
- `references.md`

Para trabalho de PDP, landing page, seção de página, checkout/carrinho, FAQ ou CRO, leia também `page-copy/index.md` da pasta do produto quando existir, depois carregue o arquivo Markdown de page-copy específico que corresponda à rota ou variante. Use o Markdown de page-copy antes de abrir HTML bruto.

Para trabalho de checkout/carrinho, upsell pós-adição ao carrinho, cross-sell, módulo de oferta, combo ou CRO que toque em lógica de preço/CTA/carrinho, leia antes qualquer documentação de comércio do próprio negócio (regras de preço, carrinho, upsell) que o usuário fornecer, em vez de abrir código bruto de carrinho/tema.

Abra as referências mais profundas de **copy-de-conversao** só quando a tarefa precisar delas: voz em idioma nativo, nuance de sequência de e-mail, ofício de VSL ou página de vendas, ou um framework que o brief ainda não carrega.

Mantenha um recibo de contexto nas suas notas de trabalho: o brief e os arquivos de produto que você carregou, os arquivos de page-copy e comércio quando aplicável, o template de canal, os padrões da biblioteca de controles e da biblioteca de exemplos, as referências mais profundas, entradas faltantes ou desatualizadas e notas de risco de alegação. Entregue ao usuário quando ele pedir ("mostre seu trabalho"); se ele salvar o deck, o recibo vai ao final do arquivo salvo. A resposta em si é a copy primeiro, depois os flags.

## Use Isto em Vez de

- `copy-de-anuncio-meta.md` quando a saída for uma PDP, landing page, e-mail, advertorial, listicle, reescrita de módulo ou variante de CRO, e não um anúncio de Meta.
- Um método de roteiro de vídeo ou de criador quando a saída for copy escrita de página ou e-mail.
- Um briefing de anúncio estático único quando a saída for um deck de página, e-mail ou CRO.
- `diagnostico-de-oferta.md` quando a oferta já estiver diagnosticada o suficiente e o usuário quiser copy de produção.

Se a oferta, a postura de alegação, o público ou a pilha de provas estiverem pouco claros, rode `diagnostico-de-oferta.md` primeiro ou inclua uma seção curta de diagnóstico antes de escrever.

## Entradas

Obrigatórias:

- pasta do produto ou dossiê do produto
- canal: `pdp`, `landing_page`, `sales_page`, `advertorial`, `listicle`, `email_sequence`, `email_single`, `cro_test`, `checkout_cart`, `faq_objection` ou `module_rewrite`
- público/arquétipo
- nível de consciência
- mecanismo ou porquê
- oferta ou CTA
- prova disponível

Opcionais:

- esqueleto da página ou lista de seções
- copy atual da página/e-mail
- referência de concorrente/controle
- idioma
- flag de modo: `--extreme`, `--unrestricted` ou `--lite`
- número de variantes

O tom padrão é resposta direta agressivo-conversacional. Não recorra por padrão a polimento cauteloso de marca, a menos que o usuário peça explicitamente.

## Fluxo de Trabalho

### 1. Estabeleça o Trabalho da Copy

Nomeie o canal e o trabalho único:

- PDP: converter tráfego consciente do produto e da solução em checkout.
- Landing page: manter a congruência anúncio-página e aprofundar a mudança de crença.
- Advertorial/listicle: conquistar atenção fria, educar e fazer a ponte para o produto.
- E-mail: mover um segmento um passo mais perto da ação.
- Teste de CRO: mudar uma variável da página e prever o efeito na conversão.
- Módulo de FAQ/objeção: remover uma inibição específica perto do CTA.

Se o usuário pedir uma página "pega-tudo", ainda assim escolha uma espinha de mecanismo principal e uma decisão de compra principal. Não escreva uma pilha de alegações desconexas.

### 2. Selecione o Template do Canal

Carregue `construtor-de-copy-de-conversao--templates-por-canal.md` apenas para o canal relevante. Use-o para ordem das seções, prova obrigatória e campos de saída.

### 3. Crie o Recibo de Contexto

Antes de escrever a copy, liste:

- arquivos do dossiê do produto carregados
- arquivos de page-copy carregados, se houver
- arquivos de comércio carregados, se houver
- template de canal carregado
- padrões da biblioteca de controles selecionados
- padrões da biblioteca de exemplos selecionados
- referências carregadas, se houver
- skills extras carregadas, se houver
- entradas faltantes, desatualizadas ou que precisam de revisão do dono
- notas de risco de alegação

Se o recibo mostrar que a fonte de oferta, prova, preço, estoque, CTA ou mecanismo está faltando/desatualizada, escreva o rascunho mesmo assim: um [placeholder] nomeado onde entra o específico e um flag nomeando a lacuna. Nunca pare por isso.

### 4. Escolha Controles de Referência e Padrões de Exemplo

Se `../biblioteca-de-padroes/padroes.json` existir, escolha 1-3 padrões que combinem com a pressão do comprador, o nível de consciência, o mecanismo, a prova e o canal. Trate-os como evidência estrutural, não como copy de swipe.

Para trabalho de PDP/CRO, carregue apenas os arquivos Markdown de page-copy e comércio nomeados em Contexto Obrigatório, e apenas o que cada seção precisa.

Para ganchos, ganchos de desejo, headlines de seção, lógica de assunto/abertura de e-mail, leads de advertorial, títulos de listicle ou blocos adjacentes ao CTA, carregue também `_compartilhado/padroes-de-motivacao-de-headline.md`. Use-o para nomear o tipo de motivação do comprador e a família de padrão por trás da seção. Não force toda seção em uma fórmula; use-a apenas onde o formato de abertura afeta atenção, movimento de crença, emoção ou clareza de decisão.

Quando a tarefa precisar de inspiração de estrutura de página, e-mail, advertorial, listicle ou CRO, carregue `construtor-de-copy-de-conversao--biblioteca-de-exemplos.md`. Ele contém padrões destilados de uma página própria de dispositivo ficcionalizada e de páginas de referência externas. Use a biblioteca para estrutura, movimento de crença, mecânica de oferta, sequenciamento de prova e notas de risco - não para copiar redação.

Se o usuário fornecer links de páginas ao vivo, páginas de swipe, advertoriais, PDPs, e-mails ou copy atual de página como exemplos, trate-os como controles. Extraia as mecânicas em notas Markdown ou estenda `construtor-de-copy-de-conversao--biblioteca-de-exemplos.md`; não cole copy bruta de página nas saídas nem nos dossiês de produto.

### 5. Construa a Cadeia de Crença

Toda saída precisa de uma cadeia de crença visível:

`crença atual -> pressão -> caminho antigo fracassado -> novo mecanismo -> prova -> ação de baixo arrependimento`

Para e-mail, faça a cadeia atravessar a sequência. Para PDP/CRO, mapeie-a nas seções da página. Para advertorial/listicle, mapeie-a no caminho de "sim" do leitor.

### 6. Escreva com Tags de Fonte

Para todo bloco principal, declare a base de fonte:

- `[source: VOC]`
- `[source: reviews]`
- `[source: offer.md]`
- `[source: product-info.md]`
- `[source: constraints.md]`
- `[source: biblioteca-de-padroes/<pattern-id>]`
- `[source: original - precisa de revisão do dono]`

As tags de fonte podem ficar na tabela de trabalho ou no Mapa de Fontes, não necessariamente dentro da copy final para o cliente.

Não invente fatos, depoimentos, preços, credenciais, garantias, escassez, prova clínica ou alegações de performance.

### 7. Escreva a Copy

Use o formato de saída do canal selecionado em `construtor-de-copy-de-conversao--templates-por-canal.md`.

Regras:

- Um mecanismo principal por página/e-mail/teste, a menos que o brief diga o contrário.
- Coloque a linguagem de risco nos flags depois da copy, a menos que ela precise ser voltada ao cliente.
- Use prova exata quando for respaldada por fonte; onde faltar um específico, coloque um `[placeholder]` nomeado na linha e marque com flag.
- Mantenha o CTA singular: uma próxima ação.
- Para qualquer idioma que não seja o português do Brasil, escreva de forma nativa. Não traduza ganchos ou esqueletos de página literalmente.
- Para `--extreme`, acrescente um flag para as alegações mais ousadas que o usuário deve conseguir respaldar.

### 8. Passada do Revisor-chefe de Conversão

Rode a passada universal de `_compartilhado/passada-do-revisor-chefe.md`, mais esta passada de copy de conversão:

- Se a seção poderia estar em qualquer página DTC, reescreva em torno do mecanismo e da pressão do comprador deste produto.
- Se a página abre com características do produto antes de o comprador se reconhecer, reordene.
- Se a prova está longe do ponto de decisão, mova-a ou repita-a perto do CTA.
- Se a copy explica demais antes de pedir, comprima.
- Se uma variante de CRO muda mais de uma variável, divida.
- Se um e-mail tenta vender todas as razões de uma vez, corte para uma mudança de crença.
- Se copy em outro idioma soa polida mas não falada, reescreva antes da validação.
- Se um padrão de headline foi usado, confirme que tipo de motivação, mudança de crença, necessidade de prova e reescrita nativa estão alinhados.

### 9. Validação

Antes de entregar o deck, rode a revisão de `validador-de-copy.md` para o formato de copy de conversão nas suas notas de trabalho, incluindo a checagem de alegações para páginas, e-mails ou testes de CRO arriscados. Corrija o que falhar; uma alegação que você não consegue respaldar vira um flag. Relate vereditos por requisito só quando o usuário pedir.

Use `--extreme` ou `--unrestricted` quando esse modo estiver ativo.

## Contrato de Saída

Por padrão, entregue:

- uma linha nomeando o canal e o produto
- a seção de copy específica do canal de `construtor-de-copy-de-conversao--templates-por-canal.md`, pronta para colar
- `Flags:` uma linha cada, só se houver (alegações a respaldar, `[placeholders]` a preencher, suposições, linguagem de risco mantida fora da copy)
- uma linha do Chefe: o que a passada mudou

Monte o restante nas suas notas de trabalho e inclua qualquer parte quando o usuário pedir: os campos do topo (`Público`, `Nível de Consciência`, `Oferta`, `Objetivo Principal`), `## Recibo de Contexto`, `## Estratégia de Copy`, `## Mapa de Fontes`, `## Notas de Estratégia`, `## Recomendação de Teste`.

## Regras do Operador

- Se a verdade de prova, preço, estoque, alegações ou CTA puder estar desatualizada, diga isso em um flag.
- Não enterre o mecanismo. Ele deve aparecer no herói/abertura, corpo, prova e fechamento.
- Não escreva "sopa de benefícios" genérica. Todo bloco precisa mover crença, provar uma alegação, remover uma inibição ou pedir ação.
- Restrições são o piso factual, não o teto criativo.
