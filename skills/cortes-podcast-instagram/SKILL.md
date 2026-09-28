---
name: cortes-podcast-instagram
description: Padrão aprovado pelo usuário para editar cortes de podcast em vertical para Instagram/Reels — locutor sempre centralizado (quem fala decidido pela VOZ), legenda palavra a palavra em SF Pro Text Black com sombra dupla discreta, edição simples só com legenda, e entrega numa pasta única com nomes legíveis. Use junto com a skill corte-viral sempre que o pedido for cortar/editar/legendar/enquadrar cortes de podcast, entrevista ou videocast para Instagram, Reels, TikTok ou Shorts, ou quando o usuário disser "mesmo padrão dos cortes do podcast", "edita esses cortes", "deixa vertical com legenda".
---

# Cortes de podcast para Instagram — padrão aprovado

Consolidado do projeto **Executoria Cast / Metal Glass** (2026-09-26), onde cada item abaixo
foi pedido, testado ou aprovado explicitamente pelo usuário. A seleção de momentos e o corte
seguem a skill `corte-viral` (fases 1–2); esta skill manda na **fase 3 (vertical + legenda)** e
na **entrega**.

## 1. O entregável

| Item | Padrão |
| --- | --- |
| Formato | 1080×1920, fps herdado (29,97), H.264 CRF 18, AAC 192k |
| Áudio | loudnorm −14 LUFS, pico −1 dBTP (o render da skill já faz) |
| Edição | **simples: só legenda**. Sem punch-in, card, B-roll, música, efeito |
| Respiro | não cortar pausas curtas (0,7–1,4s costumam ser retóricas); só o que o clip-builder já tirou |
| Duração | 30–60s (alvo 35–75, teto 90) |
| Pasta final | `Cortes Finais - <Nome do Projeto>` na **raiz do projeto**, arquivos `NN - Título legível.mp4` |
| Títulos | propor a lista para aprovação junto com o último teste; sem inflar número (ex.: "239%" sem base) |
| Versões antigas/testes | mover (não apagar) para `runs/<run>/output/versoes-anteriores/` |

Antes de gerar os 10: **fazer 1 corte de teste** (o de fundo mais difícil) e esperar aprovação.

## 2. Enquadramento: quem FALA fica no centro

Regra do usuário: centralizar sempre o rosto de quem está falando; com duas pessoas no mesmo
quadro, nunca o maior rosto nem quem escuta.

O que funcionou (e o que falhou):

- ❌ **Movimento de boca** (autoframe da skill): errou feio — a convidada que escutava bebeu água
  e olhou em volta e "ganhou" da que falava. Além disso o autoframe troca de pessoa com um pan
  de 150 px/s depois de ~6s: o recorte atravessa a mesa e ninguém fica no centro.
- ✅ **Quem fala = VOZ** (`scripts/voz.py`): MFCC + GMM diagonal (só numpy), treinado com 30–100s
  por pessoa de trechos inequívocos do próprio episódio (abertura do apresentador, apresentação
  de cada convidado). **Validar** em trechos separados, conferidos visualmente — exigir ~100%
  (deu 16/16 frases).
- ✅ **Onde está o rosto = YuNet** por plano de câmera (cortes do bruto via scene detect).
- ✅ **Lugar fixo** de cada convidado no plano duplo (conferir olhando quadros de todos os ângulos:
  quem senta à esquerda/direita). No Metal Glass: Fernanda (blazer) esquerda, Jane (blusa preta) direita.
- ✅ Decisão **palavra a palavra** (janela de voz de 1s em volta de cada palavra, margem ≥0,3);
  trechos <1s são absorvidos (um "Exato." do outro não troca o quadro).
- ✅ Troca de pessoa = **corte seco** no meio da pausa entre as frases.
- Plano de reação (fala alguém que não está no quadro): fica em quem aparece.
- Plano com um rosto só: recorte fixo nesse rosto. Zoom 1,0 quando o rosto já tem ≥17% da altura; teto 1,3.
- **Sempre conferir**: contact sheet com um quadro por trecho de cada corte; nos casos ambíguos,
  close das bocas das duas pessoas ao longo do tempo. Corrigir à mão o que a voz errar
  (anotar o motivo no `framing_reason`).

## 3. Legenda (estilo do vídeo de referência)

Referência: `C:\Users\NOT - LIVE\Documents\Você já viu alguém reclamar da empresa por anos, como se reclamar fosse um plano de carreira 🤔S.mp4`.
Exemplos visuais em `exemplos/`.

- **Fonte: SF Pro Text Black** (`fonts/SF-Pro-Text-Black.otf`, enviada pelo usuário — não usar Inter).
  No libass o nome que funciona é o **PostScript `SFProText-Black`** ("SF Pro Text Black" cai em Arial).
  Sempre passar `fontsdir`.
- Caixa-alta, branca. PlayRes 1080×1920: linha pequena **54**, linha grande **100**; centro do bloco
  em y=1150 (~60%, no peito, abaixo do rosto); largura máx. 860.
- Blocos de 1–4 palavras (≤24 caracteres, ≤2,2s); quebra em pausa >0,35s e pontuação.
  **Nunca** terminar bloco/linha em artigo, preposição, pronome ou intensificador ("A / GENTE",
  "SE TU TÁ SE"); **nunca** partir um termo de destaque entre blocos.
- **Linha grande só para destaque**: termos fortes curados por corte (`exemplos/destaques-*.json`)
  + números. Fica ~1/3 dos blocos, como na referência. Palavra comprida sem peso não vira destaque.
- Palavra a palavra: entra com alpha + desfoque 7→0 em 170ms; a linha desliza 14px em 220ms.
- **Sombra v3 (aprovada)**: halo difuso (bord 10, blur 22, alpha `8C` ≈45%) + sombra de contato
  (dx 1, dy 4, bord 2, blur 4, alpha `48` ≈72%). Sem contorno, sem tarja. A v1 (uma cópia preta
  com blur 14) sumia em fundo claro — blusa branca, parede lilás — e o usuário reclamou.
- Número por extenso → algarismo ("duzentos e trinta e nove por cento" → "239%").
- Palavra com <70% dentro do corte (rabo de palavra na borda) não entra na legenda.
- **Conferir palavras com Whisper** (`scripts/conferir_palavras.py`, large-v3-turbo, CPU) no áudio
  do corte renderizado. Corrigir só erro real de reconhecimento (ex.: "Emex"→"Amex",
  "Destocagem"→"Estocagem", frase que não fecha). **Não** aplicar as normalizações do Whisper
  ("tá"→"está", "pra"→"para", "né" sumindo): o VTT do usuário é mais fiel à fala.
  Correções entram em `CORRECOES` por corte, com o motivo comentado.

## 4. Transcrição

- Pedir ao usuário VTT/JSON com **uma palavra por legenda** (tempo por palavra). SRT/VTT por frase
  (1–2s por cue) não serve para cravar in/out nem para legenda palavra a palavra.
- Converter com `scripts/vtt_para_json.js` (node) para `segments[].words[]` e passar no `vch init`.
- Validar uma janela de 50s contra o Whisper antes de confiar (no Metal Glass: mediana 0,03s).

## 5. Pipeline (ordem que funcionou)

1. `corte-viral` fase 1: digest → context-mapper → clip-hunter → lista de momentos (parar no portão).
2. `corte-viral` fase 2: clip-builder → feed-psychologist → audit → blind-reviewer → dedupe →
   previews horizontais (parar no portão). REBUILD aplica as notas das revisões.
3. Vertical: `enquadrar.py` (voz + YuNet) → `montar_planos.py` (11-edit-plans.json, validar) →
   `render_limpo.py` (render_clip da skill + decupagem srt/ass) → contact sheets →
   `conferir_palavras.py` → `queimar_legenda.py` (teste em 1 corte, aprovar, depois todos).
4. Checagem final: 1080×1920, duração, −14 LUFS, blackdetect = 0, quadros com legenda.

Os scripts assumem o layout da run: copiar `scripts/` para `<run>/assets/`, `fonts/` para
`<run>/assets/fonts/`, e ajustar o que é **específico do episódio**:
`voz.py` (TREINO/TESTE com os trechos de cada voz), `enquadrar.py` (SEATS, esquerda→direita),
`legenda_ref.py` (CORRECOES), `destaques.json`, `queimar_legenda.py` (DEST e NOMES),
`render_limpo.py` (VIDEO) e o caminho `SK` da skill corte-viral (muda quando o plugin atualiza).

## 6. Armadilhas desta máquina (Windows)

- O lanchador `vch` é bash/Mac (`.venv/bin`): chamar `python scripts/vch.py` com o Python da venv
  (`%LOCALAPPDATA%\corte-viral\venv\Scripts\python.exe`) e `PYTHONUTF8=1`.
- A cópia instalada da corte-viral **não tem `models/`**: o YuNet fica em `models/` desta skill e
  deve ir para `%LOCALAPPDATA%\corte-viral\models\` — o OpenCV não abre caminho com acento ("Edições").
- Whisper na GPU (RTX 4070, float16, ~10x mais rápido) funciona desde 2026-09-26: os pacotes
  `nvidia-cublas-cu12` / `nvidia-cudnn-cu12` estão na venv e as pastas `bin` deles precisam ser
  registradas (`os.add_dll_directory`) antes de carregar o modelo — ver `carregar_whisper()` em
  `scripts/conferir_palavras.py`. Sem isso dá `cublas64_12.dll` ausente; aí, CPU int8.
- `ffmpeg drawtext` dá segfault (fontconfig): não usar para rotular quadros.
- Ao extrair quadro para conferir legenda, usar `-ss` **depois** do `-i` (senão o ASS recomeça do zero).
- Aviso sonoro para tarefas >1 min já está configurado (hook em `~/.claude/settings.json`).
