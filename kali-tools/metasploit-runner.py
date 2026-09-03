#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from datetime import datetime
from pathlib import Path

from utils import analyze_with_ai, build_command, repo_path, run_command, write_json_report


def build_resource_file(args: argparse.Namespace) -> Path:
    log_name = f"metasploit-session-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
    lines = [f"spool {repo_path('logs', log_name)}"]
    if args.search:
        lines.append(f"search {args.search}")
    if args.module:
        lines.append(f"use {args.module}")
        if args.rhost:
            lines.append(f"set RHOSTS {args.rhost}")
        if args.rport:
            lines.append(f"set RPORT {args.rport}")
        if args.payload:
            lines.append(f"set PAYLOAD {args.payload}")
        if args.lhost:
            lines.append(f"set LHOST {args.lhost}")
        for option in args.option:
            key, _, value = option.partition("=")
            if key and value:
                lines.append(f"set {key.strip()} {value.strip()}")
        lines.append("run")
    lines.extend(["spool off", "exit -y"])

    handle = tempfile.NamedTemporaryFile("w", suffix=".rc", prefix="metasploit-", delete=False)
    with handle:
        handle.write("\n".join(lines) + "\n")
    return Path(handle.name)


def main() -> None:
    parser = argparse.ArgumentParser(description="Wrapper para msfconsole con logging y sugerencias IA")
    parser.add_argument("-r", "--resource", help="Archivo .rc existente")
    parser.add_argument("--search", default="", help="Término de búsqueda de módulos")
    parser.add_argument("--module", default="", help="Módulo a usar automáticamente")
    parser.add_argument("--rhost", default="", help="Objetivo RHOSTS")
    parser.add_argument("--rport", default="", help="Puerto RPORT")
    parser.add_argument("--payload", default="", help="Payload opcional")
    parser.add_argument("--lhost", default="", help="LHOST opcional")
    parser.add_argument(
        "--option",
        action="append",
        default=[],
        help="Opciones extra en formato CLAVE=VALOR (repetible)",
    )
    parser.add_argument("--ia", action="store_true", help="Solicitar sugerencias IA")
    parser.add_argument("-o", "--output", default="", help="Ruta opcional del reporte JSON")
    args = parser.parse_args()

    if not args.resource and not args.search and not args.module:
        parser.error("Debes indicar --resource, --search o --module")
    if args.resource and not Path(args.resource).exists():
        parser.error(f"No existe el recurso indicado: {args.resource}")

    resource_path = Path(args.resource) if args.resource else build_resource_file(args)
    cmd = build_command("msfconsole", "-q", "-r", resource_path)
    result = run_command(cmd, require_confirmation=True, timeout=1800)
    ai_analysis = ""
    if args.ia:
        summary_source = result.get("stdout") or result.get("stderr") or args.search or args.module
        try:
            ai_analysis = analyze_with_ai("Metasploit", str(summary_source))
        except Exception as exc:
            ai_analysis = f"Error en análisis IA: {exc}"

    report = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "tool": "metasploit",
        "command": cmd,
        "resource_file": str(resource_path),
        "search": args.search,
        "module": args.module,
        "result": result,
        "ai_analysis": ai_analysis,
    }
    report_path = write_json_report("metasploit-report", report)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nReporte guardado en: {report_path}")


if __name__ == "__main__":
    main()
