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
| Formato | 1080×1920, 29,97 fps, H.264 CRF 18 (~230 MB em 2:40; CRF 10 = 1,2 GB, reprovado: "não pode ser tão pesado"), AAC 320k; voz −14 LUFS / −1 dBTP |
| Imagem | tela cheia 9:16, Clailton centralizado; **aberto** (rosto ~30% da largura) e **fechado** (punch-in 1,5×; 1,25× se o bruto já vem fechado) — ver "Zoom" abaixo |
| Corte | colado na voz; **nenhuma palavra repetida nas emendas** (checagem literal automática) |
| Legenda | a da novela (caixa-alta, 1–3 linhas, destaque maior sozinho, layouts centro/esquerda/escada/direita, sombra v3), com o centro do bloco a ~52% da altura (peito) e nunca em cima do queixo |
| Sem | imagens de apoio, abertura dividida, flash, película, música |
| Final | CTA preta digitada (a da novela) com clique de teclado |
| Pasta | `Reels Editados/<nome> - EDITADO.mp4`; trabalho em `_trabalho/<slug>/` |

## Zoom (regras do usuário, correção de 28/09/2026 — "os zooms estão ruins, sem timing")

1. **Zoom seco só na emenda (corte).** Cada pedaço do corte tem UM enquadramento; aberto ↔ fechado só
   troca no quadro exato da emenda. Nunca no meio da fala contínua.
2. **Zoom fora da emenda só animado (keyframes)**, com entrada e saída suaves: aproximação de ~18% em
   0,55 s no rabo da frase que fecha o pedaço, segurando até a emenda (`Z` no `timeline.txt`).
3. **Todo zoom mantém os olhos na mesma altura**: o zoom amplia em volta do ponto entre os olhos
   (YuNet, medido a cada 0,5 s). Como ele mexe a cabeça, cada fechado é posicionado para os olhos
   entrarem na linha em que estavam no fim do plano anterior e saírem na linha do começo do seguinte,
   com um ajuste animado discreto dentro do fechado (keyframes suaves, ≤ 150 px e ≤ 60 px/s). O que a
   cabeça mudar além disso fica como aviso "olhos: ..." no `timeline.txt`. Conferência:
   `qa/zoom_olhos.jpg` (6 piores trocas, linha vermelha nos olhos) — no "Dirigir uma empresa sem GPS"
   a diferença mediana caiu de ~70 px para ~30 px (de 1920).

Vale também na tela dividida (pedido do usuário). Como decide (`plano_td.auto_zoom_cortes`, padrão;
a linha `ZOOMLIVRE` no plano volta ao fechado antigo, reprovado):
emenda de tomada (trecho novo ou pulo ≥ 1 s no bruto) troca o zoom e esconde o pulo; pedaço que é
frase curta de fecho ("A rota.", "Pensa comigo.") vai para o fechado; o fechado volta ao aberto na
emenda seguinte; aberto por mais de 7 s fecha na 1ª emenda boa; nenhum plano < 0,6 s; zoom animado
só em pedaço aberto ≥ 3 s, com pelo menos 6 s entre dois, e nunca com fechado logo depois (< 3 s).
Confira em `T\timeline.txt` (linha "planos do Clailton": A, F, Z) antes do render.

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
   `SEMZOOM` desliga o aberto/fechado automático.
6. **Olhar** — `T\qa\fundo_mais_claro.png`, `T\qa\zoom_olhos.jpg`, `T\qa\relatorio.txt` (e
   `folha_geral_NN.jpg` no 1º do lote).
7. **Entregar** — vídeo + relatório curto: tempo por etapa, diferenças fala × roteiro, decisões a confirmar.

Correções: texto da legenda → `legenda.txt` + `finalizar`; enquadramento → `plano.txt` + `finalizar`;
trocar tomada → decupagem → `montar` → revisar a legenda (os índices mudam) → `finalizar`.
Sem a pasta de trabalho da versão anterior (ela ficou em outro PC): refaça do bruto já com as correções.

## Onde ajustar

| O quê | Onde |
| --- | --- |
| altura da legenda (peito) | `es.py`: `Y_CENTRO` (1010), `TOPO_MIN`, `BASE_MAX`; queixo: `QUEIXO_FATOR` |
| aberto/fechado | tela dividida: `td_comum.py` (`ROSTO_ABERTO`, `FECHADO_FATOR`) e `plano_td.py` |
| regra do zoom na emenda / zoom animado | `plano_td.py` (`auto_zoom_cortes`) e `td_comum.py` (`ZOOM_SUAVE`, `ZOOM_SUAVE_RAMPA`, `ZOOM_SUAVE_INTERVALO`, `PLANO_MIN`, `FECHADO_MAX`, `ABERTO_MAX`) |
| olhos na mesma altura | `td_comum.py` (`rect_zoom`, `rect_plano`, `OLHOS_AJUSTE_MAX`, `OLHOS_AJUSTE_PS`); `plano_td.py` (`olhos_na_linha`); olhos medidos em `enquadrar_td.py`; conferência `olhos_qa.py` |
| palavra repetida na emenda | novela: `emendas_literal.py` (`JANELA`, `fragmentos`) |
| legenda (tamanhos, sombra, CTA) | novela: `legenda_novela.py` (vale para as duas skills) |
