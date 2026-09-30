---
name: carrossel-canva
description: Monta no Canva, já diagramado e com as imagens colocadas, um carrossel de Instagram nos dois padrões do usuário — LEGACY (1080×1440, escuro, foto por card, capa com manchete Bebas em 3 linhas de mesma largura, pergunta dourada e círculo com imagem, card de reflexão em fundo preto e CTA em fundo claro) e CLAILTON (1080×1350, post estilo X/Twitter em fundo branco com avatar, @clailtonluiz e contador NN/NN) — a partir da copy card a card. No LEGACY, busca e coloca sozinha a imagem de cada card (foto real de notícia/marca com crédito, banco Freepik ou IA, conforme o card) e ajusta fonte, posição e degradê ao tamanho de cada texto. Use sempre que o usuário mandar a copy de um carrossel e pedir para "montar/diagramar no Canva", "fazer o carrossel no Canva", "passa pro Canva", "carrossel LEGACY", "carrossel do Clailton", ou colar slides (SLIDE 1, Card 1…) pedindo o projeto no Canva. Não use para escrever a copy (legacy-carrossel-copy) nem para HTML/Figma (carrossel-legacy-html).
---

# Carrossel no Canva — padrão LEGACY e CLAILTON

Entrega: **um design novo no Canva**, com todos os cards na ordem, textos nas fontes/cores/posições
dos carrosséis reais do usuário e, no LEGACY, **a imagem certa em cada card** (capa, círculo e
corpos), com o degradê posicionado para o texto ficar legível e o crédito das fotos. O ganho está na
diagramação e na escolha das imagens: não improvisar layout nem pegar a primeira foto que aparecer.

**Meta: no máximo 10 minutos por carrossel, imagens incluídas.** Tudo o que precisa ser decidido já
está nas referências e nos scripts: não medir fonte na hora, não abrir carrosséis de referência, não
abrir o editor do Canva. As buscas e gerações de imagem rodam **em paralelo** com a montagem.

Requisitos: conector do **Canva** (conta com os templates-mestre) e, para banco e IA, o conector do
**Magnific** (é o do Freepik: banco de imagens, IA, ampliação); busca na web ligada. Funciona no Claude Code e no Claude do navegador
(claude.ai, com execução de código ligada; com acesso à rede liberado, a coleta de fotos é mais
rápida). Sem as ferramentas do Canva (`merge-designs`, `read-design`, `edit-design`) na conversa,
pedir ao usuário para ligar o conector antes de começar. Sem o Magnific, seguir só com fotos reais
(`imagens.md` §10).

Referências (ler só quando precisar):
- `references/template.md` — IDs, mapa de páginas/elementos (foto, degradê, círculo) e **o que a API
  do Canva faz e não faz**. Ler antes da 1ª execução da sessão.
- `references/copy.md` — classificar os cards, o que vai em cada marcador, regra da capa, textos de
  tamanhos diferentes, crédito no rodapé.
- `references/imagens.md` — de onde vem cada imagem, briefing, busca, escolha, crédito, custos.
- `scripts/medir.py` (ou `node scripts/medir.mjs`) + `references/metricas.json` — larguras reais das
  fontes e curva do degradê do Canva; devolve, para o texto que veio, fonte, posições e as
  `operacoes` de cada página. Bate com a quebra real do Canva.
- `scripts/imagens.py` — coleta de fotos de matérias, Wikimedia, folha de contato, escala, recorte.
- `references/recriar-templates.md` — só se um template sumir ou for outra conta do Canva.

## Regras fixas

1. **Formato**: LEGACY ou CLAILTON. Se o usuário não disse, **perguntar** (uma pergunta curta, junto
   com qualquer outra dúvida real da copy) e não montar antes da resposta.
2. **Copy intocada**: não reescrever, resumir nem "melhorar" a copy. Só distribuir nos marcadores,
   quebrar linhas e marcar destaques (negrito/azul/cinza/dourado) conforme `copy.md`.
3. **Nunca** usar `create-design`, `generate-design` ou `add_text`: não respeitam fontes e layout.
   Tudo parte dos templates-mestre via `merge-designs`.
4. **Não mexer nos templates-mestre** (LEGACY `DAHWWhuFIEI`, CLAILTON `DAHWW8zqYcQ`) — só usá-los
   como fonte das páginas.
5. Salvar (`commit`) só depois de mostrar a prévia e o usuário aprovar (exigência do Canva).
6. **Capa LEGACY em 3 linhas de mesma largura**: manchete em duas linhas brancas (a quebra sai do
   `medir.py manchete`, que deixa as duas grandes) e a pergunta/frase de impacto em dourado, cada
   frase numa linha só, cada linha com o tamanho que a faz ocupar a largura toda (`copy.md`). Só o
   tamanho da fonte muda de uma linha para outra; o texto não. No template, cada linha tem a sua
   caixa (`{{H1}}`, `{{H2}}`, `{{H3}}`), então a capa sai pronta pelo conector. Capa com linhas de
   larguras diferentes não se entrega (reprovada em 28/09/2026). A cor padrão não muda por nota de
   cor na copy.
7. **Capa LEGACY com círculo (462 px) e logo**: o círculo nunca some e fica do lado oposto ao
   sujeito da foto de fundo; o logo da Legacy (com o confete) entra acima da manchete. Os dois vêm
   nas `operacoes` do `medir.py manchete`/`capa`.
8. **Texto sempre legível, qualquer que seja o tamanho**: fonte, posição do texto, do degradê e da
   foto saem do `medir.py` para o texto real de cada card. Texto que sobe leva o degradê junto.
9. **Imagem pela natureza do card** (`imagens.md`): notícia/entidade real → foto real com crédito;
   situação humana comum → banco Freepik (sem IA); ideia abstrata → IA. Pessoa real só com
   identidade confirmada. Escolher olhando (folha ou miniaturas), nunca pelo 1º resultado.
10. **Capa chamativa, forte e bonita** (reprovada em 28/09/2026 a capa com fachada genérica no fundo
   e placa cortada no círculo): fundo = a cena que prova a manchete; círculo = a montagem
   protagonista + fato, com placa/logo inteiros. Direção de arte, prompts e referências aprovadas em
   `imagens.md` §1b. A capa ganha 2 variações de cada imagem para escolher olhando.

## Fluxo rápido

**1. Planejar e calcular (sem Canva).** Classificar cada card e montar a lista de páginas-modelo:
- LEGACY (template de 4 páginas desde 29/09/2026): capa=1, corpo=2, corpo com título=3, CTA=4 →
  ex. `[1,3,3,3,3,3,4]`. Card de reflexão em fundo preto = pág. 3 sem foto (`template.md`). Não há
  mais página do bônus 1%: se a copy pedir, avisar o usuário.
- CLAILTON: capa=1, corpo curto=2, corpo longo e CTA=3 → ex. `[1,2,2,2,2,2,2,2,2,3,3]`.

Rodar o script **numa única execução** para todos os cards (claude.ai: `python3`; sem Python:
`node scripts/medir.mjs`):
- `medir.py manchete "Manchete inteira" "Pergunta" --circulo esquerda|direita` → quebra a manchete
  em H1 + H2 e devolve as `operacoes` prontas: `format_text` e `position_element` de H1, H2 e H3
  (tamanho inteiro que enche a largura), CIRCULO (462 px, lado pedido), `position_element` do
  LOGO (o grupo logo + confete que já vem na capa do template) + degradê/foto. O lado do círculo sai da
  composição da foto de fundo (`imagens.md` §1b); na dúvida, `direita`. Se a copy já trouxer as
  duas linhas separadas de propósito, `medir.py capa "Linha 1" "Linha 2" "Pergunta"` (mesma saída).
- `medir.py pag3 "Título" "Parágrafo 1" "Parágrafo 2" …` → título quebrado, fonte do corpo, largura,
  posições e `operacoes` (TITULO, CORPO, DEGRADE, FOTO), `sujeito_entre_pct`, `foto_util`, `aviso`.
  Card com fonte na copy ("Rodapé: fonte X"): passar `"Fonte: X, 2026."` como último parágrafo
  (a linha `{{FONTE}}` fica dentro da caixa do corpo e ocupa o espaço de ~1 parágrafo).
- `medir.py pag2 "Parágrafo 1" …` → o mesmo para o corpo simples (fonte 53/44/40).
- CTA: `medir.py corpo … --tam 37.33 --larg 967`.

No LEGACY, escrever junto o **briefing de imagem** de cada vaga com `foto_util: true` (tipo pelo
roteador, mensagem, sujeito, onde o sujeito fica = `sujeito_entre_pct`, 2–4 buscas ou o prompt).

**2. Montar + disparar as imagens — uma única mensagem com as chamadas em paralelo:**
`merge-designs` (`create_new_design`, `title: "<headline curta> | LEGACY"`, `insert_pages` com a
lista) + buscas na web das vagas de notícia + `stock_search` das vagas de banco + `images_generate`
das vagas de IA + as **duas imagens da capa** (fundo e círculo, `count: 2` cada, `imagens.md` §1b). Se o template der "not found"/sem acesso: `search-designs` com `"TEMPLATE
CARROSSEL"` (LEGACY = 4 páginas 1080×1440; CLAILTON = 3 páginas 1080×1350), seguir com esse ID e
avisar para atualizar a skill. Não achou → `recriar-templates.md`.

**3. Ler os IDs + coletar — em paralelo:** `read-design` (`open_transaction: true`,
`fields: ["design_content"]`, sem thumbnails) → `locator_id` dos marcadores (na capa, as 3 caixas
`{{H1}}`, `{{H2}}`, `{{H3}}`), do handle, da FOTO, do CIRCULO e do DEGRADE de cada página (como
achar: `template.md`). Junto: fotos das matérias
(`imagens.py coletar` ou web_fetch), `imagens.py wikimedia` se houver pessoa/marca, `creations_wait`.

**4. Escolher e subir as imagens.** Folha de contato (`imagens.py folha`) ou, sem Python/rede,
`upload-asset-from-url` das 2–3 melhores + `get-assets`. Rubrica e eliminatórios em `imagens.md` §5;
escolhida + reserva por vaga. Preparar só o necessário (ampliar 2x, recortar o círculo,
`stock_download`) e subir todas as escolhidas com `upload-asset-from-url` em paralelo.

**5. Preencher** — **uma** chamada `edit-design` (`keep_open`) **por página**, com tudo junto:
`find_and_replace_text` de cada marcador (o marcador inteiro, dentro de um único trecho),
`update_fill` da FOTO/CIRCULO, as `operacoes` do `medir.py`, crédito no handle, contador
`{{N}}/{{T}}` no CLAILTON. A resposta traz a miniatura: conferir ali mesmo (nenhum `{{`, texto
dentro da área, cores certas, capa sem linha quebrada, **sujeito da foto visível e texto legível**)
e corrigir na hora; imagem ruim no card → a reserva (no máximo 1 troca por card).

Capa LEGACY (detalhe em `copy.md`): `find_and_replace_text` de `{{H1}}`, `{{H2}}` e `{{H3}}`, cada um
na sua caixa, `update_fill` da FOTO e do CIRCULO + as `operacoes` do `medir.py manchete` (H1–H3,
CIRCULO e o `position_element` do grupo do LOGO), tudo numa chamada só. Sai pronta, sem ajuste
no editor. Conferir no `document` que cada caixa de H ficou com **1 linha** (altura ≈ 1,2 × fonte;
bem maior = quebrou → baixar 1 px naquela caixa) e, na miniatura, que o logo não caiu sobre algo
importante da foto e que a placa do círculo está inteira.

Armadilhas (detalhes em `template.md`):
- CTA LEGACY: `{{P1}}` **sem `\n`** (1º parágrafo); o resto do bloco preto vai em `{{P1B}}`.
- Marcador vazio → `""`, apagando junto a quebra do mesmo trecho (`"\n\n{{P1B}}"`,
  `"{{BRANCO}}\n\n"`) para não sobrar linha em branco.
- Nunca buscar texto que atravesse duas cores/pesos (o estilo do 1º trecho contamina o resto).
- Pág. 3 (corpo com título): trocar só `"{{CORPO}}"`; sem fonte, apagar `"\n\n{{FONTE}}"` → `""`.
  Nunca trocar `"{{CORPO}}\n\n"`: o último parágrafo cai na linha da fonte e sai miúdo (se
  acontecer: `format_text` `font_size` 40 no elemento todo).
- Palavra sozinha na última linha ou "R$" separado do número: espaço inseparável (` `) no
  lugar do espaço (`"R$ 400"`, `"os juros."`). Não muda o texto, só a quebra.
- `format_text` só aceita tamanho inteiro. `merge-designs` aceita uma operação por chamada.

**6. Entregar** — mostrar as miniaturas das respostas do passo 5 (se a interface não exibir
imagens, mandar os links, um por card) e perguntar se pode salvar. Com o ok:
`edit-design finalize: commit`. Responder curto com:
- link de edição do design (`edit_url`);
- de onde veio cada imagem (real/banco/IA) e a linha de créditos pronta para a legenda do post;
- "trocar foto": só as vagas sem imagem boa (CLAILTON: nenhuma), com a melhor opção achada;
- ajustes feitos para caber (ex.: "card 5 com o corpo em 36 px") e os `aviso` do script.

Ajustes depois do commit ("troca a foto do card 4", "usa foto real no card 3"):
`read-design open_transaction` + `edit-design` nas páginas citadas, prévia, commit.

## Economia

- Não ler os carrosséis de referência nem os templates a cada execução — tudo que importa está em
  `references/` e nos scripts. Só reler um template se um `find_and_replace_text` falhar.
- Uma leitura de estrutura (passo 3); as miniaturas vêm das próprias edições.
- Chamadas independentes sempre na mesma mensagem (montagem, buscas, gerações, uploads).
- Sem subagentes e sem editor do Canva. IA: `count: 1` por vaga (2 só no card mais importante).

## Manutenção dos templates

Se o usuário mudar o padrão (nova cor, novo tipo de card): copiar a página de um carrossel novo para
o template com `merge-designs modify_existing_design` + `insert_pages`, trocar os textos por
marcadores **trecho a trecho, sem inserir `\n`** (quebra inserida cria parágrafo que herda o estilo
do anterior) e atualizar `references/template.md`. Nunca redigitar a página do zero.
Se mudar a foto, o degradê ou as molduras, atualizar as medidas de `PAG` no `medir.py`/`medir.mjs`
(lidas pelo `read-design` com transação). Passo a passo completo em `references/recriar-templates.md`.

Carrossel antigo com a manchete da capa numa caixa só (feito antes de 28/09/2026 à noite) e o
usuário pede para acertar a capa: roteiro em `template.md` ("Consertar capa de caixa única").
