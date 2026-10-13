# Ferramentas: instalação, uso e armadilhas

Caminhos com `~` = pasta do usuário. Nada aqui usa o nome de usuário do Windows.

## HyperFrames (base de todo motion)

- Skills `hyperframes`, `hyperframes-core`, `-animation`, `-creative`, `-cli`, `-registry`, `-audio`,
  `-keyframes`, `-studio`, `media-use`, `product-launch-video` já chegam pela sincronia. Ler
  `hyperframes-core` antes de escrever HTML.
- CLI: `npx hyperframes@latest` (baixa sozinho). Projeto: `npx hyperframes init "videos/<nome>"
  --non-interactive --example=blank`.
- Bibliotecas locais (sem depender de CDN): `npm install gsap @fontsource-variable/inter` no projeto e
  copiar `node_modules/gsap/dist/gsap.min.js` para `assets/`. Fonte da marca: baixar o `.woff2` do site
  oficial e declarar `@font-face`.
- Catálogo de efeitos: `npx hyperframes catalog --query "glitch transition"` (também "3d phone mockup",
  "particles", "liquid glass", "chart count up", "shader transition"). `npx hyperframes add <nome>` copia
  para `compositions/`. Os componentes vêm genéricos (telas de exemplo, textos em inglês): usar como base e
  trocar pelo material real.
- Comandos de revisão: `lint`, `check` (layout, contraste, texto fora do quadro), `snapshot --at t1,t2`,
  `render --quality high --output renders/x.mp4`. Avisos de contraste no instante de um clarão são
  aceitáveis; texto cortado não.
- Efeitos que já funcionaram (ver `videos/black-motion-v3/index.html` e `scripts/upgrade_v3.py`):
  texto palavra a palavra com desfoque; glitch RGB por `text-shadow` em passos; grão de filme (PNG de ruído
  com `background-position` em `steps()`); raio em SVG com `stroke-dashoffset` + clarão + tremor; onda de
  choque e faíscas; círculo que abre do centro (transição escuro→claro); grade 3D de cards inclinada;
  monitor/tablet/celular em CSS com prints reais; cursor que clica com ripple; contador de números;
  brilho passando em botão; confete/partículas com posições fixas (sem `Math.random`).

## Manim (gráficos e animação "matemática")

- Instalar: `pip install manim` (Windows: vem com as dependências; sem LaTeX, usar `Text`, não `MathTex`).
- Render: `manim -r 1424,600 --fps 30 --format mp4 --media_dir <pasta temporária> -o nome arquivo.py Cena`
  (`-ql` para teste rápido). Fundo igual ao do cartão onde vai entrar (ex.: `#ffffff`), `tips=False` nos
  eixos.
- Modelo: `templates/manim_grafico.py` (curva de crescimento com meses, área e selo de meta).

## Motion Canvas (diagramas com editor visual)

- Copiar `templates/motion-canvas/` para uma pasta do projeto e `npm install`.
- O plugin do Vite é CommonJS: o `vite.config.ts` do modelo já importa com `createRequire` e usa caminho
  absoluto do projeto (o servidor pode ser iniciado de outra pasta).
- Abrir no painel do navegador do app: `.claude/launch.json` com `node <projeto>/node_modules/vite/bin/vite.js
  <projeto> --port 9001` e `preview_start`. Render pelo botão do editor. Para lote, usar Revideo.
- Erro "thread is not available" depois de mudar a configuração = cache do navegador: apagar
  `node_modules/.vite` e abrir em outra porta.

## Remotion

- Testar: `npx create-video@latest --yes --hello-world <pasta>`; skills oficiais:
  `npx skills add remotion-dev/skills --yes` (ficam no projeto). Render: `npx remotion render <Comp> out/x.mp4`.
- Licença: grátis para pessoa física, empresas com até 3 pessoas e para avaliar. Uso comercial de empresa
  maior exige licença paga, mesmo usando em uma conta só.

## Diffusion Studio (projeto editável pelo time)

- Instalador oficial: release `Diffusion-Studio-x64-Setup.exe` em github.com/diffusionstudio/editor
  (conferir assinatura "Diffusion Studio Inc."; instala em `%LOCALAPPDATA%/DiffusionStudio`).
- Login obrigatório no primeiro uso (Google, GitHub ou e-mail) — feito pelo usuário. Se a volta do
  navegador para o app travar em "Returning you to Diffusion Studio", clicar em "Open the app" e permitir
  no Chrome, ou usar o link mágico por e-mail.
- Comando: `%LOCALAPPDATA%/DiffusionStudio/app-<versão>/resources/cli/bin/dapi.cmd` (`open -b <pasta>`,
  `context`, `check <cena>`, `capture <cena> -t 1 2`, `export <cena>`, `window show`). MCP em
  `http://127.0.0.1:3274/mcp`. Ler `resources/docs/skills/editor.md` antes de editar.
- Projetos em pasta local fora do Drive/OneDrive (ex.: `C:/DiffusionProjects/<nome>`). Projeto = pasta
  com `index.tsx` (JSX tipo SVG, `<stage><scene id="...">`).

## LottieFiles

- Conector oficial gratuito: `claude mcp add --transport http lottiefiles https://mcp.lottiefiles.com/mcp`
  e autorizar no navegador (pedir ao usuário). 100 mil+ animações; no HyperFrames, usar o adaptador
  Lottie (`hyperframes-animation/adapters/lottie.md`).

## Blender (3D)

- Quando o pedido pedir 3D real: instalar o Blender e o Blender MCP (perguntar antes). A placa de vídeo
  do PC (RTX 4070 no NOT-LIVE-LAIR) dá conta.

## Magnific (IA de imagem, vídeo, voz e efeitos)

- Conector já ligado na conta. Sempre ver `account_balance` e avisar o custo antes de gerar.
- Voz: `audio_voices_list` (search "portuguese") → `audio_tts` (modelo `eleven_v3`, tags como
  `[serious]`, `[softly]`, `[energetic]`) → `creations_wait` → `creations_register_download` → baixar a URL →
  `audio_timing_get` (tempo de cada palavra).
- Efeitos sonoros curtos: `audio_sfx_generate` (1–2 s). Vídeo/imagem: `video_generate`, `images_generate`.

## Skill `watch` (assistir vídeo)

- Para entender um vídeo de referência ou tutorial: quadros + transcrição. Configurada no modo local.
