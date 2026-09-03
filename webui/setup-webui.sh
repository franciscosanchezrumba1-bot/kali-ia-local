#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR/webui"
CONFIG_FILE="$ROOT_DIR/webui/config.json"
INSTALL_SYSTEMD=false

if [[ "${1:-}" == "--systemd" ]]; then
  INSTALL_SYSTEMD=true
fi

if ! command -v git >/dev/null 2>&1; then
  echo "git no instalado" >&2
  exit 1
fi

if [[ ! -d open-webui ]]; then
  git clone https://github.com/open-webui/open-webui.git
fi

if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
  echo "Node.js/npm no encontrados. Instálalos antes de continuar." >&2
  exit 1
fi

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install open-webui

if [[ -f open-webui/package.json ]]; then
  npm --prefix open-webui install
fi

PORT="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8")).get("port", 8080))' "$CONFIG_FILE")"
OLLAMA_URL="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8")).get("ollama_base_url", "http://localhost:11434"))' "$CONFIG_FILE")"

if [[ "$INSTALL_SYSTEMD" == true ]]; then
  SERVICE_PATH="/etc/systemd/system/open-webui-local.service"
  cat <<EOF | sudo tee "$SERVICE_PATH" >/dev/null
[Unit]
Description=Open WebUI local
After=network.target

[Service]
Type=simple
WorkingDirectory=$ROOT_DIR/webui
Environment=OLLAMA_BASE_URL=$OLLAMA_URL
ExecStart=$ROOT_DIR/webui/.venv/bin/open-webui serve --host 0.0.0.0 --port $PORT
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF
  sudo systemctl daemon-reload
  echo "Servicio systemd creado en $SERVICE_PATH"
fi

echo "Open WebUI instalado. Ejecuta: bash webui/start-webui.sh"
echo "Puerto configurado: $PORT"
echo "Ollama configurado: $OLLAMA_URL"
