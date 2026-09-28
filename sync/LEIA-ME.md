# Sincronia das skills — manual para o Claude

O que sincroniza: `skills/`, `agents/`, `hooks/`, `sync/` e `CLAUDE.md` de `~/.claude`, no cofre
privado `equipelegacyexecutoria-ai/claude-skills` (ramo `main`). Nunca sincroniza: conversas,
memórias, `settings.json`, credenciais, `skills/synced/` (skills da conta), vídeos.

Como roda: o hook `SessionStart` chama `sync.ps1 -Modo inicio` (recebe e avisa) e o hook `Stop`
chama `sync.ps1 -Modo fim` em segundo plano (envia). Log: `~/.claude/sync-local/sync.log`.
O usuário não é técnico: explique pelo dia a dia, sem termos como commit, merge ou branch.

## Comandos (rodar no Bash)

```
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "$HOME/.claude/sync/sync.ps1" -Modo agora
git -C ~/.claude log --oneline --since="7 days ago"          # o que mudou na semana
git -C ~/.claude log --oneline -- skills/<skill>              # histórico de uma skill
```

## Avisos `SYNC:` na abertura

- **recebido de X: ...** — só informe o usuário em uma linha, se for relevante para o pedido.
- **skill ou agente novo chegou** — diga ao usuário para abrir uma conversa nova (ou `/reload-skills`).
- **hooks.json mudou** — rode `powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$HOME/.claude/sync/mesclar-hooks.ps1"`.
- **arquivo(s) apagado(s) fora do Claude foram restaurados** — pergunte se era para apagar; se sim, veja "Apagar".
- **mais de 10 MB / senha ou chave** — o arquivo ficou fora; explique e sugira a correção.
- **OFFLINE** — nada a fazer; envia sozinho quando a rede voltar.
- **LOGIN** — veja "Login".
- **CONFLITO** — veja "Conflito".

## Conflito

Dois PCs mudaram o mesmo trecho. A versão do outro PC está no ramo `origin/conflito/<PC>`;
nada foi perdido.
A outra versão é `origin/main` quando o aviso diz "este PC" (a versão deste PC está aqui), ou
`origin/conflito/<PC>` quando o aviso é "pendente de outro PC".
1. `git -C ~/.claude fetch origin` e `git -C ~/.claude diff HEAD <outra versão> -- <arquivos>`.
2. Mostre ao usuário, em linguagem simples, as duas versões do trecho e pergunte: ficar com a
   deste PC, com a do outro, ou juntar as duas (proponha o texto juntado).
3. Com a resposta: `git -C ~/.claude merge --no-commit <outra versão>`, deixe os arquivos
   como o usuário escolheu, `git add` e `git commit -m "junta conflito"`, depois rode o
   `sync.ps1 -Modo agora`. O ramo `conflito/<PC>` some sozinho depois da junção.
Se aparecer "juncao pela metade" (MERGE_HEAD): termine a junção como acima ou `git merge --abort`.

## Voltar uma versão

"Volta a skill X para como estava ontem": ache o commit com `git -C ~/.claude log -- skills/X`,
rode `git -C ~/.claude checkout <commit> -- skills/X`, confira com o usuário e deixe o hook
enviar (ou rode `-Modo agora`). Nunca use `reset --hard`, `stash` ou `clean`.

## Apagar

Apagar pelo Explorer é revertido. Para apagar de verdade: `git -C ~/.claude rm -r skills/X`
e `sync.ps1 -Modo agora`. Sai de todos os PCs.

## Login

O PC perdeu o login do GitHub da conta `equipelegacyexecutoria-ai`. Peça ao usuário para rodar,
numa janela do PowerShell fora do app: `git -C "$HOME\.claude" fetch` — o navegador abre e ele
entra com a conta **equipelegacyexecutoria-ai** (não a legacyeducacao). Depois `-Modo agora`.

## PC novo

Ver `INSTALAR-MAQUINA.cmd` nesta pasta (ou o playbook da Central de Render).
