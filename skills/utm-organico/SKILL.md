---
name: utm-organico
description: Padrão de UTM do orgânico da Legacy Executoria (aprovado pelo Igor em 24/11/2026). Monta links com etiquetas UTM para qualquer publicação do orgânico (bio, story, destaque, mensagem de boas-vindas do ManyChat, live, comente, direct, post, e-mail, WhatsApp) dos perfis Legacy e Clailton; confere links que alguém mandar e devolve corrigidos; troca nomes antigos (bio_legacy, Story_legacy, boas_vindas, link_in_bio, live_instagram) pelos novos; monta os botões da página de links do Clailton (legalinks) nas versões Instagram e TikTok. Use sempre que pedirem "monta o link", "link com UTM", "UTM do story/da live/da bio", "confere esse link", "esse link está no padrão?", "link para o ManyChat", "link para o linktree/legalinks", ou mandarem um endereço da Legacy para etiquetar. Não serve para tráfego pago (anúncios da Meta têm padrão próprio).
---

# UTM Orgânico (Legacy)

Padrão aprovado pelo Igor (coordenador do Orgânico) em 24/11/2026. O guia do time, em linguagem
simples, está no Notion: "PLAYBOOK | Padrão de UTM do Orgânico"
(https://app.notion.com/p/422c9747efab81bdbfbae01fa1fb04c6). Esta skill segue exatamente o mesmo padrão.

Responda sempre em português do Brasil, direto, sem travessão. Quem pede não é técnico: entregue o
link pronto em bloco de código (um link por bloco, com o nome do botão ou da peça em cima) e só
explique o que for preciso.

## O padrão: cinco etiquetas, cada uma responde uma pergunta

| Etiqueta | Pergunta | Valor |
|---|---|---|
| utm_source | é orgânico? | sempre `organico` |
| utm_medium | em qual rede o link foi publicado? | a rede (tabela abaixo) |
| utm_campaign | de qual perfil saiu? | o perfil (tabela abaixo) |
| utm_content | por onde a pessoa clicou dentro do perfil? (no Pipedrive: "Conjunto") | o caminho (tabela abaixo) |
| utm_term | qual peça trouxe o lead? (no Pipedrive: "Criativo") | a peça (tabela abaixo) |

Modelo, sempre nesta ordem:

```
ENDEREÇO?utm_source=organico&utm_medium=REDE&utm_campaign=PERFIL&utm_content=CAMINHO&utm_term=PECA
```

Se o endereço já tiver `?`, troque o `?` do modelo por `&`.

### utm_medium (rede)

`instagram` · `tiktok` · `facebook` · `youtube` · `linkedin` · `email` · `whatsapp`

ManyChat (boas-vindas e resposta ao "comente") chega pelo direct do Instagram: a rede é `instagram`.

### utm_campaign (perfil)

- `legacy`: tudo que sai do perfil da Legacy (Instagram @legacyexecutoria, YouTube, LinkedIn, e-mail da Legacy).
- `clailton`: tudo que sai do perfil do Clailton (Instagram @clailtonluiz, TikTok, Facebook dele).

Outro perfil (ex.: Allan) ainda não tem nome aprovado: diga que precisa da aprovação do Igor e não invente.

### utm_content (caminho)

| A pessoa clica... | utm_content |
|---|---|
| no link da bio ou num botão da página de links da bio | `bio` |
| na figurinha de link do story do dia | `story` |
| num story feito para ficar fixo nos destaques | `destaque` |
| na mensagem automática para quem começa a seguir (ManyChat) | `boasvindas` |
| no link mostrado ou fixado durante a live | `live` |
| no link que o ManyChat manda depois que a pessoa comenta uma palavra (reels, post ou live) | `comente` |
| num link mandado à mão numa conversa do direct | `direct` |
| no link escrito no texto do post (LinkedIn, Facebook, descrição do YouTube) | `post` |
| no e-mail para a base | `email` |
| numa mensagem de WhatsApp para uma lista | `disparo` |
| numa mensagem em grupo ou comunidade do WhatsApp | `grupo` |

Story que sai no dia é `story`, mesmo que depois vá para os destaques.

### utm_term (peça)

| Caminho | A peça diz | Exemplo |
|---|---|---|
| story, live, post, direct | data e assunto | `2026-11-24_lucro-caixa` |
| comente | data do post ou da live e a palavra comentada | `2026-11-18_lucro` |
| boasvindas | versão e tema da mensagem | `versao-a_vendas` (só uma versão no ar: `versao-a`) |
| bio com um link só (ex.: bio da Legacy) | nada: não leva `utm_term` | |
| bio que abre uma página de links com vários botões | qual botão | `botao-sessao`, `botao-quiz`, `botao-palestra` |
| destaque | nome do destaque | `venda-mais-lucre-mais` |
| email, disparo, grupo | data do envio e assunto | `2026-11-22_convite-live` |

Dois links na mesma peça (ex.: dois links no mesmo story): cada um com assunto diferente.

### Regras de escrita (valem para todas as etiquetas)

- Tudo minúsculo, sem acento, sem espaço, sem cedilha.
- `_` separa as partes; `-` junta as palavras dentro de uma parte.
- Data sempre `aaaa-mm-dd` (ex.: `2026-11-24`).
- Assunto com 1 a 3 palavras.
- Nunca deixar etiqueta vazia nem usar valor fora das tabelas. Única exceção: bio com um link só não leva
  `utm_term` (regra do Igor, 24/11/2026: é o padrão, não precisa marcar). Valor novo só com aprovação do Igor.

## Páginas de destino (endereço sem nada depois)

| Página | Endereço |
|---|---|
| Sessão estratégica (bio da Legacy) | `https://formulario.legacyexecutoria.com.br/` |
| Quiz do Clailton (Venda Mais, Lucre Mais) | `https://quiz.legacyexecutoria.com.br/` |
| Legado Sinergia | `https://legado.legacyexecutoria.com.br/sinergia` |
| Black (orgânico) | `https://black.legacyexecutoria.com.br/organico` |
| Comunidade (Academy) | `https://academy.legacyexecutoria.com.br/lp/captacao` |
| Palestras do Clailton (formulário) | `https://legalinks.legacyexecutoria.com.br/clailton/palestras` |

Se pedirem um link para uma página fora desta lista, monte com o endereço que a pessoa mandar, mas
avise que a página não está na lista e que vale testar se ela guarda as etiquetas.

## Como atender cada pedido

**"Monta o link de..."**
1. Tire do pedido a página, o perfil, a rede, o caminho e a peça (data e assunto). Deduza o óbvio
   (story da Legacy no Instagram → `instagram`, `legacy`, `story`; data de hoje se a pessoa disser "hoje").
2. Pergunte só o que faltar e não der para deduzir, numa pergunta curta. Sem assunto, use o tema que a
   pessoa citou; sem tema nenhum, pergunte.
3. Entregue o link pronto num bloco de código. Embaixo, uma linha lembrando de abrir o link no celular
   antes de publicar e conferir se as etiquetas continuam na barra de endereço.

**"Confere esse link"**
1. Separe o endereço e cada etiqueta. Ignore `fbclid`, `mcp_token` e outros parâmetros que as redes
   colocam sozinhas.
2. Diga o que está fora do padrão, em frases curtas (ex.: "o perfil está no medium", "a data está no
   formato antigo", "esse botão leva ao Sinergia mas está marcado como VMLM").
3. Entregue o link corrigido. Se não der para saber a peça ou o caminho, pergunte.

**Página de links / bio (legalinks, linktree)**
Monte um link por botão e entregue as duas versões quando o perfil estiver nas duas redes: uma com
`utm_medium=instagram` e outra com `utm_medium=tiktok`. Avise que, para o TikTok ser contado separado,
ele precisa de uma página de links própria; se os dois perfis abrirem a mesma página, tudo conta como
a rede que estiver nos botões. O `utm_source=ig&utm_medium=social` que o Instagram coloca sozinho no
link da bio não precisa ser mexido: o que vale para o lead são as etiquetas dos botões.

**"Mandar tudo junto / numa mensagem só"**
Junte todos os links num único bloco de código, cada um com uma linha de título antes, para a pessoa
copiar de uma vez.

## Página de links do Clailton (legalinks.legacyexecutoria.com.br/clailton)

Botões que levam a lead (conferidos em 24/11/2026): "Ver caminho" (quiz Venda Mais, Lucre Mais),
"Quero minha sessão estratégica" (Legado Sinergia) e "Pedir uma palestra" (formulário de palestras).
Os botões Instagram e YouTube do rodapé só abrem o perfil e não levam etiqueta.

Versão Instagram:
```
https://quiz.legacyexecutoria.com.br/?utm_source=organico&utm_medium=instagram&utm_campaign=clailton&utm_content=bio&utm_term=botao-quiz
https://legado.legacyexecutoria.com.br/sinergia?utm_source=organico&utm_medium=instagram&utm_campaign=clailton&utm_content=bio&utm_term=botao-sessao
https://legalinks.legacyexecutoria.com.br/clailton/palestras?utm_source=organico&utm_medium=instagram&utm_campaign=clailton&utm_content=bio&utm_term=botao-palestra
```

Versão TikTok: os mesmos três, com `utm_medium=tiktok`.

## Nomes antigos e o nome novo

| Antes | Agora |
|---|---|
| `bio_legacy`, `bio_clailton`, `link_in_bio` | perfil em `utm_campaign` e `bio` em `utm_content` |
| `Story_legacy`, `story_clailton`, `stories_legado` | `story` em `utm_content` |
| `boas_vindas`, `boasvindas_clailton`, `legacy_mensagem_boas_vindas`, `clailton_mensagem_boas_vindas`, `menssagem_de_boas_vindas` | `boasvindas` em `utm_content` |
| `live_instagram` e data na campanha (`17_11_26`) | `instagram`, `live` e a data na peça |
| `teste_a_vendas`, `teste_b_lucro` | `versao-a_vendas`, `versao-b_lucro` |
| perfil no medium (`facebook_clailton`, `reels_clailton`, `stories_clailton`, `legacy`) | só a rede no medium e o perfil na campanha |
| `organic`, `ig`, `Instagram`, `Tiktok` | `organico`, `instagram`, `tiktok` |
| datas `17_11_26`, `05-11-2026`, `28_07_2026` | `2026-11-17`, `2026-11-05`, `2026-07-28` |
| `bio_clailton_vmlm`, `bio_clailton_legado`, `bio_clailton_palestras` | `bio` + `botao-quiz`, `botao-sessao` ou `botao-palestra` |

## Exemplos prontos

Story da Legacy de 24/11 sobre lucro, levando para a Black:
```
https://black.legacyexecutoria.com.br/organico?utm_source=organico&utm_medium=instagram&utm_campaign=legacy&utm_content=story&utm_term=2026-11-24_lucro-caixa
```

Boas-vindas da Legacy, versão A sobre vendas, levando para a Comunidade:
```
https://academy.legacyexecutoria.com.br/lp/captacao?utm_source=organico&utm_medium=instagram&utm_campaign=legacy&utm_content=boasvindas&utm_term=versao-a_vendas
```

Bio da Legacy, levando para a sessão estratégica:
```
https://formulario.legacyexecutoria.com.br/?utm_source=organico&utm_medium=instagram&utm_campaign=legacy&utm_content=bio
```

Reels do Clailton de 18/11 com "comente LUCRO", levando para o quiz:
```
https://quiz.legacyexecutoria.com.br/?utm_source=organico&utm_medium=instagram&utm_campaign=clailton&utm_content=comente&utm_term=2026-11-18_lucro
```

Link fixado na live da Legacy de 17/11, levando para a Black:
```
https://black.legacyexecutoria.com.br/organico?utm_source=organico&utm_medium=instagram&utm_campaign=legacy&utm_content=live&utm_term=2026-11-17_cenario-2027
```

## Bom saber

- Nunca publique o endereço sem etiquetas: o lead entra sem origem e não dá para descobrir depois.
  Em novembro de 2026, 102 dos 105 leads do Legado Sinergia chegaram assim.
- Se ao abrir o link a página perder as etiquetas da barra de endereço, não publique e avise o Igor.
- O painel Leads do Cérebro contava os funis pelos nomes antigos até ser ajustado. Se alguém perguntar
  quando começar a usar, a data é a que o Igor combinar com o time.
