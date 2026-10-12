Se você ainda não configurou, rode a checagem de instalação: confirme que as 9 skills estão disponíveis e peça para abrir o INVENTARIO-DE-RECURSOS.json da Biblioteca dos Mestres. A entrevista completa do brief do negócio deixa todo trabalho mais afiado, mas você pode começar um trabalho antes dela: a IA trabalha com o que você fornece, sinaliza o que falta e oferece a entrevista uma vez.

Reutilize o brief aprovado; peça só as entradas que faltam.

Você não chama skill nenhuma. Peça a copy em linguagem natural; o CopyOS aciona sozinho a revisão, a checagem de alegações e o resto. No ChatGPT, se ele não acionar sozinho, digite @ e escolha "Copy de Conversão" na primeira mensagem. No Codex, se precisar, digite `$copy-de-conversao` no começo do pedido. Não pesquise contas conectadas em busca de arquivos de instalação.

Encontre os arquivos de apoio em references/produto/, dentro da sua instalação completa. Faça cópias de trabalho dos templates. Mantenha os resultados neste projeto do negócio, ou baixe-os para o próximo chat.

# CopyOS - Início rápido (a sua primeira saída útil)

Um pipeline: **Voz do Cliente → O Enquadramento → O Banco de Provas → O Motor → O Chefe → As Checagens.**
Funciona para qualquer coisa que você venda: produto, SaaS, serviço, mentoria, agência. Aqui vai a sua primeira passada, de ponta
a ponta, em uma peça real.

## Etapa: alimente a máquina, abasteça o banco

> "Comece do meu brief do negócio aprovado. Reutilize as respostas confirmadas, peça só as entradas de pesquisa que faltam e prepare os prompts de pesquisa e as lacunas do Banco de Provas para este trabalho."

O CopyOS parte do seu brief aprovado e pede qualquer entrada de pesquisa que falte. Depois entrega prompts de deep research prontos para colar que extraem o seu mercado,
a linguagem literal dos seus compradores, os ângulos dos seus concorrentes, e quais das suas alegações são de fato
prováveis. Você cola os prompts; ele faz o raciocínio. Os resultados preenchem o seu dossiê do negócio E o seu
Banco de Provas (`MODELO-DO-BANCO-DE-PROVAS.md` em `3-biblioteca-dos-mestres/`, dentro de biblioteca-dos-mestres em
references/produto/) - o arquivo de evidências até o qual toda linha de copy vai rastrear.

Já está sentado em cima de avaliações, pesquisas ou anúncios vencedores? Cole-os durante o levantamento. Não enfeite: um
banco honesto pela metade vale mais que um inflado, e linhas vazias viram sinalizadores que a máquina se oferece para
pesquisar por você.

## Etapa: defina o Enquadramento

> "Aqui estão meu produto e meu mercado: [contexto]. Rode o Teste de Posicionamento Próprio
> e a Checagem do Inimigo. O que só NÓS podemos dizer, e o que estamos substituindo?"

Salve a saída - ela alimenta todo rascunho a partir daqui.

## Etapa: rode o Motor

> "Rascunhe [a peça de que você realmente precisa - primeira tela de PDP / anúncio / e-mail]
> para [produto], usando o meu Banco de Provas: [cole]. Combine o gancho com o nível de consciência do meu comprador: fato/prova
> verificado para frio, guiado por produto/oferta onde já me conhecem."

Observe o que acontece com as alegações: o que está no seu banco entra como fato. Onde a copy precisa de um fato
que você não forneceu, ela escreve um placeholder nomeado como [sua taxa de resposta] e sinaliza embaixo da
copy, em vez de inventar o número. **Isso é a máquina funcionando.** (Quando você QUISER que ela vá além
da evidência, para fazer brainstorm de mecanismos e ângulos, é só dizer: ela vai com tudo e rotula toda
linha não provada, para que você veja exatamente o que checar antes de qualquer coisa ir ao ar.)

## Etapa: o Chefe, depois as checagens

A passada do Chefe já rodou naquele rascunho antes de você vê-lo. A linha embaixo da copy diz o que ele
corrigiu. Quer a passada completa?

> "Mostre a revisão."

Você recebe um veredito por ponto (APROVADO / APROVADO·anotado / REVISAR / N/A) contra o checklist completo de ofício (ritmo, linguagem simples,
o escorregador, ganchos honestos, sem marcas de IA, o teste do estranho, a tríade do gancho), com correções exatas por
linha e o trecho mais fraco reescrito. Depois:

> "Isto está pronto para publicar? Confira as alegações e faça a checagem final."

Revise a copy final e os sinalizadores antes de publicar. Cada sinalizador vem com a correção específica; você
decide o que vai ao ar.

## Quando você quiser profundidade: a Biblioteca dos Mestres

`3-biblioteca-dos-mestres/` é a biblioteca clássica de resposta direta em 14 volumes (leis da persuasão, diagnóstico de mercado, posicionamento,
ofertas, estruturas, headlines, bullets, prova, linguagem, funis, objeções, otimização, swipes).
Peça ao Motor coisas como *"puxe as fórmulas de headline da Biblioteca dos Mestres para um comprador consciente do problema"* ou leia
você mesmo - o volume 01 é a navegação. O Motor já sabe qual mestre é dono de qual parte de uma
peça (Schwartz para o mercado, Caples para headlines, Masterson e Forde para a abertura, Halbert para
a voz, Sugarman para o fluxo, Bencivenga para o corpo e a prova, Kennedy para o fechamento) e qual
volume guarda a profundidade de cada um. Pergunte *"qual dos grandes cabe nesta parte?"* ou *"escreva a abertura do
jeito que Masterson e Forde escreveriam, dois leads diferentes"*. Leia primeiro `COMO-USAR-ESTA-BIBLIOTECA.md` nessa pasta: o
Biblioteca dos Mestres é ensino de ofício e estrutura, seus exemplos (incluindo estudos e estatísticas nomeados) são
ilustrativos, e as skills instaladas prevalecem sobre ele onde quer que discordem. Os números da sua copy sempre
vêm do SEU Banco de Provas.

## Toda semana depois

- Adicione todo fato verificado novo, gancho vencedor e citação de avaliação ao Banco de Provas - a máquina
  se acumula com ele (o CopyOS mantém tudo conectado).
- Quando aprender uma lição de ofício, diga ao Chefe: *"capture isto como o próximo ponto de contexto"* - a sua
  camada de QA cresce com o seu gosto.
