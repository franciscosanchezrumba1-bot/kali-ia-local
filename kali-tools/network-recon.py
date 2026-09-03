#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from utils import analyze_with_ai, build_command, parse_nmap_discovery, parse_nmap_services, run_command, write_json_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Reconocimiento de red automatizado con descubrimiento y puertos")
    parser.add_argument("-n", "--network", required=True, help="Red objetivo (ej: 192.168.1.0/24)")
    parser.add_argument("--top-ports", default="20", help="Cantidad de puertos top para el escaneo detallado")
    parser.add_argument("--ia", action="store_true", help="Analizar resultados con IA local")
    parser.add_argument("-o", "--output", default="", help="Ruta opcional del reporte JSON")
    args = parser.parse_args()

    discovery_cmd = build_command("nmap", "-sn", args.network)
    discovery_result = run_command(discovery_cmd, require_confirmation=True)
    hosts = parse_nmap_discovery(str(discovery_result.get("stdout", "")))

    detail_result = {"status": "skipped", "stdout": "", "stderr": "", "returncode": 0}
    network_map: dict[str, list[dict[str, str]]] = {}
    if hosts:
        targets = " ".join(host["address"] for host in hosts)
        detail_cmd = build_command("nmap", "-sV", "--top-ports", args.top_ports, extra=targets)
        detail_result = run_command(detail_cmd, require_confirmation=True)
        network_map = parse_nmap_services(str(detail_result.get("stdout", "")))
    else:
        detail_cmd = ""

    ai_analysis = ""
    if args.ia:
        combined = (
            f"Descubrimiento:\n{discovery_result.get('stdout', '')}\n\n"
            f"Puertos:\n{detail_result.get('stdout', '')}"
        )
        try:
            ai_analysis = analyze_with_ai("reconocimiento de red", combined)
        except Exception as exc:
            ai_analysis = f"Error en análisis IA: {exc}"

    report = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "network": args.network,
        "discovery_command": discovery_cmd,
        "detail_command": detail_cmd,
        "discovery_result": discovery_result,
        "hosts": hosts,
        "detail_result": detail_result,
        "network_map": network_map,
        "ai_analysis": ai_analysis,
    }
    out = write_json_report("network-recon-report", report)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nReporte guardado en: {out}")


if __name__ == "__main__":
    main()
