#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import requests

from utils import run_command, ensure_dirs


def analyze_with_ai(scan_output: str) -> str:
    prompt = (
        "Analiza este resultado de nmap en español y resume puertos abiertos, "
        "servicios y riesgos potenciales:\n\n" + scan_output[:12000]
    )
    payload = {"model": "mistral", "prompt": prompt, "stream": False}
    r = requests.post("http://localhost:11434/api/generate", json=payload, timeout=120)
    r.raise_for_status()
    return r.json().get("response", "").strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Wrapper de nmap con caché y análisis IA")
    parser.add_argument("-t", "--target", required=True, help="Objetivo (IP, rango o dominio)")
    parser.add_argument("-p", "--ports", default="", help="Puertos (ej. 22,80,443)")
    parser.add_argument("-i", "--ia", action="store_true", help="Analizar salida con IA local")
    parser.add_argument("-o", "--output", default="", help="Ruta de reporte JSON")
    args = parser.parse_args()

    ensure_dirs()
    cache_dir = Path(".cache/nmap")
    cache_dir.mkdir(parents=True, exist_ok=True)

    key = hashlib.sha256(f"{args.target}|{args.ports}".encode()).hexdigest()
    cache_file = cache_dir / f"{key}.json"

    if cache_file.exists():
        data = json.loads(cache_file.read_text(encoding="utf-8"))
    else:
        ports = f" -p {args.ports}" if args.ports else ""
        cmd = f"nmap -sV{ports} {args.target}"
        result = run_command(cmd, require_confirmation=True)
        data = {"command": cmd, "result": result, "ai_analysis": ""}
        if args.ia and result.get("stdout"):
            try:
                data["ai_analysis"] = analyze_with_ai(str(result["stdout"]))
            except Exception as exc:
                data["ai_analysis"] = f"Error en análisis IA: {exc}"
        cache_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    output_file = Path(args.output) if args.output else Path("reports/nmap-report.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
