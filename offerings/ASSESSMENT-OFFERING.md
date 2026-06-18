# Discovery & Readiness Assessment Offering
### Establishing the FERPA/COPPA, Identity, System, Accessibility, and State-Law Posture Before the Agents

> The assessment is the engagement's diagnostic. It does not deploy an agent. It answers, in writing, the questions that decide whether — and how — the institution can safely put governed AI agents on its student records: What is the data-governance and student-privacy posture? How does identity and role really work here? What systems of record are in play, and how do you reach them? What is the accessibility baseline? Which state laws apply? And, given all of that, which agent should land first and what does the roadmap look like? The output is a prioritized roadmap a CISO, privacy officer, registrar, and academic leadership can sign.

A POC can run in parallel with the assessment — the POC proves the controls are real in demo mode while the assessment closes the readiness gaps the POC surfaces. But a **pilot depends on the assessment's outputs**: the IdP/role model, the system inventory, the state-law mapping, and the accessibility baseline are inputs the pilot's Phase 1 cannot proceed without.

---

## 1. Why an assessment comes before a pilot

Education AI programs stall at the security and privacy review — not because the model is weak, but because the institution discovers, mid-pilot, that its role model does not cleanly express the FERPA age-of-majority transfer, that guardian relationships are not reliably represented in the IdP, that a state law imposes a data-residency or consent requirement nobody mapped, or that the student-facing surface was never tested to WCAG 2.2 AA. Each of those is cheap to find in an assessment and expensive to find in a pilot. The assessment de-risks the pilot by turning unknowns into a documented posture and a sequenced plan.

The assessment is scoped to the **Documented** end of the maturity ladder: its deliverables are written, reviewed artifacts — useful for customer discovery and architecture review — that set up the pilot's path to **Deployable** and **Production-ready**.

---

## 2. The seven assessment workstreams

### A. Data governance & FERPA/COPPA posture
Establish how the institution currently classifies, controls, and discloses education records, and where the gaps are relative to a governed-agent deployment.

- **FERPA:** How are education records defined and access-controlled today? How are disclosures recorded? Is there a "school official / direct control" framework for vendors, and does it extend to an agent acting on the institution's behalf for an authorized purpose? Can the institution disable a vendor's or agent's access immediately?
- **COPPA (where under-13 learners are served):** Is school-authorized consent in place and limited to an educational context? Is there any current behavioral-profiling or non-educational use that an agent must be prohibited from?
- **PPRA:** Are there protected categories (political affiliation, religion, sexual behavior, etc.) that outreach or student-success workflows must never collect or infer?
- **Data minimization & retention:** What retention schedules apply? What is the appetite for returning only the fields a tool needs?

**Output:** a privacy-posture summary mapping each obligation to the platform control that honors it (identity-scoped retrieval, purpose-of-use enforcement, the PII masker, the append-only audit, configurable retention), and a gap list.

### B. Identity provider (IdP) & role mapping
The authorization model is only as good as the identity that feeds it. Map how identity actually works and whether it can carry what the gateway needs.

- **IdP:** Okta, Entra ID, Google Workspace, Active Directory? Federation path via IAM Identity Center / Cognito?
- **Roles:** Can the IdP reliably express **student, guardian, educator, counselor, and administrator**, and the distinctions the gateway enforces between them?
- **Age-of-majority / rights transfer:** Is the FERPA transfer of rights at 18 / postsecondary enrollment represented in claims, so a guardian agent cannot surface records the guardian no longer has a right to?
- **Guardian relationships:** Are parent/guardian-to-student relationships reliably represented and current? (This is frequently the hardest gap in K–12.)
- **Under-13 flag:** Can the IdP carry the COPPA under-13 state that drives heightened Guardrails and data minimization?

**Output:** a role-mapping design (which IdP claims map to which `ROLE_ENTITLEMENTS`), an age-of-majority and guardian-relationship handling plan, and a remediation list where the IdP cannot yet express what the gateway requires.

### C. System inventory (SIS / LMS / ERP / ITSM and the rest)
Catalog the systems of record an agent would act on, and how reachable they are.

| Category | Examples to inventory | What to capture |
|---|---|---|
| **SIS** | PowerSchool, Infinite Campus, Banner, Workday Student | API availability, auth model, rate limits, data owner |
| **LMS** | Canvas, Blackboard, Schoology, Moodle, D2L | LTI 1.3 support, API scopes, course/section/role segmentation |
| **ERP / finance** | Workday, Banner Finance | Procurement/HR/finance API surface, segregation-of-duties rules |
| **CRM** | Slate, Salesforce EDU | Lead/applicant data model, consent capture |
| **ITSM** | ServiceNow, Jira | Ticket API, knowledge-base access, workflow automation |
| **Scheduling / contact center / library / transportation** | Amazon Connect, scheduling systems | Channel coverage, after-hours posture |

**Output:** a system inventory keyed to the connector framework, a "reachability" rating per system (clean API → bespoke/limited), and a recommendation for which single system is the cleanest pilot target.

### D. Accessibility baseline
Student-facing surfaces are subject to ADA and Section 508; WCAG 2.2 AA conformance is a production-readiness gate, not an afterthought.

- What is the current conformance posture of the portals/surfaces the agent would appear in?
- Is there an existing accessibility coordinator, VPAT history, and remediation process?
- What multilingual and reading-level obligations exist (Title VI language access, the populations served)?

**Output:** an accessibility baseline, the conformance gaps that must close before a student-facing surface goes live, and the role Agent 07 (Document & Accessibility Services) could play in remediating content at scale.

### E. State student-privacy & sector-specific law mapping
Most states have their own student-data-privacy law (~140 statutes nationally — e.g., California's SOPIPA), with state-specific consent, data-localization, breach-notification, and vendor-contract requirements.

- Which state(s) does the institution operate in, and what do their student-privacy statutes require?
- Data residency: does any obligation constrain region/VPC placement?
- Consent capture, breach notification, vendor-contract clauses, retention windows?

**Output:** a state-law obligation map, expressed as the platform configuration that satisfies it (the control design is parameterized — data residency, retention, consent capture, and prohibited-use are configuration, not code), plus the contract terms the institution will need from the SI/vendor (feeding the `TPRM-DUE-DILIGENCE-PACKET.md`).

### F. Use-case prioritization
Map the institution's actual pain to the eight agents and rank candidates by value and readiness.

- Where is the most acute, most visible, most measurable pain?
- Which workflows are mature and comparatively low decision-risk (favoring the best-first set: 01, 03, 08, 07)?
- Which valuable workflows touch learning and outcomes directly and therefore require the higher-governance posture (02, 04, 05, 06) the institution may not yet be ready for?

**Output:** a ranked use-case list scoring each candidate on value, decision-risk, system readiness, and governance readiness — converging on a recommended landing agent (default: 01 Concierge) and an expansion order.

### G. Hosting & gateway-model selection
Decide how the institution will build the governed access layer, since the pilot's Phase 1 depends on it.

- Operating model: does the platform team want managed infrastructure, AWS primitives they assemble, or code they own?
- Map to the three options from `docs/WHY-THE-MCP-LAYER.md`: **AgentCore Gateway** (managed default), **AWS primitives** (API Gateway + Lambda + Step Functions), or **FastMCP** (self-built).

**Output:** a recommended gateway hosting model with rationale, noting that the enforcement semantics are identical across all three.

---

## 3. Timeline (typical 3–5 weeks)

| Week | Focus |
|---|---|
| **1** | Kickoff; stakeholder interviews (CISO, privacy/FERPA officer, registrar, CIO, accessibility coordinator, an academic leader, IT service-desk lead); document request |
| **2** | Data-governance/FERPA-COPPA posture, IdP & role mapping, under-13 and guardian-relationship analysis |
| **3** | System inventory and reachability, accessibility baseline, state-law mapping |
| **4** | Use-case prioritization workshop; gateway hosting-model selection |
| **5** | Roadmap synthesis and readout to leadership |

---

## 4. The deliverable: a prioritized roadmap

The assessment produces a single, signable **readiness roadmap** containing:

1. **The posture summary** across all seven workstreams, each obligation mapped to the platform control that honors it.
2. **The gap list** — what must be remediated (in the IdP, the accessibility surfaces, the data-governance program, the contracts) before a pilot and before production.
3. **The recommended landing agent and expansion order**, with the rationale (value × decision-risk × system readiness × governance readiness).
4. **The recommended single pilot system of record** (the cleanest, highest-value target).
5. **The recommended gateway hosting model.**
6. **The baseline-metrics plan** — which of the five ROI categories to instrument before the pilot, and how (handoff to `COST-ROI-MODEL.md`).
7. **The contract/TPRM checklist** the institution's procurement and security teams will run (handoff to `TPRM-DUE-DILIGENCE-PACKET.md`).
8. **A phased plan to a pilot** (handoff to `PILOT-OFFERING.md`), gateway-first.

---

## 5. What the assessment is not

- It is not a legal opinion or a compliance certification. It is a control-design diagnostic the institution operationalizes, validates, and accepts accountability for.
- It does not deploy an agent or touch live student data.
- It does not replace the institution's own FERPA/COPPA/PPRA compliance program — it maps to it and identifies gaps.

---

## 6. Related offerings

- **Parallel:** `POC-OFFERING.md` (demo-mode proof that the controls are real).
- **After:** `PILOT-OFFERING.md` (the pilot the assessment's outputs feed).
- **Supporting:** `governance/README.md` (the compliance spine being assessed), `docs/WHY-THE-MCP-LAYER.md` (the gateway hosting options), `docs/STAKEHOLDER-SECURITY-BRIEFINGS.md` (the interview audience), `TPRM-DUE-DILIGENCE-PACKET.md` (the procurement/security checklist), `SOLUTION-FIELD-GUIDE.md` (qualification questions that seed the assessment).
