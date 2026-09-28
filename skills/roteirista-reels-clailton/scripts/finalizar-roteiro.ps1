<#
.SYNOPSIS
  Monta a entrega final de um roteiro do fluxo rápido (sem rodada de reescrita).

.DESCRIPTION
  Lê na pasta de trabalho:
    03-roteiro.md        rascunho do roteirista, já no template da entrega (obrigatório)
    05-auditoria.json    veredito, nota, abertura escolhida, ranking de hooks, correções {de, para}, "por que" (obrigatório)
    04-fatos.json        correções {de, para}, pendências e fatos novos confirmados (opcional)
    01-pauta.md          linha "Alternativo:" com o ângulo alternativo (opcional)
  Aplica a abertura escolhida e as correções, recalcula palavras e segundos, preenche as seções finais,
  grava roteiros/<pasta>-<novela|tela>.md, roda o lint, registra em roteiros/_log.csv e acrescenta os fatos
  novos em dados/casos-verificados.md. Imprime a fala final.
  Códigos de saída: 0 ok · 1 lint com FALHA na entrega · 2 veredito REPENSA (nada é gravado).

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File finalizar-roteiro.ps1 -Pasta roteiros\_trabalho\2026-09-27-meu-tema
#>
param(
  [Parameter(Mandatory = $true)][string]$Pasta,
  [string]$Saida,
  [switch]$SemRegistro
)

$ErrorActionPreference = 'Stop'
$raizArq = Join-Path $PSScriptRoot 'raiz-do-projeto.txt'
$root = if (Test-Path $raizArq) { (Get-Content -Raw -Encoding UTF8 $raizArq).Trim() } else { Split-Path (Split-Path (Split-Path (Split-Path $PSScriptRoot))) }
if (-not [IO.Path]::IsPathRooted($Pasta)) { $Pasta = Join-Path $root $Pasta }
$utf8 = New-Object Text.UTF8Encoding $false
$avisos = New-Object Collections.Generic.List[string]

function Ler([string]$nome) { $p = Join-Path $Pasta $nome; if (Test-Path $p) { return [IO.File]::ReadAllText($p, [Text.Encoding]::UTF8) } else { return $null } }
function Json([string]$nome) { $t = Ler $nome; if ($t) { return ($t | ConvertFrom-Json) } else { return $null } }

# ---------- Seções do markdown ----------
function Dividir([string]$md) {
  $pre = New-Object Text.StringBuilder; $secoes = New-Object Collections.Generic.List[object]; $cur = $null
  foreach ($linha in ($md -split "\r?\n")) {
    if ($linha -match '^##\s+(.+?)\s*$') { $cur = [pscustomobject]@{ titulo = $Matches[1]; linhas = New-Object Collections.Generic.List[string] }; $secoes.Add($cur) }
    elseif ($cur) { $cur.linhas.Add($linha) } else { [void]$pre.AppendLine($linha) }
  }
  return [pscustomobject]@{ pre = $pre.ToString().TrimEnd(); secoes = $secoes }
}
function Secao($doc, [string]$titulo) { foreach ($s in $doc.secoes) { if ($s.titulo -like "$titulo*") { return $s } }; return $null }
function TextoSecao($s) { if (-not $s) { return '' }; return (($s.linhas -join "`n").Trim()) }
function DefinirSecao($doc, [string]$titulo, [string]$texto, [string]$novoTitulo) {
  $s = Secao $doc $titulo
  if (-not $s) { $s = [pscustomobject]@{ titulo = $(if ($novoTitulo) { $novoTitulo } else { $titulo }); linhas = New-Object Collections.Generic.List[string] }; $doc.secoes.Add($s) }
  if ($novoTitulo) { $s.titulo = $novoTitulo }
  $s.linhas.Clear(); foreach ($l in ($texto -split "`n")) { $s.linhas.Add($l) }
}
function Montar($doc) {
  $sb = New-Object Text.StringBuilder
  [void]$sb.AppendLine($doc.pre); [void]$sb.AppendLine('')
  foreach ($s in $doc.secoes) { [void]$sb.AppendLine("## $($s.titulo)"); [void]$sb.AppendLine((($s.linhas -join "`n").Trim())); [void]$sb.AppendLine('') }
  return $sb.ToString().TrimEnd() + "`n"
}

# Substitui "de" por "para" tolerando diferenças de espaço e de aspas.
function Substituir([string]$texto, [string]$de, [string]$para, [ref]$ok) {
  $ok.Value = $false
  if (-not $de) { return $texto }
  $i = $texto.IndexOf($de)
  if ($i -ge 0) { $ok.Value = $true; return $texto.Substring(0, $i) + $para + $texto.Substring($i + $de.Length) }
  $pad = [regex]::Escape(($de -replace '\s+', ' ').Trim())
  $pad = $pad -replace '\\ ', '\s+'
  $pad = $pad -replace '["“”]', '["“”]' -replace "['‘’]", "['‘’]"
  $m = [regex]::Match($texto, $pad)
  if ($m.Success) { $ok.Value = $true; return $texto.Substring(0, $m.Index) + $para + $texto.Substring($m.Index + $m.Length) }
  return $texto
}
function Palavras([string]$t) { return @(($t.ToLower() -replace '[^\p{L}\p{N}\s]', ' ') -split '\s+' | Where-Object { $_ }).Count }

# ---------- Entradas ----------
$rascunho = Ler '03-roteiro.md'
if (-not $rascunho) { throw "Não achei 03-roteiro.md em $Pasta" }
$aud = Json '05-auditoria.json'
if (-not $aud) { throw "Não achei 05-auditoria.json em $Pasta" }
$fat = Json '04-fatos.json'
$pauta = Ler '01-pauta.md'

if ($aud.veredito -eq 'REPENSA') {
  "VEREDITO: REPENSA (nota $($aud.nota), estimada após correções $($aud.nota_estimada_final)). Nada foi gravado."
  "Motivo: $($aud.riscos)"
  exit 2
}

$doc = Dividir $rascunho
$fala = Secao $doc 'ROTEIRO FALADO'
if (-not $fala) { throw 'O rascunho não tem a seção "## ROTEIRO FALADO".' }
$linhasFala = @($fala.linhas | Where-Object { $_.Trim() })

# ---------- Abertura escolhida pelo Auditor ----------
$ab = $aud.abertura
if ($ab -and $ab.texto -and [int]$ab.substituir_linhas -gt 0) {
  $n = [Math]::Min([int]$ab.substituir_linhas, $linhasFala.Count)
  $nova = @(([string]$ab.texto) -split "\r?\n" | Where-Object { $_.Trim() })
  $linhasFala = @($nova) + @($linhasFala | Select-Object -Skip $n)
}
DefinirSecao $doc 'ROTEIRO FALADO' ($linhasFala -join "`n") $null

# ---------- Correções {de, para} (Auditor e Checador) ----------
$todas = @()
if ($aud.correcoes) { $todas += @($aud.correcoes) }
if ($fat -and $fat.correcoes) { $todas += @($fat.correcoes) }
$aplicadas = 0
foreach ($c in $todas) {
  $alvo = if ($c.secao) { [string]$c.secao } else { 'ROTEIRO FALADO' }
  $s = Secao $doc $alvo
  if (-not $s) { $avisos.Add("Seção '$alvo' não existe; correção não aplicada: `"$($c.de)`""); continue }
  $ok = $false
  $novo = Substituir (TextoSecao $s) ([string]$c.de) ([string]$c.para) ([ref]$ok)
  if ($ok) { DefinirSecao $doc $alvo $novo $null; $aplicadas++ } else { $avisos.Add("Correção não aplicada (trecho não encontrado em $alvo): `"$($c.de)`" → `"$($c.para)`"") }
}

# ---------- Cabeçalho ----------
$falaFinal = TextoSecao (Secao $doc 'ROTEIRO FALADO')
$np = Palavras $falaFinal
$seg = [Math]::Round($np / 2.8)
$nota = if ($aud.nota_estimada_final) { $aud.nota_estimada_final } else { $aud.nota }
$pre = $doc.pre
$pre = $pre.Replace('{{NOTA}}', "$nota/100 (auditoria: $($aud.nota); estimada após as correções: $nota)").Replace('{{VEREDITO}}', [string]$aud.veredito).Replace('{{PALAVRAS}}', [string]$np).Replace('{{SEGUNDOS}}', "~$seg")
if ($ab -and $ab.hook_tipo) { $pre = [regex]::Replace($pre, 'hook_tipo:\s*[^·\r\n]+', "hook_tipo: $($ab.hook_tipo) ") }
if ($ab -and $ab.ressalva) { $pre = [regex]::Replace($pre, 'ressalva:\s*[^·\r\n]+', "ressalva: $($ab.ressalva) ") }
$pre = [regex]::Replace($pre, 'palavras:\s*\d+', "palavras: $np")
$doc.pre = $pre

# ---------- Seções finais ----------
$hooks = @()
if ($aud.ranking_hooks) {
  $k = 0
  foreach ($h in $aud.ranking_hooks) {
    if ($ab -and $h.id -and $ab.id -and $h.id -eq $ab.id) { continue }
    $k++; if ($k -gt 3) { break }
    $hooks += "$k. `"$($h.texto)`" ($($h.tipo) · venceu $($h.vitorias))"
  }
}
if (-not $hooks.Count) { $hooks = @('(sem alternativas no ranking)') }
DefinirSecao $doc 'HOOKS DO ROTEIRISTA' ($hooks -join "`n") 'HOOKS ALTERNATIVOS'

$afirm = TextoSecao (Secao $doc 'AFIRMAÇÕES FACTUAIS')
if ($fat) {
  $linhasF = @([string]$fat.resumo)
  if ($fat.correcoes) { foreach ($c in $fat.correcoes) { $linhasF += "- Corrigido: `"$($c.de)`" → `"$($c.para)`"$(if ($c.motivo) { " ($($c.motivo))" })" } }
  if ($fat.prazo_validade) { $linhasF += "Prazo de validade: $($fat.prazo_validade)" }
  $txtF = $linhasF -join "`n"
} elseif ($afirm -and $afirm -notmatch '(?i)^\s*-?\s*nenhuma') {
  $txtF = "Checagem não rodou. Afirmações a conferir antes de gravar:`n$afirm"
} else { $txtF = 'Sem afirmações factuais checáveis (cenas hipotéticas e opinião).' }
DefinirSecao $doc 'AFIRMAÇÕES FACTUAIS' $txtF 'CHECAGEM DE FATOS'

$por = @(); foreach ($b in @($aud.por_que)) { if ($b) { $por += "- $b" } }
if ($aud.riscos) { $por += "Risco apontado pelo Auditor: $($aud.riscos)" }
DefinirSecao $doc 'POR QUE DEVE PERFORMAR' ($por -join "`n") $null

$pend = TextoSecao (Secao $doc 'PENDÊNCIAS')
$pendL = @(); if ($pend) { $pendL += $pend }
if ($fat -and $fat.pendencias) { foreach ($p in $fat.pendencias) { $pendL += "- $p" } }
foreach ($a in $avisos) { $pendL += "- [ORQUESTRADOR] $a" }
if (-not $pendL.Count) { $pendL = @('- Nenhuma.') }
DefinirSecao $doc 'PENDÊNCIAS' ($pendL -join "`n") 'PENDÊNCIAS ANTES DE GRAVAR'

if ($pauta) {
  $alt = ([regex]::Match($pauta, '(?im)^\s*[-*]?\s*\**Alternativo\**\s*:\s*(.+)$')).Groups[1].Value.Trim()
  if ($alt) { DefinirSecao $doc 'ÂNGULO ALTERNATIVO' $alt $null }
}

# ---------- Gravar, lint, log, banco ----------
$nomePasta = Split-Path $Pasta -Leaf
$formato = if ($doc.pre -match '(?i)TELA DIVIDIDA') { 'tela_dividida' } else { 'novela' }
if (-not $Saida) { $Saida = Join-Path $root ("roteiros\{0}-{1}.md" -f $nomePasta, $(if ($formato -eq 'novela') { 'novela' } else { 'tela' })) }
elseif (-not [IO.Path]::IsPathRooted($Saida)) { $Saida = Join-Path $root $Saida }
[IO.File]::WriteAllText($Saida, (Montar $doc), $utf8)

$obj = ([regex]::Match($doc.pre, '(?i)Objetivo:\s*([^\s·(]+)')).Groups[1].Value.ToLower()
$obj = $obj -replace 'ã', 'a' -replace 'ç', 'c'
if ($obj -notin @('alcance', 'envio', 'salvamento', 'conversao')) { $obj = 'alcance' }
$lint = Join-Path $PSScriptRoot 'lint-roteiro.ps1'
$saidaLint = & powershell -NoProfile -ExecutionPolicy Bypass -File $lint -Arquivo $Saida -Formato $formato -Objetivo $obj
$codLint = $LASTEXITCODE

$novos = 0
if (-not $SemRegistro) {
$logPath = Join-Path $root 'roteiros\_log.csv'
if (-not (Test-Path $logPath)) { [IO.File]::WriteAllText($logPath, "data;slug;formato;objetivo;hook_tipo;tema;ressalva;nota;palavras;arquivo`n", $utf8) }
$campo = { param($nome) ([regex]::Match($doc.pre, "(?i)$($nome):\s*([^·\r\n]+)")).Groups[1].Value.Trim() -replace ';', ',' }
$slug = $nomePasta -replace '^\d{4}-\d{2}-\d{2}-', ''
$linhaLog = "{0};{1};{2};{3};{4};{5};{6};{7};{8};{9}" -f (Get-Date -Format 'yyyy-MM-dd'), $slug, $formato, $obj, (& $campo 'hook_tipo'), (& $campo 'tema'), (& $campo 'ressalva'), $nota, $np, ($Saida.Substring($root.Length + 1) -replace '\\', '/')
[IO.File]::AppendAllText($logPath, $linhaLog + "`n", $utf8)

if ($fat -and $fat.novos_fatos) {
  $banco = Join-Path $root 'dados\casos-verificados.md'
  foreach ($f in $fat.novos_fatos) {
    $linha = "| $($f.chaves) | $($f.forma) | $($f.nao_dizer) | $($f.fonte) | $(Get-Date -Format 'yyyy-MM-dd') |" -replace "`r?`n", ' '
    [IO.File]::AppendAllText($banco, $linha + "`n", $utf8); $novos++
  }
}
}

"ENTREGA: $Saida"
"Veredito: $($aud.veredito) · nota $($aud.nota) → estimada $nota · correções aplicadas: $aplicadas de $($todas.Count) · fatos novos no banco: $novos · $np palavras (~$seg s)"
foreach ($a in $avisos) { "AVISO: $a" }
$saidaLint | Where-Object { $_ -match '^(FALHA|AVISO|RESULTADO)' }
""
"----- ROTEIRO FALADO -----"
$falaFinal
if ($codLint -ne 0) { exit 1 } else { exit 0 }
