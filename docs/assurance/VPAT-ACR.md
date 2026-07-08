# Accessibility Conformance Report (ACR) — VPAT® 2.5 (draft self-assessment)

### EDU AI Agent Suite

**Name of product:** EDU AI Agent Suite (reference accelerator)
**Report date:** 2026-07-08 · **Version:** draft self-assessment
**Contact:** report issues via the repository's GitHub Security/Issues per `SECURITY.md`
**Evaluation methods used:** review of the deterministic accessibility preflight
(`governance/accessibility/wcag.py`), source and template review, and design inspection. **No
third-party audit, assistive-technology testing, or automated CI scan has been performed.**

> **Read this first — honest status.** This is a **draft self-assessment for a reference
> accelerator, not a conformance claim for a shipped product.** The suite is a starting point an
> institution deploys and configures; the *deployed* agent UI and the *AI-generated output* are what
> must actually conform. A concrete ACR for a real deployment must be produced by the deploying
> institution after the conformance activities in
> [`ACCESSIBILITY-CONFORMANCE-PLAN.md`](ACCESSIBILITY-CONFORMANCE-PLAN.md) (automated scanning,
> keyboard + screen-reader testing, PDF/UA review, and testing by people with disabilities). This is
> not legal advice. Conformance-level terms below use the ITI VPAT definitions: **Supports /
> Partially Supports / Does Not Support / Not Applicable / Not Evaluated.**

## Applicable standards / guidelines

| Standard | Included |
|---|---|
| WCAG 2.1 Level A and AA | Yes (target) |
| WCAG 2.2 Level A and AA | Yes (institution's deployed target; DOJ ADA Title II adopts WCAG 2.1 AA, compliance dates 2027/2028) |
| Revised Section 508 (2017) | Yes |
| EN 301 549 | Referenced (institutions with EU obligations) |

## Terms

- **Supports** — meets the criterion (with any noted caveats).
- **Partially Supports** — some functionality does not meet the criterion.
- **Does Not Support** — majority of functionality does not meet the criterion.
- **Not Evaluated** — not yet assessed (no AT/audit testing performed for this draft).

Because no assistive-technology testing has been performed, criteria whose satisfaction depends on
rendered behavior are marked **Not Evaluated** rather than claimed. The shipped preflight
(`wcag.py`) provides *partial automated pre-send coverage* for the criteria noted; a preflight is not
conformance.

## Table 1 — WCAG 2.x Level A (representative)

| Criterion | Conformance | Remarks |
|---|---|---|
| 1.1.1 Non-text Content | Partially Supports | Preflight flags missing text alternatives on generated HTML; images the institution adds and PDF alt text are Not Evaluated |
| 1.3.1 Info and Relationships | Partially Supports | Preflight checks heading/structure on generated content; deployed UI Not Evaluated |
| 2.1.1 Keyboard | Not Evaluated | Depends on the deployed UI framework; requires manual test |
| 2.4.2 Page Titled | Partially Supports | Generated pages titled; UI Not Evaluated |
| 3.1.1 Language of Page | Partially Supports | Generation sets language; UI Not Evaluated |
| 4.1.2 Name, Role, Value | Not Evaluated | Requires AT testing of the deployed UI |

## Table 2 — WCAG 2.x Level AA (representative)

| Criterion | Conformance | Remarks |
|---|---|---|
| 1.4.3 Contrast (Minimum) | Not Evaluated | Requires contrast analysis of the deployed theme; institution owns the UI palette |
| 1.4.5 Images of Text | Supports | Suite generates text, not images of text |
| 1.4.10 Reflow | Not Evaluated | 320px / 400% zoom manual test required on the deployed UI |
| 1.4.11 Non-text Contrast | Not Evaluated | Deployed UI component contrast; manual |
| 2.4.6 Headings and Labels | Partially Supports | Preflight checks generated-content headings/labels |
| 3.3.1 / 3.3.3 Error Identification / Suggestion | Not Evaluated | Deployed form behavior |
| 4.1.3 Status Messages | Not Evaluated | Deployed UI live-region behavior |

## Section 508 — Chapters 3–5 (summary)

| 508 area | Conformance | Remarks |
|---|---|---|
| Ch. 3 Functional Performance Criteria | Not Evaluated | Requires AT testing |
| Ch. 4 Hardware | Not Applicable | Software-only suite |
| Ch. 5 Software (incl. 502/503 interoperability with AT) | Not Evaluated | Deployed-UI dependent |
| 504 Authoring Tools — accessible output | Partially Supports | The suite is an authoring surface; preflight nudges output toward AA, but tagged-PDF/PDF-UA for Agent 07 documents is **Does Not Support** in the preflight and must be added |

## Documents (Agent 07 and family-facing output)

Untagged PDFs and missing text alternatives are the most common accessibility-complaint category.
The preflight is an HTML pre-send check and **does not produce PDF/UA-tagged documents** — closing
this is a named item in the conformance plan and is required before a "Supports" claim for
document-generation surfaces.

## What must happen before an institution issues a real ACR

Per [`ACCESSIBILITY-CONFORMANCE-PLAN.md`](ACCESSIBILITY-CONFORMANCE-PLAN.md): automated scanning in
CI (axe-core/equivalent), keyboard-only and screen-reader passes (NVDA/JAWS/VoiceOver), color-contrast
verification of the deployed theme, PDF/UA validation for generated documents, and usability testing
with people with disabilities. Only then can the **Not Evaluated** rows be resolved and a deployment-
specific ACR be signed.
