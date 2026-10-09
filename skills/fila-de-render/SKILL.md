---
name: fila-de-render
description: Processa a fila de vídeos do Notion no PC de render — lê os cards das colunas CLAUDE e "Correções (Claude)" do Calendário Editorial | Legacy (visão Audiovisual), pega o bruto no Google Drive (disco G:), edita com a skill certa pelo nome da pauta (TD = tela dividida, NV/Novela = novela, ES = edição simples, CX = caixinha de perguntas da Executoria 0800), salva em EDITADO do mês, cola o link em MATERIAL FINALIZADO, comenta o que fez e move o card para Aprovação; nas correções faz a v2, v3. Use quando o usuário pedir "edita os vídeos do Claude", "processa a fila", "roda a fila do Notion", "faz as correções do Claude", ou mandar editar um card específico do quadro.
---

# Fila de render (Notion → edição → Drive → Notion)

Só roda quando o usuário pede ("edita os vídeos do Claude", "processa a fila", "faz as correções").
Todo card da fila é editado **no PC de render** (`~/.claude/maquina.json` com `"papel": "render"`).
Em outro PC: pergunte "aqui ou no PC de render?" e, se for lá, diga para mandar o pedido pela
conversa do PC de render (Controle Remoto, no celular ou em claude.ai/code).

**"Roda por aqui" (outro PC, a pedido do usuário — 28/09/2026):** vale. Diferenças:
- Sem disco G:: baixe o bruto pelo link do card direto do Drive (arquivo compartilhado por link):
  `curl -sL -o "C:\Render\brutos\<slug>\<arquivo>" "https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t"`
  (confira antes com `curl -sIL` que volta `Content-Type: video/...` e o tamanho certo; confira o espaço no C:).
- A pasta de trabalho da versão anterior ficou no PC de render: na correção, refaça do bruto já com
  as correções (decupagem revisada à mão, não a proposta automática).
- Entrega: o Notion só aceita anexo de até 20 MB e o conector do Drive não sobe vídeo grande. Sem
  Google Drive para computador neste PC, deixe o vídeo em `C:\Render\Reels Editados\`, mostre ao
  usuário e combine a subida (ele arrasta para a pasta EDITADO do mês no Drive; depois você cola o link
  em MATERIAL FINALIZADO, comenta e move para Aprovação). Não mova o card sem o link do vídeo.
- Traga as correções aplicadas na conversa (o usuário pede "me traga por aqui") além do comentário no card.
- O PC NOT-LIVE-LAIR já tem o Google Drive para computador (G:) desde 28/09/2026: a entrega segue o Passo 4.
- Quando o usuário diz "deixa eu conferir", mostre o vídeo na conversa e **só suba no Drive / mexa no
  Notion depois do ok**. MATERIAL FINALIZADO fica SÓ com o link da versão mais nova (usuário, 29/09/2026: "retire os links das versões anteriores"); os arquivos antigos continuam na pasta EDITADO.
- Arquivo final leve (CRF 18, ~200 MB para 2:30): o de 1,2 GB (CRF 10) foi reprovado ("não pode ser tão pesado").

O usuário não é técnico: relatórios curtos, pelo dia a dia dele (ver CLAUDE.md global).

## Quem faz o trabalho: a própria conversa que recebe o gatilho (regra do usuário, 28/09/2026)

**Sem horário automático e sem tarefa agendada.** A fila só começa quando o usuário manda o gatilho
("edita os vídeos do Claude", "processa a fila", "faz as correções"), nesta conversa ou de outro PC.
- **Quem recebe o gatilho edita:** a conversa "Render central" (ou "Central de Render") do PC de render
  começa na hora, do "Passo 0" em diante, e vai contando o andamento ao usuário em linhas curtas.
- **Se o usuário pedir outra conversa** ("faz num chat novo", "usa a conversa X"): o trabalho vai para
  ela. Conversa nova **sempre no modo Automático** — confira e, se não estiver, ajuste
  (`set_session_permission_mode`) ou peça ao usuário para ligar antes de começar.
- A tarefa agendada `fila-de-render` ficou **desligada** (as rodadas automáticas se atropelavam: a
  nova cortava a anterior no meio). Não religue nem dispare sem o usuário pedir.
- Conversa ficando pesada: sugira ao usuário abrir uma nova (no Automático) e continue lá.

## Pedido vindo de outro PC ou do celular

A conversa de recepção no PC de render se chama **"Render central"** (ou "Central de Render"; pasta
`C:\Render`, modo Automático, Controle Remoto ligado).
- **Celular ou navegador:** o usuário abre o app do Claude (ou claude.ai/code), entra na conversa
  "Render central" e escreve o pedido; ela mesma começa a editar.
- **Claude de outro PC** recebeu "manda o PC de render editar", "ativa o PC de render", "edita os vídeos
  do Claude" (e o usuário quer que seja lá): use `ListAgents`, ache a sessão do PC de render (nome com "Central de Render" ou
  "Render central") e mande com `SendMessage` o pedido do usuário (ex.: "edita os vídeos do Claude",
  ou "edita só o card <PAUTA>"; se o usuário pediu outra conversa, diga qual). Mande só o pedido,
  sem instruções técnicas (nada de "dispare a tarefa"). Responda ao usuário que o pedido foi entregue
  e que o resultado aparece no Notion (cards em Aprovação) e na própria Central de Render.
  Se a Central não aparecer na lista: o PC de render está desligado, o app está fechado ou o
  Controle Remoto caiu. Diga isso ao usuário e peça para alguém abrir o app lá (o Claude abre sozinho
  quando o PC liga) e reabrir a conversa "Central de Render".
- Você não liga o PC de render à distância: ele precisa estar ligado (não dorme, o Claude abre com o Windows).

## Onde está cada coisa

| Item | Onde |
| --- | --- |
| Quadro | "CALENDÁRIO EDITORIAL \| Legacy", visão Audiovisual: https://app.notion.com/p/73ac9747efab8374a5b5812011259272?v=c7bc9747efab821ea98b88388c677927 · fonte `collection://f0cc9747-efab-822b-8678-07f92372d6b7` |
| Colunas (status ANDAMENTO) | entrada: **CLAUDE** (novo) e **Correções (Claude)** (ajuste); saída: a coluna de aprovação (confira o nome exato no esquema, ex.: "Aprovação") |
| Campos do card | PAUTA (título), IDEIA (instruções extras), MATERIAL NECESSÁRIO (link do bruto no Drive, às vezes arquivo), MATERIAL FINALIZADO (arquivo/link do editado), CORREÇÕES (Claude) (texto das correções), roteiro/briefing no **corpo** do card |
| Drive (conta equipelegacyexecutoria@gmail.com) | `G:\Meu Drive\02. Captação de Vídeos\<AAAA>\<MM - Mês>\ORGÂNICO\BRUTO` e `\EDITADO` (ex.: `2026\09 - Setembro`) |
| Trabalho local | `C:\Render` (brutos copiados, `_trabalho\<slug>`, `Reels Editados\`) |

Antes da 1ª leitura, busque o esquema da fonte (`notion-fetch` na fonte) e use os nomes **exatos**
das colunas e campos. Se a coluna "Correções (Claude)" não existir, avise o usuário e siga só com CLAUDE.

## Passo 0 — preparar

1. `powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "$HOME/.claude/sync/sync.ps1" -Modo agora` (skills em dia).
2. Confira `G:\Meu Drive` (Google Drive para computador) e o espaço livre no C: (≥ 30 GB). Sem G:, pare e avise.
3. Liste os cards com ANDAMENTO = CLAUDE ou Correções (Claude) (`notion-query-data-sources`/`notion-fetch`
   da visão; se não der, `notion-search` na fonte). Ordene por PRIORIDADE (ALTA → MÉDIA → BAIXA) e DATA D/ PUBLICACÃO.
4. Diga ao usuário em 2–4 linhas o que vai fazer (quantos cards, quais, em que ordem) e comece; não espere resposta.

Um card por vez, do começo ao fim. Leia o **card inteiro** (`notion-fetch` na página: campos, corpo e
comentários com `notion-get-comments`) — às vezes há mais informação, às vezes menos.

## Passo 1 — ler o briefing e decidir a edição

**Primeiro o briefing, depois o estilo.** Antes de escolher a skill, leia com atenção a IDEIA, o corpo
do card e os comentários e anote em `C:\Render\_trabalho\<slug>\briefing.md` cada orientação
(formato, duração máxima, partes, ângulos, o que mostrar, quem é o cliente, material que falta).
Isso vale para **todo** card, inclusive os que não se encaixam nos formatos de sempre (Case,
depoimento, aniversário...).

**Hierarquia (regra do usuário):** o **estilo** vem sempre do **nome da task** quando ele tem NV/Novela,
TD ou ES — o briefing não troca o estilo. O briefing é lido de qualquer forma e manda nos **detalhes**
dentro daquele estilo (duração, partes, ângulo, o que mostrar, material pendente). Só quando o nome
não tem NV, TD nem ES é que o briefing decide o estilo.

Estilo pelo título da PAUTA:

| No título | Skill |
| --- | --- |
| `_TD_` | `reels-tela-dividida-clailton` |
| `_NV_` ou `_Novela_` | `reels-novela-clailton` |
| `_ES_` | `reels-edicao-simples-clailton` |
| `_CX_` (ex.: `Reels_0800_CX_*`) | `reels-caixinha-0800` (bruto em `G:\Meu Drive\EXECUTORIA 0800\Videos a editar`, se o card não tiver link) |
| sem NV/TD/ES (Case, depoimento...) | o briefing decide (ex.: "é para ser no formato tela dividida" → tela dividida); sem indicação, a skill mais próxima do material (1 pessoa falando para a câmera → novela; com imagens de apoio → tela dividida) |

Exemplos de orientação que mudam a edição: "gravado em 16:9, redimensionar para 9:16", "máximo
2min59", "tem parte 1 e parte 2, a parte 2 em outro ângulo" (junte as partes na ordem e trate a troca
de ângulo como emenda), "usar imagens do Instagram do cliente".

Material que o briefing diz que **ainda vai chegar** (ex.: "vou pedir o Instagram da pastelaria"):
se dá para editar bem sem ele, edite e diga no comentário o que ficou provisório; se é essencial,
comente "AGUARDANDO: <o quê>" e pule o card. Dúvida que muda a edição inteira: comente "DÚVIDA: ..." e pule.

No comentário de entrega, liste em 1 linha as orientações do briefing que você seguiu.

## Passo 2 — pegar o bruto

0. **Antes de baixar, confira se o bruto já está no PC** (regra do usuário, 30/09/2026: "não baixe de novo,
   evite retrabalho"): `C:\Render\brutos\<slug>\` e a fonte gravada em `C:\Render\_trabalho\<slug>\corte.json`
   (campo `fonte`). Existindo e com o tamanho igual ao do Drive, use esse arquivo e pule os itens 1–4.
   Vale sempre, principalmente nas correções (v2, v3).
1. Tire o ID do link do Drive em MATERIAL NECESSÁRIO (`/file/d/<ID>/`, `?id=<ID>`, `/folders/<ID>`).
   Arquivo anexado direto no Notion: baixe com a ferramenta de anexo do Notion.
2. Com o conector do Drive (`get_file_metadata`), suba pelos `parentId` até a raiz e monte o caminho
   `G:\Meu Drive\...`. **Ache pelo link, nunca pelo nome** (há pasta com nome de vídeo, ex.: `Reels_Clailton_ES_Parabéns.MP4`).
   Link de pasta = vários arquivos (parte 1, parte 2...): liste com `search_files` (`parentId = '<ID>'`) e use todos, na ordem.
3. Arquivo que não está no "Meu Drive" dessa conta (compartilhado de outra conta): comente no card
   pedindo para colocar o bruto em `ORGÂNICO\BRUTO` do mês e pule.
4. Copie para o disco local antes de editar (o G: baixa sob demanda):
   `robocopy "<pasta no G:>" "C:\Render\brutos\<slug>" "<arquivo>" /J /R:3 /W:10`
   `<slug>` = PAUTA sem acento, só `[A-Za-z0-9_-]`.

Roteiro: o corpo do card (e anexos/links de roteiro, se houver). Salve em `C:\Render\_trabalho\<slug>\roteiro.txt`.

## Passo 3 — editar (modo fila)

Rode a skill escolhida com a raiz do projeto em `C:\Render` (entrega em `C:\Render\Reels Editados\`,
trabalho em `C:\Render\_trabalho\<slug>\`), seguindo o modo rápido dela, com estas diferenças:
- **Não pare para aprovação** (o portão do 1º vídeo e o teste de fundo claro da regra global): gere
  mesmo assim `qa\fundo_mais_claro.png` e cite no comentário; a aprovação é no Notion.
- **Não edite skills.** Correção que se repete vira "sugestão para a skill" no comentário.
- Guarde `C:\Render\_trabalho\<slug>\` até o card ser aprovado (as correções partem dele).

## Passo 4 — entregar

1. Nome: `<PAUTA> - EDITADO.mp4` (v2 em diante: `<PAUTA> - EDITADO v2.mp4`).
2. Pasta EDITADO do **mês atual**: `G:\Meu Drive\02. Captação de Vídeos\<AAAA>\<MM - Mês>\ORGÂNICO\EDITADO\`
   (meses: 01 - Janeiro, 02 - Fevereiro, 03 - Março, 04 - Abril, 05 - Maio, 06 - Junho, 07 - Julho,
   08 - Agosto, 09 - Setembro, 10 - Outubro, 11 - Novembro, 12 - Dezembro). Se a pasta do mês não
   existir, procure uma variação (ex.: "OUTUBRO - ORGÂNICO - BRUTOS E EDITADO") e, sem nenhuma, crie
   `<MM - Mês>\ORGÂNICO\EDITADO` e avise no relatório.
3. `robocopy "C:\Render\Reels Editados" "<EDITADO>" "<arquivo>" /J /R:3 /W:10`
4. Espere o upload do Drive para computador: repita `search_files` (`title = '<arquivo>' and parentId = '<ID do EDITADO>'`)
   a cada ~30 s (até 20 min). Link: `https://drive.google.com/file/d/<ID>/view`.
5. No card (`notion-update-page`): MATERIAL FINALIZADO = o link (arquivo externo com o nome do vídeo);
   ANDAMENTO = coluna de aprovação. Na v2, v3...: MATERIAL FINALIZADO passa a ter SÓ o link da versão nova (troque, não acrescente).
6. Comentário no card (`notion-create-comment`), curto:
   `v1 pronta · <duração> · editado com <skill> · o que conferir: <1–3 pontos> · tempo: <min>`.

## Correções (coluna "Correções (Claude)")

1. Leia o campo **CORREÇÕES (Claude)** e os comentários novos. Cada item deve ter o tempo do vídeo
   ("0:12 legenda errada", "0:25 a 0:31 trocar a cena", "geral: legenda maior").
2. Aplique sobre a edição guardada em `C:\Render\_trabalho\<slug>\` (sem ela, refaça do bruto com as correções).
3. Correção ambígua: **não chute**. Comente "DÚVIDA: ..." e deixe o card em Correções (Claude); siga para o próximo.
4. Entregue como `v2`, `v3`... (Passo 4) e mova para aprovação.
5. Depois de entregar, comente no card **neste formato (padrão do usuário, 09/10/2026)**:
   ```
   Correções pedidas (v2):
   <texto do campo CORREÇÕES (Claude) colado EXATAMENTE como o usuário escreveu — copiar e colar, sem resumir>

   O que foi feito: <seu comentário, item por item, com ✔ / o que ficou pendente / dúvidas>
   ```
   Card que voltou sem texto em CORREÇÕES (Claude) (regra geral de outro card): "Correções pedidas: (nenhuma neste
   card — aplicada a regra geral: <qual>)". Só DEPOIS de comentar, **esvazie** o campo CORREÇÕES (Claude).
6. Erro que se repete em vários cards = causa na skill: ache a causa, corrija o script/regra, **confira nos cards
   que reclamaram** e só então registre na skill (usuário, 09/10/2026).

Correções que já têm caminho pronto (lote de 08/10/2026):
- "Áudio estourado", "ruído", "barulho externo", "tratar o áudio", "usa o Adobe": skill de reels, seção
  "Tratar o áudio no Adobe Podcast" (Chrome do perfil Legacy Executoria). Rode `tratar_audio.py medir`; se der QUENTE,
  ponha no comentário "gravação com ganho alto: baixar ~10 dB o ganho do microfone/câmera".
- "Cortou a palavra X" / "pausa natural cortada": o corte agora mede o ritmo de cada vídeo e só encurta a pausa que
  quebra o ritmo (skill de reels, linha "Corte"); refaça com `montar_corte.py --manter-palavras`.
- "Vazio com barulho" / "erro de corte no <palavra>": a conferência acusa "trecho sem palavra"; `INICIO n i@t`.
- "Cor esverdeada / white balance": `balanco_branco.py` (grava `cor.txt`). "Altere a CTA": `cta.txt` no trabalho.
- Card devolvido para Correções SEM texto novo junto com outros que têm uma regra geral ("ajuste a skill", "em todos"):
  a regra vale para ele também (09/10/2026: pausas naturais em todos os 11).
- Erro de fala que ficou ("populi... popularidade"): `INICIO n i@t` na decupagem + `--manter-palavras`.
- "Diagramação quebrada": rode a legenda de novo (escada com linha curta vira esquerda sozinha) e confira o quadro.

## Relatório final (para o usuário)

Uma linha por card: título → resultado (Aprovação v1 / v2, pulado e por quê, dúvida) e o tempo gasto.

## Limpeza (só local)

Nunca apague nada no Drive nem no Notion. No `C:\Render`: ao começar a fila, remova `brutos\<slug>`
e `_trabalho\<slug>` de cards que já saíram da fila e da aprovação (aprovados) há mais de 3 dias, e
qualquer pasta com mais de 30 dias.

## Quando der errado

- Falhou a edição: comente "ERRO: <o que houve em 1 linha>" no card, deixe onde está e siga.
- Sem Notion (conector caiu): pare e avise o usuário para reconectar em claude.ai/settings/connectors.
- Upload do Drive não aparece em 20 min: deixe o vídeo em EDITADO, comente o caminho e avise.
