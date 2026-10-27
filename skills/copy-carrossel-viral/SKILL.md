---
name: "copy-carrossel-viral"
description: "Gera a copy completa de carrosséis virais da Legacy (cenário, tela dividida, empresa/notícia) e do Clailton (estilo X), perguntando antes o que falta, e sobe o briefing no Notion."
---

# Copy Carrossel Viral (Legacy e Clailton)

Entrega: o 📝 BRIEFING completo de um carrossel (direcionamento, design, referências, dimensões, entrega, copy card a card e legenda), pronto para o time de design, e o upload no card do Notion.

Regra zero: NUNCA usar travessão (— ou –) em nada, nem na copy nem na resposta. Trocar por ponto, vírgula ou dois pontos.

## 1. Entrevista (antes de escrever)

Confira o que o usuário já mandou. Pergunte SÓ o que faltar, numa única mensagem curta (use AskUserQuestion quando disponível, até 4 perguntas). Não pergunte o que dá para descobrir sozinho.

Obrigatório:
1. Perfil e formato:
   - LEGACY · Cenário
   - LEGACY · Tela dividida (quem afunda x quem cresce)
   - LEGACY · Empresa/notícia (quadro de empresas conhecidas, Do Topo à Falência, empresas recalculando a rota)
   - CLAILTON · Post estilo X (Twitter)
2. Base do conteúdo: link de referência (reel/post validado, próprio ou de outro perfil), notícia/dado com link, ou só o tema (aí você pesquisa).
3. Card do Notion onde subir (link). Se não houver, pergunte se cria um card novo ou só entrega no chat.

Opcional (pergunte só se fizer diferença real):
4. Vai sair outro post no mesmo dia sobre o mesmo tema? (se sim, o carrossel não pode ser transcrição dele)
5. Ângulo desejado (ex.: contratação, caixa, liderança) ou setor específico.
6. Card-modelo aprovado para seguir a estrutura.
7. Campanha ativa que muda o CTA (Black, Plano 2027, palavra-chave de DM).

Se o usuário não responder ou disser "decide você", escolha o caminho mais provável, diga em uma linha qual escolheu e siga.

## 2. Coleta e checagem (sozinho)

- Referência do Instagram: abrir o post no Chrome (aba no instagram.com) e ler o og:description via JS: `const h=await fetch(location.href).then(r=>r.text());const t=document.createElement('textarea');t.innerHTML=(h.match(/og:description" content="([^"]*)/)||[])[1];t.value`. Daí saem curtidas, data e legenda. Fechar a aba ao final.
- Card do Notion: `notion-fetch` para pegar data/hora de publicação (UTC: 23:00Z = 20h, 21:00Z = 18h, 18:00Z = 15h, 15:00Z = 12h, 12:30Z = 9h30) e o perfil.
- Repetição de pauta: antes de propor tema novo, consultar as PAUTAS já feitas no Notion (data source collection://f0cc9747-efab-822b-8678-07f92372d6b7) e não repetir assunto.
- Dados: todo número precisa de fonte nomeada e específica ("Serasa Experian, 2026"), nunca "imprensa". Pesquisar na web considerando a data atual. Se as fontes divergem, usar a forma conservadora ("mais de 13%") e anotar o cuidado no briefing. Pesquisa antiga: não usar "acaba de".
- Autoridade citada (ex.: especialista, livro): verificar antes; se não verificou, avisar o usuário na entrega.

## 3. Regras de texto (valem para tudo)

- Sem travessão. "Juros" sempre no plural.
- Linguagem de almoço entre empresários; nada de jargão de MBA. Traduzir: ponto de equilíbrio = "quanto você precisa vender para não perder dinheiro"; fluxo de caixa desequilibrado = "o dinheiro some e você não sabe por quê".
- Público 40/50+: evitar gírias e termos modernos como "feeling" (usar "no achismo", "no olho", "sem número").
- Sem frase de efeito/aforismo de fechamento (tipo "X não era destino"). Escrever direto.
- Sem cara de IA: aplicar a skill escrita-sem-cara-de-ia se estiver disponível.
- Vilão sempre externo ou estrutural (juros, cenário, falta de gestão, gurus). Nunca o empresário.
- Política: nunca tomar lado; não usar governo, partido ou candidato como vilão nem protagonista; resultados citados de forma neutra. Foto de político não entra.
- 1 ideia por card; quebra de linha depois de cada frase; linha nunca termina em palavra curta de ligação (de, da, que, e, o, a).
- Narrativa 2027 (desde out/2026): todo post reforça que 2027 tende a ser mais duro, sem citar lado político, e que a Legacy é a aliada para o empresário viver sem medo.
- Não reescrever copy já aprovada pelo usuário sem pedido.

## 4. Capa (Legacy)

Aprendizado de 191 capas analisadas:
- Afirmação com número e cara de notícia nova ("acaba de", "pela primeira vez", "recorde", "2027 vai ser pior"), 16 a 25 palavras somando as linhas.
- NUNCA ponto de interrogação na capa.
- "Você" nunca no começo; se usar, só no fim, depois do fato.
- Medo e alerta funcionam; inspiração, promessa e "como fazer" não.
- Capa de cenário chama todo mundo primeiro (impacto no brasileiro) e só depois vira para o empresário.
- Uma mensagem só: não colocar dois números que se contradizem (ex.: setor caiu x famílias gastaram mais).
- Visual: foto real (marca, fachada, lugar da notícia) + círculo de detalhe com logo/objeto + manchete. Nunca IA evidente, nunca cena encenada.
- Headline em camadas: linha 1 menor de contexto, linha 2 gigante (palavra de choque), linha 3 opcional (pergunta/complemento em dourado no template Canva).

## 5. Estruturas por formato

### LEGACY · Cenário (máx. 7 cards de texto + CTA)
1. Capa: fato do Brasil + ameaça futura (verbo no futuro).
2. O tamanho: dado com autoridade nomeada e fonte.
3. A tradução: o que isso significa na prática.
4. Chega até você: liga o macro a crédito, cliente, margem e caixa do leitor (obrigatória).
5. "Mas repara...": não é só o cenário, é gestão.
6. Contraponto: empresas crescendo no mesmo cenário graças à gestão (com fonte).
7. Conexão: desejo do empresário primeiro, depois "a metodologia da executoria" (a palavra metodologia aparece), mais de 20 mil empresários, "viver sem medo", e fecha com "E o seu primeiro passo para não passar mais um ano à mercê do cenário é agora."
8. CTA: imagem coringa de CTA (Sessão Estratégica).
Opcional: card bônus "Se você faz parte do 1% que chegou até aqui, nós temos um presente para você...".

### LEGACY · Tela dividida
- Capa já em tela dividida.
- Cenário primeiro (cacau caro, juros altos, chegada das chinesas), explicando por que uns afundam e outros crescem.
- 3 cards de pares: empresa que afundou em cima (uma frase com o número), concorrente que cresceu embaixo ("No mesmo cenário"/"Do mesmo setor" + número em negrito).
- Comparar SEMPRE a mesma métrica, no mesmo período e no mesmo cenário (lucro 2T26 x lucro 2T26). Nunca prejuízo de um ano x lucro de outro, nem desconto x volume. Nunca empresa x setor. Não repetir empresa.
- Depois: "Mas repara no que os três pares mostram" (mesmo setor, mesmos juros, a diferença estava dentro), "E na sua empresa, é igual" (de que lado você vai estar?), Conexão e CTA.
- Texto curto, sem cards extras de explicação.
- Modelos no Notion: "Quem quebra x quem cresce" e "Tela dividida: materiais de construção".

### LEGACY · Empresa/notícia
- Precisa de gancho de notícia atual (história antiga sem fato novo não performa).
- Inclui a página "chega até você" para não ficar só sobre a empresa citada.
- Pode ser empresa que quebrou, que não está bem ou que está recalculando a rota.
- Fecha com Conexão e CTA como no cenário.

### CLAILTON · Post estilo X (8 cards)
- Layout de post do X: fundo branco, avatar, Clailton Luiz, @clailtonluiz, selo, contador NN/NN. Poppins preto, fecho de cada card em negrito.
- Se vier de um reel: NÃO transcrever. Manter a ideia central e levar para um ângulo prático do empresário (exemplos novos, perguntas para entrevista, trocas de frase ❌/✅, teste para o leitor). Se reel e carrossel saem no mesmo dia, o gancho pode ser mantido, mas o resto precisa ser diferente.
- Estrutura: 01 capa (headline em caixa-alta + sub terminando em 👉); 02 a 05 desenvolvimento, uma ideia por card; 06 só a frase de impacto; 07 virada/aplicação para o próprio dono; 08 CTA da Legacy ("É isso que a executoria da Legacy faz: entra na empresa ... e executa junto com o empresário." + "Clica no link da bio e agenda uma sessão estratégica gratuita com um especialista Legacy.").
- Tom: conselheiro que já viveu, acolhedor e direto; ganchos contrários ao senso comum funcionam.

## 6. Legendas

### Legacy (enxuta, parágrafos curtos)
1. "Você sabia que..." + o fato viral do post.
2. Pergunta espelho: "E a sua empresa...?"
3. Desenvolvimento curto com o dado e a fonte; "Mas repara:" com o lado de quem está indo bem.
4. "É isso que a executoria da Legacy faz com você: [resultados concretos: aumentar o faturamento, controlar os gastos, aumentar o lucro, previsibilidade de caixa]. Foi assim que mais de 20 mil empresários passaram a viver sem medo."
5. CTA fixo:
   👇 Dá o primeiro passo agora, é gratuito:
   1. Clique no link da bio e agende a sua Sessão Estratégica Gratuita.
   2. Preencha o formulário de aplicação.
   3. Aguarde o contato do nosso time para confirmar o seu horário com um especialista Legacy.
6. Linha final curta, específica do tema (nunca genérica, nunca repetindo a frase da conexão).

### Clailton
1. Pergunta provocativa terminando em 🤔.
2. Frase curta que reposiciona o tema.
3. Blocos curtos de desenvolvimento (paradoxo, nuance, virada).
4. Fecho de maturidade ligando a liderança, negócio e vida.
5. Pergunta reflexiva terminando em 👇.
6. Assinatura fixa: "Se você não segue 👉 @clailtonluiz, provavelmente nunca mais vai me ver. Mas se você já está aqui, parabéns! Você está investindo melhor o seu tempo e blindando a sua empresa todos os dias. 🤝"

### LinkedIn (se pedirem versão)
Abertura direta, listas com →, corte no público de R$ 70 mil/mês, pergunta no fim, hashtags e link com UTM: https://formulario.legacyexecutoria.com.br/?utm_source=organico&utm_medium=linkedin_legacy&utm_campaign=<nome_do_post>

## 7. Modelo do briefing (o que vai no Notion)

```
# 📝 BRIEFING DE CARROSSEL [TWITTER (@clailtonluiz) | (@legacyexecutoria)]

**Base verificada:** (só Legacy: dados com fonte e data)
**Cuidado:** (divergências, neutralidade, o que não repetir)

📌 **DIRECIONAMENTO CRIATIVO:**
(ideia central, de onde veio, ângulo escolhido, por que não é transcrição)

---
🎨 **DESIGN / MOTION:**
(Legacy: capa com foto real + círculo + headline em camadas; problema em fundo #0d0d0d, solução em #080e1c; Bebas Neue nas headlines e Poppins no corpo; azul #1353D5 nos destaques; fonte no rodapé do card; foto real de pessoa em pelo menos 2 cards. Clailton: layout X descrito acima. Sem travessão.)

---
🔍 **REFERÊNCIAS (Apenas base):**
(link original, card-modelo)

---
📐 **DIMENSÕES:**
1080 x 1350 (Carrossel) [Legacy no template Canva: 1080 x 1440]

---
🗓 **ENTREGA:**
DD/MM (dia da semana), HHh

---
✍️ **CONTEÚDO:**
**Card 01/NN (capa)** Headline / Sub
**Card 02/NN** ...

---
💬 **LEGENDA:**
(legenda completa)
```

No Notion: escapar "R$" como "R\$" e "US$" como "US\$" (senão vira fórmula).

## 8. Subir no Notion

1. `notion-update-page` com `replace_content` no card (se der 503, repetir sem allow_async).
2. `update_properties`: PAUTA = headline/título do post; ANDAMENTO = "Revisão"; RESPONSÁVEL = "Mac".
3. Não mexer na data do card; se o horário já passou, avisar.

## 9. Checklist antes de entregar

- [ ] Nenhum travessão em lugar nenhum.
- [ ] Capa: número, 16 a 25 palavras, sem "?", "você" só no fim, uma mensagem só (Legacy).
- [ ] Todo dado com fonte nomeada e verificada; data da pesquisa coerente com "acaba de".
- [ ] Vilão externo; nada de lado político.
- [ ] Máximo de 7 a 8 cards; 1 ideia por card.
- [ ] Tela dividida: mesma métrica, período e cenário em todos os pares.
- [ ] Clailton: não é transcrição do reel; card 06 só com a frase; card 08 com CTA Legacy.
- [ ] Legenda no padrão do perfil, com CTA único.
- [ ] "Juros" no plural; sem "feeling"; sem aforismo de fechamento.
- [ ] Notion: conteúdo + PAUTA + Revisão + Mac.

## 10. Resposta ao usuário

Curta: em que card subiu, data/hora, título, resumo dos cards em 3 a 5 bullets, e qualquer cuidado (dado divergente, autoridade não verificada, horário vencido). Oferecer em uma linha montar no Canva (skill carrossel-canva).