#!/usr/bin/env python3
"""Compatibility wrapper for the standalone workshop runner."""

from __future__ import annotations

import sys

from workshop_runner.cli import main


if __name__ == "__main__":
    sys.exit(main())
