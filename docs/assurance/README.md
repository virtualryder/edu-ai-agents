# Customer Assurance Package

The artifacts a CISO, privacy officer, accessibility lead, or security review board asks for before approving a deployment. Each is grounded in this repo's actual controls (every claim cites a file) and is honest about what is pre-filled vs. **[CUSTOMER TO COMPLETE]** and what residual risk remains (cross-referenced to [`../PRODUCTION-READINESS-ACTION-PLAN.md`](../PRODUCTION-READINESS-ACTION-PLAN.md)).

| Document | What it is | Primary reviewer |
|---|---|---|
| [THREAT-MODEL.md](THREAT-MODEL.md) | STRIDE threat model — assets, 7 trust boundaries, data flow, threats → mitigations (file-cited) → residual risk, abuse cases | CISO / security architecture |
| [IAM-MATRIX.md](IAM-MATRIX.md) | Least-privilege matrix — human roles → tool entitlements (from `policy.py`), AWS principals → permissions → resources → conditions, separation of duties, gaps | CISO / cloud security |
| [PRIVACY-IMPACT-ASSESSMENT-TEMPLATE.md](PRIVACY-IMPACT-ASSESSMENT-TEMPLATE.md) | FERPA/COPPA/state-law PIA the institution completes; platform controls pre-filled | Privacy officer / general counsel |
| [ACCESSIBILITY-CONFORMANCE-PLAN.md](ACCESSIBILITY-CONFORMANCE-PLAN.md) | WCAG 2.x AA / ADA Title II plan for the UI and AI-generated output; preflight vs. conformance, test matrix, VPAT/ACR stub | Accessibility lead / Section 508 |

**Scope note.** These are written against the **Agent 01 golden path + shared platform**. Extend per agent as the suite expands. None of this is legal advice; the institution owns the FERPA/COPPA determinations, the conformance testing, and acceptance of residual risk.

- **Accessibility Conformance Report (VPAT 2.5 draft):** [`VPAT-ACR.md`](VPAT-ACR.md) — the ACR artifact procurement/committees request, alongside the [`ACCESSIBILITY-CONFORMANCE-PLAN.md`](ACCESSIBILITY-CONFORMANCE-PLAN.md).
