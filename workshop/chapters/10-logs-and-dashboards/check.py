#!/usr/bin/env python3
"""Chapter 10 checkpoint: verify Grafana, Loki, and Prometheus are running."""

import sys

import httpx


def check_grafana() -> bool:
    """Check Grafana is reachable."""
    try:
        resp = httpx.get("http://localhost:3100/api/health", timeout=10)
        if resp.status_code == 200:
            print("  \033[32m✓\033[0m Grafana is reachable at http://localhost:3100")
            return True
        print(f"  \033[31m✗\033[0m Grafana returned status {resp.status_code}")
        return False
    except Exception as e:
        print(f"  \033[31m✗\033[0m Grafana unreachable: {e}")
        return False


def check_prometheus() -> bool:
    """Check Prometheus is reachable."""
    try:
        resp = httpx.get("http://localhost:9090/-/ready", timeout=10)
        if resp.status_code == 200:
            print("  \033[32m✓\033[0m Prometheus is reachable at http://localhost:9090")
            return True
        print(f"  \033[31m✗\033[0m Prometheus returned status {resp.status_code}")
        return False
    except Exception as e:
        print(f"  \033[31m✗\033[0m Prometheus unreachable: {e}")
        return False


def check_prometheus_targets() -> bool:
    """Check Prometheus has at least one active target."""
    try:
        resp = httpx.get("http://localhost:9090/api/v1/targets", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            active = data.get("data", {}).get("activeTargets", [])
            if active:
                print(f"  \033[32m✓\033[0m Prometheus has {len(active)} active target(s)")
                return True
            print("  \033[31m✗\033[0m Prometheus has no active targets")
            return False
        print(f"  \033[31m✗\033[0m Prometheus targets endpoint returned {resp.status_code}")
        return False
    except Exception as e:
        print(f"  \033[31m✗\033[0m Prometheus targets check failed: {e}")
        return False


def main() -> int:
    print("Chapter 10 — Logs & Dashboards\n")
    results = [
        check_grafana(),
        check_prometheus(),
        check_prometheus_targets(),
    ]
    print()
    if all(results):
        print("\033[32mAll checks passed!\033[0m")
        return 0
    print("\033[31mSome checks failed.\033[0m")
    return 1


if __name__ == "__main__":
    sys.exit(main())
