---
name: motion-legacy
description: Diretriz para qualquer vídeo motion / motion graphics / animação que o usuário pedir (anúncio, criativo, Reels animado, vinheta, explicativo, demonstração de plataforma, logo animado) — qual ferramenta usar em cada caso (HyperFrames, Remotion, Motion Canvas, Manim, Diffusion Studio, LottieFiles, Blender, IA de vídeo da Magnific), o processo completo do briefing à entrega (referência, telas reais, voz, duas trilhas do Artlist, efeitos, área segura do Reels, revisão quadro a quadro, Drive e Notion) e as armadilhas já resolvidas. Use sempre que o pedido for "faz um motion", "motion designer", "anúncio animado", "criativo motion", "vídeo animado da plataforma", "refaz a animação", ou qualquer vídeo que não parta de filmagem do Clailton/Lucas (filmagem vai para as skills de reels).
---

# Motion Legacy

Processo e caixa de ferramentas para motion da Legacy. Projeto de referência (aprovado pelo usuário em
11/10/2026): `Desktop/Projetos Edições/Motion Designer/videos/legacy-academy-promo` (Criativo Motion Black).

## 1. Qual ferramenta usar

| Pedido | Ferramenta principal | Por quê |
| --- | --- | --- |
| Anúncio, criativo, demonstração de plataforma/site, Reels animado, vinheta | **HyperFrames** | Padrão. HTML + GSAP, grátis, 446 efeitos prontos no catálogo, regras da Legacy já aplicadas |
| Gráfico de finanças, juros, margem, fluxo de caixa, fórmula, conceito "matemático" | **Manim** (cena isolada) → entra como vídeo dentro do HyperFrames | Curvas, eixos e transformações de forma com precisão de livro |
| Diagrama explicativo vetorial (setas, fluxos, "como funciona") com muito ajuste fino | **Motion Canvas** (cena isolada) → vídeo dentro do HyperFrames | Editor visual com linha do tempo para acertar tempo de cada passo |
| Muitas variações do mesmo criativo (20 cidades, 20 nichos, nomes, números) ou modelo pronto do ecossistema React | **Remotion** | Templates e renderização em lote. **Licença:** grátis só para avaliar; uso comercial da Legacy (mais de 3 pessoas) exige licença paga (remotion.pro/license). Não usar em peça publicada sem a licença |
| Edição que o time vai abrir e mexer depois (tela dividida, cortes, legenda, B-roll) | **Diffusion Studio** | Eu e o time editamos o MESMO projeto no app (não perde nada como na exportação para o Premiere). Precisa do login do usuário no app |
| Ícone animado, check, confete, seta, carregamento | **LottieFiles** (conector, quando instalado) → `<lottie>` no HyperFrames | 100 mil+ animações prontas |
| Logo 3D, celular girando em 3D real, cena com câmera voando | **Blender** (quando instalado) ou Three.js dentro do HyperFrames | 3D de verdade |
| Cena cinematográfica real (porta de loja fechando, empresário de madrugada) | **Magnific** `video_generate` / `images_generate` (gasta créditos, avisar antes) | Vídeo de IA para abertura e transição |

Regra: o vídeo final é montado **no HyperFrames**; as outras ferramentas geram peças (MP4/PNG/Lottie) que
entram como camada. Exceção: entrega editável para o time → Diffusion Studio.

Antes de desenhar qualquer efeito à mão, procurar no catálogo:
`npx hyperframes catalog --query "<efeito em inglês>"` (transições com shader, glitch, celular/tablet em 3D
`device-frame-stage`/`multi-device-splay`, partículas `particle-image-reveal`, `vfx-liquid-glass`, gráficos
`data-chart`, texto `rgb-glitch-text`...). Instalar com `npx hyperframes add <nome>`.

## 2. Processo (do tutorial "Insane Motion Graphics With Opus 5.5" + o que deu certo aqui)

1. **Briefing curto** com o usuário só do que faltar: objetivo (vender ou mostrar), destino/formato
   (Reels 9:16 é o padrão), duração (30–45 s), narração ou não. Campanha ativa: ler o documento da campanha
   (ex.: Black Friday 2026 em `Documents/Black_Friday_2026_Narrativas_e_Copies_3.1.pdf`) e seguir as regras
   de copy dele.
2. **Referência de estilo:** pedir uma ou oferecer 3 (abrir no Chrome do usuário). Baixar, tirar 1 quadro a
   cada 0,5 s e escrever a "gramática" (cores, fonte, tempo de cena, transições, como o texto entra/sai).
   Copiar a gramática, nunca o conteúdo nem o logo. Acervos: `athemeroy/awesome-opus-5-5-videos`,
   `yihui-dev/awesome-opus5-5-videos` (GitHub).
3. **Material real:** prints e imagens reais pelo Chrome logado do usuário (plataforma, site); logo, fonte e
   cores do site oficial. Nunca redesenhar a interface de cabeça; reconstruir componentes com as imagens
   reais em alta.
4. **Roteiro:** gancho forte sobre o cenário nos primeiros 2–3 s, depois o produto, uma ideia a cada 2–4 s.
5. **Voz:** ElevenLabs pela Magnific (`audio_tts`, modelo eleven_v3, vozes brasileiras; Duarte Queiroz
   aprovada). Conferir a pronúncia transcrevendo. Acelerar 1,05–1,07× se passar do tempo.
6. **Trilha e efeitos:** Artlist pelo Chrome do usuário (sem conector; downloads caem em Downloads).
   - **Duas músicas quando há virada de clima:** sombria/tensa antes da virada, pra frente (rock) depois.
   - Medir batidas e picos (librosa) e encaixar as viradas e pancadas da música nos momentos-chave.
   - Efeitos: clique a cada toque do cursor, whoosh a cada transição, impacto no logo; raio/trovão quando
     pedido. Mixar com script (`scripts/mix_audio.py` do projeto de referência): voz por cima, música
     abaixando sob a voz e chegando até o fim (atenção: estender a voz com `apad` no sidechain), -14 LUFS.
7. **Montagem** no HyperFrames, cena a cena, tempos amarrados às palavras da narração.
8. **Revisão antes de entregar (obrigatória):**
   - `npx hyperframes check` sem erro;
   - snapshots de todas as cenas com a **máscara do Reels** (`scripts/area_segura.py` do projeto de
     referência) — nada importante fora da área segura;
   - conferir as transições (antes/depois de cada corte);
   - transcrever a mixagem final para provar que a voz está clara;
   - depois do render, folha de quadros do MP4 final.
9. **Entrega:** MP4 na pasta do projeto + enviar ao usuário. Quando pedido: Drive
   (`02. Captação de Vídeos/<ano>/<mês>/...`, ex.: `Black Friday/Criativos`) e card no Notion na aba certa
   (ex.: "Black Legacy", base DEMANDAS | BLACK FRIDAY, Andamento = Revisão, link do Drive em Material
   Finalizado).

## 3. Regras fixas

- **Área segura do Reels (1080×1920):** margem lateral ≥ 80 px; topo até 220 px é do cabeçalho; abaixo de
  1480 px ficam nome/legenda/áudio; à direita (x > 950, y 1000–1720) ficam os botões. Texto que não cabe
  quebra linha ou diminui, nunca corta.
- **Identidade de campanha (ex.: Black)** só onde o usuário pedir (na Black: só na abertura); a parte do
  produto segue o visual limpo do próprio produto.
- Legenda queimada sempre com a "sombra v3" (CLAUDE.md global).
- Créditos pagos (Magnific): avisar antes; downloads do Artlist com o "sim" do usuário.

## 4. Onde está cada ferramenta (instaladas em 11/10/2026 no PC NOT-LIVE)

- **HyperFrames:** `npx hyperframes` (skills em `~/.claude/skills/hyperframes*`). Projeto novo:
  `npx hyperframes init "videos/<nome>" --non-interactive --example=blank`.
- **Remotion:** projeto de teste em `Motion Designer/testes/remotion-teste` (skills `remotion-*` dentro dele,
  em `.claude/skills`). Render: `npx remotion render <Composição> out/x.mp4`.
- **Manim:** `pip` (v0.22). Render: `manim -qh --format mp4 arquivo.py Cena` (`-ql` para teste). Sem LaTeX
  instalado: usar `Text`, não `MathTex`.
- **Motion Canvas:** `Motion Designer/testes/motion-canvas-teste`. Abre no painel do navegador pelo
  `.claude/launch.json` (porta 9001). Renderiza pelo botão de render do editor (não tem render por comando;
  para lote, usar Revideo). O `vite.config.ts` precisa do plugin via `createRequire` e do caminho absoluto
  do projeto.
- **Diffusion Studio:** app em `%LOCALAPPDATA%/DiffusionStudio`; ferramenta de comando
  `%LOCALAPPDATA%/DiffusionStudio/app-<versão>/resources/cli/bin/dapi.cmd` (`open -b <pasta>`, `check`,
  `capture`, `export`); servidor MCP em `http://127.0.0.1:3274/mcp`. Documentação do próprio app em
  `.../resources/docs` (ler `skills/editor.md` antes). Projetos em pasta local fora do Drive (ex.:
  `C:/DiffusionProjects`). **Precisa do login do usuário no app** (Google/GitHub/e-mail) — Claude não faz
  login.

## 5. Armadilhas já resolvidas

- No Windows, editar arquivos com acento via PowerShell `Set-Content` estraga a acentuação: usar Python
  (`io.open(..., encoding="utf-8")`) ou a ferramenta de edição.
- HyperFrames: elemento posicionado com flex precisa de `align-items: flex-start` (senão estica —
  aconteceu com o selo e com os chips); camada clara de fundo só pode começar depois que a transição cobre
  a tela.
- Mixagem: `amix` precisa de uma base de silêncio com a duração exata (`anullsrc` + `duration=first`).
- Motion Canvas: erro "thread is not available" depois de mudar a config = cache do navegador; limpar
  `node_modules/.vite` e abrir em outra porta.
- yt-dlp pode dar 429 na legenda do YouTube: baixar o áudio e transcrever com faster-whisper (GPU), ou usar a
  skill `watch`.
