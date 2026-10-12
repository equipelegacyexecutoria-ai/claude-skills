Se você ainda não configurou, rode a checagem de instalação: confirme que as 9 skills estão disponíveis e peça para abrir o INVENTARIO-DE-RECURSOS.json da Biblioteca dos Mestres. A entrevista completa do brief do negócio deixa todo trabalho mais afiado, mas você pode começar um trabalho antes dela: a IA trabalha com o que você der, sinaliza o que está faltando e oferece a entrevista uma vez.

Reaproveite o brief aprovado; peça só os dados que faltarem.

Você não chama skill nenhuma. Peça a copy em linguagem natural; o CopyOS aciona sozinho a revisão, a checagem de alegações e o resto. No ChatGPT, se ele não acionar sozinho, digite @ e escolha "Copy de Conversão" na primeira mensagem. No Codex, se precisar, digite `$copy-de-conversao` no começo do pedido. Não procure arquivos de instalação em contas conectadas.

Encontre arquivos de apoio em references/produto/, dentro da sua instalação completa. Faça cópias de trabalho dos templates. Mantenha os resultados neste projeto de negócio, ou baixe-os para o próximo chat.

# Prompts de exemplo · CopyOS

Você não chama skill nenhuma. Peça a copy em linguagem natural; o CopyOS aciona sozinho a revisão, a checagem de alegações e o resto. No ChatGPT, se ele não acionar sozinho, digite @ e escolha "Copy de Conversão" na primeira mensagem. No Codex, se precisar, digite `$copy-de-conversao` no começo do pedido. Preencha os [colchetes] com os seus próprios fatos.

## O único padrão

Todo prompt que tira uma copy boa disso tem as mesmas cinco coisas. Deixe uma de fora e ele chuta, e um chute é seguro e sem graça.

1. **O trabalho e o formato dele.** O que é, quantos, quão longo, onde roda. "3 anúncios frios de Meta, um curto, um padrão, um longo em formato de história."
2. **Quem e onde.** Quem lê, se já conhece você, e o que acontece depois do clique. "Donos de casa que nunca ouviram falar de nós. O clique vai para um formulário de orçamento."
3. **A coisa que só você pode dizer.** O único fato que um concorrente não consegue copiar. "Nós passamos por cima do azulejo antigo. Sem demolição." Pule isso e você recebe anúncios que qualquer negócio da sua categoria poderia rodar.
4. **Cor.** O que os clientes realmente dizem, uma história real, a prova que você tem. Ou diga "nenhuma ainda, deixe um [placeholder] para mim". De um jeito ou de outro, ele não vai inventar.
5. **O dial.** `--extreme` para intensidade máxima (já é o padrão do Motor em trabalho de marketing; escreva a flag para deixar isso explícito), `--unrestricted` para abandonar o estilo da casa e definir tom e extensão você mesmo, os dois para os dois.

Depois rode em três turnos. O primeiro rascunho de ninguém é o que roda, nem o meu.

1. **Peça opções.** Ângulos, conceitos, ganchos. Curtos, uma linha cada.
2. **Filtre.** "3 e 6 têm uma ideia. O resto é seguro demais. Me dê mais 5 como o 3."
3. **Finalize.** "Escreva 3 na íntegra." Depois corrija o que está errado: "A primeira linha está fraca porque [por quê]."

---

## Antes do primeiro trabalho

**Ainda não tem brief? Cole os fatos.** Funciona no primeiro dia, antes da entrevista.
> Antes de começarmos, aqui está meu negócio: [o que você vende e o preço]. [Quem compra]. [O problema com que chegam até você]. [O que te diferencia, em uma linha]. [Qualquer prova: avaliações, números, resultados]. [Onde isso vai rodar]. Use isso para tudo neste chat.

**A entrevista, uma vez.** Todo trabalho depois dela roda a partir do seu brief, então você para de redigitar o texto acima.
> Monte meu brief do negócio: me conduza pela entrevista completa.

**Sua voz.** A principal reclamação depois de "genérico demais" é "não é assim que eu falo".
> Aqui estão três coisas que escrevi que soam como eu: [cole um post, um e-mail, uma mensagem para um cliente]. Não as copie. Me diga em cinco linhas como eu escrevo, e depois escreva tudo neste chat desse jeito.

**As palavras dos seus clientes.** O jeito mais rápido de ter uma copy que não soa igual à de todo mundo.
> Aqui estão [10 avaliações / e-mails de suporte / DMs / anotações de chamadas]. Extraia as frases que se repetem e me diga quais deveriam entrar na minha copy palavra por palavra.

**Agências e freelancers: uma pasta por cliente.** Instale as skills uma vez na pasta pessoal do Claude Code (`~/.claude/skills/`), depois mantenha uma pasta de projeto por cliente com o brief daquele cliente dentro. As skills são as mesmas para todo cliente. O brief é o que muda.
> Monte o brief deste negócio: esta pasta é para o meu cliente [nome]. Me conduza pela entrevista para o negócio dele.

---

## Os trabalhos

Cada um: quando usar, o que trazer, o prompt, e o segundo turno.

### 1. Anúncios frios que começam do zero
Traga: o brief, e para onde vai o clique.
> Me dê 8 ângulos para anúncios frios de Meta para [produto]. Uma linha cada: quem ele para e por quê. A única coisa que só nós podemos dizer: [sua diferença]. O clique vai para [página / formulário / checkout]. Só os ângulos, eu escolho. --extreme

Turno 2:
> Escreva [3] e [6] na íntegra como anúncios de Meta. Cada um recebe dois textos primários que abrem de duas formas diferentes, duas headlines e duas descrições. Faça um curto e um longo guiado por história. A primeira linha precisa dizer ao leitor em dois segundos se é para ele.

### 2. O anúncio longo ou advertorial para quem não te conhece
Para tráfego de topo de funil. Mais longo, com uma história, e não faz oferta na primeira linha.
> Um anúncio longo de Meta para tráfego frio, 250 a 400 palavras, guiado por história. Abra com um momento que meu comprador vai reconhecer: [a situação em que ele está]. Não nomeie o produto até o leitor querer a resposta. Termine com um motivo para clicar agora. Use as palavras dos meus clientes do brief. --extreme --unrestricted

### 3. A headline que faz continuarem lendo
> 10 pares de headline e sub-headline para [página], cada um construído sobre uma abordagem diferente. A headline fisga, a sub-headline diz exatamente o que eles recebem e por que deveriam se importar. Sem frases espertas que precisam de explicação. Me diga quais duas você testaria e por quê.

Turno 2, quando estão perto mas não lá:
> [Número] é o mais próximo. A headline está certa mas a sub-headline está falando de características. Reescreva a sub-headline de cinco formas, só benefícios, uma linha cada.

### 4. Uma página de vendas completa
Uma página que carrega a venda inteira é planejada antes de ser escrita.
> Preciso de uma página de vendas para [produto] a [preço]. Planeje primeiro: a ordem do argumento, onde entra a prova, qual objeção é resolvida onde. Me mostre o plano, espere meu OK, depois escreva a página inteira.

### 5. O e-mail que soa como uma carta sua
> Um e-mail em texto simples para [minha lista / novos compradores / pessoas que não compraram] sobre [a única coisa]. Um trabalho, um link. Escreva como se eu estivesse escrevendo para uma pessoa. Deixe em negrito só as duas ou três linhas que quem passa os olhos rapidamente não pode perder. Assunto e linha de preview também, três opções cada.

### 6. Uma sequência de boas-vindas ou follow-up
> Uma sequência de [3] e-mails para pessoas que acabaram de [se cadastrar em X / comprar Y]. E-mail 1 entrega o que vieram buscar. E-mail 2 [constrói a crença que precisam ter]. E-mail 3 [faz a oferta]. Texto simples, de mim, um link cada. Me diga o timing de envio que você usaria e por quê.

### 7. O post de rede social na sua voz
> Um post de LinkedIn sobre [algo real que aconteceu / uma lição / um resultado de cliente]. Na minha voz (veja os exemplos acima ou meu brief). A primeira linha precisa parar a rolagem sozinha. Sem parede de hashtags, sem abertura de "aqui está o que eu aprendi". Me dê duas versões: uma curta, uma mais longa com a história.

### 8. A isca digital e a página que a entrega
> Estou dando de graça [a coisa gratuita]. Escreva a headline e três bullets para a caixa de cadastro, a linha de agradecimento, e o e-mail que entrega o material. Os bullets dizem o que eles vão ter em mãos assim que usarem.

### 9. Botões, barras e as palavras pequenas
> Reescreva o texto do botão e a linha abaixo de cada botão nesta página: [cole]. Todo botão diz o que eles recebem, não "Enviar" ou "Saiba mais". Me dê três opções por botão.

### 10. A proposta que recebe resposta
> Reescreva esta proposta: [cole]. Abra com o problema do cliente nas palavras dele, depois o que eu vou fazer, depois por que eu, depois o preço e o que está incluído. Faça o próximo passo ser uma frase para a qual ele possa dizer sim.

### 11. Um anúncio de serviço local
Para prestadores de serviço, clínicas, estúdios. As pessoas compram o que está perto e em quem confiam.
> 3 anúncios de Meta para [serviço] em [cidade + raio]. Chame a pessoa exata na primeira linha: [quem, em que situação]. A coisa que só nós podemos dizer: [diferença]. Prova: [avaliações / anos / trabalhos feitos]. O pedido é [uma ligação / um orçamento / um agendamento]. Um curto, um padrão, um longo. --extreme

### 12. A abertura de webinar, ligação ou curso
> Os primeiros dois minutos do meu [webinar / ligação de vendas / vídeo de lançamento de curso], palavra por palavra. Abra com o problema que meu comprador tem agora, mostre que eu entendo isso melhor do que ele, depois prometa o que ele vai ter ao final. Sem história de vida ainda.

### 13. Conserte o que você já tem
Diga o que está errado. "Deixe melhor" te dá uma versão polida do mesmo problema.
> Aqui está minha [página / anúncio / e-mail]: [cole]. O que está errado: [longo demais / soa igual a todo mundo / ninguém clica / parece IA]. Reescreva. Mantenha [o que você quer manter].

### 14. Faça mais de um vencedor
> Este anúncio é o meu melhor: [cole, mais o que ele fez]. Me diga em duas linhas o que está sustentando ele. Depois escreva 5 versões que cada uma muda uma coisa, a abertura, a prova ou o ângulo, e diga qual coisa cada uma mudou.

### 15. Anúncios escritos do jeito que os mestres escreviam
A Máquina dá cada etapa de um anúncio ao mestre que era dono dela: Schwartz lê seu mercado, Caples escreve a headline e as palavras na imagem, Masterson e Forde escolhem as aberturas, Halbert escreve, Sugarman mantém o ritmo, Bencivenga constrói o corpo e a prova, Kennedy fecha, e a lista de erros fatais de Forde é a última checagem. Os nomes deles nunca aparecem no seu anúncio.
> 3 anúncios de Meta para [produto]. Use os grandes mestres por função. Cada anúncio recebe dois textos primários que abrem com dois leads diferentes sobre o mesmo corpo, duas headlines e duas descrições. São anúncios estáticos, então me dê as palavras para a imagem também. A única coisa que só nós podemos dizer: [sua diferença]. O clique vai para [página]. --extreme

Turno 2:
> Me mostre quais leads você usou em cada anúncio e por que combinam com meu comprador. Depois dê ao anúncio [2] uma terceira abertura de um tipo de lead que você ainda não usou.

Turno 3, quando um anúncio está perto:
> Rode os erros fatais de Forde no anúncio [1] e corrija o que falha. Depois leia comigo toda headline com todo texto primário e corrija qualquer par que não combine.

---

## Quando ainda não está bom

Use isso em qualquer coisa que a Máquina devolver.

- **Poderia ser de qualquer um.** "Um concorrente poderia rodar qualquer um destes. Reescreva em torno de [sua diferença]."
- **Não dá para saber para quem é.** "Alguém lendo a primeira linha não consegue saber se é para ele. Chame essa pessoa: [quem]."
- **Está vendendo o maquinário.** "Isso é característica. Me diga o que eles ganham com isso."
- **Soa como IA.** "Isso parece que foi escrito por IA. Encontre as linhas que entregam isso e reescreva como uma pessoa fala."
- **Está fraco demais.** "Seguro demais. Rode de novo com --extreme."
- **Está curto ou raso demais.** "Mais longo, 300 palavras, e dê cor: um momento real, um cliente real, um número real do meu brief."
- **Empreste um mestre.** "Como o Halbert abriria isso? Carregue a análise das Boron Letters e reescreva as três primeiras linhas do jeito dele, depois me diga o que ele deixaria em negrito." Ou nomeie a etapa: "Reescreva o fechamento do jeito que o Kennedy faria." "Me dê a headline do jeito que o Caples faria, dez delas, e fique com as duas melhores."
- **Pergunte qual mestre se encaixa.** "Qual dos grandes mestres é dono da parte que está fraca aqui? Conserte essa parte do jeito dele e me diga o que você mudou."
- **Vá para o livro certo.** "Abra o volume de headlines da Biblioteca dos Mestres e me dê mais 10 usando as abordagens que você ainda não usou." Ou o volume de objeções, ou o volume de ofertas.
- **Você quer o raciocínio.** "Mostre a revisão." Você recebe a passagem completa do Chefe em vez de uma linha.
- **Salve isso.** "Guarde o que decidimos sobre minha voz e meus ângulos hoje."

---

## Quando algo dá errado

- **A resposta é longa e cheia de notas.** Diga "Só a copy, guarde a revisão para você." Copy primeiro e notas curtas é o padrão do CopyOS; se a resposta vier diferente, repita o pedido.
- **Diz que a skill não está lá.** Ela não está instalada neste chat. No Claude Code, comece um novo chat na sua pasta de negócio; as skills carregam quando um chat começa. No ChatGPT, confira se a skill aparece em Instaladas.
- **Fica fazendo perguntas.** "Não pergunte, decida, e sinalize o que você presumiu."
- **Não escreve um número.** Ele não vai inventar um. Dê o número real, ou mantenha o [placeholder] e preencha antes de rodar.
- **Tudo soa igual.** Provavelmente falta o item 3. Diga a ele a única coisa que só você pode dizer.
