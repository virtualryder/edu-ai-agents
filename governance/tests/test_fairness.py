"""Fairness checks: representativeness flagging and confusion-rate monitoring."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from governance.fairness import confusion_rates, representativeness_flag


def test_balanced_selection_is_equitable():
    base = {"A": 0.5, "B": 0.5}
    sel = {"A": 0.52, "B": 0.48}
    rep = representativeness_flag(base, sel, tolerance=0.2)
    assert rep.equitable


def test_disproportionate_selection_flagged():
    base = {"A": 0.5, "B": 0.5}
    sel = {"A": 0.85, "B": 0.15}  # group B under-selected, A over-selected
    rep = representativeness_flag(base, sel, tolerance=0.2)
    assert not rep.equitable
    assert "B" in rep.flagged_groups


def test_confusion_rates():
    predicted = [True, True, False, False]
    actual = [True, False, True, False]
    rates = confusion_rates(predicted, actual)
    assert rates["false_positive_rate"] == 0.5
    assert rates["false_negative_rate"] == 0.5
