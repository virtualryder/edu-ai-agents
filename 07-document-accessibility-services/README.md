# Document & Accessibility Services
### Agent 07 — the enrollment document engine and the suite's accessibility transformation agent, in one bounded agent

> **Best-first deployment for enrollment.** Document Services turns a seasonal, document-heavy, error-prone intake process into a governed pipeline — and transforms approved content into accessible, multilingual formats — while the admissions and enrollment decisions stay with the humans who are accountable for them.

---

## What it does

Agent 07 consolidates two coordinated capabilities that share one intake substrate, one audit trail, and one governance spine.

**(A) Enrollment / document processing.** The agent ingests the documents that enrollment runs on — registration forms, transcripts, transfer records, residency documents, immunization records, income verification, applications, recommendation letters, and prior-learning records. For each, it **classifies** the document type, **extracts** the fields the downstream system needs, **validates** completeness against the institution's checklist, **identifies** discrepancies (a name that does not match the application, a missing signature, an expired immunization), **requests** missing items from the family, and **prepares** a structured update for the authoritative SIS. It does not commit the admissions or enrollment decision — it prepares the file so a registrar or admissions officer can decide faster, with the evidence assembled and the gaps named.

**(B) Accessibility & multilingual transformation.** The agent transforms **already-approved** content into the formats students and families actually need: multiple languages, plain-language and reading-level variants, captions and transcripts, audio, image descriptions and alt text, accessible document formats, family communications in a preferred language, and vocabulary/comprehension support. Human verification is **required** before any consequential material — individualized plans, legal notices, safety information — is released.

The two capabilities are deliberately bounded. The document pipeline reads and prepares; it never decides admissions. The accessibility workflow transforms approved source content; it never originates policy or alters the meaning of a legal notice. Both are **decision-support**: they retrieve, extract, validate, draft, and route exceptions to a named human.

---

## What it solves

Enrollment is the most document-intensive, most seasonal, and most deadline-sensitive process an institution runs. A district fielding kindergarten registration, a community college processing transfer transcripts, and a university evaluating international credentials all face the same bottleneck — manual classification, keying, and completeness-checking of paper and PDF, performed by a small staff against a hard calendar. The cost shows up as long processing cycles, application abandonment when families cannot tell what is missing, and a credential-evaluation backlog that delays a student's first day.

In parallel, every institution must serve students and families across languages, disabilities, and reading levels — an ADA, Section 504, Section 508, and WCAG 2.2 AA obligation, not a nice-to-have. Remediating a single PDF for accessibility or translating a family notice into five languages is slow manual work that competes for the same scarce staff time as enrollment.

Agent 07 attacks both. It compresses the document cycle by classifying and extracting at machine speed while routing anything uncertain or high-sensitivity to a human, and it makes accessible, multilingual content a standing capability rather than a per-request scramble.

---

## Where it sits in the rollout & why

Agent 07 is in the **best-first** deployment tier alongside Agents 01, 03, and 08 — broad visibility, comparatively low decision-risk, mature workflows, and measurable cycle-time return. Within that tier it is positioned as the **best-first deployment for enrollment** specifically: the work is high-volume and well-bounded, the bright line is clean (the agent prepares, the human decides), and the return — processing cycle time, cost per application, manual touches per document — is directly measurable against a pre-deployment baseline.

The single best entry point for the whole suite remains **Agent 01 (Concierge)**, which is the most visible to the most users. Agent 07 is the strongest *enrollment* land: a delivery team that opens with the Concierge and adds Document Services covers the two highest-traffic, lowest-decision-risk surfaces an institution has — and both inherit the same governed MCP authorization gateway, so the second agent costs far less than the first. See `../README.md` and `../SOLUTION-FIELD-GUIDE.md` for the full "land with 01, expand to the portfolio" motion.

---

## AWS implementation

Agent 07 runs on the shared six-layer architecture (`../docs/SUITE-ARCHITECTURE.md`). Documents arrive in a secure **S3** intake bucket. **Amazon Textract** and **Amazon Bedrock Data Automation** perform classification and field extraction. **AWS Lambda** runs deterministic completeness and discrepancy validation. Two distinct **AWS Step Functions** state machines orchestrate the work — a document-processing pipeline and a separate accessibility-review workflow — with **Amazon DynamoDB** holding case state and a human-review interface surfacing uncertain fields. **Amazon API Gateway** tools execute approved SIS/CRM updates; **Amazon EventBridge** drives missing-information notifications. The original submission **and** the extracted version are retained immutably in **S3 + Object Lock (COMPLIANCE mode)**. Accessibility transformation draws on **Amazon Translate**, **Amazon Polly** (text-to-speech), and **Amazon Transcribe** (captions). All inference runs in-account on **Amazon Bedrock (Claude models)** behind **Bedrock Guardrails**; **KMS** encrypts at rest, and **CloudWatch** and **CloudTrail** feed the unified audit record.

**Confidence thresholds are set by field sensitivity.** A low-confidence extraction *or* a high-sensitivity field (legal name, date of birth, immunization status, residency basis) routes to human review regardless of the model's confidence score. Routine, low-sensitivity fields above threshold proceed; everything else stops at a person.

The agent can be deployed either way the canon describes: as an **AgentCore Runtime** container lift (ARM64, `/invocations`, `/ping`) or as the **Strands + Step Functions** native rebuild, where deterministic validation runs as Lambda and the HITL gate is a Step Functions `waitForTaskToken`. See `docs/aws-deployment-guide.md`.

### Narrowly-scoped tools — READ vs WRITE

No tool grants the agent broad database access. Each tool has a single purpose; read and write are separate tools with separate grants; every call passes through the MCP authorization gateway (`../platform_core/edu_agent_platform/mcp_gateway/`). WRITE tools that touch consequential material are HITL-gated.

| Tool | R/W | Purpose | Gate |
|---|---|---|---|
| `document.classify` | READ | Identify document type from an S3 intake object | None (analysis only) |
| `document.extract_fields` | READ | Extract named fields via Textract / Bedrock Data Automation | None; low-confidence routes to review |
| `sis.get_application_status` | READ | Read the authoritative application/enrollment state | Identity-scoped |
| `sis.get_required_documents` | READ | Read the institution's completeness checklist for a case | Identity-scoped |
| `kb.get_approved_content` | READ | Retrieve approved source content for transformation | Identity-scoped |
| `translate.render_language` | READ | Produce a translated variant of approved content | Human verify for consequential material |
| `accessibility.render_variant` | READ | Produce plain-language / reading-level / alt-text / audio / caption variants | Human verify for consequential material |
| `sis.prepare_record_update` | WRITE (staged) | Stage extracted fields as a proposed SIS update — not committed | HITL gate |
| `sis.commit_record_update` | WRITE | Write approved fields into the SIS system of record | HITL gate (registrar/admin) |
| `crm.update_case` | WRITE | Update CRM case/communication state | HITL gate for consequential changes |
| `comms.send_missing_info_request` | WRITE | Send a family request for a missing/expired document | Identity-scoped; templated |

---

## Systems of record / connectors

The SIS/CRM remains the system of record; the agent prepares and, on approval, writes — it never holds standing credentials and never becomes the authoritative store. Connectors live in `../platform_core/edu_agent_platform/connectors/`.

| Category | Examples | Agent 07 use |
|---|---|---|
| SIS | PowerSchool, Infinite Campus, Banner, Workday Student | Read application status / required-document checklist; staged then committed record updates (WRITE, HITL) |
| CRM | Slate, Salesforce EDU | Read and update enrollment case and family-communication state |
| Document store | S3 secure intake + S3 Object Lock WORM | Original submission and extracted version, immutable |
| Knowledge bases | Bedrock Knowledge Bases (approved policy/catalog/notices) | Approved source content for accessibility/multilingual transformation |
| Media services | Textract, Bedrock Data Automation, Translate, Polly, Transcribe | Classification, extraction, translation, audio, captions |

See `docs/integration-guide.md` for identity/role mapping and the gateway flow.

---

## Phased adoption

| Phase | Scope | Maturity target |
|---|---|---|
| **1 — Document discovery** | Classify and extract on a single high-volume document type (e.g., transcripts or registration forms) in `EXTRACT_MODE=demo`; baseline cycle time, touches per document, extraction accuracy | Demonstrated |
| **2 — Governed pipeline pilot** | Live Textract / Bedrock Data Automation + staged SIS updates behind the HITL gate; S3 Object Lock retention live; confidence thresholds tuned by field sensitivity | Deployable |
| **3 — Accessibility workflow** | Stand up the separate accessibility-review state machine — translation, plain-language, captions, audio, alt text — with human verification for consequential material | Deployable |
| **4 — Production enrollment season** | Full SIS/CRM connector validation, WCAG 2.2 AA conformance on family-facing surfaces, privacy review, records-retention configuration accepted by the institution | Production-ready |

---

## Regulations that apply

Document processing handles education records and, in K–12, the data of minors; accessibility transformation is the suite's named ADA/508 surface. The full control design is in `../governance/README.md`; the agent-specific reading is in `docs/edu-compliance.md`.

| Regulation | Why it applies here |
|---|---|
| **FERPA** | Every extracted field, application record, and family message is an education record; identity-scoped retrieval and disclosure recordkeeping apply |
| **COPPA** | K–12 intake collects information on children under 13; heightened masking, data minimization, and educational-purpose limits apply |
| **ADA / Section 504 / Section 508** | The agent's accessibility transformation must produce conformant output; family-facing surfaces must be usable by people with disabilities |
| **WCAG 2.2 AA** | The conformance standard for all student- and family-facing output and surfaces |
| **Immunization / residency record rules** | High-sensitivity validation fields with state-specific requirements; routed to human review |
| **Records retention** | S3 Object Lock (COMPLIANCE mode) supports immutable retention of original + extracted version on the institution's schedule |
| **State student-privacy laws** | Data-residency, retention, consent, and breach-notification parameters are configuration, mapped during assessment |

**The bright line:** Agent 07 **never decides admissions or enrollment**. It classifies, extracts, validates, identifies discrepancies, requests missing items, and prepares the file — a human owns the decision.

---

## ROI — what to measure

Baseline before deployment, then measure. The categories map to the governance ROI model (`../governance/README.md`, §4) — primarily **Labor**, **Service**, **Student journey**, and **Risk & quality**.

| Category | Example measures for Agent 07 |
|---|---|
| **Labor** | Manual touches per document; staff hours per application/registration; seasonal/overtime staffing load; time/cost per remediated document |
| **Service** | Processing cycle time; translation turnaround; time to enrollment decision; reduced accommodation delays |
| **Student journey** | Application/registration completion rate; application abandonment rate; family engagement by preferred language |
| **Risk & quality** | Extraction accuracy; discrepancy-catch rate; % of content meeting accessibility standards; privacy-incident and override rate |

Full baseline-then-measure model with an illustrative before/after table in `docs/roi-analysis.md`.

---

## Proof points

Verified, attributed carefully, not embellished.

- **Illinois Institute of Technology** used AWS AI/ML to automate transcript-processing steps — including record updates and international grade conversion — cutting credential-evaluation turnaround from **4–6 weeks to about 1 day**.
- **AWS has documented education initiatives using Amazon Bedrock for multilingual reading activities**; students at **Ohio State** and **Arizona State** developed an automated PDF-remediation approach for web accessibility.

These illustrate the two capabilities Agent 07 consolidates — document/credential automation and accessibility transformation — and the direction of return. They are reference points, not a performance guarantee for any specific deployment.

---

Maturity: **Demonstrated locally — not AWS-deployed.** Architecture and the classify/extract/transform pattern are written and reviewed, and the agent runs end-to-end locally in demo mode (`EXTRACT_MODE=demo`, deterministic fixtures, no API key) with a passing `tests/` suite (connectors run in **fixture** mode). The accessibility work ships a deterministic WCAG pre-flight (`governance/accessibility/`); formal WCAG 2.x conformance testing (axe-core + screen-reader + PDF/UA) is still customer-owned — along with a clean-account AWS deploy, real-model invocation, production IdP, and real document-source connectors. Status is governed by [`../docs/STATUS-MANIFEST.md`](../docs/STATUS-MANIFEST.md); see also `../README.md`.
