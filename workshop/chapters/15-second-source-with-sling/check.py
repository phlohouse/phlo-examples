#!/usr/bin/env python3
"""Chapter 15 checkpoint: verify Sling ingestion and card join model."""

import subprocess
import sys


def query_trino(sql: str, schema: str = "raw") -> str:
    """Run a SQL query against Trino via the Phlo CLI."""
    result = subprocess.run(
        [
            "phlo",
            "trino",
            "query",
            "--catalog",
            "iceberg",
            "--schema",
            schema,
            "--output-format",
            "CSV",
            sql,
        ],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Trino query failed: {result.stderr.strip()}")
    return result.stdout.strip()


def check_table(schema: str, table: str, min_rows: int) -> bool:
    """Check a table exists and has at least min_rows."""
    fqn = f"{schema}.{table}"
    try:
        output = query_trino(f"SELECT COUNT(*) FROM {fqn}", schema=schema)
        count = int(output.strip().strip('"'))
        if count >= min_rows:
            print(f"  \033[32m✓\033[0m {fqn}: {count} rows")
            return True
        print(f"  \033[31m✗\033[0m {fqn}: {count} rows (expected >= {min_rows})")
        return False
    except Exception as e:
        print(f"  \033[31m✗\033[0m {fqn}: {e}")
        return False


def main() -> int:
    print("Chapter 15 — Second Source with Sling\n")
    results = [
        check_table("raw", "pokemon_cards", 50),
        check_table("gold", "fct_card_values", 1),
    ]
    print()
    if all(results):
        print("\033[32mAll checks passed!\033[0m")
        return 0
    print("\033[31mSome checks failed.\033[0m")
    return 1


if __name__ == "__main__":
    sys.exit(main())
