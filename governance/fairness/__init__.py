"""
Fairness checks — equity guardrails for student-success targeting.

Student-success and intervention agents must not concentrate recommendations on a
protected or proxy group, and their value should come from assembling evidence
and coordinating action — not from an opaque risk score that becomes a permanent
label (see governance/README.md and IES guidance). These checks support, they do
not replace, the institution's equity review.

Three lightweight, deterministic checks (no protected attributes are stored or
inferred — groups are supplied by the institution's analytics layer for
aggregate monitoring only):

  * representativeness_flag: flags when a cohort's selected-rate for any group is
    disproportionate relative to its base rate beyond a tolerance.
  * confusion_rates: false-positive / false-negative rates for a proposed
    early-warning flag vs. realized outcomes, for ongoing monitoring.
  * four_fifths (in disparate_impact.py): the four-fifths disparate-impact screen
    for any flag/rank workflow — the civil-rights (Title VI / OCR) exposure when a
    model decides whose case to surface as at-risk.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .disparate_impact import DisparateImpactReport, four_fifths  # noqa: F401

__all__ = [
    "representativeness_flag",
    "RepresentativenessReport",
    "confusion_rates",
    "four_fifths",
    "DisparateImpactReport",
]


@dataclass
class RepresentativenessReport:
    flagged_groups: List[str] = field(default_factory=list)
    detail: Dict[str, Dict[str, float]] = field(default_factory=dict)
    tolerance: float = 0.20

    @property
    def equitable(self) -> bool:
        return not self.flagged_groups


def representativeness_flag(
    base_rates: Dict[str, float],
    selected_rates: Dict[str, float],
    tolerance: float = 0.20,
) -> RepresentativenessReport:
    """
    base_rates[g]     = group g's share of the population (0..1)
    selected_rates[g] = group g's share of those the agent selected for outreach
    Flags any group whose relative over/under-selection exceeds `tolerance`.
    """
    report = RepresentativenessReport(tolerance=tolerance)
    for g, base in base_rates.items():
        sel = selected_rates.get(g, 0.0)
        if base <= 0:
            continue
        relative = abs(sel - base) / base
        report.detail[g] = {"base": base, "selected": sel, "relative_delta": round(relative, 3)}
        if relative > tolerance:
            report.flagged_groups.append(g)
    report.flagged_groups.sort()
    return report


def confusion_rates(predicted: List[bool], actual: List[bool]) -> Dict[str, float]:
    """Return false-positive and false-negative rates for monitoring an early-warning flag."""
    if len(predicted) != len(actual) or not predicted:
        raise ValueError("predicted and actual must be non-empty and equal length")
    tp = fp = tn = fn = 0
    for p, a in zip(predicted, actual):
        if p and a:
            tp += 1
        elif p and not a:
            fp += 1
        elif not p and a:
            fn += 1
        else:
            tn += 1
    fpr = fp / (fp + tn) if (fp + tn) else 0.0
    fnr = fn / (fn + tp) if (fn + tp) else 0.0
    return {"false_positive_rate": round(fpr, 3), "false_negative_rate": round(fnr, 3),
            "tp": tp, "fp": fp, "tn": tn, "fn": fn}
