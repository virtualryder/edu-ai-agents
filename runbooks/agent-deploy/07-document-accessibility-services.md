# Agent 07 — Document & Accessibility Services — Deploy Runbook

> Per-agent runbook. The **shared secure request path** is in [`docs/AWS-DEPLOYMENT-REFERENCE.md`](../../docs/AWS-DEPLOYMENT-REFERENCE.md). Stand the platform up once per environment, then deploy Agent 07. This covers only Document & Accessibility specifics.

**Agent id:** `07-document-accessibility-services`
**Governance intensity: lower (best-first)** by visibility, but it writes to the SIS, so one consequential tool is HITL-gated. Clearest **MAP modernization** candidate (document-processing).

---

## 1. What it does + the bright line

Classifies and processes submitted documents: classify, extract fields, validate completeness, transform to accessible formats, and translate content. It writes extracted enrollment data back to the SIS and drafts family messages.

**Bright line — consequential, human-owned:** `sis.update_enrollment_record` (writing extracted data into the system of record) is HITL-gated. Extraction and accessibility transformation are safe; **committing to the SIS is the gate.** `comms.draft_message` is draft-only.

---

## 2. Agent creation

- **Runtime config:** `agent-service.yaml`, `AgentId=07-document`. Native path recommended — completeness validation is deterministic and belongs in a Lambda; the `waitForTaskToken` gate makes the SIS-write approval explicit.
- **Prompt registry:** the Document Services prompt (pinned).
- **Model + Guardrail:** Bedrock Claude under the env Guardrail. **Inbound documents are untrusted** — prompt-injection hidden in a submitted document is a real vector; authorization, the human gate, and audit live outside the model (Layer 3), so they hold regardless. See `governance/redteam/`.

---

## 3. Tools it needs

From `AGENT_TOOL_GRANTS["07-document-accessibility-services"]`:

| Tool | Connector | R/W | Consequential? |
|---|---|---|---|
| `docpipe.classify_document` | docpipe | analysis | no |
| `docpipe.extract_fields` | docpipe | analysis | no |
| `docpipe.validate_completeness` | docpipe | deterministic | no |
| `docpipe.transform_accessible` | docpipe | transform | no |
| `docpipe.translate_content` | docpipe | transform | no |
| **`sis.update_enrollment_record`** | SIS | write | **YES — HITL** |
| `comms.draft_message` | comms | draft | no |

- **Connectors / ingestion:** the document pipeline is backed by **Amazon Textract** (extraction/classification of PDFs/handwriting), **Amazon Translate** (`translate_content`), and **Amazon Polly** (accessible audio); SIS for the write; comms for drafts. **Secrets Manager:** `edu-agents/<env>/{docpipe,sis,comms}` (Textract/Translate/Polly are AWS service calls under the agent role, not external secrets).
- **Gateway targets:** `sis` ships (its `WriteTools`/`ConsequentialTools` already include `sis.write_extracted_document`); **add a `docpipe` target spec** and ensure `sis.update_enrollment_record` is gated.

---

## 4. Per-agent infra parameters

- **Textract / Translate + accessible-output S3:** Agent 07 needs **Amazon Textract** and **Amazon Translate/Polly** (grant the agent role the scoped service permissions — **not in the shipped least-privilege role; add them**) and an **accessible-output S3 bucket** for transformed artifacts. Finalized accessible versions of consequential material and submitted enrollment documents land in the **S3 Object Lock (WORM)** store.
- **CMK / data domains:** shared env CMK; audit + HITL; **WORM is heavily used here** (submitted documents + finalized accessible outputs) — confirm Object Lock retention against the records-retention schedule.
- **WCAG 2.2 AA:** transformed accessible outputs are subject to ADA / Section 508 — conformance-test them.
- **Roles that approve:** REGISTRAR / ENROLLMENT_STAFF approve `sis.update_enrollment_record` (the entitled roles for that write).

---

## 5. Step-by-step deploy

1. Build artifact (`scripts/local_smoke.sh 07-document-accessibility-services`); native:
   ```bash
   scripts/package_lambdas.sh --agent 07-document-accessibility-services --bucket <lambda-bucket> --agent-id 07-document --region <region>
   ```
2. Create connector secrets (`docpipe`, `sis`, `comms`); add Textract/Translate/Polly permissions to the agent role; provision the accessible-output S3 bucket (CMK-encrypted).
3. Register/extend gateway targets: `sis` (+ `docpipe`); gate `sis.update_enrollment_record`.
4. Deploy:
   ```bash
   scripts/deploy.sh --env prod --agent-id 07-document --mode native \
     --template-bucket <cfn-bucket> --lambda-bucket <lambda-bucket> \
     --idp-metadata https://<idp-host>/.../saml/metadata --region <region>
   ```

---

## 6. Smoke test (Document-specific)

- **Allowed analysis:** ENROLLMENT_STAFF classifies and extracts a submitted document → `docpipe.classify_document` / `docpipe.extract_fields` → ALLOW + audit.
- **Denied over-reach:** a role without enrollment-write entitlement attempts `sis.update_enrollment_record` → DENY.
- **Consequential blocked:** agent proposes writing extracted enrollment data to the SIS → `sis.update_enrollment_record` → PENDING_APPROVAL; committed only after a REGISTRAR/ENROLLMENT_STAFF approves, with the document snapshot in WORM.
- **Injection check:** feed a document containing an injected instruction; confirm it cannot exceed the human-in-the-loop's permissions and is audited.

---

## 7. Teardown notes

Standard reverse-order teardown (master §13). Drain pending SIS-write approvals. **WORM documents (submitted + accessible outputs) are immutable until retention expires.** De-provision the accessible-output bucket and Textract/Translate usage. Audit/HITL + CMK are `Retain`.
