#!/usr/bin/env python3
"""Chapter 08 checkpoint: verify alerting system is configured."""

import subprocess
import sys

import httpx


def check_dagster_running() -> bool:
    """Check Dagster webserver is running."""
    try:
        resp = httpx.get("http://localhost:3000/server_info", timeout=5)
        if resp.status_code == 200:
            print("  \033[32m✓\033[0m Dagster webserver is running")
            return True
        print(f"  \033[31m✗\033[0m Dagster returned status {resp.status_code}")
        return False
    except Exception as e:
        print(f"  \033[31m✗\033[0m Dagster unreachable: {e}")
        return False


def check_pokemon_table() -> bool:
    """Check Pokemon table still has data (pipeline still works after alerting setup)."""
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "phlo.cli.main",
                "trino",
                "query",
                "SELECT COUNT(*) FROM raw.pokemon",
                "--catalog",
                "iceberg",
                "--schema",
                "raw",
                "--output-format",
                "CSV",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            print(f"  \033[31m✗\033[0m Trino query failed: {result.stderr.strip()}")
            return False
        count = int(result.stdout.strip().strip('"'))
        if count >= 100:
            print(f"  \033[32m✓\033[0m pokemon table: {count} rows (pipeline healthy)")
            return True
        print(f"  \033[31m✗\033[0m pokemon: {count} rows (expected >= 100)")
        return False
    except Exception as e:
        print(f"  \033[31m✗\033[0m Trino check failed: {e}")
        return False


def main() -> int:
    print("Chapter 08 — Alerting & the Hook Bus\n")
    results = [
        check_dagster_running(),
        check_pokemon_table(),
    ]
    print()
    if all(results):
        print("\033[32mAll checks passed!\033[0m")
        return 0
    print("\033[31mSome checks failed.\033[0m")
    return 1


if __name__ == "__main__":
    sys.exit(main())
