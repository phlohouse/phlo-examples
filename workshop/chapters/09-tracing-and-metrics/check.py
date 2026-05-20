#!/usr/bin/env python3
"""Chapter 09 checkpoint: verify observability stack is running."""

import sys

import httpx


def check_clickstack() -> bool:
    """Check ClickStack is reachable."""
    try:
        resp = httpx.get("http://localhost:8123", timeout=10, follow_redirects=True)
        if resp.status_code == 200:
            print("  \033[32m✓\033[0m ClickStack is reachable at http://localhost:8123")
            return True
        print(f"  \033[31m✗\033[0m ClickStack returned status {resp.status_code}")
        return False
    except Exception as e:
        print(f"  \033[31m✗\033[0m ClickStack unreachable: {e}")
        return False


def check_clickhouse_http() -> bool:
    """Check ClickStack's ClickHouse HTTP endpoint."""
    try:
        resp = httpx.get("http://localhost:18123/ping", timeout=10)
        if resp.status_code == 200 and "Ok" in resp.text:
            print("  \033[32m✓\033[0m ClickHouse HTTP is reachable at http://localhost:18123")
            return True
        print(f"  \033[31m✗\033[0m ClickHouse HTTP returned status {resp.status_code}")
        return False
    except Exception as e:
        print(f"  \033[31m✗\033[0m ClickHouse HTTP unreachable: {e}")
        return False


def main() -> int:
    print("Chapter 09 — Tracing & Metrics\n")
    results = [
        check_clickstack(),
        check_clickhouse_http(),
    ]
    print()
    if all(results):
        print("\033[32mAll checks passed!\033[0m")
        return 0
    print("\033[31mSome checks failed.\033[0m")
    return 1


if __name__ == "__main__":
    sys.exit(main())
