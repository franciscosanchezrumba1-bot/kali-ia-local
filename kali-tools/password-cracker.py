#!/usr/bin/env python3
from __future__ import annotations

import argparse

from utils import run_command


def main() -> None:
    parser = argparse.ArgumentParser(description="Wrapper básico para hashcat/john")
    parser.add_argument("--tool", choices=["hashcat", "john"], required=True)
    parser.add_argument("--hash-file", required=True)
    parser.add_argument("--wordlist", required=True)
    parser.add_argument("--mode", default="0", help="Modo hashcat (solo hashcat)")
    args = parser.parse_args()

    if args.tool == "hashcat":
        cmd = f"hashcat -m {args.mode} -a 0 '{args.hash_file}' '{args.wordlist}'"
    else:
        cmd = f"john --wordlist='{args.wordlist}' '{args.hash_file}'"

    result = run_command(cmd, require_confirmation=True, timeout=3600)
    print(result.get("stdout", ""))
    if result.get("stderr"):
        print(result["stderr"])


if __name__ == "__main__":
    main()
