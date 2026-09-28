# Matriz de pauta: ângulo, formato e objetivo

Usada pelo Diretor de Pauta para transformar uma ideia (ou uma referência desconstruída) em 2 a 3 ângulos, cada um com formato sugerido e motivo. **Quem escolhe o formato é o usuário**; o Diretor só recomenda.

## Árvore de decisão de formato

1. **A ideia tem (ou ganha) 3+ âncoras visuais mostráveis?** História com personagens, caso de empresa, fábula, notícia, sequência de cenas do dia a dia, montagem de dados, objeto em cena. → candidata a **TELA DIVIDIDA**.
2. **A força está numa frase que vira título?** Paradoxo, finitude, ordem contraintuitiva, pergunta direta, tese proibida sobre vida ou sobre patrão x funcionário. → candidata a **NOVELA**.
3. **As duas coisas?** Ofereça os dois ângulos (um por formato) e explique a diferença.
4. **Nenhuma das duas?** O tema ainda não é reel. Procure a tese proibida (o que o dono de empresa acredita e está errado?) ou o caso concreto (quem viveu isso, com nome e número?). Se não achar, diga ao usuário.

Encaixe tema x formato (maduros; acertos acima de 1x / n):

| Tema | NOVELA | TELA DIVIDIDA | Recomendação |
|---|---|---|---|
| Patrão x funcionário | **3,71x · 17/24** FORTE | 2/8 | Novela; na tela só com fábula ou caso |
| Finitude / tempo de vida | 4/5 (todos ≥ 3x) | 1/1 ≥ 3x | Os dois; novela para tese, tela para cenas |
| Dinheiro / sucesso | 5/5 | 1/1 (16x) | Os dois |
| Relações (amizade, traição, família) | 14/29 | 3/6 | Novela com hook forte; recado de relação vive de repost |
| Gestão técnica (processo, caixa, reunião) | 10/23 (0,81x) | 5/9 | Tela com caso de empresa ou novela com número que dói |
| Comportamento / disciplina | 3/11 (0,66x) | 2/3 | Tela com história ou dado; evitar novela genérica |
| Notícia / política | 1/3 | 2/4 | Tela com print; prazo de validade curto; sem figura política como protagonista |

Encaixe hook x formato: tabela completa em `hooks.md`. Resumo: novela = paradoxo, finitude, pergunta direta, ordem contraintuitiva, tese proibida. Tela = tese proibida + história, abertura narrativa, finitude, pergunta direta; promessa só se o vídeo cumprir ao pé da letra.

## Objetivo e política de CTA

| Objetivo | Quando | CTA |
|---|---|---|
| **Alcance** (padrão da novela) | Furar a bolha, seguidor novo | Nenhum; no máximo "me siga" ou anti-CTA coerente |
| **Envio** | Tema com destinatário óbvio (o sócio, o amigo, o pai) | "Manda este vídeo para [quem]..." casado com o tema |
| **Salvamento** | Método, dado, fórmula, checklist | "Já salva esse vídeo" no começo |
| **Conversão** (slot de talking head do funil) | Impulsão, sessão estratégica, comunidade | 1 palavra-chave temática depois do fecho, com a dor nomeada antes. Avisar: reduz alcance e repost |

Na novela, o padrão é alcance. **Na tela dividida, pergunte sempre** (o slot do funil é de conversão, mas os virais do formato não tinham CTA).

## Ponte para o empresário

Tema universal atrai público frio; a ponte até a 2ª ou 3ª frase garante que o seguidor novo seja dono de empresa.
- Casamento → "Você vai se arrepender de abandonar o emprego seguro e abrir uma empresa." (2ª frase)
- Filhos → "A empresa que um dia ele vai trabalhar não é a extensão da sua família."
- Morte → "Coisas que serão esquecidas estão decidindo o que você faz com a tua vida hoje."
- Celular → presença → "O teu filho não vai ter a mesma idade de novo."
- Confiança → "Vai abrir uma sociedade até com seu melhor amigo? Faça um bom contrato."

## Campos da pauta (template do `01-pauta.md`)

```
# Pauta · <ideia> · <data>
Entrada: <ideia do usuário | referência: 00-referencia.md>

## Ângulo A · formato sugerido: <NOVELA|TELA DIVIDIDA> · <exploração?>
Por que este formato: <1 a 2 frases ligadas aos dados>
Objetivo sugerido: <alcance|envio|salvamento|conversão> · CTA: <política>
Tese "proibida": <frase que o dono de empresa quer contestar>
Tema universal e ponte: <tema> → <frase-ponte até a 3ª frase>
Oposição A x B: <A> x <B>
Hook-alvo: <tipo> (+ alternativo: <tipo>) · rascunho: "<hook provisório>"
Material concreto: <cenas, histórias, números, casos; na tela, 3+ âncoras mostráveis com tipo>
Virada: <que erro nomeia> · como absolve o espectador: <...>
Faixa de palavras: <novela 170-260 | tela 280-460>
Riscos: <fatos a verificar, desgaste do tema nas últimas 2 semanas, prazo de validade, direitos de imagem>
Gate P: tese soa proibida [sim/não] · ponte até a 3ª frase [sim/não] · 1 oposição [sim/não] · (tela) 3+ âncoras [sim/não]

## Ângulo B ...
## Recomendação do Diretor: <ângulo + formato + objetivo, em 1 frase>
```

## Gate P (a pauta só segue se passar)

- A tese soa errada, ofensiva ou proibida para quem ouve pela 1ª vez.
- Existe ponte universal para o empresário até a 3ª frase.
- Existe UMA oposição de dois lados.
- Na tela dividida: 3 ou mais âncoras visuais que a edição consegue mostrar.

Se falhar: reangular, trocar de formato ou avisar que o tema não sustenta um reel.

## Desgaste e exploração

- Antes de propor, busque em `roteiros/` os roteiros das últimas 2 semanas (Grep por tema, tipo de hook e ressalva). Evite repetir o mesmo tipo de hook e a mesma ressalva em sequência.
- Finitude e paradoxo são os tipos mais fortes e os que mais cansam: no máximo 1 de cada por semana.
- Em cerca de 1 a cada 5 pautas, inclua um ângulo de **exploração** (tipo de hook ou tema ainda pouco testado no perfil) e marque como tal. É assim que o Analista mensal descobre o próximo padrão.
