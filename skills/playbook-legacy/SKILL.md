---
name: playbook-legacy
description: Cria e atualiza playbooks (guias passo a passo para o time) no padrão Legacy Executoria, rápido (meta de ~5 minutos por playbook). Sai um arquivo .html único, com a identidade visual do site legacyexecutoria.com.br travada num template. A estrutura é fixa (caminho em N passos, o que é, checklist, passos numerados com capturas e avisos, boas práticas, problemas comuns e glossário) e a escrita é didática, para quem nunca fez o processo. Use sempre que o usuário pedir playbook, manual, guia passo a passo, tutorial, POP, procedimento, "documenta esse processo para o time", "como usar o app/a skill X", onboarding de ferramenta ou de processo, ou quiser atualizar/refazer um playbook existente, mesmo sem dizer a palavra "playbook". Não use para README técnico de código, documento de contexto para IA (.md), carrossel, reels, copy ou legenda.
---

# Playbook Legacy

Um playbook ensina alguém do time a fazer um processo **sozinho, do zero**. O leitor nunca fez aquilo e não é técnico. Por isso cada passo é uma ação concreta, com o que aparece na tela, como saber que deu certo e o que fazer quando der errado.

O visual é o do site da Legacy Executoria e fica **travado** em `assets/template.html`. Você só escreve o conteúdo. O `scripts/montar.mjs` põe o conteúdo no template, embute as capturas e confere tudo. Assim todo playbook sai igual e vira **um arquivo .html que abre sozinho** em qualquer computador, sem internet.

**Meta: pronto em ~5 minutos.** Nos testes, um playbook completo de ~1.900 palavras saiu em 6 a 7 minutos, quase todos gastos pensando e escrevendo o texto. Por isso: uma rodada de leitura, uma escrita, uma montagem, e cada peça no tamanho da tabela de medidas. Não abra o resultado no navegador, não releia o arquivo e não faça conferências extras (grep, rascunho, plano para aprovar). O design já foi testado e o relatório do montar confere estrutura, links, capturas e escrita.

## Fluxo

1. **Leia tudo numa rodada só, em paralelo:** `references/componentes.md` + as fontes do processo (1 a 3 arquivos: `Contexto *.md`, README, `SKILL.md` e `Instruções de uso *.txt` de uma skill, ou o que o usuário colou). Não varra pastas nem código-fonte, e não leia o exemplo nem os scripts da skill. O `componentes.md` basta: tem o esqueleto do arquivo e a forma exata de cada componente, e é a única fonte de marcação (o verificador recusa tag, classe ou atributo fora dele). Se faltar algo essencial, faça **uma** rodada curta de perguntas (até 3). Se o usuário não puder responder, siga com o que as fontes dizem e liste as suposições na entrega.
2. **Escreva o arquivo de uma vez, direto,** em `<pasta>\Playbook <Nome>.html`: só o bloco `playbook-dados` e os capítulos, na ordem fixa, sem CSS nem `<html>`. Decida só a lista de passos e comece a escrever: não componha o texto inteiro de cabeça antes. **Tamanho-alvo: 1.200 a 2.000 palavras** (a capa mostra ~6 a 9 min de leitura). É o que mantém a meta de tempo, porque cada palavra a mais é tempo de escrita. Seja completo no que a pessoa precisa para fazer sozinha e corte o resto: repetição entre capítulos, contexto que ela não usa, exemplos demais. Só um app complexo, com muitas telas, passa de 2.500. O alvo orienta a escrita; não é motivo para refazer. Passar algumas centenas de palavras está ok: não monte de novo só para cortar.
3. **Monte e confira**, com o caminho completo da pasta da skill (a "Base directory" mostrada quando ela carrega; `%USERPROFILE%` não funciona no Bash nem no PowerShell):
   ```
   node "C:\Users\<usuário>\.claude\skills\playbook-legacy\scripts\montar.mjs" "<pasta>\Playbook <Nome>.html" [--capturas "<pasta das capturas>"]
   ```
   O mesmo arquivo vira o playbook completo. No fim sai o relatório: **ERROS** (corrija todos) e **AVISOS** (corrija os que fizerem sentido). Corrija com Edit no próprio arquivo e rode de novo. Normalmente passa de primeira.
4. **Entregue** em 3 a 5 linhas: o caminho do arquivo, quantos passos, as suposições e o que falta confirmar (ex.: "não achei o prazo de reembolso; deixei sem").

**Mapa rápido das fontes** (para não perder tempo decidindo onde cada coisa entra):

| Na fonte | Vira |
|---|---|
| "o que faz", "em uma frase", visão geral | `o-que-e` |
| requisitos, "do que depende", "antes de usar" | `antes` (checklist) |
| "como usar", etapas, fluxo | os passos, na mesma ordem |
| telas e botões | ações e capturas dentro dos passos |
| dicas, cuidados, "não faça" | avisos nos passos ou `boas-praticas` |
| custos e tempos | tabela no passo em que acontecem, ou `custos` |
| instalação em outro computador | pergunta que abre e fecha em `antes`, ou extra "avançado" |
| problemas, erros, "se der errado" | `problemas` |
| siglas e termos técnicos | `glossario` |

Quando a fonte não diz o nome de um botão ou menu, descreva a ação sem inventar o nome (ex.: "nas configurações de conectores do Claude") e siga em frente.

**Onde salvar:** onde o usuário pedir. Sem indicação:
- processo de um app ou projeto com pasta própria: `<pasta do projeto>\Playbook\`;
- skill do Claude: a pasta da skill em `Desktop\Projetos Edições\SKILLS\<skill>\`;
- outros casos: `Desktop\Projetos Edições\PLAYBOOKS\<Nome>\`.

**Atualizar um playbook:** edite o próprio arquivo. Mude o bloco `playbook-dados` (sempre a data em `"atualizado"`) e os capítulos entre `<!-- playbook:secoes:inicio -->` e `<!-- playbook:secoes:fim -->`. Depois rode o `montar.mjs` nele. O design é reaplicado (inclusive melhorias futuras do template) e as capturas continuam. A linha `const SHOTS = {…}` tem as imagens embutidas e é enorme: não leia o arquivo inteiro. Use Grep ou Read com offset para achar o trecho. Um playbook antigo, fora deste padrão, é reescrito no formato novo com o mesmo conteúdo.

**Capturas de tela:** só em processos com tela (app, site, sistema). Salve em JPEG, com 1440 px de largura e nomes como `01-login.jpg`; no texto, a chave é o nome sem o número: `data-shot="login"`. Elas podem ser prints que o usuário mandar ou, em app web local, o `scripts/capturar-telas.mjs`. Veja `references/capturas.md` antes de capturar. Processo sem tela não tem captura: use tabela, árvore de pastas ou exemplos prontos.

## Estrutura fixa

A ordem e os nomes abaixo são sempre os mesmos. O leitor de um playbook já sabe navegar em todos, e isso vale mais que qualquer variação.

| Capítulo (id) | Etiqueta | Título | Conteúdo |
|---|---|---|---|
| `comece` | comece aqui | O caminho em **N passos** | lead + um cartão por passo |
| `o-que-e` | entenda | O que é o/a **Nome** | o que é e para que serve; 2 a 4 cartões (opcional); até 1 aviso |
| `antes` | checklist | Antes de **começar** | checklist do que a pessoa precisa ter (3 a 6 itens) |
| `passo-1`…`passo-N` | passo N | Verbo + **objeto** | 2 a 5 ações numeradas; capturas, tabela e avisos só quando ajudam |
| extras (0 a 3) | extra · outra ferramenta · avançado | livre | assunto que não é um passo do fluxo principal |
| `custos` (opcional) | dinheiro | Quanto **custa** | só se o processo gasta dinheiro ou créditos |
| `boas-praticas` | jeito certo | Boas **práticas** | 3 a 5 cartões curtos |
| `problemas` | socorro | Problemas comuns e como **resolver** | 5 a 8 perguntas e respostas |
| `glossario` | palavras | **Glossário** | 5 a 10 termos |

A palavra em **negrito** é o destaque do título (`<span class="hl">`): exatamente um por título, de 1 a 3 palavras, normalmente o objeto do título. A etiqueta e o título dos capítulos fixos são sempre os da tabela. No `o-que-e`, use "O que são os/as" para nome no plural; se o nome for longo, destaque só a parte principal (ex.: `O que são os <span class="hl">Reels Novela</span>`).

No sumário, os capítulos ficam em três grupos (`data-grupo`, só no primeiro capítulo de cada grupo):
- "Comece aqui": `comece`, `o-que-e` e `antes`.
- O nome do fluxo principal (ex.: "Extrator de perfil" ou "Passo a passo"): os passos e os extras que continuam o fluxo.
- "Mais": qualquer outro extra (etiqueta "outra ferramenta", "avançado" ou "extra"), `custos`, `boas-praticas`, `problemas` e `glossario`.

**Configuração inicial:** o que toda pessoa faz uma vez antes de usar (conectar conta, fazer login no sistema) vira passo com `· só na primeira vez`. O que só alguns precisam (instalar num computador novo quando o do time já está pronto) vira uma pergunta que abre e fecha (`details.faq`) dentro de `antes`, ou um extra "avançado".

**Boas práticas × avisos:** o que vale para um passo só fica no passo, como aviso. As boas práticas são hábitos que valem para o processo inteiro (ex.: "uma coisa por vez", "guarde os arquivos") e podem retomar em uma frase um aviso importante.

**Custos:** o capítulo existe só quando o processo gasta dinheiro que a pessoa acompanha ou paga por uso (ex.: créditos de IA no OpenRouter, anúncio, frete). Consumo normal do plano do Claude (tokens) não conta: se ajudar, vira uma boa prática ("uma conversa por tarefa gasta menos").

### O que pode variar (pouco, e só isto)
- Número de passos: de 3 a 8 (no máximo 10). Mais que isso vira dois playbooks.
- Um complemento na etiqueta do passo: `passo 3 · só na primeira vez`, `passo 5 · quando precisar`.
- De 0 a 3 capítulos extras entre o último passo e `custos`/`boas-praticas`.
- `custos` só existe quando há custo.
- Cartões no `o-que-e` são opcionais.
- Dois caminhos para o mesmo passo: subtítulos "Jeito A: …" e "Jeito B: …" dentro do passo.
- Área da capa e as 2 frases da faixa azul (para quem é e onde acontece).

### O que não pode
- Mexer no template, usar `style=`, criar classes ou componentes, usar emoji, itálico, cor no texto ou imagem por link. O verificador barra tudo isso.
- Mudar a ordem, a etiqueta ou o título dos capítulos fixos.
- Quando o catálogo não cobrir uma necessidade real, faça com o que existe e sugira ao usuário incluir no template. Uma mudança no template vale para todos os playbooks e é decisão dele.

## Como escrever

O leitor está com o processo aberto na outra tela, seguindo linha por linha. Tudo serve para ele não travar.

**Medidas de cada peça** (é o que mantém o tamanho-alvo sem precisar contar palavras):

| Peça | Medida |
|---|---|
| lead de capítulo | 1 frase (no máximo 2) |
| ação de um passo | título + até 2 frases |
| aviso | título + até 2 frases |
| cartão (`o-que-e`, boas práticas) | título + 1 ou 2 frases |
| resposta de problema comum | até 3 frases |
| termo do glossário | 1 frase, até ~15 palavras |
| linha de tabela | até ~20 palavras por célula |

- **Um passo = uma ação.** O passo começa com um título em negrito que é uma frase completa no imperativo, com ponto: `<b>Abra o Google Chrome.</b>`. Depois vêm uma ou duas frases dizendo onde fica, o que aparece e o que esperar.
- **Diga como saber que deu certo.** Ex.: "Quando aparecer `JEV Lab rodando em http://localhost:3777`, o programa está ligado."
- **Use os nomes exatos da tela.** Botão com `<span class="ui">`, escrito como aparece (maiúsculas iguais); o botão principal da ação leva `ui go`. Tecla vai em `<kbd>`, e endereço, comando, nome de arquivo ou pasta em `<code>`. Campo que na tela está em MAIÚSCULAS fica em maiúsculas. `ui` é só para o que se clica ou aparece como interface. O nome de uma parte de uma resposta em texto (ex.: a seção "ROTEIRO FALADO" que o Claude devolve) vai em `<b>`.
- **Pedido ou comando com parte variável:** prefira um exemplo real (`/carrossel-canva LEGACY`). Se precisar mostrar a variável, use colchetes: `<code>/roteirista-reels-clailton [sua ideia]</code>`.
- **Explique o termo técnico na primeira vez,** com um apelido do dia a dia: "o terminal (a janela preta)", "Node.js (é o que faz o programa rodar)". Depois use sempre o mesmo nome.
- **Use números concretos:** tempo, limite, custo, prazo. Use `~` para aproximado e o formato brasileiro (0,03 · 27/09/2026 · US$ 5 · R$ 10,00).
- **Cada aviso tem um propósito,** no máximo 3 por capítulo:
  - `tip` (dica): atalho ou economia;
  - `info` (bom saber): contexto útil;
  - `warn` (atenção): erro comum que atrapalha;
  - `danger` (cuidado): risco sério, como bloqueio de conta, perda de dados, dinheiro ou segurança.

  O título do aviso é a própria regra ("Não feche a janela preta"). O texto diz o porquê e o que fazer.
- **Problemas comuns partem do sintoma, como a pessoa vê.** Ex.: "Digitei localhost:3777 e a página não abre" ou "Apareceu "npm ERR! enoent"". A resposta dá a causa em uma frase e o conserto, com link para o passo certo.
- **Ligue as partes** com link: `veja o <a href="#passo-3">Passo 3</a>`. Diga **a quem pedir ajuda** (cargo ou "quem cuida do X"); nunca deixe a pessoa sem saída.
- **Frases curtas** (até ~25 palavras), voz ativa e "você". Negrito só no essencial. Não use travessão (—): troque por dois-pontos, vírgula ou ponto. Não use "simplesmente", "basta" ou "fácil": para quem está aprendendo, nada é óbvio. Não use emoji; se a fonte tiver um que importa (ex.: 👉 no fim da capa), descreva em palavras.
- **Não invente.** Botão, número, prazo e custo saem das fontes. Sem certeza, deixe de fora ou pergunte.
- **Não coloque segredos.** Senha, token, chave ou valor de `.env` nunca entram no playbook; diga onde pedir.

Antes e depois:
- ✗ `<li>Configure o ambiente e rode o servidor.</li>`
  ✓ `<li><b>Abra o terminal.</b> Menu <span class="ui">Terminal</span> → <span class="ui">New Terminal</span>. Uma área de texto abre na parte de baixo.</li>`
- ✗ Aviso "Observação" com "É importante ter atenção ao login."
  ✓ Aviso `danger` "Use uma conta secundária" com "Automação pode levar a bloqueio. Nunca conecte a conta da empresa."
- ✗ Pergunta "Erro de conexão"
  ✓ Pergunta "A tela diz que o Instagram não está conectado", com a resposta "Faça o <a href="#passo-3">Passo 3</a> de novo…"

O `references/exemplo-jev-lab.html` tem o Playbook do JEV Lab no formato de entrada. É o primeiro playbook aprovado, um app complexo com telas e por isso mais longo que o alvo. No fluxo normal não precisa ler: abra só se o usuário pedir "o mesmo tom do JEV".

## Arquivos da skill

- `assets/template.html`: design travado (identidade do site, sumário, capa, faixa, componentes, impressão e celular). Não edite para um playbook específico.
- `scripts/montar.mjs`: monta, embute as capturas, guarda uma cópia do arquivo anterior em `%TEMP%\playbook-legacy-backups` e confere.
- `scripts/verificar.mjs`: só confere (`node verificar.mjs "<arquivo>"`).
- `scripts/capturar-telas.mjs`: modelo de capturas de app web local (Playwright).
- `references/componentes.md`: esqueleto e catálogo (leitura obrigatória).
- `references/capturas.md`: como fazer as capturas.
- `references/design.md`: a identidade visual e como evoluir o template com segurança.
- `references/exemplo-jev-lab.html`: exemplo completo no formato de entrada.
