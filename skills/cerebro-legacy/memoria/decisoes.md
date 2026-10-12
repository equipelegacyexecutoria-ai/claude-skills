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
  no GitHub privado `equipelegacyexecutoria-ai/cerebro-legacy` (remote `origin`, escolha do Igor) e na
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
