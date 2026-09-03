#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shlex
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable

import requests


BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
REPORT_DIR = BASE_DIR / "reports"
CACHE_DIR = BASE_DIR / ".cache"
OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "mistral"


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
    for folder in (LOG_DIR, REPORT_DIR, CACHE_DIR):
        folder.mkdir(parents=True, exist_ok=True)


def repo_path(*parts: str) -> Path:
    return BASE_DIR.joinpath(*parts)


def is_critical_command(command: str) -> bool:
    c = command.lower()
    return any(token in c for token in CRITICAL_TOKENS)


def confirm(message: str) -> bool:
    value = input(f"{message} (s/N): ").strip().lower()
    return value in {"s", "si", "sí", "y", "yes"}


def append_log(path: str | Path, text: str) -> None:
    ensure_dirs()
    stamp = datetime.now().isoformat(timespec="seconds")
    log_path = Path(path)
    if not log_path.is_absolute():
        log_path = repo_path(log_path.as_posix())
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{stamp}] {text}\n")


def build_command(program: str, *args: object, extra: str = "") -> str:
    parts = [shlex.quote(str(program))]
    parts.extend(shlex.quote(str(arg)) for arg in args if str(arg))
    if extra.strip():
        parts.append(extra.strip())
    return " ".join(parts)


def run_command(
    command: str,
    require_confirmation: bool = True,
    timeout: int = 900,
    cwd: str | Path | None = None,
) -> Dict[str, Any]:
    ensure_dirs()
    if require_confirmation and is_critical_command(command):
        if not confirm(f"Comando crítico detectado: {command}. ¿Ejecutar?"):
            return {"command": command, "status": "cancelled", "returncode": 130, "stdout": "", "stderr": "Cancelado"}

    append_log(LOG_DIR / "commands.log", f"RUN {command}")
    proc = subprocess.run(
        command,
        shell=True,
        text=True,
        capture_output=True,
        timeout=timeout,
        cwd=str(cwd or BASE_DIR),
    )
    append_log(LOG_DIR / "commands.log", f"EXIT {proc.returncode} {command}")
    return {
        "command": command,
        "status": "ok" if proc.returncode == 0 else "error",
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def analyze_with_ai(title: str, content: str, model: str = DEFAULT_MODEL, timeout: int = 120) -> str:
    prompt = (
        f"Analiza en español el siguiente resultado de {title}. "
        "Resume hallazgos, riesgos potenciales y próximos pasos recomendados.\n\n"
        f"{content[:12000]}"
    )
    payload = {"model": model, "prompt": prompt, "stream": False}
    response = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
    response.raise_for_status()
    return response.json().get("response", "").strip()


def write_json_report(name: str, payload: Dict[str, Any]) -> Path:
    ensure_dirs()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    file_name = f"{name}-{stamp}.json"
    report_path = REPORT_DIR / file_name
    report_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return report_path


def parse_nmap_discovery(output: str) -> list[dict[str, str]]:
    hosts: list[dict[str, str]] = []
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("Nmap scan report for "):
            target = line.replace("Nmap scan report for ", "", 1).strip()
            match = re.match(r"(.+?) \(([\dA-Fa-f:\.]+)\)$", target)
            if match:
                hosts.append({"name": match.group(1), "address": match.group(2)})
            else:
                hosts.append({"name": target, "address": target})
    return hosts


def parse_nmap_services(output: str) -> dict[str, list[dict[str, str]]]:
    services: dict[str, list[dict[str, str]]] = {}
    current_host = ""
    for raw_line in output.splitlines():
        line = raw_line.rstrip()
        if line.startswith("Nmap scan report for "):
            current_host = line.replace("Nmap scan report for ", "", 1).strip()
            services.setdefault(current_host, [])
            continue
        stripped = line.strip()
        if not current_host or not stripped or "/tcp" not in stripped or " open " not in stripped:
            continue
        parts = stripped.split()
        if len(parts) < 3:
            continue
        services[current_host].append(
            {
                "port": parts[0],
                "state": parts[1],
                "service": parts[2],
                "details": " ".join(parts[3:]).strip(),
            }
        )
    return services


HASH_SIGNATURES = [
    {"name": "bcrypt", "pattern": re.compile(r"^\$2[aby]\$"), "hashcat_mode": "3200", "john_format": "bcrypt"},
    {"name": "md5", "pattern": re.compile(r"^[a-fA-F0-9]{32}$"), "hashcat_mode": "0", "john_format": "raw-md5"},
    {"name": "sha1", "pattern": re.compile(r"^[a-fA-F0-9]{40}$"), "hashcat_mode": "100", "john_format": "raw-sha1"},
    {"name": "ntlm", "pattern": re.compile(r"^[a-fA-F0-9]{32}$"), "hashcat_mode": "1000", "john_format": "nt"},
    {"name": "sha256", "pattern": re.compile(r"^[a-fA-F0-9]{64}$"), "hashcat_mode": "1400", "john_format": "raw-sha256"},
    {"name": "sha512", "pattern": re.compile(r"^[a-fA-F0-9]{128}$"), "hashcat_mode": "1700", "john_format": "raw-sha512"},
]


def extract_hash_candidate(line: str) -> str:
    candidate = line.strip()
    if ":" in candidate and not candidate.startswith("$2"):
        parts = [part.strip() for part in candidate.split(":") if part.strip()]
        if parts:
            candidate = max(parts, key=len)
    return candidate


def detect_hash_type(sample: str) -> dict[str, str]:
    candidate = extract_hash_candidate(sample)
    if re.fullmatch(r"[a-fA-F0-9]{32}", candidate):
        return {
            "name": "md5/ntlm",
            "hashcat_mode": "0",
            "john_format": "raw-md5",
            "sample": candidate,
        }
    for signature in HASH_SIGNATURES:
        if signature["pattern"].match(candidate):
            return {
                "name": str(signature["name"]),
                "hashcat_mode": str(signature["hashcat_mode"]),
                "john_format": str(signature["john_format"]),
                "sample": candidate,
            }
    return {"name": "desconocido", "hashcat_mode": "", "john_format": "", "sample": candidate}


def suggest_wordlists(hash_name: str) -> list[str]:
    suggestions = [
        "/usr/share/wordlists/rockyou.txt",
        "/usr/share/seclists/Passwords/Common-Credentials/10k-most-common.txt",
    ]
    if "bcrypt" in hash_name.lower():
        suggestions.append("/usr/share/seclists/Passwords/darkweb2017-top10000.txt")
    return suggestions


def pick_existing_path(paths: Iterable[str]) -> str:
    for path in paths:
        if Path(path).exists():
            return path
    return next(iter(paths), "")
