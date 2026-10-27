# Capa dos cards do MURAL (Notion)

Padrão das capas "Bibliografia perfil Legacy", "Pesquisa perfil dos clientes", "Ads que funcionam" e
"Capas que funcionam": 1538x433, grade escura, logo Legacy, título Bebas branco (linha 1) + azul #2744CB
(linha 2), subtítulo cinza Poppins em 2 linhas e dois destaques à direita com barra azul.

Uso: `capa_mural.capa("ADS QUE", "FUNCIONAM", "linha 1\nlinha 2", [("19 ANÚNCIOS", "legenda"), ("R$ 0,28", "legenda")], "saida.png")`
(Poppins precisa estar instalada no Windows). Se o primeiro destaque for largo, empurrar o segundo e recuar o
bloco para terminar até x ≈ 1465.

Subir no card: o conector do Notion só aceita capa por link. Pelo Chrome: "Adicionar capa" → "Alterar" →
aba "Carregar" → interceptar o input de arquivo por JavaScript e usar o upload de arquivo da extensão
(o arquivo precisa estar numa pasta da sessão, ex.: Desktop\RENDER\Capas Notion).
