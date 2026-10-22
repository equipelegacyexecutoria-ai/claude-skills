# Grade semanal de conteúdo (Legacy, Clailton e Comunidade)

**A fonte é a grade de dentro do Cérebro** (pedido do Igor, 22/10/2026): janela **Posts › Grade de conteúdos** do site
(https://cerebro-legacy-organico.vercel.app/#posts/grade), guardada no banco do Cérebro na tabela `cerebro_grade`
(migração 0013; formato em `api/_grade.js` do projeto cerebro-legacy). O card 📌 GRADE DE CONTEÚDOS do Notion e a página
antiga do Mac **não valem mais** como fonte.

Antes de responder qualquer coisa sobre a grade (o que sai em tal horário, se um post saiu no horário da grade, o que está
em teste), **leia a tabela** e use o que vier de lá; o resto deste arquivo é só a foto de 22/10/2026 e pode estar velho:

```sql
select dados, resumo, atualizado_em, atualizado_por from public.cerebro_grade where id = 'atual';
-- histórico (cada mudança guarda a versão anterior):
select resumo, valia_desde, guardada_em from public.cerebro_grade_versoes order by id desc limit 10;
```

Quem muda a grade: os gestores, pelo **Editor da Grade** (https://claude.ai/artifact/Tjxs8R1ZiL3oqHJZvxv1r1, botão
"Editar grade" na janela): a grade atual em cima, a mudança escrita num chat embaixo, prévia do que muda antes de salvar.
Grava pelo Supabase do aplicativo do Claude no PC (o conector Supabase Cérebro do claude.ai só lê).
Quando a grade mudar, este arquivo não precisa ser reescrito: a tabela é a verdade. Atualize só se a mudança for grande
(ex.: um perfil novo) e diga a data.

Ligado a `testes-e-aprendizados-perfis.md` (o que é teste) e `estilos-e-formatos.md` (NV, TD, B-roll, Do topo à falência...).

## Foto de 22/10/2026 (a carga inicial da tabela, conferida pelo Igor)

### Perfis do Instagram

#### @clailtonluiz: 4 posts todo dia (os 7 dias)

| Horário | O quê | Formato |
|---|---|---|
| 09h | Novela (às vezes vira B-roll, em teste) | Reels |
| 13h | Tela dividida | Reels |
| 18h | Novela | Reels |
| 20h | Carrossel Twitter (o único carrossel do Clailton) | Carrossel |

#### @legacyexecutoria

| Horário | Seg | Ter | Qua | Qui | Sex | Sáb | Dom |
|---|---|---|---|---|---|---|---|
| 09h30 (extra, em teste) | Mudança do consumidor (carrossel) | Verdades duras, estilo Twitter (carrossel) | Mudança do consumidor | Verdades duras | Mudança do consumidor | — | — |
| 12h | Notícia (estático) | Notícia | Notícia | Notícia | Notícia | Antecipação da LIVE de segunda (estático) | Notícia |
| 16h | Do topo à falência (carrossel) | Análise de cenário (carrossel) | Do topo à falência | Análise de cenário | Do topo à falência | Do topo à falência | Do topo à falência |
| 17h | Corte / vídeo de conteúdo (reels) | — | Corte | — | Corte | — | Corte |
| 18h | Conteúdo técnico, colab Legacy + Clailton (carrossel) | Conteúdo técnico | Conteúdo técnico | Conteúdo técnico | Conteúdo técnico | Conteúdo técnico | Conteúdo técnico |

- Por dia: seg, qua e sex 5 posts; ter e qui 4; sáb 3; dom 4. Total da Legacy na semana: 30 posts.
- Na semana: Notícia 6×, Conteúdo técnico (colab) 7×, Do topo à falência 5×, Corte 4×, Mudança do consumidor 3×,
  Análise de cenário 2×, Verdades duras 2×, Antecipação da LIVE 1×.
- O sábado é o dia da antecipação da LIVE de segunda (12h, estático branco na página).

### Comunidade (gratuita, no Discord; quem conduz é o Lucas)

| Horário | Seg | Ter | Qua | Qui | Sex | Sáb e dom |
|---|---|---|---|---|---|---|
| 12h | Gestão e Processos (Legado) | Financeiro (Impulsão) | Vendas (Impulsão) | Tema da live + Hotseat (Método) | Números da Semana (Execução) | Estímulo de conversa (leve) |
| 18h | Diário Legacy (notícias) + áudio de análise | igual | igual | igual | igual | — |

- Assunto de cada pilar: Gestão = time, delegação, saída do operacional; Financeiro = controle financeiro, margem, fluxo
  de caixa; Vendas = processo comercial, fechamento, funil; Quinta = caso real ao vivo, qualquer pilar do método;
  Sexta = indicadores e leitura de DRE, cobrança de execução.
- Em dia variável: o Lucas pega um post da Legacy que performou bem e traz uma análise "traduzida" para os membros
  aplicarem no próprio negócio.

### Grade de teste (desde 13/10)

Nos horários abaixo o formato alterna entre as duas opções:

| Horário | Teste | Perfil |
|---|---|---|
| 09h30 seg, qua, sex | Mudança do consumidor (impacto para o empresário) | Legacy, conteúdo extra |
| 09h30 ter, qui | Verdades duras, estilo Twitter | Legacy, conteúdo extra |
| 16h | Cenário (Brasil) ou Do topo à falência | Legacy |
| 18h | Cenário ou Tela dividida | Legacy |
| 20h | Carrossel Twitter: o único carrossel do Clailton | Clailton |

Regras do teste: carrosséis da Legacy às 09h30 (seg a sex), 16h e 18h; carrosséis do Clailton só o Twitter, às 20h.

### O que mudou em relação à grade anterior

- Clailton: a grade de 05/10 era 10h30 B-roll · 13h tela dividida · 18h novela · carrossel de roteiro antigo no fim do
  dia. Agora é 09h novela (B-roll só às vezes) · 13h TD · 18h novela · 20h carrossel Twitter.
- Legacy: entrou o horário extra das 09h30 (em teste desde 13/10).

## Informação que não bate

- 18h da Legacy: a aba de testes diz "Cenário ou Tela dividida" (alternando), mas o quadro principal mostra "Conteúdo
  técnico, colab Legacy + Clailton" todo dia. O Igor confirmou a página como está em 22/10; se a pergunta depender do que
  sai às 18h, avise que as duas abas divergem.
