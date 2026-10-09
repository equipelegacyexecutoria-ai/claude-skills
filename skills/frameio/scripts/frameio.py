"""Ligacao direta com o Frame.io (API V4, login Adobe).

Codigos e login ficam em $HOME/FrameIO (fora da sincronia das skills):
  credenciais.txt  CLIENT_ID= / CLIENT_SECRET= (o usuario cola)
  token.json       login salvo (criado pelo comando login)

Uso:
  python frameio.py login                      abre o navegador para "Permitir"
  python frameio.py projetos                   lista workspaces e projetos
  python frameio.py listar <projeto|pasta_id>  lista o conteudo (pasta raiz se for projeto)
  python frameio.py comentarios <arquivo_id>   comentarios com o tempo do video
  python frameio.py baixar <arquivo_id> [destino]
  python frameio.py subir <arquivo_local> <pasta_id|projeto_id>
  python frameio.py criar-pasta <pasta_id|projeto_id> <nome>
  python frameio.py get <caminho_api>          chamada crua (debug), ex.: /accounts
"""
import base64
import http.server
import json
import mimetypes
import os
import secrets
import ssl
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

PASTA = os.path.join(os.path.expanduser("~"), "FrameIO")
CRED = os.path.join(PASTA, "credenciais.txt")
TOKEN = os.path.join(PASTA, "token.json")
CERT = os.path.join(PASTA, "localhost.pem")
CHAVE = os.path.join(PASTA, "localhost-key.pem")
CONTA = os.path.join(PASTA, "conta.json")

PORTA = 8443
REDIRECT = f"https://localhost:{PORTA}/callback"
IMS = "https://ims-na1.adobelogin.com/ims"
API = "https://api.frame.io/v4"
ESCOPOS = "offline_access,openid,email,profile,additional_info.roles"
UA = "LegacyClaude-FrameIO/1.0 (+python)"


def ler_credenciais():
    if not os.path.exists(CRED):
        sys.exit(f"Falta o arquivo {CRED}")
    vals = {}
    with open(CRED, encoding="utf-8-sig") as f:
        for linha in f:
            linha = linha.strip()
            if "=" in linha and not linha.startswith("#"):
                k, v = linha.split("=", 1)
                vals[k.strip()] = v.strip()
    cid, sec = vals.get("CLIENT_ID", ""), vals.get("CLIENT_SECRET", "")
    if not cid or not sec:
        sys.exit("CLIENT_ID ou CLIENT_SECRET vazio em credenciais.txt (colou e salvou com Ctrl+S?)")
    return cid, sec


def _post_token(dados):
    cid, sec = ler_credenciais()
    basic = base64.b64encode(f"{cid}:{sec}".encode()).decode()
    req = urllib.request.Request(
        f"{IMS}/token/v3",
        data=urllib.parse.urlencode(dados).encode(),
        headers={"Authorization": f"Basic {basic}",
                 "Content-Type": "application/x-www-form-urlencoded", "User-Agent": UA},
    )
    try:
        with urllib.request.urlopen(req) as r:
            tok = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Erro no login da Adobe ({e.code}): {e.read().decode(errors='replace')[:400]}")
    tok["expira_em"] = time.time() + int(tok.get("expires_in", 3600)) - 120
    if "refresh_token" not in tok and dados.get("refresh_token"):
        tok["refresh_token"] = dados["refresh_token"]
    with open(TOKEN, "w", encoding="utf-8") as f:
        json.dump(tok, f)
    return tok


def gerar_certificado():
    if os.path.exists(CERT) and os.path.exists(CHAVE):
        return
    subprocess.run(
        ["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "3650",
         "-keyout", CHAVE, "-out", CERT, "-subj", "/CN=localhost"],
        check=True, capture_output=True,
    )


def login():
    cid, _ = ler_credenciais()
    gerar_certificado()
    estado = secrets.token_urlsafe(16)
    resultado = {}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if not self.path.startswith("/callback"):
                self.send_response(404); self.end_headers(); return
            antigo = q.get("state", [""])[0] != estado
            ok = not antigo and "code" in q
            if ok:
                resultado["code"] = q["code"][0]
            elif antigo:
                pass  # aba de um login anterior: ignora e continua esperando a aba nova
            else:
                resultado["erro"] = q.get("error_description", q.get("error", ["resposta invalida"]))[0]
            if ok:
                msg = "Pronto! O Claude ja esta ligado ao Frame.io. Pode fechar esta aba."
            elif antigo:
                msg = "Esta aba e de um login antigo. Feche-a e use a aba de login mais nova."
            else:
                msg = f"Nao deu certo: {resultado.get('erro')}"
            corpo = f"<html><meta charset='utf-8'><body style='font-family:sans-serif;padding:40px'><h2>{msg}</h2></body></html>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(corpo.encode())

        def log_message(self, *a):
            pass

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", PORTA), H)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(CERT, CHAVE)
    srv.socket = ctx.wrap_socket(srv.socket, server_side=True)
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    url = f"{IMS}/authorize/v2?" + urllib.parse.urlencode({
        "client_id": cid, "redirect_uri": REDIRECT, "scope": ESCOPOS,
        "response_type": "code", "state": estado, "prompt": "login",
    })
    print("Abrindo o navegador para o login da Adobe...")
    print("Se nao abrir, cole este endereco no Chrome:\n" + url, flush=True)
    webbrowser.open(url)
    fim = time.time() + 1200
    while not resultado and time.time() < fim:
        time.sleep(0.5)
    time.sleep(1)  # deixa a pagina de resposta chegar ao navegador (sem shutdown: pode travar em conexao TLS pendente)
    if "code" not in resultado:
        sys.exit("Login nao concluido: " + resultado.get("erro", "tempo esgotado (20 min)"))
    _post_token({"grant_type": "authorization_code", "code": resultado["code"]})
    print("Login salvo.")
    eu = api("GET", "/me")["data"]
    print(f"Conectado como {eu.get('name')} <{eu.get('email')}>")


def token_valido():
    if not os.path.exists(TOKEN):
        sys.exit("Ainda nao ha login. Rode: python frameio.py login")
    with open(TOKEN, encoding="utf-8") as f:
        tok = json.load(f)
    if time.time() > tok.get("expira_em", 0):
        if not tok.get("refresh_token"):
            sys.exit("Login expirou. Rode: python frameio.py login")
        tok = _post_token({"grant_type": "refresh_token", "refresh_token": tok["refresh_token"]})
    return tok["access_token"]


def api(metodo, caminho, corpo=None):
    url = caminho if caminho.startswith("http") else API + caminho
    dados = json.dumps(corpo).encode() if corpo is not None else None
    req = urllib.request.Request(url, data=dados, method=metodo, headers={
        "Authorization": f"Bearer {token_valido()}",
        "Content-Type": "application/json",
        "User-Agent": UA,
    })
    try:
        with urllib.request.urlopen(req) as r:
            txt = r.read()
            return json.loads(txt) if txt else {}
    except urllib.error.HTTPError as e:
        sys.exit(f"Erro do Frame.io ({e.code}) em {caminho}: {e.read().decode(errors='replace')[:500]}")


def todas_paginas(caminho):
    itens = []
    while caminho:
        r = api("GET", caminho)
        itens += r.get("data", [])
        prox = (r.get("links") or {}).get("next")
        caminho = prox if prox else None
    return itens


def conta_id():
    if os.path.exists(CONTA):
        with open(CONTA, encoding="utf-8") as f:
            return json.load(f)["account_id"]
    contas = todas_paginas("/accounts")
    if not contas:
        sys.exit("Nenhuma conta do Frame.io encontrada para este login.")
    with open(CONTA, "w", encoding="utf-8") as f:
        json.dump({"account_id": contas[0]["id"], "nome": contas[0].get("display_name")}, f)
    return contas[0]["id"]


def pasta_de(id_):
    """Aceita id de pasta ou de projeto (usa a pasta raiz do projeto)."""
    a = conta_id()
    req = urllib.request.Request(f"{API}/accounts/{a}/projects/{id_}",
                                 headers={"Authorization": f"Bearer {token_valido()}", "User-Agent": UA})
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)["data"]["root_folder_id"]
    except urllib.error.HTTPError:
        return id_


def projetos():
    a = conta_id()
    for w in todas_paginas(f"/accounts/{a}/workspaces"):
        print(f"[workspace] {w.get('name')}  id={w['id']}")
        for p in todas_paginas(f"/accounts/{a}/workspaces/{w['id']}/projects"):
            print(f"   [projeto] {p.get('name')}  id={p['id']}  pasta_raiz={p.get('root_folder_id')}")


def listar(id_):
    a = conta_id()
    for it in todas_paginas(f"/accounts/{a}/folders/{pasta_de(id_)}/children"):
        print(f"[{it.get('type')}] {it.get('name')}  id={it['id']}  status={it.get('status', '')}")


def _tempo(c):
    seg = c.get("timestamp")
    if seg is None:
        return "--:--"
    if isinstance(seg, (int, float)) and c.get("timestamp_unit", "seconds") == "frames" and c.get("fps"):
        seg = seg / c["fps"]
    try:
        seg = float(seg)
        return f"{int(seg // 60):02d}:{seg % 60:05.2f}"
    except (TypeError, ValueError):
        return str(seg)


def comentarios(id_):
    a = conta_id()
    itens = todas_paginas(f"/accounts/{a}/files/{id_}/comments?include=owner")
    if not itens:
        print("Sem comentarios.")
    for c in itens:
        autor = (c.get("owner") or {}).get("name", "")
        print(f"[{_tempo(c)}] {autor}: {c.get('text', '')}")
    with open(os.path.join(PASTA, f"comentarios_{id_}.json"), "w", encoding="utf-8") as f:
        json.dump(itens, f, ensure_ascii=False, indent=1)


def baixar(id_, destino="."):
    a = conta_id()
    d = api("GET", f"/accounts/{a}/files/{id_}?include=media_links.original")["data"]
    url = ((d.get("media_links") or {}).get("original") or {}).get("download_url")
    if not url:
        sys.exit("Sem link de download para este arquivo.")
    alvo = os.path.join(destino, d.get("name", id_)) if os.path.isdir(destino) else destino
    print(f"Baixando {d.get('name')} -> {alvo}")
    urllib.request.urlretrieve(url, alvo)
    print("Pronto.")


def subir(arquivo, id_):
    a = conta_id()
    tam = os.path.getsize(arquivo)
    nome = os.path.basename(arquivo)
    d = api("POST", f"/accounts/{a}/folders/{pasta_de(id_)}/files/local_upload",
            {"data": {"name": nome, "file_size": tam}})["data"]
    tipo = d.get("media_type") or mimetypes.guess_type(nome)[0] or "application/octet-stream"
    partes = d["upload_urls"]
    print(f"Enviando {nome} ({tam / 1e6:.1f} MB) em {len(partes)} parte(s)...", flush=True)
    with open(arquivo, "rb") as f:
        for i, p in enumerate(partes, 1):
            pedaco = f.read(p["size"])
            for tentativa in range(4):
                try:
                    req = urllib.request.Request(p["url"], data=pedaco, method="PUT", headers={
                        "Content-Type": tipo, "x-amz-acl": "private"})
                    urllib.request.urlopen(req).read()
                    break
                except Exception as e:
                    if tentativa == 3:
                        sys.exit(f"Falhou a parte {i}: {e}")
                    time.sleep(2 * (tentativa + 1))
            print(f"  parte {i}/{len(partes)} ok", flush=True)
    print(f"Enviado. id={d['id']}")
    print(f"Link: https://next.frame.io/project/{d.get('project_id', '')}/view/{d['id']}")


def criar_pasta(id_, nome):
    a = conta_id()
    d = api("POST", f"/accounts/{a}/folders/{pasta_de(id_)}/folders", {"data": {"name": nome}})["data"]
    print(f"Pasta criada: {d.get('name')}  id={d['id']}")


def main():
    os.makedirs(PASTA, exist_ok=True)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    if not args:
        print(__doc__); return
    cmd, resto = args[0], args[1:]
    if cmd == "login":
        login()
    elif cmd == "projetos":
        projetos()
    elif cmd == "listar":
        listar(resto[0])
    elif cmd == "comentarios":
        comentarios(resto[0])
    elif cmd == "baixar":
        baixar(*resto[:2])
    elif cmd == "subir":
        subir(resto[0], resto[1])
    elif cmd == "criar-pasta":
        criar_pasta(resto[0], " ".join(resto[1:]))
    elif cmd == "get":
        print(json.dumps(api("GET", "/" + resto[0].lstrip("/")), ensure_ascii=False, indent=1))
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
