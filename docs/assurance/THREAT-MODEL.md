# Threat Model — EDU AI Agent Suite (Agent 01 Golden Path + Shared Platform)

*Audience: customer CISO / security architecture review board. Scope: the Agent 01 (Student & Family Concierge) golden path and the shared platform controls it exercises, as actually implemented in this repository. Every control claim cites a file a reviewer can open and verify. Residual risks are stated honestly and cross-referenced to [`docs/PRODUCTION-READINESS-ACTION-PLAN.md`](../PRODUCTION-READINESS-ACTION-PLAN.md).*

Companion document: [`IAM-MATRIX.md`](IAM-MATRIX.md) (least-privilege entitlement and AWS-principal matrix).

---

## 1. Scope, assumptions, and maturity caveat

### 1.1 In scope

- The **MCP authorization gateway** — the single enforcement point for every agent tool call: authentication, deny-by-default authorization, record-level authorization, the human-in-the-loop (HITL) approval gate, scoped-token minting, connector invocation, audit, and fail-closed error handling (`platform_core/edu_agent_platform/mcp_gateway/gateway.py`).
- The **authorization policy model** — agent grants, role entitlements, consequential-tool set, record-scoped tools (`.../mcp_gateway/policy.py`).
- **Signed, transaction-bound, single-use approvals** (`.../mcp_gateway/approvals.py`, `.../mcp_gateway/approval_store.py`).
- **Identity/claims handling** and demo-mode gating (`platform_core/edu_agent_platform/auth.py`, `.../mcp_gateway/tokens.py`).
- **PII masking at the log/audit boundary** (`platform_core/edu_agent_platform/pii_masker/__init__.py`).
- The **shared AWS reference IaC**: identity/safety (`infra/cloudformation/security.yaml`), network (`network.yaml`), data/audit/WORM (`data.yaml`), edge (`edge.yaml`), and the AgentCore provisioner custom resource (`infra/lambdas/agentcore_provisioner/index.py`).

### 1.2 Assumptions (trust assumptions a reviewer should validate)

1. The institution operates an authoritative IdP (Okta / Microsoft Entra / Google Workspace / AD FS) and federates it through Amazon Cognito or IAM Identity Center. Roles and the EDU-specific claims (`edu_role`, `under_13`, `rights_transferred`) are **sourced from verified IdP/SIS assertions only** and are never self-asserted by the end user (`security.yaml` UserPool `Schema` comment block; `auth.py` `verify_jwt`).
2. In production, no demo flag is set: `CONNECTOR_MODE` is not `fixture`/`demo`, `EXTRACT_MODE` is not `demo`, and `AUTH_ALLOW_UNVERIFIED_CLAIMS` is unset. These flags loosen authentication and approval verification and are for local development only (`auth.py::_demo_mode`, `approvals.py::_demo_mode`).
3. The customer pins and tunes the Bedrock Guardrail, the Bedrock model allow-list (`BedrockModelArns`), the WORM retention window/mode, and the egress perimeter before production (`security.yaml`, `data.yaml`, `network.yaml`).
4. The customer signs the appropriate FERPA "school official" determination / Data Processing Agreement; legal compliance is a shared, customer-owned obligation (`governance/controls/control_mappings.py` — most regimes are status `Configurable` or `Customer`).

### 1.3 Maturity caveat (read this first)

This suite is a **governed reference accelerator and pilot kit** — strong on architecture, governance, and candor — **not** a turnkey, certified, production-deployed product. Several controls in this model are **reference-grade with a documented gap to production**, in particular:

- The scoped tool token is a **development HMAC**, not yet AgentCore Identity / STS (`tokens.py` module docstring; action plan P3).
- The single-use approval nonce store defaults to **in-process memory**; the durable DynamoDB conditional-write store exists but must be wired in production (`approval_store.py::default_store`; action plan P2).
- AgentCore Gateway/Runtime is a **provisioning contract**: until the provisioner Lambda is wired, the gateway endpoint reads `PENDING-PROVISION` (`agentcore_provisioner/index.py` module docstring; action plan P2).
- General internet egress (`AllowedEgressCidr` default `0.0.0.0/0`) and shared-execution-role breadth remain (action plan P2/P3).

The residual risks in §5 are **real**, not hypothetical, and each points to the action-plan item that closes it.

---

## 2. Assets

| # | Asset | Why it matters | Primary protecting control(s) |
|---|---|---|---|
| A1 | **Student education records / PII** (profiles, schedules, grades, attendance, application status) | FERPA-protected; COPPA-heightened for under-13 | Deny-by-default + record-scope authz (`policy.py`); masking at audit boundary (`pii_masker`); Guardrail PII policy (`security.yaml`) |
| A2 | **Tamper-evident audit trail** | FERPA disclosure recordkeeping; non-repudiation of every agent action | Append-only DynamoDB (PutItem-only IAM); WORM S3 Object Lock (`data.yaml`); masked at write (`gateway.py` step 6) |
| A3 | **IdP tokens / sessions** | Compromise = impersonation of a real principal | Cognito federation, MFA-capable, RS256 JWT verification (`security.yaml`, `auth.py::verify_jwt`) |
| A4 | **Signed approval records** | Authorize consequential actions (grade release, enrollment change, family outreach) | Signed, transaction-bound, single-use (`approvals.py`); durable nonce store (`approval_store.py`) |
| A5 | **Scoped tool tokens** | Bearer credential the connector presents to a system of record | Short-lived, single-tool scope, user context embedded (`tokens.py`) |
| A6 | **KMS customer-managed key** | Root of encryption for audit, HITL, WORM, secrets | Per-env CMK, key rotation, retain-on-delete, scoped key policy (`security.yaml` `EnvKmsKey`) |
| A7 | **Model prompts / outputs** | May contain student PII; injection target | Guardrail (PII + content + prompt-attack filters), masking, in-account Bedrock VPC endpoint (`security.yaml`, `network.yaml`) |
| A8 | **Connector credentials** | Standing access to systems of record if leaked | Secrets Manager path-scoped to `edu-agents/<env>/*`, CMK-encrypted; agent holds NO direct SoR creds (`security.yaml`) |

---

## 3. Trust boundaries and data flow

The shared request path. Each numbered boundary is a point where data or trust changes hands and is enumerated in the STRIDE table (§4).

```
                            ┌──────────── TB1 ────────────┐
   [ Viewer / browser ] ───▶│ CloudFront + AWS WAFv2      │   edge.yaml
   (student, guardian,      │  - TLS 1.2_2021, HSTS       │   (managed rules,
    staff, reviewer)        │  - managed rules + rate cap │    rate-based rule,
                            │  - static cached; API       │    security headers)
                            │    pass-through, no cache   │
                            └──────────────┬──────────────┘
                                           │ HTTPS (Authorization forwarded)
                            ┌──────────── TB2 ────────────┐
                            │ Cognito / IdP federation +  │   security.yaml,
                            │ JWT verification (RS256)    │   auth.py
                            │  - roles + edu_role/under_13│
                            │    /rights_transferred from │
                            │    VERIFIED assertions only │
                            └──────────────┬──────────────┘
                                           │ verified claims (sub, roles, scope claims)
                            ┌──────────── TB3 ────────────┐
                            │ App / Agent runtime         │   agent-service.yaml
                            │ (private subnets, no public │   (Step Functions +
                            │  inbound) — NO direct SoR    │    Lambdas, or
                            │  network path                │    AgentCore Runtime)
                            └──────────────┬──────────────┘
                                           │ invoke(tool, args, approval?)
        ┌──────────────────────────── TB4 ──────────────────────────────┐
        │  MCP AUTHORIZATION GATEWAY  (gateway.py — the one front door)   │
        │  1 authn (fail-closed on no sub)                               │
        │  2 deny-by-default authz: agent_grant ∩ user_entitlement       │
        │  2b record_scope_ok (own/linked record for self-scoped roles)  │
        │  3 HITL gate for CONSEQUENTIAL tools (signed approval required) │
        │  4 mint short-lived, single-tool scoped token                  │
        │  5 invoke connector   6 audit (masked, with lineage)   7 fail   │
        │                                                         closed  │
        └───────┬───────────────────────────────────────┬───────────────┘
                │ TB5                                     │ TB6
   ┌────────────▼─────────────┐          ┌───────────────▼──────────────────┐
   │ Bedrock + Guardrails     │          │ Connectors → Systems of Record    │
   │ (in-account VPC endpoint)│          │ (SIS / CRM / KB / Comms)          │
   │ security.yaml/network.yaml│         │ Secrets-Manager creds, path-scoped │
   └──────────────────────────┘          └───────────────┬───────────────────┘
                                                          │ TB7
                                         ┌────────────────▼──────────────────┐
                                         │ Data tier                          │
                                         │  - Append-only audit (DynamoDB)    │
                                         │  - WORM S3 (Object Lock COMPLIANCE)│
                                         │  - HITL queue (DynamoDB, TTL)      │  data.yaml
                                         └────────────────────────────────────┘
```

**Boundaries:**
- **TB1** — Untrusted internet → edge (CloudFront/WAF). Only public surface.
- **TB2** — Edge → identity/authentication (Cognito/JWT).
- **TB3** — Authenticated session → agent runtime (private; no public inbound).
- **TB4** — Agent runtime → authorization gateway (the trust pivot; everything consequential is decided here).
- **TB5** — Gateway → model plane (Bedrock + Guardrails).
- **TB6** — Gateway → connectors → systems of record.
- **TB7** — Gateway/connectors → data tier (audit, WORM, HITL).

The security-critical property: **authorization, the human gate, and the audit trail live at TB4, outside the model (TB5).** No prompt content can move those controls.

---

## 4. STRIDE analysis

STRIDE categories: **S**poofing, **T**ampering, **R**epudiation, **I**nformation disclosure, **D**enial of service, **E**levation of privilege.

| # | Threat | STRIDE | Boundary | Asset | Existing mitigation (cite) | Residual risk | Owner |
|---|---|---|---|---|---|---|---|
| T-01 | **Indirect prompt injection** — instructions hidden in a student-submitted document, inbound family email, or pasted text try to make the agent exceed scope, exfiltrate another student's record, or skip the human gate | T / E / I | TB3→TB4 | A1, A7 | Authz, HITL, and audit are **outside the model** at the gateway — they hold regardless of prompt text. Red-team scenarios encode the exact attack strings (`governance/redteam/__init__.py::PROMPT_INJECTION`); `governance/tests/test_redteam.py::test_injection_cannot_grant_unauthorized_tool` proves a "you are admin" arg still yields `DENY`. Guardrail `PROMPT_ATTACK` filter at `InputStrength: HIGH` (`security.yaml`) | Injection can still degrade *answer quality* within the user's own authorized scope (e.g., a misleading drafted message); the gateway bounds *actions*, not output fidelity. Grounding/eval depth is governance-owned | Dev / Cust |
| T-02 | **Approval replay / forgery / retarget** — reuse or hand-craft a consequential-action approval to send a different message, target another student, or skip the gate | S / E / T | TB4 | A4 | Approvals are **signed, bound to exact (agent, user, tool, canonical args), single-use (one-time nonce), expiring** (`approvals.py::sign_approval`/`verify_approval`). Hand-built unsigned dicts are rejected outside demo mode (`gateway.py::_approval_associated`). Tests: wrong-args rejected, replay rejected, tampered signature rejected, prod-reject-unsigned, signed-allow (`platform_core/tests/test_approvals.py`, 5 tests) | Single-use enforcement defaults to an **in-process nonce store** (`approval_store.py::InMemoryApprovalNonceStore`); replay across multiple workers is only closed once the **DynamoDB conditional-write store** is wired. Signing key is a dev HMAC, not KMS/AgentCore-issued | Dev (P2/P3) |
| T-03 | **Cross-record access / IDOR** — a student (or guardian) passes another student's `student_id` to a tool they are otherwise entitled to | E / I | TB4 | A1 | Record-level authorization: `policy.record_scope_ok` restricts self-scoped roles (STUDENT, GUARDIAN) to their own / explicitly linked records; enforced at gateway step 2b *before* the connector (`gateway.py` lines 119–131). Tests: own-ok, other-denied, guardian-linked-ok/unlinked-denied, gateway integration deny (`platform_core/tests/test_record_authz.py`) | Staff roles operate at **institutional scope** by default; narrowing a staff member to assigned students/sections requires the customer to populate an entitlement claim (`policy.py` `record_scope_ok` comment). Verified guardian↔student linkage is an IdP/SIS data-quality dependency | Cust (P3) |
| T-04 | **Self-asserted claims / authz bypass** — a caller submits a forged claims dict asserting `REGISTRAR` or flips `rights_transferred` | S / E | TB2→TB4 | A1, A3 | `verify_jwt` rejects a pre-decoded claims dict outside demo mode and requires an RS256-verified JWT (`auth.py`); deny-by-default intersection means even a forged role only grants what that role is entitled to AND the agent is granted (`policy.decide`). Cognito schema flags role/`under_13`/`rights_transferred` as IdP-sourced, non-self-asserted (`security.yaml` Schema comment). Tests: prod rejects unverified dict, demo still requires `sub` (`platform_core/tests/test_auth.py`) | If the customer leaves a demo flag set in a non-local environment, the unverified-claims path re-opens — this is an **operational/config residual** that deployment hardening must prevent. IdP attribute write-lockdown on the mutable Cognito attributes is customer-owned | Cust |
| T-05 | **Token theft / replay** — capture a scoped tool token and reuse it | S / I | TB4→TB6 | A5 | Tokens are **short-lived (default 60s TTL), scoped to exactly one tool, carry user context**, and are signature-verified with tool-scope match on every use (`tokens.py::mint_scoped_token`/`verify_scoped_token`). No standing service account | Dev HMAC symmetric secret (`GATEWAY_TOKEN_SECRET`) rather than AgentCore Identity / STS asymmetric issuance; no revocation list yet (`tokens.py` docstring). Closing this is action-plan **P3** | Dev / AWS |
| T-06 | **PII exfiltration to logs / audit** — raw SSN, student ID, DOB, address, email, card number lands in a log or audit record | I | TB4→TB7 | A1, A2 | Deterministic masker applied at the audit/log boundary covering SSN, student/case/app IDs, dates finer than a year, email, phone, address, Luhn-validated cards, long numeric IDs (`pii_masker/__init__.py`); `gateway.py` audits masked. Guardrail PII policy anonymizes/blocks at the model boundary (`security.yaml`). Test: `test_redteam.py::test_pii_exfil_is_redacted` | Regex masking is conservative but **not exhaustive** (names without identifiers, free-text edge cases); the optional ML NER pass (`MASK_ENGINE=ml`, Comprehend/Presidio) is a customer-wired enhancement. Pseudonym salt must be set in prod (`PII_PSEUDONYM_SALT`) | Dev / Cust |
| T-07 | **Tampering with / repudiating the audit trail** — alter or delete an access record to hide a disclosure | T / R | TB7 | A2 | **Append-only by IAM omission**: the agent role is granted `dynamodb:PutItem` only — no `UpdateItem`/`DeleteItem` (`security.yaml` `AppendOnlyAudit`; `data.yaml` immutability comment). PITR enabled; DeletionProtection on. WORM S3 Object Lock (COMPLIANCE mode) for finalized snapshots (`data.yaml` `WormBucket`) | DynamoDB exposes **no table-level resource policy** to add an explicit `Deny` — the guarantee rests on IAM omission. Defense-in-depth (conditional `attribute_not_exists` PutItem, writer/reader role split, scheduled WORM export) is documented but **enforcement is partially pending** (`data.yaml` comment block; action plan P2). A privileged human with broad IAM could still drift the role | Dev / Cust |
| T-08 | **Denial of service** — volumetric / brute-force flood from a source IP, or approval-queue exhaustion | D | TB1 / TB4 | A1, A4 | WAFv2 rate-based rule blocks a source IP exceeding `WafRateLimit` (default 2000) in the 5-min window, plus AWS managed Common/KnownBadInputs/IpReputation rule groups (`edge.yaml`). HITL queue has TTL so stale tokens fail closed (`data.yaml` `HitlQueueTable`); gateway fails closed on any error (`gateway.py` step 7) | Rate limit is per-IP — NAT'd campus networks need tuning and the limit does not stop a distributed (botnet) flood without Shield Advanced. No per-tenant request quota / cost-anomaly auto-throttle in the shipped templates (observability alarms recommended, P2) | Cust |
| T-09 | **Privilege escalation via agent over-reach** — an agent granted a broad tool list acts beyond the human's permissions; or a broad Bedrock grant invokes unapproved models | E | TB4 / TB5 | A1, A7 | **Least-privilege intersection**: `permitted(tool) ⇔ tool ∈ AGENT_TOOL_GRANTS[agent] ∩ ⋃ ROLE_ENTITLEMENTS[roles]` — an agent can never exceed the human (`policy.decide`). The previously broad `bedrock:InvokeModel* Resource:"*"` grant is now scoped to the `BedrockModelArns` allow-list (`security.yaml` `BedrockInvokeWithGuardrail`). Red-team `AUTHZ_BYPASS` tuples all denied (`governance/tests/test_redteam.py`) | A **single shared `AgentExecutionRole`** is assumed by every Lambda and the Step Functions state machine (`agent-service.yaml`); per-function / per-connector role split is recommended but **not yet shipped** (action plan P3; see `IAM-MATRIX.md` Part B) | Dev |
| T-10 | **Egress / data exfiltration** — a compromised runtime or connector exfiltrates student data over open egress | I / E | TB3 / TB6 | A1, A8 | Private subnets, no public inbound; in-account Bedrock via VPC interface endpoints; S3/DynamoDB gateway endpoints keep that traffic off the internet (`network.yaml`). Connector creds are Secrets-Manager path-scoped and CMK-encrypted; agent holds no direct SoR creds (`security.yaml`) | **`AllowedEgressCidr` defaults to `0.0.0.0/0`** with a NAT default route — a real exfiltration path for student-data workloads. Mitigation (Network Firewall/SNI allow-list, VPC-endpoint policies, data perimeter, dropping NAT) is documented but **customer-owned and not enabled by default** (`network.yaml` egress comment; action plan P2) | Cust |
| T-11 | **Spoofed origin / edge bypass** — attacker reaches the origin directly, bypassing WAF | S / E | TB1→TB3 | A1 | App tier in private subnets with no public inbound (`network.yaml`); CloudFront is the only public surface, origin is HTTPS-only (`edge.yaml`) | Origin lockdown (Origin-Verify header and/or CloudFront managed-prefix-list restriction on the origin SG) is **documented as customer hardening, not enforced** in the template (`edge.yaml` Origin comment) | Cust |
| T-12 | **Guardian access after FERPA rights transfer** — a parent retains access to a now-adult student's record | E / I | TB2→TB4 | A1 | At age of majority / postsecondary enrollment, `rights_transferred` drops the `GUARDIAN` role in both `auth.roles_from_claims` and `gateway._roles_from_claims`, so the intersection can no longer surface the student's record to the parent. Red-team tuple (guardian, rights transferred, `sis.get_grades`) denied (`governance/redteam/__init__.py`, `test_redteam.py`) | Depends entirely on the IdP/SIS setting `rights_transferred` accurately and promptly — a **data-quality dependency** the customer owns | Cust |

---

## 5. Top residual risks (ranked)

Each points to the action-plan item that closes it.

1. **Open egress for student-data workloads (T-10).** `AllowedEgressCidr` default `0.0.0.0/0` + NAT default route is an exfiltration path. → **Action plan P2** (egress perimeter: Network Firewall / VPC-endpoint policies / data perimeter; drop NAT). Customer-owned.
2. **Single-use approvals not durable cluster-wide (T-02).** In-memory nonce store permits cross-worker replay until the DynamoDB conditional-write store is wired. → **Action plan P2** (durable single-use store).
3. **Scoped tokens are a dev HMAC, not AgentCore Identity/STS (T-05).** Symmetric secret, no revocation. → **Action plan P3** (AgentCore Identity / STS; purpose-of-use; revocation).
4. **Audit immutability rests on IAM omission (T-07).** No table-level deny possible in DynamoDB; defense-in-depth (conditional PutItem, writer/reader split, WORM export) partially pending. → **Action plan P2**.
5. **Shared execution role (T-09).** One `AgentExecutionRole` for all Lambdas + Step Functions; blast radius wider than per-function/per-connector roles. → **Action plan P3** (role split). See `IAM-MATRIX.md` Part B.

A sixth, **config-discipline** residual underlies several rows: a demo flag left set in a non-local environment (T-04) re-opens unverified-claims and unsigned-approval paths. Deployment hardening and CI must assert these flags are unset in prod.

---

## 6. Abuse / misuse cases

These trace the same controls through realistic adversary stories.

### 6.1 A student trying to read another student's record
A student authenticates legitimately, then drives the Concierge agent (or crafts a request) to call `sis.get_student_profile` with a classmate's `student_id`. Authentication passes (real `sub`); authorization passes (a student *is* entitled to `sis.get_student_profile`); but **record-level authorization (TB4 step 2b)** computes `record_scope_ok` and denies, because the target record is neither the student's own nor a linked record (`policy.record_scope_ok`; `test_record_authz.py::test_gateway_denies_student_cross_record`). Result: `DENY`, audited. No connector call is ever made.

### 6.2 A parent after rights transfer
A guardian retains an active session/credential after the student turns 18 / enrolls postsecondary. The IdP/SIS sets `rights_transferred=true`. On the next request the gateway's role derivation **drops the GUARDIAN role** before the intersection is computed, so even read tools the guardian once had (e.g., `sis.get_attendance`) no longer resolve to any entitlement; grades were never in the guardian set at all (`gateway._roles_from_claims`; `policy.ROLE_ENTITLEMENTS["GUARDIAN"]`). Red-team-verified (`test_redteam.py`). **Residual:** correctness depends on the IdP setting the flag promptly (customer-owned).

### 6.3 A compromised connector
A connector to a system of record is compromised (leaked credential or supply-chain). Blast radius is bounded by design: the agent holds **no** direct SoR credentials (all access is brokered by the gateway with short-lived scoped tokens), connector secrets are **path-scoped** to `edu-agents/<env>/*` and CMK-encrypted (`security.yaml`), and every brokered call is audited with connector lineage (`gateway.py` step 6). **Residual:** with open egress (T-10) a compromised runtime could still attempt exfiltration outbound; the data-perimeter hardening in P2 is what fully closes this. A compromised connector returning poisoned *data* is an injection vector into the model (T-01) — bounded in action by the gateway, not in content fidelity.

---

*This threat model is a point-in-time engineering artifact, not legal advice or a compliance certification. Regulatory obligations (FERPA "school official" status, COPPA consent, state student-privacy law, GLBA, PPRA) are shared and largely customer-owned — see `governance/controls/control_mappings.py` and `docs/SHARED-RESPONSIBILITY-MATRIX.md`.*
