# Instalación completa

## Requisitos
- Kali Linux (o Debian/Ubuntu compatibles)
- Python 3.10+
- Acceso a internet

## Pasos
```bash
git clone https://github.com/franciscosanchezrumba1-bot/kali-ia-local.git
cd kali-ia-local
bash instalar.sh
bash start-stack.sh
```

## Verificación rápida
```bash
python3 chat-ia.py
python3 agente-ia.py "escanea 192.168.1.1 con nmap"
python3 kali-tools/nmap-scanner.py -t 192.168.1.1 -i
```
