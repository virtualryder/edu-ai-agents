# Suite Status

> **What this is:** an independent, open-source reference accelerator for discovery, architecture design, demos, and scoped pilots on AWS. **What it is not:** an AWS service or official AWS solution, a compliance certification (FERPA/COPPA/WCAG), a penetration-tested system, or a turnkey production deployment. Production requires customer-specific identity integration, connectors, security hardening, accessibility conformance testing, operations, and legal/privacy review. If you work at AWS, obtain internal approval before using it as a customer-facing asset.

**Phase:** Demonstrated + Deployable-by-design (platform controls built and tested; Agent 01 golden path demonstrated locally).

> **Authoritative status:** maturity is governed by [`docs/STATUS-MANIFEST.md`](docs/STATUS-MANIFEST.md).
> The summary below derives from it; if anything disagrees, the manifest is correct.

## Maturity
Documented + **Demonstrated** (all 8 agents run end-to-end in `EXTRACT_MODE=demo`, no API key; Agents 01/04/05
also exercise a local-HTTP live-connector path) + **Deployable-by-design** (CloudFormation + Terraform parse/lint,
AgentCore container contract; Agent 01 has a one-command `make golden-path-01`). The shared platform controls are
built and unit-tested. **No agent is AWS-deployed in a clean account, invokes a real model, uses production identity,
or is production-approved** — that, plus live connectors, WCAG 2.2 AA conformance, and a penetration test, is the
customer engagement.

## Built & verified
- **Shared platform** (`platform_core/edu_agent_platform/`): LLM factory (Anthropic/Bedrock + Guardrails),
  student-PII masker (FERPA/COPPA identifiers + stable pseudonyms), MCP authorization gateway
  (deny-by-default least-privilege intersection, human-approval gate, short-lived scoped tokens,
  PII-masked append-only audit, FERPA rights-transfer), connectors (fixture + live HTTP), auth, secrets,
  tracing, demo-aware generation.
- **Governance in code** (`governance/`): grounding verification, hash-pinned prompt registry + manifest
  (8 prompts pinned), structural evals, fairness (representativeness + confusion rates), red team
  (prompt-injection / authz-bypass / PII-exfil), HITL gate enforcement across all 8 agents.
- **8 agents to Demonstrated depth**: each with `agent/` (graph, nodes, state, prompts, persistence),
  gateway-scoped `tools/`, deterministic `data/fixtures/`, Streamlit `app.py`, `requirements.txt`,
  `Dockerfile`, `.env.example`, and a `tests/` suite.
- **Live-connector reference path (Agents 01, 04, 05)**: each has `demo/reference_service.py` (a local
  stand-in for its systems of record), `demo/demo_live.py` (runs the agent end-to-end over REAL HTTP
  through the gateway, `CONNECTOR_MODE=live`, inference auto-selecting Bedrock->Anthropic->demo),
  `demo/DEMO-LIVE.md`, and `tests/test_live_path.py`. Consequential actions (send a message, release a
  grade) are gated at the gateway before any HTTP call, then execute on approval. Point each
  `<KIND>_BASE_URL` at the cus
## June 2026 additions (SLG-parity uplift + GTM & deployment)
- **Governance deepened to SLG parity:** added `governance/accessibility/` (WCAG 2.1 AA / ADA Title II
  pre-flight on AI-generated content), `governance/fairness/disparate_impact.py` (four-fifths screen for
  at-risk flag/rank workflows), `governance/controls/control_mappings.py` (obligation → platform/AWS
  control map), `governance/evals/` (structural golden-artifact harness), and a **consequential
  bright-line test** (`tests/test_consequential_bright_line.py`) asserting no agent can execute an
  irreversible commit without human approval. All governance + gateway tests pass
  (`docs/AWS-DEPLOYMENT-VALIDATION.md`).
- **Step-by-step AWS deployment runbooks:** `docs/AWS-DEPLOYMENT-REFERENCE.md` (master shared path —
  CloudFront/WAF → Cognito/JWT → app → S3 WORM + KMS CMK + DynamoDB audit) and one
  `runb
## June 2026 — security & candor hardening pass
Following an external CISO-style review (validated against the code in `docs/PRODUCTION-READINESS-ACTION-PLAN.md`):
- **Closed two real bypasses in code:** `verify_jwt` now rejects unverified claims dicts outside demo mode (`platform_core/edu_agent_platform/auth.py`), and consequential approvals are signed, transaction-bound (agent/user/tool/args), single-use, and expiring (`mcp_gateway/approvals.py`) — proven by `test_auth.py` + `test_approvals.py` (46 tests passed at the time of this pass; the full `make test` suite is 120 tests green as of 2026-07-07).
- **Hardened IaC:** Bedrock IAM scoped to model ARNs; MFA/callback/egress/WORM-retention parameterized; audit-immutability defense-in-depth documented.
- **Hardened CI:** cfn-lint is blocking; added bandit, pip-audit, detect-secrets, checkov, SBOM, and Dependabot.
- **Corrected messaging** across README + 19 docs (no "compliant with law" / "PII never egresses VPC" / AgentCore-"deployed" overclaims), added a seller disclaimer and root `SECURITY.md`.
- **Remaining work** (golden path, AgentCore provisioner, record-level authz, Cedar/Verified Permissions, customer assurance package) is staged with verification steps in `docs/PRODUCTION-READINESS-ACTION-PLAN.md`.

## June 2026 — golden path (Agent 01) scaffolding landed
The first golden-path build (Agent 01) is in-repo and verified (59 tests passed at the time of this pass; the full `make test` suite is **120 tests green as of 2026-07-07**; 9 CFN templates parse):
- **Record-level authorization** (`policy.record_scope_ok` + gateway): a student/guardian reaches only their own/linked record, even on an entitled tool.
- **Durable single-use approval store** (`mcp_gateway/approval_store.py`): in-memory default + DynamoDB conditional-write impl so a signed approval executes exactly once cluster-wide.
- **Edge** (`infra/cloudformation/edge.yaml`: CloudFront + WAFv2 + ACM + security headers) and **observability** (`observability.yaml`: alarms + dashboard + SNS).
- **AgentCore provisioner** (`infra/lambdas/agentcore_provisioner/`: custom-resource Lambda, fails closed, 7 unit tests) wired via quickstart service-token params.
- **One-command** `make golden-path-01` + the end-to-end `runbooks/agent-deploy/01-GOLDEN-PATH.md`.
Remaining golden-path work (live IdP federation, real SIS/LMS connector, ephemeral-account CI deploy) is customer-engagement scope — tracked in `docs/PRODUCTION-READINESS-ACTION-PLAN.md`.
