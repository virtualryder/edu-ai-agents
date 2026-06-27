# IAM & Least-Privilege Matrix — EDU AI Agent Suite

*Audience: customer CISO / security architecture review board. This is an auditable least-privilege matrix for the Agent 01 (Student & Family Concierge) golden path and the shared platform. **Part A** derives human-role → tool entitlements directly from `platform_core/edu_agent_platform/mcp_gateway/policy.py`. **Part B** maps AWS principals → permissions → resources → conditions from `infra/cloudformation/security.yaml` and siblings. Companion: [`THREAT-MODEL.md`](THREAT-MODEL.md). Honest gaps cross-reference [`docs/PRODUCTION-READINESS-ACTION-PLAN.md`](../PRODUCTION-READINESS-ACTION-PLAN.md).*

---

## How authorization actually resolves (the two-key model)

A tool call executes only if **both keys turn**:

```
permitted(tool) ⇔ tool ∈ AGENT_TOOL_GRANTS[agent]  ∩  ⋃ ROLE_ENTITLEMENTS[user_roles]
```

(`policy.decide`). The agent's grant list is its job description; the user's role entitlement is the human's real permission. **The intersection is what runs — an agent can never exceed the human on whose behalf it acts**, even if the agent's own grant list is broader. On top of that:

- **CONSEQUENTIAL** tools additionally require a signed, transaction-bound, single-use human approval at runtime (`policy.CONSEQUENTIAL_TOOLS`; `gateway.py` step 3; `approvals.py`).
- **RECORD_SCOPED** tools additionally enforce that a self-scoped principal (STUDENT, GUARDIAN) reaches only their own / linked student record (`policy.record_scope_ok`; `gateway.py` step 2b).

Part A is therefore the **ceiling** of what each human role can reach across all agents; the effective surface for a given agent is the intersection with that agent's grant (see §A.4 for Agent 01).

---

## Part A — Human roles → tool entitlements

Source of truth: `policy.ROLE_ENTITLEMENTS`, `policy.CONSEQUENTIAL_TOOLS`, `policy.RECORD_SCOPED_TOOLS`. Roles derive from IdP group membership (`auth.py` — e.g. `GRP-STUDENTS → STUDENT`). Legend: **C** = consequential (human-gated), **R** = record-scoped (own/linked only for self-scoped roles).

### A.1 Reference data (the canonical sets)

- **CONSEQUENTIAL_TOOLS (8):** `assessment.release_grade`, `comms.send_message`, `erp.initiate_approval`, `itsm.reset_password`, `itsm.restart_service`, `lms.publish_content`, `lms.update_assignment_due_date`, `sis.update_enrollment_record`.
- **RECORD_SCOPED_TOOLS (9):** `crm.get_case`, `sis.check_application_status`, `sis.get_attendance`, `sis.get_grades`, `sis.get_graduation_requirements`, `sis.get_schedule`, `sis.get_student_profile`, `sis.get_transfer_credits`, `sis.update_enrollment_record`.
- **Self-scoped roles** (constrained to own/linked record on record-scoped tools): `STUDENT`, `GUARDIAN`. All other roles operate at **institutional scope** by default (`policy._SELF_SCOPED_ROLES`).

### A.2 Entitlement matrix (per role)

| Role | # tools | Tools entitled (C = consequential, R = record-scoped) |
|---|---:|---|
| **STUDENT** | 20 | `sis.get_student_profile`R, `sis.get_schedule`R, `sis.check_application_status`R, `sis.get_grades`R, `sis.get_graduation_requirements`R, `sis.get_transfer_credits`R, `kb.search_policies`, `kb.search_course_material`, `lms.get_course_content`, `lms.get_assignments`, `crm.schedule_appointment`, `crm.create_advising_case`, `rules.run_degree_audit`, `rules.check_prerequisites`, `labor.get_career_pathways`, `docpipe.transform_accessible`, `docpipe.translate_content`, `itsm.get_ticket`, `itsm.create_ticket`, `comms.draft_message` |
| **GUARDIAN** *(scoped subset; **dropped entirely when `rights_transferred`**)* | 9 | `sis.get_student_profile`R, `sis.get_schedule`R, `sis.check_application_status`R, `sis.get_attendance`R, `kb.search_policies`, `crm.schedule_appointment`, `docpipe.translate_content`, `comms.draft_message`, `itsm.create_ticket` |
| **EDUCATOR** | 19 | `lms.get_roster`, `lms.get_course_content`, `lms.get_assignments`, `lms.get_engagement`, `lms.identify_missing_submissions`, `kb.search_course_material`, `lms.create_assignment_draft`, `lms.create_rubric_draft`, `lms.post_announcement_draft`, **`lms.update_assignment_due_date`C**, **`lms.publish_content`C**, `assessment.evaluate_rubric`, `assessment.draft_feedback`, `assessment.summarize_class_patterns`, **`assessment.release_grade`C**, `sis.get_grades`R, `sis.get_attendance`R, `analytics.get_risk_signals`, `comms.draft_message` |
| **COUNSELOR** | 16 | `analytics.get_risk_signals`, `analytics.get_intervention_history`, `sis.get_attendance`R, `sis.get_grades`R, `sis.get_student_profile`R, `sis.get_graduation_requirements`R, `sis.get_transfer_credits`R, `crm.create_advising_case`, `crm.schedule_appointment`, `crm.get_case`R, `comms.draft_message`, **`comms.send_message`C**, `rules.run_degree_audit`, `rules.check_prerequisites`, `labor.get_career_pathways`, `kb.search_policies` |
| **REGISTRAR** | 10 | `sis.get_student_profile`R, `sis.get_schedule`R, `sis.get_grades`R, `sis.get_graduation_requirements`R, `sis.get_transfer_credits`R, **`sis.update_enrollment_record`C,R**, `crm.get_case`R, `docpipe.classify_document`, `docpipe.extract_fields`, `docpipe.validate_completeness` |
| **FINANCIAL_AID** | 7 | `sis.check_application_status`R, `sis.get_student_profile`R, `crm.get_case`R, `crm.create_advising_case`, `comms.draft_message`, **`comms.send_message`C**, `kb.search_policies` |
| **ENROLLMENT_STAFF** | 8 | `docpipe.classify_document`, `docpipe.extract_fields`, `docpipe.validate_completeness`, `docpipe.transform_accessible`, `docpipe.translate_content`, **`sis.update_enrollment_record`C,R**, `comms.draft_message`, `kb.search_policies` |
| **ADMINISTRATOR** | 11 | `sis.get_student_profile`R, `sis.get_schedule`R, `sis.check_application_status`R, `analytics.get_risk_signals`, `analytics.get_intervention_history`, `crm.get_case`R, `crm.create_advising_case`, `comms.draft_message`, **`comms.send_message`C**, `kb.search_policies`, `erp.search_policy` |
| **IT_STAFF** | 4 | `itsm.get_ticket`, `itsm.create_ticket`, `itsm.run_diagnostic`, `kb.search_policies` |
| **IT_ADMIN** *(IT_STAFF + privileged remediation)* | 6 | `itsm.get_ticket`, `itsm.create_ticket`, `itsm.run_diagnostic`, **`itsm.reset_password`C**, **`itsm.restart_service`C**, `kb.search_policies` |
| **STAFF** | 4 | `erp.search_policy`, `erp.draft_document`, `kb.search_policies`, `itsm.create_ticket` |
| **STAFF_APPROVER** *(STAFF + financial/procurement approval authority)* | 5 | `erp.search_policy`, `erp.draft_document`, **`erp.initiate_approval`C**, `kb.search_policies`, `itsm.create_ticket` |

### A.3 What this design enforces (verifiable invariants)

- **No self-service write to the record of record.** No `STUDENT` or `GUARDIAN` is entitled to any consequential tool — `sis.update_enrollment_record`, `assessment.release_grade`, and the privileged IT remediations are **registrar/educator/IT-admin only**.
- **The EDU bright line.** Posting a grade, changing enrollment, sending family/student outreach, publishing content to students, financial/procurement approval, and privileged IT remediation are all consequential and require a named human approver bound into the record before execution (`policy.py` registry comments; `gateway.py` step 3).
- **Guardian rights-transfer drop.** When `rights_transferred` is set, the GUARDIAN role is removed before the intersection is computed (`gateway._roles_from_claims`, `auth.roles_from_claims`), so the parent can no longer reach the now-adult student's record. Negative-tested in `governance/tests/test_redteam.py` and `platform_core/tests/test_record_authz.py`.
- **Record scope for self-scoped principals.** Even on a tool they are entitled to, a student/guardian is denied another student's record at gateway step 2b (`policy.record_scope_ok`).

### A.4 Agent 01 effective surface (golden path)

Agent 01's grant is `AGENT_TOOL_GRANTS["01-student-family-concierge"]` = `{sis.get_student_profile, sis.get_schedule, sis.check_application_status, kb.search_policies, crm.get_case, crm.create_advising_case, crm.schedule_appointment, comms.draft_message, comms.send_message}`. The **effective** tool surface for a user driving Agent 01 is the intersection of that grant with the user's role entitlement:

| User role on Agent 01 | Effective tools (agent grant ∩ entitlement) |
|---|---|
| **STUDENT** | `sis.get_student_profile`R, `sis.get_schedule`R, `sis.check_application_status`R, `kb.search_policies`, `crm.create_advising_case`, `crm.schedule_appointment`, `comms.draft_message` — **all reads record-scoped to self; no `comms.send_message`** (student isn't entitled), no consequential tools |
| **GUARDIAN** | same minus `crm.create_advising_case`; reads scoped to **linked** student; dropped to nothing on rights transfer |
| **COUNSELOR** | adds `crm.get_case`R and **`comms.send_message`C** (consequential — requires approval); institutional record scope |
| **FINANCIAL_AID** | `sis.get_student_profile`R, `sis.check_application_status`R, `crm.get_case`R, `crm.create_advising_case`, `comms.draft_message`, **`comms.send_message`C**, `kb.search_policies` |
| **ADMINISTRATOR** | `sis.get_student_profile`R, `sis.get_schedule`R, `sis.check_application_status`R, `crm.get_case`R, `crm.create_advising_case`, `comms.draft_message`, **`comms.send_message`C**, `kb.search_policies` |

Note that the **same agent** exposes a deliberately different surface per role — a student gets self-scoped reads and draft-only comms; a counselor additionally gets case access and (approval-gated) outbound family messaging. This is the intersection model doing its job.

---

## Part B — AWS principals → permissions → resources → conditions

Source: `infra/cloudformation/security.yaml` (identity/safety), `data.yaml` (audit/WORM), `agent-service.yaml` (native Step Functions path), `infra/lambdas/agentcore_provisioner/index.py` (provisioner). All ARNs are templated per environment; `${Environment}` ∈ {dev,test,stage,prod}.

| Principal | Permission (action) | Resource (scope) | Condition / guard | Source |
|---|---|---|---|---|
| **AgentExecutionRole** (assumed by Lambda / Step Functions / Bedrock) — `bedrock:InvokeModel`, `InvokeModelWithResponseStream`, `ApplyGuardrail` | Invoke models + apply Guardrail | **`!Ref BedrockModelArns`** — pinned foundation-model + inference-profile ARNs (Claude 3.5/3.7 Sonnet/Haiku families by default), **not `Resource:"*"`** | Customer MUST pin exact approved model/region ARNs; cross-region inference profile also needs invoke on the underlying FM in each member region | `security.yaml` `BedrockInvokeWithGuardrail` |
| **AgentExecutionRole** — `dynamodb:PutItem` | **Append-only audit** | `!Ref AuditTableArn` (the audit table only) | **`UpdateItem`/`DeleteItem` intentionally absent** — append-only by IAM omission; statement only present when `HasAuditTable` | `security.yaml` `AppendOnlyAudit` |
| **AgentExecutionRole** — `secretsmanager:GetSecretValue` | Read connector credentials | **Path-scoped**: `arn:${Partition}:secretsmanager:${Region}:${Account}:secret:edu-agents/${Environment}/*` | No wildcard secret access; per-env prefix | `security.yaml` `ScopedSecretsAndKms` |
| **AgentExecutionRole** — `kms:Decrypt`, `kms:GenerateDataKey` | Use env CMK | **`!GetAtt EnvKmsKey.Arn`** (the single per-env CMK) | CMK key policy also grants the role Encrypt/Decrypt/GenerateDataKey/DescribeKey (`AllowAgentRoleUse`) | `security.yaml` `ScopedSecretsAndKms`, `EnvKmsKey` |
| **AgentExecutionRole** — VPC ENI mgmt | Lambda-in-VPC networking | AWS managed `AWSLambdaVPCAccessExecutionRole` | Trust policy limits assume to `lambda`, `states`, `bedrock` service principals | `security.yaml` `AgentExecutionRole` |
| **Step Functions state machine role** | `lambda:InvokeFunction` (router, HITL-enqueue, finalize); `waitForTaskToken` HITL gate | The agent's own Lambdas / HITL queue table | **Currently the same `AgentExecutionRoleArn`** is reused (see gap G1) | `agent-service.yaml` (`Role: !Ref AgentExecutionRoleArn`, `HitlApprovalGate` waitForTaskToken) |
| **AgentCore provisioner Lambda role** | `bedrock-agentcore:CreateGateway/UpdateGateway/DeleteGateway/GetGateway` + `*GatewayTarget*` + `*AgentRuntime*`; `ssm:GetParameter(s)`; **`iam:PassRole` on AgentExecutionRoleArn**; `kms:DescribeKey/CreateGrant` on env CMK; `cognito-idp:DescribeUserPool*` (read-only); `logs:*` (own logs) | Each statement scoped to the env's resource ARNs | Module docstring instructs: **"Scope every statement to the env's resource ARNs; do NOT grant `Resource:"*"`."** PassRole limited to the one execution role | `agentcore_provisioner/index.py` (IAM PERMISSIONS block) |
| **Cognito authenticated identity** (federated end user) | Reach the app/agent as a verified principal carrying `sub`, roles, `edu_role`, `under_13`, `rights_transferred` | Identity pool denies unauthenticated identities (`AllowUnauthenticatedIdentities: false`) | Claims **mapped from verified IdP assertions only** (`AttributeMapping`); MFA via `CognitoMfaConfiguration` (**prod MUST = ON**, defense-in-depth atop IdP MFA); 14-char password policy | `security.yaml` `UserPool`, `IdentityPool`, `UserPoolIdentityProvider` |
| **Compliance/audit reader** (optional) | `dynamodb:GetItem`, `Query` (read-only); `s3:GetObject`, `ListBucket` on WORM | Audit table + index; WORM bucket | Only created when `HasAuditReader` (customer wires their privacy/compliance role ARN); read-only, separate from the writer | `data.yaml` `AuditReadOnlyPolicy`, `WormBucketPolicy` |
| **Any principal** (WORM bucket) | `s3:*` **denied** without TLS | WORM bucket + objects | `Condition aws:SecureTransport=false → Deny`; Object Lock COMPLIANCE makes objects immutable for the retention window for **every** principal incl. root | `data.yaml` `WormBucketPolicy`, `WormBucket` |

### B.1 Recommended future role split (recommended — NOT YET SHIPPED)

The action plan (P3) calls for decomposing the single shared role into per-function / per-connector roles. **This is a recommendation, not the current state.** Marked clearly so a reviewer does not credit the platform for controls it does not yet ship:

| Recommended principal (future) | Intended scope | Status |
|---|---|---|
| Per-Lambda execution roles (router / HITL-enqueue / finalize) | Each Lambda gets only the actions it needs; no Lambda holds the union | ⬜ **Recommended, not shipped** (action plan P3) |
| Per-connector identity for SoR access | Distinct credential + scope per system of record; connector compromise blast-radius reduced | ⬜ **Recommended, not shipped** (action plan P3 / "connector identity") |
| Dedicated audit-**writer** role (PutItem + conditional `attribute_not_exists`) vs audit-**reader** role | Writer cannot read; reader cannot write; defends audit immutability beyond IAM omission | ⬜ **Partially** — reader policy exists (`data.yaml`); writer/reader split + conditional-write enforcement pending (action plan P2) |
| AgentCore Identity / STS scoped-token issuance replacing the dev HMAC | Asymmetric, revocable, purpose-of-use tokens | ⬜ **Recommended, not shipped** (`tokens.py` docstring; action plan P3) |

---

## Separation of duties (requestor ≠ approver)

For every CONSEQUENTIAL tool, the **requestor (the agent acting for a user) is structurally distinct from the approver (a named, verified human)**:

- The agent can *initiate* a consequential action but **cannot self-approve** — the gateway pends the call (`PENDING_APPROVAL`) until a signed approval that names a verified reviewer `sub` is presented (`gateway.py` step 3; `approvals.sign_approval` requires `reviewer.sub`).
- The approval is **bound to the exact (agent, acting user, tool, canonical args)** and is **single-use** — it cannot be reused, retargeted to another student, or applied to different arguments (`approvals.verify_approval`; tests in `platform_core/tests/test_approvals.py`).
- The reviewer identity is verified and recorded into the audit trail as `approved_by` (`gateway.py` step 6; `auth.record_reviewer_identity`).

**Honest limit:** the platform enforces *requestor (agent) ≠ approver (human)*. It does **not yet** enforce that the approving human is a *different person than the human who triggered the request* in the requestor-human ≠ approver-human sense — that stronger SoD test (and post-action reconciliation) is an explicit **action-plan P3** item ("Separation of duties on approvals (requestor ≠ approver where required); post-action verification"). Customers requiring two-person integrity on specific actions must wire role separation at the reviewer experience.

---

## Least-privilege gaps (honest)

Stated plainly so the review board sees the residual exposure, each pointing to the action plan.

1. **G1 — Shared execution role.** A single `AgentExecutionRole` is assumed by every Lambda *and* the Step Functions state machine (`agent-service.yaml` reuses `!Ref AgentExecutionRoleArn`). Blast radius is wider than per-function/per-connector roles. → **Action plan P3** (role split). See Part B.1.
2. **G2 — Egress breadth.** `AllowedEgressCidr` defaults to `0.0.0.0/0` with a NAT default route for the private subnets — a data-exfiltration path for student-data workloads. Mitigation (Network Firewall / VPC-endpoint policies / data perimeter / dropping NAT once Secrets/KMS/Logs interface endpoints are added) is documented but **customer-owned and off by default** (`network.yaml`). → **Action plan P2**.
3. **G3 — Audit immutability rests on IAM omission.** DynamoDB has no table-level resource policy to add an explicit `Deny` on `UpdateItem`/`DeleteItem`; the guarantee is principal-side (PutItem-only). Defense-in-depth (conditional `attribute_not_exists` PutItem, writer/reader split, scheduled WORM export) is documented; enforcement is **partially pending** (`data.yaml` comment block). → **Action plan P2**.
4. **G4 — Dev scoped-token + in-memory single-use store.** The scoped tool token is a symmetric dev HMAC and the single-use approval nonce store defaults to in-process memory, so cross-worker replay is only closed once the DynamoDB conditional-write store and AgentCore Identity/STS are wired (`tokens.py`, `approval_store.py`). → **Action plan P2/P3**.
5. **G5 — Config discipline for demo flags.** Leaving `CONNECTOR_MODE=fixture/demo`, `EXTRACT_MODE=demo`, or `AUTH_ALLOW_UNVERIFIED_CLAIMS=1` set in a non-local environment re-opens the unverified-claims and unsigned-approval paths (`auth.py`/`approvals.py` `_demo_mode`). Deployment hardening and CI must assert these are unset in prod. → Operational; reinforced by **action plan P0/P3** identity items.
6. **G6 — Mutable Cognito identity claims.** `edu_role`, `under_13`, `rights_transferred` are `Mutable: true` so the IdP/SIS sync can update them — the template explicitly warns this is **not** a license for end users to set their own role/age/rights state, and write access must be locked down (`security.yaml` Schema comment block). Lockdown is customer-owned.

---

*This matrix is an engineering artifact for security review, not a compliance certification. Regulatory obligations are shared and largely customer-owned — see `governance/controls/control_mappings.py` and `docs/SHARED-RESPONSIBILITY-MATRIX.md`.*
