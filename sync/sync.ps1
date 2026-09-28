# Sincronia das skills entre os PCs (cofre privado no GitHub).
#   -Modo inicio : ao abrir a conversa. Recebe novidades e avisa em uma linha "SYNC: ...".
#   -Modo fim    : ao fim de cada resposta, em segundo plano. Envia o que mudou.
#   -Modo agora  : manual ("sincroniza agora") e antes de cada pedido do PC de render.
# Nunca pede nada na tela, nunca apaga trabalho: conflito vira o ramo conflito/<PC>.
# Compatível com PowerShell 5.1. Saída só em ASCII. Gravado em UTF-8 com BOM.
param([ValidateSet('inicio', 'fim', 'agora')][string]$Modo = 'agora')

$ErrorActionPreference = 'Continue'
$env:GIT_TERMINAL_PROMPT = '0'
$env:GCM_INTERACTIVE = 'never'
$env:GIT_ASKPASS = ''
$PC = $env:COMPUTERNAME
$claude = Join-Path $HOME '.claude'
$local = Join-Path $claude 'sync-local'
if (-not (Test-Path $local)) { New-Item -ItemType Directory -Force $local | Out-Null }
$logArq = Join-Path $local 'sync.log'
$avisos = New-Object Collections.Generic.List[string]

function Log([string]$t) {
  try { Add-Content -Path $logArq -Value ("{0:yyyy-MM-dd HH:mm:ss} [{1}] {2}" -f (Get-Date), $Modo, $t) -Encoding UTF8 } catch {}
}
function Ascii([string]$t) {
  $n = $t.Normalize([Text.NormalizationForm]::FormD)
  return (-join ($n.ToCharArray() | Where-Object { [int]$_ -lt 128 }))
}
function Aviso([string]$t) { $avisos.Add((Ascii $t)); Log $t }

# git com prazo máximo; devolve @{code; out; err}
function G([string[]]$a, [int]$seg = 60) {
  $psi = New-Object Diagnostics.ProcessStartInfo 'git'
  $psi.Arguments = ($a | ForEach-Object { if ($_ -match '[\s"]') { '"' + ($_ -replace '"', '\"') + '"' } else { $_ } }) -join ' '
  $psi.WorkingDirectory = $script:repo
  $psi.UseShellExecute = $false
  $psi.RedirectStandardOutput = $true
  $psi.RedirectStandardError = $true
  $psi.CreateNoWindow = $true
  $psi.StandardOutputEncoding = [Text.Encoding]::UTF8
  $psi.StandardErrorEncoding = [Text.Encoding]::UTF8
  $p = [Diagnostics.Process]::Start($psi)
  $o = $p.StandardOutput.ReadToEndAsync()
  $e = $p.StandardError.ReadToEndAsync()
  if (-not $p.WaitForExit($seg * 1000)) {
    try { $p.Kill() } catch {}
    return @{ code = -1; out = ''; err = 'timeout' }
  }
  $p.WaitForExit()
  return @{ code = $p.ExitCode; out = $o.Result.TrimEnd(); err = $e.Result.TrimEnd() }
}
function Linhas([string]$t) { if ($t) { return @($t -split "`r?`n" | Where-Object { $_ -ne '' }) } else { return @() } }

function ProblemaDeRede($r) {
  if ($r.code -eq -1) { return 'OFFLINE' }
  if ($r.err -match 'Authentication|could not read Username|terminal prompts disabled|403|401|credential') { return 'LOGIN' }
  if ($r.err -match 'Could not resolve host|unable to access|Failed to connect|timed out') { return 'OFFLINE' }
  return $null
}

# Resumo curto de caminhos: skills/x, agents/y
function Resumo([string[]]$arqs) {
  $grupos = $arqs | ForEach-Object {
    $p = $_ -split '/'
    if ($p.Count -ge 2 -and $p[0] -in @('skills', 'agents', 'sync', 'hooks')) { if ($p[0] -eq 'agents') { 'agents/' + ($p[1] -replace '\.md$', '') } else { $p[0] + '/' + $p[1] } } else { $p[0] }
  } | Select-Object -Unique
  $lista = @($grupos)
  if ($lista.Count -gt 6) { return (($lista[0..5] -join ', ') + " e mais $($lista.Count - 6)") }
  return ($lista -join ', ')
}

# ---------- trava: uma sincronia por vez ----------
$travaArq = Join-Path $local 'trava'
try {
  $trava = [IO.File]::Open($travaArq, 'OpenOrCreate', 'ReadWrite', 'None')
} catch {
  if ($Modo -eq 'fim') { exit 0 }
  Start-Sleep -Seconds 5
  try { $trava = [IO.File]::Open($travaArq, 'OpenOrCreate', 'ReadWrite', 'None') } catch { Log 'trava ocupada'; exit 0 }
}

function Sincronizar([string]$repoDir, [string]$nome) {
  $script:repo = $repoDir
  $gitDir = Join-Path $repoDir '.git'
  if (-not (Test-Path $gitDir)) { return }

  $lock = Join-Path $gitDir 'index.lock'
  if ((Test-Path $lock) -and ((Get-Item $lock).LastWriteTime -lt (Get-Date).AddMinutes(-10))) { Remove-Item $lock -Force; Log "index.lock antigo removido em $nome" }
  if (Test-Path (Join-Path $gitDir 'MERGE_HEAD')) { Aviso "$nome tem uma juncao pela metade; peca ao Claude para resolver (LEIA-ME, secao Conflito)"; return }

  $ramo = (G @('rev-parse', '--abbrev-ref', 'HEAD')).out
  if ($ramo -ne 'main') { Aviso "$nome esta no ramo '$ramo', nao no main; sincronia pulada"; return }

  # 1. Proteções antes de gravar
  $apagados = Linhas (G @('ls-files', '--deleted')).out
  $skillMd = @($apagados | Where-Object { $_ -match '(^|/)SKILL\.md$' })
  if ($apagados.Count -gt 5 -or $skillMd.Count -gt 0) {
    G @('checkout', '--', '.') | Out-Null
    Aviso "$nome : $($apagados.Count) arquivo(s) apagado(s) fora do Claude foram restaurados ($(Resumo $apagados)). Para apagar de verdade, peca ao Claude (git rm)."
  }
  G @('add', '-A') | Out-Null
  $staged = Linhas (G @('diff', '--cached', '--name-only', '--diff-filter=AM')).out
  foreach ($f in $staged) {
    $full = Join-Path $repoDir $f
    if ((Test-Path $full) -and ((Get-Item $full).Length -gt 10MB)) {
      G @('reset', '-q', '--', $f) | Out-Null
      Add-Content -Path (Join-Path $gitDir 'info\exclude') -Value ('/' + $f) -Encoding UTF8
      Aviso "$nome : '$f' tem mais de 10 MB e ficou fora da sincronia."
    }
  }
  $padrao = 'ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-ant-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|EAA[A-Za-z0-9]{40,}|IGQV[A-Za-z0-9_-]{40,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|(password|senha|token|api_key|apikey)\s*[:=]\s*["''][^"''\s]{12,}'
  foreach ($f in (Linhas (G @('diff', '--cached', '--name-only', '--diff-filter=AM')).out)) {
    $d = (G @('diff', '--cached', '-U0', '--', $f)).out
    $novas = (Linhas $d | Where-Object { $_ -match '^\+' -and $_ -notmatch '^\+\+\+' }) -join "`n"
    if ($novas -match $padrao) {
      G @('reset', '-q', '--', $f) | Out-Null
      Aviso "$nome : '$f' parece ter senha ou chave e NAO foi enviado. Tire o segredo do arquivo."
    }
  }

  # 2. Commit
  $mudou = Linhas (G @('diff', '--cached', '--name-only')).out
  $commitNovo = $false
  if ($mudou.Count -gt 0) {
    $r = G @('commit', '-q', '-m', "auto($PC): $(Resumo $mudou)")
    if ($r.code -eq 0) { $commitNovo = $true; Log "commit: $(Resumo $mudou)" } else { Log "commit falhou: $($r.err)" }
  }

  # 3. Buscar novidades
  $marca = Join-Path $local "ultimo-fetch-$nome"
  $precisaFetch = ($Modo -ne 'fim') -or $commitNovo -or (-not (Test-Path $marca)) -or ((Get-Item $marca).LastWriteTime -lt (Get-Date).AddMinutes(-5))
  $antes = (G @('rev-parse', 'HEAD')).out
  if ($precisaFetch) {
    $r = G @('fetch', '-q', '--prune', 'origin') $(if ($Modo -eq 'fim') { 60 } else { 15 })
    $prob = ProblemaDeRede $r
    if ($prob) {
      if ($Modo -ne 'fim') { Aviso $(if ($prob -eq 'LOGIN') { "LOGIN: o GitHub pediu login de novo neste PC. Rode ~/.claude/sync/INSTALAR-MAQUINA.cmd ou peca ao Claude (LEIA-ME, secao Login)." } else { "OFFLINE: sem internet agora; as mudancas deste PC seguem quando a rede voltar." }) }
      Log "fetch: $prob $($r.err)"
      return
    }
    if ($r.code -ne 0) { Log "fetch falhou: $($r.err)"; return }
    Set-Content -Path $marca -Value (Get-Date -Format o)
  }

  # 4/5. Juntar com o que veio de fora
  $atras = [int](G @('rev-list', '--count', 'HEAD..origin/main')).out
  $frente = [int](G @('rev-list', '--count', 'origin/main..HEAD')).out
  if ($atras -gt 0 -and $frente -eq 0) {
    G @('merge', '-q', '--ff-only', 'origin/main') | Out-Null
  } elseif ($atras -gt 0 -and $frente -gt 0) {
    $r = G @('merge', '-q', '--no-edit', 'origin/main')
    if ($r.code -ne 0) {
      G @('merge', '--abort') | Out-Null
      G @('push', '-q', '--force', 'origin', "HEAD:refs/heads/conflito/$PC") 60 | Out-Null
      Aviso "CONFLITO: este PC e outro mudaram o mesmo trecho. A versao deste PC continua aqui e esta guardada em conflito/$PC. Pergunte ao usuario se pode juntar as duas (LEIA-ME, secao Conflito)."
      return
    }
  }

  # 6. Enviar
  $frente = [int](G @('rev-list', '--count', 'origin/main..HEAD')).out
  if ($frente -gt 0) {
    $r = G @('push', '-q', 'origin', 'HEAD:main') 60
    if ($r.code -ne 0) {
      G @('fetch', '-q', 'origin') 30 | Out-Null
      $m = G @('merge', '-q', '--no-edit', 'origin/main')
      if ($m.code -eq 0) { $r = G @('push', '-q', 'origin', 'HEAD:main') 60 } else { G @('merge', '--abort') | Out-Null }
      if ($r.code -ne 0) { Log "push falhou: $($r.err)" }
    }
  }

  # 7. Ramo de conflito deste PC já resolvido: apagar
  $meu = "origin/conflito/$PC"
  if ((G @('rev-parse', '-q', '--verify', $meu)).code -eq 0 -and (G @('merge-base', '--is-ancestor', $meu, 'HEAD')).code -eq 0) {
    G @('push', '-q', 'origin', '--delete', "conflito/$PC") 30 | Out-Null
  }

  # Avisos da abertura
  if ($Modo -ne 'fim') {
    $depois = (G @('rev-parse', 'HEAD')).out
    if ($antes -and $depois -ne $antes) {
      $recebidos = Linhas (G @('diff', '--name-only', $antes, $depois)).out
      $autores = (Linhas (G @('log', '--format=%s', "$antes..$depois")).out | ForEach-Object { if ($_ -match '^auto\(([^)]+)\)') { $Matches[1] } } | Where-Object { $_ -ne $PC } | Select-Object -Unique) -join ', '
      if ($recebidos.Count -gt 0) { Aviso ("recebido" + $(if ($autores) { " de $autores" } else { '' }) + ": $(Resumo $recebidos)") }
      $novas = Linhas (G @('diff', '--name-only', '--diff-filter=A', $antes, $depois, '--', 'skills/*/SKILL.md', 'agents/*.md')).out
      if ($novas.Count -gt 0) { Aviso "skill ou agente novo chegou: rode /reload-skills ou abra uma conversa nova." }
      if ($recebidos -contains 'sync/hooks.json') { Aviso "hooks.json mudou: rode sync/mesclar-hooks.ps1 (LEIA-ME)." }
    }
    $outros = Linhas (G @('branch', '-r', '--list', 'origin/conflito/*')).out | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne $meu }
    foreach ($o in $outros) { Aviso "CONFLITO pendente de outro PC em $o : pergunte ao usuario se pode juntar (LEIA-ME, secao Conflito)." }
  }
}

try {
  Sincronizar $claude 'skills'
  $maq = Join-Path $claude 'maquina.json'
  $rot = $null
  if (Test-Path $maq) { try { $rot = (Get-Content -Raw -Encoding UTF8 $maq | ConvertFrom-Json).roteirista } catch {} }
  if (-not $rot) { $rot = Join-Path ([Environment]::GetFolderPath('Desktop')) 'Projetos Edições\Roteirista de Reels' }
  if (Test-Path (Join-Path $rot '.git')) { Sincronizar $rot 'roteirista' }
} catch {
  Log "erro: $($_.Exception.Message)"
} finally {
  if ($trava) { $trava.Dispose() }
}

if ($Modo -ne 'fim' -and $avisos.Count -gt 0) {
  foreach ($a in $avisos) { Write-Output "SYNC: $a" }
}
exit 0
