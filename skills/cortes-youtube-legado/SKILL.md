---
name: cortes-youtube-legado
description: Transforma as aulas gravadas do Legado Empresarial (presenciais no auditório, com o Clailton falando; 2–3 h cada, no Drive em "LEGADO - AULAS AO VIVO") em episódios de 15 a 45 minutos para o YouTube, cada um com começo, meio e fim — acha a aula no Drive, transcreve palavra a palavra, monta o mapa de temas, escolhe os episódios, corta (sem avisos, intervalos, apresentação de aluno, vídeo de terceiros no telão nem música), abre com 15–40 s do trecho mais forte, coloca o card "SESSÃO ESTRATÉGICA GRATUITA" com QR code (igual ao Executoria Cast) em 3 momentos estratégicos, trata o som, confere tudo e entrega em ORGÂNICO > EDITADO do mês com título, texto da thumb, descrição com capítulos e link da sessão estratégica, tags, comentário fixado, legenda .srt e quadros do Clailton para a thumb. Use quando pedirem "cortes do Legado para o YouTube", "transforma a aula em episódios", "corta as aulas do Legado", "vídeo longo das aulas", "aula do auditório para o YouTube", "cortes de 15 a 45 minutos", ou mandarem uma aula/turma do Legado para virar vídeo do YouTube.
---

# Cortes do Legado para o YouTube (episódios de 15–45 min)

Pedido do usuário (13/10/2026), ideia do Clailton: as aulas do **Legado presencial** (Clailton no auditório)
viram episódios de YouTube de **15 a 45 min**, cada um **com começo, meio e fim**, com **CTA de QR code para a
sessão estratégica** igual ao do Executoria Cast (youtube.com/watch?v=v0jEA57pYL8, card no canto aos 17:08), e a
**descrição direcionando para a sessão**. Edição: **só a aula** (sem vinheta, sem legenda queimada, sem música).
Primeira aula feita: **Turma 14 · Aula 06** (mapa estratégico, versão com slide) → 4 episódios de 15–24 min
depois de 3 rodadas do revisor às cegas (exemplo completo em `exemplos/t14a06_plano.json`, com `cortar`). A T12 · Aula 10 (só câmera) ficou de exemplo de aula sem
versão com slide (`exemplos/t12a10_plano.json`).

O usuário não é técnico: relatório curto, pelo dia a dia dele (ver CLAUDE.md global). Sempre em português.

## O que sai para o usuário (por aula)

Pasta no Drive: `G:\Meu Drive\02. Captação de Vídeos\<AAAA>\<MM - Mês>\ORGÂNICO\EDITADO\CORTES YOUTUBE - LEGADO\<Turma NN - Aula NN - Tema>\`
(o usuário pediu "dentro de orgânico outubro editados"; vale o mês em que a edição é entregue).

| Arquivo | O que é |
| --- | --- |
| `EP01 - <título curto>.mp4` | episódio 1920×1080, 30 fps, H.264 CRF 20, AAC 192k, −14 LUFS |
| `EP01 - <...> - YOUTUBE.txt` | título recomendado + 2 alternativas (teste A/B), texto da thumb + 2, descrição pronta (link na 1ª linha, capítulos), comentário fixado, tags, onde o QR aparece, dados imprecisos da fala |
| `EP01 - <...>.srt` | legenda para subir no YouTube (não queimada) |
| `thumbs/EP01 - <...> - thumb N (...).png` | 3 quadros do Clailton para a arte: inteiro e recorte com o rosto |

E uma **página de revisão** (Artifact) com todos os episódios da aula: link do Drive, duração, títulos, thumbs,
descrição e as imagens candidatas — o usuário aprova pelo celular. Notion só se pedirem.

## Padrão aprovado do episódio (usuário, 14/10/2026 — EP01 da T14 A06)

- **Intro de 40–50 s só com conteúdo do Clailton valendo**: 4–6 falas dele (explicação, opinião, caso, conclusão),
  **nunca** ele lendo frase de famoso/citação de slide (Grant Cardone, "a média é a fórmula...", "Ou você aumenta o
  sacrifício..."), e evite trecho em que o telão mostra citação. Clarão branco (`"flash"` no 3º item da abertura)
  entre blocos de assunto; última fala = a mais forte, no ápice da música. Ex. aprovado: "a maioria está perdida...
  precisam de líderes inspiradores" → "as pessoas saem de lá supervalorizadas... triplicaram o faturamento" →
  Stallone vendendo o cachorro → "nós vamos virar esse jogo".
- **Música crescente só na intro** (`"musica_abertura"` no plano: arquivo, `fim_no_arquivo` = o ápice/corte da
  faixa, `db_ini`/`db_fim`), abaixa sozinha sob a voz e corta no preto. Faixas do Artlist já baixadas da conta do
  usuário ficam em `~/Downloads` ("Artista - Título.mp3"); aprovada: "Ian Post - Come Back Alive" (ápice em 60,9 s).
  Meça a curva com `ebur128` e escolha uma que cresça sem parar até o ápice.
- **Identificação** do Clailton quando o conteúdo começa e ele aparece de frente: animação "C · fio fino" (nome
  grande, fio branco→azul que se desenha, cargo embaixo: "Clailton Luiz / Sócio Fundador · Legacy Executoria"),
  arquivo com transparência em `C:\Render\_youtube\recursos\nome_clailton_C.mov` (se faltar: `npx hyperframes render --format mov` no projeto `references/identificacao/projeto_C`); no plano:
  `{"aula": "<1 s antes de ele virar>", "estilo": "video", "arquivo": "<mov>", "texto": "Clailton Luiz", "dur": 7}`.
  A versão com caixa (`estilo: "nome"`) foi **reprovada** ("animação ruim").
- **Fim**: a imagem continua (ele se mexendo) e escurece em 1,2 s; nunca congelar o último quadro (reprovado).
- **Vinheta da Legacy** depois do fim (`"vinheta"` no plano): "Feixe de luz", 4,5 s, com o acorde final da mesma
  música (`references/vinheta/vinheta_legacy_feixe.mp4`, cópia em `C:\Render\_youtube\recursos`). Projeto HyperFrames das 3 opções em
  `references/vinheta/` (refazer a partir dali se o logo mudar).

- **Abertura sem eco** (revisor, 14/10/2026: aconteceu em 8 de 8 episódios na 1ª rodada): nenhuma frase da abertura pode
  voltar no corpo antes de ~2,5 min (confira por script comparando as palavras da abertura com os primeiros minutos do
  corpo), e cada trecho começa e termina em frase inteira (nada de "e quanto mais...", "São o antídoto..." sem sujeito).

## Crivo do corte (usuário, 14/10/2026)

Nota 0–10 em cada ponto, média = nota do corte. **Por enquanto todo corte sobe para o Notion com a nota e a
opinião** (o usuário quer calibrar o crivo com o julgamento dele antes de eu descartar algo); no card, escrever
"publicaria" / "publicaria com ressalva" / "não publicaria" e por quê.

| Ponto | O que vale 10 |
| --- | --- |
| Valor para o dono | Ele assiste e pensa "vou aplicar isso na minha empresa". **Conteúdo técnico e profundo vale tanto quanto história**: como montar processo, organograma, indicadores, planejamento, DRE. Não precisa ter caso com virada |
| Tema buscável | Assunto que dono de empresa procura e que cabe num título forte e verdadeiro |
| Começo, meio e fim | Entende-se sem a aula; fecha a ideia (explicação completa, conclusão ou moral) |
| Gancho | Há 4–6 falas dele fortes o bastante para a intro (sem citação de famoso) |
| Limpo | Pouca fala de turma/planilha/material, poucas emendas, duração ≥ 15 min sem enchimento |
| Imagem | Slide legível ou Clailton visível; pouco tempo de citação no telão; sem aluno identificável |

Melhor 1–2 cortes ótimos por aula do que 4–5 fracos.

## Notion: Audiovisual Claude e aprovação

Cortes do YouTube vão para o quadro **Audiovisual Claude** (mesma base do Calendário Editorial, aba YouTube),
um card por episódio com: tema, nota do crivo e opinião, título recomendado + 2, texto da thumb, thumbs anexadas,
descrição pronta (convite para a sessão estratégica com link, redes do Clailton e da Legacy), capítulos, tags,
link da prévia (Sala de Revisão) e do Drive. Andamento: Claude editou → Aprovação (usuário) → Correções (Claude)
(notas no tempo do vídeo na Sala de Revisão) → Aprovado → Agendado/Publicado.
**Nunca publicar nada no YouTube** sem o usuário pedir explicitamente; postagem automática é etapa futura.
Como montar (T14 A06, 14/10/2026): `scripts/cards_notion.py <trabalho> <cards_cfg.json>` gera o texto de cada card
(`notion_card_epNN.md`, a partir do `- YOUTUBE.txt` e do `crivo.json`); crie os cards na base
(`collection://f0cc9747-efab-822b-8678-07f92372d6b7`: ANDAMENTO "Aprovação", RESPONSÁVEL "🤖 CLAUDE", REDE SOCIAL
["Youtube"], FORMATO ["🎥 Film (Video Longo)"], NOTA DO CRIVO), anexe as thumbs A e B `_1280.jpg` em MATERIAL
FINALIZADO (`notion-create-file-upload` + `curl -F file=@...` + `update_properties` com `file_upload`), suba o
episódio inteiro na Sala de Revisão em partes (skill `sala-de-revisao`, "Vídeo longo") e grave `videos/<id>` com o
link do card; em MATERIAL FINALIZADO vão o link da Sala (primeiro), o do Drive e as thumbs (`update_properties` com
as duas URLs + os `file_upload`). Bloco de código
sem linguagem vira "javascript" no Notion: o gerador já escreve ```` ```plain text ````.

## Onde está cada coisa

| Item | Onde |
| --- | --- |
| Aulas | `G:\Meu Drive\LEGADO - AULAS AO VIVO\TURMA NN\...` — **presenciais (auditório): Turma 12, 13, 14, 17**; Turma 15 e 16 são **online** (Zoom/OBS, não usar sem o usuário pedir). Os arquivos estão **espalhados** (usuário, 13/10/2026): procure também na raiz do Meu Drive e pelo conector do Drive (`search_files`) |
| **Qual versão usar** | **Sempre a versão com o PowerPoint no quadro** (usuário, 13/10/2026: "são as versões finais que enviávamos para os alunos, melhores para o YouTube do que a imagem bruta da câmera"): a gravação do programa da transmissão (OBS/StreamYard), que alterna **slide grande + Clailton numa janela à direita sobre fundo vermelho escuro** com a câmera, às vezes com vinheta "LEGADO EMPRESARIAL". Nomes típicos: data-hora do OBS (`2025-12-04 09-40-39.mp4`) ou `LEGADO AULA 06.mp4`. Câmera crua (só auditório, sem slide na tela) = último recurso, e só se a aula não tiver versão com slide. Para saber: 12 quadros espalhados numa folha (`ffmpeg -nostdin -ss ...`) e olhar |
| Mapa conhecido (13/10/2026) | **Com slide:** T14 `LEGADO AULA 06.mp4` (3h01, 1080p, Clailton) · T12 `AULA SOBRE MARKETING - 2025-10-16...` (mistura câmera/slide, tem convidados) · T14 `AULA 02\2025-12-04 09-40-39.mp4` (slide, mas quem fala é outro professor) · T14 `AULA 01 - LEGADO - TURMA 14.mp4` (slide, só 640×360). **Só câmera:** T12 `Turma 12 - Aula 10`, `AULA 11`, `MAIOR MENTIRA`; T14 `AULA 07`. **Alunos/convidado:** T14 `AULA 03 SWOT`, T12 `AULA DE DRE - ADRIANO`. **Editadas no Vimeo:** T12 Aulas 01–09 (links na planilha "Trilha de Lives do Legado", na pasta LEGADO - AULAS AO VIVO; status "No vimeo"/"Para Editar"). Pastas `INTELIGENCIA EMPRESARIAL\CURSO\LIVES` e `MODULO 02` são de **outro curso** (Inteligência Empresarial), não do Legado |
| Link da sessão estratégica | `https://formulario.legacyexecutoria.com.br/` (o da bio do Instagram, conferido em 13/10/2026; o antigo `lp.legacyexecutoria.com.br/form-organico` **não existe mais**). Antes de cada aula, abrir o link e ver se responde "Legacy Educação — Agendamento"; se mudou, pegar o novo na bio do @legacyexecutoria |
| UTM | `utm_source=organico&utm_medium=youtube&utm_campaign=<codigo>e<N>` (+ `&utm_content=descricao` / `comentario`). `codigo` = turma+aula curto, ex.: `t12a10`. O `utm_source=organico` é o que o relatório do orgânico (cerebro-legacy) já filtra |
| Trabalho local | `C:\Render\brutos\legado_tNNaNN\` (cópia da aula) e `C:\Render\_youtube\legado_tNNaNN\` (transcrição, plano, render, qa, thumbs) |
| Python | `%LOCALAPPDATA%\corte-viral\venv\Scripts\python.exe` (tem faster-whisper com CUDA, OpenCV 4.10, Pillow, numpy) com `PYTHONUTF8=1`. Pacotes: `requirements.txt` |
| Pesquisa que embasa as regras | `references/pesquisa-youtube.md` (13/10/2026, com fontes) |

## Passo a passo

Rode no **PC de render** (`~/.claude/maquina.json` → `"papel": "render"`). Scripts em `~/.claude/skills/cortes-youtube-legado/scripts/`.
`P="$LOCALAPPDATA/corte-viral/venv/Scripts/python.exe"`, sempre `PYTHONUTF8=1`.

1. **Achar a aula (a versão com slide).** Liste `LEGADO - AULAS AO VIVO`, a raiz do Meu Drive e busque pelo
   conector (`search_files`: vídeo com "LEGADO AULA", data-hora do OBS, "TURMA NN"). Para cada candidata:
   `"$P" scripts/folha_aula.py <folha.jpg> <video1> <video2> ...` e escolha a que tem **slide no quadro** e o
   **Clailton** falando (ver "Qual versão usar"). Aula em várias partes (pasta `AULA 02\` com 3–4 arquivos):
   junte na ordem. Em loop no bash, todo `ffmpeg` leva `-nostdin` (senão ele come a lista do laço).
2. **Copiar** para o disco local (o G: baixa sob demanda; ~3 min para 5 GB):
   `robocopy "<pasta no G:>" "C:\Render\brutos\legado_tNNaNN" "<arquivo>" /J /R:3 /W:10` (código 1 = copiou).
3. **Transcrever** (GPU, ~7 min por hora de aula): `"$P" scripts/transcrever.py <aula.mp4> <trabalho>`.
   Sai `transcricao.txt` (uma frase por linha com `[hh:mm:ss]`, e `~~ silêncio Ns ~~` nos buracos).
4. **Assistir lendo** a transcrição inteira (não pule: é aqui que a qualidade nasce) e montar o **mapa de
   temas**: bloco a bloco, com início/fim e o que é. Marque para **cortar**: abertura/logística ("boa noite",
   formatura, fotos, avisos, intervalos, "pessoal de casa"), apresentação de aluno, pergunta de plateia sem
   microfone, procura de microfone, **vídeo de terceiros no telão** (Fantástico, influenciador, trailer: voz que
   não é do Clailton, frases de narrador) e **silêncio longo com música** (animação de slide — meça o volume:
   RMS alto sem fala = música, corte). Monte também uma folha com 1 quadro a cada 30 s
   (`ffmpeg -vf "fps=1/30,scale=256:-1,tile=12x18"`) para ver ângulos e o que passa no telão.
5. **Escolher os episódios** (regras abaixo) e cravar os cortes palavra a palavra:
   `"$P" scripts/palavras.py <trabalho> 00:11:25 00:26:04 ...` — corte logo antes da 1ª palavra (−0,1 a −0,3 s)
   e logo depois da última (+0,1 a +0,4 s), nunca no meio de palavra; no meio de frase só se a frase seguinte
   continuar o sentido. Para achar uma frase: `"$P" scripts/achar.py <trabalho> "frase" --perto 01:20:40`.
   **Frase a tirar de dentro de um trecho: use `"cortar"` no plano, pelo texto** (não pelo relógio):
   `{"frase": "como o Adriano bem falou ali", "perto": "01:10:44"}`, `{"de": "...", "ate": "..."}` ou
   `{"de": "...", "ate_antes": "..."}` — o corte cai no meio da pausa e nunca pega meia palavra.
6. **Escrever o `plano.json`** (formato no topo de `scripts/render_episodio.py`; exemplo em `exemplos/`):
   trechos, `cortar`, abertura, CTAs (instantes da aula) e o bloco `meta` (títulos, thumbs, resumo, bullets,
   capítulos, tags, hashtags, fatos imprecisos). No topo do plano, `"correcoes"`: nomes que o Whisper erra, para
   a legenda .srt (`{"Cléuto": "Clailton", "Ruas": "ROAS", "Graham Cardone": "Grant Cardone"}`; maiúscula conta,
   então "Ruas" não troca "ruas"). Confira com `"$P" scripts/render_episodio.py <trabalho> --so-mapa`
   (mostra duração e onde cai cada CTA em %; reclama se a CTA cair num trecho cortado ou perto do fim).
7. **Renderizar**: `"$P" scripts/render_episodio.py <trabalho> [--so 1]` (~1 min de render por 2–3 min de vídeo
   no libx264). Em paralelo: `"$P" scripts/thumbs.py <trabalho> candidatos`.
8. **Conferir cada episódio**: `"$P" scripts/conferir.py <trabalho> "<arquivo>"` — reprova formato, duração,
   volume, tela preta, QR que não lê, card em cima de rosto; mostra o texto da abertura, do começo e do fim.
   **Abra a folha** `qa/<arquivo>_folha.jpg` (antes/depois de cada emenda + cada CTA) e olhe de verdade.
   Depois rode o **revisor às cegas** (abaixo). Corrigiu? renderize e confira de novo.
9. **Thumbs**: abra `thumbs/epNN_candidatos.jpg`, escolha 3 (expressão que casa com o tema, olhos abertos,
   boca bem) e `"$P" scripts/thumbs.py <trabalho> exportar --ep N --escolha 3,7,11`.
10. **Pacote do YouTube**: `"$P" scripts/metadados.py <trabalho>` (gera o `- YOUTUBE.txt` e acusa título longo,
    thumb fora de 2–4 palavras, capítulo inválido).
11. **Entregar**: copie mp4, srt, YOUTUBE.txt e thumbs para a pasta do Drive (robocopy /J), espere aparecer no
    Drive (conector `search_files` com `parentId = '<id da pasta>'`; o tamanho tem que bater com o do PC), grave
    `drive.json`, rode `"$P" scripts/pagina.py <trabalho>` e publique a página (Artifact): copie `pagina/` para o
    scratchpad e publique de lá pelo **caminho longo** (com o nome inteiro do usuário; pelo nome curto do Windows,
    o que tem `~1`, a publicação dos vídeos é barrada), com `root` = a pasta e `files` = `media/*`.
    Para trocar só os links depois: `pagina.py --sem-media`, copie o index.html e publique o mesmo arquivo.
    Mande o resumo.

## Regras do episódio (o que é "começo, meio e fim")

- **1 episódio = 1 problema + 1 resposta**, que se entende sem ter visto o resto da aula. Alvo **18–35 min**,
  mínimo 15, máximo 45. Uma aula de 1h45 rendeu 3 (19, 23 e 26 min); de 3 h, espere 4–6.
- **Começo:** a 1ª frase que apresenta o problema ou a história (ex.: "1932, o ano em que foi criada a Lego").
  Nunca "boa noite", aviso, "como eu falei semana passada".
- **Meio:** blocos de 3–8 min na ordem da aula. Pode juntar blocos não vizinhos do mesmo tema (ex.: história
  de abertura + parte central), desde que a emenda faça sentido falada. Retomada de assunto do começo
  ("é isso que quase quebrou aquela empresa, a Lego") é ouro: fecha o laço.
- **Fim:** a conclusão, a moral ou uma pergunta de reflexão do próprio Clailton ("Como eu posso melhorar?").
  Nunca terminar em "agora vamos para a dinâmica", "pessoal de casa", nem em "uma boa semana a todos". O render
  segura o último quadro 1,2 s e escurece em silêncio (`RESPIRO`), então pode parar logo depois da última palavra.
  Fechar com a mesma história da abertura funciona (EP02: a dona que contratou um vendedor que ganha mais que ela).
- **Abertura (cold open, 15–40 s):** o trecho mais forte do próprio episódio (frase-tese, pergunta, virada de
  história), sem entregar a solução. Entra antes do começo, com um mergulho de 0,3 s no preto. Nas pausas
  da abertura, nada acima de 1,2 s. Exemplos: "o problema é o líder desqualificado..." (EP1), "o nome dessa
  empresinha chamava-se Netflix... olha o nosso tamanho" (EP2), "o Alex... é o nosso maior vendedor" (EP3).
- **Pausas sem fala > 2,5 s** viram 0,9 s sozinhas (o render faz). Risada/aplauso curto fica.
- **Direitos autorais:** nada de vídeo de TV/terceiros nem música de animação. Se a fala do Clailton depende
  do vídeo, mantenha só a parte dele que se sustenta (ex.: o pipoqueiro de Curitiba: apresentação + comentário
  depois, sem a reportagem). Se ele **narra por cima** de um clipe (ex.: a luta Ali x Wepner na T14 A06), mantenha
  a fala e **desfoque o clipe**: `"borrar": [["ini", "fim", x, y, w, h], ...]` no plano (tempo da aula, px em
  1080p; tela cheia = `0, 0, 1920, 1080`; só o slide no layout com janela = `96, 205, 1190, 670`). Para achar o
  começo/fim do clipe: movimento quadro a quadro na área do slide (clipe = movimento alto; slide = ~0).
  Foto parada de filme/pessoa famosa no slide pode ficar.
- **Aluno identificável falando** (apresentação de trabalho): fora, sem autorização.
- **Frases de turma** (o revisor pegou dezenas na 1ª rodada; tire com `cortar`): "semana que vem a gente vê",
  "nos próximos encontros", "que é o que vamos tratar hoje", "como o Adriano falou", "o Claudio me mostrou
  ontem", "dá o microfone ali", "eu vou mostrar daqui a pouco", "você vai olhar porque nós vamos cobrar",
  "alguns já fizeram", "a planilha que vocês têm", nome de empresa de aluno ("o exemplo da Rick Entalho").
  **Material da turma** é o mais traiçoeiro: "versão digital e versão impressa", "a ferramentinha que vocês têm
  aí na mesa", "a coluninha do impresso", "puxar da planilha", "vocês vão colocar isso aí no local estratégico",
  "a gente vai trazer você aqui uma vez por mês" — o espectador não recebe nada disso. Também: data presa à
  aula ("esse sábado agora", "vou compartilhar no meu Instagram"), bordão de outra aula sem contexto ("devagar
  na reta e pau na curva"), "para finalizar" no meio do vídeo, frase que morre no meio ("E se você fizer...").
  Também: **dúvida de memória** ("foi no CDL, não, não foi no CDL..."), **repetição** ("É surreal. É surreal."),
  **afirmação grandiosa sem fonte** ("melhor ideia de gestão dos últimos 100 anos", "50% das empresas da Forbes",
  "só gênios") e **tema trabalhista delicado** (cobrar prejuízo do funcionário em 7 vezes).
- **Os cortes do revisor encurtam 10–25 %.** Planeje cada episódio com ≥ 18 min antes da revisão. Se cair
  abaixo de 15, traga uma história do mesmo tema de outro ponto da aula (EP04: a do entregador e da pesquisa de
  satisfação entrou em "melhorar a experiência do cliente"); os trechos tocam na ordem em que estão no plano.

## Letreiros (só quando ajudam quem nunca viu a aula)

`scripts/letreiro.py`: caixa azul no estilo do card, etiqueta verde opcional, embaixo à esquerda (x 96, na faixa
escura abaixo do slide). No plano: `"letreiros": [{"frase": "...", "perto": "...", "tag": "FINANCEIRO · 1/15",
"texto": "Aumentar lucratividade", "dur": 7}]` (ou `"aula": "hh:mm:ss"`; `"onde": "abertura"` para a abertura).
Entra pela frase falada, como os cortes, e sai quando o próximo entra. Não é legenda nem vinheta. Use em:
- **episódio que é lista** (os 15 objetivos do mapa): 1 letreiro por item, com o nome exato do slide;
- **quem é o personagem** da abertura ("Sylvester Stallone, antes de Rocky") e "A história completa no fim do
  episódio" quando a abertura é uma história que só volta no fim;
- **o que está desfocado** ("A LUTA QUE INSPIROU ROCKY · Muhammad Ali x Chuck Wepner, 1975") — sem isso o
  borrão parece defeito.
Texto do telão que a câmera mostra andando (ex.: "HARVARD 100 ANOS" num plano aberto) não dá para borrar sem
seguir o movimento: tire a fala e deixe a imagem.

## CTA da sessão estratégica (QR)

- Card igual ao do Executoria Cast (`scripts/qr_card.py`): caixa azul em degradê, QR em quadro branco à
  esquerda, "SESSÃO / ESTRATÉGICA / [GRATUITA] / APONTE A CÂMERA". Maior que o original (escala 1,65 ≈
  500×250 px, QR ~185 px em 1080p, 5 px por módulo) porque a pesquisa mostrou que QR pequeno não lê da TV.
- **3 por episódio, 30 s cada:** ~25–35% do vídeo, ~70–80% e perto do fim (até 25 s antes do fim; nos últimos
  5–20 s fica a tela final do YouTube). **Estratégico** = logo depois de um ponto que dá vontade de ajuda: quando
  o Clailton fala do que a Legacy faz dentro da empresa, depois da moral de uma história, depois de "eles
  participaram do meu treinamento". Nunca em cima do clímax de uma história.
- **Posição e tamanho automáticos:** o render olha 4 quadros dos 30 s de cada CTA e escolhe entre o card
  **grande** (escala 1,65) nos 4 cantos e o **compacto** (escala 1,2, QR ~164 px) — no layout "slide + janela"
  o compacto entra **na faixa escura de cima, alinhado com a borda do slide (`topo-e`) ou da janela do Clailton
  (`topo-d`)**, sem cobrir nada. Critério: nada de rosto, de texto de slide ou de área clara embaixo do card;
  prefere o grande se ele não cobrir nada. Forçar: `"cantos": {"2": "sd"}` ou `{"1": "topo-d/compacto"}`.
- **URL curta no QR** (≤ 106 caracteres → QR versão 5): sem `utm_content`. O `conferir.py` lê o QR no vídeo
  final, nas 3 posições de cada CTA; se não ler, reprova.
- Quem assiste no celular não escaneia a própria tela: por isso a **descrição abre com o link** e o comentário
  fixado repete o link.

## Título, thumb e descrição (pesquisa em `references/pesquisa-youtube.md`)

**Thumb = padrão do canal "Legacy Executoria Empresarial"** (usuário, 15/10/2026: "siga o padrão que já usamos no nosso
canal ... use as fotos que já temos prontas do Clailton"): `scripts/thumb_canal.py` — fundo quase preto com brilho azul,
Clailton recortado do **ensaio de estúdio** à direita e na frente do texto, linha branca (Montserrat ExtraBold) + palavra-
chave grossa azul (vermelha se for negativa: QUEBREI, ERRADO, DESCULPA), sem logo. Duas por episódio (A/B), com fotos e
textos diferentes. Fotos: `G:/Meu Drive/4. Design/11 - Fotos/Clailton/2026_02_23_Fotos_Estudio_Clailton` (117 fotos);
recortes sem fundo prontos em `C:/Render/_youtube/fotos_clailton/recortes` (01–12, 18, 19; recorte novo = Magnific
`images_remove_background`, 3 créditos). Não use mais quadro da aula ampliado (`thumb_legacy.py` fica de reserva).
Evite fotos em que o ensaio cortou os braços (a 11) e as de braço aberto atrás do texto (a 12); a medição da cabeça erra
com braço levantado: `--cab-foto`. Relatório do padrão: `C:/Render/_youtube/thumbs_canal/relatorio.md`; script de lote de
exemplo: `C:/Render/_youtube/thumbs_canal/gerar_todas.sh`.

- **Título:** promessa + palavra-chave nos primeiros ~45 caracteres; ideal ≤ 70 (máx. 100); 1–2 palavras em
  CAIXA-ALTA; número concreto ou enquadramento de erro/alerta; tag da série no fim (`| Legado Empresarial`).
  Nunca "Aula 10", "Turma 12", data, nome de evento. Tem que ser **verdade no vídeo** (confira na transcrição).
  3 títulos por episódio (o 1º é o recomendado; os outros para o "Testar e comparar" do YouTube).
- **Texto da thumb:** 2–4 palavras que **completam** o título, nunca repetem (título "A Lego QUASE QUEBROU…" →
  thumb "800 MILHÕES EM DÍVIDAS"). 3 opções.
- **Quadro da thumb:** Clailton grande (rosto 35–45% do quadro), expressão casada com o tema, olhos abertos.
  As aulas são plano aberto de auditório: o recorte sai em baixa resolução — avise que o designer pode
  ampliar com IA.
- **Descrição:** linha 1 = `🔹 AGENDE SUA SESSÃO ESTRATÉGICA GRATUITA: <link>`; depois resumo com palavra-
  chave, "Neste episódio:" com 3–5 bullets, o convite de novo com o link, **capítulos** (00:00, ≥ 3, crescentes,
  ≥ 10 s, nas viradas reais, títulos descritivos), rodapé da Legacy, 3–5 hashtags.
- **Dados imprecisos falados** (o Clailton conta de cabeça: anos, valores): não corte a fala, mas **não repita
  no título/descrição** e liste em "fatos" do plano para o usuário saber (ex.: Netflix x Blockbuster foi em 2000).

## Revisor às cegas (depois do conferir.py)

Prompt pronto em `references/revisor-as-cegas.md`: um agente (`general-purpose`) lê só o texto de cada episódio
(`qa/<arquivo>_texto.txt`), a abertura, o título e a thumb, e responde se dá para entender sem a aula, se o
começo prende e o fim fecha, que emenda soa quebrada (com o tempo), se o título promete só o que o vídeo
entrega, e dá nota 0–10 com as correções. **Abaixo de 8 ou qualquer "não": corrija o plano e refaça.**
Na T14 A06 foram 3 rodadas: 6/6/7/5 → 7/7/7/6 → 8/8/8/8. Na 1ª, o que ele pega é quase sempre frase de turma, teaser que entrega pedaço
da história, começo que repete a frase anterior e fim sem ponto final; na 2ª, material da turma (planilha,
impresso), lista sem letreiro e borrão sem explicação. Na rodada seguinte, diga ao revisor o que já foi decidido
(ex.: "só a aula", limite do QR em 720p) para ele não pedir de novo, e peça a frase exata de cada correção. Para achar no tempo da aula o que ele
apontou no tempo do episódio: `"$P" scripts/achar.py <trabalho> --ep "<arquivo>" 13:16`.

## Armadilhas desta máquina

- **Nome de arquivo com dois-pontos** ("EP02 - Missão da empresa: ...") vira fluxo alternativo no NTFS e o mp4 sai
  com 0 byte; o render agora recusa `: ? " / | * < >` no `arquivo`. Use vírgula.
- `pgrep` não existe no Git Bash desta máquina: para encadear renders, espere pelo arquivo/log, não pelo processo.
- **Créditos da thumb:** o upscale 4x custa 180 créditos até ~600 px de largura e 270 acima disso. Recorte o busto
  com ~3,6× a altura do rosto e, se passar de 600 px, reduza antes de enviar.
- **Thumb A com rosto grande demais** (tarja cobrindo a boca): `thumb_legacy.py A ... --cabeca 290 --x 1030`.
- **Sala de Revisão:** o episódio vai inteiro, em partes de 6 min no depósito de arquivos da página (1 GB), não em
  `media/` (skill `sala-de-revisao`, "Vídeo longo"). Prévia curta não serve: o usuário quer comentar o vídeo todo.

- **h264_nvenc não abre** no PC de render ("Driver does not support the required nvenc API version 13.1, found
  13.0"): o ffmpeg do winget é mais novo que o driver. O render usa **libx264** (28 núcleos, rápido o bastante).
  Não atualize driver sem o usuário pedir.
- `cv2.QRCodeEncoder_Params()` usa `correction_level` (não `correctionLevel`); o leitor do OpenCV falha em QR
  denso pequeno: por isso a URL curta e o QR com pixels inteiros por módulo, colado depois da redução.
- O Python padrão do PC não tem numpy: use o da venv `corte-viral`.
- `robocopy` termina com código 1 quando copia (o PowerShell acusa "falhou"): leia o resumo.
- O áudio das aulas chega com pico acima de 0 dBFS (+2 dBTP): o render comprime de leve e normaliza; o
  conferir.py exige pico ≤ −1 dBTP.
- Comandos Python longos com aspas triplas dentro de heredoc no bash quebram: escreva um `.py` e rode.
- `cv2.imwrite` estraga nome de arquivo com acento no Windows ("sacrifÃ­cio"): grave com
  `cv2.imencode(".png", img)[1].tofile(caminho)` (o thumbs.py já faz).
- **Thumbs:** o detector de rosto acha também rosto de FOTO no slide (Stallone, Grant Cardone). O thumbs.py
  descarta rosto P&B e rosto com cabelo/chapéu (o Clailton é careca), mas **careca famoso passa** (Jeff Bezos
  apareceu como candidato): sempre olhe a folha e escolha à mão.
- O áudio vai com limitador (−3 dBFS) depois do loudnorm, e mesmo assim um **estalo de microfone** (plosiva no
  meio de uma palavra) pode passar de 0 dBTP depois do AAC (EP01 v3: +0,1). O render mede o pico real do mp4
  pronto e, se passou de −1, refaz só o áudio com o limitador mais baixo (`segurar_pico`, ~20 s). Para um mp4
  antigo: `"$P" scripts/render_episodio.py --so-pico "<arquivo.mp4>"`.
- **Adobe Podcast num episódio pronto** (EP03 T12A08, 21/10/2026: o usuário achou o áudio ruim no YouTube; fundo
  só 25 dB abaixo da voz, eco e zumbido de 60/120 Hz do auditório). O envio pelo Chrome aceita até 10 MB por arquivo:
  mande só a fala (0 → `duracao` do json do render, sem a vinheta) em 3 partes MP3 mono 192k cortadas em pausas.
  O Adobe tira a música da intro: remixe a `musica_abertura` do plano por cima da voz tratada (mesmo sidechain do
  render) e deixe a vinheta com o som original. Não use o compressor do `AUDIO_PRE` depois do Adobe (sobe o fundo
  5 dB); só passa-alta, ganho até −14 LUFS e `alimiter` com `latency=true` (sem isso o som atrasa 4 ms).
  **Use Fala 100%, Música 0%, Fundo 0%** (pedido do usuário em 21/10/2026, "precisa dar uma tratada mais forte", depois de "ainda ficou bem chiado" na v2 a 50%): a 50%
  o Adobe mistura metade do original e traz junto o chiado, deixando os "s" 6 dB mais ardidos que o próprio original
  (5–12 kHz sobre 300–3000 Hz, p95: v1 +14, 50% +20, 100% +2 dB). A 100% a correlação com o original cai para ~0,77
  (atraso continua 0) e o limitador tira ~0,6 dB (compense no alvo). Os ajustes do Adobe valem por arquivo e às vezes
  voltam para 50% ao trocar de arquivo na lista: confira com zoom antes de baixar (o nome sai `-esv2-100p-bg-m-music-m`).
  Script: `C:\Render\_youtube\legado_t12_aula08\audio_v2\juntar_v2.py 100p <saida.mp4> 0.6`.
  O `salvar_downloads.ps1` pega qualquer "Salvar como" do Chrome, inclusive de outra conversa: desligue logo depois.
- QR de 4 px por módulo (card compacto) lê no vídeo em 1080p; reduzido para 720p o leitor do OpenCV falha
  (celular costuma ler). O conferir.py só avisa; para TV/computador o vídeo roda em 1080p.
