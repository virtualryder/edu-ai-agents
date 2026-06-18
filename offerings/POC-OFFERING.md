# Proof-of-Concept Offering
### A 2–4 Week, Demo-Mode Proof of Concept for the EDU AI Agent Suite

> A POC proves the **idea and the controls** before a single live system is touched. It runs entirely in `EXTRACT_MODE=demo` against deterministic fixtures — no API keys, no connection to PowerSchool, Banner, Canvas, or ServiceNow, no student PII. The deliverable is a credible, governed, hands-on demonstration that an institution's leadership, CISO, privacy officer, and academic stakeholders can react to — and a written verdict on whether to fund a pilot.

This is the lowest-commitment, lowest-risk entry point in the engagement model. It exists because the question education buyers actually need answered first is not "does the model work?" — they have all used a chatbot. It is "**can an AI agent act on a student record in a way my CISO and privacy officer will accept?**" A POC answers that question with running software, not slides.

---

## 1. What the POC is — and is not

| The POC is | The POC is not |
|---|---|
| A demonstration of one agent (typically **01 Concierge**) running end-to-end in demo mode, with the MCP authorization gateway, student-PII masking, the HITL gate, and the audit trail all live | A pilot — it touches no live system of record and processes no real student data |
| Proof that the **governance is real and enforced**, not narrated — the security reviewer can watch a deny, a PII mask, and a human-gated write happen | A production system, a certified product, or a WCAG-conformance-tested deployment |
| A shared artifact for a workshop with leadership, IT, privacy, and academic stakeholders | An integration project — no connector is wired to a customer API |
| A written go/no-go input to the pilot decision, mapped to the customer's actual pain | A commitment to a specific agent, vendor system, or hosting option |

The POC sits at the **Demonstrated** rung of the maturity ladder: code runs end-to-end on deterministic fixtures, suitable for internal demos and early customer workshops. It deliberately stops short of **Deployable** (which requires the customer AWS account and Bedrock access) and **Production-ready** (which requires the full security, privacy, IdP, connector, and accessibility work).

---

## 2. Scope

### Landing agent: 01 Student & Family Services Concierge
The Concierge is the default POC subject for the same reasons it is the best first production deployment: it is the most visible agent to the most users, the lowest in decision-risk, and the easiest to measure. In demo mode it demonstrates the full bounded-agent loop — authenticate, check a (fixture) financial-aid or application status, explain an institutional term grounded in approved content, schedule an appointment, open an advising case, draft a family message, and escalate an exception — without ever holding a real credential.

A POC may instead land on **03 Educator Copilot**, **08 Operations Service Desk**, or **07 Document & Accessibility Services** when the customer's most acute pain or most engaged sponsor sits there. These four are the best-first set: broad visibility, comparatively low decision-risk, mature workflows, and measurable deflection/cycle-time return. The higher-governance agents (02, 04, 05, 06) are not POC subjects — they touch learning and student outcomes directly and require the evaluation, oversight, and bias-testing depth that only a pilot can establish.

### In scope
- One agent, running in `EXTRACT_MODE=demo` with deterministic fixtures.
- The **MCP authorization gateway** demonstrated live: deny-by-default authorization, least-privilege role intersection across student / guardian / educator / counselor / administrator, and the bright-line rule that the agent can never exceed the human it acts for.
- **Student-PII masking** shown operating before any content enters a prompt or audit record.
- The **HITL gate** demonstrated on a consequential (write/irreversible) action — the action blocks until a named, authorized reviewer is bound into the record.
- The **PII-masked, append-only audit trail** shown logging every attempt (ALLOW / DENY / PENDING_APPROVAL / ERROR) with lineage to the (fixture) system of record.
- A scripted demo narrative mapped to two or three of the customer's own scenarios, expressed in their vocabulary (their terms, their departments, their pain).
- A facilitated stakeholder workshop.

### Out of scope (deferred to pilot or assessment)
- Any connection to a live SIS / LMS / ERP / CRM / ITSM.
- Any real student, family, or staff data.
- IdP integration and customer role mapping (demonstrated with fixture identities only).
- Bedrock Guardrail tuning for the customer's population.
- WCAG 2.2 AA conformance testing of a customer-facing surface.
- State student-privacy-law mapping (that is the Assessment offering's job).
- Production AWS account provisioning.

---

## 3. Timeline and activities (2–4 weeks)

| Week | Focus | Activities |
|---|---|---|
| **0 (pre-start)** | Framing | Confirm landing agent and 2–3 customer scenarios; identify workshop stakeholders (sponsor, IT, CISO/security delegate, privacy officer, an academic or service owner); agree on the go/no-go criteria up front. |
| **1** | Configure the demo | Stand up the suite in demo mode; load fixtures that reflect the customer's institution type (district / college / university / online / workforce); tailor the grounding content (a slice of their public policy/catalog language) and the agent's vocabulary to the customer. |
| **2** | Build the narrative | Script the demo against the customer's scenarios; wire the governance moments into the script (a deny, a PII mask, a human-gated write, an audit entry the reviewer can read); rehearse internally. |
| **3** | Workshop + iterate | Run the facilitated stakeholder workshop; capture objections and questions live (privacy, accuracy, accessibility, equity, lock-in, cost — see `OBJECTION-HANDLING.md`); adjust the demo to address the sharpest concerns. |
| **4 (or end of wk 3)** | Verdict | Deliver the POC findings memo, the recorded demo, and the recommended pilot scope; hold the go/no-go conversation. |

A focused 2-week POC compresses weeks 1–2 and runs a single workshop; a 4-week POC adds a second iteration cycle and a broader stakeholder round (e.g., a separate session for the school board or cabinet, drawn from `docs/STAKEHOLDER-SECURITY-BRIEFINGS.md`).

---

## 4. Deliverables

1. **A running demo** of the landing agent in `EXTRACT_MODE=demo`, configured to the customer's institution type, scenarios, and vocabulary.
2. **A recorded walkthrough** of the demo, including the governance moments, suitable for circulation to stakeholders who could not attend live (board, cabinet, additional IT/security staff).
3. **A facilitated stakeholder workshop** and a captured objection/question log with responses.
4. **A POC findings memo**: what was demonstrated, which customer scenarios it addressed, which objections were raised and how they were answered, and what the POC did *not* prove (and why those questions belong to the assessment or pilot).
5. **A recommended pilot scope**: the proposed live system of record, the gateway-first sequencing, the baseline metrics to capture, and the exit criteria to production — handed off to `PILOT-OFFERING.md`.
6. **A pointer to the readiness gaps** that the `ASSESSMENT-OFFERING.md` discovery would close (IdP/role mapping, FERPA/COPPA posture, state-law mapping, accessibility baseline, system inventory).

---

## 5. Success criteria

The POC is successful when **all** of the following are true:

- Stakeholders have seen — not been told — that the agent operates under deny-by-default authorization, masks student PII before it reaches a prompt or log, blocks consequential actions behind a named human approver, and produces a tamper-evident audit trail.
- The security and privacy stakeholders can articulate, in their own words, why this is "an agent that acts under governed control" rather than "a chatbot with API keys."
- At least two of the customer's own scenarios were demonstrated in their vocabulary, and the relevant service or academic owner agreed the workflow is recognizable and valuable.
- The customer has a clear, written go/no-go decision and, if go, an agreed pilot scope with baseline metrics identified.

Note what is **not** a success criterion: chat volume, demo polish, or "the AI sounded smart." Per the platform's standing principle, ROI in education is measured on outcomes — deflection, cycle time, learning, persistence — not conversations. The POC's job is to make those outcomes *credible and governed*, not to claim them.

---

## 6. What the POC proves (and what it deliberately leaves open)

| It proves | It does not prove (next phase) |
|---|---|
| The bounded-agent model is real: the agent retrieves, analyzes, drafts, initiates low-risk workflows, and escalates — and never decides grades, admissions, discipline, financial aid, special-education eligibility, or placement. | That the agent performs correctly against the customer's *live* SIS/LMS data (pilot). |
| The MCP authorization gateway enforces identity, least privilege, the human gate, and audit — the controls a CISO, privacy officer, and registrar need to say yes. | That the customer's IdP, role mapping, and age-of-majority/guardian rules integrate cleanly (assessment + pilot). |
| The governance is enforced by the framework, not by trusting the model — a reviewer can watch a deny and a PII mask happen. | That the deployment meets WCAG 2.2 AA on the customer's surfaces (pilot/production gate). |
| The workflow maps to the customer's real pain in their own vocabulary. | The measured outcome (deflection, cycle time) in the customer's environment (pilot establishes the baseline and measures the lift). |

---

## 7. Why this sequencing works for education buyers

Education AI programs do not usually stall on the model. They stall at the **security and privacy review** — when the CISO, the privacy officer, and the registrar ask who is allowed to do what, whether a human signs consequential actions, and whether every access can be proven to a parent or auditor. The POC front-loads exactly that conversation, with running software, before the institution has spent on integration. It is the cheapest way to find out whether the governed-platform story lands with the people who can stop the program — and it sets up the pilot to be a measurement exercise rather than an argument.

Proven analogs that started from this kind of bounded, visible, measurable first step include UA–Pulaski Tech's MyAgent (94.5% adoption, a 253% lift in admissions engagement) and Highline College's financial-aid self-service (a 75% reduction in status emails, calls, and visits, and FAFSA processing time roughly halved) — Concierge-class workflows where the value showed up as deflection and cycle time, exactly what a pilot would baseline and measure after a POC like this proves the controls.

---

## 8. Related offerings

- **Before / alongside:** `ASSESSMENT-OFFERING.md` — discovery/readiness (FERPA/COPPA posture, IdP & role mapping, system inventory, accessibility baseline, state-law mapping, use-case prioritization). A POC can run in parallel with an assessment; the assessment closes the gaps the POC surfaces.
- **After:** `PILOT-OFFERING.md` — the 6–12 week pilot with one live system of record and the gateway in Phase 1.
- **Supporting:** `COST-ROI-MODEL.md` (the outcome-baseline categories the POC recommends capturing), `OBJECTION-HANDLING.md` (the workshop's objection log), `docs/WHY-THE-MCP-LAYER.md` (the gateway-first talk track), `SOLUTION-FIELD-GUIDE.md` (qualification and the land-with-01 motion).
