# Componentes do Playbook Legacy

Este é o catálogo inteiro. Todo playbook é escrito só com o que está aqui: o `verificar.mjs` recusa tag, classe ou atributo fora dele, e o visual vem pronto do template. Numeração dos passos, moldura das capturas, botão de copiar, caixinhas do checklist, ícones dos avisos, sumário e números da capa são colocados sozinhos: não escreva nada disso à mão.

Sumário:
1. Esqueleto do arquivo (copie e preencha)
2. Bloco de dados da capa
3. Capítulos: atributos
4. Componentes de texto
5. Componentes de bloco
6. Tags, classes e atributos permitidos

## 1. Esqueleto do arquivo

O arquivo de entrada tem **só** isto: o bloco de dados e os capítulos, nesta ordem. Os textos em `‹›` são para trocar. Os capítulos fixos (comece, o-que-e, antes, custos, boas-praticas, problemas, glossario) mantêm a etiqueta e o título exatamente como estão.

```html
<script type="application/json" id="playbook-dados">
{
  "nome": "‹Nome do processo ou ferramenta›",
  "artigo": "do",
  "area": "‹Área ou time›",
  "atualizado": "‹dd/mm/aaaa›",
  "lead": "O guia passo a passo para ‹objetivo›, feito para quem ‹nunca fez / nunca usou›. Siga na ordem e ‹resultado concreto que a pessoa terá›.",
  "faixa": ["‹Para quem é›", "‹Onde acontece›"],
  "contexto": "‹Contexto X.md›",
  "ajuda": "‹quem cuida do X›"
}
</script>

<section class="chapter" id="comece" data-grupo="Comece aqui" data-toc="O caminho em ‹N› passos">
  <span class="eyebrow">comece aqui</span>
  <h2 class="title">O caminho em <span class="hl">‹N› passos</span></h2>
  <p class="lead">‹Uma frase: o que a pessoa vai conseguir seguindo os passos.› Clique num passo para ir direto a ele.</p>
  <div class="road">
    <a href="#passo-1"><strong>‹Título do passo 1›</strong><span>‹dica de até 60 caracteres›</span></a>
    <a href="#passo-2"><strong>‹Título do passo 2›</strong><span>‹dica›</span></a>
  </div>
</section>

<section class="chapter" id="o-que-e" data-toc="O que é ‹o/a Nome›">
  <span class="eyebrow">entenda</span>
  <h2 class="title">O que é ‹o/a› <span class="hl">‹Nome›</span></h2>
  <p class="lead">‹O que é e para que serve, em 1 ou 2 frases.›</p>
  ‹cartões e 1 aviso info, se ajudarem›
</section>

<section class="chapter" id="antes" data-toc="Antes de começar">
  <span class="eyebrow">checklist</span>
  <h2 class="title">Antes de <span class="hl">começar</span></h2>
  <p class="lead">Confira se você tem tudo isto. Pode ir marcando:</p>
  <ul class="check">
    <li>‹Item que a pessoa precisa ter, com o essencial em <b>negrito</b>.›</li>
  </ul>
</section>

<section class="chapter" id="passo-1" data-passo="1" data-grupo="‹Nome do fluxo principal›" data-toc="‹Título curto›">
  <span class="eyebrow">passo 1</span>
  <h2 class="title">‹Verbo› ‹o/a› <span class="hl">‹objeto›</span></h2>
  <p class="lead">‹Opcional: uma frase do que acontece neste passo.›</p>
  <ol class="steps">
    <li><b>‹Ação no imperativo.›</b> ‹Onde fica, o que aparece, o que esperar.›</li>
  </ol>
</section>

<!-- passo-2 … passo-N iguais (data-passo="2", etiqueta "passo 2"…); sem data-grupo -->

<section class="chapter" id="‹id-livre›" data-tipo="extra" data-toc="‹Título curto›">
  <span class="eyebrow">extra</span>
  <h2 class="title">‹Título› <span class="hl">‹destaque›</span></h2>
  ‹conteúdo›
</section>

<section class="chapter" id="custos" data-grupo="Mais" data-toc="Quanto custa">
  <span class="eyebrow">dinheiro</span>
  <h2 class="title">Quanto <span class="hl">custa</span></h2>
  <p class="lead">‹Quando gasta, com o quê e quando não gasta nada.›</p>
  ‹tabela "O que / Custo aproximado" + dica de economia›
</section>

<section class="chapter" id="boas-praticas" data-toc="Boas práticas">
  <span class="eyebrow">jeito certo</span>
  <h2 class="title">Boas <span class="hl">práticas</span></h2>
  <div class="cards praticas">
    <div class="card"><h4>‹2 a 4 palavras›</h4><p>‹Uma ou duas frases.›</p></div>
  </div>
</section>

<section class="chapter" id="problemas" data-toc="Problemas comuns">
  <span class="eyebrow">socorro</span>
  <h2 class="title">Problemas comuns e como <span class="hl">resolver</span></h2>
  <p class="lead">Clique na pergunta para ver a resposta.</p>
  <details class="faq"><summary>‹O sintoma, como a pessoa vê›</summary><p>‹Causa em uma frase. Conserto, com link para o passo.›</p></details>
</section>

<section class="chapter" id="glossario" data-toc="Glossário">
  <span class="eyebrow">palavras</span>
  <h2 class="title"><span class="hl">Glossário</span></h2>
  <dl class="gloss">
    <dt>‹Termo›</dt><dd>‹Definição em uma frase, sem jargão.›</dd>
  </dl>
</section>
```

Regras do esqueleto:
- Os capítulos extras e `custos` são opcionais.
- Grupos do sumário: `data-grupo` vai só no primeiro capítulo de cada grupo.
  - "Comece aqui": em `comece`.
  - O nome do fluxo: em `passo-1`. Um extra que continua o fluxo (ex.: "Ligar números e imagens") vem logo depois dos passos, sem `data-grupo`.
  - "Mais": no primeiro capítulo que não é do fluxo, seja um extra "outra ferramenta" ou "avançado", o `custos` ou o `boas-praticas`.
- Etiquetas dos extras: `extra` (complemento do fluxo), `outra ferramenta` ou `avançado`. Dentro de um extra vale qualquer componente, inclusive `ol.steps`.
- O `id` de um extra é curto, em minúsculas e com hífen (ex.: `imagens`, `radar`).
- O texto pode conter `{{…}}` (ex.: um marcador de template do Canva): o montar só troca os próprios marcadores `@@…@@`.

## 2. Bloco de dados da capa

| Campo | Obrigatório | O que é | Limite |
|---|---|---|---|
| `nome` | sim | como o time chama o processo ou a ferramenta; sai em destaque na capa | 40 caracteres |
| `artigo` | sim | `do`, `da`, `de`, `dos` ou `das`, para ler "Playbook do JEV Lab" | |
| `area` | sim | time ou área (ex.: "Marketing e conteúdo", "Comercial", "Financeiro") | 40 |
| `atualizado` | sim | data de hoje, dd/mm/aaaa | |
| `lead` | sim | a frase da capa: o que é o guia, para quem e o que a pessoa terá no fim | 320 |
| `faixa` | sim | exatamente 2 frases curtas: para quem é e onde acontece (ex.: "Feito para quem nunca usou", "Roda no seu computador") | 38 cada |
| `contexto` | não | nome do documento técnico do processo (ex.: "Contexto JEV Lab.md"), para quem mantém o processo saber o que procurar | |
| `ajuda` | não | a quem pedir ajuda (ex.: "quem cuida do JEV", "o time de operações") | |

É texto puro: não use HTML nos campos. `contexto` e `ajuda` aparecem no rodapé ("Contexto técnico: …" e "Dúvida que este guia não resolve: fale com …"); sem eles, a linha some. O playbook é copiado e enviado por WhatsApp ou e-mail, então nenhum texto dele deve depender da pasta em que está: escreva o caminho completo quando precisar citar um lugar. Os números da capa (passos, minutos de leitura e dúvidas respondidas) são calculados sozinhos.

## 3. Capítulos: atributos

```html
<section class="chapter" id="passo-3" data-passo="3" data-toc="Conectar o Instagram">
```
- `class="chapter"` e `id`: sempre.
- `data-passo="N"`: só nos passos, igual ao número do id.
- `data-grupo`: só no capítulo que **abre** um grupo do sumário.
- `data-toc`: o nome no sumário, com até 34 caracteres. Sem ele, o sumário usa o título.
- `data-tipo="extra"`: nos capítulos extras.
- `data-marca`: opcional nos extras, com 1 símbolo para o sumário (ex.: `◎`). O padrão é `+`.

A primeira coisa dentro do capítulo é a etiqueta `<span class="eyebrow">`; a segunda, o título `<h2 class="title">` com exatamente um `<span class="hl">`. Depois, se quiser, vem uma `<p class="lead">`.

## 4. Componentes de texto (dentro de parágrafos, passos, tabelas)

| Para | Use | Exemplo |
|---|---|---|
| o essencial da frase | `<b>` | `Gasta <b>créditos</b>.` |
| botão ou menu, como aparece na tela | `<span class="ui">` | `<span class="ui">Entrar</span>`, `<span class="ui">EXPORTAR CSV</span>` |
| o botão principal da ação | `<span class="ui go">` | `<span class="ui go">INICIAR</span>` |
| status positivo mostrado na tela | `<span class="ui ok">` | `<span class="ui ok">conectado</span>` |
| tecla | `<kbd>` | `<kbd>Ctrl</kbd> + <kbd>C</kbd>` |
| endereço, comando, arquivo, pasta ou mensagem do sistema | `<code>` | `<code>localhost:3777</code>` |
| link para outra parte | `<a href="#id">` | `veja o <a href="#passo-1">Passo 1</a>` |
| link externo | `<a href="https://…">` | só quando a pessoa precisa abrir o site |
| caminho de menus | `→` entre os itens | `<span class="ui">File</span> → <span class="ui">Open Folder</span>` |

## 5. Componentes de bloco

### Passos numerados
A numeração e a linha que liga os passos são automáticas. Cada `<li>` começa com o título em negrito (frase completa, com ponto) e segue com o detalhe.
```html
<ol class="steps">
  <li><b>Abra o Google Chrome.</b></li>
  <li><b>Digite <code>localhost:3777</code> e aperte <kbd>Enter</kbd>.</b> Use a barra de endereço, lá em cima.</li>
  <li><b>Digite o comando e aperte <kbd>Enter</kbd>:</b>
    <div class="cmd"><code>npm start</code></div>
  </li>
</ol>
```
Dois caminhos para o mesmo passo: use `<h3>Jeito A: …</h3>` + `<ol class="steps">` e depois `<h3>Jeito B: …</h3>` + outra lista.

### Comando para copiar
Uma linha de comando (ou um pedido pronto para colar no Claude) por caixa. O botão "copiar" aparece sozinho. Pode vir texto antes e depois da caixa, inclusive dentro de um passo.
```html
<div class="cmd"><code>npm install</code></div>
```

### Avisos (no máximo 3 por capítulo)
O ícone e a etiqueta ("Dica", "Bom saber", "Atenção", "Cuidado") são automáticos. O título é a regra; o texto, o porquê e o que fazer.
```html
<div class="note tip">
  <b class="h">Deixe nos favoritos</b>
  <p>Salve <code>localhost:3777</code> nos favoritos do Chrome (<kbd>Ctrl</kbd> + <kbd>D</kbd>).</p>
</div>
```
Tipos: `note tip` (dica: atalho, economia), `note info` (bom saber: contexto), `note warn` (atenção: erro comum), `note danger` (cuidado: risco sério). Dentro do aviso cabem `<p>` e `<ul class="plain">`.

### Captura de tela
A moldura, o zoom ao clicar e a imagem embutida são automáticos. `browser` põe a barra de navegador em cima; use em tela inteira de um site ou app web, e deixe sem ela em recortes.
```html
<figure class="shot browser">
  <img data-shot="login" alt="Tela de entrada com o campo Senha de acesso e o botão Entrar" />
  <figcaption><b>Tela de entrada.</b> Digite a senha e clique em Entrar.</figcaption>
</figure>
```
- O `alt` descreve o que aparece na tela.
- A legenda começa com um trecho em negrito que nomeia a tela ou o momento.
- A imagem vem do arquivo `NN-login.jpg` da pasta passada em `--capturas`.

### Tabela
Boa para "você quer… / faça assim", "botão / o que faz", "coluna / o que quer dizer" e custos e tempos. Cabeçalho curto (vira azul-marinho, em maiúsculas).
```html
<table>
  <thead><tr><th>Você quer…</th><th>Preencha assim</th></tr></thead>
  <tbody>
    <tr><td>Só os números, sem gastar créditos</td><td>PERFIS <code>@perfil</code> · os últimos 7 dias · ☐ transcrever</td></tr>
  </tbody>
</table>
```

### Cartões
Use no `o-que-e` (as partes ou ferramentas) e em `boas-praticas` (com a classe `praticas`, que põe o ícone de check).
```html
<div class="cards">
  <div class="card main">
    <span class="tag">a mais usada</span>
    <h4>Extrator de perfil</h4>
    <p>Você informa um ou vários perfis e um período…</p>
  </div>
  <div class="card">
    <span class="tag">tendências</span>
    <h4>Radar de vídeos</h4>
    <p>Mostra o que está em alta agora…</p>
  </div>
</div>
```
`card main` é o cartão em destaque (fundo azul-marinho): no máximo um por grupo, na parte principal. `tag` é uma etiqueta curta e opcional.

### Checklist
Cada item vira uma caixinha de marcar.
```html
<ul class="check">
  <li>O <b>Google Chrome</b> instalado.</li>
</ul>
```

### Pergunta que abre e fecha
Obrigatória em `problemas`. Também serve para um "e se…" longo que atrapalharia a leitura, como a instalação num computador novo em `antes`.
```html
<details class="faq">
  <summary>Digitei localhost:3777 e a página não abre</summary>
  <p>O programa está desligado. Faça o <a href="#passo-1">Passo 1</a> e recarregue a página com <kbd>F5</kbd>.</p>
</details>
```
Dentro da resposta cabem `<p>`, `<ol class="plain">`, `<ul class="plain">` e `<div class="cmd">`.

### Árvore de pastas
Para mostrar onde ficam os arquivos. `d` destaca uma pasta; `c`, um comentário.
```html
<pre class="tree"><span class="d">carrosseis/</span>
└─ <span class="d">clailtonluiz/</span>        <span class="c">← uma pasta por perfil</span>
   └─ card-01.jpg</pre>
```

### Lista simples, subtítulo e separador
```html
<ul class="plain"><li>…</li></ul>
<ol class="plain"><li>…</li></ol>
<h3>Exemplos prontos</h3>
<hr class="sep" />
```
`<h3>` separa blocos dentro de um capítulo ("Jeito A", "Exemplos prontos", "O que cada número quer dizer"). Não use `<h4>` fora dos cartões.

### Glossário
```html
<dl class="gloss">
  <dt>Carrossel</dt><dd>Post com várias imagens que a pessoa passa para o lado.</dd>
</dl>
```

## 6. Permitido (o resto é recusado)

- **Tags:** section, span, h2, h3, h4, p, b, strong, a, ul, ol, li, div, figure, img, figcaption, table, thead, tbody, tr, th, td, code, kbd, pre, details, summary, dl, dt, dd, br, hr.
- **Classes:** chapter, eyebrow, title, hl, lead, steps, plain, sep, ui, go, ok, cmd, note, tip, info, warn, danger, h, shot, browser, road, cards, card, main, tag, praticas, check, tree, d, c, faq, gloss.
- **Atributos:** id, class, href, alt, data-*, colspan, rowspan, open, target, rel, width, height.
- **Nunca:** `style=`, `<style>`, `<script>` (fora do bloco de dados), `<link>`, `<iframe>`, `<i>`/`<em>` (itálico), emoji, imagem por link.
