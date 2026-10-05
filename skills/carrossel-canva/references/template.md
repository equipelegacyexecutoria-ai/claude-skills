# Templates-mestre no Canva

Criados em 2026-09-26/27 a partir dos carrosséis mais recentes do usuário. **Não editar o texto dos
marcadores nem reordenar/apagar páginas** — a skill depende da ordem das páginas e dos `{{...}}`.
Trocar a foto de exemplo de uma página-modelo é seguro.

## Modelos atuais (lidos em 30/09/2026 — valem estes; o resto do arquivo é histórico)

Os IDs de elemento mudam a cada montagem: achar pelo marcador e pelo tipo, como abaixo.

**LEGACY — `DAHWWhuFIEI`** (https://canva.link/6uw20gnd9l3y8e9), 3 páginas 1080×1440:
1. CAPA: FOTO (`shape` 1104×1142 em −10.8, −10), DEGRADE (`rect` FADE `MAFuE1lvpvY` em y 386.8),
   **LOGO = `rect` 128×120 em (477, 744.6)**, grupo com `{{H1}}` `{{H2}}` brancos e `{{H3}}` **azul
   `#013e6a`** (Bebas 106,67 px, lh 0.95, x 50.64 w 981, tops 904 / 1021 / 1136), grupo com a seta +
   `@legacyexecutoria` (26,67 px) em y 1303. Sem pill "Arraste para o lado".
   **Atualização 30/09 (carrossel da Light): o círculo voltou** — `shape` redondo 334,6 px com borda
   branca 4, em (697, 470) no template. Preencher com `update_fill` (logo/placa da empresa) e, se
   precisar, subir para y ≈ 360 para não encostar no logo da Legacy. A imagem do círculo entra
   **quadrada, com a marca inteira e folga** (logo centrado ocupando ~80% da diagonal): imagem
   retangular é cortada nas laterais (saiu "Lig" em vez de "Light").
2. CORPO COM TÍTULO (igual à antiga pág. 3): `{{TITULO}}` Bebas 80 (y 776.6), corpo `"{{CORPO}}\n\n"`
   + `"{{FONTE}}"` (y 884.6), FOTO 1109×943, DEGRADE 1109×813 em y 333.6, handle `@legacyexecutoria`.
3. CTA: fundo claro, caixa em (64.2, 248) w 953, marcadores `{{TITULO}}` `{{P1}}` `{{P1B}}` `{{A1}}`
   `{{P2}}` `{{A2}}` `{{P3}}` como antes; handle preto.

**LEGACY + CLAILTON — `DAHWsMeChdQ`** (https://canva.link/sloukpu2dld0xek), 3 páginas 1080×1440:
1. CAPA: FOTO, DEGRADE, grupo H1/H2 brancos + H3 azul `#013e6a` (106,67 px, tops 909.5 / 1026.6 /
   1141.2, x 46.2), grupo seta + `@legacyexecutoria & @clailtonluiz` em y 1303–1318. Sem logo, sem
   círculo.
2. CORPO (igual à antiga pág. 2): `"{{BRANCO}}\n\n"` + `"{{CINZA}}"` Poppins 53,33 ancorado embaixo,
   FOTO 1109×1210, DEGRADE em y 472.2, handle duplo (w 551).
3. CTA: caixa em (56.2, 269.4) w 967.5; handle duplo **preto**.

**TWITTER (CLAILTON) — `DAHWW8zqYcQ`** (https://canva.link/kyj3oijlhpuk2jk): sem mudança — 3
páginas 1080×1350 (capa `{{H}}` `{{SUB}}` `01/{{T}}`; corpo `{{P1}} {{B1}}` / `{{P2}} {{B2}}` +
`{{N}}/{{T}}`; corpo longo `{{P1}}` `{{B1}}` `{{P2}}`), avatar `MAHVSCntTPw`, detalhes na seção
CLAILTON abaixo.

**Lições do lote de 01/10/2026 (7 carrosséis):**
- CTA LEGACY sem `{{P1}}`: o `{{A1}}` fica logo depois do título e, se tiver `\n`, a 1ª linha sai em
  caixa-alta (herda o estilo do título). Nesse caso, trocar o `\n` do A1 por espaço.
- Título do CTA também não termina em conector: o script não pega (Bebas/caixa-alta). Colar com
  espaço inseparável (`"ano que vem"`, `"é aí"`) e conferir na miniatura.
- CTA longo do LEGACY + CLAILTON encostando no `@`: subir a caixa de texto para y ≈ 150.
- Card de reflexão (fundo preto) = pág. 2 do LEGACY com FOTO, DEGRADE e o ponto apagados e o texto
  centrado na altura. Nota "fundo preto" na copy dos outros cards: manter a foto (padrão Marisa).
- TWITTER: `"{{P2}} "` com P2 terminando em `\n` joga o B2 para a linha de baixo; frase em negrito
  com palavra sozinha na última linha → `\n` dentro do mesmo trecho (ex.: `"termina.\nMas"`);
  emoji 👉 colado com espaço inseparável na palavra anterior; número no fim da linha (`"8 em"`)
  também. Último card longo: `format_text` 36 px.

**Lições de 05/10/2026 (IA prática em LEGACY + CLAILTON):**
- Copy com título + desenvolvimento no LEGACY + CLAILTON (pág. 2 não tem título): título vai no
  `{{BRANCO}}` e os parágrafos todos no `{{CINZA}}` (unidos com `\n\n`); medir com
  `m.pag2([título, p1, p2, …])` para o tamanho sair certo.
- "Ilustrar com o Clailton": Nano Banana Pro (`imagen-nano-banana-2`, 2k, 1:1) com as fotos dele
  como referência (`ks38ouZ16B`, `Cq7T08VEEy`), prompt "the man from the reference images (keep his
  exact face, bald head, glasses and beard)…", sujeito na metade de cima e parte de baixo escura.
- Imagem de IA com papel/tela costuma vir com palavra em inglês ("PROCEDURE"): conferir ampliado e,
  se aparecer, editar com a própria imagem como referência pedindo para tirar os títulos.
- Miniatura do Canva às vezes mostra linhas do `{{CINZA}}` mais claras: é só a miniatura, a cor no
  design é a mesma.

## LEGACY antigo — `DAHWWhuFIEI` até 29/09/2026 (histórico)

Link: https://www.canva.com/d/NlwpU8NbKEt6BL9 · Origem: SER DONO É SABER COBRAR (`DAHWCDizSTE`
p1, p2, p10, p11) + 5 MATÉRIAS (`DAHWJAVgBic` p3).

| Pág. | Tipo | Elemento(s) de texto e marcadores | Observações de layout |
| --- | --- | --- | --- |
**Mudanças do usuário em 29/09/2026** (manter): o template passou a ter **4 páginas** (saiu a do
bônus 1%), o logo com confete entrou na capa, a pág. 3 ganhou a linha `{{FONTE}}` e o CTA mudou de
posição/tamanho. A manchete da capa tinha voltado a ser uma caixa só; foi separada de novo em 3
caixas no mesmo dia (editor: Ctrl+D ×2 com o usuário em modo de aprovação manual; depois conector).

**Mudanças do usuário em 30/09/2026** (lidas no `read-design`; conferir sempre o que veio, não
supor): o handle de **todas** as páginas passou a `@legacyexecutoria & @clailtonluiz` (w=551, já
alinhado: não mexer); a **capa veio sem o CIRCULO e sem o grupo do LOGO** (só FOTO, DEGRADE, H1–H3,
pill e handle): nesse caso pular as `operacoes` de CIRCULO/LOGO do `medir.py` e não gerar imagem de
círculo; o handle do CTA veio **branco** sobre o fundo claro (fica invisível): `format_text`
`color: "#000000"` nele. Capa cuja copy só rende **2 frases** (ex.: "Vou dizer o que está
entalado:" + frase de impacto): H1 branca + H3 dourada, `delete_element` na H2; H3 top =
1250 − 1,19 × px; H1 top = H3 top − 1,099 × px(H1) + 0,149 × px(H3). CTA com ~770 caracteres e
título de 3 linhas: caixa em top 180 termina em y≈1302.

| 1 | CAPA | **3 elementos**, um por linha (separados em 28/09/2026 e de novo em 29/09/2026): `{{H1}}` branco (80 px, y=979) · `{{H2}}` branco (114 px, y=1049.9) · `{{H3}}` dourado `#e7aa51` (72 px, y=1164.5). Todos Bebas, centralizado, lh 0.95, ls −0.02, x=50.64 w=981, um trecho só cada. Tamanho e posição de cada caixa vêm do `scripts/medir.py capa` (regra em `copy.md`) | FOTO 1104×1142 em (−10.8, −10); DEGRADE 1158×748 em (−51.39, 386.8); **CIRCULO** (shape redondo com foto, borda branca 5 px, x=589.5 y=277.7, 432.8×432.8 no template; o `medir.py` leva a 462×462 em y 330, à esquerda x=50.64 ou à direita x=567.2); pill "Arraste para o lado" y=1270; `@legacyexecutoria` x=388.7 y=1357 w=305 (centralizado pela posição). **LOGO**: grupo (logo `MAHUzbG7AjM` recortado + confete `MAFAqYR48A0`) 127,9×124,1 em x 477,2 — só reposicionar (`medir.py`). Atrás de tudo, um `shape` preto que cobre a página (ignorar) |
| 2 | CORPO | 1 elemento: `{{BRANCO}}` branco · `\n\n` · `{{CINZA}}` `#858489` — Poppins bold 53 px, lh 1.4, x=64 w=974, **ancorado embaixo** (base fixa em y≈1290: texto longo cresce para cima, sobre o degradê) | FOTO 1109×1210 em (−14.3, −17.47); DEGRADE 1109×769 em (−13.19, 472.23); handle x=64 y=1354 w=301 (alinhado ao centro); seta x=926 y=1340 |
| 3 | CORPO COM TÍTULO | 2 elementos: `{{TITULO}}` Bebas 80 px (x=64 y=777; altura 96 px com 1 linha, 176 px com 2) · corpo = **um elemento com 2 trechos**: `"{{CORPO}}\n\n"` Poppins bold 40 px branco + `"{{FONTE}}"` Poppins bold 26,67 px cinza `#a6a6a6` (x=68 y=885 w=974, cresce para baixo) | FOTO 1109×943 em (−14.3, −17.47); DEGRADE 1109×813 em (0, 333.65); handle `@legacyexecutoria` (1 trecho só, w=568). **Trocar só `{{CORPO}}`**; sem fonte, `"\n\n{{FONTE}}"` → `""`. Trocar `"{{CORPO}}\n\n"` joga o último parágrafo no estilo da fonte (miúdo) |
| 4 | CTA | 1 elemento, x=56 **y=269** w=968, lh 1.1: `{{TITULO}}` azul `#013e6a` 46,67 px (renderiza em caixa-alta) · `{{P1}}` · `{{P1B}}` · `{{A1}}` · `{{P2}}` · `{{A2}}` · `{{P3}}` (P = preto **40 px**, A = azul 40 px). Texto da página: `{{TITULO}}\n\n{{P1}}\n\n{{P1B}}\n\n{{A1}} \n\n{{P2}}\n\n{{A2}} \n\n{{P3}}` | fundo claro (imagem); handle preto y=1354; seta preta. ~700 caracteres com 23 linhas terminam em y≈1290: acima disso, `format_text` menor ou subir a caixa |

**Card de reflexão em fundo preto** (a antiga pág. 5 saiu): pág. 3 com `delete_element` na FOTO, no
DEGRADE e no `rect` 21×17,5 em (179, 172) (aparece como um pontinho no preto); título + corpo
centralizados na altura (topo do título = (1440 − (96 + 12 + altura do corpo)) / 2). Frase em azul
dentro do corpo não dá (a caixa tem um trecho só de cor): fica branca, avisar na entrega.

## CLAILTON — `DAHWW8zqYcQ` (1080×1350, branco, post do X)

Link: https://www.canva.com/d/DmWX9pJp8ro6gbZ · Origem: "Nenhum funcionário se importa"
(`DAHWNGXt-To` p1, p2, p10), redimensionado de 2160×2700 (backup 2160: `DAHWWof0Xf8`, não usar —
o `merge-designs` falha com ele).

| Pág. | Tipo | Marcadores | Observações |
| --- | --- | --- | --- |
| 1 | CAPA | `{{H}}` Bebas 96 px lh 0.99 (x=58 y=521 w=963) · `{{SUB}}` Poppins medium 40 px (y=851) · contador `01/{{T}}` | header agrupado y=339 (avatar 117 px, "Clailton Luiz", selo, `@clailtonluiz`, contador Bebas 40 px op. 0.5) |
| 2 | CORPO | 1 elemento x=76 y=546 w=928, Poppins 40 px lh 1.4: `{{P1}} ` medium · `{{B1}}` bold · `\n\n` · `{{P2}} ` medium · `{{B2}}` bold · contador `{{N}}/{{T}}` | header y=364; texto cresce para baixo (até ~12 linhas) |
| 3 | CORPO LONGO | 1 elemento x=76 y=304: `{{P1}}` medium · `\n\n` · `{{B1}}` bold · `\n\n` · `{{P2}}` medium · contador `{{N}}/{{T}}` | header no topo y=122; cabe ~16 linhas |

## Comportamento da API (testado em 2026-09-26/27 — seguir à risca)

**Montagem**
- `merge-designs` aceita **uma operação por chamada**. `create_new_design` + `insert_pages` com
  `page_numbers` repetidos (ex.: `[1,2,2,2,3,4]`) funciona → é assim que o carrossel é montado.
- `copy-design` **não** aceita página repetida (erro enganoso "Design not found").
- Páginas mescladas ganham **IDs novos** de página e elemento → sempre um `read-design`
  (`open_transaction: true`, `fields: ["design_content"]`) no design novo. O texto dos marcadores
  identifica cada elemento; não precisa de thumbnail nessa leitura.

**Troca de texto (`find_and_replace_text`)**
- Substituição dentro de **um único trecho** mantém fonte, tamanho, cor e peso do trecho. ✅
- Substituição que **atravessa trechos** de estilos diferentes aplica o estilo do primeiro trecho a
  tudo (ex.: o azul vira preto). ❌ Nunca buscar um texto que cruze duas cores/pesos — exceção útil:
  `"{{H1}}\n"` → `""` apaga uma linha da capa sem efeito colateral.
- Quebra de linha `\n` dentro do texto novo cria parágrafos novos que **copiam os atributos do
  parágrafo anterior**. Por isso o `{{P1}}` do CTA (logo abaixo do título em caixa-alta) aceita
  **só um parágrafo, sem `\n`** — os demais parágrafos do primeiro bloco preto vão em `{{P1B}}`
  (que aceita `\n`). Todos os outros marcadores aceitam `\n` normalmente.
- ` ` (quebra suave) vira espaço — não usar.
- Marcador sem conteúdo: trocar por `""`. Para não sobrar linha em branco, apagar junto a quebra
  **que esteja no mesmo trecho** (ex.: `"\n\n{{P1B}}"` → `""`, tudo preto).
  No CTA, `"{{P1}}\n\n{{P1B}}\n\n"` é um trecho só: trocar por `""` tira os dois de uma vez.
- Apagar (`""`) um texto que atravessa trechos funciona sem efeito colateral: o que sobra mantém o
  estilo do próprio trecho (testado em 28/09/2026 separando a capa: `"\n{{H2}}\n{{H3}}"` → `""`).
  O problema de atravessar trechos só aparece quando se **insere** texto.
- Emoji funciona (🎁 👉).

**Ajuste de caber**
- `format_text` com só `font_size` muda o elemento inteiro e **preserva as cores de cada trecho**.
- **Não existe tamanho por linha dentro de uma caixa**: `format_text` vale para a caixa toda. Por
  isso a capa LEGACY tem uma caixa por linha (H1, H2, H3): cada uma recebe o seu `font_size`.
  O conector não duplica elemento nem cria texto em Bebas (`add_text` sai na fonte padrão); a
  separação foi feita uma vez no editor e vem pronta em toda capa montada do template.
- Número do painel do Canva = px × 0,75 (72 px aparece como 54). O conector trabalha em px.
- Caixa Bebas de 1 linha (lh 0.95): altura ≈ 1,19 × px (62 → 73,5; 80 → 96; 117 → 140,25). Bem
  maior que isso = a linha quebrou → baixar 1 px. Com o tamanho que o `medir.py` devolve (inteiro,
  para baixo, alvo 975 px numa caixa de 981) nenhuma linha quebrou nas capas testadas.
- Espaçamento entre as 3 caixas: o `medir.py capa` usa a mesma conta da antiga caixa única
  (topo da seguinte = topo + 1,099 × px − 0,149 × px da seguinte; base do bloco em y 1250),
  conferida nas capas Bets e Endividamento (28/09/2026).

**Logo da Legacy na capa** (padrão desde 28/09/2026; **desde 29/09/2026 já vem no template**)
- É um grupo na capa: `Logo.jpg` `MAHUzbG7AjM` recortado dentro da moldura (não aparece o fundo
  azul) + confete dourado `MAFAqYR48A0`. O `medir.py` devolve só o `position_element` do grupo
  (topo 150 px acima da H1, x 477,21), conferido no carrossel da Marisa (29/09/2026).
- É a versão do **mês de aniversário** (chapéu de festa + confete). Acabado o mês, o usuário troca o
  logo no template; se o grupo mudar de tamanho, atualizar `LOGO_LEFT`/`LOGO_ACIMA` no
  `medir.py`/`medir.mjs`. Logo sem fundo avulso, se precisar: `MAHWiBeuIzI`.
- `insert_fill`, `crop_media` e `group_elements` funcionam em designs novos; no template-mestre
  qualquer mudança precisa do ok explícito do usuário na conversa.

**Consertar capa de caixa única** (carrossel montado antes da separação, manchete toda num elemento)
1. Editor do Canva (navegador logado, ex.: Claude in Chrome): abrir
   `https://www.canva.com/design/<ID>/edit`, clicar uma vez na manchete (a barra mostra "Bebas Neue"),
   `Ctrl+D` duas vezes, `Esc`, esperar salvar e sair da página (evita conflito com o conector).
2. `read-design` com transação: aparecem 3 elementos iguais (o original e 2 cópias deslocadas 16 px).
3. Uma chamada `edit-design`: no 1º, apagar `"\n<linha 2>\n<LINHA 3>"`; no 2º, `"<linha 1>\n"` e
   `"\n<LINHA 3>"`; no 3º, `"<linha 1>\n<linha 2>\n"` (texto exato do `document`, com acento);
   depois as `operacoes` do `medir.py capa` nos 3 (H1 = 1º, H2 = 2º, H3 = 3º). Conferir a miniatura
   e a altura de cada caixa, commit. Feito assim nas capas Bets e Endividamento em 28/09/2026.
- Imagem redonda não se cria pelo conector: `insert_shape` só aceita cor (o `update_fill` falha:
  "no editable fill") e `replace_shape` não funciona em imagem inserida com `insert_fill`. O círculo
  do template foi colado no editor; nas capas ele vem junto com a página.
- Corpo com título (pág. 3) com mais de 8 linhas: manter 40 px e ancorar embaixo à mão —
  CORPO top = 1317 − (47 + 55 × (linhas − 1)); TITULO top = CORPO top − 12 − altura do título.
  Testado: 8 linhas → posição do template; 10 → CORPO 775 / TITULO 587; 11 → 720 / 532.
  O `medir.py pag3` faz essa conta; se o título passar acima de y 350, o corpo vai a 36 px, e se nem
  assim couber, avisa (card longo demais: contar na entrega). Quando o texto cobre quase o card todo,
  devolve `foto_util: false` e apaga a foto.
- Palavra sozinha na última linha de um parágrafo: estreitar a caixa do corpo com `resize_element`
  (só `width`, ex.: 920) muda a quebra sem mexer na fonte.
- Pág. 5 como card de reflexão: ~270 caracteres a 68 px = 11 linhas (altura 721) → top = 720 − altura/2.
- Medidas: `references/metricas.json` tem a largura de cada caractere da Bebas e da Poppins Bold
  medida no editor do Canva (2026-09-27); `scripts/medir.py` usa essa tabela. A quebra do corpo em
  Poppins leva um fator de 1,1% (calibrado: cards de 8, 10 e 11 linhas quebraram igual ao Canva).
- Corpo LEGACY (pág. 2) está ancorado embaixo: até 6 linhas a 53 px fica igual ao original; de 7 a
  9 linhas → `font_size` 44; 10+ linhas → 40 (teste: 10 linhas a 40 px ficaram perfeitas).
- `edit-design` devolve JSON + thumbnail a cada chamada: agrupar **todas** as operações de uma
  página numa chamada. `update_title` também exige `page_index`.
- A fonte não pode ser escolhida pela API → tudo parte das páginas-modelo, nunca de `add_text`.
- `format_text` só aceita `font_size` inteiro: o `medir.py` já devolve tamanhos inteiros.

**Imagens, degradê e foto (lidos no template em 2026-09-27)**
- Como achar cada elemento no `read-design` (os IDs mudam a cada montagem):
  - FOTO = `shape` com `fill.media` e `isMediaReplaceable: true`, ~1104–1109 de largura, top −10
    (capa) ou −17.47 (cards);
  - CIRCULO = `shape` com o caminho `M32 0A32 32 0 1 0 32 64…`, em x≈590 y≈278 (só na capa);
  - DEGRADE = `rect` com a imagem `MAFuE1lvpvY` (FADE.png, preto com transparência 1080×1350);
  - ignorar o `rect` 21×17.5 em (179, 172) dos cards e a seta (`MAFiAyIMtaY`).
- Curva do degradê (FADE.png, em `metricas.json`): transparente até ~49% da altura da imagem,
  54% de escuro a ~67%, 91% a ~80%, preto a partir de ~89%. Na pág. 3 do template: 14% em y 537,
  54% em y 681, **~76% no topo do título (y 776.6)**, 91% em y 860.
- **Regra**: o topo do texto (título na pág. 3, primeira linha na pág. 2, manchete na capa) fica
  onde o degradê está pelo menos tão escuro quanto no template (~76%; capa 70%). Texto que sobe →
  o DEGRADE sobe junto (`position_element`); se o fim do degradê ficar acima do fim da foto, a FOTO
  sobe o mesmo tanto (senão aparece uma faixa clara da foto atrás do corpo). Nunca descer. O
  `medir.py` (`capa`, `pag3`, `pag2`) calcula tudo e devolve as `operacoes` prontas.
- Simulação com as fotos do teste e o degradê real: parado, o card 6 ficou com o título em
  "atenção" (luz 31, variação 32); acompanhando o texto, os 5 cards ficaram "ok" (luz 3–23 de 255).
- `update_fill` troca a imagem de FOTO/CIRCULO (`asset_type: "image"`, `asset_id`, `alt_text`).
  **Testado em 28/09 no carrossel da Chilli Beans** (capa, círculo e cards 2 a 6): a imagem entra
  centralizada, cobrindo a moldura (o `imageBox` é recalculado). Na mesma chamada funcionaram
  `position_element` no DEGRADE e na FOTO e, no handle, `find_and_replace_text` com `\n`,
  `resize_element` (width) e `format_text` (`text_align`). Em shape criado com `insert_shape` (só
  cor) o `update_fill` dá "no editable fill". Se falhar numa moldura, deixar a foto de exemplo e
  mandar o link da imagem escolhida na lista "trocar foto".
- Texto do handle é Poppins Bold 24 px em caixa-alta com espaçamento 0,07: cabe ~850 px por linha
  nos cards (a seta começa em x 926) e ~900 na capa. Crédito mais longo que isso vai na legenda.
- Subir imagem: `upload-asset-from-url` (só endereço público; usado em 26/09 para as fotos de
  exemplo) ou `create-upload-url` + POST dos bytes crus (`Content-Type: application/octet-stream`)
  → `{"mediaId": "…"}` (Claude Code: 7 imagens de até 4 MB em 28/09, sem erro). Enviar com `curl`:
  pelo `urllib` do Python o Canva devolve 403 (o endereço continua valendo; refazer com curl). No
  Windows, endereço lido de arquivo gerado pelo Python leva `\r` no fim: limpar com `tr -d '\r'`.
- `get-assets` devolve a miniatura (~200 px) de cada imagem, visível para o Claude, com largura e
  altura: serve de "folha de contato" quando não há Python/rede (testado em 27/09).
- `crop_media` (ajustar o enquadramento dentro da moldura) existe mas não foi testado: para centralizar
  o sujeito, recortar antes no Magnific (`images_crop`) ou localmente.
- Editar designs pelo conector no modo automático do Claude Code pode ser bloqueado pelo
  classificador de permissões ("Modify Shared Resources"), até em rascunho descartado, quando o
  usuário não pediu aquela edição. Com o pedido explícito dele na conversa ("coloca as imagens no
  carrossel"), passou. Nunca contornar um bloqueio.
