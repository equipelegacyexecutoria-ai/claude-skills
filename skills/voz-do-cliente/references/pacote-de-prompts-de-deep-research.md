# O Pacote de Prompts de Deep Research

Quatro prompts prontos para colar. A MÁQUINA preenche cada [colchete] a partir do levantamento antes de entregá-los -
o usuário cola prompts prontos, nunca templates em branco. Rode-os em uma IA com capacidade de deep research
(Claude com ferramentas de pesquisa, Perplexity, ou similar). A ordem importa: 1 → 2 → 3 → 4.

Cada prompt carrega o contrato de evidência. Não o suavize.

---

## Prompt 1 - Mercado, Concorrência e Panorama de Preços

```text
Você está fazendo deep research para [NOME DO NEGÓCIO], um(a) [descrição em uma linha] que vende para [mercado/idioma]
a [ponto(s) de preço]. Estágio: [estágio].

Fatos conhecidos para usar como contexto, não como prova: [cole as seções de negócio + promessa do
levantamento, incluindo cada "unknown" (desconhecido)].

Contrato de evidência inegociável: não invente fatos, preços, tamanhos de mercado, volumes de busca ou
citações. Rotule cada achado como verificado-atual (você checou uma fonte ao vivo agora, com link),
snapshot-local (fonte datada que pode ficar desatualizada), inferência (raciocinado), ou suposição. Um chute rotulado
como achado é uma falha.

Pesquise e retorne:
1. O conjunto competitivo real: com quem [comprador em uma frase] realmente nos compara - rivais
   diretos, substitutos, alternativas DIY, e "não fazer nada". Nomes, links, preços atuais, ofertas atuais.
2. O panorama de preço e oferta: pontos de preço, pacotes/planos, garantias, testes gratuitos, descontos rodando
   AGORA. Cálculo de preço-por-unidade ou preço-por-resultado onde possível.
3. Como a categoria fala: as promessas que todo mundo faz (linguagem saturada a evitar), os tipos de prova
   usados, as alegações que parecem regulamentadas ou arriscadas.
4. Leitura de sofisticação do mercado: esse mercado é novo, consciente de soluções, ou exausto de alegações? Que
   espaço de mecanismo/ângulo parece não reivindicado?
5. Lacunas: o que não pôde ser verificado e a próxima fonte exata que resolveria isso.
```

## Prompt 2 - Linguagem do Comprador e Voz do Cliente

```text
Mesmo contexto de negócio de antes: [descrição em uma linha], comprador: [frase do comprador], mercado: [mercado].

Contrato de evidência: citações literais APENAS, cada uma com o link da fonte. Nunca parafraseie em linguagem
de marketing. Nunca calcule porcentagens a partir de temas qualitativos - diga "tema recorrente" e mostre as
citações. Não invente uma única citação.

Explore estes tipos de fonte por linguagem do comprador: [cole o mapa de fontes do Passo 2 - subreddits, plataformas
de avaliação, fóruns, seções de comentários, comunidades relevantes para este negócio].

Extraia e retorne, com citações sob cada item:
1. Eventos-gatilho: o que aconteceu logo antes de as pessoas começarem a procurar ativamente. Histórias exatas.
2. A escada de dor: reclamação superficial → custo prático → custo emocional/social → medo de identidade.
3. Alternativas fracassadas: o que elas tentaram, nas próprias palavras, e por que dizem que fracassou.
4. Objeções: o que quase impede a compra, ranqueado por frequência e intensidade.
5. Resultado dos sonhos: como é "funcionou" nas palavras do dia a dia delas.
6. Voz do Cliente da concorrência: o que os compradores elogiam e reclamam sobre [nomes dos concorrentes] - padrões
   de 5 estrelas, padrões de 1 estrela, linguagem de reembolso.
7. Um banco de frases: 20-40 linhas literais que soam como ganchos, agrupadas por emoção.
8. Lacunas e pontos fracos: onde a evidência é fraca e onde procurar em seguida.
```

## Prompt 3 - Alegações e Comprovação de Provas

```text
Negócio: [descrição em uma linha]. Estamos preparando alegações voltadas ao cliente e precisamos saber o que
podemos comprovar e o que não podemos.

Alegações candidatas a checar: [liste cada alegação que o levantamento revelou + cada promessa que a copy vai querer
fazer, incluindo qualquer campo de prova "unknown" (desconhecido)].

Contrato de evidência: para cada alegação, retorne o status - comprovada (cite a fonte exata que possuímos ou uma
fonte autoritativa atual), parcial (diga exatamente o que está faltando), ou não comprovada (diga que evidência
seria necessária e o jeito mais barato de consegui-la). Para uma alegação não comprovada, diga que prova a
sustentaria e o jeito mais barato de consegui-la; nunca a apresente como comprovada. Sinalize qualquer alegação que
pareça restrita por plataforma (políticas de anúncio da Meta/Google/TikTok) ou regulamentada
[específico da categoria: saúde/finanças/jurídico se aplicável] e diga por quê.

Retorne também: as 5 alegações mais fortes que POSSAMOS fazer agora em máxima agressividade, ranqueadas, cada uma com
sua prova anexada.
```

## Prompt 4 - Dissecação de Anúncios e Ângulos da Concorrência

```text
Negócio: [descrição em uma linha]. Concorrentes: [nomes do Prompt 1].

Verifique a Biblioteca de Anúncios da Meta (e a transparência de anúncios do TikTok/Google onde disponível) para cada
concorrente. Ordene pelo que parece rodar por mais tempo / com mais impressões - uma proxy do que está funcionando, não
prova de lucro. Rotule tudo de acordo.

Retorne:
1. Por concorrente: quantos anúncios estão ativos, quais formatos dominam (estático/vídeo/carrossel), e os 3-5
   anúncios que parecem ser os cavalos de batalha (links ou descrições).
2. O mapa de ângulos: quais argumentos, ganchos, ofertas e dispositivos de prova a categoria explora - e quais
   ângulos NINGUÉM está explorando (a lacuna é a oportunidade).
3. Estrutura que vale a pena tomar emprestada: layouts, posicionamento de prova, padrões de gancho - só
   estruturas. Sinalize explicitamente: alegações, depoimentos e ativos de marca nunca devem ser copiados.
4. Checagem de destino: para onde os anúncios levam (página de produto, advertorial, listicle, quiz) e o que
   isso implica sobre o que está convertendo para eles.
5. Lacunas: o que não pôde ser visto e como checar.
```

---

**Depois que os quatro retornarem:** alimente tudo no Passo 4 (mineração) e no Passo 5 (o dossiê). A pesquisa
é matéria-prima - o dossiê é o entregável.
