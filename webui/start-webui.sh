#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR/webui"

if [[ -d .venv ]]; then
  source .venv/bin/activate
fi

if command -v open-webui >/dev/null 2>&1; then
  exec open-webui serve --host 0.0.0.0 --port 8080
else
  echo "open-webui no está instalado. Ejecuta primero: bash webui/setup-webui.sh" >&2
  exit 1
fi
