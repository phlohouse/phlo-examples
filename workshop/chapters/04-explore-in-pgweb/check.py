#!/usr/bin/env python3
"""Chapter 04 checkpoint: verify PgWeb and Postgres are reachable."""

import subprocess
import sys

import httpx


def check_pgweb() -> bool:
    """Check PgWeb is reachable."""
    try:
        resp = httpx.get("http://localhost:10008", timeout=5, follow_redirects=True)
        if resp.status_code == 200:
            print("  \033[32m✓\033[0m PgWeb is reachable at http://localhost:10008")
            return True
        print(f"  \033[31m✗\033[0m PgWeb returned status {resp.status_code}")
        return False
    except Exception as e:
        print(f"  \033[31m✗\033[0m PgWeb unreachable: {e}")
        return False


def check_postgres() -> bool:
    """Check Postgres is accessible."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "phlo.cli.main", "postgres", "query", "SELECT 1;"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            print("  \033[32m✓\033[0m Postgres is ready")
            return True
        print(f"  \033[31m✗\033[0m Postgres not ready: {result.stderr.strip()}")
        return False
    except Exception as e:
        print(f"  \033[31m✗\033[0m Postgres check failed: {e}")
        return False


def main() -> int:
    print("Chapter 04 — Explore in PgWeb\n")
    results = [check_pgweb(), check_postgres()]
    print()
    if all(results):
        print("\033[32mAll checks passed!\033[0m")
        return 0
    print("\033[31mSome checks failed.\033[0m")
    return 1


if __name__ == "__main__":
    sys.exit(main())
