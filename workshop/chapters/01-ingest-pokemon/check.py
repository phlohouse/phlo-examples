#!/usr/bin/env python3
"""Chapter 01 checkpoint: verify Pokemon tables exist in Trino."""

import subprocess
import sys


def query_trino(sql: str) -> str:
    """Run a SQL query against Trino via the Phlo CLI."""
    result = subprocess.run(
        [
            "phlo",
            "trino",
            "query",
            "--catalog",
            "iceberg",
            "--schema",
            "raw",
            "--output-format",
            "CSV",
            sql,
        ],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Trino query failed: {result.stderr.strip()}")
    return result.stdout.strip()


def check_table(table: str, min_rows: int) -> bool:
    """Check a table exists and has at least min_rows."""
    try:
        output = query_trino(f"SELECT COUNT(*) FROM {table}")
        count = int(output.strip().strip('"'))
        if count >= min_rows:
            print(f"  \033[32m✓\033[0m {table}: {count} rows")
            return True
        else:
            print(f"  \033[31m✗\033[0m {table}: {count} rows (expected >= {min_rows})")
            return False
    except Exception as e:
        print(f"  \033[31m✗\033[0m {table}: {e}")
        return False


def main() -> int:
    print("Chapter 01 — Ingest Pokemon\n")
    results = [
        check_table("pokemon", 100),
        check_table("pokemon_types", 10),
    ]
    print()
    if all(results):
        print("\033[32mAll checks passed!\033[0m")
        return 0
    else:
        print("\033[31mSome checks failed.\033[0m")
        return 1


if __name__ == "__main__":
    sys.exit(main())
