# Capturas de tela

Só entram em processos com tela (app, site, sistema). A captura mostra **onde clicar e o que a pessoa vai ver**: é o que mais evita que alguém trave. Processo sem tela não tem captura. Nesse caso, use tabela, árvore de pastas ou exemplos prontos.

## O que capturar
- A tela de entrada (login ou início), para a pessoa saber que chegou ao lugar certo.
- Todo formulário que ela precisa preencher, já preenchido com um exemplo realista.
- O momento de "deu certo" (mensagem de concluído, resultado na tela).
- Os botões de uma etapa importante, recortados de perto.

Uma captura por momento-chave basta. De 3 a 8 por playbook costuma ser o suficiente; captura demais atrasa a leitura e pesa o arquivo.

## Formato
- JPEG com qualidade ~84, janela de 1440 × 900 e recorte com ~16 px de margem em volta do que importa.
- Nome `NN-chave.jpg` (ex.: `01-login.jpg`, `04-formulario.jpg`). No texto, `data-shot="login"`: a chave é o nome sem o número e sem a extensão.
- Guarde as capturas numa pasta `capturas\` ao lado do playbook. O `montar.mjs … --capturas "<pasta>"` embute tudo dentro do HTML, e a pasta fica para quando precisar refazer uma imagem.
- Acima de ~450 KB por imagem, o montar avisa: recorte melhor ou baixe a qualidade.

## De onde vêm
1. **Prints que o usuário mandar.** Renomeie para `NN-chave.jpg` e use `--capturas`.
2. **App web que roda no computador** (localhost): copie `scripts/capturar-telas.mjs` para uma pasta de rascunho do projeto que tenha o `playwright-core` instalado. Edite só a parte ROTEIRO no fim e rode `node capturar-telas.mjs "<pasta de saída>"`. Ele usa o Chrome instalado, sem janela, e bloqueia tudo que não for localhost.
3. **Sem como capturar agora:** escreva o playbook sem as figuras, entregue e diga quais capturas faltam e onde entram.

## Cuidados
- **Nada de dado real sensível na imagem**: senha, token, e-mail pessoal, dado de cliente. Use contas e exemplos de teste.
- **Não gaste créditos nem mexa em contas reais para capturar.** Simule as respostas da API com `ctx.route` (tem um exemplo no script). O playbook do JEV Lab reproduziu uma extração inteira a partir de um CSV já exportado, sem abrir o Instagram e sem chamar IA.
- Capture com a tela no estado que a pessoa vai encontrar no uso normal (sem avisos de modo de desenvolvimento, por exemplo).
