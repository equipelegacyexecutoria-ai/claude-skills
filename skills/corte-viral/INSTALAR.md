# Instalação

A skill já está instalada em `~/.claude/skills/corte-viral/`, com a venv própria e
os 8 subagentes copiados. `verificar.py` confirma o estado a qualquer momento.

## O lanchador `vch`

Use sempre:

```bash
~/.claude/skills/corte-viral/vch <subcomando>
```

Nunca `python3 scripts/vch.py` direto. Motivo medido: o `python3` do PATH deste Mac
é o **3.9.6** do sistema, e o pacote exige 3.10+. Chamando direto, o preflight
responde `Análise: AUSENTE` e o pipeline morre depois de você já achar que instalou
tudo. O lanchador resolve o interpretador certo — a venv da skill — sozinho.

Se a venv sumir, recrie:

```bash
python3.11 -m venv ~/.claude/skills/corte-viral/.venv
~/.claude/skills/corte-viral/.venv/bin/python -m pip install -r ~/.claude/skills/corte-viral/requirements.txt
```

## O que já está feito

- venv Python 3.11 em `.venv/` com `pyyaml`, `jsonschema`, `numpy`, `Pillow` e
  `opencv-contrib-python==4.10.0.84` (enquadramento por locutor ativo funcionando);
- os 8 subagentes em `~/.claude/agents/`.

Falta apenas, e só se você quiser: `faster-whisper`, para transcrever vídeo sem
legenda pronta.

```bash
~/.claude/skills/corte-viral/.venv/bin/python -m pip install faster-whisper
```

## 1. Subagentes — quando reinstalar

Os 8 subagentes só existem para o Claude Code quando estão em `~/.claude/agents/`.
A pasta `agentes/` dentro da skill é a **fonte**, não o local de registro.

```bash
cp ~/.claude/skills/corte-viral/agentes/*.md ~/.claude/agents/
```

Rode de novo sempre que atualizar a skill. `verificar.py` acusa cópia defasada.

Os 8: `context-mapper`, `clip-hunter`, `clip-builder`, `feed-psychologist`,
`blind-reviewer`, `clip-deduplicator`, `edit-director`, `quality-controller`.

## 2. Dependências

### Obrigatórias

| | Para quê | Como |
| --- | --- | --- |
| `ffmpeg` + `ffprobe` | cortar, enquadrar, renderizar, medir | `brew install ffmpeg` |
| `pyyaml` | ler config e perfis | já na venv |
| `jsonschema` | validar os 15 artefatos | já na venv |

### O ffmpeg desta máquina não tem libass

Medido: `ffmpeg -filters` não lista `ass` nem `subtitles`. Queimar legenda por esse
caminho é impossível aqui. Não afeta o padrão — esta skill entrega o vertical limpo
e a `motion-vox` queima a legenda dela por outro caminho (Pillow + `overlay`).
Só não ligue `make_captioned_version` esperando que funcione.

Sem `jsonschema` a validação de artefato passa vazia — e é ela que segura a
qualidade do pipeline. Não trate como opcional.

### Opcionais

| | Para quê | Sem ela |
| --- | --- | --- |
| `faster-whisper` | transcrever quando não há legenda pronta | precisa fornecer transcript |
| `opencv-contrib-python` + `numpy` | enquadramento por locutor ativo | anchor manual por segmento |
| `Pillow` | utilidades de imagem | sem impacto no caminho principal |

Tudo de uma vez:

```bash
pip3 install -r ~/.claude/skills/corte-viral/requirements.txt
```

### O pin do OpenCV não é capricho

```bash
pip3 uninstall -y opencv-python opencv-python-headless opencv-contrib-python
pip3 install "opencv-contrib-python==4.10.0.84"
```

Sem versão, o pip trava no 5.0.0, que removeu `cv2.dnn.readNetFromCaffe` e não
empacota os haarcascades — quebra os dois detectores.

`mediapipe` foi testado e **descartado**: a variante Tasks API trava com
`Check failed: service_ Service is unavailable` ao inicializar o `DrishtiMetalHelper`
neste ambiente, mesmo forçando `delegate=CPU`. Não insista.

## 3. Verificar

```bash
python3 ~/.claude/skills/corte-viral/verificar.py
```

Verde em tudo que é obrigatório = pronto. Rode antes do primeiro projeto: é mais
barato descobrir agora do que no meio de uma run que já gastou a transcrição.

## 4. Testes

```bash
cd ~/.claude/skills/corte-viral && python3 -m unittest discover -s tests -t . -q
```

Os testes de `autoframe` pulam sozinhos quando `cv2`/`numpy` não estão instalados.

## Invocação

A skill é invocável pelo modelo: basta pedir "corta esse podcast",
"o que vira Short disso", "deixa esse corte vertical". Para chamar direto:

```text
/corte-viral <video.mp4> [transcript.vtt] --mode full
```

Sempre com `--workspace <pasta-do-projeto>/runs` no `init`, senão a run é gravada
dentro de `~/.claude/skills/` e some da vista.

## Se instalar em outro caminho

Uma linha muda: o bloco `allowed-tools` do `SKILL.md`, que pré-aprova
`python3 ~/.claude/skills/corte-viral/scripts/vch.py`. O código Python resolve o
próprio caminho sozinho (`PROJECT_ROOT`) e não precisa de ajuste.
