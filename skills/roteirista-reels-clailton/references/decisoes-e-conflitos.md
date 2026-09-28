# Decisões e conflitos

Onde as fontes antigas discordam dos dados, esta tabela diz o que vale e por quê. Decisões do usuário (26/09/2026): prioridade total a alcance, **sem guardião de marca** no fluxo, Diretor sugere o formato e o usuário escolhe.

Fontes antigas: `molde-novela-clailton.md` e `FORMATO_talkhead-Clailton.md` (Downloads), skill sincronizada `copy-reels-legacy`, skill sincronizada `legacy-narrative-guardian`, `funil-conteudo-clailton.png`.

| # | Conflito | Fonte antiga diz | Os dados mostram | Decisão |
|---|---|---|---|---|
| 1 | CTA de palavra-chave | Talkhead: todo reel fecha com palavra-chave para o produto | Palavra-chave: comentários ~5x, mas curtida ~3,6% e repost ~0,04%; na tela, 1 de 4 acima de 1x; "link da bio" 0 de 7 acima de 150 mil | Objetivo alcance: sem CTA de venda. Palavra-chave só no objetivo conversão, com aviso de que reduz alcance |
| 2 | CTA sempre pede share ou comentário | `copy-reels-legacy` | "Nenhum" é o grupo FORTE (~1x); envio funcionou quando casado com o tema (2 de 2) | CTA pelo objetivo (tabela em `framework-viral.md`) |
| 3 | Duração | Talkhead: 1:30 a 2:30 fixo · `copy-reels-legacy`: 30 a 90 s | 60 a 180 s não explica alcance; vencedores: novela ~65 a 95 s, tela ~100 a 165 s | Faixa por formato, só como aviso |
| 4 | "pra", "tá", "cê", "Adivinha?" | `copy-reels-legacy` | Clailton fala "para" 568x contra "pra" 13x; "teu/tua" 431x contra "seu/sua" 137x | Voz medida (`voz-clailton.md`) |
| 5 | Culpar o empresário | Guardião: proibido ("você é o problema") | Hooks que acusam o espectador viralizam ("O pior funcionário da sua empresa pode ser... você", 199 mil) | Sem guardião. Regra de ofício: o hook acusa, a virada absolve |
| 6 | "Fórmula", "segredo" | Guardião: proibido | "Eu vou te mostrar uma fórmula ridiculamente simples..." 316 mil; "O segredo do sucesso é desagradar..." 167 mil | Permitido quando o vídeo entrega o que promete |
| 7 | Governo como vilão | Guardião: nunca o inimigo central | "O governo é o único sócio da tua empresa..." 6,7 mil; split payment 28 mil (fracos, sem ser por isso) | Liberado, mas a tabela de temas mostra política irregular; sem figura política como protagonista (risco de polarização) |
| 8 | Hook de lista numerada | Molde novela: "Três erros que o dono comete..." | Lista abrindo o reel: 0,64x; a única lista forte abriu com tese | Lista só depois de um hook-tese |
| 9 | Vocativos "gente", "pessoal", "rapaziada" | Talkhead: vocativos rotativos | Abertura de apresentador perde retenção; nenhum vencedor abre assim | Nunca na abertura; no meio, raro |
| 10 | Ponte pessoal obrigatória | Talkhead: batida 6 obrigatória | Histórias pessoais variam: oficial de justiça 6,5x; "Eu estava perdendo a minha família" 0,32x (abertura narrativa na novela) | Opcional, só com o banco de biografia, e nunca como hook de novela |
| 11 | "Promessa sobre o vídeo" | Estudo: antipadrão geral | Na tela, 2 de 4 acima de 3x quando o vídeo cumpriu a promessa ao pé da letra; promessa vazia fracassa | Aposta permitida só na tela, com entrega literal |
| 12 | Views das novelas | Estudo compara formatos por views | Funil: novelas vencedoras recebem verba em público frio pelo mesmo ID | Campo `impulsionado`; o Analista separa impulsionados no backtest; seleção de novela pelo funil é seguidores por alcance |
| 13 | Nome do formato | Calendário do time: "talking head" | Classificação visual: é a tela dividida | Mesma coisa; "talking head" aqui = tela dividida |
| 14 | Fala do administrador na biografia | Talkhead: "Cláudio, quebramos" | Reel #109: "Clailton, a empresa está quebrada" | Usar a fala do #109 |
| 15 | Primeiro emprego | Talkhead: "aos 16, caipirinha de steinhäger" | Reel #109: "Meu primeiro emprego foi como açougueiro" | Não usar "primeiro emprego" até o usuário confirmar |
| 16 | Gatilho duplicado | `copy-reels-legacy` também dispara com "roteiro pro Clailton" | A skill antiga não conhece os dois formatos | Esta skill tem descrição estreita (Clailton + novela/tela dividida). Ajustar a descrição da antiga no claude.ai (não dá para editar a cópia sincronizada) |
| 17 | Travessão | Molde novela e talkhead: proibido | 0 travessões nas transcrições | Mantido: proibido (lint reprova) |
| 18 | "PME" | Talkhead: proibido | 0 ocorrências nas transcrições | Mantido: proibido (lint reprova) |

Como registrar uma nova decisão: acrescente uma linha com a data, a fonte e a evidência. O Analista mensal revisa esta tabela quando os números mudarem.
