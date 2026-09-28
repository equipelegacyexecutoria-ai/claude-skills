# Adaptar o viral de outro player

Regra de ouro (do molde da equipe): **a referência empresta estrutura, nunca conteúdo.** Aproveite o mecanismo (tipo de hook, ressalva, espinha, tipo de âncora, virada, fecho). Descarte as frases, os tiques e o que só funciona para aquele criador. Nenhuma sequência de 8 ou mais palavras da referência pode aparecer no roteiro final (o lint confere com `-Referencia`).

## 1. Obter a fala (nunca adivinhar)

Ordem de preferência:
1. **Transcrição colada pelo usuário.**
2. **Export do JARVIS** (`Desktop\PROJETOS ANTIGRAVIDADE\JARVIS EXTRATOR DE PERFIS`): o extrator de perfil baixa e transcreve os vídeos (CSV com `;` e coluna `transcricao`, ou .docx com blocos "Transcrição"). O módulo "Vídeos virais" do JARVIS cobre TikTok. Use `scripts/importar-mes.ps1 -Entrada <arquivo> -Etapa normalizar` para ler o arquivo.
3. **Link, pelo navegador** (roteiro técnico abaixo): legenda do post, métricas públicas, duração, 1º frame e frames amostrados. Se o vídeo tem legenda queimada, a fala pode ser reconstruída lendo os frames em sequência; marque como "reconstruída pelos frames, pode ter lacunas".
4. Sem fala legível: **pare e peça** a transcrição ou o export do JARVIS ao usuário. Não siga com fala inventada.

YouTube: a descrição tem "Mostrar transcrição". TikTok costuma bloquear navegador sem login: peça o export do JARVIS ou a transcrição.

### Roteiro técnico para Instagram (navegador do Claude)

1. Abra `https://www.instagram.com/reel/<código>/embed/` com `preview_start` (url) ou `navigate`.
2. Rode no `javascript_tool` (mesma origem, sem login):
   ```js
   const r = await fetch('/reel/<código>/embed/'); const t = await r.text();
   const m = t.match(/"contextJSON":("(?:[^"\\]|\\.)*")/);
   const ctx = JSON.parse(JSON.parse(m[1])); const sm = ctx.gql_data.shortcode_media;
   ({ poster: sm.display_url, video: sm.video_url || null, duracao: sm.video_duration,
      views: sm.video_view_count, curtidas: sm.edge_liked_by && sm.edge_liked_by.count,
      comentarios: sm.edge_media_to_comment && sm.edge_media_to_comment.count,
      legenda: sm.edge_media_to_caption && sm.edge_media_to_caption.edges[0] && sm.edge_media_to_caption.edges[0].node.text,
      audio: sm.clips_music_attribution_info, bloqueado: ctx.context.copyright_blocked })
   ```
3. Folha de contato de frames: com `resize_window` em 540x1100 (a página vira ~980 px de largura lógica), crie um overlay fixo e desenhe frames do vídeo em canvases (desenhar vídeo de outra origem num canvas funciona para exibir; só a leitura de pixels é bloqueada):
   ```js
   const v = document.createElement('video'); v.muted = true; v.src = '<video_url>';
   await new Promise(ok => { v.onloadedmetadata = ok; setTimeout(ok, 15000); });
   const ov = document.createElement('div'); ov.style.cssText = 'position:fixed;inset:0;background:#fff;z-index:2147483647;display:flex;flex-wrap:wrap;gap:3px';
   document.body.appendChild(ov);
   for (const f of [0.02,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]) {
     v.currentTime = v.duration * f; await new Promise(ok => { v.onseeked = ok; setTimeout(ok, 8000); });
     const c = document.createElement('canvas'); c.width = 180; c.height = 320;
     c.getContext('2d').drawImage(v, 0, 0, 180, 320); ov.appendChild(c);
   }
   ```
   Depois tire `screenshot`. Para ler legenda queimada, amostre a cada ~1,5 s em folhas de 12 a 16 frames.
4. Se `bloqueado` (música licenciada, sem `video_url`): abra `https://www.instagram.com/reel/<código>/` (a página toca o vídeo em blob) e faça o mesmo com `document.querySelector('video')`.
5. Volte o viewport com `resize_window` preset `desktop` ao terminar.

## 2. Dissecar (`00-referencia.md`)

```
# Referência · @<perfil> · <link>
Métricas públicas: views <n> · curtidas <n> · comentários <n> · duração <s> · data <d> · áudio <original|música>
Formato visual: <16:9 com barras (tipo novela) | vertical com imagens (tipo tela dividida) | talking head puro | outro> · 1º frame: <descrição>
Fonte da fala: <colada | JARVIS | reconstruída pelos frames (lacunas?)>

## Fala
<transcrição>

## Dissecação pelas 7 camadas
Hook: "<frase>" · tipo (taxonomia de hooks.md): <tipo> · por que para o scroll: <...>
Ressalva: <...> · Espinha (oposição): <A x B> · Desenvolvimento: <cena/história/número/lista> · âncoras visuais: <...>
Virada: <...> · Fecho: <frase e formato> · CTA: <...>

## Mecanismo do viral
<por que espalhou: identidade, recado, utilidade, polêmica, emoção, curiosidade; o que a pessoa faz ao ver (manda, salva, comenta, reposta)>

## Transferível x não transferível
Transferível: <estrutura, fórmula do hook, tipo de âncora, ritmo, tipo de fecho>
Não transferível: <tema específico, persona, bordões e tiques do criador, contexto de plataforma, dados que não se aplicam ao Brasil>

## Adaptação sugerida para o Clailton
Formato recomendado: <NOVELA|TELA DIVIDIDA> (pode ser diferente do original) · motivo
Ponte para o empresário: <...> · Riscos: <direitos de imagem, fatos, política>
```

## 3. Adaptar

1. Separe **conteúdo** (ideia, argumentos, caso, dados) de **forma** (frases, bordões, tiques). A forma do outro se descarta.
2. Escolha o formato do Clailton pela árvore de `pauta-matriz.md`. Um talking head de outro player pode virar novela (se a força é a tese) ou tela dividida (se a força é o caso).
3. Remonte no esqueleto do formato, com a digital de `voz-clailton.md`. A ponte pessoal só usa o banco de biografia real.
4. Troque o desfecho quando necessário: referências gringas e de "coach" costumam fechar em esforço, fé ou disciplina ("levante e ande", "faça 100 vezes"). O Clailton fecha em estrutura, decisão ou consequência concreta.
5. Dados da referência (estudos gringos, números de outro país) só entram com fonte e, se possível, equivalente brasileiro (Sebrae, IBGE, Serasa).
6. Rode o lint com `-Referencia <arquivo da referência>` para garantir que nenhuma frase foi copiada.
