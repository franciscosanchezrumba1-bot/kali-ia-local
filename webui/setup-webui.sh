#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR/webui"

if ! command -v git >/dev/null 2>&1; then
  echo "git no instalado" >&2
  exit 1
fi

if [[ ! -d open-webui ]]; then
  git clone https://github.com/open-webui/open-webui.git
fi

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install open-webui

echo "Open WebUI instalado. Ejecuta: bash webui/start-webui.sh"
