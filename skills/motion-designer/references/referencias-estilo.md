# Referência de estilo

O que mais muda o resultado (tutorial "Insane Motion Graphics With Opus 5.5", Lukas Margerie): sem
referência, sai "texto centralizado com degradê". Com referência dissecada, sai no nível da referência.

## Como oferecer opções

- 3 caminhos diferentes, com link clicável e uma frase cada: claro/limpo, contrastado/colorido,
  escuro/premium. Abrir os 3 no Chrome do usuário em abas novas.
- Antes de oferecer, ver cada candidato quadro a quadro (`scripts/quadros_referencia.py <url>`).
- Busca rápida de candidatos no YouTube:
  `yt-dlp --flat-playlist --print "%(title)s | %(channel)s | %(duration)s | %(view_count)s | https://youtu.be/%(id)s" "ytsearch6:<termos>"`
  (ex.: "SaaS product launch video motion graphics UI animation", "app promo video motion design").
- Acervos de vídeos feitos com IA + o pedido usado: GitHub `athemeroy/awesome-opus-5-5-videos` e
  `yihui-dev/awesome-opus5-5-videos`.
- Referências já usadas: LangEase (claro, azul, UI 3D) https://www.youtube.com/watch?v=SgmuplXU2iY ·
  Numtera (degradê azul, vidro) https://www.youtube.com/watch?v=awUYikrGsKk · Raycast (escuro premium)
  https://www.youtube.com/watch?v=Mi173xGb0ZA.

## Dissecar a referência escolhida

`python scripts/quadros_referencia.py <url-ou-arquivo> --saida <pasta>` → quadros a cada 0,5 s com o tempo
gravado + folhas 6×6. Anotar:

- paleta (fundo, texto, destaque) e fonte (peso, tamanho, caixa alta ou não);
- tempo médio de cada cena e ritmo dos cortes;
- como o texto entra e sai (palavra a palavra, desfoque, máquina de escrever, deslize);
- transições (zoom através, whoosh com desfoque, giro 3D, wipe líquido);
- câmera (inclinação, parallax, flutuação);
- elementos recorrentes (cursor clicando, cards com contorno, barra de progresso, confete);
- fechamento (logo, chamada).

Copiar a gramática, nunca o conteúdo, o logo ou os personagens da referência.
