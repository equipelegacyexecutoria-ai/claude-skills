# Rubrica de alcance (Auditor)

O Auditor vê só o roteiro, o formato e o objetivo. Não vê a pauta, as intenções do roteirista nem as métricas de reels reais. Pesos iniciais, a reajustar a cada backtest do Analista mensal.

## Gates (passa / não passa)

| Gate | Passa quando |
|---|---|
| G1 · CTA coerente com o objetivo | Alcance: nenhum CTA de venda (vale "me siga" ou anti-CTA coerente). Envio: pedido de envio casado com o tema. Salvamento: "já salva" no começo. Conversão: exatamente 1 palavra-chave, depois do fecho, com a dor nomeada antes. "Link da bio" nunca passa em alcance. |
| G2 · Fatos | Todo número, nome, data, caso, notícia e fato biográfico está verificado pelo Checador ou marcado [VERIFICAR ANTES DE GRAVAR]. Biografia fora do banco de `voz-clailton.md` reprova. |
| G3 · Lint | `scripts/lint-roteiro.ps1` sem FALHA. Avisos (AVISO) não reprovam, mas entram na nota de voz. |
| G4 · Tela com imagem (só tela dividida) | Todo bloco tem âncora visual no mapa. |

Gate reprovado = veredito **Revisa** no mínimo, qualquer que seja a nota.

## Pontuação (100)

| Bloco | Pts | Critério e como pontuar |
|---|---|---|
| **Ângulo** | 15 | Ponte para o universo do dono de empresa até a 3ª frase (6: explícita; 3: tema universal de vida adulta sem ponte explícita; 0: nenhuma) · força do tema no formato, pela tabela de `pauta-matriz.md` (5) · existe uma pessoa óbvia para quem mandar (4) |
| **Hook** | 30 | Tipo com evidência no formato, pela tabela de `hooks.md` (10) · soa errado, contestável ou proibido (8) · fala com "você" e com certeza total (6) · imagem concreta ou número (6) |
| **Retenção** | 15 | Ressalva em até 5 s que abre um loop (5) · uma oposição espelhada que volta nos blocos (5) · re-gancho ou ponte no meio que renova a curiosidade (5) |
| **Meio concreto** | 15 | Cena, história ou número específico (8) · Novela: funciona sem nenhuma imagem, com as cenas na fala (7) / Tela: âncora visual mostrável em todo bloco (7) |
| **Virada e fecho** | 20 | Virada nomeia o erro e absolve o espectador (8) · fecho ≤ 15 palavras, citável sozinho, sem resumir (8) · fecho ecoa ou cumpre o hook (4) |
| **Voz** | 5 | Bate com a digital de `voz-clailton.md` (teu/tua, para, sem muleta na abertura, frases curtas); desconte 1 por AVISO de voz do lint |

## Veredito

- **Aprova**: nota ≥ 80, Hook ≥ 24/30 e nenhum gate reprovado.
- **Revisa**: nota 65 a 79, ou Hook < 24, ou gate reprovado. Máximo de 2 voltas.
- **Repensa**: nota < 65, ou ainda < 80 depois de 2 voltas. Volta para a pauta ou para o hook. Se o usuário quiser, entrega a melhor versão com aviso explícito.

## Como avaliar

1. **Rode o lint** (`powershell -NoProfile -ExecutionPolicy Bypass -File <skill>\scripts\lint-roteiro.ps1 -Arquivo <roteiro> -Formato <novela|tela_dividida> -Objetivo <objetivo>`) e registre FALHA e AVISO.
2. **Espectador frio.** Leia como um dono de empresa de 40 anos, rolando o feed às 21h, que nunca ouviu falar do Clailton. Registre em cada ponto se ele fica ou sai e por quê: 0 a 3 s · 3 a 8 s · 30% do vídeo · virada · fim. Diga para quem ele mandaria o vídeo e por qual frase.
3. **Ranqueie os hooks** (os do roteirista + os do Especialista) **par a par, às cegas**: "qual faria esse espectador parar e ouvir a 2ª frase?". Ganha quem vencer mais pares; em empate, o de imagem concreta. Nota absoluta de hook não decide.
4. **Pontue** bloco a bloco com uma linha de justificativa por critério.
5. **Correções**: até 5, ordenadas pelos pontos em jogo, cada uma com a frase atual e a frase nova pronta para colar.

## Formato da auditoria (`05-auditoria.md`)

```
# Auditoria · <roteiro> · v<N>
Veredito: <APROVA|REVISA|REPENSA> · Nota: <n>/100 (Ângulo <a>/15 · Hook <h>/30 · Retenção <r>/15 · Meio <m>/15 · Virada e fecho <v>/20 · Voz <x>/5)
Gates: G1 <ok|falhou: motivo> · G2 <...> · G3 <...> · G4 <...|n/a>
Lint: <FALHA n · AVISO n: lista curta>

## Espectador frio
0-3 s: <fica/sai> · <por quê>
3-8 s: ...
30%: ...
Virada: ...
Fim: ... · Mandaria para: <quem>, pela frase "<...>"

## Ranking de hooks (par a par)
1. "<hook>" · venceu <n> de <m> · <motivo em 1 linha>
2. ...

## Correções (por pontos em jogo)
1. [+<pts> <bloco>] Atual: "<...>" → Nova: "<...>"
...
```

## Validação (atualizada pelo Analista mensal)

- **26/09/2026 · holdout de setembro (10 reels não citados nas referências):** AUC 0,84 (21 de 25 pares alto x baixo na ordem certa) · Spearman nota x lift 0,28 · mesma copy pontuada duas vezes: 70 e 70. O hook foi o bloco que mais separou. Erro conhecido: paradoxo em 3ª pessoa ("Os pessimistas muitas vezes estão certos, mas os otimistas... ficam ricos", 2,55x) recebeu 58; em paradoxo, dê peso à oposição antes de descontar a falta de "você" (INDICATIVO, n=1). Relatório: `dados/relatorios/2026-09-backtest-auditor.md`.
- Nenhum reel real do holdout passou de 79: 80+ significa "melhor que a média do perfil", não "normal".

## Exemplos calibrados (julho e agosto; setembro fica fora para o backtest)

**NOVELA #080 · "Você vai se arrepender de casar e também vai se arrepender se não casar." · 4,25 mi (126x) → 94, APROVA**
Ângulo 15 (casamento com ponte para "abrir uma empresa" na 2ª frase; dilema universal; manda-se para o cônjuge ou o amigo) · Hook 28 (paradoxo é o tipo mais forte da novela; contestável; "você" com certeza; falta imagem visual) · Retenção 14 (a 2ª frase dobra a aposta com o emprego seguro; espelhos "Quem casou... / Quem ficou sozinho..."; re-gancho "O problema é que você conhece os defeitos da vida que você vive") · Meio 13 (listas espelhadas, sem número nem história) · Virada e fecho 19 ("compara o peso da realidade com a perfeição de uma fantasia" absolve; "Você escolhe com qual arrependimento está disposto a viver" ecoa o hook; o fecho final passa de 15 palavras) · Voz 5.

**NOVELA #051 · "Tem gente querendo consertar o mundo, mas não consegue organizar a própria gaveta." · 11 mil (0,32x) → 50, REPENSA**
Ângulo 8 (comportamento genérico, o tema mais fraco da novela) · Hook 10 (aforismo sobre "tem gente": 0 de 10 acima de 3x; acusa terceiros em vez de "você"; "gaveta" é a única imagem) · Retenção 7 (sem ressalva; a oposição mundo x gaveta some no meio) · Meio 10 (lista de palpites, sem cena nem número) · Virada e fecho 11 (acusa em vez de absolver; fecho de 17 palavras) · Voz 4.

**TELA #092 · "Teu funcionário não vai abandonar o seu próprio sonho para passar a vida inteira construindo o teu sonho." · selfie sem imagens, com "Clique no link da bio" · 27 mil (0,79x) → 62, REVISA (G1 e G4 reprovados)**
Ângulo 11 (patrão x funcionário é fraco na tela) · Hook 21 (tese proibida, mas "seu próprio sonho" e nenhuma imagem) · Retenção 10 ("Olha só... né" como muleta na 2ª frase) · Meio 5 (nenhuma âncora visual) · Virada e fecho 12 (fecho engolido pelo CTA) · Voz 3. **Lição: a mesma ideia, regravada depois em novela, enxuta e sem CTA, fez 12 vezes mais. Formato, muletas e CTA pesam.**

**TELA #100 · "Depois de assistir esse vídeo, você não vai querer assistir o próximo." · 3,98 mi (118x) → 91, APROVA**
Ângulo 12 (celular e presença; universal sem ponte explícita para empresa: 3 de 6) · Hook 25 (promessa é aposta na tela, mas aqui o vídeo cumpre ao pé da letra; "Acredite.") · Retenção 14 (tela infinita x vida finita; re-gancho "Mas existe uma coisa muito estranha acontecendo") · Meio 15 (banheiro, café, semáforo, elevador: cada item é uma imagem) · Virada e fecho 20 ("Essa tela nunca acaba, mas a tua vida sim."; o fecho manda desligar o celular, cumprindo o hook) · Voz 5.
