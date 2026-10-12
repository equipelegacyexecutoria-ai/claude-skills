# O CONTRATO DE SAÍDA (formato exato, sem desvios)

Depois da entrevista completa e da confirmação do usuário, produza dois artefatos nesta ordem, cada um em seu próprio bloco de código cercado, para copiarem limpos. Uma sessão pausada produz um checkpoint claramente rotulado INCOMPLETO, não estes artefatos finais.
Antes de escrever qualquer coisa, rode o 03-DIAGNOSTICO-DE-RESTRICAO.md em privado e escolha UMA
restrição.

## Regras de marcação (aplique em toda parte, nos dois artefatos)

- **COMPROVADO**: sustentado por evidência que o dono de fato possui (um número que ele pode mostrar, um
  depoimento com permissão, uma certificação). Seguro para usar em marketing.
- **NÃO COMPROVADO**: acreditado, mas ainda sem sustentação. A copy pode carregá-lo com força total com um
  [placeholder] nomeado para a prova que falta e uma flag; nunca o apresente como comprovado, e nunca o promova
  em silêncio a COMPROVADO.
- **DESCONHECIDO**: o dono disse que não sabe. Escrito como DESCONHECIDO, nunca adivinhado.
- **[aproximado]**: uma faixa ou estimativa que o dono deu. Mantida como dada, nunca estreitada.
- **[planejado]**: intenção pré-lançamento, não realidade operacional.
- **EM ABERTO**: pergunta ainda não alcançada num checkpoint incompleto. Lista a pergunta para que qualquer IA (ou
  o dono) saiba exatamente o que coletar em seguida.
- Linhas de voz do cliente aparecem entre "aspas duplas", literais, com os erros de digitação mantidos.

## ARTEFATO 1: BUSINESS-MEMORY.md

Estrutura, exatamente estas seções, nesta ordem:

```
# MEMÓRIA DO NEGÓCIO: {nome do negócio ou descritor do dono}
Gerado por briefing-inteligente em {data}.
Como usar: cole este arquivo inteiro sempre que um sistema de marketing com IA perguntar sobre o seu
negócio. As skills do CopyOS o leem antes de pedir fatos do negócio. Marcações: alegações COMPROVADAS
são seguras para marketing; linhas NÃO COMPROVADAS são sinalizadas, nunca apresentadas como comprovadas; DESCONHECIDO e EM ABERTO são lacunas honestas
que vale preencher, não espaços em branco para adivinhar.

## O NEGÓCIO
Em uma linha: {Q1, enxuta mas fiel}
Modelo: {tipo} | Em operação há: {idade} | Equipe no marketing: {Q16 quem + horas}
Canais hoje: {divisão da Q3}
Ferramentas em uso: {ferramentas da Q16}

## OS NÚMEROS
Últimos 30 dias: {receita [aproximado]} em {pedidos/clientes [aproximado]}
Oferta principal: {nome/descritor} a {preço}, custo para entregar {Q5} => margem {calculada
só se os dois números foram dados; caso contrário DESCONHECIDO}
Tráfego pago: {plataforma + verba mensal, ou "nenhum"} | Custo por cliente novo: {valor
ou DESCONHECIDO}
Lista: {tamanho}, disparos {frequência} | Participação da receita recorrente: {valor ou DESCONHECIDO}

## O COMPRADOR
A pessoa: {Q8, concreta}
O gatilho: {o momento que a faz passar de olhar a comprar}
Usava no lugar: {Q9}
A objeção mais ouvida: "{Q10 literal se dada como citação, senão resumo}"

## VOZ DO CLIENTE (literal, não limpe)
- "{citação 1}"
- "{citação 2}"
- "{citação 3 se dada}"

## A OFERTA
A promessa: {Q12}
Reversão de risco: {Q14, incluindo se é exibida}
A diferença honesta: {Q15, incluindo "paridade por enquanto" se essa foi a resposta}

## O BANCO DE PROVAS
COMPROVADO (usável em marketing hoje):
- {cada item comprovado, uma linha cada; escreva "vazio por enquanto" se nenhum}
NÃO COMPROVADO (acreditado, ainda sem sustentação; usável com um placeholder nomeado e uma flag, nunca como comprovado):
- {cada item}

## METAS E LIMITES
Número de 90 dias: {Q17}
Diagnóstico do próprio dono: "{Q18 literal}"
Limites rígidos: {Q19}

## EM ABERTO
- {todo item EM ABERTO/DESCONHECIDO como uma tarefa de coleta de uma linha, ex.: "Custo por cliente
  novo: conferir as compras do Gerenciador de Anúncios contra Stripe/banco nos mesmos 30 dias"}
```

Regras:
- Nada aparece no arquivo que o dono não tenha dito. Ajustar gramática é permitido;
  adicionar fatos, não.
- Não calcule nada além da linha de margem, e só a partir de dois números que ele deu.
- Se a Q11 não produziu citações, a seção VOZ DO CLIENTE diz: "Nenhuma coletada ainda.
  Primeiro preenchimento: puxe as últimas 10 avaliações/DMs e cole as linhas que mencionam um sentimento
  ou uma situação." Nunca invente citações.

## ARTEFATO 2: O CARTÃO DE RESTRIÇÃO

```
# O CARTÃO DE RESTRIÇÃO
Negócio: {em uma linha, forma curta}

A RESTRIÇÃO: {uma das nove, do 03-DIAGNOSTICO-DE-RESTRICAO.md}
Em palavras simples: {uma frase, segunda pessoa, sem jargão}

A EVIDÊNCIA (das suas próprias respostas):
- {2 a 4 bullets citando ou referenciando as respostas dele}

O QUE PROVARIA QUE ISTO ESTÁ ERRADO: {uma frase de falseamento}

A ÚNICA JOGADA DESTA SEMANA: {uma única ação concreta, realizável em menos de uma semana com o que
ele já tem. Uma ação, não uma compra.}

AONDE ISTO LEVA: {a linha de roteamento conforme a tabela de roteamento do 03: ou a ÚNICA
skill do CopyOS correspondente e uma frase honesta sobre por que ela se encaixa (sem preço),
ou a afirmação simples de que esta restrição está fora do escopo do CopyOS e a próxima ação útil sem compra.}
```

Regras:
- UMA restrição. Se estiver dividido entre duas, as regras de desempate do 03 decidem; se ainda
  dividido, é "medição" por definição (você não consegue enxergar com clareza suficiente para saber).
- A ÚNICA JOGADA nunca exige comprar nada, de ninguém.
- O diagnóstico do próprio dono (Q18) precisa ser tratado: uma linha concordando, ou uma linha
  explicando respeitosamente por que a evidência aponta para outro lugar.

## O FECHAMENTO (depois dos dois blocos, três linhas curtas, sem bloco de código)

1. O que fazer com o arquivo: salve-o, cole-o sempre que um sistema de marketing com IA perguntar
   sobre o negócio; as skills do CopyOS o leem antes de pedir fatos do negócio e pulam
   as perguntas da entrevista que você já respondeu aqui.
2. A única jogada, reafirmada em uma frase simples.
3. Volte e rode esta entrevista de novo quando os números mudarem; o arquivo deve ser
   gerado de novo, não remendado à mão.

---

## EXEMPLO TRABALHADO (só para calibração; nunca mostre nem reutilize o conteúdo dele)

Entrevista: loja de velas, 14 meses de vida, 8-11 mil/mês [aproximado] de ~140 pedidos, produto
principal a 42 com custo total de 14, verba na Meta de 2 mil/mês com CPA DESCONHECIDO ("a Meta diz 19 mas
o Shopify não bate"), lista de 2.300 com disparos "quando eu lembro", participação recorrente DESCONHECIDA.
Compradora: "uma mãe que acabou de se mudar, comprando para fazer a casa nova parecer dela." Principal
objeção literal: "como eu sei que não vai cheirar a falso como as da Target". Citações
coletadas: "queimei a semana inteira no apartamento novo", "o frete levou 9
dias e eu quase cancelei". Promessa: "uma vela que enche a sala de verdade".
Prova: COMPROVADO 4,8 estrelas em 312 avaliações; NÃO COMPROVADO "projeção de aroma mais forte que qualquer
grande marca". Garantia: reembolsos dados em silêncio, exibidos em lugar nenhum. Diferença: paridade honesta,
exceto a alegação de carga de aroma (não comprovada). Meta: primeiro mês de 15 mil. Diagnóstico do dono:
"Acho que preciso de mais anúncios." Limites: verba máxima de 2,5 mil/mês, sozinho, 6 h/semana.

Cartão correto para essa entrevista:

- RESTRIÇÃO: medição (a verba está rodando, CPA desconhecido, plataformas discordam; participação
  recorrente desconhecida com uma lista de 2.300). NÃO "mais anúncios": escalar verba com um CPA
  desconhecido sobre uma margem de 28 é aposta, o que responde respeitosamente ao diagnóstico do
  próprio dono.
- EVIDÊNCIA: Meta 19 vs. Shopify não bate; participação recorrente desconhecida; lista com disparos raros.
- FALSEAMENTO: uma leitura limpa de 30 dias em que as compras do Gerenciador de Anúncios batem com os pedidos da loja
  dentro de 15% resolveria.
- ÚNICA JOGADA: escolher o último mês completo, contar os pedidos reais de clientes novos no back-end
  da loja, dividir a verba por esse número. Um CPA verdadeiro antes de qualquer mudança de orçamento.
- ROTEAMENTO: copy-de-conversao NÃO é a correspondente, apesar de o dono pedir mais anúncios;
  medição fica fora do escopo do CopyOS. Linha correta: fora do escopo do CopyOS; a próxima
  ação útil sem compra é repetir esta reconciliação banco vs. plataforma toda semana até os números
  baterem. Uma linha, uma frase, sem preço.
