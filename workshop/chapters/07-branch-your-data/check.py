#!/usr/bin/env python3
"""Chapter 07 checkpoint: verify Nessie branch operations."""

import subprocess
import sys

import httpx


NESSIE_URL = "http://localhost:19120/api/v1"


def check_nessie_reachable() -> bool:
    """Check Nessie API is reachable."""
    try:
        resp = httpx.get(f"{NESSIE_URL}/trees", timeout=5)
        if resp.status_code == 200:
            print("  \033[32m✓\033[0m Nessie API is reachable")
            return True
        print(f"  \033[31m✗\033[0m Nessie returned status {resp.status_code}")
        return False
    except Exception as e:
        print(f"  \033[31m✗\033[0m Nessie unreachable: {e}")
        return False


def check_main_has_data() -> bool:
    """Check main branch has Pokemon data via Trino."""
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
            print(f"  \033[32m✓\033[0m main branch: pokemon has {count} rows")
            return True
        print(f"  \033[31m✗\033[0m main branch: pokemon has {count} rows (expected >= 100)")
        return False
    except Exception as e:
        print(f"  \033[31m✗\033[0m Trino check failed: {e}")
        return False


def main() -> int:
    print("Chapter 07 — Branch Your Data\n")
    results = [
        check_nessie_reachable(),
        check_main_has_data(),
    ]
    print()
    if all(results):
        print("\033[32mAll checks passed!\033[0m")
        return 0
    print("\033[31mSome checks failed.\033[0m")
    return 1


if __name__ == "__main__":
    sys.exit(main())
