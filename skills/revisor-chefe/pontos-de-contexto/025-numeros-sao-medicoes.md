---
id: 025
slug: numbers-are-measurements
title: Números são medições - toda contagem tem um artefato de origem e pode ser remedida agora
status: active
weight: high
date_added: 2026-09-01
source: desvio de especificação capturado ao vivo: uma contagem de componentes três versões defasada, e duas durações de vídeo escritas de memória que estavam ambas erradas; todas eram verdadeiras quando escritas pela primeira vez
tags: [truth, counts, spec-drift, maintenance]
---

# 025 - Números são medições

## Princípio
Este ponto é um hábito que vale manter, não uma checagem. Uma contagem na copy é uma alegação sobre um artefato em um momento no tempo. Medições têm fonte e data; um número carregado de uma versão anterior é uma memória vestindo a roupa de uma alegação. O chefe anota o número defasado; `checagem-de-alegacoes` e `checagem-pre-lancamento` decidem o que isso significa para a versão.

## Por que funciona
Nada decai mais rápido que uma especificação. Produtos são reembalados, mídia é regravada, bibliotecas crescem, e a copy que foi verificada uma vez apodrece em silêncio até virar uma mentira que ninguém escolheu contar. Um comprador que pega um número defasado para de confiar em todos os outros números da página, então o hábito mais barato desta biblioteca é também o que protege todos os outros.

## As regras (checáveis)
1. Todo número nomeia o artefato do qual é medido (um diretório, um manifesto, um arquivo de mídia, uma API).
2. Remeça antes de publicar. Uma duração é uma consulta; uma contagem de arquivos é uma listagem de diretório.
3. A mudança que altera o artefato deve mudar a copy junto. Quando não mudou, isso é uma nota para a guarda e para a checagem pré-lançamento, não um REVISAR de ofício: uma contagem defasada vale a captura, e a decisão de versão pertence às passadas que são donas dela.
4. Durações de mídia linkada são checadas contra a mídia, nunca contra a memória.

## Teste de aprovação
- [ ] Você consegue rederivar todo número do canal em menos de um minuto.
- [ ] Nenhuma contagem é anterior à última reembalagem do artefato, ou as que são estão nomeadas nos sinais.

## Modos de falha
- Uma contagem carregada da versão anterior.
- Uma duração escrita de memória.
- Uma especificação que era verdadeira no lançamento e que não é trabalho de ninguém rechecar.
