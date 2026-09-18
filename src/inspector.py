#!/usr/bin/env python3
"""
sre-health-inspector
Lightweight SRE diagnostic CLI for SSL/TLS certificate monitoring and endpoint telemetry.
"""

import argparse
from datetime import datetime, timezone
import json
import socket
import ssl
import sys
import time
from typing import Any, Dict, List, Optional
import urllib.parse
import urllib.request


def check_ssl_certificate(
    hostname: str, port: int = 443, timeout: float = 5.0, warn_days: int = 30
) -> Dict[str, Any]:
    """
    Connects to a host via TLS and extracts certificate expiration and issuer details.

    Args:
        hostname: Target hostname.
        port: TLS port (default 443).
        timeout: Connection timeout in seconds.
        warn_days: Days remaining threshold below which status becomes WARNING.
    """
    result: Dict[str, Any] = {
        "target": f"{hostname}:{port}",
        "check": "ssl_certificate",
        "status": "UNKNOWN",
        "days_remaining": None,
        "expiration_date": None,
        "issuer": None,
        "error": None,
    }

    context = ssl.create_default_context()
    try:
        with socket.create_connection((hostname, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                if not cert:
                    result["status"] = "CRITICAL"
                    result["error"] = "Peer provided no certificate"
                    return result

                # Parse notAfter date string: 'May 15 12:00:00 2026 GMT'
                not_after_str = cert["notAfter"]
                not_after = datetime.strptime(not_after_str, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                delta = not_after - now
                days_left = delta.days

                # Issuer organization
                issuer_dict = dict(x[0] for x in cert.get("issuer", []))
                issuer_org = issuer_dict.get("organizationName", "Unknown")

                result["days_remaining"] = days_left
                result["expiration_date"] = not_after.isoformat()
                result["issuer"] = issuer_org

                if days_left < 0:
                    result["status"] = "EXPIRED"
                elif days_left <= 14:
                    result["status"] = "CRITICAL"
                elif days_left <= warn_days:
                    result["status"] = "WARNING"
                else:
                    result["status"] = "HEALTHY"

    except Exception as exc:
        result["status"] = "ERROR"
        result["error"] = str(exc)

    return result


def check_http_endpoint(url: str, expected_status: int = 200, timeout: float = 5.0) -> Dict[str, Any]:
    """
    Executes an HTTP/HTTPS GET request and records latency and status response.
    """
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    parsed = urllib.parse.urlparse(url)
    result: Dict[str, Any] = {
        "url": url,
        "check": "http_endpoint",
        "status": "UNKNOWN",
        "status_code": None,
        "latency_ms": None,
        "error": None,
    }

    start_time = time.perf_counter()
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "SRE-Health-Inspector/1.0 (DevOps SRE Probe)"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            latency = (time.perf_counter() - start_time) * 1000.0
            result["latency_ms"] = round(latency, 2)
            result["status_code"] = response.getcode()

            if response.getcode() == expected_status:
                result["status"] = "HEALTHY"
            else:
                result["status"] = "WARNING"

    except urllib.error.HTTPError as http_err:
        latency = (time.perf_counter() - start_time) * 1000.0
        result["latency_ms"] = round(latency, 2)
        result["status_code"] = http_err.code
        result["status"] = "HEALTHY" if http_err.code == expected_status else "WARNING"
        result["error"] = f"HTTP {http_err.code}"
    except Exception as exc:
        result["status"] = "ERROR"
        result["error"] = str(exc)

    return result


def check_tcp_port(host: str, port: int, timeout: float = 3.0) -> Dict[str, Any]:
    """
    Verifies TCP handshake connectivity on a remote port.
    """
    result: Dict[str, Any] = {
        "target": f"{host}:{port}",
        "check": "tcp_port",
        "status": "UNKNOWN",
        "latency_ms": None,
        "error": None,
    }

    start_time = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            latency = (time.perf_counter() - start_time) * 1000.0
            result["latency_ms"] = round(latency, 2)
            result["status"] = "HEALTHY"
    except Exception as exc:
        result["status"] = "DOWN"
        result["error"] = str(exc)

    return result


def format_summary(results: List[Dict[str, Any]]) -> str:
    """
    Renders a one-line summary of status counts across all probes.
    """
    counts: Dict[str, int] = {}
    for r in results:
        s = r.get("status", "UNKNOWN")
        counts[s] = counts.get(s, 0) + 1

    parts = [f"{status}: {count}" for status, count in sorted(counts.items())]
    return "Summary → " + "  |  ".join(parts)


def format_table(results: List[Dict[str, Any]]) -> str:
    """
    Renders structured results as a clean ASCII tabular dashboard.
    """
    lines = []
    header = f"{'CHECK':<16} | {'TARGET':<35} | {'STATUS':<10} | {'METRICS / DETAIL'}"
    sep = "-" * len(header)
    lines.append(header)
    lines.append(sep)

    for r in results:
        check_type = r.get("check", "")
        target = str(r.get("target") or r.get("url", ""))[:35]
        status = r.get("status", "")

        detail = ""
        if check_type == "ssl_certificate":
            if r.get("days_remaining") is not None:
                detail = f"Expires in {r['days_remaining']} days (Issuer: {r['issuer']})"
            else:
                detail = f"Error: {r['error']}"
        elif check_type == "http_endpoint":
            if r.get("latency_ms") is not None:
                detail = f"HTTP {r['status_code']} ({r['latency_ms']} ms)"
            else:
                detail = f"Error: {r['error']}"
        elif check_type == "tcp_port":
            if r.get("latency_ms") is not None:
                detail = f"Connection established ({r['latency_ms']} ms)"
            else:
                detail = f"Error: {r['error']}"

        lines.append(f"{check_type:<16} | {target:<35} | {status:<10} | {detail}")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="sre-health-inspector: Production-ready endpoint and TLS certificate health probe."
    )
    parser.add_argument("--ssl", nargs="+", help="Hostnames to inspect TLS certificates (e.g. google.com api.github.com)")
    parser.add_argument("--http", nargs="+", help="HTTP/HTTPS URLs to probe for latency and status codes")
    parser.add_argument("--tcp", nargs="+", help="TCP targets formatted as host:port (e.g. 10.0.1.10:5432)")
    parser.add_argument("--timeout", type=float, default=5.0, help="Probe timeout in seconds (Default: 5.0)")
    parser.add_argument("--warn-days", type=int, default=30, dest="warn_days",
                        help="SSL WARNING threshold in days before expiration (Default: 30)")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()

    if not args.ssl and not args.http and not args.tcp:
        parser.print_help()
        return 2

    results: List[Dict[str, Any]] = []

    if args.ssl:
        for host in args.ssl:
            port = 443
            if ":" in host:
                parts = host.split(":")
                host = parts[0]
                port = int(parts[1])
            results.append(check_ssl_certificate(host, port, timeout=args.timeout, warn_days=args.warn_days))

    if args.http:
        for url in args.http:
            results.append(check_http_endpoint(url, timeout=args.timeout))

    if args.tcp:
        for target in args.tcp:
            if ":" not in target:
                sys.stderr.write(f"Invalid TCP target format: {target}. Must be host:port\n")
                continue
            h, p = target.split(":", 1)
            results.append(check_tcp_port(h, int(p), timeout=args.timeout))

    if args.json:
        print(json.dumps({"probe_timestamp": datetime.now(timezone.utc).isoformat(), "results": results}, indent=2))
    else:
        print("\n=== SRE HEALTH INSPECTOR // REPORT ===")
        print(format_table(results))
        print("--------------------------------------")
        print(format_summary(results))
        print("======================================\n")

    # Determine exit status
    has_critical = any(r.get("status") in ("CRITICAL", "EXPIRED", "ERROR", "DOWN") for r in results)
    return 1 if has_critical else 0


if __name__ == "__main__":
    sys.exit(main())
