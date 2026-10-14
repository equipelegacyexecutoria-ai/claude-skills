# Posts e Leads no painel do Cérebro (trazidos do Legacy Insights Hub)

Atualizado em 14/10/2026. Pedido do Igor (13/10): abandonar o Legacy Insights Hub e deixar o Cérebro como o único
painel de gestão do time. As telas de **Posts** e de **Leads** do Hub viraram janelas do site do Cérebro
(https://cerebro-legacy-organico.vercel.app), publicadas em 14/10/2026. O Hub não é mais fonte: só foi lido e copiado.

Leia este arquivo quando perguntarem sobre desempenho dos posts, métricas do Instagram, leads, MQL por canal, metas
do mês, vendas orgânicas, cliques no link da bio, ou quando for analisar o que mudou nos números.

## Onde fica cada coisa no site

| Janela | Endereço | O que mostra |
|---|---|---|
| Posts | `#posts` | todos os posts dos 3 perfis no período (7, 14, 30, 90 dias, mês ou personalizado), 8 números do topo com comparação ao período anterior, filtros por perfil e tipo, tabela com views, curtidas, comentários, compartilhamentos, salvos, total, engajamento, visitas, % visita e cliques no link, detalhe de cada post (comparado com a média dos posts parecidos do mesmo perfil e tipo, últimos 90 dias), "Visitas ao Perfil por Dia" e "Padrões Identificados" (melhor formato, dia e horário) |
| Leads › Visão geral | `#leads/geral` | leads do mês por origem (Legacy ou Comunidade): total, MQL (≥ R$ 70 mil), sem faturamento, canal com mais leads; metas do mês com o ritmo ("Esperado… adiantado/atrasado em N"); vendas por leads orgânicos; MQL e cliques no link por dia; leads por canal (MQL × não MQL); MQL por faixa de faturamento, nicho, colaboradores e gargalo; lista de todos os leads |
| Leads › Pipedrive | `#leads/pipedrive` | o funil do Pipedrive do relatório das 8h20 (a tela de Leads de antes) |

Ao passar o mouse nas barras aparece o balão com o detalhe (ex.: num dia de MQL, os canais de onde vieram).

## De onde vêm os dados e quando atualizam

- **Posts:** API do Instagram (Meta), perfis @legacyexecutoria (chave `legacy`), @clailtonluiz (`clailton`) e
  @allan_msilva (`allan`). Uma fotografia por post por dia, por volta das 23h (um perfil por vez), dos posts dos
  últimos 90 dias; também os seguidores do dia. Botão "Atualizar" na janela busca na hora.
  Banco do Cérebro: `cerebro_ig_posts`, `cerebro_ig_fotos`, `cerebro_ig_seguidores`; views `cerebro_ig_cliques_dia`
  e `cerebro_ig_visitas_dia` (o do dia = fotografia de hoje − a de ontem).
  - Visitas ao perfil e novos seguidores: a Meta não informa para Reels.
  - Engajamento = interações ÷ seguidores do próprio perfil do post.
- **Leads:** 5 planilhas Google lidas por CSV público, ~7h, ~12h e ~18h e pelo botão "Sincronizar":
  formulário Legacy (abas "Leads Completos" e "Leads completos V2"), o Quiz (só os MQL, desde 07/10/2026) e os 2
  formulários da Comunidade (só `utm_source = organico`, sem testes). Banco: `leads_legacy`, `leads_comunidade`,
  `leads_metas`, `leads_vendas`, `leads_sync_log`.
  - **O Cérebro não guarda nome, telefone nem e-mail de lead** (só um código para não contar a mesma pessoa duas
    vezes). Quem é o lead: só na planilha e no Pipedrive.
- **Metas e vendas orgânicas:** lançadas na própria janela ("Editar Meta", "+ Adicionar"). Uma meta por mês, que vale
  para a origem Legacy.

## Os 3 grupos de lead (nunca misturar — explicado pelo Igor em 14/10/2026)

| Grupo | De onde vem | Quem entra | Onde conta |
|---|---|---|---|
| **Orgânico** | formulário Legacy (abas "Leads Completos" e "V2"), todos com utm orgânico | MQL e não MQL | origem Legacy; por perfil pelo canal: bio_legacy, Story_legacy (Legacy); bio_clailton · instagram, Story_clailton (Clailton); bio_clailton · tiktok (TikTok do Clailton) |
| **Quiz** | planilha do quiz (desde 07/10/2026) | **só os MQL** (≥ R$ 70 mil) | também orgânico e na origem Legacy, mas mostrado à parte ("QUIZ - Boas-vindas Legacy", "QUIZ - Link da bio Clailton"…) |
| **Comunidade** | formulários da Comunidade (só utm orgânico) | todos | **totalmente à parte**: origem Comunidade, fora das contas de perfil, post e teste |

Ao falar de leads, diga sempre de qual grupo é ("12 orgânicos (5 MQL) + 2 do Quiz"; "Comunidade: 30, à parte").
Referência (planilhas, 13/10): orgânico 733 desde fev (343 MQL), Quiz 6 (todos MQL), Comunidade 745 desde abr (17 MQL).

## Regras (iguais às do Hub, com as correções)

- **MQL = faturamento a partir de R$ 70 mil** (na prática a faixa "R$ 71 a 100 mil" para cima). É o mesmo corte do
  quiz e do orgânico; só as campanhas da Black usam R$ 50 mil (ver `black-friday-2026.md`).
  Faixas: até 25 mil · 26–50 mil · 51–70 mil · 71–100 mil · 101–400 mil · 401 mil–1 milhão · 1–4 milhões · mais de 4
  milhões. "De 400 mil à 1 milhão" conta como MQL (o Hub perdia essa faixa).
- **Comunidade:** quando o faturamento vem vazio, vale a coluna "MQL (SIM/NAO)" do formulário enxuto. Desde julho o
  formulário enxuto não pergunta o faturamento, por isso o MQL orgânico da Comunidade fica 0 desde julho.
- **Canal** = utm_campaign, senão utm_content, senão a origem, senão "Sem origem". Quando o mesmo canal chega por mais
  de uma rede, o nome ganha a rede ("bio_clailton · tiktok" e "bio_clailton · instagram").
- **Quiz:** aparece como "QUIZ - Boas-vindas Legacy", "QUIZ - Link da bio Clailton" etc.
- A mesma pessoa nas abas Legacy e V2 conta uma vez (a data mais antiga).
- Cores do painel: meta abaixo do esperado em âmbar (vermelho nunca é usado para meta).

## Números para referência (planilhas em 13/10/2026)

| Mês 2026 | Legacy: leads · MQL | Comunidade orgânica: leads · MQL |
|---|---|---|
| fev | 16 · 7 | — |
| mar | 38 · 17 | — |
| abr | 62 · 24 | 1 · 0 |
| mai | 62 · 26 | 45 · 15 |
| jun | 63 · 33 | 78 · 2 |
| jul | 118 · 71 | 279 · 0 |
| ago | 93 · 58 | 141 · 0 |
| set | 212 · 87 | 114 · 0 |
| out (até 13) | 75 · 26 | 87 · 0 |

- Metas no Hub: set/2026 = vendas R$ 130 mil, 50 leads, 60 MQL; out/2026 = vendas R$ 150 mil, 200 leads, 180 MQL.
  Vendas orgânicas lançadas no Hub: set = 5 (R$ 109 mil), out = 1 (R$ 33 mil). Copiadas para o Cérebro em 14/10
  (com o ok do Igor), junto com os cliques no link por dia desde 18/09 (Legacy 8, Clailton 2). O Hub não é mais usado.
- Seguidores em 13/10/2026: Legacy 102.389 · Clailton 262.227 · Allan 2.552.
- Canais de outubro (Legacy): bio_clailton · tiktok é o que mais traz leads (28), bio_legacy o que mais traz MQL.

## Como usar nas análises

- Antes de explicar uma mudança de alcance, retenção ou cliques, leia o card **📌 BIBLIOGRAFIA PERFIL LEGACY** do
  Notion (os testes do social media por dia; ver `referencias/fontes.md`) e cruze com as datas.
- Compare sempre com o período anterior do mesmo tamanho e com a média do mesmo perfil e tipo de post.
- Lead e MQL contra a meta do mês: use o "Esperado" (meta ÷ dias do mês × dias passados).
- Nunca cite nome, telefone ou e-mail de lead.
- Pendente (14/10): uma "porta de leitura" para o Claude consultar esses números direto do banco do Cérebro (proposta;
  depende da migração do Vigia, a 0004). Até lá, peça o print ou o número ao Igor, ou leia as planilhas.

## Janela Resultados (14/10/2026, v1 no ar)

`#resultados` cruza posts × leads × roteiros do Notion × testes da Bibliografia: **Linha do tempo** (por perfil, cada
dia com posts, alcance, cliques, leads do link do perfil e as marcas dos testes), **Por formato** (TD, NV, B-roll, Do topo
à falência, Análise de empresa, Cenário Brasil; leads por post numa janela de 24h; os Ganchos = 1ª frase do roteiro) e
**Testes** (antes × depois de 7 ou 14 dias). Canal → perfil: Legacy = bio_legacy, Story_legacy, quiz Legacy; Clailton =
bio_clailton (Instagram), Story_clailton, quiz Clailton; TikTok do Clailton à parte.
Achados da v1 (dados até 14/10): "Do topo à falência" é o formato que mais traz lead por post na Legacy (só 5 posts);
"Cenário Brasil" alcança ~10× mais; o teste de 3 reels/dia no Clailton aumentou os posts (23 → 32) mas o alcance médio
por post caiu (43 mil → 12 mil) e os leads também (16 → 6); tirar a tag de IA subiu o alcance médio por post em 38%.
Em construção (v2): curva diária de views de cada post, repartição estimada dos leads da bio/story pelos posts e
stories em alta, e o aviso "bombando agora".
