---
name: motion-designer
description: Faz qualquer vídeo motion / motion graphics / animação, para qualquer marca ou produto — anúncio e criativo animado, demonstração de plataforma, site ou app, lançamento de produto, vídeo explicativo, gráfico ou dado animado, vinheta, logo animado, abertura, Reels/Stories/feed/YouTube — do briefing à entrega. Diz qual ferramenta usar em cada caso (HyperFrames como base; Manim, Motion Canvas, Remotion, Diffusion Studio, Lottie, Blender, IA de vídeo/voz da Magnific como apoio), instala o que faltar no PC, analisa a referência de estilo quadro a quadro, monta com telas reais, narração, duas trilhas e efeitos do Artlist sincronizados, confere margens e área segura de cada rede e revisa quadro a quadro antes de entregar (Drive e Notion quando pedido). Use sempre que o pedido for "faz um motion", "motion designer", "vídeo animado", "anúncio animado", "criativo motion", "animação do produto/da plataforma/do site", "vídeo explicativo animado", "refaz a animação", "vídeo igual a essa referência", ou qualquer vídeo que não parta de filmagem de pessoa (filmagem do Clailton/Lucas vai para as skills de reels).
---

# Motion Designer

Processo completo para qualquer motion. Exemplo aprovado (out/2026): Criativo Motion Black (Legacy
Academy), projeto `Desktop/Projetos Edições/Motion Designer/videos/black-motion-v3` no PC NOT-LIVE-LAIR.

O usuário não é técnico: fale pelo resultado ("a música vira no raio", "o texto não encosta na borda"),
nunca por nomes de ferramenta ou código.

## 0. Antes de começar (todo PC)

Rode `python ~/.claude/skills/motion-designer/scripts/verificar_ambiente.py`. Ele lista o que está
instalado e imprime o comando de instalação do que faltar. Base obrigatória: Node 20+, Python 3.10+,
ffmpeg, HyperFrames (`npx hyperframes`, skills `hyperframes*` já chegam pela sincronia), `pip install
librosa soundfile faster-whisper pypdf`. O resto só quando o pedido precisar (tabela abaixo).
Instalar programa novo, baixar arquivo ou gastar crédito: pedir o "sim" do usuário antes.

## 1. Qual ferramenta usar

| Pedido / trecho | Ferramenta | Observação |
| --- | --- | --- |
| Montagem do vídeo inteiro: anúncio, demonstração, Reels animado, vinheta, texto animado | **HyperFrames** | Base sempre. HTML + GSAP, grátis. Catálogo com 446 efeitos: `npx hyperframes catalog --query "<efeito em inglês>"` antes de desenhar à mão |
| Gráfico, curva, juros, crescimento, fórmula, dado "matemático" | **Manim** | Gera um MP4 da cena que entra no HyperFrames. Modelo: `templates/manim_grafico.py` |
| Diagrama explicativo com muito ajuste de tempo (setas, fluxos, passo a passo) | **Motion Canvas** | Editor visual no navegador; render pelo botão do editor. Modelo em `templates/motion-canvas/` |
| Muitas variações do mesmo vídeo (20 cidades/nomes/números) ou modelo React pronto | **Remotion** | Só para teste sem licença. Peça publicada de empresa com mais de 3 pessoas precisa de licença paga (remotion.pro/license): avisar antes |
| Projeto que o time vai abrir e editar depois (cortes, legenda, tela dividida) | **Diffusion Studio** | Mesmo projeto editável por mim e pelo time. Precisa de login do usuário no app (eu não faço login) |
| Ícone animado, check, confete, seta | **LottieFiles** (conector) → `<lottie>` no HyperFrames | Conectar com o usuário: `claude mcp add --transport http lottiefiles https://mcp.lottiefiles.com/mcp` |
| Logo 3D, objeto 3D com câmera | Three.js no HyperFrames, ou **Blender** (MCP) se instalado | — |
| Cena realista (pessoa, lugar, objeto filmado) | **Magnific** `video_generate` / `images_generate` | Gasta créditos: avisar antes |
| Narração | **Magnific** `audio_tts` (ElevenLabs, vozes BR) | Detalhes em `references/audio.md` |
| Música e efeitos | **Artlist** pelo Chrome logado do usuário | Sem conector; detalhes em `references/audio.md` |

Detalhes, instalação e armadilhas de cada uma: `references/ferramentas.md`.

## 2. Processo

1. **Briefing curto** (só o que faltar, uma pergunta por vez ou um formulário de até 4 perguntas):
   objetivo (vender ou mostrar), onde vai rodar (define o formato), duração, narração sim/não,
   chamada final. Se houver documento de campanha/briefing da marca, ler e seguir as regras de copy.
2. **Referência de estilo:** pedir uma ou oferecer 3 opções diferentes (clara, contrastada, escura),
   abrindo os links no Chrome do usuário. Dissecar com `scripts/quadros_referencia.py` (1 quadro a cada
   0,5 s em folhas) e anotar a gramática: cores, fonte, tempo de cena, transições, como o texto
   entra/sai. Copiar a gramática, nunca o conteúdo nem o logo. Mais em `references/referencias-estilo.md`.
3. **Material real da marca:** prints da plataforma/site pelo Chrome logado (salvar em escala 1),
   logo, fontes e cores do site oficial (baixar assets públicos). Cobrir nome/e-mail/avatar do usuário
   logado e não usar telas com dados de clientes/alunos. Nunca redesenhar interface de cabeça.
4. **Roteiro:** gancho forte nos 2–3 primeiros segundos, uma ideia a cada 2–4 s, chamada final clara.
5. **Narração → tempos:** gerar a voz, pegar o tempo de cada palavra (`audio_timing_get`) e amarrar
   cada animação a essas palavras.
6. **Trilha e efeitos:** analisar com `scripts/analisar_audio.py` (batidas, viradas, picos dos efeitos)
   e encaixar as viradas da música nos momentos-chave. Mixar com `scripts/mix_audio.py`
   (configuração em JSON). Vídeo com virada de clima = duas músicas.
7. **Montagem no HyperFrames** (`npx hyperframes init "videos/<nome>" --non-interactive
   --example=blank`), cena a cena. Peças de Manim/Motion Canvas entram como vídeo.
8. **Revisão obrigatória antes de mostrar:**
   - `npx hyperframes lint` e `npx hyperframes check` sem erro;
   - `npx hyperframes snapshot --at <momentos>` e `scripts/area_segura.py --formato <9x16|4x5|1x1|16x9>`
     sobre os snapshots (máscara da interface da rede + margens);
   - conferir antes/depois de cada transição;
   - transcrever a mixagem (`scripts/transcrever.py`) para provar que a voz está clara;
   - renderizar (`npx hyperframes render --quality high --output renders/<nome>.mp4`) e montar a folha
     de quadros do MP4 final; corrigir e renderizar de novo se aparecer algo.
9. **Entrega:** subir o vídeo na **Sala de Revisão** (skill `sala-de-revisao`, seção "Pedido feito direto na
   conversa") e mandar o link na conversa com o que mudou e os pontos a confirmar; o usuário comenta as
   correções na Sala. Drive/Notion só quando pedido ("vai nas tasks"; padrões da marca em `references/marcas/`). Versões novas: `v2`, `v3`... sem apagar as antigas.

## Pedido vindo de outro PC ou do celular

O PC de render tem a conversa **"Central de Render Motion"** (Controle Remoto ligado). Pedido de motion para
"mandar pro PC de render": `ListAgents` → `SendMessage` para ela com o briefing completo (texto, referências,
links). Não aparece na lista: PC de render desligado ou app fechado; avise o usuário.

## 3. Regras fixas

- **Margens e área segura** (vale para todo vídeo; tabela por formato em `references/area-segura.md`):
  Reels/Stories 9:16 em 1080×1920 — margem lateral ≥ 80 px, nada importante acima de 220 px, abaixo de
  1480 px nem à direita (x > 950) entre y 1000 e 1720. Texto que não cabe quebra linha ou diminui.
- **Formato antes de tudo** (out/2026: v2 do manifesto da Legacy foi montada em 9:16 e o usuário queria 16:9):
  confirmar o formato (16:9, 9:16, 4:5) no briefing antes de buscar imagem ou montar, e buscar banco já na
  orientação certa. Recortar 4K horizontal para vertical deixou o enquadramento "horrível".
- **Uma imagem por fala** (mesma revisão): narrado com banco de imagens troca de cena a cada frase (1 a 3 s), e
  cada cena ilustra literalmente o que está sendo dito. Nunca a mesma imagem por vários segundos.
- **Duas músicas** quando há virada de clima (problema → solução): tensa antes, pra frente depois. A
  trilha chega até o fim do vídeo e fica presente, abaixando sob a voz.
- **Identidade de campanha** só onde o usuário pedir; a parte do produto segue o visual do produto.
- **Legenda queimada** sempre com a "sombra v3" (CLAUDE.md global).
- **Imagens de apoio:** sem marca d'água e sem texto em inglês (CLAUDE.md global).
- Créditos pagos e downloads: avisar/pedir o "sim" antes.
- **Anúncio pago na Meta** (reprovação real, out/2026: "temas sociais, eleições ou política"). Na fala
  e na tela, evitar: crise/falência/recuperação judicial/demissão, imposto, reforma tributária, juros,
  "cenário econômico incerto", governo/eleição; e frases que apontam atributo da pessoa ("você tem
  medo", "dinheiro curto", "todo empresário está quebrado"). Preferir benefício neutro ("Organize sua
  empresa para 2027", "gestão de caixa"). Conferir também prints e miniaturas dentro das telas.
  Em versão corrigida, trocar fala e texto juntos (voz nova só nas frases que mudam, mesma voz/ajustes).

## 4. Armadilhas já resolvidas

- Editar arquivo com acento: usar Python (`io.open(..., encoding="utf-8")`) ou a ferramenta de edição,
  nunca `Set-Content` do PowerShell; comandos com aspas aninhadas: escrever um script `.py`.
- Elemento escondido que "explode" num momento (partícula, faísca, onda, ripple): `fromTo` com
  `immediateRender: false`, senão aparece parado antes da hora.
- Flex no HyperFrames: caixa que não deve esticar precisa de `align-items: flex-start`.
- Vídeo dentro do HyperFrames (Manim etc.): na raiz do `index.html`, com `data-start` próprio, nunca
  dentro de cena temporizada; em `style`, `inset: auto` antes de `left/top`.
- Fundo que muda de cor na transição: a camada nova só começa quando a transição já cobre a tela.
- Mixagem: base de silêncio (`anullsrc` + `duration=first`) e voz estendida com `apad` no sidechain,
  senão o áudio corta ou a música some quando a voz acaba (o `mix_audio.py` já faz).
- Download do Artlist "não aparece": o Chrome pode estar perguntando onde salvar (janela do Windows que
  eu não clico) — pedir para o usuário desligar "Perguntar onde salvar" nas configurações de download.
- Página no Chrome em segundo plano não renderiza: tirar um print da aba antes de procurar elementos.
- Snapshots do HyperFrames novo ficam em `.hyperframes/artifacts/snapshots/<id>/` (não em `snapshots/`);
  o `area_segura.py` sem `--pasta` já pega o mais recente.
- Texto gigante (ano, número) passa da margem: medir no snapshot com a máscara e reduzir a fonte;
  `white-space: nowrap` nas linhas que não podem quebrar.
- Legenda do YouTube com erro 429: baixar o áudio e transcrever com `scripts/transcrever.py`, ou usar a
  skill `watch`.
