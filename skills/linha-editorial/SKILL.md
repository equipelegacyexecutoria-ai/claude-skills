---
name: linha-editorial
description: Cria a linha editorial completa de uma empresa para redes sociais (Instagram, TikTok, LinkedIn, YouTube, stories) com método pesquisado (missão editorial e diferencial do Content Marketing Institute, pilares com percentual e funil, Hero/Hub/Help do Google, tom de voz nas 4 dimensões da Nielsen Norman, frequência e horários por estudos Buffer, Sprout, Metricool e Opinion Box/mLabs). Primeiro faz as perguntas certas (12 essenciais ou questionário completo, e uma versão pronta para mandar ao cliente), depois entrega um documento HTML da linha editorial e um calendário em planilha (Excel + CSV) com datas, dias, horários, formatos, estilos de post, pilares, temas, ganchos, CTAs e as datas comemorativas e feriados do período. Use quando pedirem "linha editorial", "estratégia de conteúdo", "planejamento de conteúdo", "calendário editorial", "pilares de conteúdo", "o que postar", "cronograma de posts", "grade de postagem", "plano de redes sociais para a empresa X", ou para refazer o calendário do mês de um cliente que já tem linha editorial. Não use para escrever a copy final de cada post (carrossel, reels, legenda têm skills próprias) nem para agendar posts.
---

# Linha editorial

Linha editorial é o conjunto de decisões que diz **sobre o que** a marca fala, **para quem**, **com que
voz**, **em que formato**, **com que frequência** e **para quê**. O calendário é essa linha aplicada no
tempo. A entrega desta skill tem os dois:

1. `Linha Editorial - <Empresa>.html`: documento de uma página longa, bonito, que abre em qualquer
   computador e celular e pode ser impresso em PDF. Vai para o dono e para o time.
2. `Calendario - <Empresa>.xlsx` (+ `.csv`): planilha de produção com uma linha por post (data, dia,
   hora, rede, formato, estilo, pilar, funil, tema, gancho, CTA, data especial, status, responsável).
   O CSV importa no Notion ou em agendador.

Os dois saem de um único `dados.json`, montado pelo script `scripts/linha_editorial.py`, que também
calcula as vagas do período, coloca feriados e datas comemorativas do segmento (Páscoa, Carnaval, Dia das
Mães, Black Friday etc. são calculados para qualquer ano) e confere tudo.

## Arquivos de referência (ler na hora certa, não tudo de uma vez)

| Arquivo | Quando ler |
|---|---|
| `references/questionario.md` | Fase 1, antes de perguntar |
| `references/metodologia.md` | Fase 2, antes de decidir a estratégia (método em 10 camadas + fontes) |
| `references/estilos-de-post.md` | Fase 2, para escolher estilos, quadros, stories e CTAs |
| `references/horarios-e-frequencia.md` | Fase 2, para frequência e horários |
| `references/modelo-dados.md` + `assets/exemplo-dados.json` | Fase 3, para escrever o `dados.json` |

## Fluxo

### Fase 0. Ler o que já existe
Antes de qualquer pergunta, ler o que o usuário mandou ou apontou: site, Instagram (pelo navegador),
briefing, materiais, conversas, ou o Notion/Pipedrive se for cliente da Legacy (skill `cerebro-legacy`
tem o mapa). Se o perfil estiver na mLabs, puxar `get_best_posting_times`, `get_posts_by_day_and_time`
e `get_top_content` (conector mLabs, só leitura) para horários e formatos reais.
Nada disso é obrigatório: se não houver material, vá para as perguntas.

### Fase 1. Perguntar (o coração da skill)
Ler `references/questionario.md` e:
- **Padrão: modo rápido.** Uma mensagem com as 12 perguntas essenciais, numeradas e curtas, **tirando as
  que a Fase 0 já respondeu** (diga em uma linha o que já sabe). Avise que pode responder por áudio,
  "não sei" vale e que dá para pular.
- **Modo completo** (blocos A a I) quando o usuário pedir, quando for uma empresa grande/marca nova, ou
  quando as respostas do modo rápido vierem rasas. Mandar um ou dois blocos por vez.
- **Para o cliente responder**: se o usuário disser que vai mandar ao cliente, entregar a "Versão para
  mandar ao cliente" do questionário, adaptada com o nome da empresa, pronta para colar no WhatsApp.
- Se o usuário já trouxer tudo no pedido, pular para a Fase 2.
- Não pergunte o que dá para decidir com o método (pilares, horários, formatos): isso é trabalho da
  skill. Pergunte fatos do negócio, do público, da voz e da capacidade do time.

### Fase 2. Decidir a estratégia
Ler `metodologia.md`, `estilos-de-post.md` e `horarios-e-frequencia.md` e decidir, nesta ordem:
1. Objetivo principal e metas (com número).
2. Missão editorial na fórmula "A [empresa] é onde [público] encontra [conteúdo] para [benefício]",
   diferencial e "do que não falamos".
3. Público: persona, dores, desejos, objeções, perguntas (vira o banco de temas).
4. Tom de voz: 4 dimensões de 1 a 5, somos/não somos, usar/evitar, 1 exemplo "assim não / assim sim"
   com frase real do segmento.
5. 3 a 5 pilares com percentual (somando 100), funil, papel (Help/Hub/Hero) e 3+ exemplos de tema.
   Mix padrão 80/20 (valor x venda), ajustado ao objetivo.
6. 6 a 10 estilos de post com estrutura adaptada ao segmento; 1 a 3 quadros fixos com nome e dia.
7. Canais, frequência **dentro da capacidade do time**, grade semanal com horários (e de onde vieram),
   rotina de stories.
8. Fluxo de produção e aprovação, métricas por objetivo e rotina de revisão.

### Fase 3. Escrever o dados.json e as pautas
1. Criar a pasta de saída: a que o usuário indicar; sem indicação, a pasta desta conversa, numa
   subpasta `Linha Editorial <Empresa>`.
2. Escrever `dados.json` seguindo `references/modelo-dados.md` (copiar a estrutura de
   `assets/exemplo-dados.json`). Período padrão: 4 semanas a partir da próxima segunda.
3. Rodar as vagas (caminho completo da skill; no Bash `~` funciona):
   ```
   python ~/.claude/skills/linha-editorial/scripts/linha_editorial.py vagas "<pasta>/dados.json"
   ```
   Sai cada vaga do período (data, hora, rede, formato, estilo, pilar) e as datas especiais.
4. Escrever `pautas` no mesmo arquivo: uma por vaga (pode trocar o pilar de uma vaga para equilibrar,
   e acrescentar post extra em data forte). Cada pauta com **tema concreto, gancho (a primeira frase ou
   tela, do jeito que será dita) e CTA variado**. Usar dores, objeções e perguntas do público. Data
   especial só entra se combinar com a marca; data comercial forte do segmento vira campanha (Hero).

### Fase 4. Montar e conferir
```
python ~/.claude/skills/linha-editorial/scripts/linha_editorial.py montar "<pasta>/dados.json"
```
Corrigir todos os **ERROS** e os **AVISOS** que fizerem sentido (post extra fora da grade é normal),
editando o `dados.json` e rodando de novo. Não precisa abrir o HTML para conferir: o layout já foi testado.

### Fase 5. Entregar
Resposta curta (o usuário quer direto ao ponto): links dos arquivos, a missão editorial em uma linha,
os pilares com percentual, frequência e horários, quantos posts no período e o que ficou como suposição.
Depois ofereça, em uma linha cada, só o que fizer sentido:
- publicar o documento como link (Artifact) para mandar ao cliente;
- importar o calendário no Notion (CSV) ou criar os cards;
- escrever os posts com as skills de copy (carrossel, reels, legenda);
- refazer o calendário do mês seguinte (só rodar a Fase 3 de novo com novo `periodo` e novas pautas).
Agendar na mLabs só com pedido explícito e seguindo a regra do CLAUDE.md (sempre a versão mais recente).

## Regras de escrita
- Tudo em português do Brasil, linguagem do dia a dia do cliente, sem jargão de marketing.
- O documento é lido pelo dono e pelo time: seguir `escrita-sem-cara-de-ia` (sem travessão, sem
  "crucial", "jornada", "potencializar", "além disso"; fato concreto no lugar de frase genérica).
  O `montar` avisa quando encontra esses sinais.
- Temas e ganchos específicos: "3 sinais de que a gengiva precisa de atenção", não "dica de saúde bucal".
- Número e fonte quando citar estudo; horário sempre marcado como ponto de partida a revisar.
- Respeitar regras do conselho de classe e da lei do segmento (CFM, CFO, OAB, CVM, Anvisa, LGPD).
- Marcas da Legacy / Clailton: seguir também as regras do CLAUDE.md (Clailton sem barba, rosto da esposa
  e do filho nunca aparece, área segura dos Reels) e o contexto da `cerebro-legacy`.

## Manutenção
- Datas fixas e campanhas do mês ficam em `assets/datas.json` (com segmentos). Datas móveis são
  calculadas no script (`datas_moveis`). Para incluir uma data, edite o JSON.
- Precisa de `openpyxl` (já no `requirements.txt`); sem ele o script gera só o CSV e avisa.
