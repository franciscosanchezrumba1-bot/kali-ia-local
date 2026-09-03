#!/usr/bin/env python3
import argparse
import subprocess

CRITICAL = ("rm ", "mkfs", "dd ", "shutdown", "reboot", "poweroff")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ejecuta comandos con confirmación")
    parser.add_argument("comando", help="Comando a ejecutar")
    args = parser.parse_args()

    cmd = args.comando
    if any(token in cmd for token in CRITICAL):
        ok = input(f"Comando crítico detectado: {cmd}\n¿Continuar? (s/N): ").strip().lower()
        if ok not in {"s", "si", "sí", "y", "yes"}:
            print("Cancelado")
            return

    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
