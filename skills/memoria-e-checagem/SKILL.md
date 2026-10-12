---
name: memoria-e-checagem
description: "Gerencia a memória durável do projeto para que o produto fique mais inteligente sobre o SEU negócio a cada semana. Use ao começar ou terminar trabalho em um projeto; quando uma tarefa revela um fato durável, decisão, restrição, preferência, leitura de desempenho, insight de cliente, mudança de fonte da verdade, workflow ou lição de não-repetir; ao atualizar arquivos de aprendizados, estado atual ou fonte da verdade; ou quando o usuário pede para lembrar, registrar ou levar algo adiante. Funciona em dois modos: modo de sistema de arquivos no Claude Code (grava arquivos reais do projeto, com aprovação) e modo somente-chat no claude.ai ou em qualquer superfície de chat (produz um pacote de memória que o usuário salva e reanexa). Nunca afirma uma persistência automática que não consegue entregar."
---

# Memória e Checagem

## Visão geral

Mantenha a memória do projeto útil, atual e pequena o bastante para ser recuperada. Use um
ciclo rígido de escrever-gerenciar-ler: carregue o contexto certo do projeto antes do trabalho, capture só
aprendizado durável durante o trabalho, e registre depois do trabalho com fonte, confiança e
implicação futura.

Leia `references/modelo-do-sistema-de-memoria.md` para o modelo completo, a tabela de roteamento, os limiares de
atualização e as regras de aplicação.

## Dois modos de persistência. Declare o seu primeiro.

Memória só existe se cair em algum lugar que uma sessão futura vai de fato ler. O que esse
"algum lugar" é depende da superfície, então, na primeira vez que esta skill roda em um projeto,
declare qual modo está ativo:

- **filesystem_mode** (Claude Code, Codex ou qualquer ferramenta com acesso a arquivos): a memória vive em
  arquivos reais dentro da pasta do projeto do usuário. As gravações acontecem só depois que o usuário aprova
  o caminho de destino, e a primeira gravação em um projeto novo roda o bootstrap abaixo.
- **chat_only_mode** (claude.ai ou qualquer superfície de chat sem acesso a arquivos): você não consegue
  gravar no sistema de arquivos do usuário, e nunca deve dar a entender que consegue. Em vez disso, encerre a
  sessão produzindo um `MEMORY_UPDATE_PACKET`: um único bloco markdown cercado contendo
  as entradas de memória novas ou alteradas, pronto para o usuário copiar nos arquivos do projeto,
  adicionar ao conhecimento do Projeto ou reanexar na próxima sessão. A persistência é uma ação do usuário;
  seu trabalho é fazer dela uma ação de dez segundos.

Nunca afirme persistência automática em chat_only_mode. "Vou lembrar disso" é uma afirmação
falsa ali; "aqui está o pacote para salvar" é a verdadeira.

## Bootstrap (filesystem_mode, primeira execução em um projeto)

Se o projeto ainda não tem estrutura de memória, ofereça criar a árvore mínima antes da
primeira gravação, e crie só depois da aprovação, rodando de novo o auxiliar com
`--bootstrap` (sem aprovação o auxiliar recusa raízes que não pareçam um
projeto). A árvore que ele cria:

```text
context/
  project/
    current-state.md      o que é verdade agora, com data
    source-of-truth.md    quais fontes têm precedência sobre quais, e onde vivem
  learnings/
    index.md              uma linha por arquivo de aprendizado, o que vive onde
    <domain>-learnings.md criado no primeiro uso por domínio
```

Mantenha o bootstrap mínimo. Não crie esqueleto de pastas que o projeto ainda não precisou.

## Ciclo obrigatório

### 1. Leia antes do trabalho

Identifique o projeto primeiro. Depois leia, nesta ordem: o arquivo operacional do projeto
(`AGENTS.md` ou equivalente) se existir, o `BUSINESS-MEMORY.md` aprovado se existir (ele é dono dos fatos
do negócio; encaminhe mudanças neles de volta pelo briefing-inteligente, não os copie aqui),
`context/project/current-state.md`,
`context/project/source-of-truth.md`, `context/learnings/index.md` e o arquivo de aprendizado
do domínio relevante. Em chat_only_mode, peça o pacote de memória ou os arquivos de contexto anexados
no lugar, e diga com clareza o que está faltando se nenhum for fornecido.

Separe o contexto durável em duas camadas: contexto de marca/projeto (verdade do produto, oferta,
mercado, linguagem do cliente, dados de desempenho, restrições, decisões) pertence à memória do
projeto; doutrina de domínio reutilizável pertence às skills. Se um aprendizado pertence às duas,
escreva a versão específica do projeto na memória e anote a regra reutilizável para a skill.

### 2. Filtre durante o trabalho

Salve memória só quando ela for mudar o comportamento futuro. Memória relevante inclui:

- preferência ou correção do usuário
- restrição de produto, oferta, estrutura de preço, estoque, lançamento ou conformidade
- resultado de desempenho, leitura de campanha, criativo vencedor ou perdedor, sinal de fadiga, ou uma
  decisão de ciclo de vida que foi de fato tomada
- insight de cliente ou de voz do cliente
- decisão de site, conversão ou design
- workflow que deve ser repetido
- lição de não-repetir
- mudança de fonte da verdade ou de roteamento de arquivos
- restrição de integração, localização de credencial ou operação (localizações, nunca valores)

Não salve formatação trivial, limpeza mecânica, saída de comando pontual, leituras exploratórias
sem conclusão, ou palpites sem evidência.

### 2B. Capture rastros de raciocínio

Quando uma decisão estratégica, correção de hipótese ou regra de contexto muda o trabalho futuro,
capture o rastro de raciocínio, não só o fato final: a decisão tomada, a suposição anterior,
o gatilho de evidência, por que a mudança é melhor, o que ela afeta, a implicação
futura, e a confiança e a fonte. Rastros importam mais em estratégia criativa,
porque ensinam às sessões futuras por que uma decisão de persona, ângulo, orçamento ou ciclo de vida
foi tomada daquele jeito.

### 2C. Rotule a evidência

Use os rótulos canônicos de evidência em todo este produto quando a atualidade da fonte
afetar uma decisão:

- `verified-current`: confirmado por uma extração ao vivo, exportação recente ou fonte canônica
  atual nesta tarefa.
- `local-snapshot`: sustentado por um relatório ou exportação local datado que pode ficar defasado.
- `memory-derived`: extraído da memória durável mas não reverificado nesta tarefa.
- `source-claim`: declarado por uma fonte externa nomeada (documentação de plataforma, um
  praticante, um estudo de caso); é verdade que eles disseram, não verificado aqui.
- `inference`: deduzido a partir de evidência, não declarado diretamente por uma fonte.
- `assumption`: suposição de trabalho necessária; exponha antes de depender dela.
- `unavailable`: o dado não existe nesta conversa; diga isso, nunca substitua por
  um valor plausível.

Uma hipótese não é um rótulo: ela é um `inference` ou `assumption` mais um teste nomeado e
um falsificador. Quando uma falha ou uma correção repetida muda o comportamento futuro, guarde como
padrão de falha: `sintoma / causa / correção / onde verificar em seguida`.

### 3. Escreva depois do trabalho

**filesystem_mode:** para um aprendizado padrão, use o script auxiliar da pasta da skill
instalada, sempre com uma raiz de projeto explícita e um dry run primeiro:

```bash
python3 <caminho-da-skill-instalada>/scripts/adicionar_memoria_do_projeto.py \
  --project-root /caminho/absoluto/para/seu/projeto \
  --domain performance \
  --type decision \
  --title "Título curto e durável" \
  --source "de onde isto veio" \
  --confidence high \
  --learning "Fato durável e preciso." \
  --implication "O que as sessões futuras devem fazer diferente." \
  --affected "os workflows que isto muda" \
  --dry-run
```

O dry run não altera nada: ele imprime os caminhos de destino exatos e a entrada proposta
completa como um patch revisável. Revise, depois rode de novo sem `--dry-run` quando o usuário
aprovar. O script recusa raízes ausentes ou amplas demais (`/`, o diretório home,
diretórios de configuração de ferramentas), recusa pastas que não são projeto a menos que `--bootstrap` seja aprovado,
remove quebras de linha e estrutura Markdown dos campos armazenados para que a entrada não consiga injetar
títulos ou instruções, grava atomicamente, reverte o arquivo de aprendizado se a atualização do índice
falhar, e recusa conteúdo que pareça um segredo. Para mudanças de fonte da verdade, atualize o
arquivo canônico diretamente e adicione um ponteiro de aprendizado só se o comportamento futuro mudar.
Se `python3` não estiver disponível nesta máquina, escreva a entrada manualmente, seguindo o mesmo
formato que o script produziria (título, data, fonte, confiança, aprendizado, implicação), no arquivo de
aprendizado do domínio, mais uma linha correspondente em `context/learnings/index.md`.

**chat_only_mode:** monte o `MEMORY_UPDATE_PACKET` no lugar, com um bloco por
entrada (data, domínio, tipo, título, aprendizado, implicação, fonte, confiança, rótulos),
mais uma instrução de uma linha dizendo ao usuário onde cada entrada pertence.

### 4. Gerencie conflitos

Se uma informação nova conflita com a memória existente: preserve os dois fatos até resolver;
marque a regra mais antiga como substituída ou condicional, nunca apagada em silêncio; cite a fonte
mais forte e a data; atualize a fonte da verdade quando a própria hierarquia de confiança mudar.

### 5. Aplique o fechamento

Antes da resposta final em trabalho de projeto, verifique: esta tarefa criou memória durável?
Se sim, ela foi gravada (ou empacotada) no lugar certo? Se não, é porque o trabalho
foi mecânico ou exploratório? Mencione as atualizações de memória brevemente quando feitas. Não faça
atualizações barulhentas só para mostrar atividade.

## Domínios do projeto

- `copy`: voz, alegações, ganchos, frases aprovadas.
- `creative`: peças visuais, direção criativa, regras de produção.
- `performance`: mídia paga, analytics, leituras de eficiência, decisões de ciclo de vida tomadas.
- `product-offer`: fatos do produto, estrutura de preço, pacotes, estoque, escopo de conformidade.
- `site-cro`: decisões de loja, página e conversão.
- `customer-voc`: pesquisas, avaliações, objeções, linguagem do comprador, insights de suporte.
- `ops`: localizações de integração, caminhos de repositório, workflows, mapas de fontes (nunca valores secretos).

## Abastecendo o banco de provas

O trabalho de copy e criativo a jusante neste produto roda sobre evidência verificada: alegações,
estatísticas, citações de clientes e ganchos vencedores precisam rastrear até uma fonte, e uma prova
ausente vira um [placeholder] nomeado mais um sinalizador, nunca um valor inventado. Seu trabalho aqui é abastecer esse
banco de provas: capture fatos verificados, pontos de prova, linguagem do cliente e ganchos vencedores
COM suas fontes nos arquivos de fonte da verdade e de aprendizado do projeto, e marque
qualquer coisa não verificada como não verificada. Nunca passe adiante uma alegação de concorrente, uma estatística raspada ou
um mecanismo presumido como fato estabelecido. Aberturas guiadas por prova são preferidas onde
o canal e a evidência se encaixam; elas são um padrão forte, não uma lei que passa por cima do
julgamento sobre o comprador e o formato.

## Como o usuário fala com o CopyOS

O usuário conversa com o CopyOS, não com skills. Esta skill é carregada pela porta de entrada (`copy-de-conversao`) ou diretamente pelo host quando o pedido a aciona; nos dois casos, faça o trabalho sem pedir ao usuário para "usar", "selecionar" ou "chamar" skill nenhuma, e sem citar nomes de skill na resposta: descreva pelo que faz. Quando precisar de outra skill do CopyOS, carregue-a você mesma pela ferramenta de skills do host. Se ela não estiver disponível, diga em uma linha qual arquivo falta instalar e continue com o que dá.

## Instalação completa e continuidade do negócio

Use a skill briefing-inteligente instalada para uma checagem de instalação quando for pedido, depois de uma atualização, ou quando um componente obrigatório estiver faltando. **O pedido atual do usuário vem primeiro.** Quando ele pedir um trabalho, faça esse trabalho agora com o que está disponível (o brief salvo se houver, o chat, e sua melhor suposição rotulada para o resto). Liste os fatos do brief que estão faltando nos sinalizadores e ofereça a entrevista do negócio uma vez, como uma linha de sinalizador. Nunca segure o trabalho para rodar a entrevista ou uma checagem de instalação primeiro. Carregue o BUSINESS-MEMORY.md confirmado deste projeto antes de perguntar por fatos. Pergunte só o que está faltando ou é específico do produto. Mantenha os requisitos próprios desta skill; a camada de onboarding não os substitui. Localize os arquivos originais de apoio na skill biblioteca-dos-mestres correspondente em references/produto nas instalações de pacote completo. Retome o checkpoint salvo do negócio ao voltar. Nunca misture projetos de clientes nem afirme memória persistente sem arquivos de fato salvos ou anexados.
