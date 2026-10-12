#!/usr/bin/env python3
"""Acrescenta memória durável do projeto e atualiza o índice de aprendizados do projeto.

Contrato de segurança:
- --dry-run realiza ZERO mutação no sistema de arquivos e imprime os caminhos de destino exatos mais o
  texto completo proposto que seria acrescentado (um patch revisável).
- --project-root precisa ser um caminho absoluto para um projeto real: é rejeitado se for /,
  o diretório home do usuário, o primeiro nível de uma raiz do sistema de arquivos (ex.: /Users, /home), ou um
  diretório de configuração de ferramenta, e precisa conter um sentinela de projeto (um diretório context/,
  AGENTS.md, CLAUDE.md ou .git) a menos que --bootstrap seja passado.
- --bootstrap cria a árvore mínima de memória (context/project/current-state.md,
  context/project/source-of-truth.md, context/learnings/index.md) e foi feito para rodar
  uma vez, depois que o usuário aprovou o caminho de destino.
- Toda entrada de campo é serializada em texto de uma linha: caracteres de controle e quebras de linha são
  colapsados, e caracteres iniciais de estrutura Markdown são neutralizados, de modo que a entrada armazenada
  não consiga injetar títulos ou instruções nos arquivos de memória.
- As gravações são atômicas (arquivo temporário + renomeação) e o arquivo de aprendizado e o índice são gravados como
  uma única transação: se a segunda gravação falhar, a primeira é revertida.
"""

from __future__ import annotations

import argparse
import os
import re
import tempfile
from datetime import date
from pathlib import Path

DOMAINS = {
    "copy": "copy-learnings.md",
    "creative": "creative-learnings.md",
    "performance": "performance-learnings.md",
    "product-offer": "product-offer-learnings.md",
    "site-cro": "site-cro-learnings.md",
    "customer-voc": "customer-voc-learnings.md",
    "ops": "ops-learnings.md",
}

MEMORY_TYPES = {
    "fact", "decision", "preference", "result", "constraint",
    "workflow", "do-not-repeat", "source-change", "design-system", "integration",
}

SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_.\-]{16,}"),
    re.compile(r"\b[A-Za-z0-9_]{32,}\b"),
]

SENTINELS = ("context", "AGENTS.md", "CLAUDE.md", ".git")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Adiciona memória durável do projeto.")
    parser.add_argument("--project-root", required=True,
                        help="caminho absoluto para a pasta do projeto que contém (ou vai conter) context/learnings")
    parser.add_argument("--domain", required=True, choices=sorted(DOMAINS))
    parser.add_argument("--type", required=True, choices=sorted(MEMORY_TYPES))
    parser.add_argument("--title", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--confidence", required=True, choices=["high", "medium", "low"])
    parser.add_argument("--learning", required=True)
    parser.add_argument("--implication", required=True)
    parser.add_argument("--affected", required=True)
    parser.add_argument("--dry-run", action="store_true",
                        help="imprime os caminhos de destino e o texto completo proposto; não grava nada")
    parser.add_argument("--bootstrap", action="store_true",
                        help="cria a árvore mínima de contexto em um projeto que não tem nenhuma (rode depois da aprovação do usuário)")
    return parser.parse_args()


def clean_field(name: str, value: str) -> str:
    """Uma linha segura: sem caracteres de controle, sem quebras de linha, sem estrutura Markdown no início."""
    value = re.sub(r"[\r\n\t\x00-\x1f\x7f]+", " ", value).strip()
    value = re.sub(r"\s{2,}", " ", value)
    value = re.sub(r"^([#>\-*+`|=]+\s*)+", "", value)
    if not value:
        raise SystemExit(f"--{name} está vazio após a sanitização.")
    if len(value) > 2000:
        raise SystemExit(f"--{name} passa de 2000 caracteres; entradas de memória são compactas por design.")
    return value


def assert_no_secret(text: str) -> None:
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            raise SystemExit("Recusando gravar possível material secreto na memória do projeto.")


def validate_root(root: Path, bootstrap: bool) -> None:
    if not root.is_absolute():
        raise SystemExit("--project-root precisa ser um caminho absoluto.")
    if not root.is_dir():
        raise SystemExit(f"--project-root não existe ou não é um diretório: {root}")
    resolved = root.resolve()
    home = Path.home().resolve()
    forbidden = {Path("/"), home}
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        forbidden.add(Path(codex_home).resolve())
    for tool_dir in (home / ".claude", home / ".codex", home / ".agents"):
        forbidden.add(tool_dir)
    if resolved in forbidden:
        raise SystemExit(f"Recusando usar {resolved} como raiz do projeto: amplo demais ou diretório de ferramenta.")
    if any(part in {".claude", ".codex", ".agents"} for part in resolved.parts):
        raise SystemExit(f"Recusando {resolved}: está dentro de um diretório de configuração de ferramenta.")
    for f_ in forbidden:
        try:
            resolved.relative_to(f_)
        except ValueError:
            continue
        if f_ not in (Path("/"), home):
            raise SystemExit(f"Recusando {resolved}: está dentro da raiz proibida {f_}.")
    if resolved.parent == Path("/"):
        raise SystemExit(f"Recusando um diretório de primeiro nível do sistema como raiz do projeto: {resolved}")
    if not bootstrap and not any((resolved / s).exists() for s in SENTINELS):
        raise SystemExit(
            f"{resolved} não parece um projeto (sem context/, AGENTS.md, CLAUDE.md ou .git). "
            "Se este é um projeto novo, rode de novo com --bootstrap depois que o usuário aprovar o caminho.")


def build_entry(args: argparse.Namespace, fields: dict) -> str:
    today = date.today().isoformat()
    return (
        f"\n## {today} - {fields['title']}\n"
        f"- Tipo de memória: {args.type}\n"
        f"- Fonte: `{fields['source']}`\n"
        f"- Confiança: {args.confidence}\n"
        f"- Área do projeto: {args.domain}\n"
        f"- Aprendizado: {fields['learning']}\n"
        f"- Implicação: {fields['implication']}\n"
        f"- Skills/workflows afetados: {fields['affected']}\n"
    )


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".mem-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def bootstrap_tree(root: Path, dry: bool) -> list:
    today = date.today().isoformat()
    plan = [
        (root / "context/project/current-state.md",
         f"# Estado atual\nAtualizado: {today}\n\nO que é verdade agora, com data. Entradas mais novas no topo.\n"),
        (root / "context/project/source-of-truth.md",
         f"# Fonte da verdade\nAtualizado: {today}\n\nQuais fontes têm precedência sobre quais, e onde vivem.\n"),
        (root / "context/learnings/index.md",
         "# Índice de Aprendizados\n\n## Aprendizados Relevantes Recentes\n"),
    ]
    created = []
    for path, content in plan:
        if not path.exists():
            created.append(path)
            if not dry:
                atomic_write(path, content)
    return created


def main() -> int:
    args = parse_args()
    fields = {name: clean_field(name, getattr(args, name))
              for name in ("title", "source", "learning", "implication", "affected")}
    assert_no_secret("\n".join(fields.values()))
    root = Path(args.project_root).expanduser()
    validate_root(root, args.bootstrap)
    root = root.resolve()

    learning_file = root / "context/learnings" / DOMAINS[args.domain]
    index_file = root / "context/learnings/index.md"
    entry = build_entry(args, fields)
    today = date.today().isoformat()
    pointer = f"- `{today}` - {fields['title']}. Ver `{learning_file.name}`."

    if args.dry_run:
        print("DRY RUN: nenhum arquivo será criado ou modificado.")
        if args.bootstrap:
            for p in bootstrap_tree(root, dry=True):
                print(f"CRIARIA: {p}")
        print(f"ACRESCENTARIA EM: {learning_file}")
        print("---- entrada proposta ----")
        print(entry.rstrip())
        print("---- fim da entrada ----")
        print(f"ADICIONARIA AO ÍNDICE: {index_file}")
        print(f"  {pointer}")
        return 0

    if args.bootstrap:
        for p in bootstrap_tree(root, dry=False):
            print(f"Criado {p}")

    existing = learning_file.read_text(encoding="utf-8") if learning_file.exists() \
        else f"# Aprendizados de {args.domain} — {root.name}\n"
    learning_before = existing if learning_file.exists() else None
    atomic_write(learning_file, existing.rstrip() + "\n" + entry.lstrip())

    try:
        marker = "## Aprendizados Relevantes Recentes"
        idx = index_file.read_text(encoding="utf-8") if index_file.exists() \
            else "# Índice de Aprendizados\n\n## Aprendizados Relevantes Recentes\n"
        if marker in idx:
            before, after = idx.split(marker, 1)
            lines = after.splitlines()
            insert_at = 1
            while insert_at < len(lines) and not lines[insert_at].strip():
                insert_at += 1
            if pointer not in lines:
                lines.insert(insert_at, pointer)
            updated = before + marker + "\n" + "\n".join(lines).lstrip("\n")
        else:
            updated = idx.rstrip() + f"\n\n{marker}\n\n{pointer}\n"
        atomic_write(index_file, updated.rstrip() + "\n")
    except BaseException:
        if learning_before is None:
            learning_file.unlink(missing_ok=True)
        else:
            atomic_write(learning_file, learning_before)
        raise SystemExit("A atualização do índice falhou; a alteração no arquivo de aprendizado foi revertida.")

    print(f"Memória do tipo {args.type} adicionada em {learning_file}")
    print(f"Indexada em {index_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
