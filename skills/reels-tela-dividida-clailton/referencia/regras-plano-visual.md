# Regras do plano visual (o que o orquestrador decide)

Tirado dos 6 reels da equipe (`estilo-tela-dividida.md`). O plano é a ÚNICA parte criativa da edição:
o resto (cortes, legenda, aberto/fechado, flash, CTA) sai por regra. Escreva `T\plano.txt` numa
passada, lendo `palavras_legenda.txt` (índices) e, se houver, o MAPA DE ÂNCORAS do roteiro.

## Quanto e onde

- **Imagem em ~30–40% do tempo** (o melhor reel: 34%; o pior: 58%). Clailton ~60%.
- ~10–15 imagens por minuto. Cada imagem 1–3 s (mediana da equipe 1,3 s); mais de 4 s em tela cheia:
  divida em 2 imagens ou use `dividida`.
- **Tempo mínimo (regra do usuário): nada fica menos de 1,0 s na tela** — nem imagem, nem o Clailton
  entre duas imagens. O `plano_td.py` estica sozinho e avisa no `timeline.txt` ("tempo mínimo na
  tela"). Trecho de fala curto demais para uma imagem própria: junte com a vizinha em vez de forçar.
  Exceção de verdade (lista em sequência rápida, "mansões, carros, aviões"): `rapido` no fim da linha
  (mínimo 0,6 s).
- **Imagem entra na palavra que a nomeia** (`@a` = índice da 1ª palavra do trecho que ela ilustra)
  e sai na 1ª palavra do plano seguinte (`@a-b`, b = última palavra do trecho).
- **Gancho** (0 a 3–8 s): SEMPRE tela dividida (`ABERTURA @0-b`, b = fim da 1ª frase ou do gancho),
  com 1–3 `TOPO` (uma imagem por frase curta). A legenda vira tarja preta sozinha.
- **História/caso/exemplos**: o bloco com mais imagem (uma por ação, nome, item de lista).
- **Ponte, lição, conselho, pergunta para o espectador, fecho**: Clailton, sem imagem (os últimos
  10–20 s quase sempre só ele).
- Não encoste duas imagens longas: entre uma sequência e outra, volte ao Clailton.

## Cultura pop primeiro (preferência do usuário, 27/09/2026)

**O padrão é VÍDEO de cultura pop: cena de filme, série, desenho animado conhecido que mostra o que
está sendo dito.** Ele aprovou "Delírios de Consumo" (mulher andando com as sacolas) e o Rocky na
escadaria e reprovou as fotos de banco (academia, dinheiro, balde, espelho). **Foto só para fato:**
pessoa real citada pelo nome, marca/produto/livro, notícia, print, dado.

Para cada trecho, pergunte: "que cena famosa mostra isso?" — gastar/comprar por impulso → Delírios de
Consumo; dinheiro → O Lobo de Wall Street; desistir da academia → Homer Simpson; balde/água → Fantasia
(O Aprendiz de Feiticeiro); inundação → Titanic; consertar com fita → MacGyver; encarar a si mesmo →
Taxi Driver no espelho; "agora vai" → Rocky na escadaria; traição → O Poderoso Chefão II; sociedade →
Breaking Bad. Prefira cena que qualquer pessoa reconhece em 1 s.

## Acervo local e canais de montagem (antes de buscar na internet)

1. **Acervo do PC** (`referencia/acervo_catalogo.md`, 160 vídeos já vistos cena a cena): procure por tema
   ou obra (Grep "dinheiro", "solidão", "entrevista de emprego", "Wolf"). Cena boa → `acervo=<código>
   t=<segundo do início>` na linha, mantendo busca e `en:` (se o acervo não estiver no PC, cai na busca).
   Ex.: `@73-75 filme "The Wolf of Wall Street money scene" | en: man throwing cash money acervo=WOLF-03 t=42`.
   Sem `acervo=`, a busca já põe sozinha os 2 vídeos do acervo mais parecidos com o `en:` entre os candidatos.
   Nunca use vídeo marcado **NÃO USAR**; atenção às cenas com ⚠ (texto em inglês, tarja, escuro).
2. **Montagens só de imagem** (sem fala, sem texto, 4K): canais https://www.youtube.com/@theclipof/videos
   ("Visuals - <obra> (4K)", ~320 obras) e https://www.youtube.com/@TheBeautyOf/videos ("The Beauty Of
   <obra>", ~390 obras, também diretores). Lista: `referencia/montagens_youtube.tsv`. Quando a busca cita a
   obra em inglês ("Succession ...", "Heat ..."), a montagem entra sozinha como candidata. São planos
   bonitos de clima (cidade, solidão, poder, luxo, estrada): ótimos para `dividida` e para emoção; para
   AÇÃO específica (gritar, contar dinheiro) prefira a cena do filme.

## Qual imagem para cada tipo de fala

| Na fala | Linha do plano | Exemplo |
|---|---|---|
| Nome de pessoa, marca, lugar, produto, livro | `foto "<nome> <contexto>"` na palavra do nome (vídeo dele, se existir) | `@17-19 foto "Thomas Edison retrato" \| en: black and white portrait of Thomas Edison` |
| História inventada / parábola (ações) | cena de filme/série que mostra a ação; `ia` só com gerador autorizado | `@11-12 filme "woman bursts into hotel room movie scene" \| en: woman running into a hotel room` |
| Comportamento humano (traição, amizade, sociedade, briga, ingenuidade, motivação) | `filme "<filme/série> <cena> scene"` icônica | `@74-76 filme "Breaking Bad Jesse hugs Walter scene" \| en: two men hugging emotionally` |
| Exemplo do dia a dia (academia, dinheiro, compras, livro, celular) | cena de filme/série/desenho que mostra aquilo | `@80-85 filme "Confessions of a Shopaholic shopping scene" \| en: woman carrying many shopping bags` |
| Filme citado | `dividida filme` enquanto ele comenta | `@20-40 dividida filme "Limitless cleaning apartment scene" \| en: man cleaning a messy apartment` |
| Lista de coisas concretas | uma cena por item (0,6–1,2 s cada) | "mansões, carros, aviões" → 3 cenas |
| Metáfora | a cena que encena a metáfora; repetida com `igual` quando a fala volta nela | `@113-118 filme "Fantasia Mickey pouring bucket of water scene" id=agua` · `@128-129 igual agua` |
| Notícia, dado datado, conversa | `cartao print url=<link>` (print da página) ou `cartao foto "<manchete>"` | `@40-45 cartao print url=https://g1.globo.com/...` |
| Número forte | `NUMERO @a-b "0,07%"` (sobre o Clailton, não é imagem) | `NUMERO @66-69 "2 SEMANAS"` |
| "você", conselho, lição | nada (Clailton) | — |
| Frase curta de fecho que você quer mais perto | `FECHADO @a-b` (o automático já pega a maioria) | `FECHADO @254-258` |

Objeto que o roteiro mandou filmar no set, ou foto própria: `arquivo "C:\...\foto.jpg"`.

## Como escrever a busca

- `"..."` = busca de imagem (português funciona; para filme e vídeo use inglês: é YouTube).
- `en:` = descrição em inglês do que DEVE aparecer na imagem (ranqueia os candidatos; também vira
  2ª busca). Seja visual e concreto: "hand stubbing out a cigarette in an ashtray", não "parar vício".
- Pessoa famosa: nome + contexto ("Chuck Feeney retrato idoso", "Zuckerberg senado depoimento").
- Filme/série: `"<título em inglês> <o que acontece> scene"`. A skill procura no YouTube e no TikTok
  (cena já vertical, às vezes da conta oficial), acha a janela da cena pelo CLIP e foge de legenda/crédito
  queimado. Se souber o vídeo: `url=https://youtu.be/... t=95` (ou link do TikTok/Instagram/X).
- Genérico ambíguo dá errado ("balde" sozinho = jogador do Barcelona). Descreva a cena.
- `id=nome` num item e `igual nome` em outro = mesma mídia (motivo que volta).

## Formato do plano.txt (exemplo real do teste, versão cultura pop)

```
ABERTURA @0-18
TOPO @0 filme "The Social Dilemma phone addiction scrolling scene" | en: teenager scrolling a smartphone in bed at night
TOPO @10 filme "Mad Men Don Draper smoking cigarette scene" | en: man in a suit smoking and putting out a cigarette
@49-56 filme "Pain and Gain gym workout scene Mark Wahlberg" | en: muscular man lifting weights in a gym id=academia
@57-65 filme "Homer Simpson exercise gives up scene" | en: cartoon man giving up exercising
NUMERO @66-69 "2 SEMANAS"
@73-75 filme "The Wolf of Wall Street money throwing scene" | en: man throwing cash money in the air id=dinheiro
@80-85 filme "Confessions of a Shopaholic shopping scene" | en: woman carrying many shopping bags in a store
@89-92 cartao foto "capa livro Hábitos Atômicos James Clear" | en: book cover of Atomic Habits id=livro
@106-112 filme "Fantasia Sorcerer's Apprentice brooms carrying water buckets scene" | en: cartoon brooms carrying buckets of water id=balde
@128-129 igual agua
@158-175 dividida igual balde
@225-230 filme "Rocky running up the stairs Philadelphia scene" | en: boxer raising his arms at the top of the stairs
@238-247 filme "Taxi Driver you talking to me mirror scene" | en: man staring at himself in the mirror
FECHADO @254-258
```
Opções no fim da linha: `url=`, `t=` (segundo no vídeo), `foco=0.3` (0 = esquerda, 1 = direita; manda
no lugar do reenquadramento automático), `zoom=in|0`, `rapido` (lista: mínimo 0,6 s em vez de 1 s). Outras linhas: `ETIQUETA vermelha "TEXTO"` (etiqueta fixa na abertura, estilo do
"Fórmula"), `ABERTO @a-b`, `SEMZOOM`, `SEMCTA` (reel de salvamento termina sem CTA), `ESTILO 0.7`
(força da camada película só neste vídeo; 0 desliga).

## Escolha dos candidatos (qa/candidatos_NN.jpg)

- Cada item mostra 4 candidatos JÁ recortados no layout (tela cheia 9:16, faixa de cima, cartão).
- Escolha padrão = 1º. Só escreva exceções em `T\escolhas.txt`: `b03 2` ou `b14 igual b07`.
- **Recuse**: marca d'água (etiqueta vermelha **MARCA?** = confira em tamanho real), texto grande de
  miniatura, quadriculado de "PNG falso", rosto cortado, tarja preta, **logo de canal/streaming no
  canto** (**LOGO?** pega o logo escrito; o desenhado — hulu, Netflix, FOX — só olhando o canto),
  trecho borrado de 240p no gancho, imagem que não mostra o que a fala diz. No gancho (`TOPO`) seja
  mais exigente: é a 1ª imagem do reel. Se nenhum serve: melhore a busca no plano e rode `td.py plano` + `td.py buscar T --so b05`.
- Imagem de banco limpa (pexels, pixabay, unsplash, freepik "fotos-gratis") serve; o padrão da equipe
  é imagem "orgânica" (cena de filme, foto real da pessoa, print).
- **Cena larga** (dois personagens afastados, plano geral, ação que precisa do quadro inteiro): no 9:16
  vira um pedaço que não se entende. Na folha ela vem como **LARGA**. Se vier `LARGA→div`, passe a
  linha para `dividida` (a faixa de cima mostra 79% da largura) e rode `td.py plano` — o recorte da
  faixa já foi calculado. Senão, escolha outro candidato ou busque um close da mesma cena.
- Prefira close e plano médio (rosto grande, ação perto da câmera): é o que funciona no vertical.
