# Prepara este PC depois que o cofre das skills já está em ~/.claude (o INSTALAR-PC-*.cmd faz essa parte).
#   -Papel render  : PC de render (instala tudo de vídeo)
#   -Papel estacao : PC de quem usa o Claude (-Video para instalar também as ferramentas de vídeo)
# Pode rodar de novo quantas vezes quiser: retoma de onde parou.
# Rodar FORA do app do Claude (dois cliques no .cmd ou janela normal do PowerShell).
param([ValidateSet('render', 'estacao')][string]$Papel = 'estacao', [switch]$Video)

$ErrorActionPreference = 'Stop'
$claude = Join-Path $HOME '.claude'
$skills = Join-Path $claude 'skills'
if ($Papel -eq 'render') { $Video = $true }

function Passo($t) { Write-Host ''; Write-Host "==> $t" -ForegroundColor Cyan }
function Ok($t) { Write-Host "   ok: $t" -ForegroundColor Green }
function Alerta($t) { Write-Host "   atenção: $t" -ForegroundColor Yellow }
function TemComando($n) { return [bool](Get-Command $n -ErrorAction SilentlyContinue) }
function AtualizaPath { $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User') }
function Confere($msg) { if ($LASTEXITCODE -ne 0) { throw $msg } }
function Winget($id) {
  if (-not (TemComando winget)) { throw "o winget não existe neste PC: atualize o 'Instalador de Aplicativo' na Microsoft Store e rode de novo." }
  winget install -e --id $id --accept-package-agreements --accept-source-agreements --silent
  AtualizaPath
}

try {
  Passo "1 Papel deste PC: $Papel"
  $maq = Join-Path $claude 'maquina.json'
  $dados = [ordered]@{ papel = $Papel; pc = $env:COMPUTERNAME }
  if (Test-Path $maq) { try { $v = Get-Content -Raw -Encoding UTF8 $maq | ConvertFrom-Json; if ($v.roteirista) { $dados.roteirista = $v.roteirista } } catch {} }
  [IO.File]::WriteAllText($maq, ($dados | ConvertTo-Json), (New-Object Text.UTF8Encoding $false))
  Ok $maq

  Passo '2 Ligando a sincronia automática no app do Claude'
  & (Join-Path $PSScriptRoot 'mesclar-hooks.ps1')

  if ($Video) {
    $base = Join-Path $env:LOCALAPPDATA 'corte-viral'
    $venv = Join-Path $base 'venv'
    $py = Join-Path $venv 'Scripts\python.exe'
    $venvAl = Join-Path $env:LOCALAPPDATA 'reels-novela\venv-align'
    $pyAl = Join-Path $venvAl 'Scripts\python.exe'
    $novela = Join-Path $skills 'reels-novela-clailton'
    $env:PYTHONUTF8 = '1'
    $env:HF_HUB_DISABLE_SYMLINKS_WARNING = '1'

    Passo '3 Programas: Python 3.12, ffmpeg e Node'
    $temPy = $false
    try { & py -3.12 --version | Out-Null; if ($LASTEXITCODE -eq 0) { $temPy = $true } } catch {}
    if (-not $temPy) { Winget 'Python.Python.3.12' }
    & py -3.12 --version; Confere 'Python 3.12 não apareceu. Feche esta janela e rode o instalador de novo.'
    if (-not (TemComando ffmpeg)) { Winget 'Gyan.FFmpeg' }
    & ffmpeg -hide_banner -version | Select-Object -First 1
    if (-not (TemComando node)) { Winget 'OpenJS.NodeJS.LTS' }
    if (TemComando nvidia-smi) { Ok ((& nvidia-smi --query-gpu=name,driver_version --format=csv,noheader) -join ' ') } else { Alerta 'placa NVIDIA não encontrada: vai funcionar, só que bem mais devagar' }

    Passo "4 Ambiente principal de vídeo ($venv) — ~2 GB"
    if (-not (Test-Path $py)) { New-Item -ItemType Directory -Force $base | Out-Null; & py -3.12 -m venv $venv; Confere "falha ao criar $venv" }
    & $py -m pip install -q --upgrade pip
    & $py -m pip install -r (Join-Path $novela 'requirements.txt'); Confere 'falha ao instalar as bibliotecas do ambiente principal'

    Passo "5 Alinhador de palavras + CLIP ($venvAl) — ~5 GB"
    if (-not (Test-Path $pyAl)) { New-Item -ItemType Directory -Force (Split-Path $venvAl) | Out-Null; & py -3.12 -m venv $venvAl; Confere "falha ao criar $venvAl" }
    & $pyAl -m pip install -q --upgrade pip
    & $pyAl -m pip install -r (Join-Path $novela 'requirements-alinhador.txt'); Confere 'falha ao instalar o WhisperX'
    # o whisperx traz o torch de CPU; troca pelo de CUDA 12.8 (placas RTX 50 precisam dele)
    & $pyAl -m pip install --no-deps --force-reinstall torch==2.8.0 torchaudio==2.8.0 torchvision==0.23.0 --index-url https://download.pytorch.org/whl/cu128
    Confere 'falha ao instalar o PyTorch CUDA'

    Passo '6 Baixando os modelos (Whisper, alinhador português, CLIP, detectores) — ~5 GB, uma vez só'
    & $py -c "from faster_whisper import WhisperModel; WhisperModel('large-v3-turbo', device='cpu', compute_type='int8'); print('Whisper ok')"; Confere 'falha ao baixar o Whisper'
    & $pyAl -c "import whisperx; whisperx.load_align_model(language_code='pt', device='cpu'); print('alinhador ok')"; Confere 'falha ao baixar o alinhador'
    & $pyAl -c "from transformers import CLIPModel, CLIPProcessor; CLIPModel.from_pretrained('openai/clip-vit-large-patch14', use_safetensors=True); CLIPProcessor.from_pretrained('openai/clip-vit-large-patch14'); print('CLIP ok')"; Confere 'falha ao baixar o CLIP'
    $td = Join-Path $skills 'reels-tela-dividida-clailton\models'
    New-Item -ItemType Directory -Force $td | Out-Null
    $baixar = @{
      'watermark_model_v1.pt'                 = 'https://github.com/LAION-AI/LAION-5B-WatermarkDetection/raw/main/models/watermark_model_v1.pt'
      'text_detection_en_ppocrv3_2023may.onnx' = 'https://github.com/opencv/opencv_zoo/raw/main/models/text_detection_ppocr/text_detection_en_ppocrv3_2023may.onnx'
    }
    $ProgressPreference = 'SilentlyContinue'
    foreach ($n in $baixar.Keys) { $d = Join-Path $td $n; if (-not (Test-Path $d)) { Invoke-WebRequest -UseBasicParsing $baixar[$n] -OutFile $d } }
    Ok 'modelos'
  }

  Passo 'Conferência final'
  & (Join-Path $PSScriptRoot 'verificar-maquina.ps1')
} catch {
  Write-Host ''
  Write-Host "ERRO: $($_.Exception.Message)" -ForegroundColor Red
  Write-Host 'Tire um print desta janela e mande para quem cuida da Central de Render. Depois é só rodar de novo: ele retoma de onde parou.' -ForegroundColor Red
  exit 1
}
