# Kali Tools

Incluye wrappers para:
- `nmap-scanner.py`
- `sqlmap-wrapper.py`
- `metasploit-runner.py`
- `network-recon.py`
- `password-cracker.py`

Todos usan confirmación para comandos críticos y generan logs/reportes.

## Ejemplos

```bash
python3 kali-tools/sqlmap-wrapper.py -u "https://target.com/page.php?id=1" --ia
python3 kali-tools/metasploit-runner.py --search "wordpress" --ia
python3 kali-tools/password-cracker.py -f hashes.txt --ia
python3 kali-tools/network-recon.py -n 192.168.1.0/24 --ia
```

## Casos de uso

- Enumeración de puertos y servicios con análisis IA.
- Búsqueda guiada de módulos de Metasploit.
- Automatización básica de `sqlmap` con parámetros, cookies y cabeceras.
- Detección simple de tipo de hash y sugerencias de diccionarios.
