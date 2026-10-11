---
name: fila-de-render
description: Processa a fila de vídeos do Notion no PC de render — lê os cards das colunas CLAUDE e "Correções (Claude)" do Calendário Editorial | Legacy (visão Audiovisual), pega o bruto no Google Drive (disco G:), edita com a skill certa pelo nome da pauta (TD = tela dividida, NV/Novela = novela, ES = edição simples, CX = caixinha de perguntas da Executoria 0800), sobe a prévia na Sala de Revisão (Artifact, skill sala-de-revisao) e o arquivo final em EDITADO do mês, cola o link da Sala (e o do Drive) em MATERIAL FINALIZADO, comenta o que fez e move o card para Aprovação; nas correções lê as notas presas na minutagem da Sala de Revisão (e o campo CORREÇÕES) e faz a v2, v3. Use quando o usuário pedir "edita os vídeos do Claude", "processa a fila", "roda a fila do Notion", "faz as correções do Claude", ou mandar editar um card específico do quadro.
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
- Entrega: suba na Sala de Revisão normalmente (Passo 4, itens 1–2): com o link da Sala o card já pode ir
  para Aprovação. Sem Google Drive para computador neste PC, o arquivo final fica em `C:\Render\Reels Editados\`;
  avise o usuário para arrastar para a pasta EDITADO do mês e, depois, acrescente o link do Drive no card
  e na Sala (Passo 4, item 6). Não mova o card sem o link da Sala.
- Traga as correções aplicadas na conversa (o usuário pede "me traga por aqui") além do comentário no card.
- O PC NOT-LIVE-LAIR já tem o Google Drive para computador (G:) desde 28/09/2026: a entrega segue o Passo 4.
- Quando o usuário diz "deixa eu conferir", mostre o vídeo na conversa e **só suba no Drive / mexa no
  Notion depois do ok**. MATERIAL FINALIZADO fica SÓ com o link da Sala e o do Drive da versão mais nova (usuário, 29/09/2026: "retire os links das versões anteriores"); os arquivos antigos continuam na pasta EDITADO e as versões antigas continuam na Sala (botões v1, v2...).
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

## Passo 4 — entregar (Sala de Revisão + Drive)

**Regra do usuário (11/10/2026):** a revisão é na **Sala de Revisão** (skill `sala-de-revisao`), não no Drive.
O usuário clica no link do card, assiste em qualquer PC ou celular e deixa as notas presas no tempo do vídeo.
O arquivo final em alta continua indo para EDITADO no Drive (é ele que vai para a postagem).

1. Nome: `<PAUTA> - EDITADO.mp4` (v2 em diante: `<PAUTA> - EDITADO v2.mp4`), em `C:\Render\Reels Editados\`.
2. **Sala de Revisão primeiro** (rápido, não espera o Drive): siga a skill `sala-de-revisao`, seção
   "Publicar uma versão", com `--pauta "<PAUTA>"`, `--versao v1` (v2, v3 nas correções), `--notion "<url do card>"`,
   `--pasta "C:\Render\_sala_revisao"` e `--obs` = 1 linha (v1: "Primeira edição"; v2+: "Correções: <resumo>").
   Guarde o `link_revisao`.
3. Pasta EDITADO do **mês atual**: `G:\Meu Drive\02. Captação de Vídeos\<AAAA>\<MM - Mês>\ORGÂNICO\EDITADO\`
   (meses: 01 - Janeiro, 02 - Fevereiro, 03 - Março, 04 - Abril, 05 - Maio, 06 - Junho, 07 - Julho,
   08 - Agosto, 09 - Setembro, 10 - Outubro, 11 - Novembro, 12 - Dezembro). Se a pasta do mês não
   existir, procure uma variação (ex.: "OUTUBRO - ORGÂNICO - BRUTOS E EDITADO") e, sem nenhuma, crie
   `<MM - Mês>\ORGÂNICO\EDITADO` e avise no relatório.
   `robocopy "C:\Render\Reels Editados" "<EDITADO>" "<arquivo>" /J /R:3 /W:10`
4. Espere o upload do Drive para computador: repita `search_files` (`title = '<arquivo>' and parentId = '<ID do EDITADO>'`)
   a cada ~30 s (até 20 min). Link: `https://drive.google.com/file/d/<ID>/view`. Enquanto espera, siga para o próximo card.
5. No card (`notion-update-page`): MATERIAL FINALIZADO = `["<link_revisao>", "<link do Drive>"]` (o da Sala **primeiro**:
   é o que o usuário clica); ANDAMENTO = **Aprovação**. Na v2, v3...: troque os dois links pelos da versão nova
   (o da Sala é o mesmo endereço; ele abre na versão mais nova). Drive ainda não apareceu: ponha só o da Sala e acrescente o do Drive depois.
   **Correção (v2, v3...) — regra do usuário, 11/10/2026:** a versão antiga em alta sai do Drive e do card, e entra a nova.
   Depois que o link da nova estiver no card, mande o arquivo antigo de EDITADO para a **lixeira do Drive**
   (`trash_file` do conector do Drive, ou apague pelo G:; os dois vão para a lixeira, que guarda 30 dias). Só os arquivos
   em alta das versões anteriores deste card (`<PAUTA> - EDITADO.mp4`, `... v2.mp4`...): nunca bruto, nunca arquivo de
   outro card. Tire também o `drive` dessas versões no documento da Sala. Na Sala as versões antigas ficam
   (botões v1, v2: o usuário compara e as notas antigas apontam para elas).
   Aprovado ("está tudo ok"): o usuário mesmo posta; nada a fazer.
6. Com o link do Drive: grave-o também na Sala (`sala-de-revisao`, "Publicar uma versão", item 7).
7. Comentário no card (`notion-create-comment`), curto:
   `v1 pronta · <duração> · editado com <skill> · revisar na Sala: <link_revisao> · o que conferir: <1–3 pontos> · tempo: <min>`.

## Correções (coluna "Correções (Claude)")

1. **Fonte principal: as notas da Sala de Revisão** (skill `sala-de-revisao`, "Ler as notas e aplicar"):
   notas abertas do vídeo (`<id>` = PAUTA em slug), cada uma com o tempo exato daquela versão.
   Leia também o campo **CORREÇÕES (Claude)** e os comentários novos do card (o usuário ainda pode
   escrever ali: "0:12 legenda errada", "geral: legenda maior"). Valem as duas fontes juntas.
   Sem nota aberta e sem texto: veja a regra geral do fim desta seção; sem nada, comente "DÚVIDA: não achei correções" e pule.
2. Aplique sobre a edição guardada em `C:\Render\_trabalho\<slug>\` (sem ela, refaça do bruto com as correções).
   O tempo da nota é o da versão em que ela foi escrita (v1, v2...): ache o trecho no corte daquela versão.
3. Correção ambígua: **não chute**. Na nota da Sala, `resposta: "DÚVIDA: ..."` (fica aberta); no campo/comentário, comente
   "DÚVIDA: ...". Se a dúvida trava o vídeo, deixe o card em Correções (Claude) e siga para o próximo.
4. Entregue como `v2`, `v3`... (Passo 4: Sala primeiro, depois Drive) e mova para Aprovação.
5. Marque na Sala as notas aplicadas como resolvidas, com 1 linha do que foi feito (`sala-de-revisao`, item 5) —
   o usuário vê a resposta embaixo de cada nota.
6. Comente no card **neste formato (padrão do usuário, 09/10/2026)**:
   ```
   Correções pedidas (v2):
   <notas da Sala, uma por linha: [mm:ss.d] (v1) texto — copiadas EXATAMENTE como o usuário escreveu>
   <texto do campo CORREÇÕES (Claude), se houver, colado EXATAMENTE — sem resumir>

   O que foi feito: <item por item, com ✔ / o que ficou pendente / dúvidas>
   Revisar a v2 na Sala: <link_revisao>
   ```
   Card que voltou sem nota e sem texto (regra geral de outro card): "Correções pedidas: (nenhuma neste
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
  a regra vale para ele também (09/10/2026: pausas naturais em todos os 11; 11/10/2026: revertido para o corte justo
  em todas as novelas, pedido numa nota da Sala de Revisão).
- Erro de fala que ficou ("populi... popularidade"): `INICIO n i@t` na decupagem + `--manter-palavras`.
- "Diagramação quebrada": rode a legenda de novo (escada com linha curta vira esquerda sozinha) e confira o quadro.

## Relatório final (para o usuário)

Uma linha por card: título → resultado (Aprovação v1 / v2, pulado e por quê, dúvida) e o tempo gasto.

## Limpeza (só local)

Nunca apague nada no Drive nem no Notion, com uma exceção: na correção, o arquivo em alta da versão anterior do
mesmo card vai para a lixeira do Drive (Passo 4, item 5). **Bruto copiado para o PC:** depois que a versão nova está
na Sala e no Drive, apague `C:\Render\brutos\<slug>` (o original continua no Drive; usuário, 11/10/2026: "pouco
espaço"). No `C:\Render`: ao começar a fila, remova `brutos\<slug>`
e `_trabalho\<slug>` de cards que já saíram da fila e da aprovação (aprovados) há mais de 3 dias, e
qualquer pasta com mais de 30 dias.

## Quando der errado

- Falhou a edição: comente "ERRO: <o que houve em 1 linha>" no card, deixe onde está e siga.
- Sem Notion (conector caiu): pare e avise o usuário para reconectar em claude.ai/settings/connectors.
- Upload do Drive não aparece em 20 min: deixe o vídeo em EDITADO, comente o caminho e avise.
