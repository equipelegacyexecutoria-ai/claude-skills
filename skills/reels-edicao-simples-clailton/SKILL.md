---
name: reels-edicao-simples-clailton
description: Edita reels no formato EDIÇÃO SIMPLES (ES) do Clailton (Legacy Educação) a partir do bruto e do roteiro — vertical 1080x1920 em tela cheia (sem barras pretas e sem imagens de apoio), Clailton centralizado com aberto/fechado (punch-in) automático, corte colado na voz, legenda da NOVELA (SF Pro Text Black, telas de 1–3 linhas, destaque maior entrando sozinho, sombra v3) na altura do peito e CTA final "ME SIGA PARA MAIS CONTEÚDOS COMO ESTE" digitada. Use sempre que o pedido for editar um reel "ES"/"edição simples" do Clailton, arquivos ou cards Reels_Clailton_ES_*, ou "edita igual ao reel do colaborador que reclama da empresa".
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
| Formato | 1080×1920, 29,97 fps, H.264 CRF 10, AAC 320k; voz −14 LUFS / −1 dBTP |
| Imagem | tela cheia 9:16, Clailton centralizado; **aberto** (rosto ~30% da largura) e **fechado** (punch-in 1,5×) por corte seco, fechado nos fechos de frase e depois de emenda de tomada (automático) |
| Legenda | a da novela (caixa-alta, 1–3 linhas, destaque maior sozinho, layouts centro/esquerda/escada/direita, sombra v3), com o centro do bloco a ~52% da altura (peito) e nunca em cima do queixo |
| Sem | imagens de apoio, abertura dividida, flash, película, música |
| Final | CTA preta digitada (a da novela) com clique de teclado |
| Pasta | `Reels Editados/<nome> - EDITADO.mp4`; trabalho em `_trabalho/<slug>/` |

**Portão:** o 1º vídeo de um lote é mostrado ao usuário antes dos outros (com `--geral`), com
`qa/fundo_mais_claro.png` (regra global da sombra). Na fila de render, o portão é a coluna de aprovação.

## Ambiente

As mesmas venvs da novela/tela dividida: `P = %LOCALAPPDATA%\corte-viral\venv\Scripts\python.exe`
(ou `%LOCALAPPDATA%\reels-novela\venv\...`), sempre com `PYTHONUTF8=1`. `S = ~/.claude/skills/reels-edicao-simples-clailton/scripts`.

## Modo rápido — ~8–12 min por vídeo

`T = <projeto>\_trabalho\<slug>`. Salve o roteiro em `T\roteiro.txt` (ou `.docx`/`.md`) antes.

1. **Preparar** — `P S\es.py preparar "<bruto>" T` (transcrição na GPU + decupagem automática).
2. **Revisar a decupagem** — como na novela (`decupagem_proposta.txt` → `decupagem_ajustes.txt` →
   `P <novela>\scripts\decupar_auto.py T --aplicar T\decupagem_ajustes.txt`).
3. **Montar** — `P S\es.py montar T` (corte na voz + alinhamento + rotação + aberto/fechado).
4. **Legenda (você)** — leia `T\palavras_legenda.txt` (+ `roteiro_x_fala.txt`) e escreva `T\legenda.txt`
   no formato compacto da novela (ver `~/.claude/agents/novela-legendista-rapido.md` e
   `reels-novela-clailton/referencia/legenda-aprovada-video1.txt`). Plano visual **não** é preciso.
5. **Finalizar** — `P S\es.py finalizar T "<projeto>\Reels Editados\<nome> - EDITADO.mp4" [--geral]`
   (medido no teste de 18 s: render 41 s, conferência 38 s). Código 0 = aprovado.
   Sem `T\plano.txt`, ele cria um com `SEMABERTURA`. Para forçar o enquadramento de um trecho,
   acrescente ao plano `FECHADO @a-b` ou `ABERTO @a-b`; `SEMZOOM` desliga o aberto/fechado automático.
6. **Olhar** — `T\qa\fundo_mais_claro.png`, `T\qa\relatorio.txt` (e `folha_geral_NN.jpg` no 1º do lote).
7. **Entregar** — vídeo + relatório curto: tempo por etapa, diferenças fala × roteiro, decisões a confirmar.

Correções: texto da legenda → `legenda.txt` + `finalizar`; enquadramento → `plano.txt` + `finalizar`;
trocar tomada → decupagem → `montar` → revisar a legenda (os índices mudam) → `finalizar`.

## Onde ajustar

| O quê | Onde |
| --- | --- |
| altura da legenda (peito) | `es.py`: `Y_CENTRO` (1010), `TOPO_MIN`, `BASE_MAX`; queixo: `QUEIXO_FATOR` |
| aberto/fechado | tela dividida: `td_comum.py` (`ROSTO_ABERTO`, `FECHADO_FATOR`) e `plano_td.py` |
| legenda (tamanhos, sombra, CTA) | novela: `legenda_novela.py` (vale para as duas skills) |
