"""
Disparate-impact screening for any agent that FLAGS or RANKS students or cases
(e.g. the Student Success agent's early-warning / at-risk flagging, or any
prioritization workflow).

Implements the four-fifths rule (adapted from the EEOC selection-rate test and
widely used as a screen for disparate impact under Title VI / OCR scrutiny of
education programs): if the flag rate for any group is less than 80% of the rate
for the highest-flagged group, the screen is surfaced for human equity review.
A flag is never proof and is never an automated adverse action — this control
exists so a model that disproportionately flags a protected or proxy group is
caught before any human acts on it. It complements `representativeness_flag` in
this package: representativeness watches *who gets selected for outreach*;
four-fifths watches *whose cases the model flags as at-risk*.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DisparateImpactReport:
    selection_rates: Dict[str, float] = field(default_factory=dict)
    most_selected_group: str = ""
    impact_ratios: Dict[str, float] = field(default_factory=dict)
    flagged_groups: List[str] = field(default_factory=list)

    @property
    def passes_four_fifths(self) -> bool:
        return not self.flagged_groups


def four_fifths(selected: Dict[str, int], totals: Dict[str, int]) -> DisparateImpactReport:
    """
    selected[g] = number of group g flagged by the screen
    totals[g]   = group g's population in the evaluated cohort
    Flags any group whose flag-rate impact ratio (relative to the most-flagged
    group) falls below 0.8 — the four-fifths threshold for human review.
    """
    rep = DisparateImpactReport()
    for g, total in totals.items():
        rep.selection_rates[g] = (selected.get(g, 0) / total) if total else 0.0
    if not rep.selection_rates:
        return rep
    rep.most_selected_group = max(rep.selection_rates, key=rep.selection_rates.get)
    top = rep.selection_rates[rep.most_selected_group] or 1e-9
    for g, rate in rep.selection_rates.items():
        ratio = rate / top
        rep.impact_ratios[g] = round(ratio, 3)
        if ratio < 0.8:
            rep.flagged_groups.append(g)
    rep.flagged_groups.sort()
    return rep
