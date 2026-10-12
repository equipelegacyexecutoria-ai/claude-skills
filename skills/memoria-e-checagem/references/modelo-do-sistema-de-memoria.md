# Modelo do Sistema de Memória do Projeto

## Base das fontes

Esta skill combina:

- Modelo de engenharia de contexto: tratar a janela de contexto como memória de trabalho escassa e projetar o que entra nela.
- Prática de memória de projeto para agentes: regras obrigatórias de carregar-antes-do-trabalho e salvar-depois-do-trabalho com arquivos de memória dedicados.
- Design de memória em camadas: separar memória de usuário/projeto/procedimento, revelação progressiva, tratamento seguro de segredos e consolidação.
- Pesquisa atual sobre memória de agentes: ciclos de escrever-gerenciar-ler, tratamento de contradições, proveniência e memória hierárquica em markdown.

Isso é destilado da prática atual de engenharia de contexto e memória de agentes; o
modelo se sustenta sozinho e não precisa de leitura externa para operar.

## Camadas de memória

### 1. Memória de trabalho

Thread atual, plano da tarefa, saídas recentes de ferramentas e suposições temporárias. É volátil. Não confie nela entre sessões a menos que esteja gravada em um arquivo durável.

### 2. Contexto estático do projeto

`AGENTS.md`, `context-map.md`, `context/project/current-state.md` e `context/project/source-of-truth.md`. Esta é a sequência de boot do projeto. Ela diz aos agentes onde a verdade vive e quais fontes têm precedência sobre outras.

### 3. Aprendizados duráveis

`context/learnings/*.md` mais `context/learnings/index.md`. Esta é a memória comportamental corrente: decisões, erros, resultados, preferências e regras de não-repetir que devem alterar o trabalho futuro.

### 4. Arquivos-fonte canônicos

Arquivos de produto/oferta, arquivos derivados de fonte da verdade, snapshots de dados ao vivo, notas de design, mapas de rotas de peças e arquivos do repositório. Estes não são resumidos para fora quando a evidência exata importa.

### 5. Memória de índice externo

Se você mantém um índice externo (Notion ou similar), trate-o como camada de índice e recuperação, não como fonte de execução. Espelhe ali resumos concisos, caminhos locais, decisões e registros de workflow quando disponível, mas mantenha a evidência exata e o código em arquivos locais.

### 6. Arquivos mortos

Exportações antigas e relatórios arquivados. Use para evidência e histórico, mas não deixe que passem por cima do contexto atual a menos que os mapas de fontes atuais apontem para eles.

## Ciclo escrever-gerenciar-ler

### Ler

Carregue contexto mínimo, mas suficiente:

1. identidade do projeto e inegociáveis
2. estado atual
3. hierarquia de confiança
4. índice de aprendizados recente
5. aprendizado do domínio relevante
6. arquivos-fonte exatos só conforme necessário

### Escrever

Capture memória com:

- data
- título
- tipo de memória
- caminho da fonte ou URL
- confiança
- aprendizado preciso
- implicação futura
- skills/workflows afetados

### Gerenciar

Consolide periodicamente:

- mescle duplicatas
- marque regras substituídas
- arquive entradas obsoletas e não repetidas
- mantenha as regras atuais de alto impacto perto do topo
- atualize os mapas de fontes quando as localizações canônicas mudarem

Nunca apague memória durável sem trilha de arquivamento.

## Guia de tipos de memória

- `fact`: fato estável de projeto/produto/fonte.
- `decision`: decisão do usuário ou do negócio.
- `preference`: preferência do usuário ou correção de gosto.
- `result`: desempenho, teste ou resultado.
- `constraint`: restrição legal, de alegação, SKU, lançamento, estoque, plataforma ou API.
- `workflow`: procedimento reutilizável.
- `do-not-repeat`: abordagem que falhou ou correção explícita.
- `source-change`: arquivo canônico, repositório, peça ou hierarquia de confiança mudou.
- `design-system`: regra de token/componente/layout.
- `integration`: atualização de API, MCP, automação, localização de credencial ou ferramenta.

## Regras de confiança

- `high`: sustentado por arquivo, saída de API, decisão do usuário ou implementação verificada.
- `medium`: inferência forte a partir de múltiplas fontes, mas não confirmada diretamente.
- `low`: hipótese útil; escreva só se evitar confusão repetida e rotule com clareza.

Não guarde palpites de baixa confiança como fatos.

## Rótulos de status da evidência

Use estes rótulos quando a atualidade da fonte afetar uma recomendação estratégica, de relatório, mídia paga, CRO, prontidão de lançamento, automação ou fonte da verdade:

- `verified-current`: confirmado por uma extração de API ao vivo, contexto gerado recente ou fonte canônica atual na tarefa atual.
- `local-snapshot`: sustentado por um relatório, resumo, exportação ou contexto gerado local e datado que pode ficar defasado.
- `memory-derived`: extraído da memória durável mas não reverificado na tarefa atual.
- `inference`: deduzido a partir de evidência, mas não declarado diretamente por uma fonte.
- `source-claim`: declarado por uma fonte externa nomeada (documentação de plataforma, um praticante, um estudo de caso); é verdade que eles disseram, não verificado aqui.
- `assumption`: suposição de trabalho necessária; exponha antes de depender dela.
- `unavailable`: o dado não existe nesta conversa; diga isso e nunca substitua por um valor plausível.

Uma hipótese não é um rótulo de proveniência: ela é um `inference` ou `assumption` mais um teste nomeado e um falsificador.

Não use os rótulos como cerimônia. Use-os onde evitam que evidência defasada, suposições escondidas ou confiança sem sustentação dirijam uma decisão.

## Contrato de padrão de falha

Quando uma abordagem falha repetidamente, uma correção do usuário revela um erro recorrente, ou uma correção levou mais de duas tentativas, capture o padrão de falha reutilizável no arquivo de aprendizado relevante:

```text
sintoma: ...
causa: ...
correção: ...
onde verificar em seguida: ...
```

Este é o equivalente de projeto de um arquivo `ERRORS.md`. Mantenha dentro de `context/learnings/` para que continue roteado por projeto/domínio em vez de virar mais um arquivo de memória órfão.

## Checagens de abordagem e de passagem de bastão

Não peça opções antes de execução rotineira. Use uma checagem de seleção de abordagem só para mudanças de alto impacto: religação de fonte da verdade, contratos de schema/relatório, integrações ao vivo, comportamento de automação, lógica de decisão de campanha, edições irreversíveis de dados ou refatorações amplas. Apresente 2-3 opções concretas e espere, a menos que o usuário já tenha escolhido a direção.

Quando o usuário disser `session end`, `stop here`, `pause here`, `continue later` (ou "fim de sessão", "pare aqui", "pausa aqui", "continuo depois"), crie uma passagem de bastão compacta antes de parar:

- concluído
- em andamento
- próximo arquivo/ferramenta a abrir
- bloqueios
- o que não refazer

## Tabela de roteamento

| Memória | Arquivo |
|---|---|
| Voz/copy/alegações/ganchos | `context/learnings/copy-learnings.md` |
| Visual/UGC/imagem/vídeo/mídia de produto | `context/learnings/creative-learnings.md` |
| Anúncios/relatórios/Meta/Google Ads/ROAS | `context/learnings/performance-learnings.md` |
| Fatos do produto/preço/pacotes/rótulos/SKUs/estoque | `context/learnings/product-offer-learnings.md` |
| PDP/site/CRO/UX/implicações de design system | `context/learnings/site-cro-learnings.md` |
| Avaliações/pesquisas/VOC/objeções/linguagem do comprador | `context/learnings/customer-voc-learnings.md` |
| APIs/repositórios/workflows/automações/mapas de fontes | `context/learnings/ops-learnings.md` |
| Regras de design visual que devem governar a UI futura | o arquivo de notas de design do projeto mais um aprendizado `site-cro` ou `creative` |
| Mudanças na hierarquia de confiança ou em fonte canônica | `context/project/source-of-truth.md` mais um aprendizado `ops` |

## Limiar de atualização

Atualize a memória quando pelo menos um for verdadeiro:

- Agentes futuros repetiriam um erro sem isso.
- O usuário corrigiu uma suposição.
- Um fato canônico mudou.
- Uma localização de fonte mudou.
- Um resultado testado afeta decisões.
- Um workflow deve ser reutilizado.
- Uma regra de design/sistema deve governar o trabalho futuro.

Não atualize quando:

- o trabalho foi puramente mecânico
- o achado já está capturado
- o fato é temporário e óbvio a partir do arquivo alterado
- a evidência é fraca demais e não afeta o comportamento

## Checklist de aplicação

Use antes da resposta final:

```text
Projeto identificado?
AGENTS/estado atual/fonte da verdade verificados quando relevante?
Índice de aprendizados e arquivo do domínio verificados?
Memória durável nova criada?
Se sim: arquivo canônico atualizado?
Se sim: arquivo de aprendizado e índice atualizados?
Se conflito: regra mais antiga marcada como substituída/condicional?
Segredos evitados?
Resposta final menciona atualização de memória ou ausência de atualização durável?
```
