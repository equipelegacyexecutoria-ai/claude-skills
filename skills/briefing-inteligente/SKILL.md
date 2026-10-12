---
name: briefing-inteligente
description: "Skill de entrada do CopyOS: checagem de instalação das 9 skills e dos recursos, entrevista completa do negócio (gera BUSINESS-MEMORY.md e o Cartão de Restrição) e retomada de um projeto a partir do brief confirmado. Use as skills instaladas do CopyOS. Checagens de instalação nunca vasculham contas conectadas."
---
# Briefing Inteligente

## Selecione o trabalho, depois use a skill instalada

Há três trabalhos separados: checagem de instalação, entrevista completa do negócio, e trabalho de produto inicial ou de retorno. A entrevista é opcional e oferecida, nunca exigida: o CopyOS trabalha com o que o usuário der e pergunta só o que muda a peça (no máximo três perguntas por vez); a entrevista completa consolida os fatos quando o usuário aceita a oferta ou pede "monte meu brief do negócio". Siga o pedido atual do usuário. Não rode uma auditoria de instalação a cada início, nem comece uma entrevista durante uma checagem de instalação. Recheque só depois de uma atualização, de um recurso faltante, de uma mudança de host ou de um pedido explícito.

Esta é uma skill instalada, não um repositório nem um documento salvo do negócio. Abra os recursos relativamente à localização real ou ao identificador de recurso que o host fornece para esta skill. Nunca adivinhe um caminho no computador. Um título correspondente em resultados de busca não é uma skill instalada.

Para checagens de instalação, use apenas as ferramentas de skill instalada do host e os arquivos de recurso que elas expõem. Não vasculhe a Biblioteca do ChatGPT, o Google Drive, o GitHub, e-mail, sites públicos, conversas antigas ou outro computador em busca de arquivos de instalação. Não conecte mais contas, não peça acesso a repositório, nem crie arquivos SKILL.md substitutos. Uma menção histórica a uma pasta do CopyOS não é esta instalação.

Se uma skill obrigatória não está exposta a este chat, pare nessa dependência: diga em uma linha qual arquivo do CopyOS falta instalar (siga o Guia de Instalação do CopyOS) e continue com o que dá. As skills do CopyOS se carregam entre si pela ferramenta de skills do host; o usuário não chama skills, ele conversa. Se o host exigir uma seleção explícita (por exemplo, o menu de skills do ChatGPT ou `$nome-da-skill` no Codex), isso acontece uma vez, na primeira mensagem, e daí em diante as demais funcionam em segundo plano. Não invente sintaxe de seleção não suportada.

Para trabalho do negócio, confirme primeiro o negócio/cliente. Use apenas o brief e os arquivos fornecidos neste chat ou identificados pelo usuário neste projeto do negócio. Se faltarem, peça o arquivo. Não vasculhe arquivos de outros clientes para preencher lacunas. Pesquisa atual ou trabalho de conta podem usar fontes apropriadas quando solicitado; o limite de fontes de instalação não é uma proibição das ferramentas necessárias para um trabalho real.

## Identidade da instalação

O CopyOS é um produto só, instalado como skills avulsas. São 9 skills:

- `briefing-inteligente`: esta skill (entrada, entrevista, retomada).
- `voz-do-cliente`: pesquisa e dossiê de evidências.
- `posicionamento-de-marca`: enquadramento, voz, inimigo.
- `checagem-de-alegacoes`: Banco de Provas e flags de alegação.
- `copy-de-conversao`: o Motor de escrita (controlador do produto).
- `revisor-chefe`: passada de ofício.
- `checagem-pre-lancamento`: checklist antes de publicar.
- `memoria-e-checagem`: memória durável do projeto.
- `biblioteca-dos-mestres`: guias, prompts de exemplo e a Biblioteca dos Mestres (14 volumes).

Use as skills do CopyOS instaladas neste host para briefing-inteligente, para o controlador e para todo recurso de apoio nesta conversa. Nunca combine arquivos de duas instalações diferentes (por exemplo, uma cópia antiga e uma atual) para fazer um inventário passar. Se houver mais de uma cópia da mesma skill disponível, liste o que encontrou e pergunte qual usar. Não adivinhe em silêncio.

## Checagem de instalação

Percorra estes passos em ordem. Pare numa dependência indisponível e dê o próximo passo exato, em vez de gerar uma tabela longa de checagens que não puderam rodar.

1. **Confirme a invocação.** Abra este SKILL.md instalado e `references/testes-de-instalacao.md` usando o mecanismo de skills do host. Reporte o nome da skill, a localização/identificador real do recurso e um título lido da referência. Se o host não expõe a localização do recurso, diga isso e reporte a evidência real de invocação/leitura da skill; nunca invente um caminho. Não infira a invocação a partir de uma mensagem anterior afirmando que a skill foi carregada.
2. **Confira as 9 skills.** Abra o SKILL.md de cada uma das 9 skills listadas acima pela ferramenta de skills do host. Se uma skill não estiver exposta, peça ao usuário que selecione ou habilite essa skill exata (ou siga o Guia de Instalação do CopyOS) e retome as checagens restantes. Não a pule em silêncio nem a substitua por conteúdo de repositório.
3. **Confira os recursos.** Abra `INVENTARIO-DE-RECURSOS.json` dentro de `biblioteca-dos-mestres`. As listas `requiredSkills`, `skillFiles` e `files` dele definem os arquivos esperados. Confira que cada arquivo listado abre, resolvendo as referências de cada skill pela localização real de recurso daquela skill. Verifique que os 14 volumes do Biblioteca dos Mestres estão acessíveis e leia as instruções de uso da biblioteca. A checagem é de acesso: use uma passada de acesso a arquivo/ferramenta onde disponível; não despeje bibliotecas inteiras na conversa.
4. **Tarefa de treino (opcional).** Se o usuário pedir, rode a tarefa de treino do caderno recarregável de `references/testes-de-instalacao.md`, invocando o controlador `copy-de-conversao` pela ferramenta de skill instalada e abrindo os recursos necessários dele. Rotule claramente as entradas de treino como fictícias. Devolva a saída real do treino e as revisões obrigatórias dela. Audite a saída final contra os fatos do treino, incluindo qualquer alegação ou recomendação nova. Corrija as falhas e rode de novo as revisões aplicáveis; não chame de aprovada uma saída que falhou só porque os arquivos dela carregaram. Ler ou descrever o contrato do primeiro trabalho sem rodar a tarefa de treino não conta como treino. Se a referência de treino estiver faltando, reporte a instalação como incompleta e pare. Esta é uma pequena checagem de fluxo de trabalho, não a entrevista completa do negócio nem um trabalho real de cliente concluído. Se uma tarefa dependente de execução não puder rodar neste host, marque essa capacidade como bloqueada e dê o próximo passo suportado.
5. **Reporte de forma estreita.** Três partes: o que passou, o que está bloqueado e o próximo passo. Inclua o host, as skills e os recursos checados, e a saída do treino quando ele rodou. "Pronto para a entrevista" exige que as 9 skills abram e que os arquivos obrigatórios do inventário estejam acessíveis; arquivos obrigatórios inacessíveis são reprovação. Se o treino não foi rodado, diga isso; não o dê como aprovado. Nenhuma publicação ao vivo, envio, pagamento, submissão de evento de rastreamento ou alteração de conta é teste de instalação. Verificação não autoriza substituir arquivos. Para um arquivo faltante ou alterado, nomeie o arquivo exato a reinstalar e preserve os arquivos próprios do usuário.

## Entrevista fundacional completa

Leia references/entrevista-completa.md e references/roteiro-da-entrevista.md. Use references/02-CONTRATO-DE-SAIDA.md e references/03-DIAGNOSTICO-DE-RESTRICAO.md para os artefatos finais; references/04-ESCOPO-DO-COPYOS.md é dono do escopo. A união deles é a fundação obrigatória. Pergunte em tom de conversa, uma pergunta ou um grupo estreitamente relacionado por vez. Adapte a linguagem ao negócio sem descartar campos relevantes. Não imponha limite de tempo nem encurte a entrevista para o onboarding parecer rápido.

Para cada campo registre: resposta, fonte, data de confirmação e status (confirmado, desconhecido, precisa de confirmação, ou não aplicável com motivo). Briefs existentes e qualquer material existente do negócio podem pré-preencher campos, mas o usuário os confirma. Inferências de pesquisa nunca são promovidas a fatos confirmados do negócio.

Preserve todo campo substantivo das duas referências de entrevista. Faça perguntas de acompanhamento quando uma resposta mudar a oferta, o comprador, a economia, as restrições ou o próximo trabalho. Um número faltante fica como desconhecido, não como zero. Um fato obrigatório não resolvido permanece uma lacuna explícita; não marque a entrevista como completa só porque o usuário quer pulá-la.

Quando todas as perguntas aplicáveis tiverem sido tratadas, mostre o resumo factual e a lista de lacunas. Peça ao usuário que aprove ou corrija. Salve BUSINESS-MEMORY.md e um Cartão de Restrição apenas neste projeto do negócio, ou devolva-os como arquivos para download quando o host não puder gravar arquivos persistentes de projeto. Seja explícito quando um chat novo exigir que esses arquivos sejam anexados de novo. Nunca prometa memória que o host não consegue persistir.

Use o brief confirmado para alimentar as outras skills do CopyOS (por exemplo, o pacote do negócio de voz-do-cliente e a memória de memoria-e-checagem). Pergunte só o que for suplementar e específico da skill. Não crie cópias concorrentes da verdade do negócio; registre a derivação e atualize quando o brief aprovado mudar.

## Primeiro trabalho útil

Pergunte o que o usuário precisa publicar ou decidir agora. Uma oferta definida não precisa ser reconstruída antes que o CopyOS possa escrever. Roteie dentro do escopo do CopyOS (references/04-ESCOPO-DO-COPYOS.md) e do controlador copy-de-conversao. Preserve todo módulo, revisão, checagem de fonte, artefato de saída e checagem de liberação obrigatórios. Esta skill é uma camada de entrada e continuidade, não um substituto do controlador.

O CopyOS escreve e revisa copy: anúncios, roteiros de anúncio, páginas de vendas e de captura, e-mails e sequências, e peças parecidas. Layout, criativo e imagem, compra de mídia, operação de plataforma de e-mail, publicação e gestão de conta de anúncios ficam fora dele: entregue a copy revisada e os briefs para quem executa essas etapas. Recomendações não são autorização para publicar, enviar, gastar ou alterar contas.

## Pausar e retornar

Salve um checkpoint curto no projeto do usuário: negócio, versão do brief aprovado, perguntas respondidas, perguntas não resolvidas, artefatos concluídos e a próxima ação exata. Ao retornar, carregue-o e continue. Nunca refaça trabalho concluído sem um motivo material. Mantenha separados a conclusão da entrevista, a primeira saída revisada e o uso no mundo real. Concluir uma etapa não é evidência de receita, implantação ou campanha bem-sucedida.
