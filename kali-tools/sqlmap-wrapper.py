#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from utils import run_command, ensure_dirs


def main() -> None:
    parser = argparse.ArgumentParser(description="Automatiza sqlmap con logging y reportes")
    parser.add_argument("-u", "--url", required=True, help="URL objetivo")
    parser.add_argument("--data", default="", help="Payload POST opcional")
    parser.add_argument("--risk", default="1", choices=["1", "2", "3"]) 
    parser.add_argument("--level", default="1", choices=["1", "2", "3", "4", "5"])
    parser.add_argument("--extra", default="", help="Argumentos extra para sqlmap")
    args = parser.parse_args()

    ensure_dirs()
    data_arg = f" --data '{args.data}'" if args.data else ""
    cmd = f"sqlmap -u '{args.url}' --risk={args.risk} --level={args.level} --batch{data_arg} {args.extra}".strip()

    result = run_command(cmd, require_confirmation=True)
    report = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "tool": "sqlmap",
        "command": cmd,
        "result": result,
    }

    out = Path("reports/sqlmap-report.json")
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
