#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict


CRITICAL_TOKENS = (
    "sudo ",
    "rm ",
    "nmap",
    "sqlmap",
    "msfconsole",
    "hashcat",
    "john",
    "aircrack",
)


def ensure_dirs() -> None:
    for folder in ("logs", "reports", ".cache"):
        Path(folder).mkdir(parents=True, exist_ok=True)


def is_critical_command(command: str) -> bool:
    c = command.lower()
    return any(token in c for token in CRITICAL_TOKENS)


def confirm(message: str) -> bool:
    value = input(f"{message} (s/N): ").strip().lower()
    return value in {"s", "si", "sí", "y", "yes"}


def append_log(path: str, text: str) -> None:
    ensure_dirs()
    stamp = datetime.now().isoformat(timespec="seconds")
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"[{stamp}] {text}\n")


def run_command(command: str, require_confirmation: bool = True, timeout: int = 900) -> Dict[str, str | int]:
    ensure_dirs()
    if require_confirmation and is_critical_command(command):
        if not confirm(f"Comando crítico detectado: {command}. ¿Ejecutar?"):
            return {"command": command, "status": "cancelled", "returncode": 130, "stdout": "", "stderr": "Cancelado"}

    append_log("logs/commands.log", f"RUN {command}")
    proc = subprocess.run(command, shell=True, text=True, capture_output=True, timeout=timeout)
    append_log("logs/commands.log", f"EXIT {proc.returncode} {command}")
    return {
        "command": command,
        "status": "ok" if proc.returncode == 0 else "error",
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }
