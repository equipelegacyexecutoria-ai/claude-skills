---
name: reels-edicao-simples-clailton
description: Edita reels no formato EDIÇÃO SIMPLES (ES) do Clailton (Legacy Educação) a partir do bruto e do roteiro — vertical 1080x1920 em tela cheia (sem barras pretas e sem imagens de apoio), Clailton centralizado com aberto/fechado automático (zoom seco só na emenda, zoom animado fora dela, olhos sempre na mesma altura), corte colado na voz sem palavra repetida nas emendas, legenda da NOVELA (SF Pro Text Black, telas de 1–3 linhas, destaque maior entrando sozinho, sombra v3) na altura do peito e CTA final "ME SIGA PARA MAIS CONTEÚDOS COMO ESTE" digitada. Use sempre que o pedido for editar um reel "ES"/"edição simples" do Clailton, arquivos ou cards Reels_Clailton_ES_*, ou "edita igual ao reel do colaborador que reclama da empresa".
---

# Reels EDIÇÃO SIMPLES (ES) do Clailton

Referência: https://www.instagram.com/p/DdHziJUhn0N/ (cópia e quadros em
`Desktop\Projetos Edições\Reels Edição Simples\_referencia\`, no PC do Anderson).

A ES é a mistura das outras duas skills — não há código de edição próprio além do `scripts/es.py`:
- **corte, alinhamento, rotação da câmera deitada e aberto/fechado**: `reels-tela-dividida-clailton`
  (sem imagens, sem abertura dividida, sem película);
- **legenda**: `reels-novela-clailton` (mesmo `legenda.txt` compacto, mesmas regras de telas e destaques);
- **render e conferência**: os da tela dividida.
Regras de decupagem, grafia, destaques, ritmo (nada de pausa dramática) e "nada na nuvem": SKILL da novela.

## O entregável

| Item | Padrão |
| --- | --- |
| Formato | 1080×1920, 29,97 fps, H.264 CRF 18 (~230 MB em 2:40; CRF 10 = 1,2 GB, reprovado: "não pode ser tão pesado"), AAC 320k; voz −16 LUFS / −1 dBTP (limitador suave) |
| Imagem | tela cheia 9:16, Clailton centralizado; **aberto** (rosto ~30% da largura) e **fechado** (punch-in 1,5×; 1,25× se o bruto já vem fechado) — ver "Zoom" abaixo |
| Corte | colado na voz; **nenhuma palavra repetida nas emendas** (checagem literal automática) |
| Legenda | a da novela (caixa-alta, 1–3 linhas, destaque maior sozinho, layouts centro/esquerda/escada/direita, sombra v3), com o centro do bloco a ~57% da altura (peito; era 52%, o usuário pediu mais baixa em 28/09/2026) e nunca em cima do queixo |
| Sem | imagens de apoio, abertura dividida, flash, película, música |
| Final | CTA preta digitada (a da novela) com o **som de teclado padrão** da novela (`reels-novela-clailton/assets/cta_teclado.mp3`, usuário 30/09/2026) sincronizado com a digitação (1º toque na 1ª letra) |
| Pasta | `Reels Editados/<nome> - EDITADO.mp4`; trabalho em `_trabalho/<slug>/` |

## Zoom (regras do usuário, correção de 28/09/2026 — "os zooms estão ruins, sem timing")

1. **Zoom seco só na emenda (corte).** Cada pedaço do corte tem UM enquadramento; aberto ↔ fechado só
   troca no quadro exato da emenda. Nunca no meio da fala contínua.
2. **Zoom fora da emenda só animado (keyframes)**, com entrada e saída suaves: aproximação de ~18% em
   0,55 s no rabo da frase que fecha o pedaço, segurando até a emenda (`Z` no `timeline.txt`).
3. **Olhos na linha padrão no corte** (2ª correção, 28/09/2026 — palavras do usuário: "quando tem o
   corte, a gente continua olhando para o mesmo ponto da tela esperando encontrar os olhos"):
   - **enquadramento padrão = o aberto (original, sem zoom)**, no vídeo inteiro;
   - **linha padrão dos olhos** = a altura mediana dos olhos nesse aberto (`linha_olhos` no timeline);
   - no corte que entra no zoom, o fechado é posicionado **só na altura** para os olhos do **1º quadro
     depois do corte** caírem na linha padrão (medidos no quadro exato do bruto, YuNet);
   - **na lateral, não segue a cabeça**: fechado centrado no aberto (seguir a lateral cortou o rosto
     em 0:49–0:52 na v2);
   - o fechado fica **parado** até o próximo corte (nada de ajuste no meio do plano); na volta, o
     aberto padrão (os olhos já estão na altura padrão);
   - **trava da testa**: se, com os olhos na linha, ele levantar a cabeça no plano e os olhos subirem
     acima de 20% da altura (`OLHO_MIN_FECHADO`), esse trecho fica no aberto padrão (aviso "virou
     aberto"). No "GPS" foram 4 fechados longos (v2 cortou a testa em 0:49).
   Conferência: `qa/zoom_olhos.jpg` (6 entradas de zoom mais longe da linha; linha vermelha = padrão).

Vale também na tela dividida (pedido do usuário). Como decide (`plano_td.auto_zoom_cortes`, padrão;
a linha `ZOOMLIVRE` no plano volta ao fechado antigo, reprovado):
emenda de tomada (trecho novo ou pulo ≥ 1 s no bruto) troca o zoom e esconde o pulo; pedaço que é
frase curta de fecho ("A rota.", "Pensa comigo.") vai para o fechado; o fechado volta ao aberto na
emenda seguinte; aberto por mais de 7 s fecha na 1ª emenda boa; nenhum plano < 0,6 s; zoom animado
só em pedaço aberto ≥ 3 s, com pelo menos 6 s entre dois, e nunca com fechado logo depois (< 3 s).
Confira em `T\timeline.txt` (linha "planos do Clailton": A, F, Z) antes do render.

**Lições da v3 → v4 (29/09/2026) — não repetir:**
- **Zoom só em corte VISÍVEL** (troca de trecho ou pulo ≥ 0,35 s no bruto, `CORTE_VISIVEL`). Os microcortes do
  "aparar" (0,07–0,17 s de respiro) não trocam zoom: ali a imagem quase não pula e o zoom parece "no meio da
  fala" (0:33 e 1:21 da v3). Fechados colados por microcorte usam o MESMO recorte; zoom animado que atravessa
  microcorte usa o mesmo centro.
- **Cabeça nunca cortada:** o bruto do Clailton tem ~5% de espaço acima da careca; com os olhos na linha e
  1,25× o topo sai. O zoom de cada trecho fechado é reduzido até o **topo real da cabeça** caber (3% de folga).
  O topo é medido na imagem (`td_comum.topo_cabeca`: onde a cor de pele acaba acima dos olhos, no 1º quadro,
  a cada 0,5 s e no fim do trecho). Estimar pela largura do rosto falhou quando ele se inclina ou olha para
  baixo. Menos de 1,10× → o trecho fica no aberto.
- Conferência visual obrigatória: folha com 1º/meio/fim de cada fechado (cabeça) e `ondas.py` (cortes).

**Portão:** o 1º vídeo de um lote é mostrado ao usuário antes dos outros (com `--geral`), com
`qa/fundo_mais_claro.png` (regra global da sombra). Na fila de render, o portão é a coluna de aprovação.

## Ambiente

As mesmas venvs da novela/tela dividida: `P = %LOCALAPPDATA%\corte-viral\venv\Scripts\python.exe`
(ou `%LOCALAPPDATA%\reels-novela\venv\...`), sempre com `PYTHONUTF8=1`. `S = ~/.claude/skills/reels-edicao-simples-clailton/scripts`.

## Modo rápido — ~8–12 min por vídeo

`T = <projeto>\_trabalho\<slug>`. Salve o roteiro em `T\roteiro.txt` (ou `.docx`/`.md`) antes.

1. **Preparar** — `P S\es.py preparar "<bruto>" T` (transcrição na GPU + decupagem automática).
2. **Revisar a decupagem** — como na novela (`decupagem_proposta.txt` → `decupagem_ajustes.txt` →
   `P <novela>\scripts\decupar_auto.py T --aplicar T\decupagem_ajustes.txt`). Sem roteiro, confira
   com atenção redobrada (lições do "Dirigir uma empresa sem GPS", 28/09/2026):
   - frase que **começa igual** a outra mas **segue diferente** é paralela, não tomada ("Você sabe
     exatamente onde ela está hoje?" × "E você sabe exatamente onde você quer chegar?"): FICA. A
     proposta agora marca DÚVIDA nesses casos;
   - frase com vários recomeços dentro ("mas sem destino, meu amigo / mas sem destino e sem rota você
     pode / mas sem destino e sem rota você pode estar...") → `INICIO` no último recomeço;
   - "⚠ falso começo escondido" nem sempre é tropeço: "Não crescer, não faturar mais" e "O estado
     atual, o estado desejado" são enumerações — não corte;
   - na dúvida, escute o trecho com Whisper literal (janela curta) e olhe a energia antes de decidir.
3. **Montar** — `P S\es.py montar T` (corte na voz + alinhamento + rotação + aberto/fechado +
   **checagem literal das emendas**). "REPETIÇÃO NA EMENDA" = gaguejo colado no corte ("E... e você
   sabe"): junte o ajuste sugerido de `T\emendas_literal.txt` ao `decupagem_ajustes.txt`, `--aplicar`
   e `montar` de novo. O `finalizar` repete a checagem e **não renderiza** enquanto houver repetição
   (repetição intencional → `T\repeticoes_ok.txt`).
4. **Legenda (você)** — leia `T\palavras_legenda.txt` (+ `roteiro_x_fala.txt`) e escreva `T\legenda.txt`
   no formato compacto da novela (ver `~/.claude/agents/novela-legendista-rapido.md` e
   `reels-novela-clailton/referencia/legenda-aprovada-video1.txt`). Plano visual **não** é preciso.
5. **Finalizar** — `P S\es.py finalizar T "<projeto>\Reels Editados\<nome> - EDITADO.mp4" [--geral]`
   (medido no teste de 18 s: render 41 s, conferência 38 s). Código 0 = aprovado.
   Sem `T\plano.txt`, ele cria um com `SEMABERTURA`. Para forçar o enquadramento, acrescente ao plano
   `FECHADO @a-b` ou `ABERTO @a-b` (vale para o pedaço inteiro entre emendas em que ele cai);
   `SEMZOOM` desliga o aberto/fechado automático. `ZOOMSUAVE @a-b [x1.18]` dá zoom in suave só naquela frase (aproxima até o fim dela e volta na emenda seguinte), vale mesmo com `SEMZOOM` (pedido do usuário, 26/10/2026).
6. **Olhar** — `T\qa\fundo_mais_claro.png`, `T\qa\zoom_olhos.jpg`, `T\qa\relatorio.txt` (e
   `folha_geral_NN.jpg` no 1º do lote).
7. **Entregar** — vídeo + relatório curto: tempo por etapa, diferenças fala × roteiro, decisões a confirmar.

Correções: texto da legenda → `legenda.txt` + `finalizar`; enquadramento → `plano.txt` + `finalizar`;
trocar tomada → decupagem → `montar` → revisar a legenda (os índices mudam) → `finalizar`.
Sem a pasta de trabalho da versão anterior (ela ficou em outro PC): refaça do bruto já com as correções.

## Onde ajustar

| O quê | Onde |
| --- | --- |
| altura da legenda (peito) | `es.py`: `Y_CENTRO` (1100), `TOPO_MIN`, `BASE_MAX`; queixo: `QUEIXO_FATOR` |
| aberto/fechado | tela dividida: `td_comum.py` (`ROSTO_ABERTO`, `FECHADO_FATOR`) e `plano_td.py` |
| regra do zoom na emenda / zoom animado | `plano_td.py` (`auto_zoom_cortes`) e `td_comum.py` (`ZOOM_SUAVE`, `ZOOM_SUAVE_RAMPA`, `ZOOM_SUAVE_INTERVALO`, `PLANO_MIN`, `FECHADO_MAX`, `ABERTO_MAX`) |
| olhos na mesma altura | `td_comum.py` (`rect_zoom`, `rect_plano`); `plano_td.py` (`olhos_na_linha`, `Olhos`); olhos medidos em `enquadrar_td.py`; conferência `olhos_qa.py` |
| palavra repetida na emenda | novela: `emendas_literal.py` (`JANELA`, `fragmentos`) |
| legenda (tamanhos, sombra, CTA) | novela: `legenda_novela.py` (vale para as duas skills) |

## Correções de 20/10/2026 (lote "6 maiores medos" e "A vida é uma festa")

- **Legenda "pulando" / "vai lá pra baixo"** (usuário: "tem que ficar pela mesma região, não pode acontecer essas
  quebras brutas"): a medida dos olhos tinha picos falsos (mão na frente, cabeça virando) e o queixo calculado caía
  fora da tela. Agora (`es.py rosto_no_quadro`): mediana de 1,5 s, olhos no máximo 0,35 x rosto abaixo do normal, UM
  valor por plano (a legenda só muda de altura na emenda) e sem amostra nos 0,2 s iniciais do plano. `BASE_MAX` 1480
  (área segura do Instagram; era 1680).
- **Enquadramento pulando em microcorte** ("não aproximou mas parece ter posto o vídeo mais pra cima"): cada segmento
  tinha o próprio aberto; agora o aberto parado continua com o mesmo recorte até o próximo corte visível
  (`plano_td.py`). Para dar zoom num trecho que não começa em corte visível, force o pedaço inteiro entre dois cortes.
- `FECHADO @a-b x1.45` no `plano.txt`: punch-in escolhido sobre o aberto (o limite da cabeça continua valendo). Com
  zoom muito forte (1,7x) o queixo desce e a legenda não cabe abaixo dele antes de 1480: use ~1,45x.
- Realce baixo do bruto (IDEIA "diminuir os realces"): curva `0/0 0.5/0.5 0.7/0.67 0.85/0.79 1/0.93` (ver
  `C:\Render\_trabalho\realce_2026-10-20.sh` no PC de render) -> `<slug>_REALCE.mov`, que vira a fonte.

## Correções de 22/10/2026 ("6 maiores medos" v3: notas da Sala)

- **"Enquadramento errado, use o mesmo padrão"** (fechado em que ele se inclina para a câmera logo depois do corte e a
  cabeça desce): o fechado continua parado, mas quando a mediana dos olhos no trecho fica mais de 150 px ABAIXO da do
  1º quadro, o recorte usa a mediana (`plano_td.py`, `OLHO_DERIVA`; aviso "posicionado pela mediana do trecho").
  Só para baixo: subir não deixa o quadro vazio em cima.
- **Música:** na v3 entrou trilha (pedida numa nota) e na v4 o usuário mandou **retirar** ("deixar somente a animação e o
  efeito sonoro"): ES fica SEM música; animação e efeito sonoro pontuais podem. Se pedirem música de novo,
  mixe DEPOIS do render, sobre o vídeo pronto: tira a voz (`ffmpeg -vn`), `motion-designer/scripts/mix_audio.py`
  (exemplo em `scripts/exemplo_mix_musica.json`) e junta com `-c:v` do vídeo. Vídeo com virada (medos → "então
  comece"): duas trilhas (regra global), tensa antes e épica com o pico do arquivo no quadro da virada
  (`analisar_audio.py` + envelope de 10 ms para achar o pico exato). Trilhas já baixadas do Artlist no PC de render:
  `C:\Render\motion_ref\cerebro\musicas\`. Nível medido: tensa ~10 dB abaixo da voz, épica ~8 dB (a 15 dB "some").
  A conferência acusa "teclado da CTA fora" por causa das batidas da música: confira o atraso por correlação com a voz.
- **Animação em cima da cabeça** (relógio no "60 segundos"): `scripts/relogio_animado.py <pasta> <duração>` gera os
  quadros RGBA (cronômetro Legacy com ponteiro correndo, arco enchendo, sombra v3, entra/sai com escala) e o
  `tique_taque.wav` sintetizado; overlay com `setpts=PTS+<quadro>/(30000/1001)/TB` entre a palavra e o corte seguinte
  (mínimo 1 s). Topo do Reels: nada acima de y 250 (o relógio ficou em y 269–463).
