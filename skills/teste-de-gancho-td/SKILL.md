---
name: teste-de-gancho-td
description: Teste de gancho em reels TELA DIVIDIDA (TD) do Clailton já publicados — troca só os primeiros segundos do reel editado por um gancho novo (V2, V3...) e mantém o resto idêntico. Escreve as variações (ou usa as que o usuário trouxer prontas), gera a fala na voz clonada do Clailton no HeyGen (Chrome), usa o Clailton real de um trecho do bruto com só a boca sincronizada (Magnific lipsync-2.0), monta a tela dividida igual à do original (imagem em cima, legenda medida, sombra v3, flash), casa voz, ambiente e cor, emenda no quadro exato e entrega no Drive (VARIAÇÕES TELA DIVIDIDA), na Sala de Revisão e em cards Reels_Clailton_TD_TESTE_*_V2 em Aprovação. Use para "teste de gancho", "variação de gancho", "faz V2 e V3 desse reel", "troca o começo do reel", "teste A/B de abertura", "refaz o gancho dos reels que menos performaram" ou ganchos prontos para um reel TD já editado. Só tela dividida por enquanto.
---

# Teste de gancho — reels TELA DIVIDIDA do Clailton

Feita a partir do teste de 10–11/10/2026 (Padre Antônio, Termômetro, A Pessoa Na Chegada: aprovados e
publicados como `Reels_Clailton_TD_TESTE_*`). O usuário não é técnico: fale de "gancho", "começo do vídeo",
"voz", "boca", nunca de script, config ou venv.

## O que o usuário recebe

Para cada reel: V2 e V3 (às vezes mais), cada uma com **só o gancho trocado**. Do quadro do corte em
diante é o reel publicado, sem mudar nada. Arquivo 1080×1920, H.264 CRF 18, AAC 320k, mesmo padrão dos reels.

- **Nome:** `Reels_Clailton_TD_TESTE_<resto da pauta>_V2` (TESTE logo depois do formato; regra de 13/10/2026),
  no arquivo e no card.
- **Drive:** `G:\Meu Drive\02. Captação de Vídeos\<AAAA>\<MM - Mês>\ORGÂNICO\EDITADO\VARIAÇÕES TELA DIVIDIDA\<Título do reel>\`
  (uma subpasta por reel, com as variações dentro; o mês é o da entrega).
- **Sala de Revisão:** cada variação sobe como um vídeo (skill `sala-de-revisao`).
- **Notion:** um card por variação em **Aprovação** (modelo no passo 10).

## Antes de começar

1. **Onde:** pedido sem dizer onde → pergunte "aqui ou no PC de render?" (regra global). No PC de render,
   entregue o pedido à conversa "Central de Render", como na skill `fila-de-render`.
2. **Quais reels:** os que o usuário apontar ou, se ele pedir "os que menos performaram", os da análise
   de performance mais recente do perfil (procure a conversa/documento da análise; confirme a lista com ele).
3. **Ganchos:**
   - **O usuário trouxe as variações prontas** → use o texto dele literalmente (sem "melhorar"); só confira
     se cada uma emenda bem na frase que continua o vídeo e avise se alguma não emendar.
   - **Não trouxe** → escreva 2 por reel e mostre antes de produzir. Regra que o teste validou: abrir com
     uma **tese forte sobre a vida de quem assiste** ("Se você morresse amanhã, a tua empresa abriria as
     portas na segunda-feira?") e só depois a história como prova; nunca começar pela história de outra pessoa
     ("Ele…", "Esse homem…"). O gancho novo tem que **emendar na frase que continua o vídeo** (mostre ao
     usuário: sai X, entra Y, o vídeo segue igual a partir de Z). Até ~7 s falados.
4. **Portão:** faça a **primeira variação inteira e mostre** antes das outras (o usuário aprova a boca, a voz
   e a emenda). Depois faça as demais em lote.

## Ambiente

- `P` = Python da venv com cv2 + faster-whisper (`%LOCALAPPDATA%\corte-viral\venv\Scripts\python.exe` ou
  `%LOCALAPPDATA%\reels-novela\venv\Scripts\python.exe`), sempre com `PYTHONUTF8=1`.
  `S` = `$HOME/.claude/skills/teste-de-gancho-td/scripts`. O `casar_voz.py` acha sozinho a venv com
  `demucs` (normalmente `reels-novela\venv-align`); faltando, instale pelo `requirements.txt` da skill.
- Usa da skill `reels-novela-clailton`: detector de rosto (`models/`), fonte Inter ExtraBold (`fonts/`) e
  `scripts/salvar_downloads.ps1`.
- Pasta de trabalho `W`: no PC de render `C:\Render\_trabalho\ganchos\<AAAA-MM-DD>`; na estação, uma pasta
  em `C:\Render\_trabalho\` também (precisa de ~5 GB por reel).
- Conectores: Chrome do usuário (Claude in Chrome) logado no HeyGen; Magnific (ferramentas `video_speak`,
  `creations_*`, `images_generate`); Notion; Frame.io (skill `frameio`); Google Drive para computador (G:).

Estrutura de `W`:

```
W/ganchos.json            plano (reels, textos, imagens de cima)  -> formato no topo de scripts/montar.py
W/<reel>/original.mp4     reel editado/publicado
W/<reel>/medidas.json     medidas do gancho original (medir_original.py)
W/<reel>/img/             desenhos/fotos novos do gancho
W/vozes/<nome>.wav        fala do HeyGen de cada variação  (nome = <reel>_v2, <reel>_v3)
W/vozes/frases.json       tempo de cada palavra de cada fala
W/fontes/<nome>.mp4       trecho real do bruto para a sincronia
W/ls/<nome>.mp4           resultado da sincronia da boca
```

## Passo a passo

### 1. Material
- **Reel editado** (vira `W/<reel>/original.mp4`): link do Frame.io em MATERIAL FINALIZADO do card do reel
  publicado → `python ~/.claude/skills/frameio/scripts/frameio.py baixar <id> W/<reel>/` (o `<id>` vem do
  redirecionamento de `https://f.io/<código>`: `curl -sIL ... | grep location`, parte depois de `/view/`).
  Sem Frame.io: procure em `EDITADO` do mês no G:. Não achou → avise e pule o reel (o Stallone ficou de fora
  em 10/10 por isso).
- **Bruto** (para o Clailton real): `G:\...\<mês>\ORGÂNICO\BRUTO\<pasta>\<pauta>.MP4` (link em MATERIAL
  NECESSÁRIO). Use direto do G:; o download por link do Drive falha por cota em arquivo de 4 GB.

### 2. Medir o gancho original
```
P S/medir_original.py palavras W/<reel>          # fala dos primeiros 20 s com tempos
P S/medir_original.py medir W/<reel> <fim_frase> # fim_frase = segundo em que termina a frase que sai
```
Confira `W/<reel>/medidas.jpg`: linha vermelha na divisão imagem/Clailton, amarelo na legenda, verde nos
olhos, e a tira com o **quadro do corte** (1º quadro da cena que continua). Com flash, o quadro branco fica
antes do corte e o gancho novo sai clareando igual. Se o gancho usa B-roll de tela cheia:
`P S/medir_original.py cheio W/<reel> <t>` num segundo em que o B-roll cheio aparece.
Faça também a folha do reel inteiro com o tempo, para escolher as imagens de cima:
`ffmpeg -i original.mp4 -vf "fps=1,scale=120:-1,drawtext=fontfile=C\\:/Windows/Fonts/arial.ttf:text='%{pts\:hms}':fontcolor=yellow:fontsize=14,tile=12x8" -frames:v 1 folha.jpg`

### 3. Plano (`W/ganchos.json`)
Um bloco por reel (pauta, título, bruto) e um por variação (texto, imagens de cima). Formato completo no topo
de `scripts/montar.py`. Imagens de cima, em ordem de prioridade:
1. **cenas do próprio reel** (`topo`/`cheio` + segundo do original): mantêm a cara do vídeo;
2. **desenho novo no mesmo traço** do reel (quando o reel é ilustrado, como o Padre): Magnific
   `images_generate` com `references` de estilo = 2 quadros do reel (suba por `creations_request_upload` →
   PUT → `creations_finalize_upload`), `mode: imagen-nano-banana-2`, `aspectRatio: 4:3`, `count: 2-3`,
   prompt em inglês terminando em "No text, no letters, no signs with words, no logos.";
3. foto/cena nova só seguindo as regras de B-roll do usuário (sem marca d'água, sem texto em inglês,
   alta resolução; skill `reels-tela-dividida-clailton`).
Cada imagem **entra na palavra que ilustra** ("ate" = índice da palavra seguinte; veja os índices com
`P S/montar.py W --palavras <nome>` depois do passo 5). Imagem de capa do gancho original pode ser
reaproveitada no começo (fica familiar para quem já viu).

### 4. Fala no HeyGen (Chrome do usuário)
Leia antes a skill `chrome-browser`. Todas as frases numa gravação só:
1. Abra `https://app.heygen.com/avatar/avatar-shots` (criação rápida). Avatar **Clailton 2** (o mais
   recente; página `https://app.heygen.com/avatar/my-avatars/482e7a79b2af44b3b38a1038ffb9750b`), visual
   **Clailton 2 - 1**. Voz: a **padrão do avatar** (clonada do Clailton). **Nunca troque a voz padrão do
   avatar na conta sem autorização** (a janela "Trocar voz" muda o padrão: cancele).
2. Formato vertical, **1080p**. No campo do roteiro, digite as frases **na ordem das variações**, separadas
   por ` ... ` (o separador vira pausa). Gere (1–2 min) e anote a ordem dos nomes.
3. **Download** (autorizado pelo usuário em 13/10/2026): ícone de download do vídeo em "Criações recentes"
   → Baixar MP4. O Chrome da conta abre "Salvar como"; confirme com
   `powershell -NoProfile -ExecutionPolicy Bypass -File "$HOME/.claude/skills/reels-novela-clailton/scripts/salvar_downloads.ps1" -Pasta "<W>\vozes" -Esperar 60`.
   O arquivo vem como `Vídeo de Avatar_1080p.mp4` (pode cair em Downloads ou Documentos; procure pelos
   últimos minutos).
   **Se travar** (a janela não fecha, o arquivo não aparece em ~1 min, a aba do HeyGen trava): pare e
   **avise o usuário** ("o download do HeyGen travou de novo na janela Salvar como, pode conferir?"), para
   ele verificar se o problema se repetiu. Não fique tentando em silêncio.
4. Separe as falas:
   `P S/separar_falas.py W "<video_heygen.mp4>" padre_v2 padre_v3 chegada_v2 ...` (mesma ordem do roteiro).
   Ele confere cada fala com o texto do `ganchos.json` e avisa se não bater.

### 5. Clailton real + sincronia da boca (Magnific)
O avatar do HeyGen fica com cara de IA na boca e nos óculos (reprovado em 10/10). O que foi aprovado:
**trecho real do bruto daquele reel, mesma roupa, e só a boca sincronizada** com a fala nova.
1. `P S/achar_trechos.py "<bruto>" W/<reel>/trechos.json <dur_v2> <dur_v3>` (durações das falas + 0,1 s;
   veja em `vozes/frases.json`). Ele só aceita trechos em que o Clailton **está falando desde o 1º quadro**,
   de frente para a câmera e com o rosto firme.
2. `P S/recortar_fonte.py "<bruto>" <início> <dur> W/fontes/<nome>.mp4` e **olhe a tira** `.jpg`: mão longe
   da boca, olhando para a câmera, sem virar o rosto na 1ª palavra, roupa igual à do reel (no Termômetro,
   sem óculos). Ruim → próximo candidato do `trechos.json`.
3. Magnific: `creations_request_upload` (video/mp4 e audio/wav, `count` = nº de arquivos) → `curl -X PUT
   -H "Content-Type: ..." --data-binary @arquivo "<url>"` → `creations_finalize_upload` (`visible: false`) →
   `video_speak` com `videoUrl`/`audioUrl` = identificadores e **`mode: "lipsync-2.0"`** (máx. 30 s) →
   `creations_wait` → baixe o `url` do resultado para `W/ls/<nome>.mp4`. Dá para disparar todas juntas.
   Não use `veed-sync-2-v2v` (lábios inchados e pele com filtro, testado em 11/10).
4. `P S/tira_boca.py W <nome> ...` → olhe `W/ls/bocas.jpg`: a boca tem que **abrir e fechar nas palavras
   desde o 1º quadro**. Boca quase parada ou rosto virando → outro trecho e nova sincronia.

### 6. Pausas (quando ajudar)
Gancho com pausa natural longa (≥ 0,25 s) fica mais dinâmico cortando o silêncio e alternando
aberto/fechado no corte (o usuário pediu no Termômetro V2):
`P S/cortar_pausas.py W <nome> <ini>:<fim>:<zoom> ...` (zoom 1.3 = fechado, 1.0 = volta ao aberto; tempos
da pausa na fala). Ele mexe no vídeo da boca, na voz e nos tempos das palavras juntos (guarda os originais
como `_semcorte`). Troque a imagem de cima no mesmo corte.

### 7. Montar e conferir
`P S/montar.py W <nome> [<nome> ...]` (~1,5 min por variação). Faz sozinho:
- voz do HeyGen equalizada para o microfone e a sala do original (até ~1 dB por faixa), no volume da voz
  original, com o **ambiente real do escritório** por baixo (sem isso a emenda "abre": o fundo ficava 10–15 dB
  mais silencioso);
- cor e nitidez do Clailton casadas com as do gancho original;
- rosto no mesmo tamanho e olhos na mesma altura do original; legenda no tamanho, posição e fonte medidos,
  telas de até 4 palavras / 16 letras, sombra v3; `grande_final` deixa a última palavra grande;
- flash de saída e o "shhh" do original atravessando a emenda; emenda no quadro do corte, resto intacto;
- conferência: `<saida>_qa.jpg` (boca em 10 pontos + gancho novo × original lado a lado) e números de cor,
  ambiente, voz e timbre antes/depois da emenda (devem ficar próximos).
Depois **olhe** o vídeo: a imagem entra na palavra certa? A legenda bate com a fala? A emenda passa sem pulo?
Não dá para ouvir: a palavra final sobre "parecer IA" na voz é do usuário.

### 8. Mostrar a primeira
Mostre a 1ª variação (SendUserFile) com: o gancho novo, a frase que saiu, de onde o vídeo segue igual, e os
pontos para ele olhar (boca nas primeiras palavras, voz). Só depois do ok faça o resto.

### 9. Drive e Sala de Revisão
- Copie para `...\EDITADO\VARIAÇÕES TELA DIVIDIDA\<Título do reel>\` (crie as pastas se faltarem). Substituir
  um arquivo com o mesmo nome mantém o link do Drive.
- Link do arquivo: conector Google Drive `search_files` (`title = '<arquivo>'`), espere terminar de subir.
- Sala de Revisão: siga a skill `sala-de-revisao` (id = pauta com TESTE).

### 10. Notion (Calendário Editorial, fonte `collection://f0cc9747-efab-822b-8678-07f92372d6b7`)
Um card por variação (`notion-create-pages`, ícone 📹):
- PAUTA `Reels_Clailton_TD_TESTE_<resto>_V2` · ANDAMENTO `Aprovação` · FORMATO `["📹 Reels (Video Curto)"]` ·
  PERFIL `CLAILTON` · RESPONSÁVEL `🤖 CLAUDE` · REDE SOCIAL `["Instagram / Facebook"]` · DATA D/ CONCLUSÃO hoje ·
  IDEIA "Variação de gancho (teste A/B) do reel publicado em DD/MM. Só o gancho mudou; o resto do vídeo é o original."
- MATERIAL FINALIZADO: link da Sala (primeiro) e o do Drive.
- Corpo:
  ```
  **Variação de gancho para teste.** O V1 é o reel publicado em DD/MM.
  - **Gancho novo (0 a X s):** "..."
  - **Saiu:** "..." (0 a Y s do original)
  - **Resto do vídeo:** igual ao publicado, a partir de "..."
  - **Imagens do gancho:** ...
  - **Como foi feito:** Clailton real do bruto deste reel, com a boca sincronizada à frase nova na voz clonada dele.
  - **Teste sugerido:** postar como Reel de teste (só para quem não segue), ao meio-dia, e comparar as views em 48 h e a retenção dos 3 primeiros segundos com o original.
  - **Atenção:** a boca no gancho é gerada por IA. Se o Instagram pedir, marcar "Feito com IA".
  ```

### 11. Fechar
Resumo ao usuário: link da pasta VARIAÇÕES TELA DIVIDIDA, lista das variações, o que ficou de fora e por quê,
e os **créditos gastos** (HeyGen: vídeos de voz; Magnific: ~2 mil por sincronia, mais os desenhos). Apague as
cópias pesadas de `W` depois que tudo estiver no Drive (mantenha os `.json` e as vozes até a aprovação).

## Lições do teste de 10–11/10/2026

- Avatar do HeyGen no gancho: boca e óculos "entortam", reprovado. HeyGen serve só para a **voz**.
- Trecho do bruto com o Clailton **calado**: a sincronia quase não mexe a boca. Sempre trecho com fala.
- Rosto virando na 1ª palavra = "as primeiras palavras parecem IA". Trecho de frente desde o 1º quadro.
- Imagem de cima entrando uma palavra atrasada incomoda: confira os índices ("a tua empresa", não "tua").
- Recorte da faixa de cima do original pode trazer pedaço da legenda antiga (um "~" solto): `topo_y1` já
  corta acima da legenda; confira o `_qa.jpg`.
- Usuário reprovou um gancho (Chegada V2) e mandou o texto novo: refaça só a fala dele no HeyGen, mesmo processo.
