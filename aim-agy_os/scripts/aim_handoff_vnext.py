#!/usr/bin/env python3
"""Wrapper: python3 aim-agy_os/scripts/aim_handoff_vnext.py <cmd> ..."""
from __future__ import annotations

import sys
from pathlib import Path

OS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(OS))
sys.path.insert(0, str(OS / ".aim_core"))

from handoff.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
