<#
.SYNOPSIS
  Importa um novo período de reels para dados/reels_base.json (modo mensal do Analista de Performance).

.DESCRIPTION
  Etapa "normalizar" (padrão): lê a entrada e grava um lote em dados/lotes/.
    Entradas aceitas:
      .json  mesmo esquema do reels_base.json (objeto com "reels" ou lista de reels)
      .csv   export do JARVIS (separador ;, colunas perfil;data;tipo;link;views;curtidas;comentarios;
             compartilhamentos;salvamentos;reposts;alcance;duracao_s;...;legenda;transcricao;texto_na_tela)
      .docx  export do JARVIS (1 bloco por post: título, Link, tabela de métricas, Legenda, Transcrição, Texto na tela)
    Só entram Reel e Vídeo. Reels que já estão na base (mesmo código do link) viram "atualizacoes" (só métricas);
    os outros viram "novos", com os campos de julgamento marcados "PENDENTE" para o Analista preencher:
    hook.tipo, hook.ressalva_nos_primeiros_segundos, tema, cta_falado, marcadores_de_estrutura.tem_historia_ou_caso,
    formato_visual (novela | tela_dividida | outro), tela_com_imagens (só tela), origem (roteirizado | corte).

  Etapa "mesclar": recusa o lote se sobrou PENDENTE; faz backup da base em dados/backups/; atualiza métricas dos
  existentes; acrescenta os novos com id sequencial; recalcula taxas, maturidade (< 3 dias da extração = recente),
  mediana de views de cada mês (todos os reels do mês, como no estudo original) e lift (views ÷ mediana do mês).
  Depois rode gerar-corpus.ps1 e stats-formatos.ps1.

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File importar-mes.ps1 -Entrada "C:\...\instagram-clailtonluiz-2026-09-26_2026-10-25.csv"
  powershell -NoProfile -ExecutionPolicy Bypass -File importar-mes.ps1 -Etapa mesclar -Lote dados\lotes\2026-10-26-instagram-clailtonluiz-2026-09-26_2026-10-25.json
#>
param(
  [string]$Entrada,
  [ValidateSet('normalizar', 'mesclar')][string]$Etapa = 'normalizar',
  [string]$Lote,
  [string]$Base,
  [string]$DataExtracao,
  [string]$SaidaLote
)

$ErrorActionPreference = 'Stop'
$pt = [Globalization.CultureInfo]'pt-BR'
$raizArq = Join-Path $PSScriptRoot 'raiz-do-projeto.txt'
$root = if (Test-Path $raizArq) { (Get-Content -Raw -Encoding UTF8 $raizArq).Trim() } else { Split-Path (Split-Path (Split-Path (Split-Path $PSScriptRoot))) }
if (-not $Base) { $Base = Join-Path $root 'dados\reels_base.json' }
$utf8 = New-Object Text.UTF8Encoding $false
function Abs([string]$p) { if (-not $p) { return $p }; if ([IO.Path]::IsPathRooted($p)) { return $p }; return (Join-Path $root $p) }

function Codigo([string]$link) { $m = [regex]::Match([string]$link, '/(reel|reels|p|tv)/([^/?#]+)'); if ($m.Success) { return $m.Groups[2].Value } else { return [string]$link } }
function Num($s) {
  if ($s -eq $null) { return $null }
  $s = ([string]$s).Trim()
  if ($s -eq '' -or $s -match '^[—–-]$') { return $null }
  $d = $s -replace '[^\d]', ''
  if ($d -eq '') { return $null }
  return [int64]$d
}
function Palavras([string]$t) { if (-not $t) { return @() }; return @(($t.ToLower() -replace '[^\p{L}\p{N}\s]', ' ') -split '\s+' | Where-Object { $_ }) }
function Cnt([string]$t, [string]$pat) { if (-not $t) { return 0 }; return ([regex]::Matches($t, $pat)).Count }
function ParseData([string]$s) { return [datetime]::ParseExact($s.Substring(0, 16), 'dd/MM/yyyy HH:mm', $pt) }
function DiaSemana([string]$s) {
  $nomes = @('domingo', 'segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado')
  return $nomes[[int](ParseData $s).DayOfWeek]
}
function Med($a) {
  $s = @($a | Where-Object { $_ -ne $null } | Sort-Object)
  if ($s.Count -eq 0) { return $null }
  $m = [math]::Floor($s.Count / 2)
  if ($s.Count % 2) { return [double]$s[$m] } else { return ([double]$s[$m - 1] + [double]$s[$m]) / 2 }
}
$FALLBACK = '^(\(sem legenda\)|Sem fala no vídeo\.|Não foi possível transcrever.*|Transcrição não solicitada.*|Transcrição interrompida.*|Nenhum texto.*|Arquivo indisponível.*)$'

function NovoReel([string]$link, [string]$data, $dur, [hashtable]$m, [string]$leg, [string]$trans, [string]$tela, [string]$obs) {
  $trans = ([string]$trans).Trim(); $leg = ([string]$leg).Trim(); $tela = ([string]$tela).Trim()
  if ($trans -match $FALLBACK) { $obs = (@($obs, $trans) | Where-Object { $_ }) -join ' · '; $trans = '' }
  if ($leg -match $FALLBACK) { $leg = '' }
  $frases = @([regex]::Split($trans, '(?<=[\.\!\?])\s+') | Where-Object { $_.Trim() })
  $f1 = if ($frases.Count) { $frases[0].Trim() } else { '' }
  $nw = (Palavras $trans).Count
  $wps = if ($dur -and $nw) { [math]::Round($nw / [double]$dur, 2) } else { $null }
  $p1 = (Palavras $f1).Count
  [pscustomobject]@{
    id = $null; link = $link; data_hora = $data; dia_semana = (DiaSemana $data); duracao_s = $dur; maturidade = 'PENDENTE_CALCULO'
    metricas = [pscustomobject]@{
      views = $m['views']; curtidas = $m['curtidas']; comentarios = $m['comentarios']; compartilhamentos = $m['compartilhamentos']
      salvamentos = $m['salvamentos']; reposts = $m['reposts']; alcance = $m['alcance']
      taxa_curtida_pct = $null; taxa_comentario_pct = $null; taxa_repost_pct = $null; views_vs_mediana_do_mes = $null
    }
    hook = [pscustomobject]@{
      frase_1 = $f1; duas_primeiras_frases = (($frases | Select-Object -First 2) -join ' ').Trim(); palavras_frase_1 = $p1
      segundos_estimados_frase_1 = $(if ($wps) { [math]::Round($p1 / $wps, 1) } else { $null }); tipo = 'PENDENTE'
      flags = [pscustomobject]@{
        talvez_ou_pode_ser_no_hook = ($f1 -match '(?i)\btalvez\b|\bpode ser\b'); segunda_pessoa = ($f1 -match '(?i)\b(você|teu|tua|seu|sua|te)\b')
        pergunta = ($f1.TrimEnd().EndsWith('?')); numero_no_hook = ($f1 -match '\d'); palavra_de_alto_impacto = @()
        comeca_no_meio_da_fala = ($f1 -cmatch '^(E |e |[a-zà-ú])')
      }
      ressalva_nos_primeiros_segundos = 'PENDENTE'
    }
    fecho = [pscustomobject]@{ ultimas_frases = (($frases | Select-Object -Last 2) -join ' ').Trim(); termina_com_pergunta = ($trans.TrimEnd().EndsWith('?')) }
    cta_falado = @('PENDENTE')
    tema = 'PENDENTE'
    marcadores_de_estrutura = [pscustomobject]@{
      tem_historia_ou_caso = 'PENDENTE'; tem_numeros = ($trans -match '\d'); palavras_por_segundo = $wps
      qtd_talvez = (Cnt $trans '(?i)\btalvez\b'); qtd_preste_atencao = (Cnt $trans '(?i)prest[ea] atenção'); qtd_olha_so = (Cnt $trans '(?i)olha só')
    }
    copy_original = [pscustomobject]@{ transcricao_falada = $trans; texto_na_tela = $tela; legenda = $leg }
    observacoes_da_fonte = $obs
    analise_aprofundada = $null
    formato_visual = 'PENDENTE'; tela_com_imagens = $null; origem = 'PENDENTE'; impulsionado = $null
  }
}

function ParText($node, $ns) {
  $sb = New-Object Text.StringBuilder
  foreach ($n in $node.SelectNodes('.//w:t | .//w:br | .//w:tab', $ns)) {
    switch ($n.LocalName) { 't' { [void]$sb.Append($n.InnerText) } 'br' { [void]$sb.Append("`n") } 'tab' { [void]$sb.Append("`t") } }
  }
  return $sb.ToString()
}
function LerDocx([string]$path) {
  Add-Type -AssemblyName System.IO.Compression.FileSystem
  $zip = [IO.Compression.ZipFile]::OpenRead($path)
  try {
    $sr = New-Object IO.StreamReader(($zip.GetEntry('word/document.xml')).Open(), [Text.Encoding]::UTF8)
    $xmlText = $sr.ReadToEnd(); $sr.Close()
  } finally { $zip.Dispose() }
  [xml]$x = $xmlText
  $ns = New-Object Xml.XmlNamespaceManager($x.NameTable)
  $ns.AddNamespace('w', 'http://schemas.openxmlformats.org/wordprocessingml/2006/main')
  $posts = New-Object Collections.Generic.List[hashtable]
  $cur = $null; $campo = $null
  foreach ($node in $x.SelectSingleNode('//w:body', $ns).ChildNodes) {
    if ($node.LocalName -eq 'tbl') {
      if ($cur) {
        $rows = @($node.SelectNodes('w:tr', $ns))
        if ($rows.Count -ge 2) {
          $h = @($rows[0].SelectNodes('w:tc', $ns) | ForEach-Object { (ParText $_ $ns).Trim() })
          $v = @($rows[1].SelectNodes('w:tc', $ns) | ForEach-Object { (ParText $_ $ns).Trim() })
          for ($k = 0; $k -lt $h.Count; $k++) { $cur.met[$h[$k]] = $v[$k] }
        }
      }
      continue
    }
    if ($node.LocalName -ne 'p') { continue }
    $st = $node.SelectSingleNode('w:pPr/w:pStyle/@w:val', $ns)
    $t = (ParText $node $ns).Trim()
    if ($st -and $st.Value -eq 'Heading2') {
      if ($cur) { $posts.Add($cur) }
      $cur = @{ tipo = ''; data = ''; dur = $null; link = ''; met = @{}; legenda = ''; transcricao = ''; texto_na_tela = ''; obs = '' }
      $m = [regex]::Match($t, '^\s*\d+\.\s*([^·]+?)\s*·\s*(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2})(?:\s*·\s*(\d+)\s*s)?')
      if ($m.Success) { $cur.tipo = $m.Groups[1].Value.Trim(); $cur.data = $m.Groups[2].Value; if ($m.Groups[3].Success) { $cur.dur = [int]$m.Groups[3].Value } }
      $campo = $null; continue
    }
    if (-not $cur -or $t -eq '') { continue }
    if ($t -match '^Link:\s*(\S+)') { $cur.link = $Matches[1]; continue }
    if ($t -match '^legenda$') { $campo = 'legenda'; continue }
    if ($t -match '^(transcrição|copy dos slides|texto da imagem)\b') { $campo = 'transcricao'; continue }
    if ($t -match '^texto na tela$') { $campo = 'texto_na_tela'; continue }
    if ($t -match '^Observações:\s*(.*)$') { $cur.obs = $Matches[1]; $campo = $null; continue }
    if ($campo) { if ($cur[$campo]) { $cur[$campo] += "`n" + $t } else { $cur[$campo] = $t } }
  }
  if ($cur) { $posts.Add($cur) }
  return $posts
}

# =====================================================================
if ($Etapa -eq 'normalizar') {
  if (-not $Entrada) { throw 'Informe -Entrada (json, csv ou docx).' }
  $Entrada = Abs $Entrada
  $ext = [IO.Path]::GetExtension($Entrada).ToLower()
  $dataExt = if ($DataExtracao) { [datetime]::ParseExact($DataExtracao, 'dd/MM/yyyy', $pt) } else { (Get-Item $Entrada).LastWriteTime }
  $b = Get-Content -Raw -Encoding UTF8 $Base | ConvertFrom-Json
  $naBase = @{}; foreach ($r in $b.reels) { $naBase[(Codigo $r.link)] = $true }

  $itens = New-Object Collections.Generic.List[object]
  switch ($ext) {
    '.json' {
      $in = Get-Content -Raw -Encoding UTF8 $Entrada | ConvertFrom-Json
      $lista = if ($in.reels) { $in.reels } else { $in }
      foreach ($r in $lista) {
        if (-not $r.formato_visual) { $r | Add-Member -NotePropertyName formato_visual -NotePropertyValue 'PENDENTE' -Force }
        if (-not ($r.PSObject.Properties.Name -contains 'tela_com_imagens')) { $r | Add-Member -NotePropertyName tela_com_imagens -NotePropertyValue $null -Force }
        if (-not $r.origem) { $r | Add-Member -NotePropertyName origem -NotePropertyValue 'PENDENTE' -Force }
        if (-not ($r.PSObject.Properties.Name -contains 'impulsionado')) { $r | Add-Member -NotePropertyName impulsionado -NotePropertyValue $null -Force }
        $r.id = $null
        $itens.Add($r)
      }
    }
    '.csv' {
      foreach ($c in (Import-Csv -Path $Entrada -Delimiter ';' -Encoding UTF8)) {
        if ($c.tipo -notin @('Reel', 'Vídeo')) { continue }
        $met = @{ views = (Num $c.views); curtidas = (Num $c.curtidas); comentarios = (Num $c.comentarios); compartilhamentos = (Num $c.compartilhamentos); salvamentos = (Num $c.salvamentos); reposts = (Num $c.reposts); alcance = (Num $c.alcance) }
        $itens.Add((NovoReel $c.link $c.data (Num $c.duracao_s) $met $c.legenda $c.transcricao $c.texto_na_tela $c.observacoes))
      }
    }
    '.docx' {
      foreach ($p in (LerDocx $Entrada)) {
        if ($p.tipo -notin @('Reel', 'Vídeo')) { continue }
        $g = $p.met
        $met = @{ views = (Num $g['Views']); curtidas = (Num $g['Curtidas']); comentarios = (Num $g['Comentários']); compartilhamentos = (Num $g['Compartilh.']); salvamentos = (Num $g['Salvamentos']); reposts = (Num $g['Reposts']); alcance = (Num $g['Alcance']) }
        $itens.Add((NovoReel $p.link $p.data $p.dur $met $p.legenda $p.transcricao $p.texto_na_tela $p.obs))
      }
    }
    default { throw "Extensão não suportada: $ext (use .json, .csv ou .docx)." }
  }

  $novos = @(); $atual = @()
  foreach ($r in $itens) {
    if ($naBase.ContainsKey((Codigo $r.link))) {
      $atual += [pscustomobject]@{ link = $r.link; codigo = (Codigo $r.link); data_hora = $r.data_hora; metricas = $r.metricas }
    } else { $novos += $r }
  }
  $nome = [IO.Path]::GetFileNameWithoutExtension($Entrada)
  $dirL = Join-Path $root 'dados\lotes'; New-Item -ItemType Directory -Force -Path $dirL | Out-Null
  $saida = if ($SaidaLote) { Abs $SaidaLote } else { Join-Path $dirL ("{0}-{1}.json" -f (Get-Date -Format 'yyyy-MM-dd'), $nome) }
  $pacote = [pscustomobject]@{
    meta = [pscustomobject]@{
      fonte = [IO.Path]::GetFileName($Entrada); tipo_entrada = $ext.TrimStart('.'); data_extracao = $dataExt.ToString('dd/MM/yyyy'); gerado_em = (Get-Date -Format 'dd/MM/yyyy HH:mm')
      instrucoes = 'Preencha todo campo PENDENTE dos "novos" (hook.tipo, hook.ressalva_nos_primeiros_segundos, tema, cta_falado, marcadores_de_estrutura.tem_historia_ou_caso, formato_visual, tela_com_imagens quando tela_dividida, origem). Use a taxonomia de references/hooks.md e os temas de dados/reels_base.json. Depois rode a etapa mesclar.'
    }
    novos = $novos; atualizacoes = $atual
  }
  [IO.File]::WriteAllText($saida, ($pacote | ConvertTo-Json -Depth 30), $utf8)
  "Lote gravado: $saida"
  "Entrada: $($itens.Count) reels/vídeos · novos: $($novos.Count) · já na base (atualização de métricas): $($atual.Count)"
  if ($novos.Count) { "Novos com PENDENTE para o Analista: " + (($novos | ForEach-Object { Codigo $_.link }) -join ', ') }
  exit 0
}

# =====================================================================
if ($Etapa -eq 'mesclar') {
  if (-not $Lote) { throw 'Informe -Lote (arquivo gerado na etapa normalizar).' }
  $Lote = Abs $Lote
  $lot = Get-Content -Raw -Encoding UTF8 $Lote | ConvertFrom-Json
  $pend = New-Object Collections.Generic.List[string]
  foreach ($r in @($lot.novos)) {
    $c = Codigo $r.link
    if ($r.hook.tipo -eq 'PENDENTE' -or -not $r.hook.tipo) { $pend.Add("$c hook.tipo") }
    if ($r.hook.ressalva_nos_primeiros_segundos -eq 'PENDENTE') { $pend.Add("$c hook.ressalva_nos_primeiros_segundos") }
    if ($r.tema -eq 'PENDENTE' -or -not $r.tema) { $pend.Add("$c tema") }
    if (@($r.cta_falado) -contains 'PENDENTE') { $pend.Add("$c cta_falado") }
    if ($r.marcadores_de_estrutura.tem_historia_ou_caso -eq 'PENDENTE') { $pend.Add("$c tem_historia_ou_caso") }
    if ($r.formato_visual -notin @('novela', 'tela_dividida', 'outro')) { $pend.Add("$c formato_visual") }
    if ($r.formato_visual -eq 'tela_dividida' -and $r.tela_com_imagens -eq $null) { $pend.Add("$c tela_com_imagens") }
    if ($r.origem -notin @('roteirizado', 'corte')) { $pend.Add("$c origem") }
  }
  if ($pend.Count) { $pend | ForEach-Object { "PENDENTE: $_" }; throw "Lote com $($pend.Count) campo(s) pendente(s). Preencha antes de mesclar." }

  $b = Get-Content -Raw -Encoding UTF8 $Base | ConvertFrom-Json
  $dirB = Join-Path (Split-Path $Base) 'backups'; New-Item -ItemType Directory -Force -Path $dirB | Out-Null
  Copy-Item $Base (Join-Path $dirB ("reels_base-{0}.json" -f (Get-Date -Format 'yyyyMMdd-HHmmss')))

  $porCodigo = @{}; foreach ($r in $b.reels) { $porCodigo[(Codigo $r.link)] = $r }
  $nAt = 0
  foreach ($u in @($lot.atualizacoes)) {
    $r = $porCodigo[(Codigo $u.link)]
    if (-not $r) { continue }
    foreach ($campo in 'views', 'curtidas', 'comentarios', 'compartilhamentos', 'salvamentos', 'reposts', 'alcance') {
      $v = $u.metricas.$campo
      if ($v -ne $null) {
        if ($r.metricas.PSObject.Properties.Name -contains $campo) { $r.metricas.$campo = $v } else { $r.metricas | Add-Member -NotePropertyName $campo -NotePropertyValue $v -Force }
      }
    }
    $nAt++
  }
  $maxId = [int](($b.reels | Measure-Object -Property id -Maximum).Maximum)
  $lista = New-Object Collections.Generic.List[object]; foreach ($r in $b.reels) { $lista.Add($r) }
  foreach ($r in @($lot.novos)) { $maxId++; $r.id = $maxId; $lista.Add($r) }

  $ext = if ($DataExtracao) { [datetime]::ParseExact($DataExtracao, 'dd/MM/yyyy', $pt) } elseif ($lot.meta.data_extracao) { [datetime]::ParseExact($lot.meta.data_extracao, 'dd/MM/yyyy', $pt) } else { Get-Date }
  foreach ($r in $lista) {
    $m = $r.metricas; $v = [double]$m.views
    if ($v -gt 0) {
      $m.taxa_curtida_pct = $(if ($m.curtidas -ne $null) { [math]::Round($m.curtidas / $v * 100, 2) } else { $null })
      $m.taxa_comentario_pct = $(if ($m.comentarios -ne $null) { [math]::Round($m.comentarios / $v * 100, 3) } else { $null })
      $m.taxa_repost_pct = $(if ($m.reposts -ne $null) { [math]::Round($m.reposts / $v * 100, 3) } else { $null })
    }
    $r.maturidade = $(if (($ext - (ParseData $r.data_hora)).TotalDays -lt 3) { 'recente_ainda_acumulando' } else { 'maduro' })
  }
  $medMes = @{}
  foreach ($g in ($lista | Group-Object { (ParseData $_.data_hora).ToString('yyyy-MM') })) { $medMes[$g.Name] = Med ($g.Group | ForEach-Object { $_.metricas.views }) }
  foreach ($r in $lista) {
    $mm = $medMes[(ParseData $r.data_hora).ToString('yyyy-MM')]
    $r.metricas.views_vs_mediana_do_mes = $(if ($mm) { [math]::Round([double]$r.metricas.views / $mm, 2) } else { $null })
  }
  $b.reels = $lista.ToArray()
  $ordenado = [ordered]@{}; foreach ($k in ($medMes.Keys | Sort-Object)) { $ordenado[$k] = $medMes[$k] }
  $b.baseline.mediana_views_por_mes = [pscustomobject]$ordenado
  $b.baseline.mediana_views_geral_maduros = Med ($lista | Where-Object { $_.maturidade -eq 'maduro' } | ForEach-Object { $_.metricas.views })
  $datas = $lista | ForEach-Object { ParseData $_.data_hora } | Sort-Object
  $b.meta.periodo = "$($datas[0].ToString('dd/MM/yyyy')) a $($datas[-1].ToString('dd/MM/yyyy'))"
  $b.meta.total_reels = $lista.Count
  $b.meta.gerado_em = (Get-Date -Format 'yyyy-MM-dd')
  if ($b.meta.rotulos_visuais) {
    $b.meta.rotulos_visuais.contagem = [pscustomobject]@{
      novela = @($lista | Where-Object { $_.formato_visual -eq 'novela' }).Count
      tela_dividida = @($lista | Where-Object { $_.formato_visual -eq 'tela_dividida' }).Count
      outro = @($lista | Where-Object { $_.formato_visual -eq 'outro' }).Count
    }
  }
  [IO.File]::WriteAllText($Base, ($b | ConvertTo-Json -Depth 50), $utf8)
  "Base atualizada: $Base"
  "Novos: $(@($lot.novos).Count) · métricas atualizadas: $nAt · total: $($lista.Count) · backup em $dirB"
  "Próximo: rode gerar-corpus.ps1 e stats-formatos.ps1 -Saida dados\stats-formatos.md"
  exit 0
}
