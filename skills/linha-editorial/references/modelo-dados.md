# Formato do dados.json

Um arquivo só guarda a linha editorial inteira. O script `linha_editorial.py` lê esse arquivo, lista as
vagas (`vagas`) e gera o documento e a planilha (`montar`). Exemplo completo e válido:
`assets/exemplo-dados.json` (empresa fictícia). Copie a estrutura dele, não o conteúdo.

Campos marcados com * são obrigatórios. Datas em `AAAA-MM-DD` (ou `DD/MM/AAAA`), horas em `HH:MM`.
Dias da semana: `seg ter qua qui sex sab dom` (aceita "segunda", "Sábado" etc.).
Chaves que começam com `_` são ignoradas (use para anotações).

| Campo | Tipo | O que é |
|---|---|---|
| `empresa`* | `{nome*, segmento, cidade, site, instagram}` | Identificação |
| `cor_marca` | `"#RRGGBB"` | Cor da capa, títulos e cabeçalho da planilha (padrão azul) |
| `elaborado_por` | texto | Aparece na capa |
| `periodo`* | `{inicio*, semanas}` ou `{inicio*, fim}` | Período do calendário (padrão 4 semanas) |
| `segmentos` | lista | Quais datas especiais entram: `varejo alimentacao saude beleza educacao negocios marketing juridico imobiliario construcao tecnologia pet financas` (ou `todos`). `geral` entra sempre |
| `nao_postar` | lista de datas | Dias sem post (feriado, recesso) |
| `resumo` | texto | 2 a 3 frases sobre a estratégia |
| `missao_editorial`* | texto | "A [empresa] é onde [público] encontra [conteúdo] para [benefício]." |
| `diferencial` | texto | Por que seguir esta marca e não outra (content tilt) |
| `nao_falamos` | lista | Temas fora da linha |
| `objetivos` | `[{objetivo, meta, prazo, metrica}]` | O primeiro é o principal |
| `publico`* | `{resumo, persona:{nome, descricao}, dores[], desejos[], objecoes[], perguntas[], onde_consome[]}` | Base dos temas |
| `tom_de_voz`* | `{resumo, dimensoes:{humor, formalidade, respeito, entusiasmo}, somos[], nao_somos[], usar[], evitar[], exemplos:[{errado, certo}]}` | Dimensões de 1 a 5: humor 1=engraçado 5=sério; formalidade 1=formal 5=descontraído; respeito 1=respeitoso 5=irreverente; entusiasmo 1=entusiasmado 5=direto ao ponto |
| `pilares`* | `[{nome*, percentual*, descricao, objetivo, funil, papel, formatos[], exemplos_temas[], cor}]` | 3 a 5; percentuais somam 100; `funil`: descoberta, consideracao, decisao, fidelizacao; `papel`: Help, Hub ou Hero |
| `cadencia` | `{help:{o_que, frequencia}, hub:{...}, hero:{...}}` | Ritmo Hero, Hub, Help |
| `estilos` | `[{nome, formato, objetivo, estrutura[], exemplo}]` | 6 a 10 estilos escolhidos do catálogo |
| `series` | `[{nome, formato, dia, pilar, descricao}]` | Quadros fixos |
| `canais` | `[{rede, papel, frequencia, horarios, formatos[]}]` | Uma linha por rede |
| `grade_semanal`* | `[{dia*, hora*, rede, formato, estilo, pilar, serie}]` | Semana padrão; o script repete pelo período |
| `nota_horarios` | texto | De onde vieram os horários e quando revisar |
| `stories` | `{frequencia, rotina:[{dia, horario, conteudo}], regras[]}` | Rotina de stories |
| `datas_empresa` | `[{data, nome, acao}]` | Lançamentos, eventos, aniversário |
| `pautas` | `[{data*, hora, rede, formato, estilo, pilar, funil, tema, gancho, cta, observacao, responsavel, status}]` | Um item por publicação do período. Sem pautas, o calendário sai só com as vagas |
| `operacao` | `{capacidade_semanal, fluxo:[{etapa, responsavel, prazo}], regras[]}` | Quem faz o quê |
| `regras` | lista | Cuidados legais e de marca |
| `metricas` | `[{objetivo, metrica, meta, onde_ver}]` | Como medir |
| `revisao` | lista | Rotina de revisão |
| `suposicoes` | lista | O que foi decidido sem resposta e precisa ser confirmado |

## Regras de preenchimento
- Toda pauta tem `tema` concreto (não "dica de saúde", e sim "3 sinais de que a gengiva precisa de
  atenção"), `gancho` (a primeira frase/tela, como será falada ou escrita) e `cta`.
- `pilar` da pauta precisa ser um dos nomes em `pilares`, escrito igual.
- A distribuição de pilares nas pautas fica até 10 pontos da meta.
- Data comercial do período que combina com a marca entra em alguma pauta (ou explicar por que não).
- Texto sem travessão (—) e sem as palavras de IA (crucial, fundamental, jornada, potencializar, além
  disso etc.): o script avisa.
