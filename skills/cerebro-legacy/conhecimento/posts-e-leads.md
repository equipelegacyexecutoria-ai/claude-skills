# Posts e Leads no painel do Cérebro (trazidos do Legacy Insights Hub)

Atualizado em 21/10/2026 (mídia paga × visitas × MQL; melhores semanas de MQL × alcance; raio-x de seguidores, alcance e cliques; carrosséis jun–out por esqueleto, formato e capa). Pedido do Igor (13/10): abandonar o Legacy Insights Hub e deixar o Cérebro como o único
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
  - **A curva de cada post** (desde 14/10/2026): view `cerebro_ig_curvas_dia` = quanto cada post ganhou de alcance,
    views e cliques em cada dia. A Meta não dá essa curva pronta (só o total da vida do post): ela sai das fotografias.
    Dia sem fotografia (ex.: Legacy em 18/10/2026, a Meta demorou) = o ganho aparece somado no dia seguinte.
    Desde 19/10 a coleta tenta de novo quando a Meta demora, há repescagem à 01h e às 02h e o sino avisa o Igor.
  - **Os números do perfil por dia** (desde 19/10/2026, tabela `cerebro_ig_conta_dia`, direto da Meta, inclusive dias
    passados até 90 dias): alcance do perfil (seguidores × não seguidores; reels, feed, stories, anúncio), views,
    visitas ao perfil, cliques no site da bio, quem seguiu e quem deixou de seguir, interações. Coleta às ~03h–04h.
  - **A hora de cada lead** (desde 19/10/2026, `leads_legacy.lead_em`): para ver se os leads de um dia vieram em rajada
    logo depois de um post/story. Leads antigos ficam só com a data.
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
| **Orgânico** | formulário Legacy (abas "Leads Completos" e "V2"), todos com utm orgânico | MQL e não MQL | origem Legacy; por perfil pelo canal: bio_legacy, Story_legacy, boas_vindas (Legacy); bio_clailton · instagram, Story_clailton (Clailton); bio_clailton · tiktok (TikTok do Clailton) |
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
- **Mudanças de caminho confirmadas pelo Igor (16/10/2026):**
  - Desde ~05/10/2026 o **link da bio do Clailton leva ao Quiz** (Instagram e TikTok). Os formulários orgânicos do
    Clailton despencam a partir daí (TikTok ~35/semana → 0; Instagram ~16 → 1) e o que chega vem pelo Quiz, que só guarda
    MQL. Não ler como queda de interesse: comparar MQL (orgânico MQL antes × Quiz depois). O "3 reels por dia" começou
    na mesma data.
  - **boas_vindas** (utm_campaign, meio "legacy", desde 12/10/2026) é a mensagem de boas-vindas da Legacy: conta como
    **Orgânico da Legacy**.
  - legacy e legacy_v2 são só versões do mesmo formulário (troca no fim de setembro): não é mudança de caminho.
- A mesma pessoa nas abas Legacy e V2 conta uma vez (a data mais antiga).
- **Planilha × Pipedrive (conferido em 19/10/2026):** os MQL do painel (origem Legacy) = formulário orgânico + Quiz
  somados (out até 19/10: 39 + 11 = 50). No Pipedrive deram 38 + 11: a diferença foi 1 pessoa que preencheu o formulário
  do anúncio e, 5 min depois, o do story; o Pipedrive não duplica e ficou com a UTM do anúncio (conta como pago lá).
  Ao comparar, contar orgânico e Quiz juntos e esperar essa pequena sobra. Os negócios de teste do Quiz ("mac",
  "Igor Teste") seguem abertos no FUNIL IMPULSÃO e têm de sair da conta do Pipedrive.
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
  **Essas vendas vieram do perfil da Legacy** (Igor, 20/10/2026). Ainda não há venda marcada como vinda do perfil do
  Clailton: não atribua essas vendas a ele nem as use como "vendas do Clailton".
- Seguidores em 13/10/2026: Legacy 102.389 · Clailton 262.227 · Allan 2.552.
- Canais de outubro (Legacy): bio_clailton · tiktok é o que mais traz leads (28), bio_legacy o que mais traz MQL.

## Como usar nas análises

- **Pico ou queda de lead num dia ("por que domingo foi o melhor dia?", "algum post decolou?")**: olhe os 3 a 5 dias
  antes nos DOIS perfis, Legacy e Clailton: seguidores ganhos por dia, alcance de não seguidores, o post que mais ganhou
  alcance em cada dia (a curva) e visitas/cliques no site. Um viral de um perfil puxa gente para o outro. Caso real:
  em 17/10/2026 a Legacy ganhou +7.800 seguidores com os próprios posts somando só ~12 mil de alcance novo, no mesmo dia
  em que o reel do Clailton "palácio vira circo" (publicado 16/10) passou de 1,8 milhão de alcance e o Clailton ganhou
  +18 mil; no domingo 18/10 veio o melhor dia de MQL da bio da Legacy. Sinal, não prova: diga "coincide com".
- **Achado de 19/10/2026 (90 dias, 21/07 a 17/10, números do perfil direto da Meta):** os seguidores da Legacy andam
  junto com os do Clailton, não com os posts da própria Legacy. Seguidores novos por dia, Legacy × Clailton:
  correlação 0,95 (0,82 tirando os 10 dias de viral); Legacy × alcance da própria Legacy: −0,01. A Legacy ganha
  ~50% do que o Clailton ganha, todo mês (jul 53%, ago 52%, set 52%, out 50%). As views e interações da conta da
  Legacy acompanham as do Clailton quase 1 para 1 (views da Legacy = 111% das do Clailton, na mediana diária): sinal
  de que os reels do Clailton aparecem também na Legacy (colaboração; a confirmar com o Igor). Exceção: o reel de
  07/08 (3,3 mi) deu só 24% para a Legacy. Leads da bio da Legacy por semana × visitas ao perfil da Legacy: 0,79
  (MQL 0,67); × seguidores ganhos pelo Clailton: 0,66 (MQL 0,56). Dia a dia o MQL é ruidoso: ler por semana.
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

## Raio-x de 20/10/2026 (01/09 a 19/10, API da Meta no banco do Cérebro)

Página: https://claude.ai/artifact/So1kQKCf4fFXxT5TnhYYpF (planilha dos 74 carrosséis completa, com reels da Legacy e do Clailton).
- Seguidores: a Legacy ganhou 62.418 de 01/09 a 18/10; os posts de feed dela registram só 691 (1,1%; 418 de carrossel, 273
  de foto). Ganho diário Legacy × Clailton: 0,98; × alcance dos reels do Clailton: 0,90; × alcance do feed da Legacy: 0,39.
  Estimativa: ~4,4 seguidores da Legacy por mil de alcance dos reels do Clailton + ~140/dia de base.
- Cliques no link da bio da Legacy: 414 em 48 dias; só 22 vieram de post de feed. Por dia, clique × visitas ao perfil 0,67;
  × alcance dos reels do Clailton 0,66; × alcance do feed da Legacy 0,16.
- Reels do Clailton (122, 9,5 mi de alcance): 15 passaram de 100 mil e somam 74%. De 05/10 a 19/10, mediana por reel:
  Novela 34,8 mil (22), B-roll 12,4 mil (9), TD 8,1 mil (12), TD TESTE 876 (6). Pulo no início < 48%: mediana 34 mil;
  > 57%: 11 mil. Abertura "Você...?" 17 mil × outras 12 mil. Alcance × compartilhamento 0,97. 3 reels/dia não derrubou
  a mediana por reel (15 mil antes, 16,5 mil depois).
- Reels da Legacy (25): mediana 940; notícia "Você sabia" 1.250 (pulo 54%) × depoimento entre aspas 753 (pulo 68%).
- Carrosséis da Legacy (74, API atualizada 20/10 10h53 + transcrições do Extrator; página https://claude.ai/artifact/So1kQKCf4fFXxT5TnhYYpF):
  410.641 de alcance, 418 seguidores (47 posts com zero), 694 visitas, 14 cliques. 7 passaram de 10 mil = 64% do alcance.
  Roteiro dos acertos (FMI 2027 e R$ 1,18 tri de juros): capa com fato novo + número gigante → "o que isso significa na
  prática" → "é aí que chega na sua empresa" → "você não controla X, controla Y" → prova com empresa real → oferta. Os 3
  posts com o roteiro completo trouxeram 261 dos 418 seguidores. Card "na prática": 6 posts, alcance típico 4.709 × 1.740.
  Puxam para baixo: capa com pergunta (18 posts, típico 1.384, 4 com seguidor), história com 3+ datas (18, típico 1.186,
  2 com seguidor), fecho "a lição que fica" (24, 5 com seguidor). Do topo à falência: 17 posts, 3 seguidores; os 9 de
  outubro têm todos capa em pergunta. Cliques: 6 dos 14 vieram de comparação do mesmo setor (Habib's × Giraffas etc.).
  Típico set 2.347 → out 1.539.

## Diagnóstico dos leads da bio da Legacy em outubro (21/10/2026)

Pergunta do Igor: "pior mês de leads da bio da Legacy". Banco do Cérebro (leads_legacy, cerebro_ig_conta_dia, cerebro_ig_posts),
sempre dias 1 a 20 de cada mês para comparar igual. Canal bio_legacy, sem Quiz:
- Leads · MQL até o dia 20: mai 37·17, jun 31·19, jul 68·41, ago 50·27, set 40·24, **out 41·19**. Em volume outubro empata com
  setembro; o que caiu é o **MQL** (pior desde junho) e a taxa de MQL (46% × 59–64% em jul–ago). Faixa até R$ 25 mil: 18% dos
  leads em jul–ago, 24% em set, 27% em out.
- Somando as portas da Legacy (bio 41·19 + boas_vindas 16·2 + Quiz boas-vindas Legacy 3·3) outubro dá 60·24: igual a setembro
  no MQL. A mensagem de boas-vindas (desde 12/10) divide a porta e traz lead pior (2 MQL em 16).
- Perfil Legacy, média por dia (1–20): visitas ago 1.922, set 1.385, out 2.232; cliques na bio 178, 179, 191; alcance do feed
  da própria Legacy 52.966, 17.042, **9.495**. Ou seja, chega mais gente (puxada pelos virais do Clailton) e o conteúdo de
  negócio da Legacy é visto por muito menos gente antes do clique. Lead a cada 100 cliques: ~28 ago, 22 set, 21 out.
- Posts da Legacy (1–20/10): estático mediana 1.178 de alcance (set 3.139), 63 visitas (set 250); carrossel mediana 1.520
  (set 2.181), 98 seguidores (set 304).
- Semana 05–11/10 foi a pior: alcance do feed 3.305/dia (o menor da série), 3 MQL. Coincide com o início dos 3 reels/dia,
  link do Clailton indo para o Quiz, teste de "Dicas práticas" e "Do topo à falência" com capa em pergunta.
- Copy: o CTA quase não mudou (formulário + Sessão Estratégica Gratuita). Desde 11/10, 26 dos 29 posts abrem com "Você sabia
  que...". A oferta de aniversário (26 de 31 posts na 2ª quinzena de setembro) saiu; post de 02/10 ainda citava "condição de
  aniversário". Bibliografia sem registro novo desde 13/10.
- **Julho (o melhor mês, 83·49):** 68 dos 83 leads vieram de 01 a 20/07 (pico 06–08/07: 20 leads); de 21 a 31/07, só 15.
  O feed da Legacy viveu da Copa do Mundo (fim em 19/07): "10 negócios do Neymar" (26/06) = 472.868 de alcance, o maior post
  de jun–out; Messi (08/07) 53.288; Cazé × Globo, lições da eliminação da Seleção (06/07), Argentina, Adidas. As listas
  seguintes cansaram (CR7 837, Bellingham 1.136, Kutcher 468, Xuxa 1.046). O CTA era o mesmo de hoje (formulário + Sessão
  Estratégica Gratuita). Story_legacy forte só a partir de 20/07. Métricas do perfil antes de 21/07 não existem no banco
  (a Meta guarda 90 dias): o elo alcance → lead em julho é coincidência de datas, não prova.

## Melhores semanas de MQL da Legacy × alcance (21/10/2026)

Pergunta do Igor: as melhores semanas de MQL do perfil da Legacy têm a ver com o alcance da mesma semana ou da anterior?
Banco do Cérebro, semanas de segunda a domingo, 27/07 a 18/10 (12 semanas; a Meta só guarda 90 dias). MQL do perfil Legacy =
bio_legacy + Story_legacy + boas_vindas + Quiz boas-vindas Legacy + Manychat_legacy, cada pessoa uma vez. Alcance da Legacy
sem anúncio (o "alcance" da conta inclui ~90 a 270 mil/semana de anúncio).
- Melhores semanas: 12–18/10 = 22 MQL; 24–30/08 = 18; 07–13/09 = 16; 10–16/08 = 15; 17–23/08 = 13. Piores: 21/09 e 28/09 = 7.
  A melhor antes disso foi 06–12/07 (20 MQL, Copa), sem dado de alcance.
- Correlação com o MQL semanal (com 12 semanas só vale a partir de ~0,58): alcance próprio da Legacy na mesma semana 0,13, na
  anterior 0,10 (fraco); visitas ao perfil da Legacy na mesma semana 0,71; alcance do Clailton na mesma semana 0,70; views da
  conta Legacy 0,67. Só o MQL da bio: alcance da Legacy da semana anterior 0,43 a 0,49 (sinal fraco, puxado por agosto).
- Dois tipos de semana boa: agosto (10/08, 17/08, 24/08) com o feed da própria Legacy forte (300 a 490 mil/semana) e a semana
  seguinte colhendo; set/out (07/09, 12/10) com o feed da Legacy fraco e o Clailton viralizando (3,5 e 3,6 mi de alcance na
  semana), que lota as visitas da Legacy. 12/10 veio depois da semana com o pior alcance próprio da série.
- Contraexemplo: 27/07 teve o maior alcance próprio da série (558 mil no feed) e só 10 MQL.

## Mídia paga × visitas × MQL (21/10/2026, planilha "Marketing - Legacy Educação" + Gerenciador)

Fontes: planilha do Growth https://docs.google.com/spreadsheets/d/1lmEBMrpX_mzdz7iYwyCCaLdoLHqDnj6DKGwryTdaYL0 (lida pelo Chrome do
Igor, só leitura; a conta Google ligada ao Claude não tem acesso), abas "Overview - Mídia" (anúncios do Growth por dia: investimento,
page view, lead, MQL) e "Meta - Orgânico" (= "Overview - Orgânico"). **"Meta - Orgânico" soma as DUAS campanhas de visita ao perfil**
(conferido no Gerenciador, por dia: 14/10 = 1.327 + 761 = 2.088 × 2.081 na planilha): 121 Anúncios Insta Legacy e 119 Anúncios Insta
Clailton. Para separar, ler o Gerenciador por dia (Detalhamento › Dia, filtro "Anúncios Insta"); a 122 [BOM DE GARFO] só rodou 27/07–03/08,
com valores mínimos. A 121 começou em 24/07. Semanas 27/07 a 18/10; MQL orgânico = perfil Legacy (bio, story, boas-vindas, Quiz Legacy).
- **Peso dos anúncios nas visitas:** 121 = 52.941 de 126.762 visitas da Legacy (42%) e 4.131 de 84.609 seguidores novos (5%), R$ 14.804.
  119 = 45.214 de 195.091 visitas do Clailton (23%) e 15.982 de 174.364 seguidores (9%), R$ 9.257. Visitas da Legacy por dia ≈ 131 +
  1,36 × visitas da 121 + 2,0 por mil de alcance do Clailton (explica 93%). A 119 não mexe nas visitas da Legacy (0,20).
  (Uma leitura anterior do mesmo dia, de 77% pagas, somava as duas campanhas por engano.)
- **MQL orgânico × anúncio da Legacy:** por semana, gasto da 121 × MQL 0,78; visitas da 121 × MQL 0,56; visitas que não vêm da 121 × MQL
  0,72. Mas o gasto da 121 sobe nas mesmas semanas do viral do Clailton (0,59) e da verba do Growth (0,63), então não dá para separar; e
  dia a dia, sem a tendência, visitas e gasto da 121 × MQL = −0,07. MQL por mil visitas: 0,26 nas da 121 × 0,99 nas outras (aproximado).
- **Dia a dia e com atraso (88 dias, 24/07–19/10):** no mesmo dia o anúncio da Legacy não mexe no MQL (tirando o Growth: 0,04; dias de
  Growth baixo: R$ 116 de 121 → 1,14 MQL/dia × R$ 219 → 1,07). Com atraso aparece um sinal: atraso de 2 a 12 dias, +0,12 a +0,20; verba
  da 121 nos últimos 7 dias × MQL dos 7 dias seguintes ~0,5, mantido tirando o Growth e o Clailton e antes de outubro (0,34 a 0,49).
  Semanas sem sobreposição (11): 0,40. Depois de semanas com ~R$ 870 na 121 vieram 7 a 8 MQL; depois da maior (R$ 1.786), 18.
  O que puxa o MQL no mesmo dia: verba do Growth (0,42 nos dias sem viral) e alcance do Clailton (0,36 a 0,43 nos dias de Growth baixo).
- **Seguidor não segue o MQL (21/10):** seguidores ganhos (da 121 ou no total da Legacy) × MQL, mesmo dia ou com atraso de até 14 dias,
  por 7 dias ou por semana: de −0,25 a +0,13 (nada). Desde setembro a 121 passou a entregar seguidor barato (R$ 6 a 11 → R$ 2,2 por
  seguidor; 112 a 232/semana → 373 a 488) e o MQL caiu nas mesmas semanas. O sinal com atraso está no gasto e nas visitas, não no seguidor.
- **Visita barata, visitante pior:** semanas com a visita da 121 mais barata (R$ 0,16 a 0,21: 10/08, 17/08, 12/10) tiveram 1,3 a 2,7 MQL
  por mil visitas pagas; semanas com R$ 0,42 a 0,57 (24/08, 31/08) tiveram 5,3 a 5,6. Sinal, não prova.
- **Anúncio do Clailton (119) × MQL da Legacy:** nenhuma relação (−0,29).
- **Investimento do Growth × MQL orgânico da Legacy:** por dia, tirando a tendência, 0,32 (91 dias); por semana 0,62. Não passa pelos
  leads pagos (0,03) nem pelo Clailton (0,10). Hipótese: quem vê o anúncio do Growth e não preenche vai ao perfil e entra pela bio.
- **MQL pago (Growth):** até 28/09, gastar mais não trouxe mais MQL pago (0,02) e encareceu o MQL (0,50 a 0,67). Em outubro subiu (semana
  05/10 = 76, 12/10 = 121, CPMQL R$ 144) junto com os anúncios da Black "Viva Sem Medo" (06/10; corte de MQL da Black é R$ 50 mil).
  Alcance do Clailton não mexe no MQL pago (−0,06 antes da Black). 12 semanas: Growth R$ 159.400 e 685 MQL pagos; MQL orgânico 146.

## Carrosséis jun–out/2026: esqueleto, formato e capa (20/10/2026)

191 carrosséis da Legacy (01/06 a 19/10), pacote do Extrator + banco do Cérebro (seguidores/visitas/cliques só desde 16/07).
Página: https://claude.ai/artifact/DuTQJ6F3By2yBJTsAJt5RJ. 2,2 mi de alcance; 19 passaram de 10 mil = 84,5% do alcance e
1.613 dos 1.736 seguidores; 36 cliques em 156 posts.
- Esqueleto: "alerta do cenário → impacto na sua empresa" = 72 posts, 10 dos 19 acertos, 1.427 seguidores (82%). "Linha do
  tempo de uma marca" = 22 posts, 0 acertos, 4 seguidores, engajamento 1,7%. "Comparação lado a lado" = 11 posts, 9 dos 36
  cliques, 3,4 visitas/mil (média 1,2). Onda / várias marcas = melhor post típico (3.230).
- Formato: Cenário Brasil 1.203 seguidores (1,41/mil). Do topo à falência como notícia (Quero-Quero 220 mil, Piá 214 mil) ×
  como história (13 posts, típico 1.335, 3 seguidores). Listas de famosos: Neymar 472.868 (26/06), Messi 53.288, depois
  CR7 837, Kutcher 468, Xuxa 1.046 (cansou). Dicas práticas: típico 556, 0 acertos.
- Capa: afirmação com número 14 dos 19 acertos; "?" na capa = 29 posts, 0 acertos, 22 seguidores; capa com "você" 0,63
  seg/mil × 1,11; 16–25 palavras = 16 dos 19 acertos. Imagem: foto real 14% acertam × 4% das outras; IA evidente 0 acertos;
  círculo de logo/detalhe 16% × 5%. Combo afirmação com número + foto real + círculo = 38 posts, 10 acertos, 69% dos seguidores.
- Cuidado: 06–14/08 (20 posts) = 48% do alcance e 71% dos seguidores, coincide com o reel do Clailton de 07/08.
- No Notion: card "📌 CAPAS QUE FUNCIONAM" no MURAL do quadro de tarefas (https://app.notion.com/p/3ffc9747efab8173bed3e444dc48c591),
  com checklist da capa, números, exemplos e o HTML. Pedido do Igor (20/10): as análises novas ficam no MURAL, uma por card, e
  cada atualização entra no topo de "Atualizações" com a data.

