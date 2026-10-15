# Onde está cada coisa

## Notion

| O quê | ID / endereço |
|---|---|
| Página privada do Igor onde os relatórios são criados: **Relatórios do Orgânico (Claude)** | `3f7c9747-efab-8194-9f1e-e617dabb527c` |
| DEMANDAS \| TIME DE CRIAÇÃO (calendário editorial, visão Audiovisual) | `collection://f0cc9747-efab-822b-8678-07f92372d6b7` |
| DEMANDAS \| BLACK FRIDAY | `collection://3f3c9747-efab-80c5-94c6-000b908a6dd3` |
| DEMANDAS \| QUIZ CLAILTON | `collection://c56a8868-6e9a-4d60-b6c7-1402069a1e8f` |
| Página LEGACY (raiz) — **NÃO ABRIR: contém o bloco SENHAS** | `a23c9747efab82fcb3e28109c981c60a` |

Quadros novos "DEMANDAS | ..." entram sozinhos: ache pelo `notion-search`, busque o esquema e
acrescente aqui.

Os três quadros acima são fontes da mesma base **TASKS** (`73ac9747efab8374a5b5812011259272`), onde
ficam as abas do time e as do Claude. O Quiz também tem base própria (`e7488f7fc17f48d3882f08b1e7ada724`).

### Visões do Claude (ler no modo "view", sem gastar a cota do SQL)

Criadas em 15/10/2026 como abas da base TASKS (tabela, só leitura para o relatório; ninguém precisa
mexer). Datas relativas: continuam valendo todo dia. Concluído no calendário = Finalizado, Publicado,
Stand-by, 📌  MURAL e Publicar (o grupo "concluído" do Notion; Publicar = pronto, só falta postar).
Ler com `notion-query-data-sources` `{"mode": "view", "view_url": "<link>"}` e resumir com
`scripts/notion_visao.py`.

| Visão | Filtro | Link |
|---|---|---|
| Claude · Publicações (ontem a +7 dias) | publicação de ontem até daqui a 7 dias, qualquer andamento; ordem: publicação | https://app.notion.com/p/73ac9747efab8374a5b5812011259272?v=3fac9747efab8132b189000cc0adca65 |
| Claude · Posts não prontos (próx. 7 dias) | publicação de hoje até +7 dias e andamento ≠ Publicar/Publicado | https://app.notion.com/p/73ac9747efab8374a5b5812011259272?v=3fac9747efab8150945d000c6021d4c4 |
| Claude · Tarefas de hoje | conclusão = hoje e não concluído; ordem: responsável | https://app.notion.com/p/73ac9747efab8374a5b5812011259272?v=3fac9747efab81ab97a0000cb71d62cc |
| Claude · Atrasados | conclusão antes de hoje e não concluído; ordem: responsável, conclusão | https://app.notion.com/p/73ac9747efab8374a5b5812011259272?v=3fac9747efab81428808000c5cff71ea |
| Claude · Decisões (Aprovação e Revisão) | andamento Aprovação ou Revisão; ordem: publicação | https://app.notion.com/p/73ac9747efab8374a5b5812011259272?v=3fac9747efab81798830000c49c12edc |
| Claude · Prontos sem data | andamento Publicar e sem data de publicação | https://app.notion.com/p/73ac9747efab8374a5b5812011259272?v=3fac9747efab81b98ba7000cd425a296 |
| Claude · Semana passada | publicação **ou** conclusão nos últimos 7 dias (até hoje), qualquer andamento | https://app.notion.com/p/73ac9747efab8374a5b5812011259272?v=3fac9747efab8141906a000cc6f7ef2e |
| Claude · Black em aberto (+ concluídas na semana) | Black: Andamento ≠ Concluído, ou Concluído com conclusão nos últimos 7 dias | https://app.notion.com/p/73ac9747efab8374a5b5812011259272?v=3fac9747efab819c90bb000cef48711e |
| Claude · Quiz em aberto (+ concluídas na semana) | Quiz: Andamento ≠ Concluído e ≠ Documentos, ou Concluído com conclusão nos últimos 7 dias | https://app.notion.com/p/73ac9747efab8374a5b5812011259272?v=3fac9747efab81eda60e000ce9088d7d |

O filtro "hoje/ontem" do Notion compara a data do card; publicações com horário vêm em UTC (um post
de 21h de ontem aparece como `00:00Z` de hoje). Por isso a visão de publicações começa em ontem:
classifique pelo horário de Brasília que o `notion_visao.py` já mostra.

SQL (`notion-query-data-sources` modo "sql") **só como último recurso**: o plano tem cota
compartilhada e ela acabou em 15/10/2026. A cota do modo "view" não existe.

### Campos do calendário (TIME DE CRIAÇÃO)
`PAUTA` (título), `ANDAMENTO`, `RESPONSÁVEL` (um só), `PRIORIDADE` (URGENTE/ALTA/MÉDIA/BAIXA),
`PERFIL`, `FORMATO` (lista), `REDE SOCIAL` (lista), `IDEIA`, `CORREÇÕES (Claude)`,
datas `date:DATA D/ CONCLUSÃO:start` e `date:DATA D/ PUBLICACÃO:start` (sem acento no "CAO").

ANDAMENTO: A fazer · Aguardando material · Correção · Copy · A Gravar · A Editar · A Design ·
Gravação em andamento · Edição em andamento · Design em produção · CLAUDE (Editor) ·
CLAUDE (Designer) · Aprovação · Correções (Claude) · **Publicar** (pronto) · Stand-by ·
Finalizado · Publicado · 📌  MURAL (dois espaços).

Cards do MURAL que são referência (não tarefa): "📌 GRADE DE CONTEÚDOS" (grade semanal) e
"📌 BIBLIOGRAFIA PERFIL LEGACY" (3f8c9747efab80148173fc3e07d8fbbd): diário de testes do social media
no perfil Legacy (o que mudou em legenda, criativo, CTA, link), com a tabela "Testes em andamento" e o
registro por dia, o mais recente no topo. Leia esse card sempre que analisar métricas do Instagram ou
do LinkedIn da Legacy: uma mudança de alcance ou retenção costuma ter um teste anotado lá. Desde 13/10
substitui o Google Docs antigo de mesmo nome.

### Campos dos quadros de demandas (Black, Quiz)
`Tarefa`, `Andamento` (A fazer · Documentos · Pendência · Andamento · Correção · Revisão ·
Concluído), `Responsável` (lista), `Prioridade` (URGENTE/ALTA/MEDIA/BAIXA), `Formato`,
`Descrição da tarefa`, `date:Data D/ Conclusão:start`, `date:Data D/ Publicação:start`.
Cards em "Documentos" são material de apoio, não tarefa.

### Reuniões
Ficam como páginas soltas sob LEGACY › MARKETING › Reuniões (ex.: "Reunião | Touchpoint Black
Legacy (08/10)"). Ache pelas buscas "Reunião" / "Alinhamento" com data de criação. As tarefas que
saem da reunião já viram cards (com "Origem: Reunião ..." na descrição).

### Planejamento e narrativa
Planejamento estratégico de conteúdo V1–V4 (V4 = "Modo Viral") — **o Igor vai validar/atualizar**;
até lá, não tratar como verdade. Narrativa atual da Black: "Viva sem medo em 2027" (cenário
econômico 2027, eleições).

## Pipedrive (já conectado)

Funis e etapas (IDs):
- **2 FUNIL LEGADO**: 6 Oportunidade (MQL) → 7 Tentativa de Conexão → 8 Lead Qualificado →
  9 Agendamento Closer → 10 Reunião Realizada → 20 Forecast → 11 Vendido
- **4 FUNIL IMPULSÃO**: 41 Op Allbound → 24 Em Atendimento → 43 Demo Agendada →
  42 Link de Pagamento Enviado → 25 Fechado; saídas: 40 Sem Resposta, 39 Refugo Allbound
- **5 SOCIAL SELLING**: 44 Prospect → 47 Lead → 51 Lead Qualificado → 52 Agendamento
- **6 FUNIL OUTBOUND**: 53 Lista → 54 Filtro 1 → 55 Filtro 2 → 56 Agendamento Closer

Campos personalizados do negócio (códigos):
- utm_source `8edcf78215c52bc6cd4e609bbcc9556e9340d237`
- utm_campaign `ad2d705d02225947afb06abb446e71b45925619a`
- utm_medium `e3d3416c2ffc921e46b99ceb5ff1acb7e987b55c`

Etiquetas: `BLACK FRIDAY`, `QUIZ`.

**Regra de origem** (o Igor chama de "UTM source orgânico"):
- **Quiz**: etiqueta QUIZ ou utm_source `QUIZ_LEGACY`.
- **Orgânico**: utm_source `organico` ou `instagram` (campanhas `clailton` + medium
  `automacao-novo-seguidor` = automação de novo seguidor do Clailton; `bio_legacy`, `bio_clailton`,
  `Story_legacy`, `Story_clailton`; medium `tiktok` = bio do TikTok).
- **Pago**: utm_source `facebook` (anúncios) — só como referência.

Como puxar sem estourar: `getDeals` com `updated_since` (15 dias atrás, em UTC), `status`
open/won/lost, `include_labels: true`, `sort_by: add_time`, `sort_direction: desc`, `limit: 500`.
A resposta é grande e vai para um arquivo; passe o caminho dos arquivos para
`scripts/leads_funil.py` (roda com `python -I`). Se vier `next_cursor` e o último negócio ainda for
mais novo que 15 dias, busque a próxima página (máx. 4 páginas).

## Discord (ainda não ligado)

A empresa já usa Discord (comunidade e avisos de MQL do Peterson). Para mandar o relatório lá, o
Igor cria um canal privado só dele, em Configurações do canal › Integrações › Webhooks › Novo
webhook, e guarda o link no arquivo `~/.claude/sync-local/discord-relatorio.txt` (fora da
sincronia, nunca no Notion nem nesta skill). Com o arquivo existindo, o relatório manda um resumo
curto + link da página do Notion.
