#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from utils import run_command, ensure_dirs


def main() -> None:
    parser = argparse.ArgumentParser(description="Reconocimiento de red automatizado")
    parser.add_argument("-n", "--network", required=True, help="Red objetivo (ej: 192.168.1.0/24)")
    args = parser.parse_args()

    ensure_dirs()
    cmd = f"nmap -sn {args.network}"
    result = run_command(cmd, require_confirmation=True)
    report = {"command": cmd, "result": result}
    out = Path("reports/network-recon.json")
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
