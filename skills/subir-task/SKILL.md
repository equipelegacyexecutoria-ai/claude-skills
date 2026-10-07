---
name: subir-task
description: Sobe brutos de reels para o time editar — ouve cada vídeo, descobre qual roteiro é de qual, renomeia na nomenclatura de reels (Reels_Clailton_TD_/NV_/ES_..., Reels_0800_CX_...), copia para a pasta BRUTO do mês no Google Drive, cria um card por vídeo no Notion (Calendário Editorial | Legacy, visão Audiovisual) com o roteiro no corpo, o link do bruto, observações para o editor e as datas distribuídas na agenda do editor (um por dia útil, nunca no fim de semana). Use sempre que o usuário pedir "sobe a task", "sobe esses vídeos pro Alex/Mac/Igor editar", "renomeia e sobe no drive", "cria os cards desses brutos", "distribui na agenda do editor", ou mandar uma pasta de brutos junto com roteiros para virarem tasks. Não edita o vídeo (isso é a fila-de-render e as skills de reels).
---

# Subir task (brutos → Drive → card no Notion)

O usuário não é técnico: relatório curto, pelo dia a dia dele (ver CLAUDE.md global).
Ele confere tudo depois; não pare no meio para pedir aprovação, só para dúvidas que mudam o resultado.

## O que o usuário manda

- A pasta com os brutos (normalmente a pasta aberta na conversa, ex.: `E:\ORGÂNICO\10 - Outubro\Reels\BRUTOS\<pasta>`).
- Os roteiros colados (separados por linhas `----`). A ordem dos roteiros **não** é a ordem dos vídeos.
- O formato (TD = tela dividida, NV = novela, ES = edição simples, CX = caixinha da Executoria 0800).
  Sem formato dito: pergunte.
- O editor (Alex, Mac, Igor, Lucas, Paim, Santini ou Claude) e, às vezes, o dia de começo
  ("ele não tem mais TD a partir do dia 13"). Sem editor dito: pergunte.

## Passo 1 — ouvir os vídeos e casar com os roteiros

Rode em segundo plano (demora ~1 min por vídeo na CPU):
```
P="$LOCALAPPDATA/reels-novela/venv/Scripts/python.exe"; [ -x "$P" ] || P="$LOCALAPPDATA/corte-viral/venv/Scripts/python.exe"
PYTHONIOENCODING=utf-8 "$P" ~/.claude/skills/subir-task/scripts/ouvir_brutos.py "<pasta dos brutos>"
```
Sai o começo (75 s) e o fim (50 s) de cada vídeo, com o tempo de cada frase.
- Case cada vídeo com o roteiro pelo gancho (primeiras frases). Vídeo sem roteiro ou roteiro sem
  vídeo: pergunte ao usuário antes de seguir.
- Anote para o editor (vira o campo IDEIA): conversa de set no começo ("até ~0:05"), frases
  regravadas ("volta um pouquinho" → "usar sempre a última tomada de cada trecho"), trecho de
  conversa no meio, e o **CTA gravado** com o tempo e o texto falado — principalmente quando
  ele é diferente do roteiro. Se o Whisper repetir a mesma frase várias vezes seguidas, é falha
  da transcrição, não do vídeo: ignore.

## Passo 2 — renomear (nomenclatura de reels)

`Reels_Clailton_<FMT>_<Título>.<extensão original>` — ex.: `Reels_Clailton_TD_O_Cliente_Que_Menos_Paga.MP4`.
- Título curto (3 a 7 palavras) tirado do gancho, cada palavra com inicial maiúscula, separadas
  por `_`, com acentos, sem pontuação; número em algarismo (`Os_3_Trabalhos_Do_Dono`).
- Outros perfis: Executoria 0800 → `Reels_0800_CX_<Título>`; case de cliente → `Reels_Case_<Título>`.
- Confira que o nome ainda não existe no Notion (busca na PAUTA) nem na pasta BRUTO do mês.
- Renomeie na própria pasta (`Rename-Item`) e mostre a lista antigo → novo no relatório.

## Passo 3 — subir no Drive (pasta BRUTO do mês atual)

Destino: `G:\Meu Drive\02. Captação de Vídeos\<AAAA>\<MM - Mês>\ORGÂNICO\BRUTO\<AAAA_MM_DD>_Reels_Clailton\`
(data de hoje; meses `01 - Janeiro` ... `10 - Outubro` ... `12 - Dezembro`; perfil 0800 →
`<AAAA_MM_DD>_Reels_0800`). Se o mês não existir, procure uma variação antes de criar.
- Confira o espaço livre do G: (o Drive para computador guarda cópia local até subir).
- Copie em segundo plano: `robocopy "<pasta>" "<destino>" "Reels_*" /J /R:3 /W:10 /NP`
  (código de saída 0–7 = deu certo; 1 = copiou). Sem disco G: neste PC: peça ao usuário para
  arrastar os vídeos para a pasta BRUTO do mês no Drive e siga com os cards.
- Enquanto o Drive sobe (vários GB levam minutos), crie os cards (Passo 4) sem o link.
- Para pegar os links: `search_files` com `title = '<AAAA_MM_DD>_Reels_Clailton'` (ID da pasta) e
  depois `parentId = '<ID da pasta>'`. Só considere pronto quando todos os arquivos aparecerem com o
  `fileSize` igual ao do disco. Vazio = ainda subindo: espere com um `Start-Sleep 240` em segundo
  plano e procure de novo (nada de espera longa em primeiro plano).
- Link no card: `https://drive.google.com/file/d/<ID>/view?usp=sharing`.

## Passo 4 — cards no Notion

Fonte: `collection://f0cc9747-efab-822b-8678-07f92372d6b7` (base "DEMANDAS | TIME DE CRIAÇÃO",
visão Audiovisual). Busque o esquema (`notion-fetch` na fonte) e use os nomes exatos.

**Agenda do editor (DATA D/ CONCLUSÃO)** — regra do usuário (07/10/2026):
- Um vídeo do formato por **dia útil** (segunda a sexta). **Nunca sábado nem domingo.**
- Começa no dia útil seguinte ao último card do mesmo formato que o editor já tem (ou no dia que
  o usuário disser). Para achar o último:
  ```sql
  SELECT PAUTA, ANDAMENTO, "date:DATA D/ CONCLUSÃO:start" AS conc, "date:DATA D/ PUBLICACÃO:start" AS pub
  FROM "collection://f0cc9747-efab-822b-8678-07f92372d6b7"
  WHERE "RESPONSÁVEL" = ? AND PAUTA LIKE ? AND ANDAMENTO NOT IN ('Publicado','Finalizado')
  ORDER BY conc
  ```
  (params: editor e `%\_TD\_%` / `%\_NV\_%`...; olhe também os sem filtro de ANDAMENTO dos
  últimos dias, para não colidir com o que acabou de ser entregue.)
- Ordem dos vídeos: a ordem dos arquivos (gravação), salvo pedido do usuário.

**Publicação (DATA D/ PUBLICACÃO)**: continue a fila do mesmo perfil e formato depois da última
publicação já marcada, um por dia, às 13h de Brasília (`T16:00:00.000Z`, `is_datetime` 1),
qualquer dia da semana, sempre pelo menos 2 dias depois da conclusão. É sugestão: diga no relatório.

**Campos de cada card** (`notion-create-pages`, `parent` = `data_source_id`, `allow_async` false, ícone 📹):

| Campo | Valor |
| --- | --- |
| PAUTA | o novo nome sem extensão |
| ANDAMENTO | `A Editar` (editor Claude: `CLAUDE (Editor)`, aí ele entra na fila-de-render) |
| RESPONSÁVEL | o editor (`Alex`...; Claude = `🤖 CLAUDE`) |
| FORMATO | `["📹 Reels (Video Curto)"]` |
| PERFIL | `CLAILTON` (0800/Lucas: `LEGACY`; confira com o usuário se não for óbvio) |
| REDE SOCIAL | `["Instagram / Facebook"]` |
| DATA D/ CONCLUSÃO | dia útil da agenda (`is_datetime` 0) |
| DATA D/ PUBLICACÃO | ver acima |
| IDEIA | as observações do Passo 1 (tomadas, conversa de set, CTA gravado) |
| MATERIAL NECESSÁRIO | o link do Drive (quando o upload terminar: `notion-update-page`, `update_properties`) |
| corpo | `## Roteiro` + o roteiro **exatamente como o usuário colou** (sem corrigir nem resumir) |

Depois de pôr os links, faça `notion-fetch` em um card e confira link, datas e roteiro.

## Relatório final

1. Tabela: vídeo original → novo nome → entrega do editor → publicação.
2. Onde ficou no Drive (caminho em palavras) e que os cards estão em "A Editar" com o editor.
3. Pontos para conferir: datas de publicação sugeridas, CTA gravado diferente do roteiro,
   vídeo que ficou com dúvida.

## Cuidados

- Nunca apague bruto (nem no disco, nem no Drive) e nunca mexa em cards que já existiam.
- Não mude a agenda de outros cards para encaixar os novos; se não couber, pergunte.
