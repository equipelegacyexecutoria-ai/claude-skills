# Imagens de cada card (LEGACY)

Método validado no teste da Chilli Beans (27/09/2026, relatório em
`Desktop\Projetos Edições\Designe\teste-imagens-chilli-beans\RELATORIO.html`): nota média 8,5/10
contra 1,3 da busca ingênua ("primeiro resultado do banco"). O que dá a precisão: **fonte certa
para cada tipo de card → briefing → buscas curtas → escolher olhando → conferir no card**.

## 1. Quais vagas

| Página | Vaga | Observação |
| --- | --- | --- |
| Capa (pág. 1) | foto principal + círculo | o círculo nunca some; sujeito da foto principal à esquerda ou no centro (o círculo ocupa x 590–1022, y 278–711) |
| Corpo (pág. 2) e corpo com título (pág. 3) | 1 foto por card | só se o `medir.py` disser `foto_util: true` |
| CTA, bônus, reflexão (págs. 4 e 5) | nenhuma | fundo próprio |
| CLAILTON | nenhuma | avatar fixo |

Pular a etapa inteira quando o usuário disser "sem imagens" / "eu coloco as fotos". Se ele mandar
imagens (link ou arquivo), usar as dele na vaga indicada. Dica de imagem na copy ("Imagem: foto do
fundador") vira o briefing daquela vaga.

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

Círculo da capa: o segundo elemento da história. Notícia sobre empresa → rosto do fundador/CEO
(confirmado) ou o produto; se a foto principal já é a pessoa, o círculo leva a marca/loja/produto.

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
   criação. Arquivo local (só Claude Code): `create-upload-url` e enviar os bytes com
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
