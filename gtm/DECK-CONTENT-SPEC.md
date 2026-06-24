# EDU AI Agent Suite — Deck Content Spec

> **Verified June 2026.** The deck builder uses this as the per-agent source of truth. Every ROI figure cites an entry in `EDU-DECK-SOURCES.md` and is tagged `[gov/peer-reviewed]`, `[foundation/research]`, `[sector-press/estimate]`, or `[vendor]`. Outcomes are *documented results applied to a reference institution* — modeled to the customer's baseline, never guaranteed. Lead every slide with the strongest source class; flag vendor and estimate figures on-slide.
>
> **Shared platform (every agent inherits it):** CloudFront + WAF edge; Cognito / IAM Identity Center federation with role scoping (student / guardian / educator / counselor / administrator); MCP authorization gateway (managed AgentCore Gateway, AWS primitives, or self-built FastMCP) with deny-by-default + short-lived scoped tokens; Amazon Bedrock (Claude) + Guardrails in-VPC (student PII never egresses after masking); PII masker; HITL gate (AgentCore approval or Step Functions `waitForTaskToken`); S3 Object Lock + DynamoDB append-only audit. Agent-specific blocks are called out per agent below.

---

## 01 — Student & Family Services Concierge

- **PAIN:** Families can't find answers and staff drown in routine status inquiries — during the 2024-25 FAFSA cycle **~4M of 5.4M calls (≈3/4) to the federal call center went unanswered.** `[gov/peer-reviewed — GAO-24-107407, 2024]`
- **WHAT WE SOLVE FOR:**
  - Routine, repetitive status/eligibility/deadline questions that crowd out complex casework.
  - After-hours and multilingual demand a fixed staff can't cover.
  - Seasonal peaks (FAFSA, registration, move-in) that spike contact volume.
- **HOW WE SOLVE IT:** retrieve approved KB/policy + the student's own record via gateway-scoped connectors → analyze intent and entitlement → answer in the student's language or draft a reply → **HITL gate for any consequential action** (only reads/low-stakes status in public mode; staff approves account-touching actions) → append-only audit of every record access.
- **ROI:**
  - **75% reduction** in financial-aid status emails/calls/visits (Highline College). `[vendor — AWS]`
  - **Wait times >15 min → <30 sec** at similar staffing (UT Austin). `[vendor — AWS]`
  - Self-service contact cost **$1-$4 vs. $17-$25 phone**. `[sector-press/estimate]`
- **AWS BLOCKS:** CloudFront+WAF · Cognito · AgentCore Gateway · Bedrock+Guardrails · Amazon Connect / chat channel · SIS + financial-aid connectors · Amazon Translate (multilingual) · S3 Object Lock + DynamoDB audit.
- **TRAFFIC FLOW:** student request → CloudFront/WAF → Cognito → Gateway (scoped read) → Bedrock+Guardrails → answer/translate → (HITL if account action) → audit.
- **DEPLOY ONE-LINER:** CloudFormation quick-deploy provisions the isolated environment + gateway + Connect/chat channel; point connectors at SIS and financial-aid system; load approved KB.

## 02 — Personalized Tutor & Study Companion

- **PAIN:** Students need help at scale outside class hours, but human tutoring is expensive and access is uneven — high-impact tutoring runs **$1,200-$2,500+ per student/year.** `[foundation/research]`
- **WHAT WE SOLVE FOR:**
  - 24/7 on-demand help grounded in the course's own materials.
  - Equity of access for students who can't afford private tutoring.
  - Socratic, step-at-a-time guidance (no answer-dumping) that protects academic integrity.
- **HOW WE SOLVE IT:** retrieve approved course content/LMS materials → analyze the student's question and level → coach one step at a time via Guardrails-bounded prompts → escalate to a human (instructor/tutor) on distress or repeated struggle → audit interactions for integrity review.
- **ROI:**
  - AI tutor cohort learned **>2x as much in less time** vs. active-learning class (Harvard RCT). `[gov/peer-reviewed]`
  - Human-tutoring benchmark **~0.37 SD** gain establishes the value ceiling AI helps democratize. `[gov/peer-reviewed]`
  - Tech-substitution can cut tutoring cost **~one-third.** `[gov/peer-reviewed]`
- **AWS BLOCKS:** CloudFront+WAF · Cognito · AgentCore Gateway · Bedrock+Guardrails (integrity prompts) · LMS/content connector (Canvas etc.) · Bedrock Knowledge Base over course materials · AgentCore memory (retention-bounded) · S3 Object Lock + DynamoDB audit.
- **TRAFFIC FLOW:** student question → CloudFront/WAF → Cognito → Gateway → KB retrieve → Bedrock+Guardrails (Socratic) → response → (escalate if flagged) → audit.
- **DEPLOY ONE-LINER:** quick-deploy environment + gateway; connect LMS, index course materials into a Knowledge Base, set integrity guardrails and memory-retention boundaries.

## 03 — Educator Copilot (lesson / rubric / quiz drafting, differentiation)

- **PAIN:** Teachers work **~53 hrs/week (vs. 44 for comparable adults, 2024)** with only ~4.4 hrs of planning time — hours lost to prep, differentiation, and LMS navigation. `[gov/peer-reviewed — RAND]`
- **WHAT WE SOLVE FOR:**
  - First-draft lessons, rubrics, quizzes, and differentiated versions in minutes.
  - Standards-aligned, on-template output the educator edits and owns.
  - Reclaimed time that reduces burnout (turnover costs ~$11,860-$24,930 per teacher). `[foundation/research]`
- **HOW WE SOLVE IT:** retrieve standards + approved curriculum/templates → analyze the educator's intent (grade, standard, level) → draft lesson/rubric/quiz + differentiated variants → **educator reviews and approves** (HITL by design; nothing publishes unedited) → audit drafts and approvals.
- **ROI:**
  - Targets the **9-hr/week** above-peer workload (RAND). `[gov/peer-reviewed]`
  - Avoided turnover cost **~$11,860-$24,930/teacher** when burnout drops. `[foundation/research]`
  - Vanderbilt "Amplify" runs lesson-plan/template agents in production. `[vendor]`
- **AWS BLOCKS:** CloudFront+WAF · Cognito · AgentCore Gateway · Bedrock+Guardrails · standards/curriculum Knowledge Base · LMS connector · document templating (S3) · S3 Object Lock + DynamoDB audit.
- **TRAFFIC FLOW:** educator prompt → CloudFront/WAF → Cognito → Gateway → standards/template retrieve → Bedrock+Guardrails draft → educator HITL approve → audit.
- **DEPLOY ONE-LINER:** quick-deploy + gateway; index standards/curriculum/templates into a Knowledge Base; connect the LMS for publish-on-approval.

## 04 — Assessment, Grading & Feedback

- **PAIN:** Grading and feedback are slow and inconsistent — an estimated **~40% of teaching time** goes to grading, delaying the feedback students need. `[sector-press/estimate — flag on slide]`
- **WHAT WE SOLVE FOR:**
  - Faster feedback turnaround, especially in large/online sections.
  - Consistent rubric application with a draft score + rationale.
  - Instructor stays the grader of record — no autonomous grades.
- **HOW WE SOLVE IT:** retrieve the approved rubric + assignment context → analyze the submission against rubric criteria → draft score + targeted feedback → **instructor reviews/overrides every grade (HITL gate, mandatory)** → audit the draft, the override, and the final grade.
- **ROI:**
  - RCTs (4 courses, ~300 students, 2023-24): AI-assisted grading **comparable to human** with **faster turnaround.** `[gov/peer-reviewed]`
  - Benchmark Education reports accelerated grading + better feedback on AWS. `[vendor]`
  - Marking-speed uplift cited ~80% (vendor — supporting only). `[vendor — flag on slide]`
- **AWS BLOCKS:** CloudFront+WAF · Cognito · AgentCore Gateway · Bedrock+Guardrails · LMS/gradebook connector · rubric Knowledge Base · Step Functions `waitForTaskToken` HITL · S3 Object Lock + DynamoDB audit.
- **TRAFFIC FLOW:** submission → CloudFront/WAF → Cognito → Gateway → rubric retrieve → Bedrock+Guardrails draft score → instructor HITL approve/override → gradebook write → audit.
- **DEPLOY ONE-LINER:** quick-deploy + gateway; connect LMS gradebook, load rubrics, enable the mandatory instructor-approval gate before any grade write-back.

## 05 — Student Success & Proactive Engagement

- **PAIN:** Warning signs accumulate before anyone acts — **22.4% of first-year students don't return for year two** (community colleges retain only ~55%). `[gov/peer-reviewed — NSC 2024]`
- **WHAT WE SOLVE FOR:**
  - Surfacing at-risk signals early, across SIS/LMS, instead of after withdrawal.
  - Drafting personalized, timely nudges advisors approve and send.
  - Protecting recurring tuition revenue and recruitment investment per retained student.
- **HOW WE SOLVE IT:** retrieve risk signals (attendance, grades, engagement) via scoped connectors → analyze against an approved risk model → recommend an outreach + draft the nudge → **advisor approves the intervention (HITL; consequential by nature)** → audit who was flagged, contacted, and why.
- **ROI:**
  - Targets the **22.4% non-return** rate (NSC). `[gov/peer-reviewed]`
  - Each retained full-timer preserves a year of tuition (~$340-$642/credit hr) + ~$457-$2,433 recruitment cost. `[gov]` `[foundation/research]`
  - Instructor-initiated early alerts associated with **lower withdrawal, higher grades** (CCRC + peer-reviewed). `[gov/peer-reviewed]`
- **AWS BLOCKS:** CloudFront+WAF · Cognito · AgentCore Gateway · Bedrock+Guardrails · SIS + LMS connectors · risk-model / analytics (Bedrock or SageMaker) · EventBridge triggers · Step Functions `waitForTaskToken` HITL · S3 Object Lock + DynamoDB audit.
- **TRAFFIC FLOW:** signal event → EventBridge → Gateway (scoped read) → risk analysis → Bedrock+Guardrails draft nudge → advisor HITL approve → outreach + audit.
- **DEPLOY ONE-LINER:** quick-deploy + gateway; connect SIS/LMS, configure the approved risk model and advisor-approval gate, wire EventBridge triggers.

## 06 — Academic / College / Career Pathway Navigator

- **PAIN:** Degree/transfer rules are complex and advisors are overloaded — transferring students lose **~43% of credits on average**, lengthening time-to-degree and inflating cost. `[gov/peer-reviewed — GAO; flag year]`
- **WHAT WE SOLVE FOR:**
  - Plain-language degree audits and transfer-credit mapping.
  - Keeping students on a guided pathway (right courses, no excess credits).
  - Relieving advisor caseloads (~441 students/advisor at 2-yr institutions). `[foundation/research]`
- **HOW WE SOLVE IT:** retrieve degree requirements + the student's transcript/transfer record → analyze against catalog/articulation rules → recommend next-best courses + flag credit gaps → **advisor verifies before plan is finalized (HITL for consequential planning)** → audit the audit.
- **ROI:**
  - Reducing the **~43% credit loss** shortens time/cost to degree (GAO). `[gov/peer-reviewed]`
  - Guided-pathways scaling lifted early-momentum credit milestones (CCRC/AACC). `[foundation/research]`
  - Illinois Tech cut credential evaluation **4-6 weeks → 1 day** on AWS. `[vendor]`
- **AWS BLOCKS:** CloudFront+WAF · Cognito · AgentCore Gateway · Bedrock+Guardrails · SIS / degree-audit + articulation connectors · catalog/articulation Knowledge Base · Step Functions `waitForTaskToken` HITL · S3 Object Lock + DynamoDB audit.
- **TRAFFIC FLOW:** student/advisor request → CloudFront/WAF → Cognito → Gateway → transcript + rules retrieve → Bedrock+Guardrails plan → advisor HITL verify → audit.
- **DEPLOY ONE-LINER:** quick-deploy + gateway; connect SIS/degree-audit, index catalog and articulation rules, enable advisor verification gate.

## 07 — Document & Accessibility Services

- **PAIN:** Enrollment is document-heavy and accessibility is now legally enforced — **ADA Title II (WCAG 2.1 AA) deadlines hit April 26 2027 (≥50k pop.) / 2028 (smaller)**, and **~95% of accessibility complaints involve PDFs.** `[gov/peer-reviewed + sector-press]`
- **WHAT WE SOLVE FOR:**
  - High-volume, seasonal document intake (transcripts, aid docs) with error/turnaround pressure.
  - Remediating inaccessible PDFs/content to WCAG 2.1 AA at scale.
  - Multilingual document handling.
- **HOW WE SOLVE IT:** ingest + **Textract** extract → analyze/classify and detect accessibility gaps → draft remediated/structured output (+ **Translate** for multilingual) → **staff reviews consequential records and accessibility sign-off (HITL)** → audit every document touched.
- **ROI:**
  - Transcript/credential eval **4-6 weeks → 1 day** (Illinois Tech). `[vendor]`
  - Automated PDF remediation for the ADA deadline (Ohio State, open-sourced). `[vendor]`
  - Directly addresses the **2027/2028 WCAG 2.1 AA deadlines** and PDF-dominated complaint risk. `[gov/peer-reviewed + sector-press]`
- **AWS BLOCKS:** CloudFront+WAF · Cognito · AgentCore Gateway · **Amazon Textract** · **Amazon Translate** · Bedrock+Guardrails · intelligent-document-processing pipeline · SIS/CRM connector · S3 Object Lock + DynamoDB audit.
- **TRAFFIC FLOW:** document in → S3 → Textract extract → Bedrock+Guardrails classify/remediate → (Translate) → staff HITL sign-off → record write + audit.
- **DEPLOY ONE-LINER:** quick-deploy + gateway; wire the Textract/IDP pipeline, connect SIS/CRM, enable Translate and the staff accessibility-approval gate.

## 08 — Operations / IT Service Desk

- **PAIN:** IT/admin staff drown in repetitive tickets — education cost per ticket is **~$6-$12**, and password resets alone cost **~$70 each** in labor. `[sector-press/estimate]`
- **WHAT WE SOLVE FOR:**
  - High-volume, self-resolvable tickets (password/access, how-to, status).
  - Deflection to self-service so small IT teams focus on real incidents.
  - Knowledge-grounded answers from approved runbooks/KB.
- **HOW WE SOLVE IT:** retrieve approved IT KB/runbooks → analyze the ticket intent → resolve self-service or draft the response/automated action → **HITL gate for privileged/consequential actions** (low-risk resets auto, account changes escalate) → audit every action.
- **ROI:**
  - Self-service resolves at **$1-$4 vs. $17-$25 phone**; AI deflects **45%+** of queries. `[sector-press/estimate]`
  - Password-reset automation targets the **~$70/reset** labor cost. `[sector-press/estimate]`
  - K-12's small IT teams gain the most from deflection. `[vendor — flag on slide]`
- **AWS BLOCKS:** CloudFront+WAF · Cognito · AgentCore Gateway · Bedrock+Guardrails · ITSM connector (ticketing) · IAM/identity-provider connector (resets) · runbook Knowledge Base · S3 Object Lock + DynamoDB audit.
- **TRAFFIC FLOW:** ticket/chat → CloudFront/WAF → Cognito → Gateway → KB retrieve → Bedrock+Guardrails resolve/draft → (HITL if privileged) → action + audit.
- **DEPLOY ONE-LINER:** quick-deploy + gateway; connect the ITSM tool and identity provider, index runbooks, set which actions auto-resolve vs. require approval.

---

### Cross-agent notes for the builder
- **Land-with-01 motion holds:** Concierge (01), Service Desk (08), and Document/Accessibility (07) are best-first (visible, low decision-risk, measurable). Tutor (02), Assessment (04), Success (05), and Pathway (06) are higher-governance — sequence them after the control plane is proven.
- **HITL is non-negotiable on consequential agents (04, 05, 06)** and on any account-touching action in 01/07/08 — always show the human gate on the flow slide.
- **Suite-wide adoption slide:** open with EDUCAUSE (57% strategic priority) + Tyton (59% students / 36% instructors never) + RAND K-12 (48% districts training); these set the "everyone is moving, few are governed" frame the platform answers.
