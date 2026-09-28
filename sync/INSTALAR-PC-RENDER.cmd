@echo off
title Instalador - PC de render (Legacy)
echo.
echo  Instalador do PC de render. Nao feche esta janela.
echo  Se o Windows perguntar "Deseja permitir...", clique em SIM.
echo  Quando o navegador abrir pedindo login no GitHub, entre com a conta
echo  equipelegacyexecutoria-ai e clique em Authorize.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -Command "$s=[IO.File]::ReadAllText('%~f0'); $i=$s.LastIndexOf('#PS'+'START'); Invoke-Expression $s.Substring($i)"
echo.
pause
exit /b

#PSSTART
$ErrorActionPreference = 'Stop'
$Papel = 'render'
$repo = 'https://equipelegacyexecutoria-ai@github.com/equipelegacyexecutoria-ai/claude-skills.git'
$claude = Join-Path $HOME '.claude'
function Passo($t) { Write-Host ''; Write-Host "==> $t" -ForegroundColor Cyan }
function AtualizaPath { $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User') }
try {
  Passo 'A Git'
  if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) { throw "winget nao existe: atualize o 'Instalador de Aplicativo' na Microsoft Store e rode de novo." }
    winget install -e --id Git.Git --accept-package-agreements --accept-source-agreements --silent
    AtualizaPath
  }
  git --version
  if ($LASTEXITCODE -ne 0) { throw 'o Git nao apareceu. Feche esta janela e abra o instalador de novo.' }

  Passo 'B Baixando as skills do cofre (o navegador pode abrir pedindo login no GitHub)'
  New-Item -ItemType Directory -Force $claude | Out-Null
  if (-not (Test-Path (Join-Path $claude '.git'))) {
    $bak = Join-Path $HOME ('.claude-antes-da-sincronia-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
    $mover = @('skills', 'agents', 'hooks', 'CLAUDE.md') | Where-Object { Test-Path (Join-Path $claude $_) }
    if ($mover) {
      New-Item -ItemType Directory -Force $bak | Out-Null
      foreach ($m in $mover) { if ($m -eq 'skills') { New-Item -ItemType Directory -Force (Join-Path $bak 'skills') | Out-Null; Get-ChildItem (Join-Path $claude 'skills') | Where-Object { $_.Name -ne 'synced' } | Move-Item -Destination (Join-Path $bak 'skills') } else { Move-Item (Join-Path $claude $m) $bak } }
      Write-Host "   o que ja existia foi guardado em $bak"
    }
    git -C $claude init -q -b main
    git -C $claude remote add origin $repo
  }
  git -C $claude config core.quotepath false
  git -C $claude config credential.https://github.com.username equipelegacyexecutoria-ai
  git -C $claude config user.name $env:COMPUTERNAME
  git -C $claude config user.email equipelegacyexecutoria@gmail.com
  git -C $claude fetch origin
  if ($LASTEXITCODE -ne 0) { throw 'nao consegui acessar o cofre. Confira o login do GitHub (conta equipelegacyexecutoria-ai) e rode de novo.' }
  git -C $claude checkout -q -f -B main origin/main
  git -C $claude branch -q --set-upstream-to=origin/main main
  Write-Host '   skills baixadas' -ForegroundColor Green

  Passo 'C Preparando o PC (programas de video e modelos: pode levar de 30 a 60 minutos)'
  & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $claude 'sync\instalar-maquina.ps1') -Papel $Papel
} catch {
  Write-Host ''
  Write-Host "ERRO: $($_.Exception.Message)" -ForegroundColor Red
  Write-Host 'Tire um print desta janela e mande. Depois e so abrir o instalador de novo: ele retoma.' -ForegroundColor Red
}
