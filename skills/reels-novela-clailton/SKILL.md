---
name: reels-novela-clailton
description: Edita reels no estilo NOVELA do Instagram do Clailton (Legacy Educação) a partir do bruto 4K horizontal e do roteiro — decupagem das tomadas, faixa de imagem 5:4 com barras pretas, legenda SF Pro Text Black em telas com destaque maior entrando sozinho (desfoque + queda, sombra v3 em camadas, layouts centro/esquerda/escada), âncora em enumerações e CTA final "ME SIGA PARA MAIS CONTEÚDOS COMO ESTE" em máquina de escrever. Modo rápido — scripts fazem transcrição (GPU), decupagem, corte, alinhamento de palavras, comparação fala x roteiro, render e conferência; o próprio orquestrador revisa a decupagem e escreve a legenda (agentes só em lote e com prazo). Entrega 1080x1920 em qualidade máxima. Use sempre que o pedido for editar/legendar um reel "NV"/"novela" do Clailton, arquivos Reels_Clailton_NV_*, "edita igual ao reel do PHD", "estilo novela", "legenda com barra preta em cima e embaixo", ou refazer um reel nesse formato.
---

# Reels NOVELA — Clailton

Padrão tirado, quadro a quadro, do reel de referência "Você quer ficar rico? Então torna-te
um PHD" (e conferido em outras duas edições da equipe). **Tudo o que foi medido está em
`referencia/estilo-novela.md`** — leia antes de mexer em qualquer parâmetro. Telas da
referência: `referencia/telas-referencia.jpg`. Legendas de exemplo no formato compacto:
`referencia/legenda-aprovada-video1.txt` (aprovada pelo usuário) e `referencia/legenda-video2.txt`.

## O entregável

| Item | Padrão |
| --- | --- |
| Formato | 1080×1920, 29,97 fps, H.264 High **CRF 10** preset slow, yuv420p BT.709, AAC 320k — o usuário pediu **qualidade máxima, sem comprimir** |
| Imagem | faixa 1080×864 (5:4) centrada, barras pretas; recorte fixo tirado direto do 4K (só redução) |
| Corte | tomadas escolhidas, sem tropeço; início e fim **colados na voz**; frases coladas com ~0,16 s, **nenhuma pausa > 0,3 s** (nada de pausa dramática); sem música (entra depois) |
| Legenda | SF Pro Text Black, caixa-alta, telas de 1–3 linhas inteiras, **só o destaque entra sozinho e maior**, sombra v3 |
| Final | ~0,45 s depois da última palavra, corte seco para CTA preta digitada (2,9 s) |
| Voz | −14 LUFS, pico −1 dBTP |
| Pasta | `Reels Editados/` na raiz do projeto, `<nome do bruto> - EDITADO.mp4` |
| Trabalho | `_trabalho/<slug>/` na raiz do projeto (transcrição, decupagem, legenda, QA) |

**Portão:** o primeiro vídeo de um lote é sempre mostrado ao usuário para validar e lapidar
ANTES de editar os outros. Regra global do usuário: testar a legenda no trecho de fundo mais
claro e mostrar antes de gerar em lote (`qa/fundo_mais_claro.png` sai da conferência).

## Entrada: bruto + roteiro

O usuário manda o **bruto** (arquivo do vídeo) e, sempre que possível, o **roteiro** (texto
colado na conversa, `.txt`, `.docx` ou `.md`). Salve o roteiro em `T\roteiro.txt` (ou copie o
arquivo para `T\roteiro.docx`) ANTES do passo 1. Palavras em MAIÚSCULAS ou *entre asteriscos*
no roteiro = destaque sugerido. Não precisa pedir transcrição: a skill gera a sua (literal, com
tempo de cada palavra, 15 s na GPU).

O Clailton às vezes muda frases e termos na gravação. Regras:
- **A legenda segue o que foi FALADO**, nunca texto que não está no áudio.
- Frase fluente diferente do roteiro (reformulou, trocou termo) = improviso: **fica** como falada.
- Recomeço quebrado, frase interrompida = tropeço: **sai**. O roteiro mostra qual é a frase inteira.
- Trecho do roteiro sem nenhuma frase que fica: procure a tomada (pode ter sido descartada por
  engano). Se ele não gravou, avise na entrega.
- Duas tomadas completas e fluentes: fica a última (padrão), salvo se só a outra bate com o roteiro.
- Grafia de nomes, termos e números: a do roteiro (e `referencia/grafias.md`).
- Deslize que muda o sentido ou palavra estranha ("peça comigo" x "pensa comigo"): confira com
  `ctc_candidatos.py` e **pergunte** ao usuário em vez de decidir sozinho.
- Toda diferença entre o corte final e o roteiro vai listada na entrega: "falou X | roteiro Y".

Sem roteiro, tudo funciona igual (a decupagem usa só a fala). `roteiro.py` roda sozinho no
preparar e no montar quando existe roteiro e grava `T\roteiro_x_fala.txt`:
1. cada frase do bruto x roteiro (quanto cobre), frase que FICA fora do roteiro e trecho do
   roteiro sem frase que FICA (com a frase SAI que o cobre, se houver);
2. depois do corte: TROCOU / FALTOU / A MAIS palavra a palavra, com o `@índice` do corte, e
   os destaques sugeridos pelo roteiro com o índice.

## Economia de tempo e tokens (medido no vídeo 2)

- **Uma conversa nova por vídeo** (ou por lote pequeno). Numa conversa longa, cada chamada
  relê todo o histórico: no vídeo 2 foram ~437 mil tokens por chamada (~5,7 milhões de
  tokens-equivalentes no total). Em conversa nova são ~80–150 mil por chamada, cerca de 3×
  menos. A skill e a memória guardam tudo o que importa.
- **Escolha o modelo antes de começar e não troque no meio**: a troca obriga a regravar todo o
  histórico no cache (~21% do custo do vídeo 2).
- O orquestrador faz a revisão da decupagem e a legenda direto. Agentes só em lote e **com
  prazo**: 6 min sem o arquivo esperado = pare o agente e faça você (no vídeo 2 o legendista
  ficou 18 min "rodando" sem gravar nada).
- Agrupe chamadas independentes numa resposta só. Não releia arquivos grandes nem imagens sem
  necessidade.
- Na entrega, relate o **tempo por etapa** (o usuário acompanha e pergunta).

## Ambiente (Windows)

- Python da skill, sempre com `PYTHONUTF8=1`:
  - `P = %LOCALAPPDATA%\reels-novela\venv\Scripts\python.exe` (instalado pelo pacote);
  - na máquina onde a skill nasceu, `P = %LOCALAPPDATA%\corte-viral\venv\Scripts\python.exe`;
  - no bash: `P="$LOCALAPPDATA/reels-novela/venv/Scripts/python.exe"; [ -x "$P" ] || P="$LOCALAPPDATA/corte-viral/venv/Scripts/python.exe"`.

  O Whisper roda na **GPU NVIDIA** (float16): as DLLs do CUDA vêm dos pacotes
  `nvidia-cublas-cu12` / `nvidia-cudnn-cu12` da venv e o `comum.whisper()` registra as pastas.
  Sem GPU, cai sozinho para CPU int8 (~10× mais lento).
- **Alinhador**: venv própria `%LOCALAPPDATA%\reels-novela\venv-align` (WhisperX 3.8, torch
  2.8.0+cu128, modelo `jonatasgrosman/wav2vec2-large-xlsr-53-portuguese` no cache do Hugging
  Face). O `montar_corte.py` chama sozinho. Sem ela tudo funciona, com a legenda no tempo do
  Whisper + heurística (até 0,2 s adiantada).
- ffmpeg no PATH, build completa (gyan.dev: libass, libx264, NVDEC/cuda para decodificar o 4K).
- `S = %USERPROFILE%\.claude\skills\reels-novela-clailton\scripts` (bash:
  `$USERPROFILE/.claude/skills/reels-novela-clailton/scripts`).
- **Antes do 1º vídeo de um lote:** `P S\verificar.py` (módulos, Whisper GPU, alinhador,
  ffmpeg/filtros, fontes, modelo de rosto, agentes).
- Agentes: a cópia ORIGINAL é `agentes/` desta skill; `~/.claude/agents/` é a instalada
  (o `verificar.py` compara). Se o tipo de agente não estiver disponível na sessão, crie um
  agente general-purpose com o conteúdo do `.md` como instrução (e `model` do cabeçalho).
- **Outro computador:** o pacote fica em `Projetos Edições\SKILLS\reels-novela-clailton\`
  (`reels-novela-clailton.zip` + instruções). Descompacte e rode `INSTALAR.cmd`. Ele copia a skill e
  os agentes, instala Python 3.12 e ffmpeg (winget), cria as duas venvs com as versões travadas
  (`requirements.txt`, `requirements-alinhador.txt`), baixa os modelos e roda o `verificar.py`.
  Ao mudar a skill, gere o pacote de novo.

## Modo rápido (padrão) — ~10–15 min por vídeo

Scripts, medidos no vídeo 2 (bruto de 3min39s → reel de 2:15): preparar 57 s, montar ~1 min,
finalizar 2,5 min (render 92 s + conferência 63 s). O resto é julgamento: revisão da
decupagem (~5 min) e legenda (~5 min). `T = <projeto>\_trabalho\<slug>`.

0. **Roteiro** — se veio, salve em `T\roteiro.txt` (ou `.docx`) antes do passo 1.
1. **Preparar** — `P S\editar.py preparar "<video>" T` (~1 min). Transcrição na GPU
   (`transcricao.txt`; palavra sem energia de voz sai `[sem voz]` = invenção do Whisper) +
   decupagem automática (`decupar_auto.py`). Ela divide o bruto em frases e troca cada tomada
   repetida pela última completa. Também tira a fala para a equipe e faz uma passada literal
   que acusa repetição escondida. Também acha **falso começo escondido**: silêncio dentro de uma
   palavra esticada pelo Whisper, com os dois lados transcritos ("parar al-... Parar alguma
   coisa" saía como "Parar alguma coisa"). Anáfora (palavra repetida 3+ vezes com complementos
   diferentes) sai marcada como intencional. Saída: `decupagem_proposta.txt`, uma linha por
   frase `n [i0-i1] tempo ESTADO (motivo) | texto`, com os avisos `⚠` e o ajuste provável.
   Com roteiro, sai também `roteiro_x_fala.txt` (parte 1).
2. **Revisar a decupagem** — leia `decupagem_proposta.txt` (curto) e, se houver,
   `roteiro_x_fala.txt`. Grave `T\decupagem_ajustes.txt` (vazio se estiver certo) e aplique:
   `P S\decupar_auto.py T --aplicar T\decupagem_ajustes.txt`. Reaplicar sempre parte da
   proposta original. Ajustes possíveis:
   - `SAI n` / `FICA n`;
   - `FIM n i`;
   - `INICIO n i[@t]`: a frase começa na palavra i e a fala não antes de t s;
   - `PARTE n k j[@t]`: falso começo no meio da frase; fica até k e retoma em j.

   Regras:
   - DÚVIDA de conversa com a equipe sai.
   - Falso começo escondido → o ajuste `provável` da proposta, se "depois" repete "antes".
   - "Parece anáfora" → não corte.
   - `⚠ repetição` no começo → `INICIO` depois das palavras repetidas.
   - Com roteiro: aplique as regras da seção "Entrada: bruto + roteiro".
   - Não encurtar a mensagem; nada de pausa dramática.

   No vídeo 1 a proposta automática + 3 ajustes reproduziu o corte aprovado quadro a quadro.
   No vídeo 2 os 5 falsos começos escondidos foram achados ("Mas que... mas talvez", "torcer
   pra você fracassar" 2×, "ninguém espera a ansia-", "a torcida contra começa" 3×, "Às vezes
   você" 2×).
   - **Palavra que o Whisper ouviu estranho** (ex.: "Peça comigo" em vez de "Pensa comigo"):
     confira com o modelo acústico antes de corrigir a legenda: `S\ctc_candidatos.py` (roda na
     venv do alinhador; menor perda = o que foi dito). Calibre numa palavra certa do mesmo falante.
3. **Montar** — `P S\editar.py montar T` (~1 min; o enquadramento roda junto com a retranscrição
   e o alinhamento).
   - `montar_corte.py` corta colado na voz, encurta pausas para ≤ 0,3 s e retranscreve o áudio
     cortado. Depois faz o **alinhamento forçado** (erro de ~1 quadro por palavra) e gera
     `palavras_legenda.txt`.
   - `enquadrar.py` calcula o crop e o queixo. O 4K é decodificado na GPU, que descarta os
     quadros e só baixa os 2 por segundo da amostra; detector de rosto em 6 segmentos ao mesmo
     tempo, com resultado idêntico ao da CPU.
   - Com roteiro, `roteiro_x_fala.txt` ganha a parte 2: TROCOU / FALTOU / A MAIS com o `@índice`
     e os destaques sugeridos.

   Leia `roteiro_corte.txt`: nada de repetição, falso começo ou fala para a equipe. Leia também
   os avisos.
4. **Legenda** — **escreva você mesmo** (o orquestrador), em uma passada, seguindo
   `agentes/novela-legendista-rapido.md`. Leia `palavras_legenda.txt` e o tempo alinhado de
   cada palavra (`palavras_corte.json`), para planejar telas de 0,6–3 s. Grave `legenda.txt` no
   formato compacto e valide com `legenda_novela.py` até zerar os avisos (no vídeo 2: 5,5 min,
   passou de primeira).
   - Com roteiro: a legenda segue a fala; grafia e destaques sugeridos vêm do roteiro.
   - Palavra duvidosa: `correcao | i=... whisper=... legenda=... motivo=...` e pergunte na entrega.
   - Referência de estilo: `referencia/legenda-aprovada-video1.txt`.
   - O agente **novela-legendista-rapido** só para lote em paralelo, e com prazo de 6 min.
   - Tela com destaque d2 largo não cabe em escada: use centro (o validador avisa "escada não
     coube").
5. **Finalizar** — `P S\editar.py finalizar T "<projeto>\Reels Editados\<nome> - EDITADO.mp4"`
   (~2,5 min): legenda `.ass`, render (6 intermediários sem perda por vez + 1 encode CRF 10) e
   `conferir.py --whisper`, que confere:
   - formato, loudness e pico, CTA;
   - pausas > 0,33 s;
   - sincronia A/V quadro a quadro;
   - cada emenda em transcrição literal;
   - fundo mais claro sob a legenda;
   - e gera as folhas.

   Código 0 = aprovado, 3 = reprovado (não entregue assim). Repetição **intencional** que a
   revisão manteve (anáfora "continue... continue") vai em `T\repeticoes_ok.txt`, uma palavra
   por linha: a conferência lista, mas não reprova.
6. **Olhar** — você mesmo: `qa/folha_blocos_*.jpg`, `qa/folha_cta.jpg`,
   `qa/fundo_mais_claro.png`, `qa/emendas_literal.txt`. Chame o **novela-revisor** só se a
   conferência reprovar por algo real, se algo parecer errado nas folhas ou no 1º vídeo de um lote.
7. **Entregar** — o vídeo e um relatório curto:
   - tempo por etapa;
   - diferenças entre o corte e o roteiro ("falou X | roteiro Y") e o que foi feito;
   - decisões para o usuário confirmar (trecho cortado que pode ter sido intencional, palavra
     duvidosa, repetição mantida).

   No 1º vídeo do lote, pare e espere a aprovação.

Correções depois de pronto:
- **Trocar tomada/trecho**: novo `decupagem_ajustes.txt` → `--aplicar` → `editar.py montar`
  → a legenda precisa ser refeita (os índices mudam) → `finalizar`.
- **Ajuste fino de corte sem mudar o texto**: `P S\montar_corte.py T --manter-palavras` (mesmos
  índices; tempos remapeados pelo bruto, a legenda é aproveitada) → `finalizar`.
- **Só legenda**: edite `legenda.txt` → `finalizar`.
- **Ver um quadro sem renderizar**: `P S\previa_quadro.py T 12.5,40.2 T\qa\previa.png [--faixa]`.

## Modo completo (material difícil)

Se a decupagem automática errar muito (muitas DÚVIDAs, tomadas embaralhadas, improviso),
use os agentes completos:
- **novela-decupador** escreve `decupagem.json` direto e roda `montar_corte.py`.
- **novela-legendista** escreve `legenda.json`, em várias passadas.

O `legenda_novela.py` e o `editar.py finalizar` aceitam os dois formatos (usam `legenda.txt`
se existir, senão `legenda.json`).

## Onde ajustar cada coisa

| Quero mudar | Onde |
| --- | --- |
| tamanho/espaçamento/entrelinha da legenda, níveis d1/d2/d3 | `legenda_novela.py` (bloco de constantes no topo) |
| posição vertical (centro do bloco), margens, alinhamento à esquerda, passo da escada | `legenda_novela.py` (`Y_CENTRO`, `X_*`, `PASSO_ESCADA`) |
| animação de entrada (queda, desfoque, curva) | `legenda_novela.py` (`QUEDA`, `R_POS`, `R_BLUR`, `blur_inicial`) |
| sombra | `legenda_novela.py` (`SOMBRA`) — padrão v3 aprovado pelo usuário; não trocar sem pedir |
| tempo da legenda x fala | alinhamento (`alinhar.py`); sem ele, `legenda_novela.py` (`ATRASO_FALA_CORRIDA`, `PAUSA_CORRIDA`) |
| CTA (texto, fonte, velocidade, duração) | `legenda_novela.py` (bloco CTA) |
| ritmo do corte (silêncio entre frases, pausas, respiro final) | `comum.py` (`PAUSA_*`, `FIM_RESPIRO`) e `montar_corte.py` (margens, faixas de energia) |
| decupagem automática (frase, tomada repetida, fala para a equipe, dúvida, anáfora) | `decupar_auto.py` (`PAUSA_FRASE`, `SIMIL*`, `META`, regras de DÚVIDA e anáfora) |
| comparação com o roteiro | `roteiro.py` |
| grafia de nomes/termos | roteiro do vídeo e `referencia/grafias.md` |
| enquadramento-alvo | `comum.py` (`ROSTO_*`) |
| qualidade/áudio | `comum.py` (`CRF`, `PRESET`, `AUDIO_BR`, `LUFS`) |

## Armadilhas já resolvidas (não repetir)

- **libass desliga o kerning quando há `\fsp`.** Com espaçamento negativo, "VA/TA/AT" se
  atropelavam. O `texto.py` aplica o kerning à mão: um `\fsp` por letra (espaçamento +
  kerning do par, via HarfBuzz). Não troque por `\fsp` único.
- `\fsp` vale para o espaço DEPOIS da letra; o campo Spacing do estilo é ignorado.
- Fonte no libass: nome PostScript `SFProText-Black` (o nome "SF Pro Text Black" cai em Arial);
  CTA: família `Inter 28pt ExtraBold`. Sempre `fontsdir=fonts` com caminho relativo e
  `cwd` = pasta de trabalho (o filtro `ass` não aceita bem caminho com espaço/acento).
- O Whisper marca a palavra cedo demais na fala corrida (mediana 0,09 s, até 0,3 s) e
  **estica palavra por cima da pausa** ("se", "que", "um" começando no silêncio). O
  alinhamento forçado resolve (`palavras_corte.json` com `"alinhado": true`; a legenda então
  não soma atraso). Sem alinhador: `refinar_inicios` pela energia + `ATRASO_FALA_CORRIDA`.
- `pip install whisperx` troca o torch CUDA pelo de CPU (o whisperx 3.8 fixa torch 2.8.0).
  Depois dele: `pip install --no-deps --force-reinstall torch==2.8.0 torchaudio==2.8.0
  torchvision==0.23.0 --index-url https://download.pytorch.org/whl/cu128` (o instalador já faz).
- No app Claude Desktop (MSIX) o `%LOCALAPPDATA%` do app é virtualizado
  (`AppData\Local\Packages\Claude_*\LocalCache\Local`). O que o app grava fica lá; o que o
  instalador grava por fora vai para a pasta real, que o app também enxerga.
- Caminho relativo do bruto quebrava o enquadramento (ele roda dentro da pasta de trabalho):
  o `transcrever.py` grava o caminho absoluto.
- Respiração x voz: testados Silero VAD e parselmouth. O Silero dá 0,5–0,8 de "fala" para
  respiração, então não separa melhor que o detector de energia em duas faixas do
  `montar_corte`. Não troque.
- Whisper com `condition_on_previous_text=False` (com tomadas repetidas o modelo pula texto).
- `ffmpeg drawtext` dá segfault: rotular quadros com Pillow. OpenCV não abre caminho com
  acento: frames vão por pipe do ffmpeg.
- Extrair quadro: com o ASS aplicado NA extração, `-ss` depois do `-i` (senão a legenda recomeça
  do zero). Do vídeo final (legenda já queimada), `-ss` ANTES do `-i`: mesmo quadro (md5
  conferido), sem decodificar o vídeo desde o início. Só isso levou a conferência de 480 s a 84 s.
- **loudnorm "linear" vira compressor dinâmico sem avisar** quando o ganho estoura o teto de
  pico (os brutos vêm a −21/−23 LUFS: +7 a +9,5 dB). O render usa ganho linear + limitador
  só nos picos (`alimiter`, `level=false`, `latency=true`) e registra o modo.
- `ebur128` só imprime o pico real com `peak=true`.
- Whisper de conferência só na parte falada e com VAD: no silêncio da CTA ele inventa texto.
- **O Whisper engole repetição** ("dá aquela... dá aquela" vira uma vez só). O `decupar_auto`
  e o `conferir.py` fazem passadas literais (prompt neutro de gaguejo, janela curta) e acusam
  palavra repetida. Anáfora aprovada vai em `T\repeticoes_ok.txt`.
- Corte sobrando no fim do trecho ("demorou para ele começar a falar") e pausa longa ("talvez
  seja") foram reprovados pelo usuário: margens de 0,05 s, borda estendida no máximo 0,10 s,
  toda pausa interna > 0,30 s encurtada para 0,16 s.
- Acento de linha grande embaixo de outra linha some dentro da letra de cima (L, E, T): o
  vão entre linhas é calculado letra a letra (`vao_entre`) e o contato da sombra fica abaixo
  de todas as linhas. Nunca volte o contato para cima da linha de baixo.
- Nunca cortar com `-c copy` (pega o quadro-chave errado); o render sempre recodifica.
- **Nunca `-r` no intermediário de cada segmento**: a busca cai meio quadro antes e o `-r`
  duplicava o 1º quadro e descartava o último (imagem 33 ms atrás do áudio em metade dos
  segmentos). O intermediário usa `-fps_mode passthrough`; o encode final refaz o tempo pelo
  número do quadro (`setpts=N*1001/30000/TB`). A busca `-ss` antes do `-i` é exata.
  O `conferir.py` compara quadros do final com o bruto e acusa qualquer desvio de sincronia.
- O bruto Sony vem marcado xvYCC (iec61966-2-4): o render marca BT.709 (`setparams`).
- Render existir não é render certo: `conferir.py` + olhar as folhas antes de mostrar.
- Paralelismo validado bit a bit: intermediários (6 por vez), extrações da conferência (8) e
  enquadramento (NVDEC + 6 detectores). A imagem e o áudio saem com o mesmo md5 do modo serial.
- Agente em segundo plano pode travar sem gravar nada (vídeo 2: 18 min): sempre com prazo.
- Editar arquivo da skill por script Python dentro do bash: a barra invertida de caminho vira
  caractere de controle (o `\r` de `T\repeticoes` virou quebra de linha). Use as ferramentas de
  edição do Claude ou `chr(92)`, e confira em bytes (modo texto converte CR em LF e esconde o erro).
