"""
CI gate for the Agent 01 (Concierge) scored eval + negative controls.

The positive tests hold the quality line on the golden set. The negative controls
prove the gate has TEETH — that the scorers actually catch a misclassification, an
ungrounded number, and a student-PII identifier — so a green run means something.
"""
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent.parent))
sys.path.insert(0, str(_HERE.parent.parent / "platform_core"))

from governance.evals.scorers_concierge import score_dataset, gate, THRESHOLDS, _PII  # noqa: E402
from governance.grounding import verify_grounding                                     # noqa: E402

GOLDEN = _HERE / "golden" / "agent01_concierge_scored.json"


def _cases():
    return json.loads(GOLDEN.read_text(encoding="utf-8"))["cases"]


# ── positive: the benchmark passes every threshold ───────────────────────────

def test_scored_eval_meets_all_thresholds():
    result = score_dataset(_cases())
    passed, failures = gate(result["metrics"])
    assert passed, f"threshold failures: {failures}"


def test_student_pii_leak_hard_gate_is_zero():
    result = score_dataset(_cases())
    assert result["metrics"]["student_pii_leak_rate"] == 0.0


def test_classification_meets_bar():
    m = score_dataset(_cases())["metrics"]
    assert m["classification_accuracy"] >= THRESHOLDS["classification_accuracy"]


def test_duplicate_detection_meets_bar():
    m = score_dataset(_cases())["metrics"]
    assert m["duplicate_accuracy"] >= THRESHOLDS["duplicate_accuracy"]


# ── negative controls: the gate must FAIL on bad data ────────────────────────

def test_gate_catches_a_misclassification():
    # A LOOKUP query mislabeled as STATUS in the gold -> the real classifier returns
    # LOOKUP -> a classification miss -> accuracy drops below 1 and the gate fails.
    cases = _cases()
    poisoned = json.loads(json.dumps(cases[0]))
    poisoned["id"] = "CS-POISON"
    poisoned["gold"]["intent"] = "STATUS"          # truth mislabeled; predictor says LOOKUP
    result = score_dataset([poisoned])
    passed, _ = gate(result["metrics"])
    assert result["metrics"]["classification_accuracy"] < 1.0
    assert not passed                               # the gate rejects it


def test_grounding_scorer_flags_an_ungrounded_number():
    # A summary asserting a tuition absent from the record must be flagged.
    g = verify_grounding("Tuition is $99,999 and the admission rate is 77%.",
                         {"institution_name": "Rice University", "tuition_in_state": 54960})
    assert g.ungrounded_numbers, "grounding scorer failed to flag an ungrounded number"


def test_pii_detector_catches_identifiers():
    assert _PII.search("guardian jane.doe@example.edu SSN 123-45-6789 STU-00098765")
    assert not _PII.search("Rice University (Houston, TX) reports in-state tuition of $54,960.")
