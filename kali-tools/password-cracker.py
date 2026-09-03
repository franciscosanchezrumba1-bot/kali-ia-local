#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from utils import (
    analyze_with_ai,
    build_command,
    detect_hash_type,
    pick_existing_path,
    run_command,
    suggest_wordlists,
    write_json_report,
)


def first_hash_line(hash_file: Path) -> str:
    for line in hash_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.strip():
            return line.strip()
    return ""


def main() -> None:
    parser = argparse.ArgumentParser(description="Wrapper para hashcat/john con autodetección de hashes")
    parser.add_argument("-f", "--hash-file", required=True, help="Archivo con hashes")
    parser.add_argument("--tool", choices=["auto", "hashcat", "john"], default="auto")
    parser.add_argument("--wordlist", default="", help="Diccionario opcional")
    parser.add_argument("--mode", default="", help="Modo hashcat opcional")
    parser.add_argument("--john-format", default="", help="Formato john opcional")
    parser.add_argument("--ia", action="store_true", help="Analizar resultados con IA local")
    parser.add_argument("-o", "--output", default="", help="Ruta opcional del reporte JSON")
    args = parser.parse_args()

    hash_file = Path(args.hash_file)
    if not hash_file.exists():
        parser.error(f"No existe el archivo de hashes: {hash_file}")
    sample = first_hash_line(hash_file)
    detected = detect_hash_type(sample) if sample else {"name": "desconocido", "hashcat_mode": "", "john_format": ""}
    suggestions = suggest_wordlists(str(detected.get("name", "")))
    chosen_wordlist = args.wordlist or pick_existing_path(suggestions) or suggestions[0]

    tool = args.tool
    if tool == "auto":
        tool = "hashcat" if detected.get("hashcat_mode") else "john"

    if tool == "hashcat":
        mode = args.mode or str(detected.get("hashcat_mode", "0"))
        cmd = build_command("hashcat", "-m", mode, "-a", "0", hash_file, chosen_wordlist)
        john_format = args.john_format or str(detected.get("john_format", ""))
        alternative_extra = f"--format={john_format}" if john_format else ""
        alternative_command = build_command("john", f"--wordlist={chosen_wordlist}", hash_file, extra=alternative_extra)
    else:
        john_format = args.john_format or str(detected.get("john_format", ""))
        extra = f"--format={john_format}" if john_format else ""
        cmd = build_command("john", f"--wordlist={chosen_wordlist}", hash_file, extra=extra)
        alternative_command = ""

    result = run_command(cmd, require_confirmation=True, timeout=3600)
    ai_analysis = ""
    if args.ia:
        analysis_text = (
            f"Tipo detectado: {detected.get('name')}\n"
            f"Sugerencias de diccionario: {', '.join(suggestions)}\n\n"
            f"Salida:\n{result.get('stdout', '') or result.get('stderr', '')}"
        )
        try:
            ai_analysis = analyze_with_ai("cracking de contraseñas", analysis_text)
        except Exception as exc:
            ai_analysis = f"Error en análisis IA: {exc}"

    report = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "tool": tool,
        "hash_file": str(hash_file),
        "detected_hash": detected,
        "suggested_wordlists": suggestions,
        "selected_wordlist": chosen_wordlist,
        "command": cmd,
        "alternative_command": alternative_command,
        "result": result,
        "ai_analysis": ai_analysis,
    }
    report_path = write_json_report("password-cracker-report", report)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nReporte guardado en: {report_path}")


if __name__ == "__main__":
    main()
