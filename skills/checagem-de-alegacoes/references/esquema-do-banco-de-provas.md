# Banco de Provas - Esquema e Fluxo de Trabalho

O Banco de Provas é o repositório por projeto de evidências verificadas de onde a Camada Prova-ou-Pergunta puxa. Objetivo: todo gancho/estatística/alegação/prova que afirma um fato vem daqui (qualquer outra coisa é um placeholder nomeado ou uma flag), e toda passada de pesquisa deposita aqui para que o banco se acumule.

## Onde vive
Por projeto, em `context/project/`. Local preferido: `context/project/proof-bank.md` (crie se não existir), com referência cruzada a `source-of-truth.md`, `audience-voc.md`, `products-offers.md` e qualquer pasta `*claim-research*`. Mantenha via `**memoria-e-checagem**`.

## Esquema de entrada
Uma linha por item verificado:

```
| id | alegação/fato | valor/redação | faixa (V/A/AD/R: Verde, Amarelo, Aprovado pelo Dono, Vermelho) | nível de evidência | fonte (arquivo/URL + data) | mercado | usável como | status |
```

- **nível de evidência:** 1 = dado primário / laboratório / especificação / recibo / avaliação real; 2 = fonte secundária respeitável; 3 = inferência (rotule como inferência); nunca nível 0 (presumido) em uso voltado ao cliente.
- **faixa:** de `modelo-semaforo-de-alegacoes.md`.
- **usável como:** gancho / headline / linha de prova / FAQ / sobreposição / assunto de e-mail.
- **status:** verificado (com data) / expirado / precisa de rechecagem. Estatísticas e fatos de estado atual expiram - verifique de novo antes de reutilizar.

## Fluxo de trabalho
1. **Consulte:** antes de escrever, puxe do banco ganchos/provas candidatos para o ângulo.
2. **Lacuna → flag:** se o fato necessário não está lá ou está expirado/inverificável, continue escrevendo: use um placeholder nomeado na linha (`[sua taxa de resposta]`) ou sinalize a alegação, e nomeie o jeito mais barato de obter o fato (pacote de prompts de pesquisa, Reddit/VOC, mineração de avaliações, comprovação de alegação). Nunca fabrique e apresente como real.
3. **Deposite:** quando pesquisa/dissecação/avaliações revelarem um fato verificado ou um gancho vencedor, escreva-o de volta com a fonte e a faixa. É assim que o banco evita que você pergunte duas vezes.
4. **Registro de ganchos vencedores:** mantenha os ganchos comprovados (com o fato verificado por trás + sinal de desempenho) para que peças futuras reutilizem o que funciona.

## Antipadrões
- Tratar a alegação de um concorrente ou uma estatística raspada como fato → precisa ser verificada e sustentada por fonte de forma independente antes de entrar no banco como nível 1–2.
- Arredondar/melhorar um número para soar melhor → isso é fabricação.
- Deixar o banco apodrecer → uma estatística expirada apresentada como atual é um dado inventado; sinalize alto.
