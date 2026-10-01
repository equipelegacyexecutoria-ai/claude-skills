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

## Como falar com o usuário

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
  Exceção: skills que também vivem no claude.ai (carrossel-canva, corte-viral) precisam de reenvio manual lá.
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
  4. Pronto: anexar o vídeo final em MATERIAL FINALIZADO e mover o card para **Aprovação**.
  5. Correções: o usuário escreve no campo **CORREÇÕES (Claude)** do card (com o tempo do vídeo) e move
     o card para a coluna **Correções (Claude)**; o PC de render faz a v2, v3.
- O passo a passo completo está na skill `fila-de-render`.
- De qualquer PC: se o usuário pedir para "ativar/mandar o PC de render" editar, entregue o pedido à
  conversa **"Central de Render"** (ou "Render central") do PC de render (`ListAgents` + `SendMessage`), como na skill.
- Estilo: o nome da task manda (NV/Novela, TD, ES). O briefing (IDEIA, corpo, comentários) é lido sempre
  e manda nos detalhes; só decide o estilo quando o nome não tem NV/TD/ES.
