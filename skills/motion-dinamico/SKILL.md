---
name: motion-dinamico
description: "Faz vídeos no estilo MOTION DINÂMICO: reel vertical 1080x1920 em que a fala de um especialista (Clailton ou outro) vira animação moderna na identidade da Legacy, com o especialista só ~10% do tempo num cartão de contorno azul e o resto ilustrado palavra a palavra. Fundo azul-marinho com brilho, ícones e pessoas 3D recortados com borda branca (Freepik pelo Chrome), cartões e selos com contorno azul luminoso, polaroid com alfinete, linha do tempo luminosa, carimbos azuis preenchidos, e a fala inteira em texto animado tipo Helvetica (sem legenda), cada palavra no tempo exato, com hierarquia e sem cobrir os elementos; câmera 3D suave, uma trilha do Artlist por emoção e efeito sonoro em cada animação. Use quando o usuário pedir \"motion dinâmico\", \"no estilo motion dinâmico\", \"ilustra a fala com motion\", \"transforma esse reel em motion\", \"igual ao vídeo do cérebro com defeito de fábrica\", ou mandar um bruto/roteiro pedindo animação moderna com o especialista pouco tempo na tela."
---

# Motion Dinâmico

Exemplo aprovado como base: **"Seu Cérebro Tem Um Defeito De Fábrica"** (v2, 21/10/2026; v5 com B-roll e tela dividida), projeto
`Desktop/Projetos Edições/Motion Designer/videos/cerebro-dinamico`, cenas em `references/exemplo_cenas.py`.
Referências de estilo que o usuário mandou (Instagram): `Dept_TiCu6m` (dados com brilho amarelo em fundo
vinho), `DetkzN8CPRP` (quadro de investigação: fotos com alfinete, carimbo, legenda que acende). Gramática em
`references/estilo.md`.

Fale com o usuário pelo resultado ("o título entra na palavra", "a música vira na virada"), nunca por código.
Segue também as regras da skill `motion-designer` (área segura, revisão quadro a quadro, entrega) e do CLAUDE.md.

## Regras do estilo (o que o usuário pediu)

- **Especialista ~10% do vídeo**: gancho (primeiros 3 s) e a virada da fala. O resto é animação.
- **Cada palavra/frase ilustrada literalmente**, no tempo exato em que é dita (título entra na palavra).
- **Moderno, não vintage** (21/10/2026: "esqueça a ideia de utilizar estilo vintage, quero algo moderno").
- **Fonte Helvetica bold/regular** → TeX Gyre Heros (mesmo desenho, licença livre), já em `assets/fonts`.
- **Uma música por emoção** do Artlist (tensão, mistério, tristeza, alegria, motivacional épica…), trocando
  quando a linguagem muda; nunca uma trilha só. Detalhe em "Trilhas".
- **Efeitos sonoros em todas as animações** (o gerador anota sozinho: pop, whoosh, impacto, digitação, brilho…).
- Animações suaves, sem exagero. Texto que o especialista fala errado: escrever **como ele fala**
  (nota do usuário: "aqui está escrito 'desconto' e não desconforto").
- Elementos sem marca d'água e sem texto em inglês; Freepik **pelo Chrome** (sem crédito da Magnific).
- **Sem legenda** (v3, 21/10/2026): a fala inteira vira texto animado na tela, cada palavra no tempo dela e uma vez só
  (nada repetido entre texto, etiqueta e carimbo). Hierarquia: palavras de ligação finas e menores (`fino`), palavra-chave
  grande em destaque; o texto nunca cobre um elemento (use topo a partir de y 385 e base até y 1460). Não chamar `v.legenda()`.
- **Paleta Legacy**: azul-marinho no fundo, azul claro `#17adfd` e azul `#0094ff` nos destaques, dourado `#e7aa51` para
  recompensa/alerta. Nada de laranja/vermelho/amarelo.
- **Carimbos preenchidos** (fundo azul, texto branco), nunca só o contorno. **Sem etiqueta fixa no topo** (kicker vazio).
- **Sons específicos** quando a cena pede: soco + sino de boxe, despertador analógico, ronco, passos, acerto de dardo
  (`sfx("punch"|"sino"|"despertador"|"ronco"|"passos"|"acerto", t)`); tire o que o usuário apontar com `semsom("tipo", t)`.
- Pessoas reais da equipe/especialista: recorte de cabeça vem do Drive do usuário (ex.: cabeça do Clailton na CTA).
- **Área segura pelo gabarito do usuário** (v4, 21/10/2026): conteúdo entre y 250 e 1500, margem esquerda 70 e direita 55;
  de y 1110 para baixo nada importante passa de x 887 (botões). Textos de baixo: centro em x 470, largura 780.
  Composição centrada na área segura: se o vídeo ficar "muito embaixo", suba o palco com `Video(..., css=".bz, .cena > .palco
  { top: -70px; bottom: 70px; }")` e suba o cartão do especialista o mesmo tanto.
- **Texto entra 0,15 s antes da palavra** (o molde já faz): no tempo exato o usuário achou atrasado.
  Texto que sai para outro entrar no mesmo lugar: `sai` pelo menos 0,25 s antes da primeira palavra do próximo (senão encavala).
- **Vermelho** (`rd`, `#ff3b3b`) para palavra/risco negativo (prejudique, desconforto, roube); dourado só em recompensa.
- Sino de boxe é de **fim de round**: `sfx("sinofim", t)` terminando exatamente no corte da cena.
- Efeito que o usuário achar alto ou demais: tirar (`semsom`), não só baixar.
- **B-roll de filme/série e tela dividida** (notas da v4, 21/10/2026): as cenas também podem ser trechos reais do acervo
  `Desktop/B-ROLLS` (o mesmo da tela dividida: `acervo.json`, `MAPA DE SITUACOES.md`), escolhidos pelo sentido da fala.
  Três jeitos de usar: **B-roll em tela cheia** com o texto por cima (escurecido em cima/embaixo indo até a borda);
  **tela dividida**: B-roll em cima (1080x900) e o Clailton embaixo (1080x1020), **sem linha na emenda**: faixa em degradê
  escuro de y 680 a 1120 (esmaecendo uma tela na outra) com o texto **centralizado em y 900** (v6, 21/10/2026). Carimbo
  e texto não encostam na cabeça do Clailton (cabeça começa por volta de y 1060); **Clailton em tela cheia** sem moldura (sem o cartão de fundo azul) com o texto embaixo. Enumeração
  ("treinar, estudar, economizar") = um B-roll por palavra, só a palavra na tela; aprovado (v7, 21/10/2026) em tela dividida:
  um B-roll por palavra em cima, o Clailton embaixo e a palavra sozinha na emenda. Evite trecho com legenda queimada ou
  logo (ROC-01) e desenho animado quando a fala é séria. Quando o usuário pede B-roll, o elemento 3D daquela cena sai.
  O B-roll tem que ilustrar a fala de verdade (v5 reprovada: Gladiador no trigo para "futuro", close do Rocky para
  "treinar"): para "futuro", alguém olhando o horizonte; "treinar", alguém treinando/correndo; "estudar", alguém na mesa
  ou no computador (Walter Mitty, MIT-02); recompensa/"café delicioso", alguém comendo (Kevin com pizza, HA2-01).
  Um trecho por fala, sem corte de câmera no meio (`planos` do acervo.json); confira o rosto em cada quadro do recorte.
  Trecho de animação (elementos 3D) pode virar tela dividida com o Clailton embaixo: elementos só na metade de cima.

## Passo a passo

Variáveis: `S = ~/.claude/skills/motion-dinamico/scripts`, `PY` = Python da venv do corte-viral
(`%LOCALAPPDATA%\corte-viral\venv\Scripts\python.exe`, com `PYTHONUTF8=1`), `T` = pasta de trabalho do reel
(`C:\Render\_trabalho\<slug>`), `P` = projeto (`Desktop/Projetos Edições/Motion Designer/videos/<nome>`).

1. **Corte e voz do especialista** com a skill de reels do formato (TD/NV): decupagem, `corte.json`,
   `palavras_corte.json` alinhado e, se o áudio pedir, o Adobe Podcast (`audio_tratado.wav`). Não renderiza o reel.
2. **Mapa de emoções e de cenas**: leia `palavras_corte.json` e divida a fala em cenas de 2–5 s (uma ideia
   por cena) e em trechos de emoção (para as trilhas). Marque as 1–2 janelas do especialista (≈10%).
3. **Elementos**: para cada cena, um ícone/pessoa 3D do Freepik (PNG sem fundo) pelo Chrome — busca
   `freepik.com/search?query=<termo>%20png&type=psd`, item → "Download by file types" → PNG, ~18 s
   (o watcher `reels-novela-clailton/scripts/salvar_downloads.ps1 -Pasta <pasta>` salva o "Salvar como").
   Pessoa real citada (cientista, autor): foto livre do Wikimedia Commons (licença CC BY/domínio público).
   Monte uma folha e confira cada imagem (texto em inglês, marca, moeda com "BITCOIN"… troca).
4. `PY S/novo_projeto.py "<P>"` → projeto com fontes, grão e kit de efeitos sonoros.
5. `PY S/preparar_elementos.py <pasta_baixados> "<P>" mapa.json` → `assets/img/<nome>.png` com borda branca
   e `grade/<nome>.jpg` (linhas a cada 100 px).
6. **Bonecos** (pessoas cuja cabeça balança): olhe a grade, escreva `cortes.json` (polígono da cabeça, pivô
   no pescoço, linha de corte) e rode `PY S/recortar_cabeca.py "<P>" cortes.json`.
7. **Especialista e voz**: `PY S/expert.py "<T>" "<P>" 0-3.40 40.62-43.10 [--realce]` → `expert_<n>.mp4`
   (retrato 4:5, rosto medido no próprio bruto, do alto da cabeça até a base) e `assets/audio/voz.wav`.
   Tela dividida/tela cheia: `--wh 1080x1020 --prefixo dividida --sem-voz` ou `--wh 1080x1920 --prefixo cheia --sem-voz`.
   **B-roll**: `trechos.json` (`nome`, `acervo` = código do B-ROLLS, `t`, `dur`, `lugar` "cheia"/"topo", `x`/`y` 0–1 para o
   recorte (vídeo vertical no topo: `y` ~0,35 para não cortar a cabeça), `fonte_dur` < `dur` = câmera lenta) e `PY S/preparar_broll.py "<P>" trechos.json` → `assets/broll/<nome>.mp4`
   (sem tarja preta, sem som). Confira um quadro de cada (rosto inteiro, sem legenda queimada).
   Confira um quadro de cada janela (rosto centrado, cabeça com folga). `--realce` se o card pedir "diminuir realces".
8. **Cenas**: copie `references/exemplo_cenas.py` para `T/cenas.py` e reescreva as cenas (peças na seção
   "Peças"). Rode `PY T/cenas.py "<P>" "<T>/palavras_corte.json"` → `index.html` + `assets/audio/sfx.json`.
9. **Trilhas** (Artlist pelo Chrome deste PC, logado) e `trilhas.json`; `PY S/montar_mix.py "<P>" trilhas.json`
   → `assets/audio/mix.wav` (-14 LUFS).
10. **Revisão** (obrigatória): `npx hyperframes lint`; `npx hyperframes snapshot --no-end -o snaps --at <um
    momento por cena>`; olhar a folha; `motion-designer/scripts/area_segura.py --formato 9x16 --pasta snaps
    --saida qa/area.jpg`; transcrever o `mix.wav` (`motion-designer/scripts/transcrever.py`) para provar a voz.
11. `npx hyperframes render --quality high --fps 30 --output renders/<nome>_v1.mp4`; folha de quadros do MP4
    (`fps=2,tile`) para achar quadro vazio ou elemento fora de hora.
12. **Projeto do Premiere** (quando pedirem "gera o projeto para o Premiere"):
    `PY S/premiere_motion.py "<P>" "C:\Render\Reels Editados\<nome> - PREMIERE"` → XML (Arquivo > Importar) + `midia/`:
    V1 fundo e animações sem texto (MP4), V2 textos/carimbos/CTA transparentes (ProRes 4444), V3 final (desligada),
    A1 voz, A2/A3 trilhas com fades, A4+ cada efeito sonoro, mix final (desligada); `LEIA-ME.txt` explica. Copie a pasta
    para o Drive (EDITADO do mês) para a equipe abrir em outro PC.
13. **Entrega**: Sala de Revisão (skill `sala-de-revisao`; prévia como asset `/_blob/`), link na conversa.
    Card do Notion/Drive só se for da fila (`fila-de-render`).

## Peças (motion_lib.py)

Posição sempre pelo centro (cx, cy) em 1080x1920; `z` = profundidade (negativo = longe, positivo = perto).

| Peça | Para quê |
| --- | --- |
| `img(id, nome, cx, cy, w, z)` | ícone/objeto 3D recortado |
| `boneco(id, rig, cx, cy, w)` | pessoa com a cabeça balançando |
| `titulo(id, [(tam, [(palavra, t, estilo)])], cx, top)` | título palavra a palavra; estilo `ac` amarelo, `rd` vermelho, `hl` caixa amarela, `dim`, `it` |
| `etiqueta(id, texto, cx, cy, cls="tag"/"tag lin"/"tag rd")` | pílula (1. TREINO, NO FUTURO) |
| `carimbo(id, texto, cx, cy, tam, rot)` | carimbo vermelho (AQUI, VENCE, PARE) |
| `cartao(id, nome, cx, cy, rotulo)` | cartão escuro com contorno luminoso (comparações, listas) |
| `polaroid(id, foto, cx, cy, w, legenda)` | foto presa com alfinete (pessoa citada) |
| `selo(id, nome, cx, cy, d)` | ícone em círculo com anel luminoso (linha do tempo) |
| `linha(id, d, tracejada, seta)` | caminho luminoso que se desenha (`traco`) |
| `brilho`, `raios`, `svg`, `caixa`, `camada` | luz atrás do objeto, raios, desenho livre |
| `v.expert(arquivo, t0, dur, cx, cy, w, h)` | especialista no cartão com contorno azul |
| `v.expert(..., moldura=False)` | especialista sem cartão (tela dividida embaixo: `cx=540, cy=1410, w=1080, h=1020`; tela cheia: `cy=960, h=1920`) |
| `v.video(arquivo, t0, dur, x, y, w, h, zoom)` | B-roll (tela cheia por padrão; topo da tela dividida: `0, 0, 1080, 900, zoom=0`). Texto por cima vai em `sobre=[...]` da cena, y +70 se o palco subiu |

Animações no JS da cena: `entra(sel, t, "sobe|esq|dir|pop|fade")`, `sai`, `flutua`, `cam` (câmera 3D),
`bz` (desfoque de entrada da cena), `soco`, `traco`, `corre` (ponto na curva), `digita`, `carimbo`, `pulsa`,
`sfx("brilho|ok|tique|tag|teclado|virada|doc|soco|esq|dir|pop", t)` (efeito extra).
Regras aprendidas: títulos com `top` ≥ 375 (a câmera empurra para cima e encosta na etiqueta do topo);
objeto que nasce com a cena entra já visível (sem quadro vazio no corte); nada importante em x > 950 entre
y 1000–1720; texto que troca na mesma cena: `sai("#tit", t)` antes do próximo entrar no mesmo lugar.

## Trilhas (uma por emoção)

- Mapeie a fala: gancho/problema (tensão curiosa), explicação/ciência (mistério de documentário), dor/adiar
  (tensa ou triste), virada "então se você quiser…" (épica motivacional), dicas práticas (leve, alegre),
  fechamento (épica inspiradora). Troque a música no começo da frase que muda a linguagem.
- Artlist pelo Chrome **deste PC** (`list_connected_browsers`: o "Browser 2/3" pode estar em outro computador;
  baixa lá e o arquivo não chega aqui). Sem login: peça ao usuário para entrar (Claude não digita senha).
  Busca `artlist.io/royalty-free-music/search?terms=<termos>` → botão de download → MP3. Termos que servem:
  "dark tension suspense", "mystery documentary curious", "sad emotional piano", "epic motivational inspiring",
  "happy upbeat light".
- `trilhas.json`: `{"duracao": D, "trilhas": [{"arquivo": "musicas/x.mp3", "entra": 0, "sai": 8.6,
  "inicio_no_arquivo": 0, "ajuste": 0}, ...]}` — o `montar_mix.py` iguala volumes (voz -20, música -33 +ajuste),
  cruza as trilhas (0,8 s), abaixa a música sob a voz e soma os efeitos do `sfx.json`.

## Arquivos

- `scripts/motion_lib.py` (gerador), `scripts/molde.html` (visual), `novo_projeto.py`, `preparar_elementos.py`,
  `recortar_cabeca.py`, `expert.py`, `preparar_broll.py`, `montar_mix.py`, `premiere_motion.py` (projeto do Premiere em camadas).
- `assets/fonts` (TeX Gyre Heros), `assets/fx/grao.png`, `assets/sfx` (teclado da CTA, whoosh documental).
  Kit de efeitos: `~/.claude/skills/media-use/audio/assets/sfx` (Pixabay, uso livre).
- `references/estilo.md` (gramática visual), `references/exemplo_cenas.py` (vídeo do cérebro).
- Python: pillow, opencv, numpy, soundfile (venv do corte-viral já tem; `requirements.txt`).
