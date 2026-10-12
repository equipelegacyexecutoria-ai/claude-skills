# Modelo Semáforo de Alegações

As faixas são **por produto** e lidas das salvaguardas/pesquisa de alegações daquele produto. Nunca invente uma faixa - derive-a. Abaixo está um exemplo trabalhado completo sobre um **produto fictício** ("ThermaFlow", um dispositivo aquecido de massagem para o pescoço), para você ver a forma de um mapa de faixas pronto; o mapa real de cada produto vem da pesquisa dele.

## Como derivar faixas para qualquer produto
1. Leia o `constraints.md` / `claim-proof-guardrails.md` do produto e qualquer pasta `*claim-research*` que você mantenha.
2. Classifique todo benefício/alegação em Verde / Amarelo / Aprovado pelo Dono / Vermelho usando as definições abaixo.
3. Se uma alegação não está coberta pelas salvaguardas existentes, classifique-a você mesmo a partir das definições abaixo, marque a faixa como provisória e liste-a para o dono confirmar; só alegações com padrão Vermelho e dados específicos apresentados como medidos recebem flag.

## Definições
- 🟢 **Verde** - sentida, local, específica, sustentável. Agressividade total de resposta direta permitida.
- 🟡 **Amarelo** - só com redação cuidadosa + fonte/contexto; enquadre como educação/segurança, não como prova de um resultado clínico sistêmico.
- 🟣 **Aprovado pelo Dono** - o dono liberou *com condições*; sinalize qualquer condição que esteja faltando.
- 🔴 **Vermelho** - a flag mais alta: merece um teste específico do produto e revisão de alegações antes de ir ao ar.

## Exemplo trabalhado - "ThermaFlow" (dispositivo aquecido fictício de massagem para o pescoço)
*Tudo nesta seção é uma simulação ilustrativa, não um produto real nem pesquisa de alegações real.*

**🟢 Verde (faixa do sentido/local):** "calor que você sente em menos de um minuto", "o pescoço solta", "aquela sensação de cabeça pesada depois do trabalho", "calor + pulsos + contato onde a tensão está", "calor sustentado a 45°C" (uma especificação real da ficha do produto).
Melhor espinha: *"Quando o pescoço trava, a cabeça é a primeira a pagar. O ThermaFlow aquece a região, os músculos soltam e a pressão alivia."* - sentido, local, específico, sem promessa clínica.

**🟡 Amarelo (só redação de educação/segurança):** "vasos sanguíneos", "fluxo sanguíneo", "circulação em direção à cabeça" - usáveis num enquadramento de educação ou FAQ de segurança ("por que um pescoço tenso pode parecer uma cabeça apertada"), nunca como prova de que o dispositivo produz um resultado clínico sistêmico.

**🟣 Aprovado pelo Dono - ramo de suporte à saúde** (ex.: "apoia a circulação saudável"). Condições, TODAS obrigatórias antes do uso: uma rota congruente dedicada (advertorial → página, não uma sobreposição em anúncio frio); uma página de estudos/pesquisa citando a ciência geral; um mapa de fontes; um FAQ de segurança; nenhuma promessa de métrica específica ("melhora X em Y%"); nenhum enquadramento de substituição de medicamento; nenhuma prova clínica específica do produto sugerida, a menos que esses dados existam de fato.

**🔴 Vermelho (a flag mais alta: merece teste do produto + revisão de alegações antes de ir ao ar):** "baixa a pressão arterial"; "trata hipertensão/enxaquecas"; "reduz [métrica] em X"; "relaxa as paredes dos vasos sanguíneos"; "alternativa a medicamento"; "clinicamente comprovado" (sem o teste); "pare de tomar seus remédios"; endosso falso de especialista/médico; medo diagnóstico (dor no peito, tontura, "assassino silencioso", "bomba-relógio").

## Postura para suplementos (derive dos arquivos do seu produto)
- 🟢 benefícios sentidos, ritual, ingrediente-como-mecanismo formulado como suporte; enquadramento de estilo de vida/identidade.
- 🟡 alegações ingrediente→benefício amarradas a uma fonte citada; estrutura "apoia/ajuda".
- 🔴 tratamento/cura de doença, promessas de nível hormonal ou resultado clínico sem comprovação, resultados garantidos, estudos fabricados. Confirme com a pesquisa de alegações do seu produto antes de publicar. No Brasil, alegações de suplementos e produtos de saúde seguem a regulação da ANVISA; o Código de Defesa do Consumidor (CDC) e o CONAR cobrem publicidade enganosa.

## Postura para a Amazon
- 🔴 linguagem de alegação restrita pela Amazon (médica/doença, "aprovado pelo FDA" ou "aprovado pela ANVISA" a menos que literalmente verdadeiro, garantias, pesticida/"nº 1" sem comprovação). Confira a política de alegações da Amazon em `politicas-de-anuncio-das-plataformas.md` e as restrições de listagem do produto antes da copy de listagem/PPC.

Regra padrão para todos os produtos: **comprove até a faixa mais alta defensável; nunca fabrique para alcançar uma faixa superior.** Se a faixa superior precisa de prova que você não tem, use um [placeholder] nomeado e uma flag.
