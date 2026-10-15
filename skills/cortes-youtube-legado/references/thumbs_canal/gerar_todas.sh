#!/bin/bash
S=~/.claude/skills/cortes-youtube-legado/scripts/thumb_canal.py
P=/c/Users/IgorAmanciodeOliveir/AppData/Local/corte-viral/venv/Scripts/python.exe
R=/c/Render/_youtube/fotos_clailton/recortes
export PYTHONUTF8=1
t() { # aula ep var foto apoio golpe cor rodape
  local d=/c/Render/_youtube/legado_$1/thumbs_v3; mkdir -p $d
  local extra=(); [ -n "$8" ] && extra=(--rodape "$8")
  [ "$4" = "12" ] && extra+=(--cab-foto 520)   # braço levantado engana a medição da cabeça
  [ "$4" = "18" ] && extra+=(--x 1070 --cabeca 255)   # dedo apontando para o texto
  $P $S "$d/ep$2_$3.jpg" --pessoa "$R/$4.png" --apoio "$5" --golpe "$6" --cor "$7" "${extra[@]}" | sed "s#^#$1 #"
}
t t14_aula06 01 A 08 "VOCÊ ESTÁ JOGANDO" "PARA|VENCER?" azul
t t14_aula06 01 B 02 "ELE VENDEU ATÉ" "O CACHORRO" azul "POR UM SONHO"
t t14_aula06 02 A 03 "O SEU LUCRO É SÓ" "UM|SINTOMA" azul
t t14_aula06 02 B 18 "QUEM NÃO MEDE" "NÃO|GERENCIA" azul
t t14_aula06 03 A 01 "SEM PAINEL, SUA EMPRESA" "VAI CAIR" vermelho
t t14_aula06 03 B 06 "PARE DE" "PEDALAR" azul "A SUA EMPRESA"
t t14_aula06 04 A 05 "OS 15 OBJETIVOS QUE" "TODA|EMPRESA" azul "PRECISA TER"
t t14_aula06 04 B 10 "VOCÊ SABE O SEU" "ROAS?" azul
t t14_aula02 01 A 01 "PARE DE DECIDIR" "SÓ PELO|CAIXA" azul
t t14_aula02 01 B 04 "QUAL É O SEU" "PLANO PARA|2030?" azul
t t12_aula08 01 A 06 "SEU NEGÓCIO VIROU UMA" "PRISÃO|COM CNPJ" vermelho
t t12_aula08 01 B 07 "TOQUE SUA EMPRESA COMO" "FRANQUIA" azul
t t12_aula08 02 A 08 "PARE DE DAR" "DESCULPA" vermelho
t t12_aula08 02 B 09 "VOCÊ É TERMÔMETRO" "OU|TERMOSTATO?" azul
t t12_aula08 03 A 19 "10% DE DESCONTO" "NÃO É|PUV" vermelho
t t12_aula08 03 B 02 "O QUE FAZ O CLIENTE" "ESCOLHER|VOCÊ" azul
t t12_aula08 04 A 05 "A CULPA" "NÃO É DA|AGÊNCIA" azul
t t12_aula08 04 B 03 "QUANTO VOLTA DE" "CADA R\$ 1?" azul
t t12_aula01 01 A 01 "CONTRATEI UM GESTOR E" "QUEBREI" vermelho "A MINHA HISTÓRIA"
t t12_aula01 01 B 04 "OFICIAL DE JUSTIÇA" "NA MINHA|PORTA" azul
t t12_aula01 02 A 05 "PARE DE VENDER" "SÓ PÃO" azul
t t12_aula01 02 B 08 "SUA MISSÃO TE ENSINARAM" "ERRADO" vermelho
t t12_aula01 03 A 09 "SEM VISÃO DE FUTURO, SUA EMPRESA VIRA UMA" "TORRE DE|BABEL" azul
t t12_aula01 03 B 10 "PARA ONDE" "VOCÊ VAI?" azul
t t12_aula01 04 A 18 "QUEM TE TIRA DO SÉRIO" "PISOU NUM|VALOR" azul
t t12_aula01 04 B 07 "SÓ SEIS" "VALORES" azul
