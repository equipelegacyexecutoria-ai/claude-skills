---
name: cortes-youtube-legado
description: Transforma as aulas gravadas do Legado Empresarial (presenciais no auditório, com o Clailton falando; 2–3 h cada, no Drive em "LEGADO - AULAS AO VIVO") em episódios de 15 a 45 minutos para o YouTube, cada um com começo, meio e fim — acha a aula no Drive, transcreve palavra a palavra, monta o mapa de temas, escolhe os episódios, corta (sem avisos, intervalos, apresentação de aluno, vídeo de terceiros no telão nem música), abre com 15–40 s do trecho mais forte, coloca o card "SESSÃO ESTRATÉGICA GRATUITA" com QR code (igual ao Executoria Cast) em 3 momentos estratégicos, trata o som, confere tudo e entrega em ORGÂNICO > EDITADO do mês com título, texto da thumb, descrição com capítulos e link da sessão estratégica, tags, comentário fixado, legenda .srt e quadros do Clailton para a thumb. Use quando pedirem "cortes do Legado para o YouTube", "transforma a aula em episódios", "corta as aulas do Legado", "vídeo longo das aulas", "aula do auditório para o YouTube", "cortes de 15 a 45 minutos", ou mandarem uma aula/turma do Legado para virar vídeo do YouTube.
---

# Cortes do Legado para o YouTube (episódios de 15–45 min)

Pedido do usuário (13/10/2026), ideia do Clailton: as aulas do **Legado presencial** (Clailton no auditório)
viram episódios de YouTube de **15 a 45 min**, cada um **com começo, meio e fim**, com **CTA de QR code para a
sessão estratégica** igual ao do Executoria Cast (youtube.com/watch?v=v0jEA57pYL8, card no canto aos 17:08), e a
**descrição direcionando para a sessão**. Edição: **só a aula** (sem vinheta, sem legenda queimada, sem música).
Primeira aula feita: Turma 12 · Aula 10 (Inovação) → 3 episódios (exemplo completo em `exemplos/t12a10_plano.json`).

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

## Onde está cada coisa

| Item | Onde |
| --- | --- |
| Aulas | `G:\Meu Drive\LEGADO - AULAS AO VIVO\TURMA NN\...` — **presenciais (auditório): Turma 12, 13, 14, 17**; Turma 15 e 16 são **online** (Zoom/OBS, não usar sem o usuário pedir). Turma 14 tem aulas de alunos apresentando (SWOT, aula 06): só servem os trechos do Clailton |
| Link da sessão estratégica | `https://formulario.legacyexecutoria.com.br/` (o da bio do Instagram, conferido em 13/10/2026; o antigo `lp.legacyexecutoria.com.br/form-organico` **não existe mais**). Antes de cada aula, abrir o link e ver se responde "Legacy Educação — Agendamento"; se mudou, pegar o novo na bio do @legacyexecutoria |
| UTM | `utm_source=organico&utm_medium=youtube&utm_campaign=<codigo>e<N>` (+ `&utm_content=descricao` / `comentario`). `codigo` = turma+aula curto, ex.: `t12a10`. O `utm_source=organico` é o que o relatório do orgânico (cerebro-legacy) já filtra |
| Trabalho local | `C:\Render\brutos\legado_tNNaNN\` (cópia da aula) e `C:\Render\_youtube\legado_tNNaNN\` (transcrição, plano, render, qa, thumbs) |
| Python | `%LOCALAPPDATA%\corte-viral\venv\Scripts\python.exe` (tem faster-whisper com CUDA, OpenCV 4.10, Pillow, numpy) com `PYTHONUTF8=1`. Pacotes: `requirements.txt` |
| Pesquisa que embasa as regras | `references/pesquisa-youtube.md` (13/10/2026, com fontes) |

## Passo a passo

Rode no **PC de render** (`~/.claude/maquina.json` → `"papel": "render"`). Scripts em `~/.claude/skills/cortes-youtube-legado/scripts/`.
`P="$LOCALAPPDATA/corte-viral/venv/Scripts/python.exe"`, sempre `PYTHONUTF8=1`.

1. **Achar a aula.** Liste `LEGADO - AULAS AO VIVO`, meça com `ffprobe` e tire 8 quadros espalhados (`ffmpeg -ss`)
   para ver se é auditório e quem fala. Aula em várias partes (pasta `AULA 02\` com 3–4 arquivos): junte na ordem.
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
   continuar o sentido.
6. **Escrever o `plano.json`** (formato no topo de `scripts/render_episodio.py`; exemplo em `exemplos/`):
   trechos, abertura, CTAs (instantes da aula) e o bloco `meta` (títulos, thumbs, resumo, bullets, capítulos,
   tags, hashtags, fatos imprecisos). Confira com `"$P" scripts/render_episodio.py <trabalho> --so-mapa`
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
    Drive (conector `search_files`), publique a página de revisão (Artifact) com os links e mande o resumo.

## Regras do episódio (o que é "começo, meio e fim")

- **1 episódio = 1 problema + 1 resposta**, que se entende sem ter visto o resto da aula. Alvo **18–35 min**,
  mínimo 15, máximo 45. Uma aula de 1h45 rendeu 3 (19, 23 e 26 min); de 3 h, espere 4–6.
- **Começo:** a 1ª frase que apresenta o problema ou a história (ex.: "1932, o ano em que foi criada a Lego").
  Nunca "boa noite", aviso, "como eu falei semana passada".
- **Meio:** blocos de 3–8 min na ordem da aula. Pode juntar blocos não vizinhos do mesmo tema (ex.: história
  de abertura + parte central), desde que a emenda faça sentido falada. Retomada de assunto do começo
  ("é isso que quase quebrou aquela empresa, a Lego") é ouro: fecha o laço.
- **Fim:** a conclusão, a moral ou uma pergunta de reflexão do próprio Clailton ("Como eu posso melhorar?").
  Nunca terminar em "agora vamos para a dinâmica", "pessoal de casa".
- **Abertura (cold open, 15–40 s):** o trecho mais forte do próprio episódio (frase-tese, pergunta, virada de
  história), sem entregar a solução. Entra antes do começo, com um mergulho de 0,3 s no preto. Nas pausas
  da abertura, nada acima de 1,2 s. Exemplos: "o problema é o líder desqualificado..." (EP1), "o nome dessa
  empresinha chamava-se Netflix... olha o nosso tamanho" (EP2), "o Alex... é o nosso maior vendedor" (EP3).
- **Pausas sem fala > 2,5 s** viram 0,9 s sozinhas (o render faz). Risada/aplauso curto fica.
- **Direitos autorais:** nada de vídeo de TV/terceiros nem música de animação. Se a fala do Clailton depende
  do vídeo, mantenha só a parte dele que se sustenta (ex.: o pipoqueiro de Curitiba: apresentação + comentário
  depois, sem a reportagem).
- **Aluno identificável falando** (apresentação de trabalho): fora, sem autorização.

## CTA da sessão estratégica (QR)

- Card igual ao do Executoria Cast (`scripts/qr_card.py`): caixa azul em degradê, QR em quadro branco à
  esquerda, "SESSÃO / ESTRATÉGICA / [GRATUITA] / APONTE A CÂMERA". Maior que o original (escala 1,65 ≈
  500×250 px, QR ~185 px em 1080p, 5 px por módulo) porque a pesquisa mostrou que QR pequeno não lê da TV.
- **3 por episódio, 30 s cada:** ~25–35% do vídeo, ~70–80% e perto do fim (até 25 s antes do fim; nos últimos
  5–20 s fica a tela final do YouTube). **Estratégico** = logo depois de um ponto que dá vontade de ajuda: quando
  o Clailton fala do que a Legacy faz dentro da empresa, depois da moral de uma história, depois de "eles
  participaram do meu treinamento". Nunca em cima do clímax de uma história.
- **Canto automático:** o render escolhe, a cada CTA, o canto com menos coisa (sem rosto, sem texto de slide,
  sem área clara do telão); preferência pelo superior esquerdo. Forçar: `"cantos": {"2": "sd"}` no episódio
  (`se`, `sd`, `ie`, `id`).
- **URL curta no QR** (≤ 106 caracteres → QR versão 5): sem `utm_content`. O `conferir.py` lê o QR no vídeo
  final, nas 3 posições de cada CTA; se não ler, reprova.
- Quem assiste no celular não escaneia a própria tela: por isso a **descrição abre com o link** e o comentário
  fixado repete o link.

## Título, thumb e descrição (pesquisa em `references/pesquisa-youtube.md`)

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

Mande um agente (`general-purpose`) ler, para cada episódio, só: a abertura, os 90 primeiros e os 90 últimos
segundos de texto (`qa/<arquivo>_qa.json`), a transcrição do episódio inteiro (`palavras_no_episodio`) e o título.
Ele responde: (1) dá para entender sem ter visto a aula? (2) o começo prende e o fim fecha? (3) tem emenda que
soa quebrada (cite o tempo)? (4) o título e a thumb prometem só o que o vídeo entrega? (5) nota 0–10.
Abaixo de 8 ou qualquer "não": corrija o plano e refaça.

## Armadilhas desta máquina

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
