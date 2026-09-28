# Conferência de um PC na sincronia. Verde = ok, vermelho = corrigir. Pode rodar a qualquer momento.
$ErrorActionPreference = 'Continue'
$claude = Join-Path $HOME '.claude'
$falhas = 0
function Item($nome, [bool]$ok, $dica) {
  if ($ok) { Write-Host "  [ok]    $nome" -ForegroundColor Green }
  else { Write-Host "  [FALTA] $nome -> $dica" -ForegroundColor Red; $script:falhas++ }
}

$papel = 'estacao'
try { $papel = (Get-Content -Raw -Encoding UTF8 (Join-Path $claude 'maquina.json') | ConvertFrom-Json).papel } catch {}
Write-Host "PC $env:COMPUTERNAME · papel: $papel · usuário: $HOME"

Item 'nome do usuário do Windows sem acento' ($HOME -notmatch '[^\x00-\x7F]') 'os programas de vídeo falham com acento no caminho; use um usuário sem acento'
Item 'Git instalado' ([bool](Get-Command git -ErrorAction SilentlyContinue)) 'rode o instalador de novo'
$env:GIT_TERMINAL_PROMPT = '0'; $env:GCM_INTERACTIVE = 'never'
git -C $claude fetch -q origin 2>$null
Item 'acesso ao cofre das skills no GitHub' ($LASTEXITCODE -eq 0) "abra o PowerShell e rode: git -C `"$claude`" fetch  (entre com a conta equipelegacyexecutoria-ai)"
$st = git -C $claude status -sb 2>$null | Select-Object -First 1
Item "skills em dia com o cofre ($st)" ($st -notmatch 'behind|ahead') 'abra uma conversa nova no Claude (sincroniza sozinho)'
$n = @(Get-ChildItem (Join-Path $claude 'skills') -Directory | Where-Object { $_.Name -ne 'synced' -and (Test-Path (Join-Path $_.FullName 'SKILL.md')) }).Count
Item "$n skills no PC" ($n -ge 7) 'faltam skills: rode o instalador de novo'
$set = Get-Content -Raw (Join-Path $claude 'settings.json') -ErrorAction SilentlyContinue
Item 'sincronia ligada no app (abrir e terminar conversa)' ($set -match 'sync\.ps1.{0,3}-Modo inicio' -and $set -match 'sync\.ps1.{0,3}-Modo fim') 'rode sync\mesclar-hooks.ps1'

if ($papel -eq 'render' -or (Test-Path (Join-Path $env:LOCALAPPDATA 'corte-viral\venv'))) {
  Write-Host ''; Write-Host 'Vídeo:'
  Item 'ffmpeg' ([bool](Get-Command ffmpeg -ErrorAction SilentlyContinue)) 'rode o instalador de novo'
  Item 'placa NVIDIA' ([bool](Get-Command nvidia-smi -ErrorAction SilentlyContinue)) 'atualize o driver pelo NVIDIA App (sem placa funciona, mas lento)'
  $livre = [math]::Round((Get-PSDrive C).Free / 1GB)
  Item "espaço livre no C: ($livre GB)" ($livre -ge 30) 'libere espaço: cada edição usa uns 10 GB temporários'
  $py = Join-Path $env:LOCALAPPDATA 'corte-viral\venv\Scripts\python.exe'
  $env:PYTHONUTF8 = '1'
  if (Test-Path $py) {
    Write-Host ''; Write-Host 'Conferência da skill Novela:'
    & $py (Join-Path $claude 'skills\reels-novela-clailton\scripts\verificar.py')
    if ($LASTEXITCODE -ne 0) { $falhas++ }
    Write-Host ''; Write-Host 'Conferência da skill Tela Dividida:'
    & $py (Join-Path $claude 'skills\reels-tela-dividida-clailton\scripts\verificar_td.py')
    if ($LASTEXITCODE -ne 0) { $falhas++ }
  } else { Item 'ambiente Python de vídeo' $false 'rode o instalador de novo' }
}

Write-Host ''
if ($falhas -eq 0) { Write-Host 'TUDO PRONTO NESTE PC.' -ForegroundColor Green }
else { Write-Host "FALTAM $falhas ITEM(NS). Tire um print desta janela e mande para quem cuida da Central de Render." -ForegroundColor Red }
