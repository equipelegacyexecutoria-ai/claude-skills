<#
.SYNOPSIS
  Checagens objetivas de um roteiro de reel do Clailton (novela ou tela dividida).

.DESCRIPTION
  Lê a seção "## ROTEIRO FALADO" do arquivo (ou o texto inteiro, se não houver a seção) e imprime:
    FALHA  → reprova o gate de lint (exit code 1)
    AVISO  → não reprova, mas entra na nota de voz
    INFO   → números de referência (palavras, segundos estimados, frases)
  Checa: "talvez/pode ser" na 1ª frase, abertura de apresentador, travessão, "PME",
  CTA incompatível com o objetivo, cópia de 8+ palavras da referência (FALHA);
  tamanho fora da faixa do formato, frases longas, "pra/tá/cê/tô", possessivo seu/sua,
  fecho longo ou com "talvez", marcadores repetidos, palavrão em excesso, menção a imagens
  na novela, frases reaproveitadas de roteiros anteriores ou do corpus e ressalvas gastas (AVISO).

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File lint-roteiro.ps1 -Arquivo roteiros\_trabalho\2026-09-26-x\03-roteiro-v1.md -Formato novela
  powershell ... -Arquivo <roteiro> -Formato tela_dividida -Objetivo conversao -Referencia roteiros\_trabalho\...\00-referencia.md
#>
param(
  [string]$Arquivo,
  [string]$Texto,
  [Parameter(Mandatory = $true)][ValidateSet('novela', 'tela_dividida')][string]$Formato,
  [ValidateSet('alcance', 'envio', 'salvamento', 'conversao')][string]$Objetivo = 'alcance',
  [string]$Referencia,
  [string]$Historico,
  [string]$Base,
  [switch]$SemCorpus
)

$ErrorActionPreference = 'Stop'
$raizArq = Join-Path $PSScriptRoot 'raiz-do-projeto.txt'
$root = if (Test-Path $raizArq) { (Get-Content -Raw -Encoding UTF8 $raizArq).Trim() } else { Split-Path (Split-Path (Split-Path (Split-Path $PSScriptRoot))) }
if (-not $Historico) { $Historico = Join-Path $root 'roteiros' }
if (-not $Base) { $Base = Join-Path $root 'dados\reels_base.json' }

function Secao([string]$txt, [string[]]$titulos) {
  foreach ($t in $titulos) {
    $m = [regex]::Match($txt, ('(?ms)^##\s*' + [regex]::Escape($t) + '\s*$(.*?)(?=^##\s|\z)'))
    if ($m.Success) { return $m.Groups[1].Value }
  }
  return $txt
}
function Limpa([string]$t) {
  $t = $t -replace '(?m)^\s*>\s?', ''
  $t = $t -replace '\[VERIFICAR[^\]]*\]', ''
  $t = $t -replace '\s+', ' '
  return $t.Trim()
}
function Palavras([string]$t) { return @(($t.ToLower() -replace '[^\p{L}\p{N}\s]', ' ') -split '\s+' | Where-Object { $_ }) }
function NGramas([string[]]$w, [int]$n = 8) {
  $set = New-Object 'System.Collections.Generic.HashSet[string]'
  for ($i = 0; $i -le $w.Count - $n; $i++) { [void]$set.Add(($w[$i..($i + $n - 1)] -join ' ')) }
  return , $set
}
function Cnt([string]$t, [string]$pat) { return ([regex]::Matches($t, $pat)).Count }

if ($Arquivo) {
  if (-not [IO.Path]::IsPathRooted($Arquivo)) { $Arquivo = Join-Path (Get-Location) $Arquivo }
  $bruto = Get-Content -Raw -Encoding UTF8 $Arquivo
} elseif ($Texto) { $bruto = $Texto } else { throw 'Informe -Arquivo ou -Texto.' }

$fala = Limpa (Secao $bruto @('ROTEIRO FALADO', 'Roteiro falado', 'Fala'))
$frases = @([regex]::Split($fala, '(?<=[\.\!\?…])\s+') | Where-Object { $_.Trim() })
$w = Palavras $fala
$falhas = New-Object Collections.Generic.List[string]
$avisos = New-Object Collections.Generic.List[string]
$infos = New-Object Collections.Generic.List[string]

# ---------- FALHAS ----------
$primeira = if ($frases.Count) { $frases[0] } else { '' }
if ($primeira -match '(?i)\btalvez\b|\bpode ser\b|\bàs vezes\b') { $falhas.Add("1ª frase com hesitação ('talvez', 'pode ser', 'às vezes'): `"$primeira`"") }
if ($fala -match '(?i)^\s*(oi|olá|ola|fala|e aí|bom dia|boa tarde|boa noite)\b' -or $fala.Substring(0, [Math]::Min(120, $fala.Length)) -match '(?i)hoje eu (quero|vou) (falar|conversar)') {
  $falhas.Add('Abertura de apresentador ("oi gente", "fala pessoal", "hoje eu quero falar sobre").')
}
$trav = Cnt $bruto '[—–]'
$travFala = Cnt $fala '[—–]'
if ($travFala -gt 0) { $falhas.Add("Travessão na fala: $travFala ocorrência(s). Troque por ponto, vírgula ou dois-pontos.") }
elseif ($trav -gt 0) { $avisos.Add("Travessão fora da fala (no resto do arquivo): $trav. Não afeta a gravação, mas evite.") }
$pme = Cnt $fala '\bPMEs?\b'
if ($pme -gt 0) { $falhas.Add("'PME' na fala ($pme). Diga 'dono de empresa', 'empresário' ou o porte em número.") }

$linkBio = Cnt $fala '(?i)link\s+(da|na)\s+bio'
# Palavra-chave: verbo + (aqui/embaixo/a palavra) + UMA palavra + fim de frase ou "aqui embaixo"/"que eu te mando"...
$kwPat = '(?i)\b(comenta|comente|digita|digite|escreve|escreva)\b(\s+aqui:?)?(\s+embaixo:?)?(\s+a\s+palavra)?\s+["“'']?(\p{L}+)["”'']?(?=\s*[\.\!,;]|\s*$|\s+(aqui|que\s+eu|e\s+eu|embaixo|no\s+coment|nos\s+coment|pra\s+mim|para\s+mim))'
$kw = @([regex]::Matches($fala, $kwPat) | Where-Object { $_.Groups[5].Value -notmatch '^(o|a|os|as|qual|quais|como|se|sua|tua|seu|teu|aí|ai)$' })
if ($Objetivo -ne 'conversao') {
  if ($linkBio -gt 0) { $falhas.Add("'Link da bio' com objetivo $Objetivo (7 roteiros com link da bio, nenhum passou de 150 mil).") }
  if ($kw.Count -gt 0) { $falhas.Add("CTA de palavra-chave ($(($kw | ForEach-Object { $_.Groups[5].Value }) -join ', ')) com objetivo $Objetivo. Palavra-chave só no objetivo conversão.") }
} else {
  if ($kw.Count -eq 0) { $avisos.Add('Objetivo conversão sem CTA de palavra-chave (esperado: 1, depois do fecho).') }
  if ($kw.Count -gt 1) { $avisos.Add("Mais de 1 CTA de palavra-chave ($($kw.Count)). Use um só.") }
  if ($linkBio -gt 0) { $avisos.Add("'Link da bio' também em conversão: prefira a palavra-chave.") }
}
if ($Referencia) {
  if (-not [IO.Path]::IsPathRooted($Referencia)) { $Referencia = Join-Path (Get-Location) $Referencia }
  $refTxt = Limpa (Secao (Get-Content -Raw -Encoding UTF8 $Referencia) @('Fala', 'ROTEIRO FALADO', 'Transcrição'))
  $refSet = NGramas (Palavras $refTxt)
  $copiadas = @(); for ($i = 0; $i -le $w.Count - 8; $i++) { $g = ($w[$i..($i + 7)] -join ' '); if ($refSet.Contains($g)) { $copiadas += $g } }
  if ($copiadas.Count) { $falhas.Add("Sequência de 8+ palavras copiada da referência ($($copiadas.Count)): `"$($copiadas[0])`"...") }
}

# ---------- AVISOS ----------
$n = $w.Count
$seg = [math]::Round($n / 2.8)
if ($Formato -eq 'novela') { $alvo = @(170, 260); $lim = @(120, 300) } else { $alvo = @(280, 460); $lim = @(220, 520) }
if ($n -lt $lim[0] -or $n -gt $lim[1]) { $avisos.Add("Tamanho: $n palavras (~$seg s). Faixa dos vencedores de $Formato é $($alvo[0]) a $($alvo[1]).") }
elseif ($n -lt $alvo[0] -or $n -gt $alvo[1]) { $infos.Add("Tamanho um pouco fora do alvo ($($alvo[0]) a $($alvo[1])), mas dentro do tolerável.") }

$longas = @($frases | Where-Object { (Palavras $_).Count -gt 18 })
if ($longas.Count -gt 2) {
  $ex = ($longas | Select-Object -First 2 | ForEach-Object { $s = $_.Trim(); if ($s.Length -gt 70) { $s.Substring(0, 70) + '…' } else { $s } }) -join ' | '
  $avisos.Add("$($longas.Count) frases com mais de 18 palavras (ex.: $ex).")
}
$pra = Cnt $fala '(?i)\bpra\b'; $ta = Cnt $fala '(?i)\btá\b(?!\s*\?)'; $ce = Cnt $fala '(?i)\bcê\b'; $to = Cnt $fala '(?i)\btô\b'
if ($pra + $ta + $ce + $to -gt 0) { $avisos.Add("Fora da voz medida: 'pra' $pra · 'tá' $ta · 'cê' $ce · 'tô' $to (ele fala 'para' e 'está').") }
$teu = Cnt $fala '(?i)\b(teu|tua|teus|tuas)\b'; $seu = Cnt $fala '(?i)\b(seu|sua|seus|suas)\b'
$infos.Add("Possessivo: teu/tua $teu · seu/sua $seu (voz medida: ~3 teu para 1 seu).")
if ($seu -gt $teu -and $seu -ge 3) { $avisos.Add("Possessivo 'seu/sua' ($seu) acima de 'teu/tua' ($teu). Prefira 'teu/tua'.") }
$ultima = if ($frases.Count) { $frases[-1] } else { '' }
$ultimaSemCta = $ultima
if ($frases.Count -ge 2 -and ($ultima -match '(?i)comenta|comente|digite|digita|me siga|link|salva|envie|manda')) { $ultimaSemCta = $frases[-2] }
if ((Palavras $ultimaSemCta).Count -gt 15) { $avisos.Add("Fecho com $((Palavras $ultimaSemCta).Count) palavras (alvo ≤ 15): `"$($ultimaSemCta.Trim())`"") }
if ($ultimaSemCta -match '(?i)\btalvez\b|\bpode ser\b') { $avisos.Add('Fecho com "talvez/pode ser": enfraquece a frase citável.') }
$pa = Cnt $fala '(?i)preste atenção|presta atenção'; $os = Cnt $fala '(?i)olha só'
if ($pa -gt 1) { $avisos.Add("'Preste atenção' $pa vezes (máximo 1).") }
if ($os -gt 2) { $avisos.Add("'Olha só' $os vezes.") }
$palavrao = Cnt $fala '(?i)\bmaldit\w*|\bporcaria\b|\bdroga\b|\bmerda\b|\bcaralho\b|\bporra\b'
if ($palavrao -gt 1) { $avisos.Add("Palavrão $palavrao vezes (máximo 1, leve).") }
if (Cnt $fala '(?i)\bmerda\b|\bcaralho\b|\bporra\b') { $avisos.Add('Palavrão pesado: fora da voz dele.') }
if ($Formato -eq 'novela' -and (Cnt $fala '(?i)(nessas|essas|nesta|esta|essa|nessa) imagens?|olha (essa|esta) imagem|na tela aqui') -gt 0) {
  $avisos.Add('Novela não tem imagens de apoio: tire as menções a "imagem".')
}
if ($Formato -eq 'tela_dividida' -and $Arquivo) {
  $mapa = Secao $bruto @('MAPA DE ÂNCORAS', 'MAPA DE ANCORAS')
  if ($mapa -eq $bruto) { $avisos.Add('Tela dividida sem a seção "## MAPA DE ÂNCORAS".') }
  else { $linhas = @(($mapa -split "`n") | Where-Object { $_ -match '^\|\s*\d+' }); if ($linhas.Count -lt 3) { $avisos.Add("Mapa de âncoras com $($linhas.Count) linha(s); a pauta pede 3 ou mais âncoras mostráveis.") } }
}

# Frases reaproveitadas (roteiros anteriores e corpus real) e ressalvas gastas
$assinaturas = @('antes que você me cancele', 'sim, de propósito', 'parece exagerado', 'deixa eu te contar uma história', 'é aqui que essa história deixa de ser', 'calma, essa cena não aconteceu', 'e eu vou te explicar porquê', 'já salva esse vídeo', 'não estou falando aqui de')
$anteriores = @()
if (Test-Path $Historico) {
  $anteriores = @(Get-ChildItem $Historico -Filter '*.md' -File | Where-Object { -not $Arquivo -or $_.FullName -ne $Arquivo } | Sort-Object LastWriteTime -Descending | Select-Object -First 30)
}
if ($anteriores.Count) {
  $histSet = New-Object 'System.Collections.Generic.HashSet[string]'
  $recentes = @()
  foreach ($f in $anteriores) {
    $t = Limpa (Secao (Get-Content -Raw -Encoding UTF8 $f.FullName) @('ROTEIRO FALADO', 'Roteiro falado'))
    foreach ($g in (NGramas (Palavras $t))) { [void]$histSet.Add($g) }
    $recentes += $t.ToLower()
  }
  $rep = @(); for ($i = 0; $i -le $w.Count - 8; $i++) { $g = ($w[$i..($i + 7)] -join ' '); if ($histSet.Contains($g)) { $rep += $g } }
  if ($rep.Count) { $avisos.Add("$($rep.Count) sequência(s) de 8+ palavras repetidas de roteiros anteriores (ex.: `"$($rep[0])`").") }
  $falaLow = $fala.ToLower()
  foreach ($a in $assinaturas) {
    if ($falaLow.Contains($a)) {
      $usos = @($recentes | Select-Object -First 10 | Where-Object { $_.Contains($a) }).Count
      if ($usos -ge 2) { $avisos.Add("Ressalva gasta: `"$a`" aparece em $usos dos últimos 10 roteiros. Troque.") }
    }
  }
}
if (-not $SemCorpus -and (Test-Path $Base)) {
  $j = Get-Content -Raw -Encoding UTF8 $Base | ConvertFrom-Json
  $corpSet = New-Object 'System.Collections.Generic.HashSet[string]'
  foreach ($r in $j.reels) { if ($r.copy_original.transcricao_falada) { foreach ($g in (NGramas (Palavras $r.copy_original.transcricao_falada))) { [void]$corpSet.Add($g) } } }
  $old = @(); for ($i = 0; $i -le $w.Count - 8; $i++) { $g = ($w[$i..($i + 7)] -join ' '); if ($corpSet.Contains($g)) { $old += $g } }
  if ($old.Count -gt 3) { $avisos.Add("$($old.Count) sequência(s) de 8+ palavras iguais a reels já publicados (ex.: `"$($old[0])`"). Normal em regravação; em roteiro novo, reescreva.") }
}

# ---------- SAÍDA ----------
$infos.Insert(0, "Formato: $Formato · Objetivo: $Objetivo · $n palavras · ~$seg s a 2,8 palavras/s · $($frases.Count) frases · média $([math]::Round($n / [math]::Max(1, $frases.Count), 1)) palavras/frase")
foreach ($x in $falhas) { "FALHA: $x" }
foreach ($x in $avisos) { "AVISO: $x" }
foreach ($x in $infos) { "INFO: $x" }
"RESULTADO: $(if ($falhas.Count) { 'REPROVADO' } else { 'OK' }) · FALHA $($falhas.Count) · AVISO $($avisos.Count)"
if ($falhas.Count) { exit 1 } else { exit 0 }
