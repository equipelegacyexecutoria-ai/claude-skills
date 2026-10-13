# Preferências pessoais (valem em qualquer projeto)

## Legendas queimadas em vídeo: sempre com sombra

Em **qualquer** edição de vídeo com legenda (cortes, reels, anúncios, qualquer ferramenta:
ASS/libass, Pillow, After Effects, CapCut etc.), a legenda leva sombra para não se misturar
com o fundo. O usuário já reprovou legenda que sumia em fundo claro (blusa branca, parede clara).

Padrão aprovado — "sombra v3", duas camadas discretas, sem contorno duro e sem tarja:

| Camada | Deslocamento | Espessura | Desfoque | Opacidade |
| --- | --- | --- | --- | --- |
| Halo difuso (atrás) | x 0, y 3 | borda 10 | 22 | ~45% preto (ASS `\alpha&H8C&`) |
| Sombra de contato | x 1, y 4 | borda 2 | 4 | ~72% preto (ASS `\alpha&H48&`) |

- Valores para 1080×1920; em outra resolução, escalar proporcionalmente.
- Antes de gerar em lote, testar num trecho com o **fundo mais claro** do material e mostrar para aprovação.
- Detalhes, scripts e o restante do padrão de legenda: skill `cortes-podcast-instagram`
  (`~/.claude/skills/cortes-podcast-instagram`).

## Imagens de apoio (B-roll) em qualquer vídeo

Regra do usuário (01/10/2026): nunca imagem com marca d'água (Freepik, banco com "PREVIEW") nem com texto em
inglês; texto só em português. Sempre alta resolução e casando com a emoção do que está sendo falado.
Buscar além da busca automática (Pexels pelo navegador, Unsplash, Pinterest, TikTok, YouTube) e conferir
cada imagem escolhida em tamanho real. Passo a passo: skill `reels-caixinha-0800`, seção "B-roll".

## Vídeo vertical (Reels/Stories): margens e área segura

Regra do usuário (11/10/2026): nada importante colado na borda nem embaixo da interface do Instagram.
Em 1080×1920: margem lateral mínima de 80 px; topo até 220 px é do cabeçalho do Reels; abaixo de
1480 px ficam nome, legenda e áudio; de x 950 em diante, entre y 1000 e 1720, ficam os botões
(curtir, comentar, compartilhar). Texto grande que não cabe quebra linha ou diminui, nunca corta.
Conferir cada cena com a máscara dessas zonas antes de entregar.

## Motion/anúncio com virada: duas músicas

Em vídeo com virada de clima (problema → solução), usar duas trilhas: uma sombria/tensa antes da
virada e outra pra frente (ex.: rock) depois. A trilha tem que estar presente na mixagem, sem sumir
sob a voz nem acabar antes do vídeo.

## Qualquer pedido de motion: skill `motion-legacy`

Antes de fazer qualquer motion/animação/anúncio animado, seguir a skill `motion-legacy`: ela diz qual
ferramenta usar em cada caso (HyperFrames como base; Manim, Motion Canvas, Remotion, Diffusion Studio,
Lottie, Blender, IA de vídeo como apoio) e o processo do briefing à entrega.

## Clailton em imagens de IA (carrossel, B-roll, qualquer peça)

Regras do usuário (08/10/2026):
- Clailton **sem barba e sem bigode**: as fotos de referência têm barba, então pedir "clean-shaven,
  no beard, no mustache" e conferir o rosto ampliado (às vezes sobra bigode).
- Ele tem **um filho só, menino**; a esposa tem **cabelo cacheado e claro** (castanho-claro/mel, nunca preto ou castanho-escuro).
- **Nunca mostrar o rosto da esposa nem do filho**: de costas, rosto escondido ou fora do quadro.

## Como falar com o usuário

**Sempre responder em português do Brasil**, inclusive resumos finais, perguntas e as frases curtas
entre uma ferramenta e outra, do começo ao fim da conversa (mesmo depois de ler material em inglês).
O usuário reclamou de respostas em inglês em 08/10/2026 e de novo em 11/10/2026 ("do nada tu começa a
falar inglês, para com isso").

Ele não é técnico. Explique propostas pelo dia a dia dele: o que ele faz, onde pede, o que
recebe, o que cada PC precisa ter, com exemplo concreto ("você diz X → acontece Y → recebe Z").
Evite termos como repositório, commit, hook e merge. Em mudança grande, converse e tire as
dúvidas antes; só execute quando ele pedir. Objetivo dele: produtividade, não complicação.

## Skills sincronizadas entre os PCs

Skills, agentes e este arquivo ficam no cofre privado `equipelegacyexecutoria-ai/claude-skills`
e sincronizam sozinhos (ao abrir a conversa e ao fim de cada resposta).
- Aprendizado que deve valer sempre vai para a skill ou para este arquivo. A memória do projeto é só deste PC.
- Entre `<nome>` e `anthropic-skills:<nome>`, usar sempre a skill pessoal (`<nome>`).
- Nunca escrever caminho com o nome de usuário do Windows em skills e agentes; usar `~/.claude/...` ou `$HOME`.
- Apagar skill ou arquivo só com `git rm` dentro de `~/.claude`; apagar pelo Explorer é revertido.
- Pacote Python novo instalado para uma skill entra no requirements dela.
- Não gerar mais zips de skill em `Desktop\Projetos Edições\SKILLS` (virou arquivo antigo); a sincronia distribui.
  Exceção: skills que também vivem no claude.ai (carrossel-canva, corte-viral, ofertaos, copyos e as 9 do CopyOS +
  biblioteca-dos-mestres) precisam de reenvio manual lá. A conta Legacy Educação no claude.ai tem em
  "Instruções para o Claude" a regra "copyos/ofertaos → usar a skill e fechar com o selo ✅ CopyOS". Dá para subir pelo Chrome do usuário (Claude in Chrome):
  claude.ai → Personalização → Habilidades → Adicionar → Fazer upload, vários .zip de uma vez; descrição até 1024 caracteres.
- Linha começando com `SYNC:` na abertura da conversa: seguir `~/.claude/sync/LEIA-ME.md`.
- Pedido de edição de vídeo sem dizer onde: perguntar "aqui ou no PC de render?".

## Quadro de vídeos no Notion (fila do Claude)

- Quadro: base "🗓️ CALENDÁRIO EDITORIAL | Legacy", visão **Audiovisual** (quadro por ANDAMENTO):
  https://app.notion.com/p/73ac9747efab8374a5b5812011259272?v=c7bc9747efab821ea98b88388c677927
  (fonte de dados `collection://f0cc9747-efab-822b-8678-07f92372d6b7`).
- Os vídeos para o Claude editar entram na coluna **CLAUDE** (valor `CLAUDE` do status ANDAMENTO).
- Cada card: PAUTA (título; `Reels_Clailton_TD_*` = tela dividida, `NV` = novela), FORMATO, PERFIL,
  PRIORIDADE, DATA D/ CONCLUSÃO, DATA D/ PUBLICACÃO, IDEIA (instruções extras, ex.: "máximo 2min59"),
  MATERIAL NECESSÁRIO, MATERIAL FINALIZADO, RESPONSÁVEL; roteiro no corpo do card.
- Fluxo combinado com o usuário (28/09/2026):
  1. O bruto vem em MATERIAL NECESSÁRIO (na prática, link do Google Drive; pode ser arquivo anexado).
  2. Só começa quando o usuário pedir ("edita os vídeos do Claude"), de qualquer PC ou do celular.
  3. Todo card da coluna CLAUDE é editado **no PC de render** (testes avulsos podem ser em outro PC).
  4. Pronto: subir a prévia na **Sala de Revisão** (Artifact, skill `sala-de-revisao`) e o final em alta em
     EDITADO no Drive; em MATERIAL FINALIZADO vai o link da Sala (primeiro) e o do Drive; card para **Aprovação**.
  5. Correções (desde 11/10/2026): o usuário abre o link da Sala, deixa as notas presas no tempo do vídeo
     (ou escreve no campo **CORREÇÕES (Claude)**) e move o card para **Correções (Claude)**; o PC de render
     lê as notas, faz a v2, v3 e responde cada nota na própria Sala.
- Sala de Revisão: https://claude.ai/artifact/HAcqomJqf9NXRNtyYbkX6v (link de um vídeo: `...#<pauta-em-slug>`).
- O passo a passo completo está na skill `fila-de-render`.
- De qualquer PC: se o usuário pedir para "ativar/mandar o PC de render" editar, entregue o pedido à
  conversa **"Central de Render"** (ou "Render central") do PC de render (`ListAgents` + `SendMessage`), como na skill.
- Estilo: o nome da task manda (NV/Novela, TD, ES). O briefing (IDEIA, corpo, comentários) é lido sempre
  e manda nos detalhes; só decide o estilo quando o nome não tem NV/TD/ES.
