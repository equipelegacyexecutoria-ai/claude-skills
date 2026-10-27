# Capa dos cards do MURAL (Notion)

Padrão das capas de Grade de conteúdos, Bibliografia perfil Legacy, Pesquisa perfil dos clientes, Ads que
funcionam e Capas que funcionam: 1538x433, grade escura, logo Legacy, título Bebas branco (linha 1) + azul
#2744CB (linha 2), subtítulo cinza Poppins em 2 linhas e dois destaques à direita com barra azul.

Uso: `capa_mural.capa("ADS QUE", "FUNCIONAM", "linha 1\nlinha 2", [("19 ANÚNCIOS", "legenda"), ("R$ 0,28", "legenda")], "saida")`
gera `saida_capa.png` (capa da página, 1538x433) e `saida_card.png` (701x430, recorte da esquerda).
Poppins precisa estar instalada no Windows.

Versão aprovada em 27/10/2026, depois de o usuário reprovar a 1ª ("textos em cima da logo, sem harmonia"):
margem 70, logo separado do título por 30 px, bloco centralizado na altura, título no maior tamanho que cabe
no recorte (até 124 px), espaço extra quando a 2ª linha tem acento, destaques alinhados pela base com o subtítulo.

Subir no card:
- **Capa externa** (o que aparece no quadro): o `_card.png` em MATERIAL FINALIZADO
  (notion-create-file-upload + `curl -F` rodado de dentro da pasta do arquivo, porque caminho com espaço quebra o `@`,
  + update_properties com `{"type":"file_upload","file_upload":{"id":...}}`).
- **Capa da página**: o conector só aceita link. Pelo Chrome: passar o mouse no topo → "Alterar" → aba
  "Carregar" → interceptar o input de arquivo por JavaScript (sobrescrever `HTMLInputElement.prototype.click`
  e clicar em "Carregar arquivo") e usar o upload de arquivo da extensão. O arquivo precisa estar numa pasta
  da sessão (ex.: Desktop\RENDER\Capas Notion).
