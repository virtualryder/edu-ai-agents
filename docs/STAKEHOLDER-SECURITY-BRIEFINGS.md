# Stakeholder Security & Value Briefings
### One Conversation per Decision-Maker — What They Care About, and What to Say

> Putting governed AI agents into an education institution is a multi-stakeholder sale. Each decision-maker holds a different veto and hears a different message: the CISO cares about the attack surface; the privacy officer cares about FERPA; the registrar cares about who can touch a record; the board cares about reputation and prudence. This guide gives a focused security-and-value briefing for each — written so you can walk into the meeting and lead with what that person actually weighs. Every briefing ties back to the same real controls (the MCP authorization gateway, deny-by-default, the enforced HITL gate, PII masking, the append-only audit, WCAG 2.2 AA, the bright line) so the story is consistent across the table.

Use alongside `SOLUTION-FIELD-GUIDE.md` (qualification and motion) and `OBJECTION-HANDLING.md` (the sharp pushbacks each of these stakeholders may raise).

---

## Superintendent / College or University President
**What they weigh:** institutional reputation, mission and student outcomes, prudent stewardship, avoiding a privacy headline.

This is an outcome-and-trust story, not a technology story. The institution already owns the systems that hold the answers; the pain is that families and staff can't reach them without knowing which office to call. Governed AI agents close that gap — improving service, reclaiming staff time, and supporting persistence and completion — while the platform's design guarantees the institution never cedes a consequential decision to a machine. These are **bounded agents**: they retrieve, draft, and route, and a qualified human owns every grade, admission, disciplinary, financial-aid, eligibility, or placement decision. The reputational protection is concrete: every access to a student record is identity-scoped, human-gated where it matters, and recorded in a tamper-evident audit trail aligned to FERPA. The prudent path is to land one visible, low-risk agent (the Concierge), measure the outcome — peers have seen 75% reductions in routine financial-aid contacts and 250%+ engagement lifts — and expand deliberately on a platform built to be governed from the first commit.

## CIO
**What they weigh:** architecture, integration burden, total cost, vendor lock-in, operational sustainability.

The reframe for you: the hard part of "deploy AI agents" isn't the model — it's giving agents **clean, governed API access to your systems of record**, and that capability is an asset you keep. Exposing narrowly-scoped tools over the SIS/LMS/ERP/CRM/ITSM is, in effect, API modernization the agent program funds. One authorization-and-audit layer — the MCP gateway — is built once and reused by all eight agents, so the marginal cost of each additional agent drops sharply; you do not pay the integration tax eight times. On lock-in: the enforcement logic is readable, testable Python in `platform_core/`, and you have three hosting options (managed AgentCore Gateway, AWS primitives, or a self-built FastMCP server you own) with identical controls — you choose the operating model. Inference runs on Bedrock reached over AWS PrivateLink (an interface VPC endpoint) rather than the public internet; your systems stay the source of truth. Deployment is CloudFormation-first with Terraform parity, into a customer-isolated environment.

## CISO
**What they weigh:** attack surface, credential management, least privilege, auditability, blast radius, incident containment.

The design directly targets the things that keep you up. There are **no standing service accounts** — every tool call uses a short-lived, single-purpose scoped token, so there is no broad credential sitting in an agent for an attacker to harvest. Authorization is **deny-by-default with least-privilege role intersection**: the agent can never exceed the human it acts for, which closes the "agent reads any student's record" class of failure. Consequential actions are **gated to a named human** by the framework — not by trusting the model — so a prompt injection (including one hidden in a student-submitted document or inbound email) cannot drive an unapproved write, because authorization, the gate, and audit live *outside* the model. Blast radius is contained: you can disable any agent or any tool immediately. Everything is logged to a PII-masked, append-only trail (DynamoDB with PITR; S3 Object Lock WORM), and KMS customer-managed keys, VPC isolation, and Bedrock Guardrails round out the posture. You can read exactly how the controls behave in `platform_core/` before you ever provision anything.

## Chief Privacy Officer / FERPA Officer
**What they weigh:** FERPA, COPPA, PPRA, disclosure recordkeeping, the school-official/direct-control exception, age-of-majority, guardian rights.

This platform treats your statute stack as the spine, not an afterthought. **FERPA:** identity-scoped retrieval is the technical enforcement of FERPA's access limits — an authenticated student's agent reaches that student's record and no other; the append-only audit satisfies disclosure recordkeeping; and the "school official / direct control" exception is honored concretely because the gateway enforces purpose-of-use per tool, the agent holds no standing credentials, and you can disable it instantly. **Age-of-majority:** rights transfer at 18 / postsecondary enrollment is carried in IdP claims and scoped at the gateway, so a guardian agent cannot surface records the guardian no longer has a right to. **COPPA:** an under-13 flag drives heightened Guardrails, data minimization, and a hard prohibition on non-educational use or behavioral profiling. **PPRA:** outreach and student-success agents do not collect or infer protected categories. The control design is parameterized for your state's student-privacy law (residency, retention, consent, prohibited use are configuration). Full mapping: `governance/README.md`.

## Chief Academic Officer / Provost
**What they weigh:** academic integrity, instructional quality, faculty trust, the bright line around consequential academic decisions.

The academic guardrails are explicit. The agent **never** decides a grade, an admission, special-education eligibility, or a placement — those sit on a bright line, gated to the qualified human who owns them, and tested in the codebase. Instructional agents augment faculty: the Educator Copilot drafts and differentiates but always routes to educator approval before publish; Assessment produces rubric-grounded draft feedback and routes low-confidence work to the instructor, who owns the grade; the Tutor is curriculum-grounded, instructor-controlled, and Socratic — help the faculty member can see and shape, not answer-vending (the UT Austin UT Sage model of a faculty-guided tutor). Output quality is engineered: grounding verification ties every fact, deadline, and policy to approved institutional content and fails fast on anything ungrounded, and an eval harness guards against drift. Faculty governance gets a metric, not a promise — including fairness monitoring where student outcomes are involved.

## Registrar / Enrollment
**What they weigh:** record integrity, who can touch a record, FERPA access limits, the seasonal enrollment crush.

Two messages. First, record integrity: the SIS remains the system of record; agents read and write only through narrowly-scoped, separately-granted tools (read and write are distinct grants), an authorized human approves any consequential write, and every access is audited with lineage back to the record — so you can always answer "who touched this, on what basis, and who approved it." Access is identity-scoped, which is the technical enforcement of the FERPA limits you already police. Second, capacity: the document-and-enrollment workflow is exactly where measurable relief shows up — Illinois Tech took transcript evaluation from 4–6 weeks to about a day, and Agent 07 classifies, extracts, and validates enrollment documents (with a human deciding) while producing accessible, multilingual versions for families. The agent absorbs the seasonal, repetitive load; your team keeps the judgment and the final say.

## Financial Aid Director
**What they weigh:** award-decision integrity, compliance, the volume of routine status inquiries, equitable access for families.

The bright line protects you where it matters most: the agent **checks and explains** financial-aid status, but **never decides eligibility or an award** — that stays with your office. What it removes is the routine-inquiry deluge that buries your team during peak. This is the single most proven workflow in the field: Highline College cut financial-aid status emails, calls, and visits by ~75% and roughly halved FAFSA processing time with governed self-service. Families get accurate, grounded answers (tied to your approved content, not an invented deadline) around the clock and in their language, while your staff redirect to the complex cases that need a human. Equity improves because after-hours and multilingual self-service reaches families who can't call during business hours — and every interaction is governed and audited.

## Special Education / Disability Services Director
**What they weigh:** the sensitivity of IEP/504 records, eligibility and placement integrity, IDEA/Section 504 obligations.

IEP and 504 records are treated as heightened-sensitivity throughout: the PII masker handles disability data with extra care, and IEP/504 content is access-gated to the student's authorized team only. Critically, **eligibility and placement are on the bright line the agent never decides** — the agent may retrieve an approved plan for an authorized educator or draft proposed accommodations, but a qualified human and the IEP/504 team own every determination. The agent reduces the administrative burden around the work (assembling material, drafting, reformatting) without ever touching the decision. And accessibility is a first-class capability: Agent 07 produces accessible formats with human verification required on consequential, individualized material — so the tooling supports your students' access needs rather than creating new ones.

## Accessibility Coordinator
**What they weigh:** ADA/Section 508, WCAG conformance, VPAT, content accessibility at scale, Title VI language access.

Accessibility is built in and gated, not bolted on. Every student-facing surface is built and tested to **WCAG 2.2 AA**, and conformance is a production-readiness gate — re-tested under the managed service as surfaces change, with documentation suitable for a VPAT. Beyond compliance, the platform actively *produces* accessibility: Agent 07 generates alt text, captions, transcripts, plain-language and reading-level variants, multilingual content, and audio — with human verification required on consequential material such as individualized plans and legal notices. That turns accessibility from a perpetual remediation backlog into a scalable capability, while keeping a human in the loop where the stakes demand it. Title VI language access is supported through the same multilingual pipeline.

## IT Service Desk Lead
**What they weigh:** ticket volume, mean time to resolution, after-hours coverage, staff burnout on repetitive work.

This is a direct relief story for your team. The Operations Service Desk agent handles the repetitive tickets and policy questions — password and access basics, "how do I…" knowledge lookups, routine administrative workflows — deflecting volume and shortening mean-time-to-resolution, with after-hours self-service that doesn't require staffing the off-hours. It operates under the same governance as every other agent: scoped tools, human approval on consequential actions, segregation of duties for staff handling student data, and a full audit trail. Your staff move from triaging the repetitive to solving the hard, and the agent never takes an irreversible action without a named human signing off. Measured on deflection and resolution time — not ticket chatter.

## Counseling / Advising Lead
**What they weigh:** caseload capacity, timely intervention, student outcomes, the human relationship at the center of advising.

The design keeps you at the center and gives you reach. The Student Success agent assembles the evidence (attendance, missing work, engagement signals — never PPRA-protected inferences), drafts interventions, and can run approved, event-driven outreach — but the **counselor decides every intervention**, and the agent never makes a consequential call about a student. The Pathway Navigator handles the complexity of degree, graduation, and transfer rules so your advisors spend their time on the conversation, not the rulebook — with placement remaining a human decision. The result is timely outreach at a scale your caseload can't reach manually, fairness monitored as a metric (false-positive/false-negative parity across cohorts) so targeting doesn't quietly become inequitable, and your professional judgment owning the relationship and the decisions.

## Procurement
**What they weigh:** vendor risk, contract terms, subprocessors, data usage, total cost, exit options.

You will get direct answers to your TPRM questionnaire — there is a packet built for exactly your questions (`offerings/TPRM-DUE-DILIGENCE-PACKET.md`): data flows, PII handling, the subprocessor list, the explicit commitment that **customer/student data is not used to train models**, in-account hosting with configurable region, KMS encryption, deny-by-default access control, the append-only audit, WCAG 2.2 AA/VPAT posture, incident response, and the FERPA school-official/direct-control and COPPA specifics. On lock-in — your standard concern — there are three hosting options including a self-built server the institution owns outright, with identical controls, so exit is real. The commercial shape favors you: the expensive control plane is built once and reused, so expansion is incremental, and value is measured on outcomes you can verify (deflection, cycle time) rather than on usage. This is positioned honestly as a governed accelerator the institution operationalizes — not a black-box product.

## School Board / Board of Trustees
**What they weigh:** fiduciary prudence, community trust, student safety and privacy, reputational risk, value for public money.

The board-level message is one of governed prudence. The institution is not handing decisions to a machine: AI agents here are **bounded** — they help with routine work and route everything consequential to a qualified human, so no grade, admission, discipline, financial-aid award, eligibility, or placement is ever decided by software. Student privacy is protected by design — every access to a record is identity-scoped, human-gated where it matters, and recorded in a tamper-evident trail aligned to FERPA — and the institution can shut any agent off instantly. The approach is deliberately incremental: prove value and safety with one visible, low-risk service (the Concierge), measure the result against peers who have seen large, real reductions in routine workload and large gains in family engagement, and expand only as governance keeps pace. It is a defensible, transparent use of public resources that improves service to families and students while keeping humans accountable for every decision that matters.

---

## Using these briefings
- Lead with the stakeholder's own concern; the underlying controls are the same across all of them, which keeps your story consistent if these people compare notes.
- Pair each briefing with the matching objections in `OBJECTION-HANDLING.md` and, for the security/privacy/procurement audience, the evidence in `offerings/TPRM-DUE-DILIGENCE-PACKET.md`.
- For the buying motion and qualification, see `SOLUTION-FIELD-GUIDE.md`; for the deep controls, `governance/README.md` and `docs/WHY-THE-MCP-LAYER.md`.
