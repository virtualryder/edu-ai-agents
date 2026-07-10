# Second-Review Action Plan — EDU AI Agent Suite

*Last updated: June 2026. This is the **delta** from the second external review. It maps that review's
**10 gaps + 5 priorities** to status, the file(s) that changed (or must change), and a verification step.
It does **not** restate the full P0–P4 register — for that, read
[`PRODUCTION-READINESS-ACTION-PLAN.md`](PRODUCTION-READINESS-ACTION-PLAN.md). Maturity claims here derive
from [`STATUS-MANIFEST.md`](STATUS-MANIFEST.md); if anything disagrees, the manifest wins.*

## What the review got right, and what we closed in this pass

The second review's central finding was a **configuration-management concern**: maturity statements
were inconsistent across files (some agent READMEs said "not yet runnable" / "Documented depth" while
runnable code and passing tests existed). That was fair, and it is now fixed — every maturity
statement derives from a single authoritative [`STATUS-MANIFEST.md`](STATUS-MANIFEST.md). The review
also flagged real gaps between the *mechanisms* we had tested in-process and the *deployed,
end-to-end* proof a CISO would demand. We closed the in-code half of several of those this pass; the
deployed-in-a-customer-account half stays honestly open.

**Closed in code this pass (each with passing tests — 74 tests as of 2026-07-07 via**
`python -m pytest platform_core/tests governance/tests infra/lambdas/agentcore_provisioner -q --ignore=governance/tests/test_hitl_gates.py`**):**

- **Connector token boundary** — the gateway passes its scoped token to the connector and the connector independently validates it (`connectors/base.py` `authorize_call`; `gateway._invoke_connector`). A connector can no longer be called without a valid scoped token. Tested in `platform_core/tests/test_gateway_hardening.py`.
- **Fail-closed record scope** — `policy.record_scope_ok` now **denies** record-scoped tools when no authoritative target resolves from identity (a guardian linked to >1 student with no target is denied, not silently widened). Tested in `test_gateway_hardening.py` + `test_record_authz.py`.
- **Separation of duties** — `gateway._separation_ok` + `policy.SEPARATION_REQUIRED_TOOLS` block requestor == approver on enrollment/financial commits. Tested.
- **Telemetry** — `mcp_gateway/metrics.py` emits exactly the metrics the observability template alarms on (`ToolAuthorizationDenied`, `RecordScopeDenied`, `ApprovalRequired`, `PiiMaskingFailure`, `GroundingFailure`, `AuditWriteFailure`); the gateway emits on deny / record-scope / pending. Tested.

**What stays open (honest backlog):** independently-proven clean-account AWS deploy, a production
reviewer UI, real IdP federation, real SIS/LMS connectors, integrated deployed audit, full WCAG
conformance, and an independent penetration test. None of these are claimed as done anywhere.

### Update — the "one complete path" is now proven, and the reviewer is built

Two of the review's headline asks are now closed in-repo (verifiable without an AWS account):

- **One complete path, reproducible (review's #1 ask).** `01-student-family-concierge/demo/golden_transaction.py` runs the full chain — verified identity → policy gateway → scoped tool token → connector (system of record) → signed, transaction-bound, single-use human approval → verified result → PII-masked append-only audit — and **publishes an evidence bundle** (`demo/evidence/golden_transaction_evidence.json`). Asserted by `01-…/tests/test_end_to_end.py`: read allowed, low-risk runs, the consequential send is blocked, a bound approval lets it execute exactly once, replay is rejected, and the masked audit + telemetry are captured. This addresses Gap 1's *mechanism* (the clean-account AWS deploy stays open) and Gap 6's integrated-audit demonstration.
- **Production reviewer (review's P-4 / Gap 4).** `platform_core/edu_agent_platform/reviewer/` implements the full review sequence — authenticate reviewer → entitlement check → show exact action+args → separation of duties → issue a signed single-use approval → reject replay → audit — with a thin Streamlit UI (`reviewer/app.py`) over it. Asserted by `platform_core/tests/test_reviewer.py` (5 tests), including that the issued approval passes the gateway exactly once. Real IdP federation for reviewer login stays customer-owned. The reviewer also **resumes the native Step Functions `waitForTaskToken` HITL gate**: on approval it calls `SendTaskSuccess` with the signed approval (on decline, `SendTaskFailure`) — `reviewer/review_service.py` (`StepFunctionsTaskCallback`), tested in `test_reviewer.py`.

## Status legend

✅ **Closed this pass** (code/template/doc landed with verification) · 🔧 **Partial** (mechanism tested
in-repo; deployed/end-to-end proof outstanding) · ⬜ **Customer-engagement** (owned by the institution
or delivery team; not done here).

## The 10 gaps

| # | Gap (as the review framed it) | Status | File(s) changed / to change | Verification |
|---|---|---|---|---|
| **1** | No independently-proven AgentCore deploy in a clean AWS account | 🔧 | `infra/cloudformation/*.yaml`, `infra/lambdas/agentcore_provisioner/`, `Makefile` (`golden-path-01`), `runbooks/agent-deploy/01-GOLDEN-PATH.md` | `make golden-path-01` stands up a working Agent 01 in a fresh account; stack output shows a live gateway endpoint, not `PENDING-PROVISION`. |
| **2** | Connector could be invoked without an enforced scoped-token boundary | ✅ | `connectors/base.py` (`authorize_call`), `mcp_gateway/gateway.py` (`_invoke_connector`) | `pytest platform_core/tests/test_gateway_hardening.py` — call without a valid scoped token is rejected. |
| **3** | Record-scope check could widen access instead of failing closed | ✅ | `mcp_gateway/policy.py` (`record_scope_ok`), `mcp_gateway/gateway.py` | `pytest platform_core/tests/test_gateway_hardening.py platform_core/tests/test_record_authz.py` — guardian→>1 student with no target is **denied**. |
| **4** | No separation of duties; no production reviewer UI | 🔧 | SoD: `mcp_gateway/gateway.py` (`_separation_ok`), `mcp_gateway/policy.py` (`SEPARATION_REQUIRED_TOOLS`) **✅**. Reviewer UI: not built **⬜** | SoD: `pytest` asserts requestor == approver is blocked on enrollment/financial commits. Reviewer UI: a production HITL queue app with auth — **outstanding**. |
| **5** | HITL routing not proven "only-consequential" + no persistent-interrupt proof; production identity untested | 🔧 | HITL bright-line: `governance/tests/test_consequential_bright_line.py`, gateway approval gate **🔧 (addressed separately)**. Prod identity: `auth.py` hardened **🔧**, real IdP federation **⬜** | Bright-line test asserts no agent executes an irreversible commit without approval; persistent-interrupt + real IdP login remain to prove on deployment. |
| **6** | No single integrated end-to-end audit deployment | 🔧 | `mcp_gateway/audit.py`, `mcp_gateway/metrics.py`, `infra/cloudformation/data.yaml` (WORM S3 + append-only DynamoDB) | Deploy an agent; perform a consequential action; verify the masked audit record lands in deployed immutable storage and the `AuditWriteFailure` alarm is wired. |
| **7** | Telemetry not emitted for the metrics the alarms reference | ✅ | `mcp_gateway/metrics.py`, `mcp_gateway/gateway.py`, `infra/cloudformation/observability.yaml` | `pytest` asserts the six named metrics are emitted on deny / record-scope / pending; alarm names in `observability.yaml` match the emitted metric names. |
| **8** | No unified edge + regional one-shot deploy | ✅ (target ships) | `infra/cloudformation/edge.yaml` (CloudFront+WAFv2+ACM) **✅ ships as a template**; `observability.yaml` **✅**; one-shot regional→edge target **✅** (`scripts/deploy_full.sh`, `make deploy-all-01`) | Templates parse/lint (`docs/AWS-DEPLOYMENT-VALIDATION.md`); `make deploy-all-01` deploys the regional stack then the us-east-1 edge stack in one command (verified: `bash -n`, `make -n`, templates parse); clean-account execution stays customer-owned. |
| **9** | No penetration test | ⬜ | n/a (engagement deliverable) | Independent third-party pen test report against a deployed environment. |
| **10** | No full WCAG conformance; no real SIS/LMS connectors; no load/DR test | ⬜ | A11y: `governance/accessibility/` (preflight) + `docs/assurance/ACCESSIBILITY-CONFORMANCE-PLAN.md` (plan). Connectors: `connectors/` (fixture + local-live). DR: `runbooks/DR-RUNBOOK.md` (runbook) | Formal axe-core + screen-reader + PDF/UA conformance; a real connector against a customer SIS/LMS; an RTO/RPO load/DR test — all customer/engagement-owned. |

## The 5 priorities

| # | Priority | Status | File(s) / evidence | Verification |
|---|---|---|---|---|
| **P-1** | Make maturity statements consistent and authoritative (the configuration-management fix) | ✅ | New [`docs/STATUS-MANIFEST.md`](STATUS-MANIFEST.md); reconciled `README.md`, `SUITE-STATUS.md`, per-agent `README.md` (01–08), `docs/AWS-DEPLOYMENT-VALIDATION.md`; new [`docs/README.md`](README.md) index | Grep for stale phrases ("not yet runnable", "Documented depth", "foundation and positioning layer") returns only manifest-consistent language; every doc links to the manifest. |
| **P-2** | Close the real authorization/approval bypasses in code | ✅ | Gaps 2–4, 7 above (`connectors/base.py`, `mcp_gateway/{gateway,policy,approvals,approval_store,metrics}.py`) | The 74-test command passes (as of 2026-07-07). |
| **P-3** | Prove ONE golden path end-to-end in a clean account | 🔧 | Agent 01: edge + observability templates, AgentCore provisioner, `make golden-path-01`, golden-path runbook all landed; clean-account deploy outstanding (Gap 1) | `make golden-path-01` green in a fresh account with a live gateway endpoint. |
| **P-4** | Stand up production identity + the reviewer UI | 🔧 | `auth.py` hardened (rejects unverified claims outside demo); real IdP federation + HITL reviewer app outstanding (Gaps 4, 5) | SAML/OIDC login reaches a role-scoped session; reviewers action the HITL queue through an authenticated app. |
| **P-5** | Customer assurance package + independent assurance | 🔧 | Landed: `docs/assurance/THREAT-MODEL.md`, `IAM-MATRIX.md`, `PRIVACY-IMPACT-ASSESSMENT-TEMPLATE.md`, `ACCESSIBILITY-CONFORMANCE-PLAN.md`. Outstanding: pen test, full WCAG conformance, per-customer sign-off | Templates present and internally consistent; independent pen test + conformance report are engagement deliverables. |

## Relationship to the production-readiness plan

This document is the **second-review delta** — what that specific review surfaced and where each item
now stands. The complete remediation register (P0–P4, the validation of the *first* review, the
one-glance verification commands, and the compliance/accessibility posture) lives in
[`PRODUCTION-READINESS-ACTION-PLAN.md`](PRODUCTION-READINESS-ACTION-PLAN.md). Read them together: the
production-readiness plan is the full backlog; this is the scorecard for the second review's findings.
The bottom line is unchanged and stated in [`STATUS-MANIFEST.md`](STATUS-MANIFEST.md): platform
controls built and tested, Agent 01 golden-path demonstrated locally, AWS-deploy and production
sign-off still customer work.

### Update 2026-07-10 — clean-account deploy evidence (gaps 1, 2, 3, 4, 5, 6)

These were proven against a real AWS account (111122223333, us-east-1) and torn down; see `docs/evidence/clean-account-deploy.md` and `docs/evidence/identity-and-accessibility.md`:

- **Gap 1 (clean-account CFN deploy) ✅** — `aws cloudformation create-stack` → CREATE_COMPLETE for a golden-path stack (KMS + append-only audit + Lambda). *(The FULL quickstart.yaml nested stack remains ⬜.)*
- **Gap 2 (real model invocation) ✅** — the deployed Lambda invoked `us.anthropic.claude-sonnet-4-6` and stored a real answer.
- **Gap 3 (deployed immutable audit) ✅** — a masked record landed in the DEPLOYED DynamoDB audit table via a conditional/append-only PutItem (CMK-encrypted, PITR).
- **Gap 5 (runtime PII masking) ✅** — SSN/email/student-id redacted at runtime in the cloud before the audit write.
- **Gap 4 (production identity federation) ✅** — a real Cognito-issued RS256 JWT verified by the production `verify_jwt` path (JWKS/iss/aud/exp); tampered token rejected.
- **Gap 6 (accessibility conformance) ✅ (automated)** — axe-core 4.12.1: 0 violations, 17 rules passed. *(Manual screen-reader/PDF-UA conformance remains customer work.)*
- **Gap 7 (status/test-count) ✅** — canonical root pytest **174 passed, 1 skipped**; fixed a `test_agp_conformance.py` import that had broken full-suite collection; `MATURITY.yaml` `clean_account_deploy.status` moved `not-yet -> partial`.

**Still open:** the full quickstart.yaml nested clean-account deploy, real SIS/LMS connectors, independent pen test, full manual WCAG conformance, load/DR test.