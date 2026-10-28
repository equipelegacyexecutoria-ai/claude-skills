# Decisões e combinados (valem até o Igor mudar)

- **12/10/2026** — O cérebro começa pelo **Orgânico**; quem decide no dia a dia é o **Igor**; assuntos
  grandes vão para Allan ou Clailton (sócios).
- **12/10/2026** — Relatório **só para o Igor** até segunda ordem: seg–sex às 8h e resumo da semana no
  domingo. Entrega na página privada do Notion "Relatórios do Orgânico (Claude)"; Discord quando
  houver o webhook do canal privado dele.
- **12/10/2026** — Reuniões viram cards no Notion feitos pelo time; o Claude só cria tarefa quando o
  Igor orientar.
- **12/10/2026** — O bloco SENHAS do Notion nunca é lido, copiado, enviado ou usado para nada.
- **12/10/2026** — As rotinas oficiais rodam na **nuvem da Anthropic** (não dependem de PC ligado):
  relatório seg–sex 8h (`trig_01PyJ5JGjrhN9YuDaPk8hM72`) e resumo domingo 18h
  (`trig_019Y2557NDeBn1z4Ltu7FTHJ`), em https://claude.ai/code/routines. As instruções estão dentro
  de cada rotina (sem GitHub); mudou o procedimento aqui, atualize também a rotina. Na nuvem a
  memória do dia fica na seção "🧠 Memória do dia" de cada relatório no Notion. As tarefas agendadas
  deste PC ficaram desligadas, como reserva.
- **12/10/2026** — O site do cérebro fica em Desktop › PROJETOS ANTIGRAVIDADE › cerebro-legacy,
  no GitHub privado `legacyeducacao/cerebro-legacy` (remote `origin`; mudou da conta Executoria em
  13/10 a pedido do Igor; commits assinados como legacyeducacao, senão a Vercel grátis bloqueia) e na
  Vercel `cerebro-legacy-organico` do time equipelegacyexecutoria-6387s-projects (push na main publica,
  e só quando o Igor pedir). O site lê
  o JSON da página Notion "Dados do painel (não editar)" (3f7c9747-efab-81c7-b08d-f989567f62eb),
  que a rotina na nuvem `trig_013T67yZFufHgC8mBeGUQERG` (seg–sex 8h20) monta a partir do
  relatório do dia. Senha e token do Notion ficam só nas variáveis da Vercel, colocados pelo Igor.
  O painel no claude.ai continua valendo até o site ir ao ar.
- **12/10/2026** — Planejamentos estratégicos (V1–V4) provavelmente desatualizados; o Igor valida
  na terça 13/10.
- **12/10/2026** — **O Cérebro é independente** (pedido do Igor): nada pode depender do Legacy Insights
  Hub, e tudo fica dentro da pasta `cerebro-legacy` (contrato técnico em `docs/arquitetura.md`, banco em
  `supabase/migrations/`, textos das rotinas em `rotinas/`). Outras pastas e o Supabase do Insights Hub
  só podem ser **lidos/copiados**, nunca modificados ou apagados. As tabelas `cerebro_acessos` e
  `cerebro_notificacoes` que tinham sido criadas no Supabase do Insights Hub ficam lá intocadas.
  - Banco e login próprios: projeto Supabase **"Cérebro Legacy"** (`usgbaixvzdpletkwbnlb`, org
    "Igor Oliveirs", plano grátis), já com as tabelas (acessos, notificações, tarefas + eventos +
    fotografia diária por pessoa, posts do Instagram, fotografias do dia, coletas) e o Igor como admin.
  - Instagram direto na API da Meta (`api/_instagram.js`, variável `INSTAGRAM_TOKEN`). O token atual é
    de usuário e **vence em 06/12/2026**; o site avisa o admin 20 dias antes. Trocar por token de
    usuário do sistema (não vence).
  - **Histórico de tarefas por pessoa** (pedido do Igor: concluídas, atrasadas, quem atrasa, com que
    frequência) fica no **painel do site** (aba Tarefas), não no Notion. Quem grava é `api/coletar.js`,
    chamado pelo cron da Vercel às 00h05; a rotina da meia-noite na nuvem
    (`trig_01MJmrDxNLVXbzqg7baZt9Gd`) foi **desligada** (o proxy da nuvem bloqueava o Supabase).
  - As tabelas "Posts do Instagram", "Fotografias diárias" e "Tarefas por pessoa" criadas no Notion
    (página "Histórico do Cérebro (não editar)") não são mais usadas; o Igor não quer tabela no Notion.
- **15/10/2026 — Chat do Cérebro pensa como analista (pedido do Igor).** Seja qual for a pergunta, o chat
  mira a cadeia post → visita ao perfil → lead → MQL → reunião → venda: responde com números, abre os posts
  um a um (melhores × piores do mesmo tipo, com gancho, estilo, dia/hora e roteiro do card no Notion), cruza
  com leads e Pipedrive e fecha com **Padrão** (teses com evidência, tese ≠ prova) e um próximo teste.
  Alcance comparado pela mediana (viral distorce a média). Nunca dizer que um post gerou lead.
- **19/10/2026 — Pico de lead se explica olhando os dois perfis e a curva (pedido do Igor).** Antes de explicar pico
  ou queda de lead/MQL, o Cérebro olha os 3 a 5 dias anteriores na Legacy E no Clailton: seguidores ganhos, alcance de
  não seguidores, o post que mais ganhou alcance em cada dia (curva de `cerebro_ig_curvas_dia`) e visitas/cliques no
  site (`cerebro_ig_conta_dia`). Um viral de um perfil transborda para o outro. Fala "coincide com", nunca "gerou".
- **19/10/2026 — A Nina chama lead a qualquer hora (decisão do Igor).** Não existe janela de 8h–21h;
  mensagem da Nina de madrugada ou à noite não é erro e não entra como falha nos relatórios.
- **28/10/2026 — Rotina "Pautas diárias" (pedido do Igor).** Todo dia às 9h (Brasília), na nuvem
  (`trig_016PBRSmGLbW7xrUb8CUxm8k`, https://claude.ai/code/routines/trig_016PBRSmGLbW7xrUb8CUxm8k), o Claude pesquisa
  fatos novos (Brasil, setor, empresas gigantes, comparações) e cria de 2 a 8 cards de carrossel da Legacy na coluna
  **PAUTAS DIÁRIAS** do quadro (visão Social Media), sem responsável nem data, com capa sugerida, roteiro e fontes.
  Tema de consumidor fica de fora (0 de 14 passou de 2,2 mil em set–out). O texto da rotina está em
  `rotinas/pautas-diarias.md`; mudou o texto, atualize a rotina na nuvem também. Ela só cria cards, não mexe em mais nada.
