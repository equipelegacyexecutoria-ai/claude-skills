---
id: 020
slug: the-site-is-the-asset
title: O site é a peça - audite entre páginas, nunca página por página
status: active
weight: high
date_added: 2026-09-01
source: um incidente real, 2026-08: um comprador chamou publicamente um site de lixo de IA; a causa raiz eram strings clonadas em seis páginas enquanto cada página passava na própria revisão
tags: [structure, dedup, site, house-style]
---

# 020 - O site é a peça

## Princípio
Um comprador lê páginas em sequência, então a unidade de revisão é o site, não a página. Copy que é excelente em toda página e repetida em três delas soa como template na segunda vez que é vista, e templates soam como saída de máquina. Uma frase tem exatamente uma casa.

## Por que funciona
A revisão por página não consegue ver a clonagem, e clonagem é como copy boa vira lixo genérico: cada página passa, o conjunto reprova. O caso real por trás desta regra: sete strings repetidas em até seis páginas públicas, cada página aprovada individualmente, e um cliente pagante chamou o resultado de lixo de IA em público. As frases estavam boas. A repetição era o defeito.

## As regras (checáveis)
1. **Antes de publicar qualquer página, varra toda OUTRA página voltada ao cliente em busca de frases compartilhadas.** Uma frase em duas páginas vai para uma delas ou morre.
2. **Nunca rascunhe uma página nova copiando a existente mais próxima.** Rascunhe a partir da função que esta página tem e do comprador que ela precisa convencer. Copiar uma página irmã é como o clone entra, todas as vezes.
3. **Procedimento pode se repetir; persuasão não.** Passos de instalação, rodapés jurídicos, linhas de licença e assinaturas DEVEM ser idênticos em toda parte; reformular instruções por variedade as torna piores. A regra governa argumentos, aberturas, ganchos e ofertas.
4. **Quando um bloco compartilhado é deliberado, registre.** Mantenha uma lista escrita de blocos compartilhados-por-design para que a próxima auditoria não os marque e o próximo escritor não os multiplique.
5. **Se der para automatizar a varredura, automatize.** Um teste simples que quebra o build quando uma frase de persuasão aparece em duas páginas supera qualquer revisão manual.

## Teste de aprovação
- [ ] Toda frase de persuasão nova ou alterada foi checada contra as outras páginas, não só a própria.
- [ ] Nenhum argumento, abertura ou linha de oferta existe em duas páginas voltadas ao cliente.
- [ ] Qualquer repetição deliberada está na lista registrada de compartilhados-por-design.

## Modos de falha
- Revisar a página nova isoladamente porque "as outras já foram publicadas".
- Consertar uma linha clonada reformulando-a levemente em cada página. Cinco paráfrases de um argumento ainda são um argumento, mais gasto.
- Tratar uma linha forte como reutilizável PORQUE é forte. Quanto mais forte a linha, mais custa a segunda vez que é vista.
