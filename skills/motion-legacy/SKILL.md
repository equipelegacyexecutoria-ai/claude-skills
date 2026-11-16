---
name: motion-legacy
description: Faz motion no estilo "Motion Legacy Plan" (aprovado pelo usuário em 12/11/2026) — Reels 9:16 com fundo claro e detalhes azuis, letreiro palavra a palavra no tempo da narração (marca azul atrás da palavra-chave, palavra gigante borrada lá atrás), cartões de vidro e telas da plataforma em 3D, câmera parada que só anda com intenção (viaja de uma cena à outra pela linha azul com a setinha na frente e aproxima no ponto-chave), takes reais dos executores em cartões, narração feminina e duas trilhas (tensa na dor, pra frente na solução) com poucos efeitos baixos. Use sempre que o usuário pedir "motion no estilo do Legacy Plan", "igual ao motion do Legacy Plan", "motion legacy", "SKILL MOTION LEGACY", "motion fundo branco com azul", "motion com letreiro e plataforma 3D", ou um motion novo para a Legacy (Legacy Plan, Executoria, consultoria, produto) que deva seguir esse modelo. Para outros estilos de motion use a skill motion-designer; para fala do Clailton ilustrada use motion-dinamico.
---

# Motion Legacy (estilo do Motion Legacy Plan)

Modelo aprovado no card "Motion Legacy Plan: copy + referências (perfil Legacy)" depois de 8 versões (11 e 12/11/2026).
Vídeo de referência: `exemplo/legacy-plan-v8.html` (o projeto inteiro, 73,6 s) e os quadros em `references/`.
O que ele reprovou e aprovou em cada versão está em `references/licoes.md`: **leia antes de montar.**

O usuário não é técnico: fale pelo resultado ("a câmera desce até as planilhas", "a música vira quando ela termina a
pergunta"), nunca por código. Base de ferramentas e regras gerais (área segura, créditos, Artlist): skill `motion-designer`.

## A gramática do estilo (não mude sem o usuário pedir)

| Elemento | Como é |
| --- | --- |
| Formato | 1080x1920, 30 fps, Reels do perfil Legacy. Área segura do CLAUDE.md global (topo 250, base 1500, margens 70/55, botões a partir de x 887 entre y 1110 e 1500) |
| Fundo | claro (`#f3f6fb`), degradê radial branco, duas manchas azul-claro desfocadas que andam devagar e grade de pontos azuis que sobe. **Sem chão, sem cenário virtual** (reprovado na v3) |
| Cores | navy `#0a1a33` (texto), azul `#2f7bff`, azul claro `#5aa9ff`/`#7cc4ff`, cinza `#7c8ba3`; laranja `#f97316`/`#f59e0b` só para "problema/incêndio"; verde `#10b981` para "feito" |
| Fonte | Urbanist (a mesma da plataforma Legacy Plan), em `molde/assets/fonts` |
| Letreiro | frase entra palavra a palavra **no tempo exato da voz**: cada palavra nasce desfocada, maior e deslocada; palavra-chave com marca azul que cresce atrás (`hl`), a palavra em destaque aparece gigante e borrada ao fundo (profundidade); a frase gira um pouco em 3D ao chegar e é "atravessada" pela câmera na saída. Tamanhos `sm`, normal, `big`, `xl`; `dim` cinza; `rs` risca a palavra. Referência: reel de lettering (`references/ref_letreiro.jpg`) |
| Cartões | "vidro claro" (`.vidro`): branco translúcido, borda branca, sombra azulada grande; rótulo em caixa-alta espaçada; números que contam (`contar`) |
| Plataforma | telas do Legacy Plan **remontadas em HTML** (barra lateral escura `#111c22`, topo branco, cards, KPIs, barras planejado x realizado, metas com responsável), inclinadas em 3D como no site da Contra (`references/ref_plataforma.jpg`). Nunca print com dado de cliente; números fictícios coerentes |
| Câmera | **parada**; só anda com intenção: `viagem` (a linha azul nasce na cena atual, a setinha corre por ela e a câmera vai junto, recuando e desfocando no meio do caminho), `chega` (aproxima no ponto-chave e volta devagar), `salto` (troca escondida atrás do azul ou de uma passagem). Nada de balanço contínuo (reprovado na v3) |
| Takes reais | executores da Legacy de `APRESENTAÇÃO COMERCIAL/TAKES/TAKES EXECUTORES v2.mp4` (Drive), recortados e mostrados em cartões com cantos redondos, cortes rápidos de 0,5 s. Take só se casar com a frase (na v6 um take "nada a ver" virou a barra "Seu tempo") |
| Narração | voz feminina **Lívia Moreira** (Magnific `audio_tts`, voz id 611). Gasta créditos: pedir o "sim" antes, com o custo (`simulate_cost`), uma tomada por vez. Sem Adobe Podcast (voz de IA já limpa) |
| Música | duas trilhas da pasta `~/Music/Spotclai`: tensa na dor (aprovada: "SoLaTiDo - Suspenseful and Tense Orchestra", em Tensão - Mistério) e pra frente na virada para a solução ("Cinematic Pulse - 8teen Smokes", em Energia - Confiança). A virada da trilha tensa cai no fim da 1ª pergunta do gancho; a troca de trilha cai na frase "Na Legacy é diferente". Trilhas abaixo da voz sem sumir |
| Efeitos | poucos (10 em 73 s) e baixos (volume 0,07 a 0,22): whoosh na viagem, clique de interface, impacto no "incêndio", gaveta, subida tonal na virada, clique de dado, logo. Arquivos em `molde/assets/audio/sfx` (Artlist + 2 sintetizados) |
| Fecho | CTA com chip "link na bio", botão que é clicado pelo cursor e vira "✓ Sessão agendada", logo Legacy Executoria e a assinatura "Enquanto todo mundo ensina, a gente executa." com marca azul em "executa." |

## Processo

1. **Copy**: o usuário costuma mandar ou ajustar a copy num Claude Docs. Se for pedir a copy: gancho com pergunta,
   dor concreta (planilhas, ninguém sabe quem faz, vira incêndio), virada "Na Legacy é diferente", como funciona
   (executor assume, metas com responsável, plano de ação com prazo), plataforma (números em um lugar só), benefício,
   garantia, CTA "Clique no link da bio e agende sua sessão". Sem travessão e sem "não é X, é Y" (skill
   `escrita-sem-cara-de-ia`). O vídeo **não vende o Legacy Plan como produto**: ele mostra como a Legacy executa.
2. **Projeto**: `python ~/.claude/skills/motion-legacy/scripts/novo_projeto.py "<pasta>/projeto" <duração_s>`.
   O `index.html` do molde já tem fundo, estilos, letreiro (`grupo`), cartões (`mostra`, `some`, `contar`),
   câmera (`viagem`, `chega`, `salto`) e 3 cenas de exemplo para trocar.
3. **Narração**: gerar a voz (com autorização de crédito), salvar em `<pasta>/audio/voz.mp3` e rodar
   `python ~/.claude/skills/motion-legacy/scripts/palavras_js.py <pasta>/audio/voz.mp3 --inicio 0.25 --projeto <pasta>/projeto`.
   Confira a lista impressa: o Whisper às vezes junta palavras no mesmo tempo; corrija o `.tx.json` e rode com `--so-projeto`.
4. **Cenas**: uma cena por ideia da copy, cada uma num ponto do mundo (`P` no bloco da câmera, cenas a ~1700 px na
   horizontal e ~2300 px na vertical uma da outra). Use o `exemplo/legacy-plan-v8-cenas.js` como cardápio pronto:
   três planilhas (.xls), caixa/vendas/metas com "?", tarefa sem dono com alertas e fogo, documento de 80 páginas
   que vai para a gaveta, takes dos executores, financeiro e comercial, metas com responsável, plano de ação com
   prazo e alerta, DRE planejou/faturou/sobrou, barra "Seu tempo", selo de garantia que vira, CTA com botão.
   Letreiro sempre no tempo da palavra (`TT[i]`); cada cena entra com `mostra` em 3D (z/rotationX/blur) e sai com `some`.
5. **Câmera**: chamadas em ordem de tempo (`viagem` muda a cena atual na hora da chamada). Uma viagem por troca de
   assunto, um `chega` por frase de impacto. Troca grande de clima (dor → solução): `salto` atrás do azul.
6. **Áudio**: `mix_audio.py` da skill `motion-designer` com um JSON igual ao `exemplo/mix_v8.json` (voz em 0,25 s,
   trilha tensa até a virada, trilha da solução até o fim, efeitos posicionados pelo pico). Meça a trilha antes
   (`librosa`, energia a cada 0,25 s): se ela cresce muito no meio, nivele, senão encobre a voz (v6: "incêndio"
   sumia). Para a virada cair numa palavra: `inicio_no_arquivo = tempo_da_virada_na_musica - tempo_da_palavra_no_video`.
7. **Conferir antes de mostrar** (skill `motion-designer`, item 8): `npx --yes hyperframes@0.8.162 lint`,
   `snapshot --no-end -o qa/<v> --at ...` nos momentos de cada cena, `area_segura.py`, transcrever a mixagem
   (a voz tem que sair igual à copy), render `npx --yes hyperframes@0.8.162 render --quality high --fps 30 -o renders/<nome>_vN.mp4`
   e folha de quadros do MP4.
8. **Entrega**: Sala de Revisão (skill `sala-de-revisao`). A Sala costuma estar cheia: prévia leve 540p em duas
   passadas, ~320k de vídeo e 56k de áudio mono (~3,5 MB para 74 s). Drive EDITADO e card do Notion só quando pedirem.

## Armadilhas já resolvidas

- **GSAP x/y no contêiner da cena** (`#s2` etc.) apaga o `translate` que põe a cena no ponto do mundo: a cena some.
  Anime só os filhos (ex.: tremer a gaveta = tremer `#gav-fundo`, `#gav-frente`, `#pilha`).
- Elemento que já saiu e reaparece pendurado: esconda no fim (`tl.to(el, {autoAlpha: 0, duration: 0.1}, t)`).
- Trocar a narração com cenas prontas: em vez de refazer tempos à mão, mapear tempo antigo → novo por palavras
  iguais (no exemplo: `bloco(mapaF, mapaG)`, `M(x)`, `par(a0, a1, b0)`).
- Trocar só a música: refaça a mixagem e troque o áudio do MP4 já renderizado (`ffmpeg -c:v copy`), sem renderizar de novo
  (o render leva ~13 min). Mudou só um trecho visual: renderize e confira esse trecho antes do vídeo inteiro.
- Variações de um trecho (ex.: 3 jeitos de ilustrar uma frase): mostre os quadros lado a lado numa imagem e só
  renderize o vídeo depois da escolha.

## CTA final dos reels NV_CTA do Clailton (aprovada em 16/11/2026)

A CTA em motion no fim das novelas NV_CTA agora é neste estilo (Igor aprovou o Metas e mandou aplicar nos outros).
Voz é a do próprio Clailton (sem Lívia, sem crédito). Scripts em `scripts/cta_nv/` (no PC de render rodam de `C:\Render\_trabalho\_cta_legacy`):
- `gerar.py <slug> [--render]`: SPEC por vídeo com os grupos do letreiro (índices de `palavras_corte.json`), a cena do tema
  (`metas` painel batendo 100%, `caixa` linhas de vendas/lucro/ticket subindo, `crescer` faturamento e barras dos meses),
  palavra da viagem (fecho), do clique e, se a fala depois do clique for longa, a palavra em que entra o logo.
  Fecho: chip "link na bio", botão clicado vira "✓ Vamos juntos", logo Legacy Executoria e "Enquanto todo mundo ensina, a gente executa."
- `compor.py <slug>`: flash branco na passagem, animação por cima da novela (`sem_motion.mp4` ou `v1_sem_musica.mp4`), voz + 5 efeitos baixos.
- Música: `mixar_alto.py <cta_legacy/composto_sem_musica.mov> <musica> <saida> <ini> 10 cta <inicio_cta>`.
- Drive: sobrescrever o EDITADO no mesmo nome (link do card não muda).
