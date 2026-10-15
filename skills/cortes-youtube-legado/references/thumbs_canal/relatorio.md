# Thumbs do canal Legacy Executoria + fotos do Clailton (pesquisa de 15/10/2026)

Canal: **Legacy Executoria Empresarial**, https://www.youtube.com/@legacyexecutoriaempresarial (ID `UC87lxpVNN2N5-vmOIGyiJsA`).
Baixei 35 thumbs em 1280×720 (maxresdefault):
- `thumbs_canal/lives/` traz 14 da aba **Ao vivo**, onde ficam as aulas e os aulões longos de ago. a out. 2026. É o padrão atual.
- `thumbs_canal/videos/` traz 21 da aba **Vídeos**, com o Executoria Cast, vídeos de escritório e de carro e o "Manhã com Estratégia".
- Folhas de contato: `thumbs_canal/folha_lives.jpg` e `thumbs_canal/folha_videos.jpg`.
- Teste de fonte: `thumbs_canal/_teste_fontes.jpg` e `thumbs_canal/_teste_fontes2.jpg`.

## 1. Os estilos do canal

| Estilo | Onde | Usar? |
|---|---|---|
| **A: "Aula/Live" (padrão atual)** | todas as lives de ago. a out. 2026 e os vídeos KMTjGKnmAkY, 2sVaBTLpT1Y, 0FfWzgHZn-s | **SIM, é este** |
| B: "Frame do vídeo" | vídeos de jul./ago. (4DSAq50ocS8, 0zf2p0T8bz4, OUPKPccZiks, VtKUymy8z8U, 4bxZW4bOJXU) | mesma tipografia do A, mas o fundo é o próprio quadro do vídeo (escritório escuro) |
| C: "Manhã com Estratégia" (antigo) | jun./jul. (VI3szpEeoyk, hr5v8rEB4z4, flt2RqraRDU, Ly0f1x8KnB0, hRzC-HeSrec, qyOaSTy4ppk) | NÃO: cena de IA, botões azuis 3D e logo "Comunidade Legacy" |
| Executoria Cast | v0jEA57pYL8 | só para o Cast (3 pessoas e ícone de microfone) |

Atenção: as 3 lives mais novas (W-vLAEHJ6eE, ObOjzZ7khYY e clQiPIuYjpo, de out. 2026) mostram **outro homem, de cabelo grisalho e barba**, não o Clailton.
O layout é o mesmo do estilo A.

## 2. Padrão A, receita para Pillow 1280×720

### Fundo
- É quase preto e nunca cor chapada pura. Base de **#02050A a #0A0F1A**, com textura escura bem sutil (granulado ou concreto) e vinheta nas bordas.
- Atrás da cabeça e do ombro do Clailton vai um **brilho azul**: radial, centro em x≈1000–1150 e y≈150–300, raio de ~350–450 px.
  O núcleo fica em #0A3FD0 / #011762 com opacidade de ~60–70% e cai para transparente. Também funciona como "rim light" no contorno do ombro.
- Variante frequente (96M4, QNKihb, 7w0dDCG0OWY, cKS34bnRDFI): o canto esquerdo puxa para **bordô muito escuro (#160003 a #190004)**,
  um degradê da esquerda (~40% da largura) que some no centro.
- Opcional: "fumaça" azul clara e fraca atrás da pessoa (KMTjGKnmAkY).

### Pessoa
- Clailton **recortado** (sem fundo do estúdio), **sem contorno branco** e sem adesivo. Fica sobre o fundo escuro, com o brilho azul atrás.
- Fica do **lado direito**, em x ≈ 640/700 até 1280 (45–50% da largura). É cortado pela borda de baixo (cintura ou peito), com o topo da cabeça a 15–40 px do topo.
  A cabeça (do topo ao queixo) tem **240–280 px (33–39% da altura)**.
- Variante espelhada, com a pessoa à esquerda e o texto alinhado à direita, terminando em x≈1190 (w6IwgEJ95FA, EbWsKb_R6sg, HKdiin8Ddno).
- **A pessoa fica NA FRENTE do texto**: a última letra da palavra azul às vezes passa por trás do ombro ou do braço ("CRESCIMENTO", "CAMISA DA", "QUEBREI", "CORRETA").
- Olha para a câmera. Expressões usadas: sério e desafiador (mão na têmpora), sorriso de canto, pensativo (mão no queixo), sorriso aberto,
  mão espalmada de "pare", apontando para o texto, braços cruzados, mãos abertas "explicando".
- Roupa: blazer ou terno escuro (azul-marinho ou cinza) com camisa, ou camisa social. Nunca de óculos nessas thumbs.
- Luz: pele bem iluminada e nítida, contraste alto e um pouco de saturação.

### Texto (o que faz o padrão)
- Fica **à esquerda, alinhado à esquerda, com margem x = 88–92 px**. O bloco ocupa em geral x 88 até ~780 (ou até ~990, entrando por trás da pessoa).
  Fica centralizado na vertical, entre y≈120 e y≈620.
- **Sempre CAIXA-ALTA.** São 3 a 7 palavras no total, em 2 ou 3 "andares":
  1. **Linha de apoio (kicker), branca #FFFFFF**: Montserrat ExtraBold/Black, com **altura da maiúscula de 42–56 px** (fonte de ~60–78 px).
     Tem 1–2 linhas, entrelinha de ~1,15 e nenhum contorno. Fica ~55–60 px acima da palavra azul.
  2. **Palavra(s)-chave AZUL**: fonte condensada pesadíssima.
     - Altura da maiúscula: **110–125 px** quando há 2–3 linhas e **160–190 px** quando há 1 linha. Entrelinha apertada (passo ≈ 1,08–1,12 × a altura da maiúscula).
     - Cor: **#0096EA**, com faixa de #0686D6 (sombras) a #19B8FA (brilhos).
     - Acabamento "cetim/plástico amassado": vincos claros sobre o azul, mais um **filete externo ciano claro (#3FC4FF, ~3 px)**.
     - Não leva sombra preta forte, só um escurecimento suave ao redor, se precisar.
  3. (Opcional) uma 2ª linha branca de apoio depois do azul, menor, com maiúscula de ~36–40 px: "É RISCO", "PRECISA DE MÉTODO", "DE TODO EMPRESÁRIO".
- **Fonte da palavra azul**: comparei na mesma altura.
  - **Impact** (C:/Windows/Fonts/impact.ttf) dá a largura exata do original (646 vs 658 px em "QUEBREI") e o Q com cauda igual.
  - O original é ainda mais "gordo". Para chegar nele, use `stroke_width` de 4–6 px **na mesma cor azul** e, por fora, o filete ciano.
  - Anton fica mais estreito (548 px) e serve se quiser algo mais limpo.
  - Baixei Anton, Montserrat (variável; use `set_variation_by_name('ExtraBold')`) e Bebas Neue em `C:/Render/_youtube/recursos/fonts/`. Bebas **não** combina: é fina demais.
- **Variante de ênfase**: a palavra negativa vai em **vermelho** (≈ #E3121B, com brilho #FF3B3B), com o mesmo tratamento ("VERMELHO?", "RUINS?", "ERRO").
  Outra variante é a 2ª palavra em **prata** (degradê #F4F4F4 → #BDBDBD com o mesmo amassado), como em "CLIENTE / VOLTAR".
- Exemplos reais de texto:
  - "CHEGA DE DIZER / ANO QUE VEM VAI SER DIFERENTE"
  - "FOI ASSIM QUE EU / QUEBREI"
  - "COMO FAZER O SEU TIME VESTIR A / CAMISA DA EMPRESA"
  - "DELEGUE COMO UM / PROFISSIONAL"
  - "SEM ISSO O SEU NEGÓCIO VAI / QUEBRAR"

### Elementos gráficos e logo
- **Não há logo nas thumbs de aula recentes.** A marca aparece só no fundo do estúdio ou na camisa.
  O Executoria Cast leva um triângulo Legacy pequeno no canto inferior direito. O "Manhã com Estratégia" levava "COMUNIDADE LEGACY" no canto (estilo antigo).
- Ícones pontuais aparecem às vezes: cifrão azul brilhante nas mãos (er6MhhTgiEk), montanha-russa em linha azul (JxntoGL_4KU),
  rachadura na palavra "QUEBRAR" (cKS34bnRDFI), pincelada azul atrás de "NO ESCURO" (HKdiin8Ddno). Não são obrigatórios.
- Não usam tarja, faixa nem caixa atrás do texto (exceto o pincel do HKdiin8Ddno).

### Esqueleto Pillow (ordem das camadas)
1. Fundo 1280×720 em #05080F, com ruído fraco (±6) e vinheta.
2. Degradê bordô opcional à esquerda: #190004 com alfa de 255 até 0 em x 0→500.
3. Brilho azul radial com GaussianBlur ~120, centro (1060, 230), cor #0A3FD0 e alfa ~170.
4. Texto branco (Montserrat ExtraBold).
5. Texto azul, nesta ordem:
   - Impact com stroke de 5 px na própria cor #0096EA.
   - Textura: um mapa de vincos (ruído em escala grande, desfocado, em "relevo") multiplicado/somado por cima, de modo que o azul varie entre #0686D6 e #19B8FA.
   - Contorno externo de 3 px em #3FC4FF.
6. Clailton recortado (PNG com alfa) por cima do texto, no lado direito. Leve contraste e nitidez.

## 3. Thumbs analisadas (IDs)
- **Ao vivo:** W-vLAEHJ6eE, ObOjzZ7khYY, clQiPIuYjpo, 96M4-iyujoE, QNKihbYkI54, w6IwgEJ95FA, EbWsKb_R6sg, JxntoGL_4KU, er6MhhTgiEk,
  E6IWJkjw7hs, 7w0dDCG0OWY, cKS34bnRDFI, HKdiin8Ddno, vx9DsX8159E.
- **Vídeos:** v0jEA57pYL8 (Cast), H7Fprc_OV84, 4bxZW4bOJXU, 4DSAq50ocS8, 0zf2p0T8bz4, OUPKPccZiks, VtKUymy8z8U, 2sVaBTLpT1Y,
  0FfWzgHZn-s, KMTjGKnmAkY, T2XNV5KBBvg, n9xN7MFPfmc, dq_IFX3q0Zg, 2y3EaFsiQd0, LRM5HNyNciE, qyOaSTy4ppk, VI3szpEeoyk, hr5v8rEB4z4,
  flt2RqraRDU, Ly0f1x8KnB0, hRzC-HeSrec.

## 4. Fotos do Clailton

### Onde está o arsenal
- **Drive, ensaio de estúdio (fev./2026)**: `G:/Meu Drive/4. Design/11 - Fotos/Clailton/2026_02_23_Fotos_Estudio_Clailton/`.
  São **117 JPG de 3376×6000** (16 MB cada), todos COM fundo (estúdio azul, com o letreiro "LEGACY EDUCAÇÃO" atrás da cabeça em muitas).
  Ele usa blazer azul (DSC05258–05331) ou camisa azul (DSC05334–05407), em poses variadas. É deste ensaio o estúdio azul das thumbs do canal.
  Folha completa: `fotos_clailton/_triagem/folha_estudio.jpg`.
- **Magnific, uploads de fotos reais SEM FUNDO (PNG com alfa)**, com terno cinza e fundo preto, do mesmo ensaio usado nas thumbs w6Iw, cKS34 e 7w0d.
  São de baixa resolução (~700–840 × 890–940): xgdKkiAjfW, jSXk13XLD0, MXwc0ugDCm, 5xVFHPAKxe.
- **Magnific, uploads do ensaio azul em 2305×4096** (o mesmo ensaio do Drive, só que reduzido): kLwDR5t16B, 3G0bIiDREY, rlJe2kuxtc, povJKVtehw.
  Prefira os originais do Drive.
- **Magnific, gerações de IA** (jul./2026, "identidade travada"), sem barba e sem bigode (conferi o rosto ampliado):
  - camisa branca no estúdio azul, apontando: 624EFXUiJO, 74SIoAcJAL, vut699Ya47 e J9UthIoOq4 (fundo cinza), todas em 4096²;
  - dedo para cima: brFWjPN5Y2 e VdclBufMMU (1440×2560);
  - braços cruzados: YVGrD3RWeC e mC8NudOhJQ.
  As 12 gerações de "follow-up comercial" (celular, CRM) não servem para thumb. SOsBfIlUb8 e xgPVxeJjfW **não são o Clailton**.
  Link de cada uma: `https://www.magnific.com/app/creation/<ID>`.
- **Drive, outros lugares**:
  - "Fotos Especialistas/Clailton" é uma pasta compartilhada por educacaolegacy@gmail.com, com fotos de 2024/25. Não está no G:.
  - `G:/Meu Drive/FOTOS/CONEXÃO LEGACY - 08 05 2026` tem 67 fotos de evento.
  - Os PNGs antigos (CLAILTON_CARROSSEL_LP.png, Clailton Luiz.png, BÔNUS CLAILTON.png) **não têm transparência** e são pequenos. Descartei.
  - Os "thumb N (recorte rosto).png" de EP01–EP04 são quadros de vídeo das thumbs anteriores.
- **Óculos**: em nenhuma foto do ensaio, nem nas IAs, nem nas thumbs do canal o Clailton usa óculos. Ele aparece de óculos só nos vídeos gravados no carro.
- **Fundo**: nenhuma foto do Drive vem sem fundo. Sem fundo, só as 4 PNG do Magnific (14–17).

### Copiadas para `C:/Render/_youtube/fotos_clailton/` (folha numerada: `folha_fotos_clailton.jpg`)

| # | Arquivo | Origem | Resolução | Fundo | Expressão / pose |
|---|---|---|---|---|---|
| 01 | 01_drive_DSC05258.jpg | Drive, ensaio fev./26 | 3376×6000 | estúdio azul + letreiro | sério e confiante, blazer, mãos juntas |
| 02 | 02_drive_DSC05260.jpg | Drive | 3376×6000 | estúdio azul | sorriso aberto, blazer |
| 03 | 03_drive_DSC05273.jpg | Drive | 3376×6000 | estúdio azul | pensativo, mão no queixo, olhando para a câmera |
| 04 | 04_drive_DSC05271.jpg | Drive | 3376×6000 | estúdio azul | perfil, olhar "visionário" para o lado |
| 05 | 05_drive_DSC05297.jpg | Drive | 3376×6000 | estúdio azul | explicando, mãos abertas (corpo mais distante) |
| 06 | 06_drive_DSC05334.jpg | Drive | 3376×6000 | estúdio azul | sério e frontal, camisa |
| 07 | 07_drive_DSC05339.jpg | Drive | 3376×6000 | estúdio azul | braços cruzados, sorriso |
| 08 | 08_drive_DSC05343.jpg | Drive | 3376×6000 | estúdio azul | sorriso de canto, desconfiado |
| 09 | 09_drive_DSC05352.jpg | Drive | 3376×6000 | estúdio azul | braços cruzados, olhando para cima/lado |
| 10 | 10_drive_DSC05356.jpg | Drive | 3376×6000 | estúdio azul | pensativo, mão no queixo, olhando para cima |
| 11 | 11_drive_DSC05363.jpg | Drive | 3376×6000 | estúdio azul | sério e duro, close |
| 12 | 12_drive_DSC05374.jpg | Drive | 3376×6000 | estúdio azul | apontando/mostrando para o lado e para cima, surpreso |
| 13 | 13_drive_DSC05386.jpg | Drive | 3376×6000 | estúdio azul + softbox | mão erguida, de perfil (corpo inteiro) |
| 14 | 14_magnific_xgdKkiAjfW_semfundo.png | Magnific (upload, foto real) | 715×941 | **sem fundo** | braços cruzados, sorriso confiante, terno cinza |
| 15 | 15_magnific_jSXk13XLD0_semfundo.png | Magnific (upload) | 683×914 | **sem fundo** | sorriso, terno cinza, mãos no bolso |
| 16 | 16_magnific_MXwc0ugDCm_semfundo.png | Magnific (upload) | 688×893 | **sem fundo** | sorriso aberto, mão estendida (convite) |
| 17 | 17_magnific_5xVFHPAKxe_semfundo.png | Magnific (upload) | 841×899 | **sem fundo** | explicando, braços abertos |
| 18 | 18_magnific_IA_624EFXUiJO.jpg | Magnific (IA) | 4096×4096 | estúdio azul | sério, apontando para a esquerda (para o texto), camisa branca |
| 19 | 19_magnific_IA_brFWjPN5Y2.jpg | Magnific (IA) | 1440×2560 | estúdio azul | sério, dedo indicador para cima |
| 20 | 20_magnific_IA_YVGrD3RWeC.jpg | Magnific (IA) | 1440×2560 | estúdio azul | sério, braços cruzados, camisa branca |

Observações para o uso:
- 01–13 precisam de recorte. Use rembg local; não usei créditos.
  O letreiro "LEGACY EDUCAÇÃO" atrás da cabeça some no recorte, mas atenção ao contorno da cabeça careca contra o letreiro claro.
- 14–17 já vêm recortadas, mas são pequenas. Na thumb, a pessoa tem ~720 px de altura, então elas entram quase em 1:1. Fique de olho em serrilhado.
- 18–20 são IA. O rosto está fiel e sem barba/bigode, mas prefira as reais. A 18 (apontando para o lado do texto) casa bem com o layout "pessoa à direita".
- A triagem completa está em `fotos_clailton/_triagem/`:
  - `folha_estudio.jpg`: as 117 do ensaio;
  - `folha_cand1.jpg`: 32 candidatas;
  - `folha_magnific.jpg`: gerações de IA;
  - `folha_magnific_up.jpg`: uploads;
  - `rostos_14a20.jpg`: conferência de rosto.
