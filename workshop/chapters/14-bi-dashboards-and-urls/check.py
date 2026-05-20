#!/usr/bin/env python3
"""Chapter 14 checkpoint: verify Superset and Traefik are running."""

import sys
from socket import create_connection

import httpx


def _http_status_via_host_header(hostname: str) -> int:
    """Return an HTTP status from Traefik using an explicit Host header."""
    request = (
        f"GET / HTTP/1.1\r\nHost: {hostname}\r\n"
        "Connection: close\r\nUser-Agent: phlo-workshop-check\r\n\r\n"
    ).encode()
    with create_connection(("127.0.0.1", 80), timeout=10) as sock:
        sock.sendall(request)
        response = sock.recv(128).decode("ascii", errors="replace")
    status_line = response.splitlines()[0]
    return int(status_line.split()[1])


def check_superset() -> bool:
    """Check Superset is reachable."""
    try:
        resp = httpx.get(
            "http://127.0.0.1:8088/health", timeout=15, follow_redirects=True
        )
        if resp.status_code == 200:
            print("  \033[32m✓\033[0m Superset is reachable at http://localhost:8088")
            return True
        print(f"  \033[31m✗\033[0m Superset returned status {resp.status_code}")
        return False
    except Exception as e:
        print(f"  \033[31m✗\033[0m Superset unreachable: {e}")
        return False


def check_traefik() -> bool:
    """Check Traefik is serving the default route."""
    try:
        status_code = _http_status_via_host_header("traefik.phlo.localhost")
        if status_code < 500:
            print("  \033[32m✓\033[0m Traefik is serving requests")
            return True
        print(f"  \033[31m✗\033[0m Traefik returned status {status_code}")
        return False
    except Exception as e:
        print(f"  \033[31m✗\033[0m Traefik check failed: {e}")
        return False


def check_superset_named_url() -> bool:
    """Check superset.phlo.localhost is routable via Traefik."""
    try:
        status_code = _http_status_via_host_header("superset.phlo.localhost")
        if status_code < 500:
            print("  \033[32m✓\033[0m superset.phlo.localhost is reachable via Traefik")
            return True
        print(
            f"  \033[31m✗\033[0m superset.phlo.localhost returned status {status_code}"
        )
        return False
    except Exception as e:
        print(f"  \033[31m✗\033[0m superset.phlo.localhost unreachable: {e}")
        return False


def main() -> int:
    print("Chapter 14 — BI Dashboards & Named URLs\n")
    results = [
        check_superset(),
        check_traefik(),
        check_superset_named_url(),
    ]
    print()
    if all(results):
        print("\033[32mAll checks passed!\033[0m")
        return 0
    print("\033[31mSome checks failed.\033[0m")
    return 1


if __name__ == "__main__":
    sys.exit(main())
