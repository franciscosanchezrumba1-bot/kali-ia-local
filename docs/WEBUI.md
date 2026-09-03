# Open WebUI

Instalar:
```bash
bash webui/setup-webui.sh
```

Instalación con servicio opcional:
```bash
bash webui/setup-webui.sh --systemd
```

Iniciar:
```bash
bash webui/start-webui.sh
```

Acceso: `http://localhost:8080`

## Configuración

- Puerto: `8080`
- Ollama: `http://localhost:11434`
- Config file: `webui/config.json`

## Alternativa Docker

```bash
docker compose -f webui/docker-compose.yml up -d
```
