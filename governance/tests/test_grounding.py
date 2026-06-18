"""Grounding verification: catches fabricated numbers/entities, passes grounded text."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from governance.grounding import verify_grounding


def test_grounded_text_passes():
    state = {"present_pct": 78.0, "absences": 9, "course": "MAT-120"}
    text = "Attendance is 78% with 9 absences in MAT-120."
    report = verify_grounding(text, state)
    assert report.grounded, report.to_audit_dict()


def test_fabricated_number_flagged():
    state = {"present_pct": 78.0}
    text = "Your balance due is $4,250 by the deadline."
    report = verify_grounding(text, state)
    assert not report.grounded
    assert any("4,250" in n or "4250" in n for n in report.ungrounded_numbers)


def test_fabricated_entity_flagged():
    state = {"program": "AA Liberal Arts"}
    text = "Please contact Springfield Community College for details."
    report = verify_grounding(text, state)
    assert "Springfield Community College" in report.ungrounded_entities


def test_empty_text_is_grounded():
    assert verify_grounding("", {}).grounded
