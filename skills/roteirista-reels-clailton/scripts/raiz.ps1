# Devolve a Raiz do Roteirista (pasta com dados\ e roteiros\) neste PC.
# Ordem: variável ROTEIRISTA_RAIZ, scripts\raiz-do-projeto.txt (local, não sincroniza),
# ~/.claude/maquina.json (campo "roteirista"), Área de Trabalho\Projetos Edições\Roteirista de Reels.
$candidatos = @()
if ($env:ROTEIRISTA_RAIZ) { $candidatos += $env:ROTEIRISTA_RAIZ }
$arq = Join-Path $PSScriptRoot 'raiz-do-projeto.txt'
if (Test-Path $arq) { $candidatos += (Get-Content -Raw -Encoding UTF8 $arq).Trim() }
$maq = Join-Path $HOME '.claude\maquina.json'
if (Test-Path $maq) {
  try { $m = Get-Content -Raw -Encoding UTF8 $maq | ConvertFrom-Json; if ($m.roteirista) { $candidatos += $m.roteirista } } catch {}
}
$candidatos += Join-Path ([Environment]::GetFolderPath('Desktop')) 'Projetos Edições\Roteirista de Reels'
foreach ($c in $candidatos) { if ($c -and (Test-Path (Join-Path $c 'dados'))) { return $c } }
return $candidatos[-1]
