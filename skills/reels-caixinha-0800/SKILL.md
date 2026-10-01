---
name: reels-caixinha-0800
description: Edita reels no formato CAIXINHA DE PERGUNTAS (CX) da Executoria 0800 (Legacy) — o Lucas lê uma pergunta de cliente e responde; vertical 1080x1920 em tela cheia, caixinha de pergunta do Instagram no topo enquanto ele lê (faixa azul "EXECUTORIA 0800 | Aniversário Legacy" + pergunta azul no branco, entrando com desfoque), legenda da NOVELA com destaques em AZUL, fotos de apoio em tela cheia entrando na palavra, aberto/fechado do Lucas e SEM CTA/animação no final. Use sempre que o pedido for editar um reel "CX"/"caixinha"/"Executoria 0800"/"perguntas do Lucas", arquivos ou cards Reels_0800_CX_*.
---

# Reels CAIXINHA (CX) — Executoria 0800

Referências (2 vídeos, Drive): `G:\Meu Drive\EXECUTORIA 0800\Modelo prontos (referências)`; brutos em
`G:\Meu Drive\EXECUTORIA 0800\Videos a editar`. Quadro medido da caixinha: `referencia/caixinha_ref.png`.
1º vídeo feito com esta skill: "3 clientes são 70%" (01/10/2026, card `Reels_0800_CX_3clientes`).

## O entregável

| Item | Padrão |
| --- | --- |
| Formato | 1080×1920, 29,97 fps, H.264 CRF 18, voz −16 LUFS (o render da tela dividida, sem película) |
| Lucas | tela cheia; aberto com o rosto ~31% da largura (bruto de celular 1080p: ampliação até 1,8×, `TD_UPSCALE_MAX`/`TD_ROSTO_ABERTO` no `cx.py`); fechado só em corte visível — numa tomada única, force `FECHADO @a-b` na volta de uma imagem |
| Caixinha | aparece no início da 1ª palavra da pergunta e some 0,3 s depois da última; desfoque→nítido + fade em 0,5 s; topo em y=210, 672 px de largura, faixa `#03C6FA` de 82 px com o cabeçalho em SF Pro Display Bold branco, pergunta em SF Pro Display Medium azul centrada (quebra equilibrada em 2 linhas) |
| Texto da pergunta | o que ele LÊ, em caixa normal, com número em algarismo; cabeçalho padrão "EXECUTORIA 0800 \| Aniversário Legacy" (mude no `caixinha.txt` se a campanha mudar) |
| Legenda | a da novela/ES (SF Pro Text Black, telas de 1–3 linhas, destaque maior entrando sozinho, sombra v3), **destaques em azul `#03C6FA`** (pedido do usuário: só azul, nada de vermelho/verde/amarelo da referência) |
| Imagens | fotos em tela cheia ~20–30% do tempo, entrando na palavra (empresário preocupado, ovos na cesta, aperto de mão...); a pergunta já leva 2 imagens por baixo da caixinha. A referência usa imagens geradas por IA: só gere com IA se o usuário autorizar o gasto de créditos; senão, banco de fotos pela busca da tela dividida |
| Final | **sem CTA e sem animação** (o vídeo acaba na última palavra) |
| Abertura | sem tela dividida; corta a conversa antes de gravar ("vou fazer de novo", "pronto?") |

## Modo rápido (~10 min)

`P = %LOCALAPPDATA%\corte-viral\venv\Scripts\python.exe` (com `PYTHONUTF8=1`), `S = ~/.claude/skills/reels-caixinha-0800/scripts`,
`T = C:\Render\_trabalho\<slug>` (caminho absoluto).

1. `P S\cx.py preparar "<bruto>" T` — grava uma cópia em pé se o vídeo do celular tiver rotação em metadado
   (sem isso o enquadramento não acha o rosto) + transcrição + decupagem automática.
2. Revisar `T\decupagem_proposta.txt` (regras da novela) → `T\decupagem_ajustes.txt` (`SAI 0` etc.) →
   `P <novela>\scripts\decupar_auto.py T --aplicar T\decupagem_ajustes.txt`.
3. `P S\cx.py montar T`.
4. Escrever, a partir de `T\palavras_legenda.txt`:
   - `T\legenda.txt` (formato compacto da novela; `**0800` no "Executoria 0800" da abertura);
   - `T\caixinha.txt`: `PERGUNTA <texto>` e `@i0-i1` (palavras em que ele lê a pergunta);
   - `T\plano.txt`: `SEMABERTURA`, `SEMCTA`, `ESTILO 0`, uma linha `@a-b foto "busca" | en: ...` por imagem
     (sintaxe: `reels-tela-dividida-clailton/referencia/regras-plano-visual.md`) e `FECHADO @a-b` nas voltas.
5. `P S\cx.py buscar T` → olhar `T\qa\candidatos_01.jpg` → `T\escolhas.txt` (`b01 2`) →
   `P <td>\scripts\td.py escolher T`. Se tirar/incluir uma linha do plano, os ids mudam: busque de novo inteiro.
6. `P S\cx.py finalizar T "C:\Render\Reels Editados\<PAUTA> - EDITADO.mp4" --geral`.
7. Olhar `T\qa\caixinha.png`, `folha_geral_01.jpg`, `fundo_mais_claro.png`. Entregar como na `fila-de-render`.

## Onde ajustar

| O quê | Onde |
| --- | --- |
| caixinha (cores, medidas, fontes, animação) | `cx.py`, bloco de constantes no topo |
| azul dos destaques | `cx.py` `AZUL` → `legenda_novela.py --cor-destaque` |
| zoom do Lucas | `cx.py` (`TD_UPSCALE_MAX`, `TD_ROSTO_ABERTO`) e `FECHADO @a-b` no plano |
| altura da legenda | edição simples: `es.py` (`Y_CENTRO`) |
