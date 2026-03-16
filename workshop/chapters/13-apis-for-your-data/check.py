#!/usr/bin/env python3
"""Chapter 13 checkpoint: verify REST, GraphQL, and Phlo API endpoints."""

import sys

import httpx


def check_postgrest() -> bool:
    """Check PostgREST is reachable."""
    try:
        resp = httpx.get("http://localhost:3001/", timeout=10, follow_redirects=True)
        if resp.status_code == 200:
            print("  \033[32m✓\033[0m PostgREST is reachable at http://localhost:3001")
            return True
        print(f"  \033[31m✗\033[0m PostgREST returned status {resp.status_code}")
        return False
    except Exception as e:
        print(f"  \033[31m✗\033[0m PostgREST unreachable: {e}")
        return False


def check_hasura() -> bool:
    """Check Hasura is reachable."""
    try:
        resp = httpx.get(
            "http://localhost:8888/healthz", timeout=10, follow_redirects=True
        )
        if resp.status_code == 200:
            print("  \033[32m✓\033[0m Hasura is reachable at http://localhost:8888")
            return True
        print(f"  \033[31m✗\033[0m Hasura returned status {resp.status_code}")
        return False
    except Exception as e:
        print(f"  \033[31m✗\033[0m Hasura unreachable: {e}")
        return False


def check_phlo_api() -> bool:
    """Check Phlo API is reachable."""
    try:
        resp = httpx.get("http://localhost:8000/health", timeout=10, follow_redirects=True)
        if resp.status_code == 200:
            print("  \033[32m✓\033[0m Phlo API is reachable at http://localhost:8000")
            return True
        print(f"  \033[31m✗\033[0m Phlo API returned status {resp.status_code}")
        return False
    except Exception as e:
        print(f"  \033[31m✗\033[0m Phlo API unreachable: {e}")
        return False


def main() -> int:
    print("Chapter 13 — APIs for Your Data\n")
    results = [
        check_postgrest(),
        check_hasura(),
        check_phlo_api(),
    ]
    print()
    if all(results):
        print("\033[32mAll checks passed!\033[0m")
        return 0
    print("\033[31mSome checks failed.\033[0m")
    return 1


if __name__ == "__main__":
    sys.exit(main())
