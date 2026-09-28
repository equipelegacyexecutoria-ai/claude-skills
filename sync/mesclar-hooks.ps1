# Mescla sync/hooks.json no settings.json deste PC (que não sincroniza).
# Só troca as entradas cujo comando contém /.claude/sync/; os outros hooks (ex.: som) ficam como estão.
# Faz backup antes e grava em UTF-8 sem BOM.
$ErrorActionPreference = 'Stop'
$claude = Join-Path $HOME '.claude'
$setArq = Join-Path $claude 'settings.json'
$novos = Get-Content -Raw -Encoding UTF8 (Join-Path $PSScriptRoot 'hooks.json') | ConvertFrom-Json

if (Test-Path $setArq) {
  $bak = Join-Path $claude ("sync-local\settings.backup-{0:yyyyMMdd-HHmmss}.json" -f (Get-Date))
  New-Item -ItemType Directory -Force (Split-Path $bak) | Out-Null
  Copy-Item $setArq $bak
  $set = Get-Content -Raw -Encoding UTF8 $setArq | ConvertFrom-Json
} else {
  $set = New-Object PSObject
}
if (-not $set.PSObject.Properties['hooks']) { $set | Add-Member -NotePropertyName hooks -NotePropertyValue (New-Object PSObject) }

function EhDaSincronia($entrada) {
  foreach ($h in @($entrada.hooks)) { if ($h.command -match '/\.claude/sync/') { return $true } }
  return $false
}

foreach ($ev in $novos.PSObject.Properties.Name) {
  $atuais = @()
  if ($set.hooks.PSObject.Properties[$ev]) { $atuais = @($set.hooks.$ev | Where-Object { -not (EhDaSincronia $_) }) }
  $lista = New-Object Collections.ArrayList
  foreach ($a in $atuais) { [void]$lista.Add($a) }
  foreach ($n in @($novos.$ev)) { [void]$lista.Add($n) }
  if ($set.hooks.PSObject.Properties[$ev]) { $set.hooks.$ev = $lista.ToArray() } else { $set.hooks | Add-Member -NotePropertyName $ev -NotePropertyValue $lista.ToArray() }
}

$json = $set | ConvertTo-Json -Depth 30
[IO.File]::WriteAllText($setArq, $json, (New-Object Text.UTF8Encoding $false))
Write-Output "hooks da sincronia mesclados em $setArq"
