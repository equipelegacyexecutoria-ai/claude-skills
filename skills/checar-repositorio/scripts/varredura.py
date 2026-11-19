"""Varredura de seguranca de um repositorio baixado do GitHub (ou de qualquer pasta de terceiros).

So LE os arquivos: nao executa, nao instala e nao importa nada da pasta analisada.
Rodar sempre com `python -I` e com a pasta como argumento:

    python -I ~/.claude/skills/checar-repositorio/scripts/varredura.py <pasta-do-repo> [<outra-pasta> ...]

Saida: secoes com o que precisa ser olhado por uma pessoa (ou pelo Claude) antes de instalar.
Nada encontrado numa secao = linha "(nada)".
"""
import json
import os
import re
import sys
from collections import Counter

PULAR_PASTAS = {'.git', 'node_modules', '__pycache__', '.venv', 'venv'}
EXT_TEXTO = ('.md', '.json', '.js', '.mjs', '.cjs', '.ts', '.tsx', '.jsx', '.py', '.sh', '.ps1', '.psm1',
             '.bat', '.cmd', '.txt', '.yaml', '.yml', '.toml', '.html', '.rb', '.go', '.rs', '.lua')
EXT_CODIGO = ('.js', '.mjs', '.cjs', '.ts', '.tsx', '.jsx', '.py', '.sh', '.ps1', '.psm1', '.bat', '.cmd', '.rb', '.lua')
EXT_EXECUTAVEL = ('.exe', '.dll', '.so', '.dylib', '.bat', '.cmd', '.ps1', '.vbs', '.scr', '.jar', '.pyc',
                  '.node', '.msi', '.bin', '.lnk', '.hta', '.com', '.cpl', '.wsf', '.apk', '.dmg', '.pkg')
PASTA_GERADA = re.compile(r'(/vendor/|/dist/|\.min\.|/build/|/lib/)')

MALICIOSO = re.compile(
    r"(curl|wget|iwr|Invoke-WebRequest|irm)[^|\n]{0,200}\|\s*(sh|bash|zsh|iex|python3?|node|powershell|pwsh)\b"
    r"|Invoke-Expression|\bIEX\b|-EncodedCommand|powershell[^\n]{0,40}\s-e(nc)?\s"
    r"|FromBase64String|base64 (-d|--decode)[^\n]{0,60}\|\s*(sh|bash)"
    r"|eval\(\s*(atob|Buffer\.from|unescape)|new Function\(\s*atob|marshal\.loads|exec\(\s*(base64|zlib|codecs|bytes\.fromhex)"
    r"|__import__\(['\"](base64|zlib|marshal)|discord(app)?\.com/api/webhooks|api\.telegram\.org/bot"
    r"|pastebin\.com|hastebin|ngrok\.(io|app)|transfer\.sh|webhook\.site|requestbin|pipedream\.net|interact\.sh"
    r"|Login Data|Cookies\.sqlite|wallet\.dat|\.ssh/id_|\.aws/credentials|AppData[\\/]+(Local|Roaming)[\\/]+(Google|Microsoft|Mozilla|BraveSoftware)"
    r"|ANTHROPIC_API_KEY|CLAUDE_CODE_OAUTH|\.claude/\.credentials|\.claude\.json"
    r"|Set-MpPreference|Add-MpPreference|DisableRealtimeMonitoring|schtasks\s+/create|CurrentVersion\\\\Run"
    r"|crontab\s+-|LaunchAgents|reg\s+add\s+HK",
    re.I)
INSTRUCAO_ESCONDIDA = re.compile(
    r"ignore (all |any )?(previous|prior|above) instructions|do not (tell|inform|mention (it )?to) the user"
    r"|without (telling|asking|informing|notifying) the user|silently (run|install|send|upload|execute|download)"
    r"|send (the|your|all) [a-z ]{0,20}(keys?|tokens?|credentials|env|secrets)|exfiltrat"
    r"|disregard (the|your) (system|safety|previous)|you are now (in )?(developer|dan|jailbreak)"
    r"|n[aã]o (conte|avise|diga) (ao|para o) usu[aá]rio",
    re.I)
INVISIVEL = re.compile('[​-‏‪-‮⁦-⁩\U000E0000-\U000E007F]')
URL = re.compile(r"https?://([a-zA-Z0-9.-]+|\d{1,3}(?:\.\d{1,3}){3})(:\d+)?")
IP_CRU = re.compile(r"https?://(\d{1,3}(?:\.\d{1,3}){3})")


def arquivos(raiz):
    for d, ds, fs in os.walk(raiz):
        ds[:] = [x for x in ds if x not in PULAR_PASTAS]
        for f in fs:
            yield os.path.join(d, f)


def ler(p):
    try:
        with open(p, encoding='utf-8') as fh:
            return fh.read()
    except Exception:
        return None


def secao(titulo, linhas):
    print(f"\n=== {titulo}")
    if not linhas:
        print("(nada)")
    for l in linhas[:80]:
        print(l)
    if len(linhas) > 80:
        print(f"... mais {len(linhas) - 80}")


def varrer(raiz):
    raiz = os.path.abspath(os.path.expanduser(raiz))
    rel = lambda p: os.path.relpath(p, raiz).replace('\\', '/')
    execs, ganchos, malic, instr, invis, longas, dominios, ips = [], [], [], [], [], [], Counter(), []
    total = 0
    for p in arquivos(raiz):
        total += 1
        nome = os.path.basename(p).lower()
        r = rel(p)
        if nome.endswith(EXT_EXECUTAVEL):
            execs.append(f"{r}  ({os.path.getsize(p)} bytes)")
        if nome in ('settings.json', 'settings.local.json', 'hooks.json', 'plugin.json', '.mcp.json',
                    'marketplace.json', 'setup.py', 'install.sh', 'install.ps1', 'postinstall.js'):
            ganchos.append(f"{r}  (abrir e ler)")
        if not nome.endswith(EXT_TEXTO):
            continue
        t = ler(p)
        if t is None:
            continue
        if nome == 'package.json':
            try:
                scripts = json.loads(t).get('scripts', {})
                for k in ('preinstall', 'install', 'postinstall', 'prepare', 'prepublish'):
                    if k in scripts:
                        ganchos.append(f"{r}: \"{k}\": {scripts[k]}")
            except Exception:
                pass
        if '"hooks"' in t and nome.endswith('.json'):
            ganchos.append(f"{r}: tem bloco \"hooks\" (roda comando sozinho no Claude Code)")
        longa_ja = False
        for i, linha in enumerate(t.splitlines(), 1):
            if MALICIOSO.search(linha):
                malic.append(f"{r}:{i}: {linha.strip()[:200]}")
            if nome.endswith(('.md', '.txt', '.json', '.yaml', '.yml')) and INSTRUCAO_ESCONDIDA.search(linha):
                instr.append(f"{r}:{i}: {linha.strip()[:200]}")
            if INVISIVEL.search(linha):
                cods = sorted({hex(ord(c)) for c in INVISIVEL.findall(linha)})
                invis.append(f"{r}:{i}: {cods} {linha.strip()[:120]!r}")
            if nome.endswith(EXT_CODIGO):
                if len(linha) > 1500 and not longa_ja and not PASTA_GERADA.search('/' + r):
                    longa_ja = True
                    longas.append(f"{r}:{i}: {len(linha)} caracteres: {linha[:100]!r}")
                for m in URL.finditer(linha):
                    dominios[m.group(1).lower()] += 1
                for m in IP_CRU.finditer(linha):
                    if not m.group(1).startswith(('127.', '0.0.0.0', '192.168.', '10.')):
                        ips.append(f"{r}:{i}: {m.group(0)}")
        if nome == 'skill.md' and '<!--' in t:
            instr.append(f"{r}: tem comentario HTML escondido (<!-- -->), ler")

    print(f"\n######## {raiz}  ({total} arquivos)")
    secao("1. Executaveis e scripts de sistema", execs)
    secao("2. Coisas que rodam sozinhas (instaladores, ganchos, MCP)", ganchos)
    secao("3. Padroes de codigo malicioso (download+execucao, ofuscacao, roubo de senha/chave, persistencia)", malic)
    secao("4. Instrucoes escondidas para o agente (prompt injection)", instr)
    secao("5. Caracteres invisiveis", invis)
    secao("6. Linhas gigantes em codigo (possivel ofuscacao; dados gerados sao normais)", longas)
    secao("7. Enderecos IP crus", ips)
    raros = sorted(d for d, n in dominios.items() if n <= 2)
    secao("8. Dominios que aparecem pouco no codigo (conferir se fazem sentido)", [' '.join(raros)] if raros else [])


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    for pasta in sys.argv[1:]:
        varrer(pasta)
