# Worked ROI case study — Student & Family Concierge (Agent 01)

**What this is.** A fully worked, illustrative ROI example with totals — the value counterpart to
[`TCO-MODEL.md`](TCO-MODEL.md). Illustrative, source-tagged assumptions; not a guarantee or a customer
result. Replace bracketed inputs with the institution's actuals. `[MODEL ASSUMPTION]` marks editable
drivers.

## Scenario: a regional university, ~20,000 students

| Input | Value | Source |
|---|---|---|
| Annual inbound student/family contacts (aid, deadlines, status, scheduling) | 540,000 | `[MODEL ASSUMPTION]` |
| Share routine/deflectable | 55% → 297,000 | `[GOV]` FAFSA-cycle unanswered-call data indicates large routine volume |
| Fully-loaded cost per human-handled contact | $7.50 | `[MODEL ASSUMPTION]` |
| Cost per AI-handled contact | ~$0.10 | `[MODEL ASSUMPTION]` |
| Enrollment/retention lever: contacts that, if answered promptly, avoid melt | see below | `[PEER-REVIEWED]` responsiveness ↔ retention |

## The intervention

Agent 01 answers routine student/family questions (aid status, deadlines, how-to) and drafts service
requests through the governed gateway with **FERPA rights-transfer and COPPA under-13 handling at the
identity layer**; consequential actions are human-gated. Two levers: contact deflection and
summer-melt / early-attrition avoidance from faster responsiveness.

## Worked value (illustrative)

| Line | Calculation | Annual value |
|---|---|---|
| Contacts automated | 297,000 × 45% target | 133,650 |
| Cost today (human) | 133,650 × $7.50 | $1,002,375 |
| Cost with AI | 133,650 × $0.10 | $13,365 |
| Deflection saving | | **~$989,000** |
| Retention lever (illustrative) | avoid melt on 40 students × $12,000 net tuition | **$480,000** |
| **Gross annual benefit (illustrative)** | | **~$1.47M** |

## Cost side (from TCO-MODEL.md)

| Line | Annual |
|---|---|
| AWS run cost (production scale, from TCO-MODEL) | ~$32,592/yr |
| Implementation + integration (one-time, engagement) | `[MODEL ASSUMPTION]` $120,000–$300,000 |

## ROI

Deflection alone (~$989K) against ~$33K/yr AWS + a one-time build pays back in a fraction of a year;
the retention lever, though harder to attribute, can dwarf it. For a CFO/provost: the AWS cost is
immaterial; the gate is student-data governance (FERPA/COPPA) and integration — which is exactly what
the platform addresses.

## Honesty rails

- Illustrative model, not an institutional outcome or guarantee. Contact volumes, per-contact cost,
  and especially the retention lever vary widely and are hard to attribute — treat retention as
  upside, not a commitment. Use actuals; start with a synthetic pilot.
- The agent answers and drafts; **humans own consequential actions**, and grading/decisions stay
  human-gated. Value assumes that model.
- Minor-safety and FERPA/COPPA handling are design features, not certifications — the institution owns
  its privacy determination.
- Bedrock token volume is the dominant variable cost (see TCO-MODEL sensitivity); immaterial to this ROI.
