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
| REFLEXÃO | "Reflexão", "fundo preto", fecho antes do CTA | 3 sem foto, fundo preto (`template.md`) | 2 ou 3 |
| BÔNUS 1% | "Se você faz parte do 1% que chegou até aqui…" | saiu do template em 29/09/2026: avisar o usuário | — |

Formato não informado (LEGACY ou CLAILTON) → **perguntar antes de montar**. Regra do usuário.

## 2. LEGACY — o que vai em cada marcador

**CAPA (pág. 1)** — diagramação obrigatória em **toda** capa LEGACY (referências aprovadas:
Pontofrio `DAHWNvVN9yc` e maior onda de recuperações `DAHWgdFSrXw`; não precisa abrir). São 3
linhas em Bebas, centralizadas, **cada frase numa linha só e cada linha ocupando a largura toda**: é
o tamanho da fonte de cada linha que faz a frase encher a largura. Bebas já é caixa-alta: digitar
normal. Acima da manchete, o logo da Legacy; o círculo e as imagens seguem `imagens.md` §1b.
- `{{H1}}` e `{{H2}}`, brancas: a manchete (headline), quebrada em duas pelo
  `medir.py manchete`: se ela tem duas frases, quebra no ponto final; senão, onde a menor das duas
  linhas fica com a maior fonte (as duas grandes, nenhuma miúda). Para forçar uma quebra, marcar com
  `|` ("Uma das marcas mais amadas do Brasil | acendeu um sinal de alerta").
- `{{H3}}` linha 3, **dourada** (cor padrão; nota de cor ou de tamanho na copy, tipo "linha 2
  gigante, azul", não muda isso): a pergunta/subheadline/frase de impacto, inteira.
- Nada de `\n` dentro de uma linha.

| Linha | Pontofrio (aprovada) | Chilli Beans (aprovada) | Recuperações (aprovada) |
| --- | --- | --- | --- |
| 1 branca | Ela foi uma das maiores redes do país · 84 px | Uma das marcas mais amadas do Brasil · 80 px | O Brasil vive a maior onda de · 109 px |
| 2 branca | Hoje quase não existe mais · 117 px | acendeu um sinal de alerta · 114 px | empresas quebrando da sua história · 85 px |
| 3 dourada | O que aconteceu com o Ponto Frio? · 91 px | O que está acontecendo com a Chilli Beans? · 72 px | E os números alertam que vai piorar. · 84 px |

Cada linha mede ~975 px (caixa de 981): **só o tamanho da fonte muda de uma linha para outra**.
O tamanho vem do script, nunca de estimativa:
`python3 scripts/medir.py manchete "Manchete inteira" "Pergunta" --circulo esquerda|direita` (ou
`capa "Linha 1" "Linha 2" "Pergunta"` com as linhas já separadas) → `px` de cada linha (inteiro,
para baixo, que é o que o `format_text` aceita), `altura_bloco` e as `operacoes`: `format_text` +
`position_element` de H1, H2 e H3 (left 50.64), CIRCULO e o grupo do LOGO. No template cada linha é
uma caixa separada, então é só aplicar: a capa sai pronta, sem ajuste no editor. Capa com linhas de larguras diferentes foi
reprovada pelo usuário (28/09/2026) e não se entrega. Se o script der `aviso` (linha curta demais,
fonte enorme encostando no círculo), conferir na miniatura e contar na entrega.

O mesmo comando devolve a posição do degradê e da foto da capa e a faixa onde o sujeito da foto
precisa estar (`sujeito_entre_pct`); as `operacoes` já vêm prontas.

**Círculo da capa**: foto redonda com borda branca (já vem na página-modelo), 462 px, do lado
oposto ao sujeito da foto de fundo. Nunca apagar. Leva o protagonista + o fato (`imagens.md` §1b),
com a placa/logo inteiros; sem imagem boa, fica a de exemplo e o círculo entra no "trocar foto" da
entrega.

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
Total ≤ ~750 caracteres (a 40 px, caixa em y 269: ~700 caracteres terminam em y≈1290). Mais que
isso → `format_text` `font_size` 36 ou subir a caixa (só se necessário).
Nota de design na copy pedindo CTA em fundo azul com foto do Clailton/Allan: o template não tem essa
versão; montar no padrão e avisar na entrega.
Destaques azuis: o que a copy marcar em **negrito** ou o que for claramente a solução/oferta.
Sem parágrafo preto antes do 1º destaque azul: `"{{P1}}\n\n{{P1B}}\n\n"` → `""` (um trecho só).

**REFLEXÃO em fundo preto** (a pág. 5 saiu do template em 29/09/2026): pág. 3 sem foto, título e
corpo centralizados na altura (passo a passo em `template.md`). Frase marcada em azul na copy fica
branca (a caixa do corpo tem uma cor só): avisar na entrega.

## 2b. Quebra de linha: nenhuma linha termina em conector (regra do usuário, 30/09/2026)

O usuário corrigiu à mão o carrossel da Marisa inteiro por causa disso. Palavra de ligação no fim
da linha ("…vendeu mais **e**", "…cara demais, **ela**", "…já foi **para**", "…fora **de**") desce
para a linha de baixo, junto da palavra seguinte. Lista: e, a, o, as, os, à, ao, de, do, da, dos,
das, em, no, na, nos, nas, um, uma, que, para, por, pelo, pela, com, sem, ou, se, mas, nem, ele,
ela, eles, elas, seu, sua, é, como, quando, onde, porque.

- **Corpo e CTA (Poppins)**: o `medir.py` (`pag2`, `pag3`, `corpo`) devolve `pars` = os parágrafos
  com espaço inseparável (U+00A0) depois de **todo** conector (assim ele nunca fica no fim da
  linha, mesmo quando o Canva quebra 1 palavra diferente da previsão), e `linhas_texto` = as
  linhas previstas. Colocar no card o `pars` unido com `\n\n`. Não muda a copy,
  só onde a linha quebra. Número de linhas e posições já saem contando com isso.
- **Título (Bebas)**: a quebra do `medir.py` é por largura; se a 1ª linha terminar em conector,
  mover o `\n` para antes dele ("E isso vale ainda\nmais para o pequeno.", nunca "…ainda mais
  para\no pequeno.").
- **Capa**: cada linha é uma frase inteira; na manchete dividida em H1 + H2, H1 não termina em
  conector (forçar a quebra com `|`).
- Como o usuário quebra: no fim da oração, depois de vírgula, dois-pontos ou ponto ("…voltou a dar
  prejuízo:" / "mais de R$ 68 milhões em um trimestre."). Na dúvida entre duas quebras, a que
  deixa cada linha com sentido próprio.
- Conferir na miniatura de cada página: o Canva pode quebrar 1 palavra diferente do script. Sobrou
  conector no fim → espaço inseparável depois dele e nova conferência.

**Rodapé: só o `@`; fonte da copy na linha `{{FONTE}}`**
- **Fonte da copy** ("Rodapé: fonte X") na pág. 3: vai no marcador `{{FONTE}}` (linha cinza pequena
  logo abaixo do corpo): `"{{FONTE}}"` → `"Fonte: X, 2026."`. Sem fonte: `"\n\n{{FONTE}}"` → `""`.
  No `medir.py pag3`, passar a fonte como último parágrafo para o bloco subir o suficiente.
- **Crédito da foto não entra no card** (regra do usuário, 30/09/2026: "não precisamos colocar a
  fonte da foto embaixo do @"; ele apagou os "Foto: …" do carrossel da Marisa). O handle fica
  exatamente como vem do template, em todas as páginas e na capa: sem 2ª linha, sem `resize`, sem
  mudar alinhamento.
- Os créditos das fotos reais vão só na resposta da entrega, numa linha pronta para a legenda do
  post (formatos em `imagens.md` §8).

**Handle**: padrão `@legacyexecutoria`. Se a copy/usuário pedir dupla assinatura, trocar em cada
card (`find_and_replace_text` no elemento do handle) por `@legacyexecutoria & @clailtonluiz`.
Desde 29/09/2026 a pág. 3 vem só com `@legacyexecutoria` (como as outras).

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
