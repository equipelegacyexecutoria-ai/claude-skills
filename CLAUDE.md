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

## Skills sincronizadas entre os PCs

Skills, agentes e este arquivo ficam no cofre privado `equipelegacyexecutoria-ai/claude-skills`
e sincronizam sozinhos (ao abrir a conversa e ao fim de cada resposta).
- Aprendizado que deve valer sempre vai para a skill ou para este arquivo. A memória do projeto é só deste PC.
- Entre `<nome>` e `anthropic-skills:<nome>`, usar sempre a skill pessoal (`<nome>`).
- Nunca escrever caminho com o nome de usuário do Windows em skills e agentes; usar `~/.claude/...` ou `$HOME`.
- Apagar skill ou arquivo só com `git rm` dentro de `~/.claude`; apagar pelo Explorer é revertido.
- Pacote Python novo instalado para uma skill entra no requirements dela.
- Linha começando com `SYNC:` na abertura da conversa: seguir `~/.claude/sync/LEIA-ME.md`.
- Pedido de edição de vídeo sem dizer onde: perguntar "aqui ou no PC de render?".
