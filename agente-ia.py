#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List

import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral"


def ensure_dirs() -> None:
    for d in ("logs", "reports", ".cache"):
        Path(d).mkdir(parents=True, exist_ok=True)


def log_line(text: str) -> None:
    ensure_dirs()
    with open("logs/agente-ia.log", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat(timespec='seconds')}] {text}\n")


def ask_ai(prompt: str) -> str:
    sys_prompt = (
        "Eres un planificador técnico para Kali Linux. Responde SOLO con pasos y comandos. "
        "Cada comando debe ir en una línea que empiece por 'COMMAND: '."
    )
    payload = {"model": MODEL, "prompt": f"{sys_prompt}\n\nUsuario: {prompt}", "stream": False}
    r = requests.post(OLLAMA_URL, json=payload, timeout=120)
    r.raise_for_status()
    return r.json().get("response", "").strip()


def fallback_commands(prompt: str) -> List[str]:
    p = prompt.lower()
    if "hash" in p or "crack" in p or "contrase" in p:
        return ["python3 kali-tools/password-cracker.py -f hashes.txt --ia"]
    if "metasploit" in p or "exploit" in p:
        return ["python3 kali-tools/metasploit-runner.py --search 'wordpress' --ia"]
    if "sql" in p or "sqlmap" in p:
        return ["python3 kali-tools/sqlmap-wrapper.py -u 'https://target.com/item.php?id=1' --ia"]
    if "red" in p or "/24" in p or "mapea" in p:
        return ["python3 kali-tools/network-recon.py -n 192.168.1.0/24 --ia"]
    if "nmap" in p or "puerto" in p or "escanea" in p:
        return ["python3 kali-tools/nmap-scanner.py -t 127.0.0.1 -p 22,80,443 -i"]
    return ["echo 'No se pudo inferir un comando. Ajusta el prompt.'"]


def extract_commands(plan: str) -> List[str]:
    cmds = []
    for line in plan.splitlines():
        line = line.strip()
        if line.lower().startswith("command:"):
            cmd = line.split(":", 1)[1].strip()
            if cmd:
                cmds.append(cmd)
    return cmds


def is_critical(cmd: str) -> bool:
    tokens = ("nmap", "sqlmap", "msfconsole", "hashcat", "john", "sudo ", "rm ")
    low = cmd.lower()
    return any(t in low for t in tokens)


def confirm(cmd: str) -> bool:
    ans = input(f"Confirmar ejecución de comando crítico:\n  {cmd}\n¿Continuar? (s/N): ").strip().lower()
    return ans in {"s", "si", "sí", "y", "yes"}


def run_sequence(commands: List[str]) -> List[dict]:
    results = []
    for cmd in commands:
        if is_critical(cmd) and not confirm(cmd):
            log_line(f"CANCELLED {cmd}")
            results.append({"command": cmd, "status": "cancelled", "returncode": 130})
            continue
        log_line(f"RUN {cmd}")
        proc = subprocess.run(cmd, shell=True, text=True, capture_output=True)
        result = {
            "command": cmd,
            "status": "ok" if proc.returncode == 0 else "error",
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
        log_line(f"EXIT {proc.returncode} {cmd}")
        results.append(result)
    return results


def save_report(prompt: str, plan: str, commands: List[str], results: List[dict]) -> Path:
    ensure_dirs()
    report = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "prompt": prompt,
        "plan": plan,
        "commands": commands,
        "results": results,
    }
    out = Path("reports") / f"agent-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return out


def run_prompt(prompt: str) -> None:
    try:
        plan = ask_ai(prompt)
    except Exception as exc:
        plan = f"Fallo consultando IA: {exc}"
    commands = extract_commands(plan)
    if not commands:
        commands = fallback_commands(prompt)
    print("Plan generado:\n", plan)
    print("\nComandos a ejecutar:")
    for c in commands:
        print(" -", c)
    results = run_sequence(commands)
    report_path = save_report(prompt, plan, commands, results)
    print(f"\nReporte guardado en: {report_path}")


def listen_mode() -> None:
    print("Agente en modo escucha. Escribe 'salir' para terminar.")
    while True:
        prompt = input("Prompt> ").strip()
        if prompt.lower() in {"salir", "exit", "quit"}:
            break
        if prompt:
            run_prompt(prompt)


def main() -> None:
    parser = argparse.ArgumentParser(description="Agente IA autónomo para Kali + Ollama")
    parser.add_argument("prompt", nargs="?", default="", help="Tarea a ejecutar")
    parser.add_argument("--listen", action="store_true", help="Modo escucha")
    args = parser.parse_args()

    if args.listen:
        listen_mode()
    elif args.prompt:
        run_prompt(args.prompt)
    else:
        parser.error("Debes indicar un prompt o usar --listen")


if __name__ == "__main__":
    main()
