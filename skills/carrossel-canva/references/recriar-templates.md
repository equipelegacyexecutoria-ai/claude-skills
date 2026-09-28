# Recriar os templates-mestre (só se sumirem ou for outra conta do Canva)

Antes de recriar: `search-designs` com `"TEMPLATE CARROSSEL"`. Se achar (LEGACY = 5 páginas
1080×1440; CLAILTON = 3 páginas 1080×1350), só atualizar os IDs em `template.md`.
Outra conta do Canva: o dono compartilha os dois templates (Compartilhar, com edição) e a skill acha
pelo nome. Recriar é o último recurso.

Regras que valem para tudo abaixo (testadas):
- `merge-designs`: **uma operação por chamada**.
- Trocar cada texto pelo marcador com `find_and_replace_text` **dentro de um único trecho** e **sem
  `\n` no texto novo** (apagar `\n` pode; inserir cria parágrafo que herda o estilo do anterior).
- Mostrar a prévia e só dar `commit` com o ok do usuário.

## LEGACY (a partir de "SER DONO É SABER COBRAR | LEGACY" `DAHWCDizSTE` e "5 MATÉRIAS…" `DAHWJAVgBic`)

1. `merge-designs create_new_design`, título `TEMPLATE CARROSSEL | LEGACY`, `insert_pages` de
   `DAHWCDizSTE` páginas `[1, 2, 10, 11]` (capa, corpo, CTA, bônus).
2. `merge-designs modify_existing_design` no design novo: `insert_pages` de `DAHWJAVgBic` página `[3]`
   com `after_page_number: 2` → ordem final: 1 capa · 2 corpo · 3 corpo com título · 4 CTA · 5 bônus.
3. `read-design` com `open_transaction` para pegar os `locator_id`.
4. Marcadores (texto original → marcador):

| Pág. | Texto original | Marcador |
| --- | --- | --- |
| 1 | `Deixa eu te falar ` · `uma verdade que dói:` · `SER DONO É SABER COBRAR.` | `{{H1}}` · `{{H2}}` · `{{H3}}` |
| 2 | `Se o seu sonho é ser o queridinho da equipe, você abriu o negócio errado.` | `{{BRANCO}}` |
| 2 | `Empresa não se toca na base \ndo "todo mundo me ama".` | `{{CINZA}}` |
| 2 | depois: `update_text_anchoring` `end` e `position_element` top = 1290 − altura do texto (com marcadores: top 1079, left 64.22) | — |
| 3 | `1. Leitura financeira.` · o corpo inteiro do card | `{{TITULO}}` · `{{CORPO}}` |
| 4 | `E não é culpa sua se a cobrança nunca vira resultado.` | `{{TITULO}}` |
| 4 | `Você aprendeu a fazer e a vender, \na criar o processo e o ritmo de cobrança que sustentam a exigência. Por isso você cobra, cobra, e o padrão não sobe.` | `{{P1}}` |
| 4 | `Cobrar todo dia cansa. \nCobrar com estrutura faz o padrão subir sozinho.` | `{{P1B}}` |
| 4 | `É isso que a nossa executoria faz.` | `{{A1}}` |
| 4 | `A gente entra dentro … tempo todo. \n\nFoi essa virada que já mudou a realidade de mais de 20 mil empresários.` | `{{P2}}` |
| 4 | `E não podia ter hora melhor: … dentro da sua empresa.` | `{{A2}}` |
| 4 | `Mas corre, porque são os últimos dias.` | `{{P3}}` |
| 5 | (nada — texto fixo) | — |

Copiar o texto exato do `design_content` (espaços antes de `\n` contam).

## CLAILTON (a partir de "Nenhum funcionário se importa… | CLAILTON" `DAHWNGXt-To`)

1. `copy-design` de `DAHWNGXt-To` com `page_numbers: [1, 2, 10]` (o `merge-designs` falha com
   designs de 2160×2700).
2. `read-design` com `open_transaction`; marcadores:

| Pág. | Texto original | Marcador |
| --- | --- | --- |
| 1 | `Nenhum funcionário \nse importa de verdade \ncom a sua empresa.` | `{{H}}` |
| 1 | `Até você dar um motivo \npara ele se importar. 👉` | `{{SUB}}` |
| 1 | `01/11` | `01/{{T}}` |
| 2 | `A empresa é o seu sonho. \nA meta é sua. \nO faturamento é seu. \n` | `{{P1}} ` (com espaço) |
| 2 | `O crescimento é seu.` | `{{B1}}` |
| 2 | `Então não espere que alguém acorde numa \nsegunda-feira tão empolgado quanto você ` | `{{P2}} ` (com espaço) |
| 2 | `porque a empresa precisa crescer.` · `02/11` | `{{B2}}` · `{{N}}/{{T}}` |
| 3 | `Encara essa verdade: \nO seu funcionário não tem obrigação \nde amar a sua empresa só porque ela beneficia você.` | `{{P1}}` |
| 3 | `O dia que você para de cobrar amor \ne começa a construir estrutura, \no comprometimento aparece sozinho.` | `{{B1}}` |
| 3 | `Mas isso não se faz no improviso, … no lugar certo.` · `10/11` | `{{P2}}` · `{{N}}/{{T}}` |

3. `update_title` `TEMPLATE CARROSSEL | CLAILTON` e `commit`.
4. `resize-design` desse design para `custom 1080 × 1350` → **o design redimensionado é o template**
   (o de 2160 pode ser apagado).

## Depois de recriar

- Capa LEGACY: colar no editor do Canva o círculo com foto da capa "O Digital matou as lojas
  físicas" (`DAHWJFMPkkY`): x 589.5, y 277.7, 432.8×432.8, borda branca 5 px. O conector não cria
  imagem redonda.
- Conferir no `read-design` (com transação) a posição e o tamanho da FOTO, do DEGRADE (imagem
  `MAFuE1lvpvY`, com o recorte `imageBox`) e do CIRCULO de cada página; se mudaram, atualizar `PAG`
  no `scripts/medir.py` e no `scripts/medir.mjs` e as medidas em `template.md`.

Atualizar IDs e links em `template.md` e fazer um teste curto: montar 1 capa + 1 corpo + CTA com uma
copy qualquer, conferir as miniaturas (cores, caixa-alta só no título do CTA, texto fora do rodapé)
e descartar o teste (`cancel`).

Se os carrosséis de origem também não existirem mais: usar um carrossel recente do mesmo padrão e o
mesmo método (cada trecho de texto vira um marcador, sem inserir `\n`).
