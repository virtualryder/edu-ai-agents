"""
Scored eval metrics for Agent 01 (Student & Family Concierge).

Where run_evals.py answers "does the artifact keep its required shape?" (binary,
structural), this module answers "how GOOD is the concierge's institution-facts
pipeline, on a labeled benchmark, against thresholds a CIO / privacy officer would
set?"

Predictions come from the REAL ingestion pipeline — the College Scorecard connector
(CollegeScorecardConnector._map_record) and its query classifier
(collegescorecard.classify_query) — so this scores actual extraction /
classification quality, not a stub. Grounding reuses governance/grounding.py;
the student-PII leak check reuses the platform pii_masker.

Metrics (aggregated over the golden set), with thresholds:
  classification_accuracy  >= 0.90   (query routed to the right intent)
  entity_f1                >= 0.85   (institution / location / cost-aid extraction)
  grounding_rate           >= 0.90   (summary claims traceable to the record)
  student_pii_leak_rate    == 0.00   (HARD GATE — FERPA/COPPA; any unmasked id fails)
  answer_completeness      >= 0.95   (required institution fields present)
  duplicate_accuracy       >= 0.90   (duplicate / near-duplicate institutions)
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_REPO / "platform_core"))

from governance.grounding import verify_grounding                                  # noqa: E402
from edu_agent_platform.connectors.collegescorecard import (                       # noqa: E402
    CollegeScorecardConnector as _CScC,
    classify_query as _classify_query,
)
from edu_agent_platform.pii_masker import mask                                      # noqa: E402

THRESHOLDS: Dict[str, float] = {
    "classification_accuracy": 0.90,
    "entity_f1": 0.85,
    "grounding_rate": 0.90,
    "student_pii_leak_rate": 0.0,     # <= (hard gate: must be exactly 0)
    "answer_completeness": 0.95,
    "duplicate_accuracy": 0.90,
}
# Direction: most metrics are "higher is better" (>=); the leak rate is "<=".
LOWER_IS_BETTER = {"student_pii_leak_rate"}

# Required institution fields for a complete concierge answer. Presence — NOT
# truthiness — is what counts: admission_rate == 0.0 or a tuition of 0 is a VALID
# present value; only None / "" / [] / {} count as missing.
_REQUIRED_FIELDS = ["institution_name", "city", "state",
                    "tuition_in_state", "median_debt", "admission_rate"]

# Any of: US SSN, email, education-id prefix (STU/SID/...), or a >=9-digit run.
_PII = re.compile(r"\b\d{3}-\d{2}-\d{4}\b|[\w.+-]+@[\w-]+\.[\w.]+|"
                  r"\b(?:STU|SID|STUDENT|CASE|APP|ENROLL)[-_ ]?\d{3,}\b|\b\d{9,}\b", re.I)


def _norm(s: Any) -> str:
    return re.sub(r"\s+", " ", str(s)).strip().lower()


def _set(xs: List[Any]) -> Set[str]:
    return {_norm(x) for x in xs if x not in (None, "")}


@dataclass
class InstitutionPrediction:
    intent: str
    record: Dict[str, Any]
    entities: Set[str]
    summary: str


def predict(case: Dict[str, Any]) -> InstitutionPrediction:
    """The agent's prediction for a case: real connector mapping + real classifier."""
    rec = _CScC._map_record(case["raw"])
    intent = _classify_query(case.get("query", ""))
    cost_aid = [rec.get("tuition_in_state"), rec.get("tuition_out_of_state"),
                rec.get("median_debt"), rec.get("admission_rate")]
    entities = _set([rec.get("institution_name"), rec.get("city"), rec.get("state")]) | \
        {_norm(v) for v in cost_aid if v not in (None, "")}
    return InstitutionPrediction(intent=intent, record=rec, entities=entities,
                                 summary=rec.get("summary", ""))


def _prf(tp: int, fp: int, fn: int) -> Tuple[float, float, float]:
    p = tp / (tp + fp) if (tp + fp) else 1.0
    r = tp / (tp + fn) if (tp + fn) else 1.0
    f1 = 2 * p * r / (p + r) if (p + r) else 0.0
    return p, r, f1


def score_dataset(cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    cases: list of {"id", "raw": {...}, "query": str, "gold": {institution, city,
           state, tuition_*, median_debt, admission_rate, intent, is_duplicate?,
           dup_of?}}. Returns metrics + per-case detail.
    """
    n = len(cases)
    class_correct = 0
    e_tp = e_fp = e_fn = 0
    grounded = 0
    pii_leaks = 0
    completeness_scores: List[float] = []
    detail: List[Dict[str, Any]] = []

    preds: Dict[str, InstitutionPrediction] = {}
    for c in cases:
        pred = predict(c)
        preds[c["id"]] = pred
        gold = c["gold"]

        # classification (query intent)
        ok_class = (pred.intent == gold["intent"])
        class_correct += 1 if ok_class else 0

        # entities (institution / location / cost-aid as one micro-set)
        gold_ents = _set([gold.get("institution"), gold.get("city"), gold.get("state")]) | \
            {_norm(v) for v in (gold.get("tuition_in_state"), gold.get("tuition_out_of_state"),
                                gold.get("median_debt"), gold.get("admission_rate"))
             if v not in (None, "")}
        e_tp += len(gold_ents & pred.entities)
        e_fp += len(pred.entities - gold_ents)
        e_fn += len(gold_ents - pred.entities)

        # grounding on the composed summary vs the record state
        g = verify_grounding(pred.summary, pred.record)
        is_grounded = not (g.ungrounded_numbers or g.ungrounded_entities)
        grounded += 1 if is_grounded else 0

        # student-PII leak: the emitted (masked) summary must carry no identifier
        emitted = mask(pred.summary)
        leaked = bool(_PII.search(emitted))
        pii_leaks += 1 if leaked else 0

        # completeness — presence, NOT truthiness (admission_rate 0.0 is valid)
        present = sum(1 for f in _REQUIRED_FIELDS if pred.record.get(f) not in (None, "", [], {}))
        completeness_scores.append(present / len(_REQUIRED_FIELDS))

        detail.append({"id": c["id"], "intent_gold": gold["intent"], "intent_pred": pred.intent,
                       "classified_ok": ok_class, "grounded": is_grounded, "pii_leak": leaked})

    # duplicate / near-duplicate detection: gold cases carry is_duplicate + dup_of;
    # predict by the connector's transparent institution identity key.
    dup_correct = dup_total = 0
    for c in cases:
        if "is_duplicate" not in c["gold"]:
            continue
        dup_total += 1
        gold_dup = bool(c["gold"]["is_duplicate"])
        ref = c["gold"].get("dup_of")
        pred_dup = False
        if ref and ref in preds:
            pred_dup = (_CScC.duplicate_key(preds[c["id"]].record)
                        == _CScC.duplicate_key(preds[ref].record))
        if pred_dup == gold_dup:
            dup_correct += 1

    _, _, e_f1 = _prf(e_tp, e_fp, e_fn)
    metrics = {
        "classification_accuracy": round(class_correct / n, 4) if n else 1.0,
        "entity_f1": round(e_f1, 4),
        "grounding_rate": round(grounded / n, 4) if n else 1.0,
        "student_pii_leak_rate": round(pii_leaks / n, 4) if n else 0.0,
        "answer_completeness": round(sum(completeness_scores) / n, 4) if n else 1.0,
        "duplicate_accuracy": round(dup_correct / dup_total, 4) if dup_total else 1.0,
    }
    return {"metrics": metrics, "n_cases": n, "detail": detail,
            "duplicate_cases": dup_total}


def gate(metrics: Dict[str, float]) -> Tuple[bool, List[str]]:
    """Return (passed, failures) against THRESHOLDS."""
    failures: List[str] = []
    for name, thr in THRESHOLDS.items():
        val = metrics.get(name, 0.0)
        if name in LOWER_IS_BETTER:
            if val > thr:
                failures.append(f"{name}={val} exceeds max {thr}")
        elif val < thr:
            failures.append(f"{name}={val} below min {thr}")
    return (not failures), failures
