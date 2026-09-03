#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"
mkdir -p logs

echo "==> Iniciando stack Kali + IA local..."

if ! command -v ollama >/dev/null 2>&1; then
  echo "Ollama no encontrado. Instalando..."
  curl -fsSL https://ollama.com/install.sh | sh
fi

if ! pgrep -f "ollama serve" >/dev/null 2>&1; then
  nohup ollama serve > logs/ollama.log 2>&1 &
  sleep 3
fi

ollama pull mistral >/dev/null 2>&1 || true

if ! pgrep -f "open-webui" >/dev/null 2>&1; then
  nohup bash webui/start-webui.sh > logs/webui.log 2>&1 &
fi

if ! pgrep -f "agente-ia.py --listen" >/dev/null 2>&1; then
  nohup python3 agente-ia.py --listen > logs/agente.log 2>&1 &
fi

echo "✅ Stack iniciado"
echo "- Ollama API: http://localhost:11434"
echo "- Open WebUI: http://localhost:8080"
echo "- Logs: $ROOT_DIR/logs"
