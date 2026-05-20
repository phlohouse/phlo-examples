#!/usr/bin/env python3
"""Chapter 00 checkpoint: verify the warmed stack is ready."""

import subprocess
import sys
import time


def _run(command: list[str], *, timeout: int = 30) -> tuple[bool, str]:
    result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    output = (result.stdout + result.stderr).strip()
    return result.returncode == 0, output


def check_tracing_stack() -> bool:
    ok, output = _run(["phlo", "services", "status"])
    if not ok:
        print(f"  \033[31m✗\033[0m phlo services status failed: {output}")
        return False
    expected = ("trino", "dagster", "clickstack", "grafana")
    missing = [service for service in expected if service not in output]
    if missing:
        print(f"  \033[31m✗\033[0m missing warmed services: {', '.join(missing)}")
        return False
    print("  \033[32m✓\033[0m base and observability services are running")
    return True


def check_dbt_wrapper() -> bool:
    output = ""
    retry_markers = (
        "SERVER_STARTING_UP",
        "Connection refused",
        "Failed to establish a new connection",
    )
    for attempt in range(5):
        ok, output = _run(["phlo", "dbt", "compile"], timeout=120)
        if ok:
            print("  \033[32m✓\033[0m dbt path is warmed and responsive")
            return True
        if not any(marker in output for marker in retry_markers) or attempt == 4:
            break
        time.sleep(10)
    print(f"  \033[31m✗\033[0m phlo dbt compile failed: {output}")
    return False


def main() -> int:
    print("Chapter 00 — Workshop Warmup\n")
    results = [
        check_tracing_stack(),
        check_dbt_wrapper(),
    ]
    print()
    if all(results):
        print("\033[32mAll checks passed!\033[0m")
        return 0
    print("\033[31mSome checks failed.\033[0m")
    return 1


if __name__ == "__main__":
    sys.exit(main())
