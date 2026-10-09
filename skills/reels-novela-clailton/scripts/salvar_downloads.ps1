# Aperta "Salvar" sozinho nas janelas "Salvar como" do Chrome (download do Adobe Podcast) - usuário, 09/10/2026:
# "automatize 100% o processo". O Chrome da conta Legacy pergunta onde salvar; este script acha cada janela DO CHROME
# (nunca de outro programa: o Premiere também abre "Salvar como"), põe no campo do nome do arquivo (controle fixo 1148
# do diálogo do Windows - NÃO o "Nome" da lista de arquivos, que renomeia arquivo) o caminho -Pasta\<nome sugerido>
# e aperta Salvar (comando IDOK). Avisos do próprio diálogo ("Renomear", "Confirmar Salvar como") são respondidos.
# Uso: powershell -NoProfile -ExecutionPolicy Bypass -File salvar_downloads.ps1 [-Pasta C:\Render\adobe_baixados] [-Esperar 60]
#   -Esperar: segundos esperando aparecer janela (0 = só as abertas). Continua até não sobrar nenhuma.
param([string]$Pasta = "C:\Render\adobe_baixados", [int]$Esperar = 0)

New-Item -ItemType Directory -Force $Pasta | Out-Null
Add-Type @"
using System; using System.Text; using System.Collections.Generic; using System.Runtime.InteropServices;
public class Dlg {
  public delegate bool P(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] static extern bool EnumWindows(P f, IntPtr l);
  [DllImport("user32.dll")] static extern int GetClassName(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint p);
  [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern IntPtr GetDlgItem(IntPtr h, int id);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern IntPtr FindWindowEx(IntPtr p, IntPtr a, string c, string t);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] static extern IntPtr SendMessage(IntPtr h, int m, IntPtr w, StringBuilder l);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] static extern IntPtr SendMessage(IntPtr h, int m, IntPtr w, string l);
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, int m, IntPtr w, IntPtr l);
  public static List<string> Lista() {
    var r = new List<string>();
    EnumWindows((h,l)=>{ var c=new StringBuilder(64); GetClassName(h,c,64);
      if (c.ToString()=="#32770" && IsWindowVisible(h)) { var t=new StringBuilder(256); GetWindowText(h,t,256); uint p; GetWindowThreadProcessId(h,out p); r.Add(h.ToInt64()+"|"+p+"|"+t); }
      return true; }, IntPtr.Zero);
    return r;
  }
  [DllImport("user32.dll")] static extern bool EnumChildWindows(IntPtr p, P f, IntPtr l);
  [DllImport("user32.dll")] static extern int GetDlgCtrlID(IntPtr h);
  [DllImport("user32.dll")] static extern IntPtr GetParent(IntPtr h);
  public static IntPtr CampoNome(IntPtr dlg) {
    // diálogo do Windows: o campo "Nome" do arquivo é o Edit de id 1001 dentro de um ComboBox (o outro 1001 é a
    // barra de endereço). O "Nome" da LISTA de arquivos é outro controle e renomeia arquivo — nunca usar.
    IntPtr ed = IntPtr.Zero;
    EnumChildWindows(dlg, (h,l)=>{ var c=new StringBuilder(64); GetClassName(h,c,64);
      if (c.ToString()=="Edit" && GetDlgCtrlID(h)==1001) { var pc=new StringBuilder(64); GetClassName(GetParent(h),pc,64);
        if (pc.ToString()=="ComboBox") { ed=h; return false; } }
      return true; }, IntPtr.Zero);
    return ed;
  }
  public static string Texto(IntPtr h) { var s=new StringBuilder(1024); SendMessage(h, 0x000D, (IntPtr)1024, s); return s.ToString(); }
  public static void PorTexto(IntPtr h, string t) { SendMessage(h, 0x000C, IntPtr.Zero, t); }
  public static void Comando(IntPtr dlg, int id) { PostMessage(dlg, 0x0111, (IntPtr)id, IntPtr.Zero); }
}
"@

function DoChrome([string]$linha) {
    $a = $linha -split '\|', 3
    $p = Get-Process -Id ([int]$a[1]) -ErrorAction SilentlyContinue
    if ($p -and $p.ProcessName -eq "chrome") { return @{ h = [IntPtr][long]$a[0]; titulo = $a[2] } }
    return $null
}

$fim = (Get-Date).AddSeconds($Esperar)
$n = 0
$falhas = 0
do {
    $abertas = 0
    foreach ($l in [Dlg]::Lista()) {
        $d = DoChrome $l
        if (-not $d) { continue }
        if ($d.titulo -match "^(Salvar como|Save As)$") {
            $abertas++
            $campo = [Dlg]::CampoNome($d.h)
            if ($campo -eq [IntPtr]::Zero) {
                $falhas++
                if ($falhas -ge 3) { Write-Output "ERRO: campo do nome não achado (janela deixada aberta)"; exit 2 }
                Start-Sleep -Seconds 1; continue
            }
            $nome = Split-Path -Leaf ([Dlg]::Texto($campo))
            $nome = $nome -replace ' \(\d+\)(?=\.[^.]+$)', ''      # "x (1).mp3" -> "x.mp3"
            $destino = Join-Path $Pasta $nome
            [Dlg]::PorTexto($campo, $destino)
            [Dlg]::Comando($d.h, 1)                                     # Salvar
            Write-Output "salvo: $destino"
            $n++
            Start-Sleep -Milliseconds 1200
        } elseif ($d.titulo -match "Confirmar|Confirm") {
            [Dlg]::Comando($d.h, 6)                                     # "Sim": substituir o arquivo antigo
        } elseif ($d.titulo -match "^(Renomear|Rename)$") {
            [Dlg]::Comando($d.h, 1)                                     # OK no aviso
        }
    }
    if ($abertas -eq 0) { Start-Sleep -Seconds 1 }
} while ($abertas -gt 0 -or (Get-Date) -lt $fim)
Write-Output "ok: $n arquivo(s) salvos em $Pasta"
