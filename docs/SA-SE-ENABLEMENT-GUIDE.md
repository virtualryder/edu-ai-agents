# SA/SE Enablement Guide
### "I Just Got Staffed on This — What Do I Do in the First Week?"

> This guide is for the AWS SA or SI SE who is new to the EDU AI Agent Suite engagement. Read this first. It answers the five questions you'll have in the first 48 hours and gives you everything you need to walk into the first customer meeting.

---

## 1. What This Suite Is and Isn't (Read This Before Anything Else)

The EDU AI Agent Suite is a **governed accelerator** — not a chatbot, not a SaaS product, not a point solution. The positioning that matters: **the agents are the visible surface; the platform is the product.**

The platform is an MCP authorization gateway — one deny-by-default enforcement point between every agent and every system of record (SIS, LMS, ERP, CRM, ITSM) — with identity verification, role-scoped authorization, a human-approval gate on consequential actions, PII masking tuned to FERPA/COPPA identifiers, and an append-only audit trail. Built once on the first agent, inherited by all eight. This is what passes the CISO and privacy officer review. This is what differentiates the suite from every other education AI offering. If you remember one thing, remember this: **"not which model, but how do agents get governed access to the data."**

What it is not: a certified product the customer can deploy and hand to students without operationalization. It is a governed accelerator the institution deploys, validates, and accepts compliance accountability for. Be explicit about this distinction with every stakeholder — it is a credibility asset, not a liability.

Eight agents cover: Student & Family Services Concierge (01), Tutor & Study Companion (02), Educator Copilot (03), Assessment & Grading (04), Student Success & Proactive Engagement (05), Pathway Navigator (06), Document & Accessibility Services (07), Operations Service Desk (08). Always land with one of the best-first agents (01, 03, 07, or 08). Never land with a higher-governance agent (02, 04, 05, 06) as the first deployment.

---

## 2. Engagement Phases in 90 Seconds

| Phase | What you do | Key outputs |
|---|---|---|
| **Discovery** | Qualify the opportunity; identify the landing agent; map stakeholders | Qualification scorecard; stakeholder map; POC/Assessment decision |
| **Readiness Assessment** (3–5 wks) | FERPA posture, IdP mapping, system inventory, accessibility baseline, state-law mapping, use-case prioritization | Signed readiness roadmap; recommended pilot target |
| **Demo-Mode POC** (2–4 wks) | Run the suite in `EXTRACT_MODE=demo`; show the 5 governance moments; facilitate go/no-go | POC findings memo; recorded demo; recommended pilot scope |
| **Pilot — Phase 1: Gateway** (wks 1–4) | Deploy MCP gateway, IdP federation, audit trail in customer AWS account | Gateway with deny-by-default, PII masker, HITL gate operating; security reviewer sign-off |
| **Pilot — Phase 2–5** (wks 4–12) | Live connector, grounding, agent, accessibility testing, measurement | Deployed agent; WCAG 2.2 AA report; outcome report vs. baseline |
| **Managed Service** | Operate HITL queue, change control, eval/fairness monitoring, incident response | Monthly ops report; outcome metrics; portfolio expansion roadmap |

The gateway is always Phase 1. Never compress it away.

---

## 3. Critical Artifacts — Read in This Order

| Priority | File | What it is | Why you need it |
|---|---|---|---|
| 1 | `README.md` | Suite overview, positioning, agent table, maturity ladder | The master reference; read all of it |
| 2 | `docs/WHY-THE-MCP-LAYER.md` | Gateway argument — why not just API keys | The answer to "why is this different from a chatbot" |
| 3 | `gtm/BATTLECARD.md` | One-page field reference | Carry into every customer meeting |
| 4 | `gtm/TEASER-DECK.md` | 5-slide executive leave-behind | Send before or after the first executive meeting |
| 5 | `SOLUTION-FIELD-GUIDE.md` | Full qualification, motion, stakeholder map | Read before the first discovery call |
| 6 | `docs/STAKEHOLDER-SECURITY-BRIEFINGS.md` | Per-stakeholder briefings (CISO, privacy officer, CIO, faculty, board) | Use to prep for each stakeholder meeting |
| 7 | `offerings/OBJECTION-HANDLING.md` | Every objection with full responses | Study before your first demo |
| 8 | `gtm/DEMO-STORYBOARD.md` | Scene-by-scene demo script | Run before you demo, not during |
| 9 | `docs/WELL-ARCHITECTED-GENAI-LENS.md` | WAF + GenAI Lens mapping | For SA-led architecture reviews |
| 10 | `docs/SHARED-RESPONSIBILITY-MATRIX.md` | Who owns what | For CISO and procurement conversations |

---

## 4. The Conversations You Will Have and What to Say

### Discovery / First executive meeting
**Key message:** "You already have the data. The problem is governed access to it. We solve the part that makes education AI programs fail — not which model, but how agents get deny-by-default, human-gated, audited access to your student records."

**What to ask:** "Where is your most acute, most visible student- or staff-facing pain — and can you measure it today?" Then: "Has an AI effort here stalled at security or privacy review before?"

### Security / CISO conversation
**Key message:** "Student records never leave your AWS account. The gateway enforces deny-by-default authorization outside the model — a prompt injection can't bypass it. Every access is PII-masked and logged. The audit trail is your FERPA disclosure recordkeeping, automatic. Your IdP controls who gets in; your reviewers approve every consequential action."

**What to bring:** `docs/STAKEHOLDER-SECURITY-BRIEFINGS.md` CISO section; `docs/SHARED-RESPONSIBILITY-MATRIX.md`; `offerings/TPRM-DUE-DILIGENCE-PACKET.md`.

### Procurement / Legal conversation
**Key message:** "The platform is a governed accelerator — not a SaaS product. FERPA accountability stays with the institution. The SOW is explicit: we build and operate the technical controls; you own the compliance program, the role entitlements, the reviewer roster, and the breach-notification obligation. We give you the evidence package."

**What to bring:** `gtm/SOW-TEMPLATE.md`; `docs/SHARED-RESPONSIBILITY-MATRIX.md` §6 (data governance); `offerings/TPRM-DUE-DILIGENCE-PACKET.md`.

### IT / Infrastructure conversation
**Key message:** "Everything deploys to your AWS account via CloudFormation. No agents call your SIS directly — the gateway is the only authorized path. We need your AWS account ready — Bedrock model access, CloudTrail enabled, S3 Object Lock on the audit bucket. Here's the pre-flight checklist."

**What to bring:** `docs/AWS-FUNDING-AND-PREREQUISITES.md` Part B checklist; `infra/cloudformation/quickstart.yaml` for the architecture overview; `infra/terraform/` if they prefer Terraform.

### Executive sponsor conversation
**Key message:** "UA–Pulaski Tech saw 94.5% adoption and 253% admissions-engagement lift. Highline College cut financial-aid status contacts by 75%. You pay for the gateway once on the Concierge; every subsequent agent inherits it. Run the pilot, measure the outcome against a baseline we agree on before go-live."

**What to bring:** `gtm/TEASER-DECK.md`; `gtm/roi-calculator/EDU-AI-Suite-ROI-Calculator.xlsx`; `offerings/COST-ROI-MODEL.md`.

---

## 5. Demo Setup (3 Commands)

```bash
# 1. Install
cd 01-student-family-concierge && pip install -r requirements.txt && pip install -e ../platform_core

# 2. Verify (no credentials needed)
EXTRACT_MODE=demo python -m pytest tests/ -q

# 3. Run
EXTRACT_MODE=demo python demo/demo_live.py
```

The demo runs entirely on fixtures — no AWS account, no API keys, no live system. Show the 5 governance moments in order: (1) grounded public answer, (2) authenticated read + deny, (3) PII masking, (4) human-gated write, (5) audit log. Full script in `gtm/DEMO-STORYBOARD.md`.

**For an advanced demo** (Assessment agent — relevant for faculty and academic leadership audiences): `cd 04-assessment-grading-feedback && EXTRACT_MODE=demo python demo/demo_live.py`

---

## 6. Escalation and Support

| Situation | Who to contact |
|---|---|
| AWS funding request (PoA, MAP) | Your AWS Partner Development Manager (PDM) via Partner Central |
| AgentCore regional availability question | AWS account team SA or Bedrock service team |
| Customer security questionnaire needs SI attestations | SI delivery lead / practice lead — see `offerings/TPRM-DUE-DILIGENCE-PACKET.md` |
| Connector gap (customer SIS not in connector framework) | Platform team — scope a connector build as a Change Order |
| FERPA/legal interpretation question | Do not give FERPA legal opinions — direct to customer's FERPA officer and legal counsel |
| Platform bug or test failure | Open an issue in the repo; check `runbooks/` for known failure patterns |
| Customer wants a case study or reference | Loop in the account team and PDM — reference development requires customer consent and AWS co-sell approval |

---

## 7. The 3 Things That Kill EDU AI Deals (and How to Pre-empt Them)

**1. The security/privacy review kills momentum after the demo.**
*Why it happens:* the demo is convincing, the business sponsor is excited, but the CISO and FERPA officer weren't in the room — and when the security questionnaire lands, it sits for weeks.
*How to pre-empt:* put the CISO and privacy officer in the POC stakeholder workshop from day one. Show them the deny, the PII mask, and the human gate live. Hand them the TPRM packet and the Shared Responsibility Matrix at the end of the session. Don't let the demo happen without them.

**2. "Can we skip the gateway and add it later?"**
*Why it happens:* the customer wants to see the agent quickly; the gateway feels like overhead; someone suggests just testing with direct API calls.
*How to pre-empt:* use `docs/WHY-THE-MCP-LAYER.md` §8 — "Retrofitting governance is the most expensive thing in the program." Show the cost math: build the gateway once in Phase 1 and all eight agents inherit it vs. bolt it on eight times. And remind them: the gateway is the thing that passes the security and privacy review. Skip it and you can't go to production.

**3. The pilot scope expands before the gateway is proven.**
*Why it happens:* the institution gets excited mid-pilot and wants to add a second agent or a second system of record before Phase 1 is complete.
*How to pre-empt:* the SOW explicitly scopes one agent and one system of record. Change orders require the gateway Phase 1 exit gate to be passed first. Communicate this clearly at kickoff: "We expand the portfolio after the gateway is proven in production — that's the sequence that makes the second agent cheap."
