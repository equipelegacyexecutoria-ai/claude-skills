# Imagens de cada card (LEGACY)

Método validado no teste da Chilli Beans (27/09/2026, relatório em
`Desktop\Projetos Edições\Designe\teste-imagens-chilli-beans\RELATORIO.html`): nota média 8,5/10
contra 1,3 da busca ingênua ("primeiro resultado do banco"). O que dá a precisão: **fonte certa
para cada tipo de card → briefing → buscas curtas → escolher olhando → conferir no card**.

## 1. Quais vagas

| Página | Vaga | Observação |
| --- | --- | --- |
| Capa (pág. 1) | foto de fundo + círculo | direção de arte própria (§1b); o círculo nunca some e fica do lado oposto ao sujeito/ponto de fuga do fundo |
| Corpo (pág. 2) e corpo com título (pág. 3) | 1 foto por card | só se o `medir.py` disser `foto_util: true` |
| CTA (pág. 4) e reflexão em fundo preto (pág. 3 sem foto) | nenhuma | fundo próprio |
| CLAILTON | nenhuma | avatar fixo |

Pular a etapa inteira quando o usuário disser "sem imagens" / "eu coloco as fotos". Se ele mandar
imagens (link ou arquivo), usar as dele na vaga indicada. Dica de imagem na copy ("Imagem: foto do
fundador") vira o briefing daquela vaga.

## 1b. Capa: a imagem que para o dedo (regra de 28/09/2026)

A capa tem que ser **chamativa, forte e bonita**. Reprovado pelo usuário: fachada da marca "parada"
no fundo ("não tem nada com nada") e círculo com a placa cortada. Aprovadas (abrir só se precisar
rever o estilo): `DAHWgdFSrXw` (maior onda de recuperações: rua de lojas fechadas + círculo Casas
Bahia com "Recuperação judicial"), `DAHWNvVN9yc` (Ponto Frio decadente, IA), `DAHS7bmRxys`.

**Fundo = a cena que prova a manchete, no estado dramático.** Quem olha só a foto já entende a
manchete: "empresas quebrando" → rua inteira de lojas com a porta de aço baixada; "a rede quase não
existe mais" → a loja da marca decadente e fechada; "dívida trava o consumo" → carrinho vazio,
prateleira, gente preocupada. Nunca a fachada comum da marca ou um prédio qualquer.
- Foto real só quando ela é forte (a cena inteira, perspectiva, drama) e grande (lado menor
  ≥ 1400 px ou ampliável 2x). Foto de pandemia (máscara) ou com mensagem misturada (placa de
  "oferta") não serve.
- Senão, **IA fotorrealista**: Nano Banana Pro (`mode: "imagen-nano-banana-2"`, `resolution: "2k"`,
  `aspectRatio: "1:1"`, `count: 2`). Cena brasileira, sem logo de marca real no fundo.
- Composição: o sujeito ou o ponto de fuga fica do lado **oposto** ao círculo (é isso que decide o
  `--circulo` do `medir.py manchete`); o terço de baixo escurece para a manchete; nada importante
  no centro, a ~y 810–960, onde entra o logo.

**Círculo = o protagonista + o fato, numa montagem.** A fachada, o produto ou o logo real da
história junto com o símbolo do acontecimento: documento "RECUPERAÇÃO JUDICIAL" + martelo de juiz,
seta vermelha de queda, placa "FECHADO", céu de tempestade. Nano Banana Pro com a **foto real da
marca como referência** (`references: [{type: "image", identifier: <creation da foto>}]`), 1:1, 2k,
`count: 2`. A placa/logo inteira e centralizada; nada importante nas bordas (vira círculo); fundo
escuro nas quinas (não pedir "círculo" no prompt: a IA desenha um e sobram cantos brancos).
- Só símbolo de fato **verdadeiro para aquela empresa** (recuperação judicial só se ela pediu).
- Nunca gerar rosto de pessoa real; pessoa real no círculo só com foto real confirmada (§2).
- Foto real no círculo continua valendo quando já conta a história sozinha (ex.: o fundador na
  Chilli Beans); se a placa sai cortada, é montagem.

Prompts aprovados (28/09/2026, trocar só a cena):

```
Fundo: Cinematic editorial photograph, photorealistic. A long commercial street in downtown São
Paulo, Brazil, where every shop has its metal roll-down shutter pulled down and closed. Faded
storefront signs, a few handwritten 'ALUGA-SE' signs taped on the shutters, [...], empty sidewalk
with black-and-white Portuguese stone pavement, one lone pedestrian far away. Strong one-point
perspective: the street recedes toward a vanishing point in the right third of the frame, while
large closed shutters fill the left side. Overcast, moody late-afternoon light, slightly
desaturated colors, deep shadows. The lower third of the frame is darker and uncluttered for text
overlay. 35mm lens, high detail, no watermark, no brand logos.

Círculo: Photorealistic editorial news composite, square. Use the [MARCA] store from the reference
image, now seen from outside at street level: the complete '[MARCA]' sign fully visible and
centered in the upper-middle of the frame, the glass storefront with the lit store interior below
it. Dramatic dark stormy sky above. In the foreground, lying on a table, a printed legal document
with the bold title 'RECUPERAÇÃO JUDICIAL' and a wooden judge's gavel next to it. A glowing red
downward stock-market arrow cuts across the sky. Moody cinematic light, high contrast. Keep every
key element inside the central circle-safe area because the image will be cropped to a circle.
No other text, no watermark.
```

Escolher na folha (`imagens.py folha`) a melhor de cada par. Custo: 4 × 75 créditos. Imagem de IA
não leva crédito; capa toda em IA → rodapé só `@legacyexecutoria`.

## 2. Roteador: de onde vem a imagem

| O card fala de… | Fonte | Cai para a próxima quando… |
| --- | --- | --- |
| **Fato de notícia, empresa, pessoa, lugar ou número real** (capa de notícia, "o tamanho do império", "a dívida") | **foto real**: matérias sobre o fato, site/imprensa da marca, Wikimedia Commons (com crédito) | não há foto do fato; a pessoa não tem identidade confirmada; resolução impossível mesmo com 2x |
| **Situação humana comum** (o dono no aperto, reunião, equipe, cliente) | **banco Freepik**, foto real (sem IA) | a melhor candidata fica abaixo de 7 na rubrica |
| **Ideia abstrata, lição, metáfora** ("marca não paga a conta") | **IA** (Seedream 5 Pro) com o sentido exato do card | — |

Regras que o usuário deu: notícia pede foto real (do Google/portais) sempre que existir; IA só quando
não houver foto real que diga a mesma coisa. **Pessoa real só com identidade confirmada** por legenda
ou fonte oficial; retrato sem legenda "que parece ser" o executivo é descartado. Em card de notícia,
IA nunca imita pessoa real: pedir pessoas genéricas, de costas ou em silhueta.

Capa: não passa por este roteador, segue o §1b (fundo = cena que prova a manchete; círculo =
protagonista + fato, montagem de IA a partir da foto real quando preciso).

## 3. Briefing (sem ferramenta, junto com o planejamento)

Para cada vaga, em 1–2 linhas:
`tipo · mensagem do card em até 8 palavras · sujeito + ação · emoção · cenário brasileiro · onde o
sujeito fica (sujeito_entre_pct do medir) · evitar` + 2 a 4 buscas curtas.

- Notícia: buscas em português com o nome certo ("Chilli Beans dívida reestruturação", "Caito Maia").
  A fonte citada na copy ("Rodapé: fonte NeoFeed") entra primeiro.
- Banco: buscas em inglês, concretas, de 2 a 5 palavras ("small shop owner counting money night").
- IA: o prompt descreve a cena que prova a frase do card, não o tema genérico.
- Evitar sempre: dólar (o dinheiro é real, R$), cenário claramente estrangeiro, clichê de banco
  (aperto de mão, gente sorrindo para a câmera), texto na imagem.

## 4. Buscar (em paralelo com a montagem no Canva)

**Foto real de notícia**
1. Busca na web (web_search) com 2–3 buscas; pegar 2–4 matérias do assunto, das mais recentes.
2. Com Python e internet (Claude Code; claude.ai com acesso à rede liberado na execução de código):
   `python3 scripts/imagens.py coletar URL1 URL2 URL3` → baixa as fotos das matérias já no tamanho
   original (tira o `-1200x675` do endereço), com legenda e crédito, e marca as de outras matérias
   como `[fora do assunto?]`. Pessoa ou marca: `python3 scripts/imagens.py wikimedia "Nome"` →
   original, tamanho, licença e crédito pronto.
   **Agência Brasil** (agenciabrasil.ebc.com.br) é a melhor fonte para card de economia: foto real,
   brasileira, uso livre com crédito, original de 4000–6000 px. O `coletar` volta vazio lá (o site
   recusa download sem Referer). Caminho testado em 28/09/2026: web_search com `allowed_domains`
   no site → na página, o `og:image` traz o original depois de `/1600x800/`
   (`…/sites/default/files/…jpg`) → `curl -e "https://agenciabrasil.ebc.com.br/" -o foto.jpg URL`.
   Crédito = atributo `title` da imagem na página (`Nome/Agência Brasil`).
3. Sem rede na execução de código: ler a matéria com web_fetch e procurar o endereço da imagem
   principal (og:image, `.jpg/.webp` do texto) e a legenda "Foto: …"; tirar o sufixo de tamanho do
   endereço. Wikimedia pelo web_fetch:
   `https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6&gsrsearch=NOME&gsrlimit=5&prop=imageinfo&iiprop=url|size|extmetadata`

No Claude, o conector do Freepik aparece como **Magnific** (banco, IA, ampliação e recorte; mesmos créditos).

**Banco (Freepik, pelo Magnific)** — `stock_search` com `query` (inglês), `content_type: "photo"`,
`ai_generated: "excluded"`, `orientation: "landscape"`. Devolve 50 itens com título e prévia: separar
3–4 pelo título. A escolhida é baixada só no fim (`stock_download`, passo 6).

**IA (Magnific)** — `images_generate` com `mode: "seedream-5-pro"` (100 créditos, 2304×1728 em 4:3),
`aspectRatio: "4:3"` (pág. 3) ou `"1:1"` (capa e pág. 2), `count: 1` (2 só no card mais importante).
Depois `creations_wait` (até 25 s por chamada; a imagem leva ~60 s) e `creations_get` para a `url`.
Alternativa: Nano Banana Pro (`mode: "imagen-nano-banana-2"`, 75 créditos, sai em 1k se não pedir
resolução maior). Anatomia do prompt (em inglês), testada:

```
Cinematic editorial photograph. [cena concreta que prova a frase do card, com pessoas/lugar
brasileiros]. [o contraste ou a tensão da mensagem em uma frase]. [sujeito] placed in the upper
[metade/terço] of the frame; the lower part falls into deep, clean shadow, dark and uncluttered for
text overlay. Low-key light, high contrast, realistic skin texture, 35mm lens, shallow depth of
field, no text, no logos, no brand names, no watermarks.
```

Exemplo aprovado (card "marca forte e criatividade não pagam a conta"): óculos de grife brilhando
num foco de luz ao lado de uma caixa de dinheiro de madeira vazia, meio engolida pela sombra.

## 5. Escolher olhando

- **Com Python** (Claude Code; claude.ai com rede): `python3 scripts/imagens.py folha folha.jpg
  arquivo1 url2 … --titulo "Card 3"` → grade numerada (até 12 por folha) e olhar a folha.
- **Sem Python/rede**: subir as 2–3 melhores candidatas no Canva (`upload-asset-from-url`, uma
  chamada por imagem, em paralelo) e chamar `get-assets` com os IDs: devolve a miniatura (~200 px) de
  cada uma, visível para o Claude, com largura e altura. As que não forem usadas ficam só nos uploads.

Rubrica (0–10, ponderada): **precisão com a mensagem 35 · impacto/emoção 20 · encaixe 20** (sujeito
dentro de `sujeito_entre_pct`, nada importante na parte que o degradê cobre, na capa fora do círculo)
**· qualidade técnica 15 · coerência com os outros cards 10**. Usar só nota ≥ 7; guardar a 2ª melhor
como reserva.

Eliminatórios: marca-d'água; texto ou legenda embutidos (fachada/logo da própria marca pode);
rosto ou mão deformados; dinheiro em dólar ou cenário estrangeiro óbvio; pessoa sem identidade
confirmada; logo sozinho; resolução "pequena demais" no `escala`.

## 6. Preparar

- **Resolução**: `python3 scripts/imagens.py escala LARGURA ALTURA` (ou a coluna do `coletar`).
  "ampliar 2x" → Magnific: `creations_upload_image` (url) → `images_upscale` (`mode: "ultra-photo"`,
  `scale: "2x"`, `precisionPreset: "balanced"`; 90 créditos, ~45 s) → `creations_wait` →
  `creations_get` (url). "pequena demais" → descartar. Foto de matéria costuma vir em 1200×675: na
  moldura do card precisa crescer 1,4x, na capa 1,7x.
- **Círculo**: rosto ou objeto no centro. `images_crop` na criação (`aspectRatio: "1:1"`,
  `auto: true`, `prompt: "the man's face"`; 1 crédito). Claude Code também pode recortar local:
  `python3 scripts/imagens.py recortar FOTO saida.jpg --centro X,Y --lado L`.
- **Banco**: `stock_download` (`id`) → `downloadUrl` (link assinado, vale por algumas horas).
- **Sujeito no lugar errado**: se ele fica na parte que o degradê cobre, preferir outra candidata;
  em último caso, recortar no Magnific (`images_crop` com `auto: true` e o sujeito no `prompt`).

## 7. Colocar no Canva e conferir

1. `upload-asset-from-url` para cada imagem escolhida (endereço público: foto da matéria,
   Wikimedia, `downloadUrl` do banco ou `url` da criação do Magnific), todas em paralelo → `asset_id`.
   Site que bloqueia a importação → importar no Magnific (`creations_upload_image`) e usar a `url` da
   criação. **Testado em 28/09/2026**: o Canva recusa ("Invalid download url") os links do banco
   Freepik (`downloadscdn…magnific.com`) e das criações do Magnific (`pikaso.cdnpk.net`), e o
   Magnific não importa a foto original da Agência Brasil pelo link (o site exige Referer). Nos dois
   casos: baixar com `curl` e subir o arquivo (Canva: `create-upload-url` + POST abaixo; Magnific:
   `creations_request_upload` + PUT do arquivo + `creations_finalize_upload`). Foto de banco de
   8000 px: reduzir para 3000 px antes de subir. Arquivo local (só Claude Code): `create-upload-url` e enviar os bytes com
   `curl -X POST -H "Content-Type: application/octet-stream" --data-binary @arquivo.jpg "<uploadUrl>"`
   → `{"mediaId": "…"}`.
2. Na **mesma** chamada `edit-design` da página (a do texto): `update_fill` na FOTO (e no CIRCULO
   da capa) com `asset_type: "image"`, o `asset_id` e um `alt_text` curto, + as `operacoes` do
   `medir.py` (DEGRADE e FOTO) + o crédito no handle (`copy.md`).
3. A resposta traz a miniatura da página: conferir **sujeito visível acima do degradê, título e corpo
   legíveis, nada estranho** (texto, marca-d'água, dedo a mais). Falhou → reserva (outro upload +
   `update_fill`). No máximo 1 troca por card; se a reserva também falhar, deixar a melhor e avisar.

## 8. Crédito e direito de uso (resumo, não é parecer jurídico)

| Origem | Crédito no card | Risco |
| --- | --- | --- |
| Foto oficial da marca (imprensa, site, "Divulgação") | `Foto: Marca/Divulgação` | baixo |
| Foto de matéria | como está na legenda (`Foto: Autor/Veículo`; `Reprodução/…` quando a matéria diz) | médio; foto de revista/agência como destaque é o maior risco: preferir a oficial |
| Wikimedia Commons | `Foto: Autor/Wikimedia Commons (licença)` | baixo, com o crédito completo |
| Banco Freepik (plano pago) | nenhum | baixo |
| IA | nenhum | baixo (sem rosto real, sem logo) |

- "Divulgação" só quando a foto é da própria empresa. Nunca inventar autor.
- Pessoa pública só no contexto da notícia (direito de imagem).
- Termos do Freepik: não usar foto do banco como referência para gerar imagem de IA.
- Na entrega, listar todos os créditos numa linha pronta para a legenda do post.

## 9. Custos e tempo (medidos no teste)

| Item | Créditos (Magnific/Freepik) | Tempo |
| --- | --- | --- |
| Busca na web, coleta das matérias, Wikimedia, `stock_search` | 0 | ~1 min, em paralelo |
| Imagem de IA Seedream 5 Pro | 100 cada | ~60 s (em paralelo) |
| Nano Banana Pro | 75 cada | ~40 s |
| Ampliação 2x (Magnific ultra-photo) | 90 | ~45 s |
| Recorte automático | 1 | segundos |
| Foto do banco baixada | 40 a 150 | segundos |

Carrossel típico (6 vagas de foto): 300 a 800 créditos. A etapa de imagens cabe em ~3–4 min porque
roda enquanto o Canva monta e preenche.

## 10. Sem o conector Magnific

Só foto real (matérias, marca, Wikimedia) e escolha pelas miniaturas do `get-assets`. Vaga de banco
ou de IA sem foto real boa: deixar a foto de exemplo do template e pôr o card na lista "trocar foto".
Avisar uma vez que o conector Magnific (Freepik) completa essas vagas.
