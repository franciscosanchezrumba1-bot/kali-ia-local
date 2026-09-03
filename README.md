# kali-ia-local

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Kali](https://img.shields.io/badge/Kali-Tools-success)
![Ollama](https://img.shields.io/badge/Ollama-Mistral%207B-orange)
![WebUI](https://img.shields.io/badge/Open%20WebUI-8080-purple)

Stack completo y automatizado que combina Kali Linux, IA local sin censura (Ollama + Mistral), agentes autónomos e interfaz web con Open WebUI.

## Estructura

```text
kali-ia-local/
├── README.md
├── INSTALACION.md
├── instalar.sh
├── start-stack.sh
├── requirements.txt
├── .gitignore
├── chat-ia.py
├── ejecutar.py
├── agente-ia.py
├── kali-tools/
├── webui/
├── docs/
└── config/
```

## Instalación (3 pasos)

```bash
git clone https://github.com/franciscosanchezrumba1-bot/kali-ia-local.git
cd kali-ia-local
bash instalar.sh
bash start-stack.sh
```

## Uso rápido

```bash
python3 chat-ia.py
python3 agente-ia.py "escanea 192.168.1.1 con nmap"
python3 kali-tools/nmap-scanner.py -t 192.168.1.1 -i
```

Open WebUI: http://localhost:8080

## Características

- IA local con modelo `mistral`
- Agente autónomo con confirmación de comandos críticos
- Integración de nmap/sqlmap/metasploit/hashcat/john
- Logging automático en `logs/`
- Reportes JSON en `reports/`
- Caché de escaneos en `.cache/`
