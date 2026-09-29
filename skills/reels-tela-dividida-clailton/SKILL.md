---
name: reels-tela-dividida-clailton
description: Edita reels no formato TELA DIVIDIDA do Instagram do Clailton (Legacy Educação) a partir do bruto (4K, câmera deitada ou não) e do roteiro — decupagem e corte colado na voz (da skill novela), gancho em tela dividida com imagem em cima e tarja preta na emenda, Clailton em aberto/fechado com punch-in nos fechos de frase, cenas de filme/série/desenho (cultura pop) em tela cheia entrando na palavra que ilustram (busca automática em YouTube/TikTok/DuckDuckGo, ranking por CLIP, filtros de marca d'água, texto queimado e logo), foto só para fato, cartão para print, legenda pequena SF Pro Text Black com sombra v3, flash na saída do gancho, CTA digitada e camada de estilo "película" (textura de papel e retícula fixas, grão, poeira, cor contida, vinheta). Entrega 1080x1920 em qualidade máxima e, se pedido, pacote para o Premiere (XML FCP7 + mídia + legenda com transparência). Use sempre que o pedido for editar/finalizar um reel "TD"/"tela dividida" do Clailton, arquivos Reels_Clailton_TD_*, "edita com imagens", "reel com imagem em cima", "igual ao Não confie no ser humano", ou exportar esse reel para o Premiere.
---

# Reels TELA DIVIDIDA — Clailton

Padrão medido nos 6 reels da equipe (Não confie no ser humano 1,81 mi · Me mostra teu quarto 561 mil ·
Fórmula 316 mil · Duty Free · STF · 6 tipos). **Números e regras: `referencia/estilo-tela-dividida.md`.
Como decidir as imagens: `referencia/regras-plano-visual.md`** (leia antes de escrever o plano).

## O entregável

| Item | Padrão |
|---|---|
| Formato | 1080×1920, 29,97 fps, H.264 High CRF 10 slow, BT.709, AAC 320k (~75 Mb/s com o estilo); voz −14 LUFS / −1 dBTP |
| Gancho (0–3/8 s) | tela dividida: imagem em y 0–768, Clailton embaixo; legenda vira **tarja preta** na emenda; saída com **flash** |
| Clailton | parado; **aberto** (rosto 30% da largura) e **fechado** (1,5×) por corte seco; fechado nos fechos de frase e depois de emenda de tomada (automático). **Regras de zoom do usuário (28/09/2026), padrão:** zoom seco (aberto ↔ fechado) **só na emenda**; fora da emenda só **zoom animado** (keyframes, entrada/saída suaves, ~18% em 0,55 s no rabo da frase, segura até a emenda); **todo zoom mantém os olhos na mesma altura** (fechado e zoom animado ampliam em volta do ponto entre os olhos). Detalhes na skill da edição simples, seção "Zoom" |
| Imagem | ~30–40% do tempo, entra no início da palavra que ilustra; **padrão = cena de cultura pop em vídeo** (filme, série, desenho) que mostra o que ele fala; foto só para fato (pessoa, marca, livro, notícia), com zoom-out ~5%/s; vídeo sem zoom e sem som; cartão para print; `dividida` quando ele comenta a imagem |
| Tempo mínimo na tela | **nada pisca**: imagem/cena ≥ 1,0 s; Clailton entre duas imagens ≥ 1,0 s (menos que isso a imagem emenda na próxima); sobra do Clailton colada numa emenda de tomada (< 0,5 s) vira imagem. Automático em `plano_td.py`; exceção só com `rapido` na linha (lista, ≥ 0,6 s) |
| Enquadramento do B-roll | recorte no ASSUNTO, por plano da cena: o reenquadramento testa 9 posições do 9:16 (e 5 da faixa de cima) e fica com a que mostra a ação E o personagem, sem cortar rosto ao meio; entrada do trecho sem pedaço de outra cena nas pontas |
| Estilo "película" | **só no B-roll** (tela cheia de imagem: o quadro todo; tela dividida: só a faixa de cima; o Clailton fica limpo), antes da legenda: textura de papel + retícula de pontinhos (4,43 px, 14°) FIXAS na tela, grão animado leve, poeira de 1–2 quadros, saturação 0,85, curva em S leve, vinheta. Medido na referência do usuário (instagram.com/p/Dc1tvV3sTO-) e calibrado para sobreviver à recompressão do Instagram. Força por vídeo: `ESTILO 0.7` no plano (0 desliga) |
| Legenda | 1–4 palavras, SF Pro Text Black maiúscula 34 px, y=1175, sombra v3, troca seca na palavra |
| Final | CTA preta digitada (a da novela) com clique de teclado; `SEMCTA` no reel de salvamento |
| Pasta | `Reels Editados/<nome> - EDITADO.mp4` na raiz do projeto; trabalho em `_trabalho/<slug>/` |
| Premiere (opcional) | `Reels Editados/<nome> - PREMIERE/` (XML + mídia + legenda_alpha.mov + legenda.srt) |

**Portão:** o 1º vídeo de um lote é mostrado ao usuário antes dos outros (com `--geral`), incluindo
`qa/fundo_mais_claro.png` (regra global: legenda testada no fundo mais claro).

**Sem música e nada na nuvem:** música entra depois, pelo usuário. Gemini (plugin /watch)
foi testado em 27/09 e descartado "por enquanto" (lento, falhou com 503, e manda o vídeo
para fora); não propor de novo sem ele pedir. Lacuna que o teste mostrou e as folhas de
revisão não pegam: imagem que contradiz a fala, legenda branca sobre imagem branca e
palavra faltando no áudio — confira isso a olho na revisão.

## Ambiente (Windows)

- `P = %LOCALAPPDATA%\reels-novela\venv\Scripts\python.exe` (ou `...\corte-viral\venv\...`), sempre com
  `PYTHONUTF8=1`. `S = %USERPROFILE%\.claude\skills\reels-tela-dividida-clailton\scripts`.
- Depende da skill **reels-novela-clailton** instalada (transcrição, decupagem, corte, alinhamento,
  fonte/kerning, CTA, áudio) e da venv do alinhador (`venv-align`: torch CUDA; roda o CLIP).
- Extras: `yt-dlp`, `ddgs` e `curl_cffi` (TikTok) na venv principal, `timm` na venv-align (detector de
  marca d'água), Node (JS do YouTube), modelo `openai/clip-vit-large-patch14` no cache do Hugging Face
  (1,6 GB); `models/` da skill: detector de marca d'água (LAION) e de texto (PP-OCRv3), baixados sozinhos.
  `P S\verificar_td.py` confere tudo antes do 1º vídeo.

## Modo rápido — ~10–15 min por vídeo (medido: teste de 1:44)

`T = <projeto>\_trabalho\<slug>`.

0. **Roteiro** — `P S\td.py roteiro "<roteiro.md|.docx|.txt>" T`: separa a fala (`T\roteiro.txt`, que a
   decupagem compara) do 1º FRAME + MAPA DE ÂNCORAS (`T\ancoras.txt`, base do plano visual). Colado na
   conversa: grave o texto em um .md e rode o mesmo comando.
1. **Preparar** — `P S\td.py preparar "<bruto>" T` (~15 s–1 min). Igual à novela.
2. **Revisar a decupagem** — como na novela (`decupagem_proposta.txt` → `decupagem_ajustes.txt` →
   `P <novela>\scripts\decupar_auto.py T --aplicar T\decupagem_ajustes.txt`). Regras: SKILL da novela.
3. **Montar** — `P S\td.py montar T` (~20 s–1 min): corte colado na voz + alinhamento e, junto,
   **rotação automática** (câmera deitada) + recortes aberto/fechado/dividida por tomada.
   Aviso "bruto fechado" = rosto já grande no quadro: o aberto fica o mais aberto possível.
   No fim roda `emendas_literal.py` (skill novela): transcrição literal de cada emenda. **"REPETIÇÃO NA
   EMENDA"** = gaguejo colado no corte ("E... e você sabe", "mas... mas sem destino"): junte o ajuste
   sugerido de `T\emendas_literal.txt` ao `decupagem_ajustes.txt`, `--aplicar` e `montar` de novo.
4. **Plano visual (você)** — leia `T\palavras_legenda.txt` (+ `T\ancoras.txt`, se houver) e escreva
   `T\plano.txt` seguindo `referencia/regras-plano-visual.md`: **para cada trecho, a cena famosa que
   mostra aquilo** (cultura pop em vídeo; foto só para fato). Uma linha por imagem; o resto é
   automático. `P S\td.py plano T` → confira `T\timeline.txt` (ritmo, % de imagem, avisos).
5. **Buscar** — `P S\td.py buscar T` (~2–4 min com 15 cenas; 1 item com `--so`: ~30 s): filme/vídeo
   pelo YouTube (2 vídeos por item, canal oficial primeiro) + TikTok (1; cena já na vertical — o TikTok
   às vezes bloqueia o IP: segue só com o YouTube); o CLIP acha a janela da cena na prévia de 1 quadro/s
   e só as 2 melhores janelas descem em HD. Imagem pelo DuckDuckGo (PT + EN; troca de backend sozinho
   quando volta lixo). Filtros: marca d'água, texto queimado (legenda/crédito/legenda de TikTok), logo
   escrito no canto, PNG falso, tarja. Depois do HD, o **reenquadramento** (`reenquadrar_td.py`) refaz a
   nota de cada trecho pelo que APARECE no recorte (ação + nome do filme + nitidez/luz + rosto inteiro).
   A resolução conta pelo quanto o recorte é ampliado: em tela cheia, abaixo de 720p fica borrado.
   Folhas `T\qa\candidatos_NN.jpg` (até 4 candidatos por item, já no recorte escolhido). Etiqueta
   vermelha:
   - MARCA?, TEXTO, LOGO?;
   - **LARGA** — no 9:16 a cena perde o sentido. `LARGA→div` = na faixa de cima funciona: troque a
     linha para `dividida` e rode `td.py plano`, sem buscar de novo;
   - **ESCURO**;
   - **BAIXA** — resolução baixa para tela cheia;
   - **PISCA** — pedaço de outra cena de menos de 0,6 s, ou corte a cada menos de 0,9 s (edição de fã,
     trailer): evite; é o "piscou" que o usuário reprovou.

   Olhe as folhas como o espectador ("dá para entender em 1 s?"), inclusive **logo de streaming
   desenhado (hulu, Netflix, FOX)**, que o detector de texto não pega. Escreva só as trocas em
   `T\escolhas.txt` (`b03 2`, `b14 igual b07`) e `P S\td.py escolher T`.
   Item sem candidato bom: melhore a busca no plano, `td.py plano T` e `td.py buscar T --so b05`.
   Ilustração gerada: salve em `T\midia\<id>.png` (tipo `ia`).
6. **Prévia (opcional)** — `P S\td.py previa T 20` (render rápido dos 20 s iniciais).
7. **Finalizar** — `P S\td.py finalizar T "<projeto>\Reels Editados\<nome> - EDITADO.mp4" [--premiere] [--geral]`
   (medido no teste de 1:44: legenda 1 s, render com estilo 153 s, conferência ~50 s, Premiere 30 s).
   Código 0 = aprovado. `--estilo 0` no render = sem a camada película (render ~95 s).
8. **Olhar** — `T\qa\folha_imagens.jpg` (cada imagem com a fala: a correlação está certa?),
   `T\qa\fundo_mais_claro.png`, `T\qa\relatorio.txt` (avisos, **fontes das imagens**). No 1º do lote,
   também `folha_geral_NN.jpg`.
9. **Entregar** — vídeo (+ pasta PREMIERE) e relatório curto: tempo por etapa, diferenças fala × roteiro,
   imagens com possível direito autoral (trecho de filme) ou marcadas "MARCA?", decisões a confirmar.

Correções: trocar imagem → `escolhas.txt` + `td.py escolher` + `finalizar`; mudar tempo/imagem →
`plano.txt` + `td.py plano` (+ `buscar --so`) + `finalizar`; trocar tomada → decupagem → `montar` →
refazer o plano (os índices mudam).

## Economia de tokens e tempo

- Uma conversa por vídeo (ou lote pequeno); modelo escolhido antes, sem trocar no meio.
- O que custa token é olhar imagem: **folhas de candidatos (1–3) + folha de imagens + fundo mais claro**.
  Não abra imagem por imagem. `folha_geral` só no 1º vídeo do lote.
- O plano é curto (15–30 linhas). Não escreva legenda nem zoom: saem por regra.
- Lote: o agente `td-planejador` escreve o plano de outro vídeo em paralelo (com prazo de 6 min).

## Onde ajustar

| Quero mudar | Onde |
|---|---|
| altura da emenda, enquadramento aberto/fechado, zoom da foto, cartão, flash | `td_comum.py` (bloco de constantes) |
| tempo mínimo na tela (imagem, Clailton entre imagens, lista rápida) | `plano_td.py` (`MIN_IMAGEM`, `MIN_CLAILTON`, `MIN_RAPIDO`, `MIN_LASCA`) |
| recorte do B-roll no assunto, entrada do trecho, LARGA/ESCURO | `reenquadrar_td.py` (`N_POS`, `MIN_PLANO`, `MARGEM`, `ESCURO`) |
| tamanho/posição/espaçamento da legenda, tarja, número grande, etiqueta | `td_comum.py` (`LEG_*`, `TARJA_*`, `NUMERO_*`, `ETIQUETA_*`) e `legenda_td.py` |
| quebra das telas de legenda, trocas "tô→ESTOU", censura (EST*PRO) | `plano_td.py` (`custo_tela`, `TROCAS`, `CENSURA`, `FRACAS`) |
| regra do aberto/fechado e do zoom animado | `plano_td.py` (`auto_zoom_cortes`) e `td_comum.py` (`ZOOM_SUAVE*`, `PLANO_MIN`, `FECHADO_MAX`, `ABERTO_MAX`); `ZOOMLIVRE` no plano volta ao `auto_fechado` antigo (zoom seco no meio da fala — o usuário reprovou) |
| zoom ancorado nos olhos | `td_comum.py` (`rect_zoom`); olhos por tomada em `enquadrar_td.py` (YuNet) |
| fontes de imagem, filtros, marca d'água, ranking | `buscar_td.py` (`BLOQUEADOS`, `LIMITE_MARCA`, `prior`, `CANAIS_OFICIAIS`) e `clip_rank.py` |
| quantos vídeos por cena, prévia, HD | `buscar_td.py` (`N_YOUTUBE`, `N_TIKTOK`, `QPS`, `HD_POR_ITEM`, `ITENS_JUNTOS`) |
| camada película (textura, retícula, grão, poeira, cor, vinheta) | `estilo_td.py` (constantes no topo); força geral `ESTILO_FORCA` em `td_comum.py`; por vídeo `ESTILO 0.7` no plano ou `--estilo` no render |
| corte/ritmo/áudio/CTA | skill novela (`comum.py`, `montar_corte.py`, `legenda_novela.py`) |

## Premiere

`--premiere` gera o XML (Final Cut 7) que o Premiere abre em **Arquivo > Importar**: V1 = bruto 4K por
plano com Movimento (escala/posição/rotação; entrada/saída exatas, com sobra para ajustar o corte);
V2 = imagens/vídeos já recortados (foto com zoom-out em quadros-chave); V3 = `legenda_alpha.mov`;
A1/A2 = voz do bruto por trecho com o ganho; A3 = áudio final (desligado). `legenda.srt` para editar o
texto. Fica só no MP4: o flash da abertura, o limitador de pico e a camada película — a textura fixa
vai em `estilo_textura.png` (arraste para uma trilha acima de tudo, modo **Sobrepor**; a cor e a vinheta
dá para chegar perto com Lumetri). A conta do Movimento foi conferida contra o render; a importação em
si ainda não foi aberta no Premiere (confira o 1º projeto).

## Armadilhas já resolvidas (não repetir)

- **Bing sem navegador devolve lixo** depois de algumas buscas ("balde furado" → jogador Balde do
  Barcelona; "leaking bucket" → streamer preso). Busca principal = DuckDuckGo (`ddgs`), PT + EN.
- **Marca d'água**: prévia de banco (Freepik premium = mosaico "Magnific", Unsplash+, Designi, pngtree,
  Westend61, dreamstime re-hospedado no Pinterest) passa pelo domínio. Filtro de domínio + detector da
  LAION (`models/watermark_model_v1.pt`, EfficientNet-B3 via timm; `LIMITE_MARCA` 0,6) + o "cara de
  banco" do CLIP só quando destoa dos outros candidatos do item. O CLIP zero-shot sozinho NÃO serve:
  foto de banco limpa (aperto de mão, balde em fundo branco) pontua tão alto quanto a com marca.
  "MARCA?" na folha = conferir em tamanho real.
- PNG "transparente" com quadriculado gravado: `xadrez()` descarta.
- **Tarja preta de filme** (2,39:1 dentro de 16:9 no YouTube): `cropdetect` antes do recorte.
- **Legenda sobre RGB fica cinza** (branco 235): com "YCbCr Matrix: TV.709" o libass comprime a cor.
  A legenda entra DEPOIS da conversão para YUV; na camada transparente do Premiere o .ass vai com
  "YCbCr Matrix: None".
- **Saída rawvideo sem `-fps_mode passthrough` duplica o 1º quadro** quando a busca cai entre quadros
  (plano inteiro 1 quadro atrasado; a conferência de sincronia pegou). Toda decodificação usa passthrough.
- Corte a até 6 quadros de uma emenda de tomada vai para a emenda (senão sobra plano de 1–5 quadros).
- Bruto da tela dividida vem com a câmera deitada e sem metadado: rotação por detecção de rosto.
- Miniatura do YouTube (`i.ytimg.com`) tem texto/cara de youtuber: penalizada no ranking.
- **Texto queimado** (legenda do YouTube, crédito de abertura de filme, legenda de TikTok): detector de
  texto só dentro do recorte que vai aparecer; a janela do trecho foge do texto (Delírios de Consumo:
  créditos em 96–102 s, janela escolhida em 101 s sem crédito no 9:16).
- **TikTok** bloqueia o yt-dlp puro: `--impersonate chrome` (pacote `curl_cffi`). Busca de TikTok = busca
  de texto do DuckDuckGo "tiktok <cena>" (acha as contas oficiais, ex. @breakingbad, em 1080x1920).
- Link de qualquer site no plano (`url=` TikTok, Instagram, X...) é baixado inteiro e cortado aqui.
- Agente em segundo plano pode travar: sempre com prazo (lição da novela).
- **Grão que muda a cada quadro some no Instagram** (recompressão ~2,8 Mb/s) e só engorda o arquivo
  (1,5 GB e render 3,8× mais lento na 1ª versão). O que a referência tem — e sobrevive — é textura
  FIXA na tela (correlação 0,84–1,00 entre quadros vizinhos). Calibre o estilo pelo resultado depois do
  Instagram simulado (VP9 2,8 Mb/s), nunca só pelo master.
- **Logo de streaming** (hulu, Netflix): não é texto para o PP-OCR; olhe o canto na folha de candidatos.
- **B-roll ilegível** (reprovado no v2): recorte 9:16 no centro de cena 16:9 (O Lobo de Wall Street
  virou "nada"), trecho de 272 px de altura ampliado 7× em tela cheia, cena escura, e cenas de 0,7 s
  que "piscaram". Resolvido com reenquadramento por plano, nota pela ampliação, ESCURO/LARGA na folha
  e tempo mínimo de 1 s. O CLIP recorta o CENTRO da imagem: para dar nota ao recorte vertical, ele vai
  inteiro dentro de um quadrado cinza (senão o CLIP vê só o meio do 9:16).
- Repetição (`igual`) mais longa que o trecho original congelava no fim: a busca baixa a duração do
  maior uso, e a conferência compara quadros em miniatura (o grão da película muda todo quadro).
- **Trecho velho passando por novo:** o download em HD falhou (403 do YouTube) e ficou o arquivo de
  mesmo nome da busca anterior. Agora o arquivo é apagado antes de baixar.
- **Entrada escolhida para a duração errada:** o uso real é mais curto que o trecho baixado, e o fim
  do uso caía num pedaço de 0,17 s de outra cena. A entrada é escolhida para TODAS as durações de uso
  da mídia (o item e as repetições começam no mesmo ponto).
- Fantasia/Disney: quase todo upload no YouTube é bloqueado, e o TikTok bloqueia o IP às vezes. Com
  `url=` de um vídeo que funciona, dá para usar momentos diferentes do MESMO vídeo em itens
  diferentes (balde, água, inundação), cada um com a sua janela.
  Cortina/cena escura no topo não é tarja: a conferência só avisa quando há degrau preto → imagem.
- Zoom animado: o plano é decodificado no recorte aberto em resolução maior e ampliado quadro a quadro
  em volta dos olhos (`render_td.quadro_zoom`); a conferência de sincronia pula esses planos. No pacote
  do Premiere ele vai já pronto (`midia/clailton_zoom_NNN.mp4`), sem o bruto por baixo.
- O `seg` das palavras vinha do tempo do Whisper (antes do alinhamento): o zoom por emenda caía no
  pedaço errado. O `alinhar.py` recalcula e o `plano_td` usa o tempo alinhado.
