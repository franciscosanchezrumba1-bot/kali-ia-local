#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from utils import analyze_with_ai, build_command, run_command, write_json_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Automatiza sqlmap con logging y reportes")
    parser.add_argument("-u", "--url", required=True, help="URL objetivo")
    parser.add_argument("--data", default="", help="Payload POST opcional")
    parser.add_argument("--cookie", default="", help="Cookie opcional")
    parser.add_argument("--headers", default="", help="Cabeceras adicionales")
    parser.add_argument("--params", default="", help="Parámetros extra para sqlmap")
    parser.add_argument("--risk", default="1", choices=["1", "2", "3"])
    parser.add_argument("--level", default="1", choices=["1", "2", "3", "4", "5"])
    parser.add_argument("--crawl", default="", help="Profundidad de crawl opcional")
    parser.add_argument("--extra", default="", help="Argumentos extra para sqlmap")
    parser.add_argument("--ia", action="store_true", help="Analizar salida con IA local")
    parser.add_argument("-o", "--output", default="", help="Ruta opcional del reporte JSON")
    args = parser.parse_args()

    extra_parts = [f"--risk={args.risk}", f"--level={args.level}", "--batch"]
    if args.data:
        extra_parts.append(f"--data {json.dumps(args.data)}")
    if args.cookie:
        extra_parts.append(f"--cookie {json.dumps(args.cookie)}")
    if args.headers:
        extra_parts.append(f"--headers {json.dumps(args.headers)}")
    if args.params:
        extra_parts.append(args.params)
    if args.crawl:
        extra_parts.append(f"--crawl={args.crawl}")
    if args.extra:
        extra_parts.append(args.extra)

    cmd = build_command("sqlmap", "-u", args.url, extra=" ".join(extra_parts))

    result = run_command(cmd, require_confirmation=True)
    ai_analysis = ""
    if args.ia and result.get("stdout"):
        try:
            ai_analysis = analyze_with_ai("sqlmap", str(result["stdout"]))
        except Exception as exc:
            ai_analysis = f"Error en análisis IA: {exc}"

    report = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "tool": "sqlmap",
        "command": cmd,
        "result": result,
        "ai_analysis": ai_analysis,
    }

    out = write_json_report("sqlmap-report", report)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nReporte guardado en: {out}")


if __name__ == "__main__":
    main()
