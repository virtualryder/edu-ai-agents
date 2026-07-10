#!/usr/bin/env python3
"""
check_maturity.py — portfolio drift-checker for MATURITY.yaml.

MATURITY.yaml is the machine-readable single source of truth for this repo's
maturity claims (see the header of that file). The most drift-prone claim is the
offline test count (`tests.offline_total`), which silently goes stale every time
the suite grows or shrinks. This tool re-derives the ACTUAL collected test count
by running pytest in --collect-only mode and compares it to the declared value.

Behaviour:
  * Resolves the repo root as the parent of this tools/ directory.
  * Reads `tests.offline_total` and `tests.reproduce` from MATURITY.yaml via
    stdlib regex (no PyYAML dependency — this must run anywhere).
  * Derives the pytest target paths from `tests.reproduce` when it names explicit
    paths, else falls back to the repo root (matching the canonical root
    collection `PYTHONPATH=platform_core:. pytest -q`).
  * Runs `python -m pytest --collect-only -q <paths>` via sys.executable and
    counts collected node ids (lines containing "::").
  * Prints declared vs actual. Exits 0 when they match, 1 on drift.
  * `--update` rewrites `tests.offline_total` in place to the actual count.

Stdlib-only. Intended to be run in CI and locally:

    python tools/check_maturity.py            # check, exit non-zero on drift
    python tools/check_maturity.py --update    # rewrite offline_total to actual
"""
from __future__ import annotations

import argparse
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MATURITY = REPO_ROOT / "MATURITY.yaml"

_OFFLINE_RE = re.compile(r"^(\s*offline_total:\s*)(\d+)(.*)$", re.M)
_REPRODUCE_RE = re.compile(r"^\s*reproduce:\s*[\"']?(.+?)[\"']?\s*$", re.M)


def read_maturity_text() -> str:
    if not MATURITY.is_file():
        sys.exit(f"ERROR: {MATURITY} not found")
    return MATURITY.read_text(encoding="utf-8")


def declared_offline_total(text: str) -> int:
    m = _OFFLINE_RE.search(text)
    if not m:
        sys.exit("ERROR: could not find `offline_total:` in MATURITY.yaml")
    return int(m.group(2))


def pytest_targets(text: str) -> list[str]:
    """
    Derive pytest target paths from `tests.reproduce`.

    The canonical reproduce command is a root collection with no explicit paths
    (`PYTHONPATH=platform_core:. pytest -q`), so the sensible default is the repo
    root ("."). If reproduce ever names explicit path arguments, honour them.
    """
    m = _REPRODUCE_RE.search(text)
    if m:
        cmd = m.group(1)
        # strip an inline `# comment`
        cmd = cmd.split("#", 1)[0]
        try:
            tokens = shlex.split(cmd)
        except ValueError:
            tokens = cmd.split()
        paths: list[str] = []
        seen_pytest = False
        for tok in tokens:
            if tok in ("pytest",) or tok.endswith("/pytest") or tok == "-m":
                seen_pytest = True
                continue
            if not seen_pytest:
                continue
            if tok.startswith("-"):
                continue
            if tok in ("python", "python3", "pytest", "PYTHONPATH"):
                continue
            if "=" in tok and not (REPO_ROOT / tok).exists():
                # env assignment like FOO=bar
                continue
            # treat as a path only if it resolves under the repo
            if (REPO_ROOT / tok).exists():
                paths.append(tok)
        if paths:
            return paths
    return ["."]


def collected_count(targets: list[str]) -> int:
    env = dict(os.environ)
    # Match the canonical root collection import roots.
    existing = env.get("PYTHONPATH", "")
    py_path = "platform_core:."
    env["PYTHONPATH"] = f"{py_path}:{existing}" if existing else py_path
    cmd = [sys.executable, "-m", "pytest", "--collect-only", "-q", *targets]
    proc = subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
    )
    node_ids = [ln for ln in proc.stdout.splitlines() if "::" in ln]
    if not node_ids and proc.returncode != 0:
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        sys.exit(
            "ERROR: pytest --collect-only failed and collected 0 tests "
            f"(exit {proc.returncode}). Fix collection before checking drift."
        )
    return len(node_ids)


def update_offline_total(text: str, actual: int) -> str:
    def repl(m: "re.Match[str]") -> str:
        return f"{m.group(1)}{actual}{m.group(3)}"

    return _OFFLINE_RE.sub(repl, text, count=1)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--update",
        action="store_true",
        help="rewrite tests.offline_total in MATURITY.yaml to the actual count",
    )
    args = ap.parse_args()

    text = read_maturity_text()
    declared = declared_offline_total(text)
    targets = pytest_targets(text)
    actual = collected_count(targets)

    print(f"pytest targets : {' '.join(targets)}")
    print(f"declared offline_total : {declared}")
    print(f"actual collected count : {actual}")

    if args.update:
        if declared == actual:
            print("offline_total already matches actual; nothing to update.")
            return 0
        new_text = update_offline_total(text, actual)
        MATURITY.write_text(new_text, encoding="utf-8")
        print(f"UPDATED offline_total: {declared} -> {actual}")
        return 0

    if declared == actual:
        print("OK: MATURITY.yaml offline_total matches collected test count.")
        return 0

    print(
        f"DRIFT: MATURITY.yaml declares {declared} tests but pytest collects "
        f"{actual}. Run `python tools/check_maturity.py --update` (and verify) "
        f"to reconcile.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
