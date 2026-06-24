"""Structural golden-artifact evals pass (no API key)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from governance.evals import run


def test_golden_artifact_evals_pass():
    assert run() == 0
