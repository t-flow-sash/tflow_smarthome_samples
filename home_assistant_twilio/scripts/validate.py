#!/usr/bin/env python3
"""Führt alle lokalen Gates des Twilio-Beispielpakets aus."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
PATHSPEC = str(ROOT.relative_to(REPO))


class ValidationError(RuntimeError):
    """Verständlicher, fail-closed Fehler der Git-Kandidatenauflösung."""


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )


def resolve_commit(repo: Path, reference: str, label: str) -> str:
    result = git(repo, "rev-parse", "--verify", f"{reference}^{{commit}}")
    if result.returncode:
        detail = result.stderr.strip() or "Referenz nicht gefunden"
        raise ValidationError(f"{label} '{reference}' ist kein auflösbarer Commit: {detail}")
    return result.stdout.strip()


def default_base_reference(repo: Path) -> str:
    """Ermittelt die Base deterministisch, ohne Netzwerkzugriff oder Raten."""
    if value := os.environ.get("GITHUB_BASE_SHA"):
        return value
    if value := os.environ.get("GITHUB_BASE_REF"):
        for candidate in (f"origin/{value}", value):
            if git(repo, "rev-parse", "--verify", f"{candidate}^{{commit}}").returncode == 0:
                return candidate
        raise ValidationError(
            f"GITHUB_BASE_REF='{value}' ist lokal weder als origin/{value} noch als {value} verfügbar. "
            "Base zuerst fetchen oder --base <SHA/Ref> angeben."
        )

    symbolic = git(repo, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD")
    if symbolic.returncode == 0:
        return symbolic.stdout.strip().removeprefix("refs/remotes/")

    for candidate in ("origin/main", "main"):
        if git(repo, "rev-parse", "--verify", f"{candidate}^{{commit}}").returncode == 0:
            return candidate
    raise ValidationError(
        "Keine Base ermittelbar: --base <SHA/Ref> angeben oder origin/HEAD bzw. origin/main fetchen."
    )


def resolve_candidate(repo: Path, base_reference: str | None, head_reference: str) -> tuple[str, str, str, str]:
    base_input = base_reference or default_base_reference(repo)
    base_tip = resolve_commit(repo, base_input, "Base")
    head_sha = resolve_commit(repo, head_reference, "Candidate")
    merge_base = git(repo, "merge-base", base_tip, head_sha)
    if merge_base.returncode:
        detail = merge_base.stderr.strip() or "keine gemeinsame Historie"
        raise ValidationError(f"Merge-Base für {base_tip} und {head_sha} nicht ermittelbar: {detail}")
    return base_input, base_tip, merge_base.stdout.strip(), head_sha


def print_process(result: subprocess.CompletedProcess[str]) -> None:
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)


def run_diff_checks(repo: Path, pathspec: str, base_sha: str, head_sha: str) -> int:
    """Prüft Candidate-Commit-Diff, Index und Arbeitsbaum getrennt."""
    checks = (
        ("Candidate-Diff", ("diff", "--check", base_sha, head_sha, "--", pathspec)),
        ("Index", ("diff", "--cached", "--check", "--", pathspec)),
        ("Arbeitsbaum", ("diff", "--check", "--", pathspec)),
    )
    for label, args in checks:
        result = git(repo, *args)
        print_process(result)
        if result.returncode:
            print(f"FAIL: git diff --check ({label})", file=sys.stderr)
            return result.returncode
        print(f"PASS: git diff --check ({label})")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Twilio-Verträge plus SHA-/Base-gebundene Git-Diff-Prüfung"
    )
    parser.add_argument(
        "--base",
        help="Base-SHA oder -Ref; Standard: GITHUB_BASE_SHA/GITHUB_BASE_REF, origin/HEAD, origin/main oder main",
    )
    parser.add_argument("--head", default="HEAD", help="Candidate-SHA oder -Ref (Standard: HEAD)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        base_input, base_tip, merge_base, head_sha = resolve_candidate(REPO, args.base, args.head)
    except ValidationError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2

    print(f"Base-Eingabe: {base_input}")
    print(f"Base-Tip-SHA: {base_tip}")
    print(f"Merge-Base-SHA: {merge_base}")
    print(f"Candidate-SHA: {head_sha}")

    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 1

    diff_result = run_diff_checks(REPO, PATHSPEC, merge_base, head_sha)
    if diff_result:
        return diff_result

    print("\nPASS: exakter Kamera-AI→Twilio-SMS-Vertrag, Scope-Abwesenheit und alle drei git diff --check-Gates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
