---
name: motion-tutorial
description: Faz vídeo TUTORIAL em motion (passo a passo de como usar uma plataforma, site ou app) no estilo Legacy aprovado em 18/11/2026: fundo claro com azul, telas da plataforma redesenhadas IGUAIS às reais (ícones, botões, cores copiados da conta teste), setinha (computador) ou dedo (celular) clicando com calma, câmera que aproxima e para no botão, contorno azul pulsando onde olhar, barra fixa "PASSO n DE N", narração feminina (Lívia) com pausas curtas, música comercial do Artlist ~11 dB abaixo da voz. Sai em duas versões, computador 16:9 e celular 9:16, a partir de gravações de tela do usuário. Use sempre que pedirem "tutorial", "vídeo tutorial", "passo a passo em vídeo", "ensinar a usar a plataforma", "como entrar na aula", "como acessar o Legacy Plan", "vídeo explicativo de tela para alunos/clientes", "motion tutorial", ou mandarem gravação de tela pedindo um vídeo que ensine o caminho. Para anúncio/venda use motion-legacy; para fala do Clailton ilustrada use motion-dinamico.
---

# Motion Tutorial (passo a passo em motion, computador + celular)

Modelo aprovado: "Como entrar nas aulas do Legado pelo Legacy Plan" (18/11/2026, v3). O que ele aprovou e reprovou em
cada versão está em `references/licoes.md`: **leia antes de começar**. Quadros do vídeo aprovado:
`references/folha_computador.jpg` e `references/folha_celular.jpg`. Roteiro, passos e pausas aprovados:
`exemplo/roteiro_aulas_legado.md`.

O usuário não é técnico: fale pelo resultado ("a setinha clica em Ver detalhes e a câmera aproxima"), nunca por código.
Base de ferramentas e regras gerais (créditos, área segura, Artlist): skill `motion-designer`. Estilo visual: skill
`motion-legacy` (este tutorial usa a mesma gramática, mais devagar e educativa).

## A gramática do tutorial

| Elemento | Como é |
| --- | --- |
| Versões | **computador** 1920x1080 (navegador com a plataforma) e **celular** 1080x1920 (celular com o app). Mesma narração, trocando "clique" por "toque" |
| Abertura | letreiro palavra a palavra: "Tem novidade para você!" → o que mudou → **ANTES** (o jeito antigo, em cartões que ficam cinza) → **AGORA** (logo da plataforma girando) → "Vou te mostrar o passo a passo pelo computador/celular" |
| Passo a passo | uma ação por vez: a câmera aproxima e **para** no ponto, contorno azul pulsando no que importa, setinha (computador) ou dedo cinza (celular) vai até o botão e clica com onda azul. Barra fixa "PASSO n DE N · Clique em **Botão**" (embaixo no computador, em cima no celular, fora da área do Instagram) |
| Telas | redesenhadas em HTML **iguais às reais**: mesmos ícones (Lucide, em `scripts/icones.py`), cores, raios, fontes (Urbanist) e textos da plataforma. Nomes fictícios (Sua Empresa, Marcos Lima). Nunca dado de cliente |
| Ritmo | pausas entre passos de 0,15 a 0,6 s e fala 6% mais rápida (`atempo=1.06`). Cerca de 75 a 80 s para 6 a 7 passos. Mais lento foi reprovado |
| Voz | Lívia Moreira (Magnific `audio_tts`, voz 611). Gasta créditos: pedir o "sim" com o custo (`simulate_cost`), uma tomada por versão |
| Música | uma só, comercial e com batida (Artlist; aprovada: "Adaptive Flow", Kerei), crescendo na palavra "Agora". ~11 dB abaixo da voz. Piano calmo = "música de elevador", reprovado |
| Efeitos | baixos: whoosh nas viagens da câmera, clique suave em cada clique, um "data click" nos avisos de sucesso, logo no fecho |
| Fecho | "Nos vemos no próximo encontro!" (ou equivalente) + logo Legacy Executoria e linha azul |

## Processo

1. **Entender o caminho.** O usuário manda gravações de tela (computador e celular), em geral com a narração dele.
   Link do Drive sem acesso nesta conta: abra pelo Chrome dele (Claude in Chrome), dê play e leia a **Transcrição** do
   próprio Drive (botão "Transcrição"; o texto sai pelo `javascript_tool`) + prints a cada ~4 s. Liste os passos, os
   botões e os textos exatos de cada tela.
2. **Copiar as telas reais.** No Chrome dele, na conta teste da plataforma (ele avisa quando logar), abra cada tela e janela
   e leia estilos e ícones pela página (`javascript_tool`): para cada elemento, tamanho, `font-size/weight`, cor, fundo,
   raio, borda e o nome do ícone (`class` com `lucide-...`). A saída com `=`/`;` é bloqueada como "cookie": troque esses
   caracteres antes de devolver (ex.: `≡`, `¦`) e devolva em pedaços curtos. Faça `zoom` da janela para ter a imagem.
   Botão que grava algo (check-in, enviar, pesquisa de satisfação): **não clique**; abrir e fechar janela pode.
   Ícone novo: acrescente o desenho em `scripts/icones.py` (mesmo traço da Lucide).
3. **Roteiro** (antes de gastar crédito). Escreva a narração das duas versões com as skills `escrita-sem-cara-de-ia` e
   `humanizer-pt-br`, a lista de passos da barra e o que aparece em cada um. Mostre e só siga com o "ok".
4. **Projeto:** `python ~/.claude/skills/motion-tutorial/scripts/novo_tutorial.py "<pasta>" ambos` (cria `computador/` e
   `celular/` com `modelo.html`, `k.json`, `audio/`, `projeto/`). O `modelo.html` vem com o tutorial das aulas inteiro:
   troque as telas e os passos pelos do caminho novo, reaproveitando as funções (ver "Peças do molde").
5. **Voz → pausas → tempos** (em cada versão):
   - gerar a voz (com autorização) e salvar `audio/voz_bruta.mp3`;
   - tempos da voz bruta: `python ~/.claude/skills/motion-legacy/scripts/palavras_js.py audio/voz_bruta.mp3 --inicio 0`;
   - pausas curtas no fim das frases de passo, encaixadas no silêncio:
     `python ~/.claude/skills/motion-tutorial/scripts/pausas.py audio/voz_bruta.mp3 audio/voz_p.wav 12:0.15 22:0.3 ...`
     (índice da palavra:segundos, ou `t<segundo>:<pausa>` para cortar num tempo); depois
     `ffmpeg -i audio/voz_p.wav -af atempo=1.06 audio/voz.wav`;
   - tempos finais: `palavras_js.py audio/voz.wav --inicio 0.25 --prompt "<nomes da plataforma>"`;
   - preencha `k.json` (palavra-chave → índice; exemplos em `exemplo/k_*.json`) e rode
     `python ~/.claude/skills/motion-tutorial/scripts/montar.py <pasta>/computador` (idem celular).
   - **Whisper inventa frase nas pausas** (aconteceu duas vezes): palavra repetida ou frase que não está no roteiro =
     confira o trecho isolado (corte 4 s e transcreva). Se o áudio estiver certo, tire as palavras inventadas com
     `"remover"` no `k.json`.
6. **Conferir em quadros antes do áudio final:** `npx --yes hyperframes@0.8.162 lint` e
   `snapshot --no-end -o ../qa/vN --at <um momento por passo>`. Telas no ponto, contorno no lugar certo, nada atrás da
   barra do passo. Quadro no meio de uma transição sai torto: confira o quadro com a câmera já parada.
7. **Música e mixagem.** Música do Artlist pelo Chrome **deste PC** (o arquivo precisa cair aqui; pelo Chrome de outro PC
   ele fica lá). O Artlist pode deixar o download como `.tmp` em Downloads: o `.tmp` inteiro é o MP3. Meça a energia
   (librosa/ebur128) para achar onde ela cresce. Tempos dos cliques: abra a página por um servidor local (Browser pane,
   `launch.json` com `python -m http.server`) e leia `window.__CLIQUES`. Depois:
   `python ~/.claude/skills/motion-tutorial/scripts/gerar_mix.py <pasta>/computador --musica <mp3> --cliques "<tempos>" --virada <s>`.
8. **Render:** `npx --yes hyperframes@0.8.162 render --quality high --fps 30 -o renders/<nome>_vN.mp4` (~1 min 15 s por
   versão). Folha de quadros do MP4 + transcrição da mixagem (a voz tem que sair igual ao roteiro).
9. **Mostrar antes de trocar.** Mudança visual pedida: aplique, tire os quadros e **mande as imagens** (depois e, se ele
   pedir, antes) antes de renderizar. Só renderize com o "pode".
10. **Entrega:** pasta no Drive (EDITADO do mês, `G:\Meu Drive\02. Captação de Vídeos\<AAAA>\<MM - Mês>\ORGÂNICO\EDITADO\<Nome do tutorial>`)
   com os dois vídeos, e o link da pasta na conversa (`search_files` acha o id depois que o Drive sincroniza). Correção:
   copie por cima com o mesmo nome (o link não muda). Sala de Revisão só se tiver espaço (skill `sala-de-revisao`).

## Peças do molde (`molde/computador/modelo.html` e `molde/celular/modelo.html`)

- `grupo(top, linhas, saida)`: letreiro palavra a palavra no tempo da voz (classes `sm`, `big`, `xl`, `dim`, `hl` marca azul, `rs` risco).
- `passo(t, n, "Clique em <b>Botão</b>")`: troca a barra fixa do passo (total: `NP`).
- Computador: `vai(t, x, y)` leva a setinha; `clica(t, x, y)` clica com onda (coordenadas dentro do navegador `#bw`).
  Celular: `vai`/`toca` com o dedo (coordenadas dentro da tela do celular).
- `aneis(t, x, y, w, h, fim)`: contorno azul pulsando num elemento.
- `foco(t, escala, px, py, dur, ax, ay)`: câmera aproxima no ponto (px, py) da cena e para; `geral(t)` volta ao quadro inteiro.
  `viagem(t, "cena")`: linha azul com a setinha levando de uma cena à outra (abertura e fecho).
- `mostra`/`some`/`aparece`/`esconde`/`digita(el, "texto", t, dur)` para janelas, avisos e campos.
- Cenas prontas: ANTES (mensagem com link + janela do Zoom), AGORA (logo girando), navegador/celular com o Legacy Plan
  (Cockpit, card Próxima aula, janela de detalhes com check-in, aviso "Check-in registrado", janela "Quem está assistindo?"
  com opção, marcar, digitar e adicionar), conectando, Zoom (permissão, Join, galeria) e fecho com logo.

## Armadilhas já resolvidas

- `fromTo` de elemento que aparece depois: use `immediateRender: false` e deixe o elemento com `class="oculto"`.
- Janela que cresce (opção ligada): anime `height` da caixa e da janela e empurre o que vem embaixo com `y`.
- Texto que muda (2 pessoas, 3 pessoas): tenha um `span` por estado e troque com `esconde`/`aparece`, não reescreva texto.
- App no celular sem fundo deixa ver a tela de abertura atrás: o `#app` precisa de `background`.
- Zoom muito grande no celular joga a janela para baixo da barra do passo: mantenha o topo da janela abaixo de y ~420.
- Script Python grande com aspas: escreva num arquivo `.py` (heredoc do bash quebra com aspas e acentos).
