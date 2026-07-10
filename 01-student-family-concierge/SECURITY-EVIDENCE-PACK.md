# Security Evidence Pack — EDU Agent 01 — Student & Family Concierge

*The security-review companion for the portfolio's **land** agent. It gives a CISO / director of
architecture / FERPA auditor the IAM role matrix and the MCP authorization matrix (both buildable
now), and — unlike the other heroes — lists **runtime proofs that were actually captured** in a
clean AWS account on 2026-07-10. Captured items are marked ✅ with the evidence; everything else is
staged, not asserted. Because Agent 01 is the golden path, this gateway/identity/audit/HITL evidence
is the pattern Agents 02–08 inherit.*

> Reference accelerator — not an AWS service, not a certification. See [`../NOT-CLAIMS.md`](../NOT-CLAIMS.md).

## 1. MCP authorization matrix (what this agent can and cannot do)

Effective permission = **agent grant ∩ user entitlement**, then **FERPA record scope** on top (a
self-scoped principal reaches only their own / a linked record). Consequential acts require a bound
human approval. Source: `platform_core/edu_agent_platform/mcp_gateway/policy.py`.

| Tool | Agent authority | Access / who commits |
|---|---|---|
| `sis.get_student_profile` | granted | read · **record-scoped** (own/linked only) |
| `sis.get_schedule` / `sis.check_application_status` | granted | read · record-scoped |
| `kb.search_policies` | granted | read (public institution facts in live mode — College Scorecard) |
| `crm.get_case` | granted | read · **staff only** (not a student entitlement) |
| `crm.create_advising_case` / `crm.schedule_appointment` | granted | low-risk write |
| `comms.draft_message` | granted | draft only |
| `comms.send_message` | granted | **consequential · human approval required** (family/student outreach) |

The **least-privilege intersection** is the point: a STUDENT driving the Concierge can never reach
`crm.get_case` or `comms.send_message` — those are withheld by the *user's* entitlement even though the
agent is granted them. Strict separation-of-duties (requestor ≠ approver) is reserved for the
enrollment / procurement **commits** (`sis.update_enrollment_record`, `erp.initiate_approval`).

## 1a. MCP authorization negative-test matrix (12 cases — proven, CI-gated)

The identical 12-case "hard proof" every hero ships, proven against EDU's **shipping gateway** by
`governance/tests/test_mcp_authz_matrix.py` (**12/12**). Framing maps to the deployed edge
(401/403/deny); offline the gateway returns a DENY decision or the primitive raises.

| # | Attempt | Edge | Proven by |
|---|---|---|---|
| 1 | No token / unauthenticated | **401** | gateway → DENY (no authenticated subject, fail-closed) |
| 2 | Bad / unverifiable token | **401** | `auth.verify_jwt` raises `AuthError` (no JWKS, `none`/unverified rejected) |
| 3 | Valid token, **missing scope** | **403** | a token minted for tool A is rejected at tool B (scope mismatch) |
| 4 | Unregistered tool | deny | unknown-tool deny (allow-list) |
| 5 | Wrong role (not entitled) | deny | least-privilege intersection — STUDENT denied `comms.send_message` |
| 6 | Wrong data class (**FERPA record boundary**) | deny | a student is denied **another student's** record |
| 7 | Self-approval | deny | approver == requester refused on the enrollment commit (SoD) |
| 8 | Replayed approval | deny | single-use nonce already consumed |
| 9 | Tampered approval args | deny | canonical args-hash mismatch |
| 10 | Stale / expired approval | deny | approval `exp` in the past is rejected |
| 11 | No outbound credential | deny | no valid scoped token → the connector is unreachable |
| 12 | Audit write failure | fail-closed | the gateway raises rather than proceeding without an audit trail |

```bash
PYTHONPATH=platform_core:. pytest governance/tests/test_mcp_authz_matrix.py -q   # 12 passed
```

Case 6 is EDU's data-class boundary expressed as FERPA record scope — the control a school district's
privacy officer most needs to see. AWS AgentCore note: `AUTHENTICATE_ONLY` does not enforce
authorization and "No Authorization" is not for production — this gateway always authorizes
(deny-by-default) and mints a scoped outbound credential per call. See [`../GATEWAY-MODES.md`](../GATEWAY-MODES.md).

## 2. IAM role matrix (least privilege, per role)

Full matrix: [`../docs/assurance/IAM-MATRIX.md`](../docs/assurance/IAM-MATRIX.md). The golden-path
CloudFormation provisions one scoped role — pattern:

| Role | Scope (least privilege) | Notable denies |
|---|---|---|
| Lambda execution role (deployed) | `bedrock:InvokeModel` scoped to FM / inference-profile ARNs; `dynamodb:PutItem` on the audit table ARN; KMS on the CMK ARN; logs | **no `UpdateItem` / `DeleteItem`** (append-only); no direct SIS/CRM access |
| Connector role (per `connector_kind`) | the one system-of-record endpoint + its secret | scoped to that connector only |
| Reviewer service role | mint bound approvals; resume the human gate | cannot invoke tools directly |
| KMS usage | encrypt/decrypt scoped to the data-class CMK | key policy separates admin from usage (SoD) |

Data class for this hero: **student PII / FERPA education records** (masked before model invocation and
before audit write).

## 3. Runtime proofs — ✅ CAPTURED in a clean account (2026-07-10)

Deployed via `aws cloudformation create-stack` (`eduverify-golden-path` → `CREATE_COMPLETE`), exercised,
and torn down. Full evidence: [`../docs/evidence/clean-account-deploy.md`](../docs/evidence/clean-account-deploy.md),
[`../docs/evidence/identity-and-accessibility.md`](../docs/evidence/identity-and-accessibility.md).

| Proof | Status | Evidence |
|---|---|---|
| **Runtime student-PII masking** (real deployed audit record) | ✅ **captured** | `student_body_masked = "Student [SID-REDACTED] SSN [SSN-REDACTED] … [EMAIL-REDACTED]"` — SSN/email/student-id redacted in the cloud, not a unit test |
| **Real model invocation** | ✅ **captured** | `us.anthropic.claude-sonnet-4-6` via `bedrock-runtime.invoke_model` (guardrail-attached); answer stored in the audit record |
| **Deployed immutable audit** | ✅ **captured** | conditional (`attribute_not_exists`) `PutItem` → CMK-encrypted, PITR-on DynamoDB table; `audit_id AUD-73b3d769a9329019f7cf`, `pii_masked=true` |
| **Accessibility (WCAG signal)** | ✅ **captured** | axe-core **0 violations** — [`../docs/evidence/axe-report.json`](../docs/evidence/axe-report.json) |
| **Teardown — resources removed** | ✅ **captured** | stack, guardrail, CMK deleted / scheduled at end of run |
| Bedrock Guardrail **intervention** (blocked invoke) | ☐ pending | guardrail was *attached*; a blocked-invoke capture is the next runtime item |
| IAM Access Analyzer findings | ☐ pending | `accessanalyzer list-findings` on the deployed roles |
| CloudWatch security alarms + dashboard | ☐ template ready | deploy `infra/cloudformation/security-alarms.yaml` (10 security signals) alongside `observability.yaml`; capture `describe-alarms` on next deploy |
| Production IdP (Cognito JWT) at the edge | ☐ pending | JWT verification is offline-proven (case #2); the clean-account run invoked the Lambda directly. Federation is customer engagement work |

*S3 Object-Lock WORM is the Evidence-Vault variant; this hero proves audit immutability via the
append-only conditional-PutItem DynamoDB path above + IaC deny, which is what was deployed.*

## 4. Already proven offline (cite now — no deploy needed)

- **12-case MCP authorization matrix** (`test_mcp_authz_matrix.py`, **12/12**) — §1a.
- **Consequential bright line** (`test_consequential_bright_line.py`): no agent can commit a
  consequential action without approval; every granted consequential tool is registered.
- **HITL gates** (`test_hitl_gates.py`): every agent interrupts before the human gate.
- **PII masking boundary** (`test_pii_masking_boundary.py`): raw SSN / email / student-id survive
  neither the mask output nor the audit record.
- **Red-team** (`test_redteam.py`) + **grounding** (`test_grounding.py`): prompt-injection resistance;
  fails fast rather than inventing a deadline/policy/status.
- **AGP v1.0 conformance** ([`../AGP-CONFORMANCE.md`](../AGP-CONFORMANCE.md)); **threat model**
  ([`../docs/assurance/THREAT-MODEL.md`](../docs/assurance/THREAT-MODEL.md)); security CI (blocking
  bandit + detect-secrets against committed baselines).

*If any statement reads stronger than [`../NOT-CLAIMS.md`](../NOT-CLAIMS.md) or
[`../MATURITY.yaml`](../MATURITY.yaml), those files govern.*
