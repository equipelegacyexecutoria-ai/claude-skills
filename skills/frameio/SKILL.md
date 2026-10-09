---
name: frameio
description: Ligação direta com o Frame.io da Legacy (conta educacaolegacy@gmail.com, projeto "Criativos Igor") — lista projetos e pastas, lê os comentários de um vídeo com o tempo certo (mm:ss), baixa arquivos, cria pastas e sobe vídeos finalizados. Use quando o usuário falar em Frame.io, "pega as correções do Frame", "lê os comentários do vídeo no Frame", "sobe no Frame.io", "baixa do Frame", ou mandar um link next.frame.io.
---

# Frame.io (API V4, login Adobe)

Script: `python ~/.claude/skills/frameio/scripts/frameio.py <comando>` (só biblioteca padrão do Python + `openssl` do Git).

| Comando | O que faz |
| --- | --- |
| `projetos` | workspaces e projetos (com id e pasta raiz) |
| `listar <projeto_id ou pasta_id>` | conteúdo da pasta (projeto = pasta raiz) |
| `comentarios <arquivo_id>` | comentários em ordem de tempo `[mm:ss.cc]`; salva JSON em `~/FrameIO/` |
| `baixar <arquivo_id> [destino]` | baixa o original |
| `subir <arquivo_local> <pasta_id ou projeto_id>` | envio em partes; imprime o link |
| `criar-pasta <pasta_id ou projeto_id> <nome>` | cria subpasta |
| `get <caminho>` | chamada crua para depurar (ex.: `get me`, sem barra inicial no Git Bash) |

Link `next.frame.io/project/<projeto>/view/<arquivo>`: o último id é o `arquivo_id`.

## Onde ficam os códigos (fora da sincronia, um por PC)

`~/FrameIO/`: `credenciais.txt` (CLIENT_ID/CLIENT_SECRET do projeto "Project 1" no Adobe Developer
Console da org equipelegacyexecutoria), `token.json` (login, renova sozinho), `conta.json`, certificado localhost.
Nunca pedir esses códigos no chat nem copiá-los para skills.

## PC novo (ex.: PC de render)

1. O usuário copia `~/FrameIO/credenciais.txt` deste PC para o mesmo lugar no outro PC.
2. Rodar `frameio.py login` em segundo plano: abre a Adobe → entrar com **educacaolegacy@gmail.com**
   (não a equipelegacyexecutoria: essa não é usuária do Frame.io) → Permitir → no aviso do Chrome
   "conexão não é particular", Avançado → Ir para localhost. Aparece "Pronto!".

## Erros conhecidos

- "Your Frame user is not linked to an Adobe ID" → login feito com a conta Adobe errada; refazer com educacaolegacy.
- "Please contact the application developer" → a conta não está em Beta users do projeto no Developer Console
  (hoje: educacaolegacy@gmail.com). O projeto está "In development" (máx. 25 usuários beta).
- 403 HTML → falta o cabeçalho User-Agent (o script já manda).
- Tempo dos comentários vem em **quadros**; o script converte pelo Frame Rate do arquivo.
- Comentários não trazem o autor (owner vem nulo nesta API).
