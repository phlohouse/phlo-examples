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


def check_otel_collector() -> bool:
    """Check OTEL collector health endpoint."""
    try:
        resp = httpx.get("http://localhost:4318/v1/traces", timeout=5)
        # OTLP endpoint may return 405 for GET (expects POST) — that's fine, it's alive
        if resp.status_code in (200, 405):
            print("  \033[32m✓\033[0m OTEL collector is responding at http://localhost:4318")
            return True
        print(f"  \033[31m✗\033[0m OTEL collector returned status {resp.status_code}")
        return False
    except Exception as e:
        print(f"  \033[31m✗\033[0m OTEL collector unreachable: {e}")
        return False


def main() -> int:
    print("Chapter 09 — Tracing & Metrics\n")
    results = [
        check_clickstack(),
        check_otel_collector(),
    ]
    print()
    if all(results):
        print("\033[32mAll checks passed!\033[0m")
        return 0
    print("\033[31mSome checks failed.\033[0m")
    return 1


if __name__ == "__main__":
    sys.exit(main())
