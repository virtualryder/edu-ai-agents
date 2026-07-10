"""CI drift gate — every CURRENT-state doc must agree with MATURITY.yaml on the test count.
Historical files (changelogs, deploy evidence, review/action plans) cite point-in-time numbers on
purpose and are excluded. Fails the build on drift so a stale headline can never ship."""
import glob
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CURRENT = re.compile(r"(\d{2,4})\s*(?:\*\*)?\s*(?:automated\s+)?tests?\b", re.I)
HIST = re.compile(r"(?:→|-+>|–>|\bwas\b|\bgrew\b|\bfrom\b|\$)")
SKIP_FILES = {"CHANGELOG.md", "SUITE-STATUS.md", "CLEAN-ACCOUNT-ACCEPTANCE.md", "TCO-MODEL.md",
              "SOW-TEMPLATE.md", "CONTROL-EVIDENCE.md", "DEPLOY-EVERYTHING.md",
              "PORTFOLIO-START-HERE.md", "PORTFOLIO-CONNECTOR-MATURITY.md", "COMMIT-MANIFEST.md"}
SKIP_MARKERS = ("ACTION-PLAN", "REVIEW", "REMEDIATION", "DEPLOY-NOTES", "GOLDEN-PATH-DEPLOY",
                "DECK-SOURCES")
SKIP_DIRS = {".git", "node_modules", "__pycache__", "venv", ".venv"}


def _total():
    m = re.search(r"offline_total:\s*(\d+)", open(os.path.join(REPO, "MATURITY.yaml"), encoding="utf-8").read())
    return int(m.group(1))


def test_no_test_count_drift():
    total = _total()
    findings = []
    for md in glob.glob(os.path.join(REPO, "**", "*.md"), recursive=True):
        parts = md.split(os.sep)
        base = os.path.basename(md)
        if (any(s in parts for s in SKIP_DIRS) or base in SKIP_FILES
                or any(k in base.upper() for k in SKIP_MARKERS)):
            continue
        try:
            lines = open(md, encoding="utf-8").read().splitlines()
        except (UnicodeDecodeError, PermissionError):
            continue
        for i, ln in enumerate(lines, 1):
            if HIST.search(ln):
                continue
            for num in CURRENT.findall(ln):
                n = int(num)
                if 50 <= n <= 4000 and n != total:
                    findings.append(f"{os.path.relpath(md, REPO)}:{i} cites '{num} tests' (MATURITY.yaml={total})")
    assert not findings, "status drift vs MATURITY.yaml:\n  " + "\n  ".join(findings)
