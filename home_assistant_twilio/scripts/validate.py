#!/usr/bin/env python3
"""Führt alle lokalen Gates des Twilio-Beispielpakets aus."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent


def main() -> int:
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 1

    check = subprocess.run(
        ["git", "diff", "--check", "--", str(ROOT.relative_to(REPO))],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=False,
    )
    if check.stdout:
        print(check.stdout, end="")
    if check.stderr:
        print(check.stderr, end="", file=sys.stderr)
    if check.returncode:
        return check.returncode

    print("\nPASS: YAML, Verträge, Links, IDs, Platzhalter/Secrets und git diff --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
