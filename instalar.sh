#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

SUDO=""
if [[ "${EUID}" -ne 0 ]]; then
  SUDO="sudo"
fi

echo "[1/6] Actualizando sistema..."
$SUDO apt update
$SUDO apt upgrade -y

echo "[2/6] Instalando dependencias base..."
$SUDO apt install -y curl git python3 python3-pip python3-venv python3-full nodejs npm

echo "[3/6] Instalando herramientas Kali..."
$SUDO apt install -y nmap sqlmap metasploit-framework aircrack-ng hashcat john

echo "[4/6] Instalando Ollama..."
if ! command -v ollama >/dev/null 2>&1; then
  curl -fsSL https://ollama.com/install.sh | sh
fi

echo "[5/6] Instalando dependencias Python..."
python3 -m pip install --break-system-packages --upgrade pip
python3 -m pip install --break-system-packages -r requirements.txt

echo "[5.1/6] Preparando Open WebUI..."
bash webui/setup-webui.sh

echo "[6/6] Descargando modelo Mistral..."
(ollama serve >/tmp/ollama-install.log 2>&1 &) || true
sleep 3
ollama pull mistral || true

chmod +x instalar.sh start-stack.sh agente-ia.py chat-ia.py ejecutar.py webui/setup-webui.sh webui/start-webui.sh kali-tools/*.py

echo "Instalación completada. Ejecuta: bash start-stack.sh"
