<#
.SYNOPSIS
  Gera o corpus pesquisável a partir de dados/reels_base.json.

.DESCRIPTION
  Cria dados/corpus/indice.md (1 linha por reel, ordenado por formato e lift) e
  um arquivo por reel em dados/corpus/{novela,tela,outros}/NNN.md com métricas,
  fala, texto na tela, legenda e a análise manual quando existir.
  Rodar de novo sempre que o reels_base.json mudar (o Analista faz isso no modo mensal).

.EXAMPLE
  powershell -File gerar-corpus.ps1
#>
param([string]$Base, [string]$Saida)

$ErrorActionPreference = 'Stop'
$pt = [Globalization.CultureInfo]'pt-BR'
$root = & (Join-Path $PSScriptRoot 'raiz.ps1')
if (-not $Base) { $Base = Join-Path $root 'dados\reels_base.json' }
if (-not $Saida) { $Saida = Join-Path $root 'dados\corpus' }
$utf8 = New-Object Text.UTF8Encoding $false
$j = Get-Content -Raw -Encoding UTF8 $Base | ConvertFrom-Json

$pastas = @{ 'novela' = 'novela'; 'tela_dividida' = 'tela'; 'outro' = 'outros' }
foreach ($p in $pastas.Values) {
  $dir = Join-Path $Saida $p
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
  Get-ChildItem $dir -Filter '*.md' | Remove-Item -Force
}

function K($v) {
  if ($v -eq $null) { return '-' }
  $v = [double]$v
  if ($v -ge 1000000) { return ($v / 1000000).ToString('0.00', $pt) + ' mi' }
  if ($v -ge 1000) { return ($v / 1000).ToString('0', $pt) + 'k' }
  return $v.ToString('0', $pt)
}
function F($v, [string]$fmt = '0.00') { if ($v -eq $null) { '-' } else { ([double]$v).ToString($fmt, $pt) } }
function ParaMarkdown($obj, [int]$nivel = 0) {
  # Converte a análise manual (objeto JSON de formato livre) em lista Markdown.
  $pad = '  ' * $nivel
  $out = New-Object Collections.Generic.List[string]
  if ($obj -is [System.Management.Automation.PSCustomObject]) {
    foreach ($prop in $obj.PSObject.Properties) {
      $v = $prop.Value
      if ($v -is [System.Management.Automation.PSCustomObject] -or ($v -is [array] -and $v.Count -gt 0 -and $v[0] -is [System.Management.Automation.PSCustomObject])) {
        $out.Add("$pad- **$($prop.Name)**:"); foreach ($l in (ParaMarkdown $v ($nivel + 1))) { $out.Add($l) }
      } elseif ($v -is [array]) {
        $out.Add("$pad- **$($prop.Name)**:"); foreach ($x in $v) { $out.Add("$pad  - $x") }
      } else { $out.Add("$pad- **$($prop.Name)**: $v") }
    }
  } elseif ($obj -is [array]) {
    foreach ($x in $obj) { foreach ($l in (ParaMarkdown $x $nivel)) { $out.Add($l) } }
  } else { $out.Add("$pad- $obj") }
  return $out
}

$linhas = New-Object Collections.Generic.List[object]
foreach ($r in $j.reels) {
  $fmt = $r.formato_visual; $pasta = $pastas[$fmt]
  $nnn = '{0:000}' -f [int]$r.id
  $m = $r.metricas
  $img = if ($fmt -eq 'tela_dividida') { if ($r.tela_com_imagens) { 'com imagens' } else { 'sem imagens (só o Clailton vertical)' } } else { '-' }
  $imp = if ($r.impulsionado -eq $null) { 'não informado' } elseif ($r.impulsionado) { 'sim' } else { 'não' }
  $sb = New-Object Text.StringBuilder
  [void]$sb.AppendLine("# #$nnn · $($fmt.ToUpper()) · $(K $m.views) views · $(F $m.views_vs_mediana_do_mes)x a mediana do mês")
  [void]$sb.AppendLine("")
  [void]$sb.AppendLine("- Link: $($r.link)")
  [void]$sb.AppendLine("- Data: $($r.data_hora) ($($r.dia_semana)) · Duração: $($r.duracao_s) s · Maturidade: $($r.maturidade) · Origem: $($r.origem) · Tela: $img · Impulsionado: $imp")
  [void]$sb.AppendLine("- Hook: $($r.hook.tipo) · Tema: $($r.tema) · CTA falado: $($r.cta_falado -join ' + ')")
  [void]$sb.AppendLine("- Taxas: curtida $(F $m.taxa_curtida_pct)% · comentário $(F $m.taxa_comentario_pct '0.000')% · repost $(F $m.taxa_repost_pct '0.000')% · comentários $($m.comentarios) · reposts $($m.reposts)")
  [void]$sb.AppendLine("- Estrutura: história/caso $($r.marcadores_de_estrutura.tem_historia_ou_caso) · números $($r.marcadores_de_estrutura.tem_numeros) · $($r.marcadores_de_estrutura.palavras_por_segundo) palavras/s · termina com pergunta $($r.fecho.termina_com_pergunta)")
  [void]$sb.AppendLine("")
  [void]$sb.AppendLine("## Fala")
  [void]$sb.AppendLine("")
  [void]$sb.AppendLine($(if ($r.copy_original.transcricao_falada) { $r.copy_original.transcricao_falada } else { '(sem fala)' }))
  [void]$sb.AppendLine("")
  [void]$sb.AppendLine("## Texto na tela")
  [void]$sb.AppendLine("")
  [void]$sb.AppendLine($(if ($r.copy_original.texto_na_tela) { $r.copy_original.texto_na_tela } else { '(vazio)' }))
  [void]$sb.AppendLine("")
  [void]$sb.AppendLine("## Legenda do post")
  [void]$sb.AppendLine("")
  [void]$sb.AppendLine($(if ($r.copy_original.legenda) { $r.copy_original.legenda } else { '(vazia)' }))
  if ($r.analise_aprofundada) {
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("## Análise manual")
    [void]$sb.AppendLine("")
    foreach ($l in (ParaMarkdown $r.analise_aprofundada)) { [void]$sb.AppendLine($l) }
  }
  [IO.File]::WriteAllText((Join-Path (Join-Path $Saida $pasta) "$nnn.md"), $sb.ToString(), $utf8)
  $fr = [string]$r.hook.frase_1; if ($fr.Length -gt 110) { $fr = $fr.Substring(0, 110) + '…' }
  $linhas.Add([pscustomobject]@{
    fmt = $fmt; lift = [double]$m.views_vs_mediana_do_mes; mat = $r.maturidade
    txt = "| $nnn | $fmt | $(if ($fmt -eq 'tela_dividida') { if ($r.tela_com_imagens) { 'img' } else { 'sem img' } } else { '' }) | $(if ($r.origem -eq 'corte') { 'corte' } else { 'rot.' }) | $($r.data_hora.Substring(0,5)) | $(K $m.views) | $(F $m.views_vs_mediana_do_mes)x$(if ($r.maturidade -ne 'maduro') { ' (recente)' }) | $($r.hook.tipo) | $($r.tema) | $($r.cta_falado -join '+') | $($r.duracao_s) | $($fr -replace '\|','/') |"
  })
}

$ix = New-Object Text.StringBuilder
[void]$ix.AppendLine("# Índice do corpus: reels do Clailton")
[void]$ix.AppendLine("")
[void]$ix.AppendLine("Gerado de $([IO.Path]::GetFileName($Base)) por scripts/gerar-corpus.ps1. Uma linha por reel, ordenado por formato e lift (views ÷ mediana do mês).")
[void]$ix.AppendLine("Arquivo completo de cada reel: dados/corpus/{novela,tela,outros}/NNN.md. Busque com Grep (ex.: tema, tipo de hook, palavra da 1ª frase) em vez de ler tudo.")
[void]$ix.AppendLine("")
[void]$ix.AppendLine("| id | formato | imagens | origem | data | views | lift | hook | tema | CTA | seg. | 1ª frase |")
[void]$ix.AppendLine("|---|---|---|---|---|---|---|---|---|---|---|---|")
foreach ($f in 'novela', 'tela_dividida', 'outro') {
  foreach ($l in ($linhas | Where-Object { $_.fmt -eq $f } | Sort-Object lift -Descending)) { [void]$ix.AppendLine($l.txt) }
}
[IO.File]::WriteAllText((Join-Path $Saida 'indice.md'), $ix.ToString(), $utf8)
"Corpus gerado: $($linhas.Count) reels em $Saida"
