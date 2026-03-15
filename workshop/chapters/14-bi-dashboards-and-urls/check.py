#!/usr/bin/env python3
"""Chapter 14 checkpoint: verify Superset and Traefik are running."""

import subprocess
import sys

import httpx


def check_superset() -> bool:
    """Check Superset is reachable."""
    try:
        resp = httpx.get(
            "http://localhost:8088/health", timeout=15, follow_redirects=True
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
    """Check Traefik container is running."""
    try:
        result = subprocess.run(
            ["docker", "compose", "-p", "pokemon-workshop", "-f", ".phlo/docker-compose.yml",
            "ps", "traefik", "--format", "{{.State}}"],
            capture_output=True, text=True, timeout=10,
        )
        state = result.stdout.strip().lower()
        if result.returncode == 0 and state in {"running", "healthy"}:
            print(f"  \033[32m✓\033[0m Traefik is running ({state})")
            return True
        print("  \033[31m✗\033[0m Traefik container is not running")
        return False
    except Exception as e:
        print(f"  \033[31m✗\033[0m Traefik check failed: {e}")
        return False


def check_superset_named_url() -> bool:
    """Check superset.phlo.localhost is routable via Traefik."""
    try:
        resp = httpx.get(
            "http://superset.phlo.localhost",
            timeout=10,
            follow_redirects=True,
        )
        if resp.status_code == 200:
            print("  \033[32m✓\033[0m superset.phlo.localhost is reachable via Traefik")
            return True
        print(
            f"  \033[31m✗\033[0m superset.phlo.localhost returned status {resp.status_code}"
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
