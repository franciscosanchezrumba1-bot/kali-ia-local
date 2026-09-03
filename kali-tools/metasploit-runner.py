#!/usr/bin/env python3
from __future__ import annotations

import argparse

from utils import run_command


def main() -> None:
    parser = argparse.ArgumentParser(description="Ejecuta recursos de Metasploit con confirmación")
    parser.add_argument("-r", "--resource", required=True, help="Archivo .rc de Metasploit")
    args = parser.parse_args()

    cmd = f"msfconsole -q -r '{args.resource}'"
    result = run_command(cmd, require_confirmation=True, timeout=1800)
    print(result.get("stdout", ""))
    if result.get("stderr"):
        print(result["stderr"])


if __name__ == "__main__":
    main()
