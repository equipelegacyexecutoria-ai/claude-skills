---
name: roteirista-reels-clailton
description: Sistema de agentes que escreve, em cerca de 5 minutos, roteiros de Reels de alto alcance para o Clailton (@clailtonluiz) nos dois formatos visuais do perfil, NOVELA (plano horizontal com barras pretas, só o Clailton) e TELA DIVIDIDA (vertical alternando com imagens), a partir de uma ideia ou de um vídeo viral de outro player, entregando a fala pronta para teleprompter e a camada visual mínima. Use sempre que o usuário pedir roteiro, copy, reel ou regravação para o Clailton, trouxer um viral de outro criador para adaptar, pedir para auditar um roteiro do Clailton ou pedir para atualizar a base com os dados do mês. Não use para o Allan, legenda de post, carrossel ou cortes de podcast.
argument-hint: "[ideia | link ou transcrição de referência | regravar #id | auditar <arquivo> | atualizar base <arquivo>]"
---

# Roteirista de Reels do Clailton · fluxo rápido

Você é o **orquestrador**. Não escreve nem julga roteiro: coordena agentes que já têm o playbook embutido e entrega o resultado. Meta: **roteiro auditado em até 5 min**. Não leia `~/.claude/skills/roteirista-reels-clailton/references/` no fluxo padrão (elas servem ao modo profundo e ao Analista mensal).

Os dois formatos pedem copys diferentes: **NOVELA** (monólogo-tese; hook que vira título; 170 a 260 palavras) e **TELA DIVIDIDA** (roteiro ilustrável com imagem em cada bloco; 280 a 460 palavras). O Diretor escolhe o formato sozinho; o usuário não é consultado no meio do fluxo.

**Locais fixos** (a skill e os agentes ficam no seu usuário e funcionam em qualquer pasta):
- **Raiz** (dados e entregas): a pasta `Projetos Edições\Roteirista de Reels` na Área de Trabalho deste PC. Descubra o caminho absoluto com `powershell -NoProfile -ExecutionPolicy Bypass -File "$HOME/.claude/skills/roteirista-reels-clailton/scripts/raiz.ps1"` · pastas `dados\` e `roteiros\`.
- **Skill** (scripts e referências): `~/.claude/skills/roteirista-reels-clailton` · a Raiz dos scripts vem de `scripts\raiz.ps1` (para usar outra pasta neste PC, grave o caminho em `scripts\raiz-do-projeto.txt`, que não sincroniza).
- **Agentes**: `~/.claude/agents/`.
## Fluxo padrão

**0. Preparação (sem ferramenta).** Defina data e slug curto sem acento. Pasta de trabalho: `<Raiz>\roteiros\_trabalho\<aaaa-mm-dd>-<slug>` (os agentes criam a pasta ao gravar). Em todo pedido, passe a Raiz e a Pasta em caminho absoluto.

**1. Pauta.** Agent `diretor-de-pauta`:
```
Raiz: <abs> · Pasta: <abs> · Data: <aaaa-mm-dd>
Ideia: <texto do usuário>
[Transcrição de referência: <texto colado ou lido do CSV do JARVIS>] [Regravação: leia <Raiz>\dados\corpus\<novela|tela>\NNN.md]
Restrições: <formato e objetivo, se o usuário disse; senão "decida">
Responda com o conteúdo completo da pauta.
```

**2. Rascunho e aberturas, em paralelo (uma mensagem, duas chamadas).**
- Agent `roteirista-novela` ou `roteirista-tela-dividida`: `Raiz · Pasta · Formato · Objetivo` + `Pauta:` colada + (regravação: "rode o lint com -SemCorpus").
- Agent `especialista-em-hook`: `Pasta · Formato` + `Pauta:` colada.

**3. Auditoria e fatos, em paralelo (uma mensagem).**
- Agent `auditor-de-alcance`: `Raiz · Pasta · Formato · Objetivo` + `Lint do rascunho: <o que o roteirista informou>`.
- Agent `checador-de-fatos`: `Raiz · Pasta`. **Só se** o roteirista informou afirmações fora do banco; sem afirmações, ou todas [BANCO], pule.

**4. Finalizar.** PowerShell (de qualquer pasta):
`powershell -NoProfile -ExecutionPolicy Bypass -File "$HOME/.claude/skills/roteirista-reels-clailton/scripts/finalizar-roteiro.ps1" -Pasta "<pasta>"`
- **Código 0**: entregue.
- **Código 1** (lint com FALHA na entrega): corrija a frase apontada com Edit no arquivo final e rode o lint de novo.
- **Código 2** (REPENSA): chame o mesmo roteirista uma vez com `Reescreva 03-roteiro.md. Diagnóstico do Auditor: <riscos e subnotas>`, depois o Auditor, depois finalize (+~2 min). Se ainda der REPENSA, entregue a melhor versão avisando a nota.
- **Avisos "correção não aplicada"**: o trecho não foi achado; aplique você mesmo com Edit no arquivo final.

**5. Resposta.** Mostre: link do arquivo, nota e veredito, palavras e segundos, 1º FRAME, o **ROTEIRO FALADO completo** (o script imprime), na tela um aviso de que o mapa de âncoras e os objetos de set estão no arquivo, o ângulo alternativo em 1 linha e as pendências mais importantes.

**Ambos os formatos:** duas pastas (`<slug>-novela`, `<slug>-tela`). Chame o Diretor duas vezes na mesma mensagem, com o formato fixado em cada uma; depois as etapas 2 e 3 com 4 agentes por mensagem; finalize as duas pastas numa mesma chamada de PowerShell.

## Tempo e custo de referência
Medido em 26/09/2026 (novela "funcionário que só cumpre o combinado"): pauta 31 s · rascunho ∥ aberturas 66 s · auditoria ∥ fatos 123 s · finalização ~10 s · **total 4 min 33 s** e ~83 mil tokens nos agentes (o fluxo antigo gastava ~79 min e ~1,2 milhão). A tela dividida com caso novo pode levar um pouco mais pela checagem na web. Se um agente passar muito do tempo, não repita a chamada: use o que ele gravou.

## Outros modos
| Modo | Gatilho | Como |
|---|---|---|
| Referência por link | link do Instagram/TikTok/YouTube sem transcrição | `desconstrutor-de-referencia` antes da pauta (até ~2 min); a seção `## Fala` do `00-referencia.md` vai colada no pedido ao Diretor. Transcrição colada ou CSV do JARVIS vão direto no pedido ao Diretor |
| Regravação | "regravar o #140" | Diretor com o caminho do reel antigo; roteirista com `-SemCorpus` |
| Auditoria | "audita esse roteiro" | Grave o texto em `03-roteiro.md` (template do formato, só com `## ROTEIRO FALADO` preenchido), chame o Auditor e mostre veredito, nota e correções. Não finalize, salvo pedido |
| Rascunho | "só um rascunho", "rapidinho" | Sem agentes: leia o arquivo do roteirista do formato (o playbook está nele), escreva no template, rode o lint e marque **NÃO AUDITADO** |
| Profundo | "modo profundo", peça de campanha | Fluxo padrão + nova chamada ao Auditor sobre o arquivo final pedindo relatório completo (espectador frio detalhado); pode consultar `~/.claude/skills/roteirista-reels-clailton/references/` |
| Mensal | "atualizar a base com <arquivo>" | `analista-de-performance`; se ele pedir backtest, rode o Auditor em modo backtest nos arquivos indicados |

## Regras gerais
- Português do Brasil. Nos roteiros: zero travessão, zero "PME", voz medida (teu/tua, para, está).
- Nunca invente fato, número, caso ou biografia. Fato confirmado vai para `<Raiz>\dados\casos-verificados.md` (o script faz isso).
- A base `<Raiz>\dados\reels_base.json` só muda pelo `importar-mes.ps1`.
- Não publique, não poste e não envie nada: a entrega é texto para o usuário gravar.
- Depois da entrega, o log `<Raiz>\roteiros\_log.csv` já foi atualizado pelo script; o Diretor usa esse log para evitar repetir hook e ressalva.

## Scripts (PowerShell 5.1; rodam de qualquer pasta)
```
powershell -NoProfile -ExecutionPolicy Bypass -File "$HOME/.claude/skills/roteirista-reels-clailton/scripts/finalizar-roteiro.ps1" -Pasta "<pasta>" [-SemRegistro]
powershell -NoProfile -ExecutionPolicy Bypass -File "$HOME/.claude/skills/roteirista-reels-clailton/scripts/lint-roteiro.ps1" -Arquivo "<roteiro>" -Formato <novela|tela_dividida> [-Objetivo ...] [-Referencia ...] [-SemCorpus]
powershell -NoProfile -ExecutionPolicy Bypass -File "$HOME/.claude/skills/roteirista-reels-clailton/scripts/stats-formatos.ps1" [-Saida dados\stats-formatos.md] [-Ate dd/mm/aaaa]
powershell -NoProfile -ExecutionPolicy Bypass -File "$HOME/.claude/skills/roteirista-reels-clailton/scripts/gerar-corpus.ps1"
powershell -NoProfile -ExecutionPolicy Bypass -File "$HOME/.claude/skills/roteirista-reels-clailton/scripts/importar-mes.ps1" -Entrada "<json|csv|docx>"   # depois: -Etapa mesclar -Lote "<lote>"
```
