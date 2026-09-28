# Copy de entrada → cards e marcadores

A copy chega em **qualquer formato** ("SLIDE 1 — CAPA / Título: …", "Card 1:", lista numerada,
blocos separados por linha em branco ou `─────`). Não exigir formato: classificar cada card e
extrair os campos. **Nunca reescrever a copy** — só distribuir, quebrar linhas e marcar destaques.

## 1. Classificar cada card

| Tipo | Como reconhecer | LEGACY (pág. do template) | CLAILTON (pág.) |
| --- | --- | --- | --- |
| CAPA | 1º card; "CAPA", "Título/Headline" | 1 | 1 |
| CORPO | card comum, 1–3 parágrafos curtos | 2 | 2 (≤ ~300 caracteres) · 3 se maior |
| CORPO COM TÍTULO | item numerado ("1. Leitura financeira.") ou mini-título + corpo | 3 | vira CORPO com o título em negrito (`{{B1}}`) e corpo em `{{P2}}` |
| CTA | fala da Legacy/executoria, "20 mil empresários", oferta, "últimos dias" | 4 | 3 (sempre CORPO LONGO) |
| BÔNUS 1% | "Se você faz parte do 1% que chegou até aqui…" ou pedido "com bônus" | 5 (texto fixo) | — |

Formato não informado (LEGACY ou CLAILTON) → **perguntar antes de montar**. Regra do usuário.

## 2. LEGACY — o que vai em cada marcador

**CAPA (pág. 1)** — diagramação obrigatória em **toda** capa LEGACY (referência aprovada: capa do
Pontofrio, `DAHWNvVN9yc`; não precisa abrir). São 3 linhas em Bebas, centralizadas, **cada frase numa
linha só e cada linha ocupando a largura toda**: é o tamanho da fonte de cada linha que faz a frase
encher a largura. Bebas já é caixa-alta: digitar normal.
- `{{H1}}` linha 1, branca: 1ª parte da manchete (o contexto). Costuma ser a mais longa → fonte menor.
- `{{H2}}` linha 2, branca: 2ª parte da manchete (o fato/virada). Costuma ser curta → fonte maior.
- `{{H3}}` linha 3, **dourada** (cor padrão; nota de cor na copy, tipo "azul", não muda isso): a
  pergunta/frase de impacto, inteira.
- Copy "headline + subheadline/pergunta": a headline se divide em H1 + H2 na quebra natural (fim de
  frase, vírgula ou onde entra o verbo) e a pergunta vai em H3. Nada de `\n` dentro de uma linha.

| Linha | Pontofrio (aprovada) | Chilli Beans (aprovada) |
| --- | --- | --- |
| 1 branca | Ela foi uma das maiores redes do país · 84 px | Uma das marcas mais amadas do Brasil · 80 px |
| 2 branca | Hoje quase não existe mais · 117 px | acendeu um sinal de alerta · 114 px |
| 3 dourada | O que aconteceu com o Ponto Frio? · 91 px | O que está acontecendo com a Chilli Beans? · 72 px |

Cada linha mede ~975 px (caixa de 981). O tamanho vem do script, nunca de estimativa:
`python3 scripts/medir.py capa "Linha 1" "Linha 2" "Pergunta"` → `px` (conector) e `ui` (número que
aparece no painel do Canva = px × 0,75) de cada linha, `altura_bloco` e as posições.
- Template com H1/H2/H3 em **3 caixas**: `format_text` com o `px` de cada caixa e `position_element`
  com `tres_caixas.tops` (left 50.64). Pronto, sem ajuste manual.
- Template com as 3 linhas **na mesma caixa** (situação atual): o conector só aplica um tamanho na
  caixa inteira (limite em `template.md`). Aplicar `caixa_unica.format_text_px` (o da linha mais
  larga, assim nenhuma quebra), `position_element` top = `caixa_unica.top` (left 50.64) e, na
  entrega, passar ao usuário os valores `ajuste_manual_ui` das linhas 1 e 2 (selecionar a linha →
  campo de tamanho da fonte). Nunca passar px para o usuário: o painel mostra px × 0,75.

O mesmo comando devolve a posição do degradê e da foto da capa e a faixa onde o sujeito da foto
precisa estar (`sujeito_entre_pct`); as `operacoes` já vêm prontas.

**Círculo da capa**: foto redonda com borda branca no alto, à direita (já vem na página-modelo).
Nunca apagar. A skill põe nele o segundo elemento da história (`imagens.md`); sem imagem boa, fica a
de exemplo e o círculo entra no "trocar foto" da entrega.

**CORPO (pág. 2)** — Poppins bold 53 px, ~33 caracteres por linha
- `{{BRANCO}}` = parágrafo(s) principal(is) (entre parágrafos: `\n\n`).
- `{{CINZA}}` = o **último** parágrafo (a conclusão/virada). Card sem parte cinza: trocar
  `"{{BRANCO}}\n\n"` (tudo no trecho branco) pelo texto e `{{CINZA}}` por `""` — assim não sobra
  linha vazia embaixo.
- Tamanho pelo nº de linhas (incluindo as em branco): ≤ 6 → 53 px · 7–9 → `font_size` 44 · ≥ 10 → 40.
  `python3 scripts/medir.py pag2 "Par. 1" "Par. 2" …` faz a conta e devolve fonte, largura (palavra
  sozinha na última linha), degradê e foto.
- Quebras manuais (`\n`) só onde a copy tiver; senão deixar o texto quebrar sozinho.

**CORPO COM TÍTULO (pág. 3)** — `{{TITULO}}` Bebas 80 px: até ~30 caracteres cabe em 1 linha; mais
que isso, quebrar com `\n` num ponto natural (depois da vírgula) para não sobrar palavra sozinha, e
subir o título. `{{CORPO}}` Poppins 40 px com `\n\n` entre parágrafos: até 8 linhas fica na posição
do template; mais que isso, manter 40 px e subir título + corpo (conta em `template.md`).
`python3 scripts/medir.py pag3 "Título" "Par. 1" "Par. 2" …` devolve o título já quebrado e as
`operacoes` da página (título, corpo, degradê, foto).

**Textos de tamanhos diferentes** (o script decide; nunca estimar no olho):

| Situação | O que acontece |
| --- | --- |
| Texto curto (título 1 linha, corpo ≤ 8 linhas na pág. 3; ≤ 5 linhas na pág. 2) | tudo na posição do template |
| Título em 2 ou 3 linhas | título sobe; degradê sobe junto |
| Corpo longo (pág. 3: 9+ linhas) | corpo ancorado embaixo, título e degradê sobem; se o fim do degradê passar do fim da foto, a foto sobe junto |
| Corpo longo (pág. 2) | fonte 44 ou 40; o texto cresce para cima e o degradê acompanha |
| Muito longo (título acima de y 350) | corpo em 36 px; se ainda não couber, avisar na entrega |
| Texto cobre quase o card | `foto_util: false`: sem busca de imagem, a foto de exemplo é apagada |
| Palavra sozinha na última linha | caixa do corpo mais estreita (`resize_element`), sem mudar a fonte |

Quanto mais texto, menor a faixa da foto que aparece: a imagem daquele card precisa ter o sujeito
dentro de `sujeito_entre_pct` (em % da altura da moldura, de cima para baixo). É isso que vai no
briefing e no prompt da IA.

**CTA (pág. 4)**
| Marcador | Conteúdo | Regra |
| --- | --- | --- |
| `{{TITULO}}` | frase de abertura (azul, renderiza em caixa-alta) | ≤ ~70 caracteres |
| `{{P1}}` | **1º parágrafo** do bloco preto | **sem `\n`** (senão vira caixa-alta) |
| `{{P1B}}` | demais parágrafos pretos antes do 1º destaque azul | aceita `\n`; vazio → `"\n\n{{P1B}}"` → `""` |
| `{{A1}}` | 1º destaque azul (ex.: "É isso que a executoria da Legacy faz.") | 1 frase |
| `{{P2}}` | parágrafos pretos do meio | aceita `\n\n` |
| `{{A2}}` | 2º destaque azul (a oferta, "🎁 E estamos na semana…") | — |
| `{{P3}}` | fecho preto ("Mas corre, são os últimos dias.") | — |
Total ≤ ~750 caracteres. Mais que isso → `format_text` `font_size` 34 (só se necessário).
Destaques azuis: o que a copy marcar em **negrito** ou o que for claramente a solução/oferta.
Sem parágrafo preto antes do 1º destaque azul: `"{{P1}}\n\n{{P1B}}\n\n"` → `""` (um trecho só).

**BÔNUS (pág. 5)**: texto fixo, nada a preencher. Incluir só quando a copy tiver o card do 1%.
A mesma página serve para um card de reflexão que a copy peça em **fundo preto com frase em destaque
azul**: trocar o trecho branco e o azul (texto exato em `template.md`), `format_text` ~68 px para
~270 caracteres e centralizar na altura.

**Rodapé: fonte da copy e crédito da foto** — vão juntos na 2ª linha do handle, pequena e discreta
(mesmo estilo do handle): `Fonte: X, 2026. · Foto: Y` (só o que existir; formatos de crédito em
`imagens.md`; IA e banco pago não levam crédito).
- Pág. 3: `" & @clailtonluiz"` → `"\nFonte: X, 2026. · Foto: Y"` (com dupla assinatura:
  `"@clailtonluiz"` → `"@clailtonluiz\nFoto: Y"`). Linha longa: `resize_element` do handle com
  `width` 850 (a seta começa em x 926).
- Pág. 2: `"@legacyexecutoria"` → `"@legacyexecutoria\nFoto: Y"` + `resize_element` width 850 +
  `format_text` `text_align: "start"` (o handle dessa página é centralizado).
- Capa: `"@legacyexecutoria"` → `"@legacyexecutoria\nFotos: Y e Z"` + `resize_element` width 900 +
  `position_element` left 90 (top igual) + `format_text` `text_align: "center"`.
- Na entrega, repetir todos os créditos numa linha pronta para a legenda do post.

**Handle**: padrão `@legacyexecutoria`. Se a copy/usuário pedir dupla assinatura, trocar em cada
card (`find_and_replace_text` no elemento do handle) por `@legacyexecutoria & @clailtonluiz`.
A pág. 3 já vem com a dupla — trocar para `@legacyexecutoria` quando não for o caso.

## 3. CLAILTON — o que vai em cada marcador

- Negrito: a copy do Clailton marca com `**...**`. Fora do negrito → `{{P*}}` (medium); dentro →
  `{{B*}}` (bold). Sem marcação: o fecho/frase de impacto do card vai em negrito (padrão do perfil).
- **CAPA**: `{{H}}` headline em 2–3 linhas (`\n` a cada ~22 caracteres) · `{{SUB}}` sub-headline,
  termina com 👉 · `01/{{T}}` → total com 2 dígitos (`01/11`).
- **CORPO (pág. 2)**: `{{P1}} {{B1}}` = 1º parágrafo (parte normal + fecho em negrito) · `\n\n` ·
  `{{P2}} {{B2}}` = 2º parágrafo. Parágrafo todo em negrito → `{{P*}} ` → `""` (com o espaço).
  Card de 1 parágrafo → `{{P2}} ` e `{{B2}}` → `""` (sobra uma linha em branco no fim, invisível).
- **CORPO LONGO (pág. 3)**: `{{P1}}` medium · `{{B1}}` bold (parágrafo inteiro) · `{{P2}}` medium
  (pode ter vários parágrafos com `\n\n`). Usar para > ~300 caracteres e para o CTA.
- Contador `{{N}}/{{T}}` em todos: `02/11`, `03/11`…

## 4. Exemplo (copy típica da skill legacy-carrossel-copy)

```
SLIDE 1 — CAPA
Título: Ser dono é saber cobrar.
Subtítulo: Deixa eu te falar uma verdade que dói
SLIDE 2
Se o seu sonho é ser o queridinho da equipe, você abriu o negócio errado.
Empresa não se toca na base do "todo mundo me ama".
```
LEGACY → H1 "Deixa eu te falar " · H2 "uma verdade que dói:" · H3 "Ser dono é saber cobrar." ·
card 2: BRANCO = 1ª frase, CINZA = 2ª frase.
