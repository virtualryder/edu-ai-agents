# Production-Readiness Action Plan

*Last updated: June 2026. This is the honest gap register and remediation roadmap for the EDU AI Agent Suite. It exists so a CIO, CISO, or director of architecture can see exactly what is done, what is in progress, and what they (or the delivery team) still own before production. Read it alongside the [Maturity Ladder](../README.md#maturity-ladder), the [Shared Responsibility Matrix](SHARED-RESPONSIBILITY-MATRIX.md), and the [AWS Deployment Reference](AWS-DEPLOYMENT-REFERENCE.md).*

## How to read this

The suite is a **governed reference accelerator and pilot kit** — strong on architecture, governance, and candor — **not** a turnkey, certified, production-deployed product. An external security review (validated below against the actual code) reached the same conclusion. This plan turns that review into staged, verifiable work.

Status legend: ✅ Done · 🔧 In progress · ⬜ Planned / customer-owned. Owner: **Dev** (this repo / SI), **Cust** (institution: IT, security, data, legal), **AWS** (Solutions Architect / partner engineering).

## Validation of the external review (what's accurate, what was overstated)

The review was largely accurate and fair. Confirmed against the code:

- **AgentCore Gateway and Runtime are provisioning *contracts*, not completed provisioning** — without a customer-supplied custom-resource service token the templates only write config to SSM and return a `PENDING-PROVISION` status. **Accurate** (`agentcore-gateway.yaml`, `agent-service.yaml`).
- **The native Step Functions + Lambda path is genuinely real** — 4 Lambdas + a `waitForTaskToken` human gate with a fail-closed timeout. **Accurate**, but the ASL is inline in the template (no separate `.asl.json`) and Lambda artifacts are built by `scripts/package_lambdas.sh`, not a fully automated pipeline.
- **`verify_jwt` trusted a pre-decoded claims dict; approvals weren't bound to the transaction; the scoped token is a dev HMAC.** **Accurate** — and the first two are now **fixed** (see P0 below).
- **Cognito MFA optional, mutable education claims, localhost callback; broad Bedrock IAM grant; NAT egress to `0.0.0.0/0`; audit immutability via IAM omission; 7-yr Object Lock default; cfn-lint `|| true`; no SECURITY.md.** **All accurate** — addressed in P0/P1 below.

Where the review **overstated**: the IAM role is *not* uniformly broad (audit/secrets/KMS statements are already scoped — only Bedrock used `Resource: "*"`); there are no separate ASL files to "complete" (the workflow is inline and real); and the "FERPA/COPPA compliance" issue was mostly a marketing-tagline overreach already counterbalanced by honest disclaimers elsewhere. Credit due: **the repo pre-documents nearly every gap** in `AWS-DEPLOYMENT-REFERENCE.md` and `AWS-DEPLOYMENT-VALIDATION.md`.

---

## P0 — Correct the claims and close the two real security bypasses ✅ (done this pass)

| Item | Status | Owner | Verification |
|---|---|---|---|
| Remove overclaims ("compliant with student-privacy law", "PII never egresses the VPC / in-account inference", AgentCore "deployed", "8 production workflows") across README and 19+ docs | ✅ | Dev | `grep -ri "never egresses\|in-account inference\|FERPA/COPPA compliant" --include=*.md` returns clean |
| Add a prominent **seller/usage disclaimer** (README, SUITE-STATUS, SOLUTION-FIELD-GUIDE) | ✅ | Dev | Present under the title block |
| Add root **SECURITY.md** vulnerability-disclosure policy | ✅ | Dev | File exists at repo root |
| **Close the auth bypass** — `verify_jwt` now rejects a pre-decoded claims dict outside demo mode (production requires a signed JWT / verified authorizer context) | ✅ | Dev | `platform_core/tests/test_auth.py` (4 tests) |
| **Bind approvals to the transaction** — consequential approvals are now signed, bound to the exact agent/user/tool/args, single-use (one-time nonce), and expiring; unsigned dicts are rejected in production | ✅ | Dev | `platform_core/tests/test_approvals.py` (5 tests: wrong-args, replay, tamper, prod-reject, signed-allow) |

**Verify P0 end-to-end:** `python -m pytest platform_core/tests governance/tests -q --ignore=governance/tests/test_hitl_gates.py` → 46 passing.

## P1 — Harden the shipped IaC and CI ✅/🔧 (mostly done this pass)

| Item | Status | Owner | Verification |
|---|---|---|---|
| Scope the Bedrock IAM grant from `Resource:"*"` to a `BedrockModelArns` parameter (Claude model/inference-profile ARNs) | ✅ | Dev/Cust | `security.yaml` — `bedrock:InvokeModel*` now `!Ref BedrockModelArns` |
| Make MFA, callback URLs, and identity-claim trust explicit parameters with prod guidance | ✅ | Dev/Cust | `CognitoMfaConfiguration`, `AppCallbackUrls`; comment that `under_13`/`rights_transferred`/role must be IdP-sourced, never self-asserted |
| Force a WORM retention decision (remove the 7-yr default; add `WormMode` GOVERNANCE/COMPLIANCE) | ✅ | Cust | `data.yaml` — `WormRetentionDays` now required |
| Parameterize egress (`AllowedEgressCidr`) + document Network Firewall / egress proxy / data-perimeter for student-data workloads | ✅ | Dev/Cust | `network.yaml` comments + param |
| Make **cfn-lint blocking** (remove `|| true`); add **bandit, pip-audit, detect-secrets, checkov, SBOM** jobs + **Dependabot** | ✅ | Dev | `.github/workflows/ci.yml`, `security.yml`, `dependabot.yml` |
| Document audit immutability defense-in-depth (conditional `attribute_not_exists` PutItem, writer/reader role split, WORM export) | ✅ (doc) / ⬜ (enforce) | Dev | `data.yaml` comment block; enforcement tracked in P2 |
| Resolve the documented checkov findings on `demo-in-a-box.yaml` and reference stacks; then remove checkov `--soft-fail` | 🔧 | Dev | checkov exits 0 without soft-fail |

## P2 — Make ONE golden path fully real (the highest-leverage next step) 🔧

**Progress (this pass, Agent 01 — verified in-repo; deployment still needs a customer AWS account):** the **edge stack** (`infra/cloudformation/edge.yaml` — CloudFront+WAFv2+ACM), **observability** (`observability.yaml` — alarms+dashboard), the **AgentCore provisioner** custom-resource Lambda (`infra/lambdas/agentcore_provisioner/`, fails closed, 7 unit tests), the **one-command** `make golden-path-01` target, the **golden-path runbook** (`runbooks/agent-deploy/01-GOLDEN-PATH.md`), **record-level authorization** (`policy.record_scope_ok` + gateway enforcement), and a **durable single-use approval store** (`mcp_gateway/approval_store.py`, DynamoDB conditional-write) have all landed and are test/lint-verified. Remaining P2 items below are customer-engagement work (live IdP, real connectors, ephemeral-account CI deploy).

Pick **Agent 01 (Student & Family Concierge)** or **Agent 07 (Document & Accessibility)** and take it end-to-end to production quality before adding breadth. Definition of done, each with a verification gate:

| Capability | Owner | Verification |
|---|---|---|
| One-command deploy (automated Lambda packaging + artifact publish + nested stack) | Dev | `make deploy AGENT=01 ENV=pilot` stands up a working environment in a clean account |
| Real **AgentCore Gateway/Runtime provisioner** (custom resource) OR a fully native alternative wired into quickstart | Dev/AWS | Stack output shows a live gateway endpoint, not `PENDING-PROVISION` |
| Working **IdP federation** (Cognito ↔ Okta/Entra/Google), MFA enforced, roles from groups | Cust | An authenticated SAML/OIDC login reaches a role-scoped session |
| A real or standards-based **SIS/LMS connector** (replace the fixture) with record-level authorization | Dev/Cust | A student can read only their own record; cross-record access denied |
| **Edge stack** (CloudFront + WAF + ACM + Route 53) | Dev/Cust | WAF managed rules active; TLS via ACM; no direct origin exposure |
| **Durable single-use approval store** (DynamoDB conditional write) replacing the in-process nonce set | Dev | Replay across workers is rejected |
| **Observability** — alarms for tool-denial spikes, PII-masking failures, approval backlog/timeout, grounding failures, model throttling, cost anomalies | Dev/Cust | Alarms fire in a synthetic test |
| **Monitoring + DR + teardown** runnable; synthetic integration dataset; cost report | Dev/Cust | RTO/RPO test passes; `make destroy` leaves no residue |
| **Security smoke tests** in CI deploying to an ephemeral account | Dev | Ephemeral deploy + authz/HITL smoke + auto-teardown green |

**Do not add a ninth agent until one agent clears this bar.** The other seven then ship as extensions of the proven platform.

## P3 — Identity, policy, and approval depth (platform-wide) ⬜

| Item | Owner | Verification |
|---|---|---|
| Identity ONLY from a verified authorizer context in production (now enforced in code; wire to the real Lambda authorizer / AgentCore Identity) | Dev/Cust | A request without a verified context is rejected at the edge |
| **Record-level authorization** (a user reaches only their own / their assigned students' records) and verified guardian↔student relationships | Dev/Cust | Negative tests: cross-student and post-rights-transfer access denied |
| Externalize policy to **Cedar / Amazon Verified Permissions** (or OPA) generated from `policy.py` so the Python model and the deployed authorizer can't drift | Dev/AWS | Cedar policy decisions match `policy.decide()` on a shared test vector |
| Separation of duties on approvals (requestor ≠ approver where required); post-action verification; complete case-level audit linkage | Dev | Tests assert requestor≠approver and post-write reconciliation |
| Replace the dev HMAC scoped token with **AgentCore Identity / STS**; add purpose-of-use, data-classification, connector identity, revocation | Dev/AWS | Token issued by AgentCore/STS; revocation honored |

## P4 — Customer assurance package (per golden path) ⬜

Deliverables a CISO/architecture review board will ask for: architecture + data-flow diagrams, **threat model**, **privacy impact assessment** template, FERPA/COPPA responsibility matrix (extend `SHARED-RESPONSIBILITY-MATRIX.md`), **IAM matrix**, model/prompt/tool inventories, **SBOM**, security-scan and test results, **accessibility conformance** (axe-core + manual screen-reader + PDF/UA, not just the preflight), RTO/RPO test, cost estimate, known-limitations, and a defined **operations & support model** (release/change management for model/prompt/policy/connector changes, rollback, revalidation, incident runbooks).

## Compliance & accessibility posture (unchanged, restated honestly)

The platform provides **FERPA/COPPA/IDEA/ADA-aligned control patterns**, not a certification. Compliance depends on institutional policy, contracts (DPA, FERPA "school official" determination), purpose limitation, retention, training, vendor oversight, and incident response — all **customer-owned**. Accessibility ships a deterministic **preflight**; formal **WCAG 2.x conformance testing remains the customer's responsibility**. None of this is legal advice.

## One-glance verification commands

```bash
# Governance + platform (incl. the new auth + transaction-bound-approval tests)
python -m pytest platform_core/tests governance/tests -q --ignore=governance/tests/test_hitl_gates.py

# IaC parses + lints
pip install cfn-lint checkov --break-system-packages -q
cfn-lint infra/cloudformation/*.yaml

# Security scans (as CI runs them)
bandit -r platform_core governance -ll ; pip-audit ; detect-secrets scan
```
