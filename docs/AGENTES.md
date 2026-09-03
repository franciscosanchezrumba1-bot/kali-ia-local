# Agentes autónomos

`agente-ia.py`:
- Lee prompts
- Pide plan a Ollama (Mistral)
- Extrae líneas `COMMAND:`
- Ejecuta secuencia con confirmación
- Guarda logs y reportes JSON
- Sugiere wrappers Kali según el prompt

Modo escucha:
```bash
python3 agente-ia.py --listen
```

Tarea única:
```bash
python3 agente-ia.py "busca vulnerabilidades SQL injection en target.com"
```
