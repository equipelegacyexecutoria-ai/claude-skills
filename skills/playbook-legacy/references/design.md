# Identidade visual e manutenção do template

Esta referência não é necessária para escrever um playbook. Ela registra de onde vem o visual e como mudar o template sem quebrar o padrão.

## De onde vem
Todo o visual foi extraído de **legacyexecutoria.com.br** em 27/09/2026, e não do primeiro playbook do JEV Lab (aquele design não foi aprovado). Do JEV Lab veio só a estrutura e o jeito de escrever.

| Elemento do site | No playbook |
|---|---|
| Barra do topo azul-marinho `#011126` com o logo num recorte arredondado no centro | barra do topo igual, com "Playbook · Nome" à esquerda e os atalhos à direita |
| Hero claro, título grosso em azul-marinho e a frase-chave em MAIÚSCULAS, itálico e azul (`VIVER SEM MEDO`) | capa: "Playbook do" + o NOME em maiúsculas, itálico e azul `#4185f4` |
| Selo em pílula "• ACELERADORA DE GESTÃO & RESULTADOS" | selo "• PLAYBOOK · ÁREA" |
| Cartão de vidro com números (20K+ · 15+ · 1BI+) | cartão com passos · minutos de leitura · dúvidas respondidas (calculados sozinhos) |
| Faixa azul com frases em itálico e maiúsculas ("VIVA SEM MEDO • GESTÃO DE VERDADE") | faixa azul com 2 frases + "Atualizado em" |
| Etiqueta azul `#0099ff`, 12 px, peso 900, espaçada ("O DIAGNÓSTICO") + título peso 900 com palavra em MAIÚSCULAS azul | etiqueta e título de cada capítulo |
| Cartões cinza `#f2f2f2`, cantos de 32 px, ícone num quadrado azul de 48 px com brilho | cartões, "o caminho em N passos", boas práticas |
| Botões azuis `#4185f4`, cantos de 16 px, maiúsculas, peso 900, brilho azul | botões da capa, "copiar", voltar ao topo |
| FAQ em cartões brancos com a seta num círculo, que fica azul ao abrir | problemas comuns |
| Linha divisória com degradê azul no centro | separação entre capítulos |
| Rodapé `#f8f9fa` com o logo na versão escura | rodapé |

Logos e favicon são os arquivos oficiais do site (`/images/logo-legacy.svg`, `/images/Logo-Legacy-preta.svg` e `/favicon.svg`), embutidos no template. A marca tem o degradê `#4273BD → #609CF6`; o texto do logo é branco no fundo escuro e `#000066` no claro.

## Tokens
- Cores: azul-marinho `#011126` · texto de título `#0a1a2e` · texto `#4d5867` · apagado `#6c7682` · azul da marca `#0099ff` · azul dos botões `#4185f4` · azul de link `#006fd6` · azul-claro `#609cf6` · fundo claro `#f8f9fa` · cartão `#f2f2f2`.
- Cores de aviso (só nos avisos): dica `#16a34a` · bom saber `#0099ff` · atenção `#f59e0b` · cuidado `#e11d48`.
- Fonte: a do sistema (`ui-sans-serif, system-ui…`), a mesma que o site mostra de fato (Segoe UI no Windows, SF Pro no Mac). Sem fonte da internet, o arquivo abre igual sem conexão.
- Pesos: capa 700; títulos, etiquetas, botões e números 900; texto 400/500.
- Espaçamento das letras: títulos -0,04em; etiquetas +0,4em.
- Tema só claro (como o site). A impressão tem folha própria e abre as respostas antes de imprimir.

## Como mudar o template
1. Uma mudança no `assets/template.html` vale para **todos** os playbooks: faça só com o ok do usuário.
2. Mude CSS e JS só no template. Se criar um componente novo, inclua a classe em `CLASSES` (e a tag em `TAGS`, se for o caso) no `scripts/verificar.mjs` e documente em `references/componentes.md`.
3. Atualize a versão no comentário do topo do template (`template v1` → `v2`).
4. Rode o `montar.mjs` em cada playbook existente para aplicar o design novo: o conteúdo e as capturas são mantidos.
5. Confira um playbook em tela grande e no celular (390 px) antes de espalhar a mudança.
