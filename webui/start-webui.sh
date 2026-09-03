#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR/webui"
CONFIG_FILE="$ROOT_DIR/webui/config.json"

HOST="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8")).get("host", "0.0.0.0"))' "$CONFIG_FILE")"
PORT="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8")).get("port", 8080))' "$CONFIG_FILE")"
OLLAMA_URL="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8")).get("ollama_base_url", "http://localhost:11434"))' "$CONFIG_FILE")"

if [[ -d .venv ]]; then
  source .venv/bin/activate
fi

if command -v open-webui >/dev/null 2>&1; then
  export OLLAMA_BASE_URL="$OLLAMA_URL"
  echo "✅ Open WebUI iniciando en http://localhost:$PORT"
  echo "✅ Ollama conectado en $OLLAMA_URL"
  exec open-webui serve --host "$HOST" --port "$PORT"
else
  echo "open-webui no está instalado. Ejecuta primero: bash webui/setup-webui.sh" >&2
  exit 1
fi
