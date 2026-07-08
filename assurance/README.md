# EDU Agentic AI Suite — Auditor & GRC Assurance Packet

**Cover sheet and curated index for an education security/privacy reviewer, district or
institutional CISO, or GRC assessor.** This packet does not duplicate content — it points to the
artifacts already in this repository, organized under standard assurance headings. Links are
relative to the repository root.

> **Note:** this top-level `assurance/` README is the auditor cover sheet / index. Several of
> the underlying assurance artifacts live under [`../docs/assurance/`](../docs/assurance/)
> (threat model, IAM matrix, accessibility conformance, privacy-impact template) and are linked
> from here.

---

## 1. Purpose & scope

Eight education agents (student/family concierge, tutor, educator copilot, assessment,
accessibility services, etc.) on the shared Aegis control plane, built on AWS. This packet lets a
reviewer answer a FERPA / COPPA / IDEA / WCAG questionnaire directly from repository artifacts.

> **Honesty line.** This suite is a **reference accelerator, not an ATO'd product and not a
> compliance certification.** It ships control *design* and reference IaC. Control operation on
> live student data, WCAG conformance testing, IdP/role mapping, and accountability for
> compliance are **customer-owned**. See the maturity matrix in [`../README.md`](../README.md)
> for Implemented vs. Configurable (customer-owned).

---

## 2. Architecture & data-flow diagrams

- Student data flow (FERPA/COPPA claims at the identity layer; record-level authorization; educator-gated grading release) — [`../docs/diagrams/student-data-flow.svg`](../docs/diagrams/student-data-flow.svg) ([PNG](../docs/diagrams/student-data-flow.png))
- MCP gateway authorization flow (shared control plane, deny paths) — [`../docs/diagrams/mcp-gateway-auth-flow.svg`](../docs/diagrams/mcp-gateway-auth-flow.svg) ([PNG](../docs/diagrams/mcp-gateway-auth-flow.png))
- Suite architecture (edge-to-data narrative) — [`../docs/SUITE-ARCHITECTURE.md`](../docs/SUITE-ARCHITECTURE.md)
- AWS Well-Architected GenAI lens — [`../docs/WELL-ARCHITECTED-GENAI-LENS.md`](../docs/WELL-ARCHITECTED-GENAI-LENS.md)

## 3. Threat model & abuse cases

- STRIDE threat model, abuse cases, threat → control → file — [`../docs/assurance/THREAT-MODEL.md`](../docs/assurance/THREAT-MODEL.md)

## 4. Control mappings (NIST AI RMF; FERPA / COPPA / IDEA / Section 504 / WCAG)

- Regime → platform/AWS control mapping (FERPA, COPPA, IDEA/504, ADA Title II / 508 / WCAG 2.1 AA, GLBA, Title VI, NIST AI RMF, state student-privacy laws) — [`../README.md`](../README.md) (§ "Security & Regulatory Alignment") and code in [`../governance/controls/control_mappings.py`](../governance/controls/control_mappings.py)
- Accessibility conformance plan (WCAG 2.1 AA, VPAT pathway) — [`../docs/assurance/ACCESSIBILITY-CONFORMANCE-PLAN.md`](../docs/assurance/ACCESSIBILITY-CONFORMANCE-PLAN.md); enforced WCAG pre-flight in [`../governance/accessibility/wcag.py`](../governance/accessibility/wcag.py)
- Privacy Impact Assessment template — [`../docs/assurance/PRIVACY-IMPACT-ASSESSMENT-TEMPLATE.md`](../docs/assurance/PRIVACY-IMPACT-ASSESSMENT-TEMPLATE.md)
- Per-agent education-compliance notes — each `../NN-*/docs/edu-compliance.md`
- NIST 800-53 matrix / OWASP-LLM+ATLAS mapping: **not present as standalone docs** — customer-owned; nearest equivalents are the threat model, control mappings code, and the platform overlay in the Aegis platform (`packs/education`).

## 5. Identity, authorization & human-in-the-loop controls

- IAM / authorization matrix (agent-grant ∩ user-entitlement, deny-by-default, minor-aware `custom:under_13` claim, guardian roles) — [`../docs/assurance/IAM-MATRIX.md`](../docs/assurance/IAM-MATRIX.md)
- Why the MCP layer / gateway enforcement — [`../docs/WHY-THE-MCP-LAYER.md`](../docs/WHY-THE-MCP-LAYER.md)
- Bright-line HITL gate on every consequential decision; fairness/equity review — [`../governance/fairness/`](../governance/fairness/), [`../governance/redteam/`](../governance/redteam/)

## 6. Data protection (encryption, masking, WORM audit, residency)

- Student-PII masking, minor-aware masking, KMS CMK encryption, tamper-evident audit — see [`../docs/SUITE-ARCHITECTURE.md`](../docs/SUITE-ARCHITECTURE.md) and [`../docs/assurance/THREAT-MODEL.md`](../docs/assurance/THREAT-MODEL.md)
- Residency: student data stays in the institution's AWS account/region and no student data trains models; residency guarantees are **customer-owned** (region pinning, endpoint policy).

## 7. Deployment evidence

- Clean-account acceptance run — [`../evidence/CLEAN-ACCOUNT-ACCEPTANCE.md`](../evidence/CLEAN-ACCOUNT-ACCEPTANCE.md)
- AWS deployment validation & verification run — [`../docs/AWS-DEPLOYMENT-VALIDATION.md`](../docs/AWS-DEPLOYMENT-VALIDATION.md), [`../docs/AWS-DEPLOYMENT-VERIFICATION-RUN.md`](../docs/AWS-DEPLOYMENT-VERIFICATION-RUN.md)
- No standalone `DEPLOYED-AND-VALIDATED.md` — the two validation docs above are the equivalent.

## 8. Security testing (pen-test, CI gates, SBOM)

- Pen-test scope: **not present as a standalone doc** — customer-owned; nearest equivalent is the threat model above.
- CI security gates — [`../.github/`](../.github/) workflows; Bandit baseline ([`../.bandit-baseline.json`](../.bandit-baseline.json)), secrets baseline ([`../.secrets.baseline`](../.secrets.baseline)), cfn-lint ([`../.cfnlintrc`](../.cfnlintrc)); test suite via `make test`.
- SBOM: not present as a static artifact — **customer-owned**, generated per build/release.
- Third-party risk (TPRM) due-diligence packet — [`../offerings/TPRM-DUE-DILIGENCE-PACKET.md`](../offerings/TPRM-DUE-DILIGENCE-PACKET.md)

## 9. Shared-responsibility / RACI

- Production-readiness action plan — [`../docs/PRODUCTION-READINESS-ACTION-PLAN.md`](../docs/PRODUCTION-READINESS-ACTION-PLAN.md)
- Shared-responsibility matrix — [`../docs/SHARED-RESPONSIBILITY-MATRIX.md`](../docs/SHARED-RESPONSIBILITY-MATRIX.md)
- Incident response runbook — [`../runbooks/INCIDENT-RESPONSE.md`](../runbooks/INCIDENT-RESPONSE.md)

## 10. Known limitations & maturity

- Capability maturity matrix — [`../README.md`](../README.md) (§ "Capability maturity matrix")
- Suite status — [`../SUITE-STATUS.md`](../SUITE-STATUS.md)
- Second-review action plan (self-assessment backlog) — [`../docs/SECOND-REVIEW-ACTION-PLAN.md`](../docs/SECOND-REVIEW-ACTION-PLAN.md)

## 11. Contact & reporting

- Vulnerability reporting via **GitHub Security Advisories** (repository *Security* tab →
  *Report a vulnerability*) — see [`../SECURITY.md`](../SECURITY.md). Do not open public issues
  for security reports.

---

*Reference accelerator — not an AWS service, not AWS-supported software, not a compliance
certification, and not production-ready for regulated data without customer-specific
engineering, testing, authorization, and operational ownership.*
