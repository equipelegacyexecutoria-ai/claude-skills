#!/usr/bin/env bash
# Avisos sonoros do Claude Code:
#   aviso-sonoro.sh start    -> UserPromptSubmit: grava o horario de inicio do turno
#   aviso-sonoro.sh stop     -> Stop: se o turno passou de LIMITE segundos, toca o som de "terminei"
#   aviso-sonoro.sh atencao  -> Notification: o Claude precisa de voce (permissao, pergunta) - toca sempre
LIMITE=60
DIR="${TMPDIR:-/tmp}/claude-aviso-sonoro"
mkdir -p "$DIR"

# Toca um .wav do Windows ate o fim (PlaySync: o processo so sai depois do som).
tocar() {
  powershell.exe -NoProfile -NonInteractive -Command "(New-Object System.Media.SoundPlayer 'C:\\Windows\\Media\\$1').PlaySync()"
}

payload="$(cat)"
sid="$(printf '%s' "$payload" | grep -o '"session_id" *: *"[^"]*"' | head -1 | sed 's/.*"\([^"]*\)"$/\1/')"
[ -n "$sid" ] || sid="default"
arq="$DIR/$sid"

case "$1" in
  start)
    date +%s > "$arq"
    ;;
  stop)
    [ -f "$arq" ] || exit 0
    inicio="$(cat "$arq")"
    rm -f "$arq"
    agora="$(date +%s)"
    if [ $((agora - inicio)) -ge "$LIMITE" ]; then
      tocar 'tada.wav'
    fi
    ;;
  atencao)
    tocar 'Windows Notify System Generic.wav'
    ;;
esac
exit 0
