#!/usr/bin/env python3
"""Chapter 11 checkpoint: verify lineage CLI and data exist."""

import subprocess
import sys

def _run(command: list[str]) -> tuple[bool, str]:
    result = subprocess.run(command, capture_output=True, text=True, timeout=30)
    output = (result.stdout + result.stderr).strip()
    return result.returncode == 0, output


def check_lineage_status() -> bool:
    """Check lineage CLI reports non-empty graph state."""
    ok, output = _run(["phlo", "lineage", "status"])
    if not ok:
        print(f"  \033[31m✗\033[0m phlo lineage status failed: {output}")
        return False
    if "Total Assets:" not in output or "Total Dependencies:" not in output:
        print(f"  \033[31m✗\033[0m phlo lineage status output was unexpected: {output}")
        return False
    if "Total Assets: 0" in output or "Total Dependencies: 0" in output:
        print(f"  \033[31m✗\033[0m lineage graph is empty: {output}")
        return False
    print("  \033[32m✓\033[0m phlo lineage status returned graph statistics")
    return True


def check_lineage_graph() -> bool:
    """Check lineage CLI can resolve the Pokemon assets."""
    ok, output = _run(["phlo", "lineage", "show", "dim_pokemon", "--direction", "upstream"])
    if not ok:
        print(f"  \033[31m✗\033[0m phlo lineage show failed: {output}")
        return False
    expected_assets = ("dim_pokemon", "stg_pokemon", "dlt_pokemon")
    missing = [asset for asset in expected_assets if asset not in output]
    if missing:
        print(
            "  \033[31m✗\033[0m "
            f"Lineage output missing expected asset(s): {', '.join(missing)}"
        )
        return False
    print("  \033[32m✓\033[0m phlo lineage show returned the expected asset chain")
    return True


def main() -> int:
    print("Chapter 11 — Lineage\n")
    results = [
        check_lineage_status(),
        check_lineage_graph(),
    ]
    print()
    if all(results):
        print("\033[32mAll checks passed!\033[0m")
        return 0
    print("\033[31mSome checks failed.\033[0m")
    return 1


if __name__ == "__main__":
    sys.exit(main())
