---
name: reels-caixinha-0800
description: Edita reels no formato CAIXINHA DE PERGUNTAS (CX) da Executoria 0800 (Legacy) — o Lucas lê uma pergunta de cliente e responde; vertical 1080x1920 em tela cheia, caixinha de pergunta do Instagram no topo enquanto ele lê (faixa azul "EXECUTORIA 0800" + pergunta azul no branco, entrando com desfoque), legenda da NOVELA com destaques em AZUL, fotos de apoio em tela cheia entrando na palavra, aberto/fechado do Lucas e SEM CTA/animação no final. Use sempre que o pedido for editar um reel "CX"/"caixinha"/"Executoria 0800"/"perguntas do Lucas", arquivos ou cards Reels_0800_CX_*.
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
| Texto da pergunta | o que ele LÊ, em caixa normal, com número em algarismo; cabeçalho **só "EXECUTORIA 0800"** (usuário, 01/10/2026: o "Aniversário Legacy" da referência era de uma caixinha especial; só mude com `CABECALHO` no `caixinha.txt` se ele pedir) |
| Legenda | a da novela/ES (SF Pro Text Black, telas de 1–3 linhas, destaque maior entrando sozinho, sombra v3), **destaques em azul `#03C6FA`** (pedido do usuário: só azul, nada de vermelho/verde/amarelo da referência) |
| Imagens | fotos em tela cheia ~25% do tempo, entrando na palavra; na pergunta, o Lucas aparece com a caixinha por cima (sem imagem). **Regras do B-roll** abaixo |
| Final | **sem CTA e sem animação** (o vídeo acaba na última palavra) |
| Abertura | sem tela dividida; corta a conversa antes de gravar ("vou fazer de novo", "pronto?") |

## B-roll — regras do usuário (correção da v1, 01/10/2026)

- **Nunca marca d'água** (a v1 passou um ovo do Freepik com marca; vídeos de banco do YouTube vêm com "PREVIEW"
  que o detector NÃO pega). Freepik, Shutterstock, Depositphotos, Dreamstime, Pond5/Storyblocks: fora.
- **Nunca texto em inglês** na imagem ("CONTRACT", "REJECTED", "OVERDUE"...). Texto só em português, e só se ajudar.
- **Alta qualidade**: a foto precisa ter pelo menos 1080×1920 no recorte (vertical de ≥ 1700 px de largura
  ou mais). Nada de 512 px (stockcake) nem miniatura.
- **Emoção da fala**: a imagem tem que sentir o que ele diz (pergunta de aperto → empresário angustiado;
  "ovos na mesma cesta" → cesta cheia de ovos; "sai uma nova lei" → Congresso Nacional; "impedir de
  contratar" → relatório rasgado com frustração; "comercial" → equipe de call center).
- **Onde buscar, nesta ordem:**
  1. **Pexels pelo navegador do app** (vertical, sem marca, alta resolução). Abra
     `https://www.pexels.com/pt-br/procurar/<busca em português>/?orientation=portrait` e colete os ids com
     `[...document.querySelectorAll('article img')].map(i=>(i.currentSrc||i.src).match(/photos\/(\d+)/)?.[1]+'|'+i.alt)`
     (o `fetch` da página em segundo plano devolve só as miniaturas das sugestões: navegue de verdade).
     Monte uma folha com `...pexels-photo-<id>.jpeg?auto=compress&w=500`, escolha olhando, baixe a escolhida
     com `?auto=compress&cs=tinysrgb&h=2600` em `T\pexels\<bNN>_<id>.jpg` e use `@a-b arquivo "<caminho>"` no plano.
  2. Unsplash/Pixabay (mesmo cuidado), Pinterest só se a imagem original for limpa.
  3. Vídeo (YouTube/TikTok, linha `filme`) só de cena real, nunca de banco com "PREVIEW"; confira o quadro em tamanho real.
- **Começo com o Lucas** (correção do usuário, 02/10/2026, "Faturo out/nov/dez": "deixar mais o Lucas falando e menos
  tempo de b-rolls"): enquanto ele lê a pergunta, a caixinha fica sobre ele (sem imagem por baixo) e nos primeiros
  ~20 s no máximo 1 imagem curta; nada de imagens em sequência no início.
- Olhe cada escolhida em tamanho real (`qa/folha_imagens.jpg` depois do render) antes de entregar.

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
     vídeo sem pergunta (ex.: CTA da Sessão Estratégica, 15/10/2026): só a linha `SEM CAIXINHA`;
   - `T\plano.txt`: `SEMABERTURA`, `SEMCTA`, `ESTILO 0`, uma linha `@a-b arquivo "T\pexels\bNN_<id>.jpg"` por
     imagem (escolhidas pelas regras do B-roll acima) e `FECHADO @a-b` nas voltas de imagem.
5. `P S\cx.py buscar T` (registra os arquivos). Linhas `foto`/`filme` também funcionam (busca automática da
   tela dividida), mas o resultado da v1 foi reprovado: se usar, olhe `T\qa\candidatos_01.jpg` com as regras do
   B-roll, `T\escolhas.txt` (`b01 2`) e `P <td>\scripts\td.py escolher T`. Tirar/incluir linha muda os ids.
6. `P S\cx.py finalizar T "C:\Render\Reels Editados\<PAUTA> - EDITADO.mp4" --geral`.
7. Olhar `T\qa\caixinha.png`, `folha_geral_01.jpg`, `fundo_mais_claro.png`. Entregar como na `fila-de-render`.

## Lote (lições de 01/10/2026, 5 vídeos de uma vez)

- Fotos: `P S\pexels.py folha T candidatos.json` ({"b01": [ids]}) → olhar `T\qa\pexels.jpg` →
  `P S\pexels.py baixar T escolha.json` ({"b01": ["@a-b", id]}) grava em `T\pexels\` e põe as linhas `arquivo` no plano.
  Os ids vêm do Pexels no navegador do app (várias buscas num `browser_batch`). Confira roupa/caixa com texto em inglês
  ("DELIVERY" na camiseta foi trocado) e dinheiro estrangeiro só se não houver opção.
- Legendas: em lote, um agente `novela-legendista-rapido` por vídeo, em paralelo, com as regras deste formato no pedido
  (destaque só no começo da linha, sem CTA, PRÓ-LABORE/DRE etc.). Você planeja caixinha e fotos enquanto isso.
- "REPETIÇÃO NA EMENDA": `INICIO` sugerido é seguro; **`PARTE` sugerido pode apagar um trecho inteiro** (Clínica: sumiram
  25 palavras). Gaguejo natural curto ("a sua sua", "eu eu") → `repeticoes_ok.txt` (uma palavra por linha).
- Depois de mudar a decupagem, os índices mudam: guarde `palavras_corte_antes.json` e remapeie `@` de legenda, plano e
  caixinha (difflib entre as listas de palavras); linhas que caem no mesmo índice precisam de ajuste à mão.
- Confira palavra-chave sumida no corte: o "LTV" caiu (borda de frase) — escute/transcreva o trecho e use `INICIO n i@t`.
- **Engasgada no começo** (correção do usuário, 02/10/2026, "Faturo out/nov/dez"): o vídeo começa na 1ª fala LIMPA da
  pergunta, mesmo que perca o "Olha só". O Whisper do corte esconde o tropeço (junta "faturo faturo oito faturo" numa
  palavra só): transcreva os primeiros ~10 s do bruto com o modelo `medium` (faster-whisper, CPU) + energia por 0,1 s
  e use `INICIO 0 <i>@<t>` no início do trecho limpo.
- Imagem > 5 s em tela cheia: encurte a faixa `@a-b`. Imagens ~15–25% do tempo.

## Infográficos no lugar de B-roll (padrão desde 15/10/2026)

O usuário pediu "mais motions e infográficos para ilustrar o que o Lucas explica" no lugar das fotos. 7 vídeos feitos
assim (15-16/10: O que entra e sai, Bolo, CTA Sessão, Salão, Levo trabalho, Sazonal, Gerente caro).
- Um projeto HyperFrames por vídeo em `T\motion\` (fontes SF Pro em `motionssets`), uma cena por trecho, cada
  elemento entrando NA PALAVRA (tempo local = palavra − início do trecho, tirado de `timeline.json` com um plano
  provisório). Visual: fundo `#061422` com grade e brilho azul, cartões de vidro com borda `#03C6FA`, SF Pro.
- Ideias que funcionaram: entra × sai, planilha somando, extrato, "AULA 00001", barras entradas − saídas = saldo, DRE
  em cascata + anel de rentabilidade, ficha técnica somando o custo, calculadora de preço, checklist de dores,
  medidor (ponteiro), calendário do mês, lista de tarefas com nota 1-10, delegar, balança custo × rentabilidade,
  funil de vendas, gráfico sazonal do ano, pizza 50/50, números "imaginários" riscados.
- Render: `npx hyperframes render`, recorta cada cena (`ffmpeg -ss <ini> -t <dur+0,12>`) e usa `@a-b arquivo "<cena>.mp4"`.
  Cena mais curta que o trecho: estica com `setpts` (até ~5%) ou `tpad` (congela o 1º/último quadro).
- **Armadilha:** elemento com `fromTo({opacity:0}, …, immediateRender:false)` aparece ANTES da hora; no script,
  embrulhe `tl.fromTo` para dar `tl.set(alvo,{opacity:0},0)` quando o "de" tem opacity 0 (feito nos 4 últimos).
- Imagens ~35-45% do tempo; trechos > 9 s viram 2 cenas ou saem. Números são exemplos ilustrativos (avisar).
- Vídeo sem pergunta (CTA): `caixinha.txt` = `SEM CAIXINHA`.
- Sala de Revisão perto de 256 MB: prévia com `--max-kbps 600` e tirar as prévias das versões antigas já trocadas.

## Onde ajustar

| O quê | Onde |
| --- | --- |
| caixinha (cores, medidas, fontes, animação) | `cx.py`, bloco de constantes no topo |
| azul dos destaques | `cx.py` `AZUL` → `legenda_novela.py --cor-destaque` |
| zoom do Lucas | `cx.py` (`TD_UPSCALE_MAX`, `TD_ROSTO_ABERTO`) e `FECHADO @a-b` no plano |
| altura da legenda | edição simples: `es.py` (`Y_CENTRO`) |
