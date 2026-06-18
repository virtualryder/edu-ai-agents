# Managed Service Offering
### Running and Operating Governed EDU AI Agents in Production

> Deploying a governed agent is the start, not the finish. A production agent that acts on student records carries ongoing operational obligations: a human-in-the-loop queue that must be staffed and stay responsive; model and prompt changes that must pass change control before they reach a student; evaluation and fairness monitoring that must run continuously; accessibility conformance that must be maintained as surfaces evolve; and an incident-response path for the day something goes wrong. This offering is the run/operate layer that keeps the bounded-agent posture true after go-live — and keeps the institution audit-ready.

The managed service begins when a pilot exits to production (`PILOT-OFFERING.md`) and the operational readiness criteria are met. It can be delivered as a fully SI-run service, a co-managed model where institutional staff own parts of the workflow, or an advisory model where the SI operates the platform and trains the institution to run it.

---

## 1. The operating principle

In production, the controls that made the agent deployable must keep holding every day, against drift: model updates, prompt edits, new content, changed roles, evolving surfaces, and adversarial inputs. The managed service exists to ensure the governance is not a launch artifact but a living operation — that the deny-by-default authorization, the enforced HITL gate, the grounding verification, the PII masking, and the audit trail keep doing their jobs, and that the institution can prove it to a parent, an auditor, or OCR at any time.

---

## 2. Service components

### A. HITL queue operations
The human-approval gate is only effective if the queue behind it is staffed and responsive. The managed service operates the queue mechanics and reports on its health.

- Monitor **HITL queue depth and approval latency** (CloudWatch); alarm on backlog and aging items so consequential actions are not silently stalled.
- Maintain the **reviewer roster and role bindings** so every consequential action is gated to a named, authorized human in the correct role (educator, counselor, registrar, administrator) — and so a reviewer who leaves is removed.
- Track **override and escalation rates** as quality and trust signals (rising overrides may mean a prompt or grounding problem; see eval monitoring).
- Ensure the gateway continues to refuse to mint a write token absent a valid reviewer identity — the framework-enforced gate, not a procedural one.

### B. Model & prompt change control
A model or prompt change is a change to behavior that touches students; it goes through control, not straight to production.

- **Prompt version registry:** prompts stay hash-pinned in `governance/prompt_manifest.json`; CI fails on un-bumped drift. Every prompt change is a reviewed, recorded change with a rollback point.
- **Model-change control:** a Bedrock model version change (or a switch in the LLM factory routing) triggers re-running the eval harness and a sign-off before promotion — model updates do not silently alter a tutoring explanation, an advising plan, or rubric-grounded feedback.
- **Grounding-content updates:** changes to approved institutional content (policies, catalogs, deadlines) are versioned so the agent never grounds against stale or unapproved material.
- **Change calendar and rollback:** scheduled change windows, documented rollback, and an audit entry for every promotion.

### C. Evaluation & fairness monitoring
The eval and fairness frameworks (`governance/`) run continuously, not just in CI at build time.

- **Structural eval regression:** golden-artifact regression over advising plans, intervention drafts, rubric-graded feedback, and accessible-content output, run on a cadence and on every change — catching quality drift before students do.
- **Grounding-failure monitoring:** track how often grounding fails fast (a healthy control firing) versus ungrounded output slipping through (a control gap).
- **Fairness monitoring:** equity/representativeness flags and **false-positive / false-negative monitoring** on student-success targeting and intervention recommendations, reported by cohort — so disparate impact surfaces as a metric, not a complaint. Higher-governance agents (02, 04, 05, 06) get the most scrutiny here.
- **Red-team cadence:** periodic re-runs of prompt-injection (including injection hidden in student-submitted documents or inbound email), PII-exfiltration, and authorization-bypass scenarios against the live configuration.

### D. Accessibility conformance maintenance
WCAG 2.2 AA conformance is not a one-time gate — surfaces and content change.

- Re-test student- and family-facing surfaces against **WCAG 2.2 AA** when they change, and on a periodic cadence; maintain VPAT/conformance documentation.
- Monitor Agent 07's accessible-content output (alt text, captions, transcripts, plain-language and reading-level variants, audio) and keep human verification on consequential material (individualized plans, legal notices, safety information).
- Maintain multilingual/Title VI language-access coverage as populations and content evolve.

### E. Incident response
A defined path for the day something goes wrong — a suspected disclosure, a Guardrail bypass attempt, a connector failure, a fairness alarm, an availability event.

- **Detection:** CloudWatch and CloudTrail alarms (error-rate spikes, anomalous authorization patterns, queue backlogs) feeding the unified, FERPA-aligned audit record.
- **Containment:** the institution can disable any agent or any tool immediately — no standing service accounts to revoke individually. This is also the FERPA "direct control" lever.
- **Investigation:** the PII-masked, append-only audit trail answers who accessed what, on what basis, and who approved — the questions a parent, auditor, or OCR will ask.
- **Notification:** support the institution's state-specific breach-notification obligations with the audit evidence; the institution owns the legal determination and notification.
- **Post-incident:** root-cause, control improvement (which compounds across all eight agents), and a recorded change.

---

## 3. SLAs and reporting

Illustrative SLA tiers — set to the institution's risk appetite and the agents in production; **figures below are illustrative defaults, not commitments**:

| Dimension | Illustrative target | Notes |
|---|---|---|
| Platform availability | 99.5%+ (business-critical agents) | Excludes scheduled change windows |
| HITL approval-queue health | Alarm if any consequential item ages beyond an agreed threshold (e.g., 4 business hours) | Protects against silent stalls on student-affecting actions |
| Sev-1 incident response | Acknowledge within 1 hour; contain (disable agent/tool) immediately on confirmed disclosure risk | Containment is immediate by design |
| Eval regression | Run on every change + weekly cadence | Block promotion on regression |
| Fairness review | Monthly cohort report; immediate review on a fairness alarm | Heightened for agents 02/04/05/06 |
| Accessibility re-test | On surface change + quarterly | Maintain VPAT/conformance evidence |
| Prompt/model change | Change-controlled with rollback; no un-reviewed promotion to a student-facing path | CI enforces prompt pinning |

**Reporting cadence:** a monthly operations report covering availability, HITL queue health and override/escalation rates, eval and fairness results, grounding-failure rates, accessibility status, incidents and their resolution, and the outcome metrics from `COST-ROI-MODEL.md` (deflection, cycle time, learning, persistence, risk/quality) — so leadership sees value and risk in one place.

---

## 4. What the institution still owns

Consistent with the platform's standing division of responsibility, the managed service operates the control design; the institution retains accountability for: its FERPA/COPPA/PPRA compliance program and data-governance policy; the legal determination on any breach notification; IdP role-mapping decisions and reviewer-roster authority; Guardrail policy appropriate to its population; acceptance of accessibility conformance; state-law obligations; and final approval of any consequential action — which, by design, no agent ever takes autonomously.

---

## 5. Transition into the managed service

The handoff from pilot to managed service is gated on the pilot's operational-readiness exit criteria: a working HITL queue, change control operating, eval/fairness monitoring running, accessibility evidence in hand, and an incident-response path defined. The managed service then assumes (or co-owns) day-to-day operation and scales with portfolio expansion — each new agent inherits the same control plane, so onboarding agent #2 through #8 into the managed service is incremental, not a new build.

---

## 6. Related offerings

- **Before:** `PILOT-OFFERING.md` (the pilot whose exit criteria gate this service).
- **Supporting:** `governance/README.md` (the eval, fairness, red-team, HITL, and grounding frameworks operated here), `COST-ROI-MODEL.md` (the run-cost and outcome metrics reported monthly), `TPRM-DUE-DILIGENCE-PACKET.md` (the incident-response, audit, and data-handling commitments procurement will hold the service to), `docs/SUITE-ARCHITECTURE.md` (Layer 6 observability — CloudWatch/CloudTrail — that powers monitoring).
