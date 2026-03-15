#!/usr/bin/env python3
"""Chapter 16 checkpoint: verify plugin, extension, and tests."""

import subprocess
import sys
from pathlib import Path


def check_plugin_file() -> bool:
    """Check the CLI plugin file exists."""
    plugin_file = Path("plugins/pokemon_stats.py")
    if plugin_file.exists():
        content = plugin_file.read_text()
        if "CliCommandPlugin" in content and "PokemonStatsPlugin" in content:
            print("  \033[32m✓\033[0m plugins/pokemon_stats.py defines PokemonStatsPlugin")
            return True
        print("  \033[31m✗\033[0m plugins/pokemon_stats.py missing plugin class")
        return False
    print("  \033[31m✗\033[0m plugins/pokemon_stats.py not found")
    return False


def check_test_file() -> bool:
    """Check the test file exists."""
    test_file = Path("tests/test_pokemon_ingestion.py")
    if test_file.exists():
        content = test_file.read_text()
        if "def test_" in content:
            print("  \033[32m✓\033[0m tests/test_pokemon_ingestion.py has test functions")
            return True
        print("  \033[31m✗\033[0m tests/test_pokemon_ingestion.py has no test functions")
        return False
    print("  \033[31m✗\033[0m tests/test_pokemon_ingestion.py not found")
    return False


def check_pokemon_data() -> bool:
    """Check Pokemon data still exists in Trino."""
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
            print(f"  \033[32m✓\033[0m pokemon table: {count} rows")
            return True
        print(f"  \033[31m✗\033[0m pokemon: {count} rows (expected >= 100)")
        return False
    except Exception as e:
        print(f"  \033[31m✗\033[0m Trino check failed: {e}")
        return False


def main() -> int:
    print("Chapter 16 — Build Your Own Plugin\n")
    results = [
        check_plugin_file(),
        check_test_file(),
        check_pokemon_data(),
    ]
    print()
    if all(results):
        print("\033[32mAll checks passed!\033[0m")
        return 0
    print("\033[31mSome checks failed.\033[0m")
    return 1


if __name__ == "__main__":
    sys.exit(main())
