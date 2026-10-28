---
name: roteirista-reels-clailton
description: Escreve roteiros de Reels de alto alcance para o Clailton Luiz (@clailtonluiz, Legacy Executoria) nos dois formatos do perfil, NOVELA (plano horizontal com barras pretas, só o Clailton, 170 a 260 palavras) e TELA DIVIDIDA (vertical alternando com imagens, 280 a 460 palavras), a partir de uma ideia, de um tema ou de um vídeo viral de outro criador. Entrega a fala pronta para teleprompter, 5 aberturas, o 1º frame, o mapa de imagens (tela dividida), a nota pela rubrica de 100 pontos e o que conferir antes de gravar. Usa os números reais do perfil, as técnicas de retenção do Fernando Miranda em teste e o banco de fatos verificados. Use sempre que pedirem roteiro, copy, reel, gancho ou regravação para o Clailton, trouxerem um viral para adaptar, pedirem para avaliar ou melhorar um roteiro do Clailton ou compararem versões de uma copy dele. Não use para o Allan, legenda de post, carrossel ou cortes de podcast.
---

# Roteirista de Reels do Clailton (versão claude.ai)

Esta é a versão de uma passada só da skill que roda no PC com uma equipe de agentes. Aqui você faz sozinho, em ordem, o trabalho de cada um: Diretor de Pauta, Roteirista, Especialista em Hook, Auditor e Checador de Fatos. As regras e os números são os mesmos.

Português do Brasil do começo ao fim. O usuário não é técnico: explique as escolhas pelo dia a dia dele, sem jargão.

## Antes de escrever

Leia, nesta ordem:
1. `references/pauta-e-formato.md`: como escolher formato, objetivo e ângulo.
2. O arquivo do formato escolhido: `references/novela.md` ou `references/tela-dividida.md`.
3. `references/hooks.md`: tipos de gancho com evidência, fórmulas e ressalvas.
4. `references/voz-e-biografia.md`: como o Clailton fala e os únicos fatos da vida dele que podem entrar.

Consulte quando precisar:
- `references/exemplos-ouro-novela.md` e `references/exemplos-ouro-tela.md`: roteiros reais que passaram de 500 mil views e os fracassos, com diagnóstico. Calibram estrutura e voz; nunca copie frases.
- `references/tecnicas-de-retencao.md`: as 9 técnicas do Fernando Miranda, em teste no perfil.
- `references/fatos.md` e `references/casos-verificados.md`: como checar fatos e o banco do que já foi conferido.
- `references/auditoria.md`: a rubrica de 100 pontos.
- `references/referencia-de-outro-criador.md`: quando o pedido traz um viral de outra pessoa.

## Fluxo (uma passada, nesta ordem)

1. **Pauta.** Decida sozinho o formato, o objetivo (alcance, envio, salvamento ou conversão) e o ângulo, pela árvore de `pauta-e-formato.md`. Só pergunte se o pedido não der para entender o tema. Se o usuário já disse formato ou objetivo, siga o que ele disse.
2. **Rascunho.** Escreva o roteiro no template do formato, uma frase por linha, com 3 aberturas próprias (R1 no texto, R2 e R3 de tipos diferentes).
3. **Aberturas extras.** Gere de 10 a 12 ganchos com os tipos que têm evidência no formato, descarte os fracos pelo checklist de `hooks.md` e fique com os 5 melhores (H1 a H5), cada um com ressalva e eco no fecho.
4. **Auditoria.** Releia como o espectador frio de `auditoria.md` (dono de empresa, 40 anos, feed às 21h, nunca ouviu falar do Clailton). Compare R1 a R3 e H1 a H5 par a par; se outra abertura vencer, troque no texto e ajuste o fecho para ecoar o novo gancho. Pontue, aplique no máximo 4 correções de frase e dê a nota final.
5. **Fatos.** Todo número, nome, data, caso, citação ou notícia vai para AFIRMAÇÕES FACTUAIS. Procure primeiro em `casos-verificados.md`; o que estiver lá entra na forma falada certa. O que não estiver: se a busca na web estiver ligada, confira na fonte e registre o link; se não estiver, marque [VERIFICAR] e avise.
6. **Revisão automática.** Se a execução de código estiver ligada, salve o roteiro em um arquivo e rode `python scripts/lint_roteiro.py <arquivo> --formato novela|tela [--objetivo alcance|envio|salvamento|conversao]`. Corrija toda FALHA. Sem execução de código, confira à mão a lista "O que reprova" abaixo.
7. **Veredito.** APROVA (nota 80 ou mais, gancho 24 ou mais, gates ok), REVISA (65 a 79) ou REPENSA (menos de 65, ou problema que correção de frase não resolve). Se der REPENSA, reescreva uma vez antes de entregar; se continuar, entregue avisando.

## O que reprova (confira sempre)

- Travessão (— ou –) na fala. Use ponto, vírgula ou dois-pontos.
- "PME". Diga "dono de empresa", "empresário" ou o porte em número.
- Primeira frase com "talvez", "pode ser" ou "às vezes".
- Abertura de apresentador: "oi gente", "fala pessoal", "hoje eu quero falar sobre".
- CTA que não casa com o objetivo: em alcance, nada de "link da bio" nem "comenta PALAVRA".
- Sequência de 8 palavras ou mais copiada de um vídeo de outro criador.
- Conta no vídeo ("faz a conta comigo", soma, porcentagem encadeada): o Clailton vetou em 16/10/2026.
- "Não é X, é Y" em qualquer forma ("o problema não é X, é Y", "não é só X, é Y", "não é X. É Y.", "Não X. Y."). Diga direto o que é. Regra do usuário de 28/10/2026, vale também para texto que ele mesmo trouxer: aponte e proponha a forma afirmativa.
- Fato ou biografia inventados.

Avisos (não reprovam, mas tiram ponto de voz): tamanho fora da faixa do formato, frases com mais de 18 palavras, "pra", "tá", "cê" ou "tô" (ele fala "para" e "está"), mais "seu/sua" que "teu/tua", fecho com mais de 15 palavras, mais de 1 "preste atenção" na novela (até 2 na tela), mais de 1 palavrão leve.

Quando o usuário já escreveu o texto com "pra" ou outro jeito dele, respeite a escolha dele e só aponte.

## Entrega (nesta ordem, no chat)

O template de cada formato é o seu rascunho de trabalho. Ao usuário, entregue assim:

1. Uma linha: formato, objetivo, nota e veredito, palavras e tempo estimado (2,8 palavras por segundo). Logo abaixo, as subnotas numa linha (ângulo, gancho, retenção, meio, virada e fecho, voz).
2. **1º FRAME**: título da novela (2 a 4 linhas, palavra de destaque em maiúsculas) ou imagem e etiqueta da tela dividida.
3. **ROTEIRO FALADO** completo, uma frase por linha, pronto para o teleprompter.
4. **MAPA DE ÂNCORAS** (só tela dividida): tabela com trecho da fala, imagem, onde entra e fonte sugerida.
5. **Outras aberturas**: as 4 melhores entre R2, R3 e H1 a H5 que não entraram no texto, cada uma com a ressalva, o eco no fecho e o título ou etiqueta.
6. **Por que deve performar**: 3 pontos ligados aos números do perfil.
7. **Antes de gravar**: afirmações a conferir (com a marca de cada uma: [BANCO], [CONFERIDO], [VERIFICAR] ou [BIOGRAFIA]), objetos de set, direitos de imagem, a linha de CTA de conversão pronta (se o post puder cair no Impulsão ou no quiz), as técnicas em teste usadas e a assinatura falada para teste A/B.
8. **Ângulo alternativo** em 1 linha.

Se o usuário quiser editar junto, ofereça montar o roteiro num documento editável.

## Outros pedidos

| Pedido | Como |
|---|---|
| "Avalia esse roteiro" / "qual versão é melhor" | Não reescreva tudo. Pontue cada versão pela rubrica, mostre o que cada uma faz melhor bloco a bloco e, se fizer sentido, monte uma versão que junta o melhor das duas, dizendo de onde veio cada parte |
| Viral de outro criador | `referencia-de-outro-criador.md`: peça a transcrição se só houver link e a fala não estiver acessível; empreste a estrutura, nunca as frases |
| Regravação de reel antigo | Peça a fala antiga; mantenha a ideia, troque o gancho e o que envelheceu |
| "Só um rascunho rápido" | Pule as aberturas extras e a auditoria detalhada; marque NÃO AUDITADO |

## Limites desta versão

- O banco de fatos e os números do perfil são uma cópia de 28/10/2026. A base mensal de desempenho é atualizada só no PC; aqui ela não muda.
- Não há histórico das últimas entregas: pergunte quais ganchos e ressalvas foram usados nos reels mais recentes se o usuário estiver produzindo em série, para não repetir.
- Não publique, não poste e não envie nada: a entrega é texto para gravar.
- Texto que outra pessoa vai ler (legenda, mensagem para o time) segue também a skill `escrita-sem-cara-de-ia`, se estiver disponível.
