"""Four-fifths disparate-impact screen for at-risk flagging / ranking workflows."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from governance.fairness import four_fifths


def test_balanced_flagging_passes():
    rep = four_fifths(selected={"A": 50, "B": 48}, totals={"A": 100, "B": 100})
    assert rep.passes_four_fifths


def test_disparate_flagging_is_caught():
    # Group B is flagged at far less than 80% of group A's rate.
    rep = four_fifths(selected={"A": 60, "B": 10}, totals={"A": 100, "B": 100})
    assert not rep.passes_four_fifths
    assert "B" in rep.flagged_groups
    assert rep.most_selected_group == "A"
