<#
.SYNOPSIS
  Recalcula as estatísticas dos reels do Clailton por formato visual (novela x tela dividida).

.DESCRIPTION
  Lê dados/reels_base.json e imprime (ou grava) um relatório em Markdown com:
  formato geral, tela com x sem imagens, mês x formato, hook x formato, tema x formato,
  CTA x formato, faixa de palavras/duração dos vencedores e top/bottom por formato.
  Lift = views_vs_mediana_do_mes. Só reels maduros entram nas medianas.
  Evidência: FORTE (n >= 20), MEDIA (10 a 19), INDICATIVO (n < 10).

.EXAMPLE
  powershell -File stats-formatos.ps1
  powershell -File stats-formatos.ps1 -Saida dados\stats.md
  powershell -File stats-formatos.ps1 -Ate 31/08/2026     # holdout: só até agosto
#>
param(
  [string]$Base,
  [string]$Saida,
  [string]$Ate,
  [switch]$IncluirCortes
)

$ErrorActionPreference = 'Stop'
$pt = [Globalization.CultureInfo]'pt-BR'
$root = & (Join-Path $PSScriptRoot 'raiz.ps1')
if (-not $Base) { $Base = Join-Path $root 'dados\reels_base.json' }
$j = Get-Content -Raw -Encoding UTF8 $Base | ConvertFrom-Json

function ParseData([string]$s) { [datetime]::ParseExact($s.Substring(0, 10), 'dd/MM/yyyy', $pt) }
function Med($a) {
  $s = @($a | Where-Object { $_ -ne $null } | Sort-Object)
  if ($s.Count -eq 0) { return $null }
  $m = [math]::Floor($s.Count / 2)
  if ($s.Count % 2) { return [double]$s[$m] } else { return ([double]$s[$m - 1] + [double]$s[$m]) / 2 }
}
function Pct($a, [double]$p) {
  $s = @($a | Where-Object { $_ -ne $null } | Sort-Object)
  if ($s.Count -eq 0) { return $null }
  $idx = [math]::Round(($s.Count - 1) * $p)
  return [double]$s[[int]$idx]
}
function F($v, [string]$fmt = '0.00') { if ($v -eq $null) { return '-' } else { return ([double]$v).ToString($fmt, $pt) } }
function K($v) {
  if ($v -eq $null) { return '-' }
  $v = [double]$v
  if ($v -ge 1000000) { return ($v / 1000000).ToString('0.00', $pt) + ' mi' }
  if ($v -ge 1000) { return ($v / 1000).ToString('0', $pt) + 'k' }
  return $v.ToString('0', $pt)
}
function Evid([int]$n) { if ($n -ge 20) { 'FORTE' } elseif ($n -ge 10) { 'MEDIA' } else { 'INDICATIVO' } }
function Palavras([string]$t) { if (-not $t) { return 0 }; return @($t -split '\s+' | Where-Object { $_ }).Count }

$rows = foreach ($r in $j.reels) {
  $d = ParseData $r.data_hora
  [pscustomobject]@{
    id = $r.id; fmt = $r.formato_visual; img = $r.tela_com_imagens; origem = $r.origem; imp = $r.impulsionado
    data = $d; mes = $d.ToString('yyyy-MM'); mat = ($r.maturidade -eq 'maduro')
    views = [double]$r.metricas.views; lift = $r.metricas.views_vs_mediana_do_mes
    like = $r.metricas.taxa_curtida_pct; com = $r.metricas.taxa_comentario_pct; rep = $r.metricas.taxa_repost_pct
    dur = $r.duracao_s; hook = $r.hook.tipo; tema = $r.tema; cta = ($r.cta_falado -join '+')
    pal = (Palavras $r.copy_original.transcricao_falada); frase1 = $r.hook.frase_1
  }
}
if ($Ate) { $lim = ParseData $Ate; $rows = @($rows | Where-Object { $_.data -le $lim }) }

$sb = New-Object Text.StringBuilder
function L([string]$s = '') { [void]$sb.AppendLine($s) }

function Linha($g, [string]$nome) {
  $g = @($g); $m = @($g | Where-Object { $_.mat })
  $h1 = @($m | Where-Object { $_.lift -gt 1 }).Count; $h3 = @($m | Where-Object { $_.lift -ge 3 }).Count
  $c150 = @($m | Where-Object { $_.views -gt 150000 }).Count; $c800 = @($m | Where-Object { $_.views -gt 800000 }).Count
  return "| $nome | $($g.Count) | $($m.Count) | $(Evid $m.Count) | $(K (Med ($m | ForEach-Object { $_.views }))) | $(F (Med ($m | ForEach-Object { $_.lift })))x | $h1 | $h3 | $c150 | $c800 | $(F (Med ($m | ForEach-Object { $_.like })))% | $(F (Med ($m | ForEach-Object { $_.com })) '0.000')% | $(F (Med ($m | ForEach-Object { $_.rep })) '0.000')% | $(F (Med ($g | ForEach-Object { $_.dur })) '0') | $(F (Med ($g | ForEach-Object { $_.pal })) '0') |"
}
$cab = '| grupo | n | maduros | evidência | mediana views | mediana lift | >1x | >=3x | >150k | >800k | curtida | comentário | repost | seg. | palavras |'
$sep = '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|'

$periodo = "$(($rows | Sort-Object data | Select-Object -First 1).data.ToString('dd/MM/yyyy')) a $(($rows | Sort-Object data | Select-Object -Last 1).data.ToString('dd/MM/yyyy'))"
L "# Estatísticas por formato visual"
L ""
L "Base: $Base · período: $periodo · reels: $(@($rows).Count) · maduros: $(@($rows | Where-Object { $_.mat }).Count)"
L "Lift = views ÷ mediana de views do mês. >1x e >=3x contam reels maduros acima desses lifts. Evidência pelo n de maduros: FORTE >= 20, MEDIA 10–19, INDICATIVO < 10 (use a contagem de acertos, não a mediana)."
L ""
L "## 1. Formato"
L ""; L $cab; L $sep
foreach ($f in 'novela', 'tela_dividida', 'outro') { L (Linha ($rows | Where-Object { $_.fmt -eq $f }) $f) }
L (Linha ($rows | Where-Object { $_.fmt -eq 'tela_dividida' -and $_.img -eq $true }) 'tela_dividida COM imagens')
L (Linha ($rows | Where-Object { $_.fmt -eq 'tela_dividida' -and $_.img -eq $false }) 'tela_dividida SEM imagens')
L (Linha ($rows | Where-Object { $_.fmt -eq 'novela' -and $_.origem -eq 'corte' }) 'novela (só cortes de palco/aula)')
if (@($rows | Where-Object { $_.imp -ne $null }).Count) {
  L (Linha ($rows | Where-Object { $_.imp -eq $true }) 'impulsionados')
  L (Linha ($rows | Where-Object { $_.imp -eq $false }) 'orgânicos')
}
L ""
L "## 2. Mês x formato (mediana do lift, n maduros)"
L ""
L "| mês | novela | tela dividida | tela com imagens |"; L "|---|---|---|---|"
foreach ($mes in ($rows | Select-Object -ExpandProperty mes -Unique | Sort-Object)) {
  $cel = foreach ($cond in @({ param($x) $x.fmt -eq 'novela' }, { param($x) $x.fmt -eq 'tela_dividida' }, { param($x) $x.fmt -eq 'tela_dividida' -and $x.img -eq $true })) {
    $g = @($rows | Where-Object { $_.mes -eq $mes -and $_.mat -and (& $cond $_) })
    "$(F (Med ($g | ForEach-Object { $_.lift })))x (n=$($g.Count))"
  }
  L "| $mes | $($cel -join ' | ') |"
}

$cand = @($rows | Where-Object { $_.fmt -ne 'outro' })
if (-not $IncluirCortes) { $cand = @($cand | Where-Object { $_.origem -ne 'corte' }) }
function TabelaCruzada([string]$campo, [string]$titulo) {
  L ""
  L "## $titulo"
  L ""
  L "Formato: mediana do lift · acertos >1x/n · acertos >=3x/n · evidência. Cortes de palco/aula fora, salvo -IncluirCortes."
  L ""
  L "| $campo | novela | tela dividida |"; L "|---|---|---|"
  $grupos = $cand | Group-Object $campo | Sort-Object Count -Descending
  foreach ($g in $grupos) {
    $cel = foreach ($f in 'novela', 'tela_dividida') {
      $m = @($g.Group | Where-Object { $_.fmt -eq $f -and $_.mat })
      if ($m.Count -eq 0) { '-' } else {
        $h1 = @($m | Where-Object { $_.lift -gt 1 }).Count; $h3 = @($m | Where-Object { $_.lift -ge 3 }).Count
        "$(F (Med ($m | ForEach-Object { $_.lift })))x · $h1/$($m.Count) · $h3/$($m.Count) · $(Evid $m.Count)"
      }
    }
    L "| $($g.Name) | $($cel -join ' | ') |"
  }
}
TabelaCruzada 'hook' '3. Tipo de hook x formato'
TabelaCruzada 'tema' '4. Tema x formato'
TabelaCruzada 'cta' '5. CTA falado x formato'

L ""
L "## 6. Tamanho dos vencedores (maduros com lift >= 2x)"
L ""
L "| formato | n | palavras p25 | palavras mediana | palavras p75 | min–max | segundos p25 | segundos mediana | segundos p75 |"; L "|---|---|---|---|---|---|---|---|---|"
foreach ($f in 'novela', 'tela_dividida') {
  $w = @($cand | Where-Object { $_.fmt -eq $f -and $_.mat -and $_.lift -ge 2 })
  $p = $w | ForEach-Object { $_.pal }; $s = $w | ForEach-Object { $_.dur }
  L "| $f | $($w.Count) | $(F (Pct $p 0.25) '0') | $(F (Med $p) '0') | $(F (Pct $p 0.75) '0') | $(F (Pct $p 0) '0')–$(F (Pct $p 1) '0') | $(F (Pct $s 0.25) '0') | $(F (Med $s) '0') | $(F (Pct $s 0.75) '0') |"
}

foreach ($f in 'novela', 'tela_dividida') {
  $m = @($cand | Where-Object { $_.fmt -eq $f -and $_.mat } | Sort-Object lift -Descending)
  L ""
  L "## 7. $f · top 10 e bottom 5 por lift"
  L ""
  L "| id | views | lift | hook | tema | CTA | seg. | 1ª frase |"; L "|---|---|---|---|---|---|---|---|"
  $sel = @($m | Select-Object -First 10) + @($m | Select-Object -Last 5)
  foreach ($x in $sel) {
    $fr = [string]$x.frase1; if ($fr.Length -gt 90) { $fr = $fr.Substring(0, 90) + '…' }
    L "| $($x.id) | $(K $x.views) | $(F $x.lift)x | $($x.hook) | $($x.tema) | $($x.cta) | $($x.dur) | $($fr -replace '\|','/') |"
  }
}

$texto = $sb.ToString()
if ($Saida) {
  if (-not [IO.Path]::IsPathRooted($Saida)) { $Saida = Join-Path $root $Saida }
  [IO.File]::WriteAllText($Saida, $texto, (New-Object Text.UTF8Encoding $false))
  "Relatório gravado em $Saida"
} else { $texto }
