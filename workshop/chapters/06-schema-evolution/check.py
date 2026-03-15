#!/usr/bin/env python3
"""Chapter 06 checkpoint: verify schema evolution applied correctly."""

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


def check_column_exists(table: str, column: str) -> bool:
    """Check that a column exists in a table."""
    try:
        output = query_trino(f"DESCRIBE {table}")
        if column in output:
            print(f"  \033[32m✓\033[0m {table} has column '{column}'")
            return True
        print(f"  \033[31m✗\033[0m {table} missing column '{column}'")
        return False
    except Exception as e:
        print(f"  \033[31m✗\033[0m {table}: {e}")
        return False


def check_table_exists(table: str, min_rows: int) -> bool:
    """Check a table exists and has at least min_rows."""
    try:
        output = query_trino(f"SELECT COUNT(*) FROM {table}")
        count = int(output.strip().strip('"'))
        if count >= min_rows:
            print(f"  \033[32m✓\033[0m {table}: {count} rows")
            return True
        print(f"  \033[31m✗\033[0m {table}: {count} rows (expected >= {min_rows})")
        return False
    except Exception as e:
        print(f"  \033[31m✗\033[0m {table}: {e}")
        return False


def main() -> int:
    print("Chapter 06 — Schema Evolution\n")
    results = [
        check_table_exists("pokemon", 100),
        check_column_exists("pokemon", "habitat"),
    ]
    print()
    if all(results):
        print("\033[32mAll checks passed!\033[0m")
        return 0
    print("\033[31mSome checks failed.\033[0m")
    return 1


if __name__ == "__main__":
    sys.exit(main())
