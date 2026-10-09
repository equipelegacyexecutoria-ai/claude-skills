---
name: reels-novela-clailton
description: Edita reels no estilo NOVELA do Instagram do Clailton (Legacy Educação) a partir do bruto 4K horizontal e do roteiro — decupagem das tomadas, faixa de imagem 5:4 com barras pretas, legenda SF Pro Text Black em telas com destaque maior entrando sozinho (desfoque + queda, sombra v3 em camadas, layouts centro/esquerda/escada), âncora em enumerações e CTA final "ME SIGA PARA MAIS CONTEÚDOS COMO ESTE" em máquina de escrever com o som de teclado padrão sincronizado. Modo rápido — scripts fazem transcrição (GPU), decupagem, corte, alinhamento de palavras, comparação fala x roteiro, render e conferência; o próprio orquestrador revisa a decupagem e escreve a legenda (agentes só em lote e com prazo). Entrega 1080x1920 em qualidade máxima. Use sempre que o pedido for editar/legendar um reel "NV"/"novela" do Clailton, arquivos Reels_Clailton_NV_*, "edita igual ao reel do PHD", "estilo novela", "legenda com barra preta em cima e embaixo", ou refazer um reel nesse formato.
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
| Formato | 1080×1920, 29,97 fps, H.264 High **CRF 18** preset slow (era CRF 10; em 28/09/2026 o usuário achou pesado demais: 1,2 GB em 2:42), yuv420p BT.709, AAC 320k — o usuário pediu **qualidade máxima, sem comprimir** |
| Imagem | faixa 1080×864 (5:4) centrada, barras pretas; recorte fixo tirado direto do 4K (só redução), **altura cheia do bruto: só as laterais saem** |
| Corte | tomadas escolhidas, sem tropeço; **cortes certeiros no limite da onda** (usuário, 28/09/2026: "ele parado sem falar nada denuncia que está lendo"): toda pausa de voz a voz ≥ 0,12 s sai, inclusive dentro da frase, ficando ~0,02 s antes do ataque e ~0,03 s depois do fim da onda (`aparar` + `borda_voz.py`); respiro e estalo de boca saem; sem música (entra depois) |
| Legenda | SF Pro Text Black, caixa-alta, telas de 1–3 linhas inteiras, **só o destaque entra sozinho e maior**, sombra v3 |
| Final | ~0,45 s depois da última palavra, corte seco para CTA preta digitada (2,9 s) com o **som de teclado padrão** (`assets/cta_teclado.mp3`, enviado pelo usuário em 30/09/2026) sincronizado com a digitação: 1º toque no quadro da 1ª letra, último toque na última letra |
| Voz | −16 LUFS, pico −1 dBTP, limitador suave só nos picos (−14 soava estourado). Ruído externo / gravação "quente" / pedido de "tratar o áudio": **Adobe Podcast** (seção abaixo) |
| Pasta | `Reels Editados/` na raiz do projeto, `<nome do bruto> - EDITADO.mp4` |
| Trabalho | `_trabalho/<slug>/` na raiz do projeto (transcrição, decupagem, legenda, QA) |

**Portão:** o primeiro vídeo de um lote é sempre mostrado ao usuário para validar e lapidar
ANTES de editar os outros. Regra global do usuário: testar a legenda no trecho de fundo mais
claro e mostrar antes de gerar em lote (`qa/fundo_mais_claro.png` sai da conferência).

**Enquadramento (regra do usuário, 28/09):** o recorte fica **fixo** no vídeo todo. Só
reenquadre um trecho se o rosto do Clailton **sair do quadro ou for cortado** pela borda;
fora isso, qualquer reenquadramento é desnecessário. Mudança de zoom da câmera no bruto é
proposital: não iguale o tamanho do rosto nem ofereça "aproximar o trecho".
O `enquadrar.py` só desliza o recorte de uma tomada (`crops_segmento`) quando o rosto fica a
menos de 3% da borda lateral.

**Nunca cortar em cima nem embaixo (regra do usuário, 30/09/2026):** a faixa usa a **altura
cheia do bruto** (zoom 1; do 4K sai 2700×2160). O que o usuário deixou enquadrado na vertical
é intencional — no "Ou você aumenta o seu sacrifício" o zoom automático (rosto a 23% da faixa)
cortou o caderno com as anotações na mesa e foi reprovado. A skill só escolhe a posição
**horizontal** (Clailton bem enquadrado, rosto a ~54% da largura). `--zoom` só com pedido
explícito de aproximar.

**Nada na nuvem:** Gemini, ElevenLabs, TwelveLabs e afins não foram aprovados (mandariam o
vídeo do cliente para fora). Tudo roda neste PC.

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
- Agentes: ficam só em `~/.claude/agents/`, que sincroniza entre os PCs
  (o `verificar.py` confere se estão lá). Se o tipo de agente não estiver disponível na sessão, crie um
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
   `~/.claude/agents/novela-legendista-rapido.md`. Leia `palavras_legenda.txt` e o tempo alinhado de
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
   (~2,5 min): legenda `.ass`, render (6 intermediários sem perda por vez + 1 encode CRF 18) e
   `conferir.py --whisper`, que confere:
   - formato, loudness e pico, CTA (colada no fim da imagem e som de teclado com o 1º toque na 1ª letra, ±1 quadro);
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
- **Áudio estourado / com ruído**: seção "Tratar o áudio no Adobe Podcast".
- **Ver um quadro sem renderizar**: `P S\previa_quadro.py T 12.5,40.2 T\qa\previa.png [--faixa]`.

## Tratar o áudio no Adobe Podcast (ruído externo, gravação quente)

Testado e aprovado no lote de 08/10/2026 (5 vídeos): ruído nas pausas caiu 15–20 dB (de −46/−50 para −65 dB
abaixo da voz), picos colados no teto caíram pela metade, linha do tempo idêntica (atraso 0 ms, correlação 0,97).
O Adobe **limpa ruído**; distorção de gravação muito quente ele só disfarça (usuário, 09/10/2026) — então avise a
equipe para baixar o ganho. Use quando: o usuário pedir ("tratar o áudio", "tirar o ruído", "usar o Adobe"), o
card falar em ruído/barulho externo/áudio estourado, ou `tratar_audio.py medir` disser QUENTE.

1. `P S\tratar_audio.py medir T` — QUENTE = RMS > −24 dBFS ou > 100 amostras acima de −1 dBFS (normal do
   Clailton: RMS −30). Se QUENTE, diga no comentário do card: "gravação com ganho alto; baixar ~10 dB o ganho do
   microfone/câmera".
2. `P S\tratar_audio.py exportar T` → `T\adobe\<slug>.mp3` (mono, 320k, < 10 MB). **Copie o MP3 para a pasta da
   sessão** (ex.: `<pasta da conversa>\_adobe_envio\`): o envio pelo Chrome só aceita arquivos que a sessão lê.
3. Chrome: perfil **"Legacy Executoria"** (equipelegacyexecutoria@gmail.com, `Profile 2` no PC de render; a extensão
   do Claude foi instalada nele em 09/10/2026). Com dois Chromes conectados, `list_connected_browsers` e
   `select_browser` no que abre o Adobe **logado** (canto superior direito com "Meus projetos" e o avatar).
   Abrir: `podcast.adobe.com/pt/enhance` → `find` "file input" → `file_upload` com o MP3 (dá para mandar vários,
   um por chamada; processam juntos, ~30–60 s cada). Ajustes padrão: modelo v2, Fala 50%, Música 10%, Fundo 10%.
4. Baixar: clicar no arquivo na lista (confira a duração no player) → botão **Baixar**. O Chrome dessa conta pergunta
   onde salvar e o arquivo fica como `Downloads\<guid>.tmp` (completo: MP3 mono **64 kbps**, o único formato que o
   Adobe dá; vai até 16 kHz, suficiente para voz). Não espere o diálogo: identifique cada `.tmp` pela duração
   (`ffprobe`) e use direto. No fim, peça ao usuário para fechar as janelas "Salvar como" que ficaram abertas.
5. `P S\tratar_audio.py alinhar T <arquivo>` → `T\audio_tratado.wav` + `T\adobe\relatorio.json`. Reprova se o
   arquivo não casar com o bruto (vídeo trocado).
6. **Remonte o corte** com o áudio limpo: `P S\montar_corte.py T --manter-palavras` (o `borda_voz` passa a medir a voz
   no `audio_tratado.wav`; sem isso o respiro que o Adobe tirou vira silêncio e sobram pausas de 0,4–0,5 s). A legenda
   continua valendo (mesmos índices). Depois `editar.py finalizar` (o render usa o `audio_tratado.wav` sozinho e
   escreve "usando audio_tratado.wav"). Para voltar ao som original: apague `audio_tratado.wav` e remonte.

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
| som de teclado da CTA (arquivo, volume, sincronia) | `render_final.py` (`TECLADO`, `TECLADO_GANHO_DB`, `mixar_teclado`); vale para novela, tela dividida e edição simples. A rajada do arquivo dura o mesmo que a digitação (0,75 s x `CTA_DIGITACAO` 0,76 s): mudou a velocidade da CTA, confira a sincronia. `--sem-teclado` desliga |
| ritmo do corte (silêncio entre frases, pausas, respiro final) | `montar_corte.py` (`SIL_CORTE`, `MARGEM_VOZ_*`, `aparar`; `--sem-aparar` desliga), `borda_voz.py` (limiar pela voz `alto - 26 dB`, tom/vibração `TOM`, `COLADO`), `comum.py` (`FIM_RESPIRO`) |
| ver a onda sonora das pausas e emendas | `ondas.py T [--min 0.15]` → `qa/ondas.txt` + `qa/ondas_01.jpg` (onda + espectro, caixa amarela = silêncio, vermelho = emenda) |
| decupagem automática (frase, tomada repetida, fala para a equipe, dúvida, anáfora) | `decupar_auto.py` (`PAUSA_FRASE`, `SIMIL*`, `META`, regras de DÚVIDA e anáfora) |
| comparação com o roteiro | `roteiro.py` |
| grafia de nomes/termos | roteiro do vídeo e `referencia/grafias.md` |
| enquadramento-alvo | posição horizontal do rosto: `comum.py` (`ROSTO_CX`); altura sempre cheia (`enquadrar.py`, `--zoom` só a pedido) |
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
- **Última palavra da frase sumia** ("comenta GPS" cortado, 2 vezes): o Whisper marcou o fim cedo e a
  fala real passava da janela de busca (`w1 + 0,45 s`), então o `acha_fala` descartava o pedaço
  inteiro. Agora estende até 1,2 s, sem invadir a próxima palavra do bruto (28/09/2026).
- **Gaguejo colado na emenda** ("E... e você sabe", "mas... mas sem destino"): o Whisper estica UMA
  palavra por cima da pausa e o corte emenda as duas. `emendas_literal.py` (roda no `montar` da TD/ES)
  transcreve cada emenda em modo literal e acha "pedaço curto dentro de uma palavra que continua no
  pedaço seguinte"; sugere o `INICIO`/`PARTE`. A conferência da TD/ES não tinha passada literal.
- O `seg` de cada palavra do `palavras_corte.json` vinha do tempo do Whisper; o `alinhar.py` agora
  recalcula pelo tempo alinhado (o zoom por emenda dependia disso).
- Frase paralela tomada por "tomada refeita" (começa com as mesmas 4 palavras e segue diferente): a
  proposta agora marca DÚVIDA em vez de tirar a frase.
- **Espacinho em branco nos cortes** (28/09/2026, "dá para deduzir que ele está lendo"): o envelope de 30 ms
  com limiar pelo piso do bruto (−51 dB) tratava ruído de sala e respiro (−49 dB) como voz, e pausas < 0,30 s
  dentro da frase nunca eram cortadas (17 s de silêncio num reel de 2:36). Agora `borda_voz.py`: 48 kHz,
  5 ms, limiar pela VOZ (−26 dB do volume típico dele), voz = volume OU tom (autocorrelação 70–450 Hz);
  pedaço só de chiado e sem tom sai (respiro/estalo), salvo colado ≤ 30 ms numa palavra (o "s" final).
  Regra só por tom comeu voz fraca ("a partir" → "tir"): não use. Depois de mexer nisso, confira que
  nenhuma palavra sumiu (Whisper no `audio_corte16k.wav` × `palavras_corte.json`).
- **Fim/começo de palavra cortado** (v3, 29/09/2026: "certo", "a rota", "informações", "escolhido", "perguntas"):
  o Clailton solta o "s" final e a soltura da vogal SEPARADOS, fracos (−35 a −45 dB) e sem tom — a regra do
  respiro jogava fora. Diferença física medida: final de palavra = chiado AGUDO (40–97% da energia > 4 kHz);
  respiro/estalo = grave (1–13%). Regras (`borda_voz.py`): pedaço agudo até 0,35 s depois de uma palavra é
  dela; as bordas seguem a ONDA FRACA (`estende`: agudo acima de piso+10 ou som acima de piso+16, sem pular
  buraco > 80 ms, até 0,10 s antes / 0,12 s depois) — é o que o usuário circulou em amarelo na onda;
  o fim da frase pode passar do corte original até 0,40 s se a voz continua (`FIM_EXTRA`), sem chegar na
  próxima palavra do bruto; e cada borda só vai até a METADE da pausa (senão as duas se cruzam e o trecho
  do meio toca duas vezes — pausa maior que a original, 0:15 da v3).
- **Áudio "estourado"** (v3): o bruto já vem com picos no teto (0 dBFS, 3 pontos estourados na gravação);
  subir para −14 LUFS fazia o limitador achatar 4,7% do vídeo em até 4 dB. Padrão agora: **−16 LUFS** e
  limitador suave (attack 7 ms, release 200 ms) só nos raros picos. Dica de gravação: ganho do microfone 3–6 dB
  mais baixo.
- **Legenda "quebrada"** (09/10/2026, 4 vídeos): (a) escada com linha curta ("A", "SE", "AÍ VAI") deixava a
  linha solta, longe das outras — agora linha < 200 px na escada vira **esquerda** sozinha (`ESCADA_LINHA_MIN`,
  aviso "escada com linha curta"); (b) "direita" alinhava a última linha só com a penúltima e ficavam duas bordas
  direitas ("TORCENDO / PARA QUE ELE / NÃO ACONTEÇA") — agora fecha na borda da linha MAIS LARGA. Ao escrever a
  legenda, evite escada com palavra curta solta na 1ª linha (junte "A RESPONSABILIDADE" ou use esquerda).
- **Palavra "cortada" antes da emenda** (09/10/2026: "circo", "manda", "escuta", "grupo"): o corte parava ~37 dB
  abaixo do pico, no meio da soltura da vogal, com saída de 8 ms. Agora `borda_voz.cauda` segue a vogal até o
  silêncio (piso + 6 dB, até `CAUDA_MAX` 0,10 s, parando antes de novo ataque) e o render faz saída suave de 25 ms
  (`FADE_FIM`). As emendas ficam com ~0,10–0,20 s (dentro do 0,10–0,26 s da referência).
- **Falso começo escondido NA PAUSA** ("populi-... popularidade", 09/10/2026): o Whisper juntou tudo numa palavra e o
  `aparar` manteve o pedaço de voz da pausa antes da frase. Sinal: no alinhamento a palavra atravessa a emenda
  (+0,73 s). O `conferir.py` agora reprova "palavra X atravessa a emenda" (> 0,4 s): ouça/olhe e corrija com
  `INICIO n i@t` (t = começo da palavra certa).
- **Palavra do roteiro x Whisper com a terminação diferente** ("comece" x roteiro "começa"; o usuário confirmou
  "começa"): quando só a flexão muda e o som é parecido, confira com `ctc_candidatos.py`; empate → vale o roteiro.
- **Conferência com "E E" na emenda** quando ele fala "e é aí": o Whisper literal tira o acento. É falso alarme:
  ponha `E` em `T\repeticoes_ok.txt`.
- Editar arquivo da skill por script Python dentro do bash: a barra invertida de caminho vira
  caractere de controle (o `\r` de `T\repeticoes` virou quebra de linha). Use as ferramentas de
  edição do Claude ou `chr(92)`, e confira em bytes (modo texto converte CR em LF e esconde o erro).
