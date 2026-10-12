---
name: copy-de-anuncio-meta
description: Use ao criar copy padrão de anúncio de resposta direta para Facebook/Meta, incluindo anúncios de imagem única, carrossel ou roteiros de anúncio em vídeo. Esta é a skill padrão de copy para Meta, a menos que o usuário peça especificamente estáticos longos, estáticos nativos em formato advertorial, LFS ou geração de prompt só de imagem.
---

# Copy de Anúncio de FB

## Propósito

Criar copy de anúncio de resposta direta para Meta que comprime a estratégia em copy nativa de feed: gancho, pressão do comprador, mecanismo, prova, tratamento de objeções e CTA.

Use isto para copy normal de anúncio de Facebook/Instagram. Se o usuário pedir um estático longo, um estático em estilo advertorial ou um conceito de imagem nativa, escreva a copy com `construtor-de-copy-de-conversao.md` (seus canais de advertorial e formato longo) e dê a direção de imagem em palavras simples. Prompts de imagem detalhados ficam fora do CopyOS: entregue o brief de imagem a quem produz o criativo.

## Contexto Obrigatório

Carregue `_compartilhado/contexto-obrigatorio.md`. Ele define: loop de metodologia, regras de carregamento de referências (resumo rápido primeiro, referências completas só quando necessário), arquivos do dossiê do produto, biblioteca de controles e tratamento de peças vencedoras.

## Entradas

Obrigatórias:

- descrição do produto ou pasta do produto
- público-alvo ou avatar
- formato do anúncio: `single_image`, `carousel` ou `video`
- mecanismo ou porquê
- oferta

Opcionais:

- nível de consciência
- tom: `aggressive`, `conversational` ou `professional`
- ângulo da landing page
- peças de prova
- objeções a tratar
- flag de modo, como `--extreme`

O tom padrão é agressivo-conversacional. Não recorra por padrão a voz de marca conformista, educativa ou polida, a menos que o usuário peça explicitamente.

## Consciência para Tamanho da Copy

- Inconsciente: história, curiosidade, sintoma visível ou ódio do mercado primeiro. Texto principal mais longo.
- Consciente do problema: dor e alternativas fracassadas primeiro. O mecanismo faz a ponte para a solução.
- Consciente da solução: diferenciação de mecanismo primeiro. Pesado em prova.
- Consciente do produto: oferta, prova, tratamento de objeções e urgência.
- Totalmente consciente: oferta/preço/bônus/garantia primeiro. Educação mínima.

## Regras de Variação

Gere exatamente 3 variações, a menos que o usuário peça outra coisa. A menos que o usuário defina um tamanho, faça-as em três tamanhos para que a primeira rodada mostre a amplitude: uma curta (o gancho mais uma ou duas linhas, abaixo de cerca de 60 palavras), uma padrão (3-5 parágrafos curtos) e uma longa, guiada por história (cerca de 150-300 palavras). Quando o tipo de produto do usuário pedir outros tamanhos, use a tabela em `references/pacote-de-anuncio-meta.md`.

Cada variação é um pacote de anúncio de Meta (especificação: `references/pacote-de-anuncio-meta.md`): dois textos principais que abrem com dois tipos de lead diferentes sobre um corpo compartilhado, duas headlines, duas descrições e um CTA, mais a legenda e a direção de imagem para um estático. As três variações diferem por ideia e tamanho. Dentro de uma variação, os dois textos principais carregam a mesma ideia e diferem só pelo lead. Toda headline e descrição precisa ler bem com qualquer um dos dois textos principais. Escreva cada parte sob o mestre que é dono dela (`references/os-mestres-por-etapa.md`). Se o usuário pedir um texto principal por anúncio, dê um.

Cada variação precisa usar um tipo de gancho diferente e um padrão de headline/motivação/desejo diferente, quando possível. Carregue `_compartilhado/padroes-de-motivacao-de-headline.md` e selecione o padrão depois de escolher a mudança de crença. Exemplos de padrão incluem problema-solução, anúncio/novo mecanismo, detalhe pouco conhecido, tema desconfortável, ação fracassada, resultado sem dor, transformação, erro, mecanismo-muda-tudo, presente, surpresa do cético, descoberta, pergunta social e presente emocional.

Tipos de gancho:

- lacuna de curiosidade
- contradição
- alternativa fracassada
- ódio do mercado
- resultado desejado
- prova social
- contraste preço/valor
- reversão de objeção
- chamada de identidade
- gatilho de timing

Duas variações nunca devem atacar a mesma crença do mesmo jeito.

Não cole fórmulas de headline ou gancho de desejo diretamente na copy em outro idioma. Reescreva o padrão em fala nativa e preserve o trabalho estratégico, não a sintaxe.

## Regra dos Primeiros 125 Caracteres

Os primeiros 125 caracteres são o anúncio. Confira-os nas suas notas de trabalho; não os marque na copy que você entrega, para que ela cole limpa.

```text
Contradição específica. Insinuação do mecanismo. Motivo para continuar lendo.
```

A abertura precisa:

- caber em menos de 125 caracteres
- sustentar-se sozinha antes do "Ver mais"
- criar curiosidade, pressão ou contradição
- evitar aberturas vagas como "Você está procurando..."

## Limites de Caracteres

- Texto principal: máximo de 2.200 caracteres.
- Headline: máximo de 40 caracteres.
- Descrição: máximo de 30 caracteres.

Mais curto costuma ser melhor, a menos que a consciência seja baixa e a educação seja necessária.

## Requisitos de Formato

### Imagem Única

Inclua:

- Dois Textos Principais (dois tipos de lead, um corpo compartilhado)
- Duas Headlines
- Duas Descrições
- Botão de CTA
- Legenda (as palavras na imagem; nunca uma repetição da linha 1 do texto principal)
- Direção de Imagem

O texto principal padrão tem 3-5 parágrafos curtos: gancho -> pressão -> mecanismo -> prova/objeção -> CTA. A variação curta mantém o gancho, um ponto de prova e o CTA; a longa conta a história ou constrói o mecanismo antes do pedido. Qualquer tamanho, formato ou estilo que o usuário pedir prevalece.

### Carrossel

Inclua:

- Dois Textos Principais (dois tipos de lead, um corpo compartilhado)
- Duas Headlines
- Duas Descrições
- Botão de CTA
- Cartões do Carrossel

Use 3-5 cartões:

- Cartão 1: gancho/problema
- Cartões 2-3: mecanismo/prova
- Cartão final: oferta/CTA

### Vídeo

Inclua:

- Dois Textos Principais (dois tipos de lead, um corpo compartilhado)
- Duas Headlines
- Duas Descrições
- Botão de CTA
- Roteiro do Vídeo

Estrutura do roteiro:

- 0-3s: gancho visual e verbal
- 3-10s: problema ou alternativa fracassada
- 10-25s: mecanismo
- 25-40s: prova e tratamento de objeções
- 40-60s: oferta e CTA

Os primeiros 3 segundos precisam funcionar sem som e com som.

## Seleção do Botão de CTA

Escolha entre as opções de CTA do Meta:

- Comprar agora
- Saiba mais
- Cadastre-se
- Obter oferta
- Reservar
- Fale conosco
- Inscreva-se
- Fazer pedido

Use `Comprar agora`, `Obter oferta` ou `Fazer pedido` para compra direta de produto. Use `Saiba mais` só quando o tráfego frio precisa de educação ou a landing page é um advertorial.

## Regras de Prova e Objeção

Toda variação deve carregar:

- o mecanismo do produto, não só características
- a prova mais forte que você realmente tem: depoimento, número, autoridade, demonstração, garantia, porquê. Sem nenhuma, venda o mecanismo, a situação do comprador e as próprias palavras dele; onde um específico acertaria mais forte, coloque um `[placeholder]` nomeado na linha e marque com flag
- a objeção que mais importa para este comprador, tratada direta ou indiretamente
- a jornada do público: o que ele já tentou, o que está falhando ou no que ele acredita hoje

Nunca apresente como reais fatos, resultados, depoimentos, preços, credenciais, garantias, escassez ou prova inventados. Nunca encha uma variação com "pode", "talvez" ou "vale a pena conferir" para preencher um espaço de prova.

## Aplicação de Referência

Monte as Notas de Estratégia (ver `_compartilhado/notas-de-estrategia.md`) nas suas notas de trabalho antes de escrever; elas afiam as escolhas. Inclua-as no pacote só quando o usuário pedir notas de estratégia. Puxe os nomes de alavanca de `../livros/resumo-rapido.md`. Use escolhas de alavanca específicas, não rótulos de framework.

## Passada do Revisor-chefe de Conversão

Rode a passada universal + a passada específica do formato Copy de Anúncio de FB de `_compartilhado/passada-do-revisor-chefe.md` enquanto rascunha, depois a passada do revisor-chefe como último passo antes de entregar o pacote (ver o passo 18 do controlador).

Só coloque avisos legais dentro da copy do anúncio quando o usuário pedir, a categoria do produto exigir ou `constraints.md` disser explicitamente que são obrigatórios na copy do anúncio. Caso contrário, coloque-os nos flags depois dos anúncios.

## Flags de Modo

Veja `_compartilhado/flags-de-modo.md` para as regras de `--extreme` e `--unrestricted`. A flag de modo ativa se aplica também à revisão de `validador-de-copy.md`.

## Formato de Saída

Entregue os anúncios, prontos para colar, depois os flags e uma linha do Chefe. Quando um específico faria uma linha acertar mais forte, a oferta de encontrá-lo é um dos flags (`references/espinha-da-atencao-e-camada-de-prova.md`). Nada mais, a menos que o usuário peça.

```markdown
## Anúncios Meta: [Nome do Produto]

### Anúncio 1 (curto): [a ideia única, em poucas palavras]

**Legenda (na imagem):**
[só imagem única; as linhas na imagem]

**Imagem:** [só imagem única, uma ou duas linhas]

**Texto principal 1 (lead de [tipo de lead]):**
[lead A]

[corpo compartilhado]

**Texto principal 2 (lead de [tipo de lead]):**
[lead B]

[corpo compartilhado]

**Headline 1:** [máx. 40 caracteres]
**Headline 2:** [máx. 40 caracteres]
**Descrição 1:** [máx. 30 caracteres]
**Descrição 2:** [máx. 30 caracteres]
**Botão de CTA:** [opção de CTA do Meta]
**Cartões do carrossel:** [só carrossel]
**Roteiro do vídeo:** [só vídeo; os dois leads como duas aberturas]

### Anúncio 2 (padrão): ...
### Anúncio 3 (longo, guiado por história): ...

**Rode primeiro:** Anúncio [n], porque [uma linha].

**Flags:** [só se houver, uma linha cada: uma alegação a respaldar, um `[placeholder]` a preencher, uma linha com chance de reprovação do anúncio, uma suposição que você fez]

Chefe: [o que a passada mudou, uma linha]. Diga "mostre a revisão" para a passada completa.
```

Sob pedido, acrescente qualquer um destes: o tipo de gancho e o padrão de motivação por variação, as Notas de Estratégia, a tabela de testes, os resultados do validador e do scorecard, a revisão completa do Chefe.

## Validação

Antes de entregar o pacote, rode a revisão de `validador-de-copy.md` para o formato de anúncio de Facebook e a rubrica de `scorecard-criativo.md` em cada anúncio, nas suas notas de trabalho. Corrija o que falhar e use o scorecard para escolher a linha "Teste primeiro". Mostre os resultados só quando o usuário pedir.
