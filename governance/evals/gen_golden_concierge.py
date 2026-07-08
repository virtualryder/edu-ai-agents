"""
Reproducible generator for the Agent 01 (Concierge) scored golden set.

Produces governance/evals/golden/agent01_concierge_scored.json: labeled College-
Scorecard-shaped institution records with gold labels (institution, location,
cost/aid fields) plus a query + gold intent for the classifier, one duplicate pair
(same institution id under two name variants) and one near-miss non-duplicate
(same institution name in two different states). Gold labels are the ground truth
the scorers assert against; the real connector mapping is the prediction. Grow the
set by appending cases and re-running.

    python -m governance.evals.gen_golden_concierge
"""
from __future__ import annotations
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent / "golden" / "agent01_concierge_scored.json"

CASES = []


def raw(rid, name, city, state, tin, tout, debt, adm):
    return {
        "id": rid, "school.name": name, "school.city": city, "school.state": state,
        "latest.cost.tuition.in_state": tin, "latest.cost.tuition.out_of_state": tout,
        "latest.aid.median_debt.completers.overall": debt,
        "latest.admissions.admission_rate.overall": adm,
    }


def add(cid, r, query, intent, **extra):
    gold = {
        "institution": r["school.name"], "city": r["school.city"], "state": r["school.state"],
        "tuition_in_state": r["latest.cost.tuition.in_state"],
        "tuition_out_of_state": r["latest.cost.tuition.out_of_state"],
        "median_debt": r["latest.aid.median_debt.completers.overall"],
        "admission_rate": r["latest.admissions.admission_rate.overall"],
        "intent": intent,
    }
    gold.update(extra)
    CASES.append({"id": cid, "raw": r, "query": query, "gold": gold})


# ── LOOKUP: facts about one named institution (no state word in the query) ────
add("CS-0001", raw(110404, "Rice University", "Houston", "TX", 54960, 54960, 15000, 0.0868),
    "How much is tuition at Rice University?", "LOOKUP")
add("CS-0002", raw(198419, "Duke University", "Durham", "NC", 63450, 63450, 20500, 0.0635),
    "What is the cost to attend Duke University?", "LOOKUP")
add("CS-0003", raw(243744, "Stanford University", "Stanford", "CA", 56169, 56169, 13000, 0.0368),
    "How much does Stanford University cost?", "LOOKUP")
add("CS-0004", raw(166027, "Harvard University", "Cambridge", "MA", 55587, 55587, 12665, 0.0324),
    "What is the median debt at Harvard University?", "LOOKUP")
add("CS-0005", raw(130794, "Yale University", "New Haven", "CT", 62250, 62250, 13625, 0.0457),
    "What is the admission rate at Yale University?", "LOOKUP")
add("CS-0006", raw(221999, "Vanderbilt University", "Nashville", "TN", 60348, 60348, 18000, 0.0667),
    "How much is tuition at Vanderbilt University?", "LOOKUP")
add("CS-0007", raw(139658, "Emory University", "Atlanta", "GA", 57120, 57120, 17250, 0.1090),
    "What does Emory University cost?", "LOOKUP")
add("CS-0008", raw(131496, "Georgetown University", "Washington", "DC", 62052, 62052, 21500, 0.1200),
    "What is tuition at Georgetown University?", "LOOKUP")

# ── Near-miss: same institution NAME in two different states -> NOT duplicates ─
add("CS-0009", raw(178615, "Lincoln University", "Jefferson City", "MO", 8038, 15046, 24000, 0.9962),
    "What is the admission rate at Lincoln University?", "LOOKUP",
    is_duplicate=False, dup_of="CS-0010")
add("CS-0010", raw(216542, "Lincoln University", "Lincoln University", "PA", 11279, 16481, 27500, 0.7400),
    "Is Lincoln University affordable?", "LOOKUP",
    is_duplicate=False, dup_of="CS-0009")

# ── Duplicate pair: same institution id under two name variants -> duplicates ──
add("CS-0011", raw(236948, "University of Washington-Seattle Campus", "Seattle", "WA", 12973, 43209, 14615, 0.3915),
    "Tell me about the University of Washington", "SEARCH")
add("CS-0012", raw(236948, "University of Washington - Seattle", "Seattle", "WA", 12973, 43209, 14615, 0.3915),
    "University of Washington-Seattle Campus details", "SEARCH",
    is_duplicate=True, dup_of="CS-0011")

# ── SEARCH: list / compare institutions by state ──────────────────────────────
add("CS-0013", raw(112862, "De Anza College", "Cupertino", "CA", 1454, 8722, 9500, 1.0),
    "community colleges in California", "SEARCH")
add("CS-0014", raw(224545, "Austin Community College District", "Austin", "TX", 3630, 12630, 11000, 1.0),
    "compare community colleges in Texas", "SEARCH")
add("CS-0015", raw(135717, "Miami Dade College", "Miami", "FL", 2838, 9661, 8500, 1.0),
    "list affordable colleges in Florida", "SEARCH")
add("CS-0016", raw(209533, "Portland Community College", "Portland", "OR", 4590, 10800, 10250, 1.0),
    "cheapest schools in Oregon", "SEARCH")
add("CS-0017", raw(139940, "Georgia State University", "Atlanta", "GA", 9112, 24855, 22000, 0.7600),
    "which universities are in Georgia?", "SEARCH")

# ── STATUS: personal application/record questions -> route to the SIS, not here ─
add("CS-0018", raw(204796, "Ohio State University-Main Campus", "Columbus", "OH", 11936, 35019, 24000, 0.5700),
    "What is my application status?", "STATUS")
add("CS-0019", raw(134130, "University of Florida", "Gainesville", "FL", 6381, 28658, 18000, 0.2300),
    "Did you receive my transcript?", "STATUS")
add("CS-0020", raw(104151, "Arizona State University Campus Immersion", "Tempe", "AZ", 11348, 29438, 21000, 0.8800),
    "What's my aid status?", "STATUS")


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"cases": CASES}, indent=2), encoding="utf-8")
    print(f"wrote {len(CASES)} cases -> {OUT}")


if __name__ == "__main__":
    main()
