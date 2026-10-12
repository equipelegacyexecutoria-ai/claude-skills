# Esquema Canônico de Avatar / Célula de Conceito

A estrutura obrigatória para todo avatar de comprador em todos os seus projetos e marcas.
É ao mesmo tempo o **template de construção** (use para criar avatares) e o **checklist de auditoria** (avalie os existentes).

Ele existe porque uma auditoria entre projetos descobriu que mapas de avatar acertam com consistência a camada de *superfície* (frase da
persona, gatilho, alternativas que falharam, consciência, caminho de prova, oferta, estágio), mas pulam as camadas de *profundidade psicológica*
e de *evidência* - exatamente os campos que fazem a copy converter e tornam uma persona auditável. Eles estão marcados
como **[PROFUNDIDADE-OBRIGATÓRIA]** abaixo e não podem ser pulados.

Uma persona NÃO é demografia. É um momento-gatilho + crença + emoção + identidade + necessidade de prova que muda
o anúncio. Se um campo não mudaria o ângulo, o gancho, a prova, a oferta ou o criativo, ele não está trabalhando - corte.

## Os 19 campos (★ = os 8 campos de profundidade/evidência que mais faltam)

**Camada de superfície (geralmente presente)**
1. **Persona / contexto do problema** - uma frase completa: um comprador específico reconhecendo uma circunstância específica.
2. **Evento-gatilho** - o momento concreto que causou a busca ativa (prazo, diagnóstico, foto, conta, vergonha, tentativa que falhou, acordar às 3 da manhã).
3. **Alternativas que falharam** - o que ele já tentou que não funcionou (e por quê).
4. **Nível de consciência** - Schwartz: inconsciente → consciente do problema → consciente da solução → consciente do produto → totalmente consciente. Define quanto educar.
5. **Caminho de prova / necessidades de prova** - demonstração, especialista, UGC, avaliação, mecanismo, ingrediente/material, sensorial, comparação, dados.
6. **Ângulo** - uma frase completa: a mudança de crença / o argumento que o anúncio faz.
7. **Oferta / proposta de valor** - o enquadramento de compra (combo, garantia, reversão de risco, preço/valor, assinatura).
8. **Promessa do gancho** - a promessa de relevância dos primeiros 3 segundos / primeira linha (Atenção = um gancho de fato/prova do material do usuário; um sem sustentação ganha placeholder e flag - a Camada Prova-ou-Pergunta, revisada por `checagem-de-alegacoes`).
9. **Formato** - o contêiner de execução (estático, UGC, VSL, advertorial, fundador, demonstração, carrossel).
10. **Estágio / canal** - topo / meio / fundo de funil / biblioteca principal / célula de teste / sandbox / DPA.
11. **Contexto nativo / cultural** - mercado + idioma (escreva nativamente no idioma do mercado, não traduzido).

**Camada de profundidade ★ [PROFUNDIDADE-OBRIGATÓRIA] - os campos que a auditoria encontrou faltando**
12. ★ **Crença limitante → crença habilitadora** - "Hoje acredita em [X]. Precisa acreditar em [Y] para comprar." A maior alavanca de copy que existe. Nunca deixe implícito em "dores".
13. ★ **Âncora de identidade / autoconceito** - "Eu sou o tipo de pessoa que…" antes → depois. Identidade é o sinal mais pegajoso de "isso é para mim?"; sem ela a copy escorrega para enquadramento só de sintoma.
14. ★ **Escada de dor / hierarquia de desejo** - dor superficial → dor média → dor profunda, e desejo superficial → desejo profundo. Força o desejo mais forte para o topo em vez de toda faixa parecer igualmente urgente.
15. ★ **Estado emocional / barreira** - a emoção real no gatilho (vergonha, pavor, resignação, ceticismo, esperança) e o custo emocional da inação. Copy que erra isso soa fria.
16. ★ **Objeção de fundo de funil → roteamento de resposta** - as objeções específicas de perto da compra para ESTE avatar, cada uma mapeada a uma resposta (garantia, linha segura em alegação, FAQ, bloco de prova). Para avatares sensíveis a alegação (saúde, suplementos, dinheiro, imagem corporal, outras categorias reguladas), encaminhe por `**checagem-de-alegacoes**` e pelas faixas do semáforo.
17. ★ **Sensibilidade a valor** - postura de preço/acesso/confiança: premium é uma crença habilitadora ("confio porque é premium") ou uma barreira? O que ele valoriza (velocidade, transparência, respaldo clínico, privacidade)?

**Camada de evidência ★ [PROFUNDIDADE-OBRIGATÓRIA] - torna o avatar auditável**
18. ★ **Status da evidência + fonte** - `validated` (cite o dado: linha de avaliação/VOC, linha de analytics, leitura de GA4, n da pesquisa) ou `hypothesis` (diga isso). Vincule ao Banco de Provas do projeto (construído com `checagem-de-alegacoes`; template: MODELO-DO-BANCO-DE-PROVAS.md na pasta do Biblioteca dos Mestres). Nenhum avatar alega "validated" sem fonte rastreável. Esta é a Camada Prova-ou-Pergunta aplicada a personas.
19. ★ **Campos de prontidão para lançamento** - variável de teste, tipo de trabalho, papel do criativo, critério de sucesso, critério de corte/parada, linhagem da fonte, época de lançamento. Obrigatórios para todo avatar que você planeja testar, não só o principal; sem eles, vencedores criam atrito ao escalar.

## Template por avatar (copie e cole)
```
### <AVATAR_ID> - <nome curto>  [estágio: TOFU/MOFU/BOFU] [evidência: validated|hypothesis]
- Persona (frase completa):
- Evento-gatilho:
- Alternativas que falharam:
- Nível de consciência:
- Crença limitante → crença habilitadora:        ★
- Âncora de identidade (antes → depois):         ★
- Escada de dor (superficial→profunda) / desejo: ★
- Estado emocional / barreira:                   ★
- Caminho de prova / necessidades de prova:
- Objeções de fundo de funil → respostas:        ★
- Sensibilidade a valor:                         ★
- Ângulo (frase completa):
- Oferta / proposta de valor:
- Promessa do gancho:
- Formato:
- Notas nativas/culturais:
- Status da evidência + fonte(s):                ★
- Prontidão para lançamento: test_variable / work_type / creative_role / success_gate / kill_gate / source_lineage / launch_epoch   ★
```

## Regras
- Não marque um avatar como completo sem os quatro campos em frase completa (persona, ângulo, oferta, gancho) E os campos de profundidade 12–17.
- Não marque `evidence: validated` sem fonte citada (avaliação/VOC/analytics/GA4/n da pesquisa). Caso contrário é `hypothesis` - diga isso honestamente (o padrão correto para qualquer marca pré-lançamento ou qualquer mercado onde você ainda não tem base de resposta).
- Não crie um avatar novo a menos que ele mude o anúncio, a prova, a oferta ou o trabalho de estágio (sem explosão de personas).
- Demografia (idade/gênero) entra só como precondição, nunca como a persona, a menos que o sinal do anúncio mude por causa dela.
- Mantenha os avatares em sincronia com o banco de provas e seu rastreador de conceitos; quando um avatar hipótese ganhar dados reais, atualize o status de evidência e cite a linha.
