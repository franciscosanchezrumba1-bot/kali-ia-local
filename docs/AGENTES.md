# Agentes autónomos

`agente-ia.py`:
- Lee prompts
- Pide plan a Ollama (Mistral)
- Extrae líneas `COMMAND:`
- Ejecuta secuencia con confirmación
- Guarda logs y reportes JSON

Modo escucha:
```bash
python3 agente-ia.py --listen
```
