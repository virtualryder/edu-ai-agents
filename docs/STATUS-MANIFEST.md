# Status Manifest — EDU AI Agent Suite

*Single source of truth for maturity. Last reconciled: June 2026.*

> **This file is authoritative.** The status tables and maturity statements in `README.md`,
> `SUITE-STATUS.md`, the per-agent `README.md` files, and `docs/AWS-DEPLOYMENT-VALIDATION.md`
> all **derive from this manifest**. If any other document disagrees with the matrix below,
> this file is correct and the other document is stale — fix it here first, then reconcile downstream.

## How to read this

Each row is an agent (01–08) or the **shared platform** (the controls every agent inherits:
LLM factory, PII masker, MCP authorization gateway, approvals, connectors, governance spine, IaC).
Each column is a capability the second external review asked us to state honestly. A cell answers a
single question: *has this capability been demonstrated for this row, with evidence in the repo, as
of this pass?* A **Yes** means there is code and a passing test, a shipped template, or a documented
artifact you can point at **right now** — not a plan to build it. A **No** means it is genuinely not
done here and is customer/engagement-owned (it does not mean it is impossible — it means we are not
claiming it). The bias is deliberately conservative: when in doubt, the cell says **No**. The honest
backlog (clean-account AWS deploy, real-model invocation, production identity, live connectors,
accessibility conformance, penetration test, production sign-off) is therefore mostly **No**, and
that is the correct, defensible posture for a **governed reference accelerator** — not a certified,
production-deployed product.

## Legend

| Symbol | Meaning |
|---|---|
| **Yes** | Done in-repo with evidence (code + passing test, shipped template, or completed artifact). |
| **No** | Not done here; customer/engagement-owned. Honest gap, not a hidden one. |
| **Partial** | Mechanism exists and is tested, but only on a subset (noted) or with a stand-in, not end-to-end in a customer environment. |
| **fixture** | Connector runs against deterministic local fixtures (no external system). |
| **fixture + live(local)** | Also has a local-HTTP "live" path: the agent runs end-to-end over real HTTP through the gateway against a local stand-in service of record (`CONNECTOR_MODE=live`). Not a real SIS/LMS. |

## Capability matrix

Columns: **Arch** = Architecture documented · **Unit** = Unit tested · **LocalInt** = Local integration tested ·
**AWSDeploy** = AWS deployment tested (clean account) · **RealModel** = Real model invoked · **Conn** = Connector mode ·
**ProdId** = Production identity tested · **Approval** = Signed approval tested · **Audit** = Immutable audit integrated (deployed) ·
**A11y** = Accessibility tested (conformance) · **Sec** = Security reviewed · **ProdOK** = Production approved.

| Row | Arch | Unit | LocalInt | AWSDeploy | RealModel | Conn | ProdId | Approval | Audit | A11y | Sec | ProdOK |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Shared platform** | Yes | Yes | Yes | No | No | fixture + live(local) | No | Yes | No | No | Partial | No |
| **01 — Student & Family Concierge** | Yes | Yes | Yes | No | No | fixture + live(local) | No | Yes | No | No | Partial | No |
| **02 — Tutor & Study Companion** | Yes | Yes | Partial | No | No | fixture | No | Yes | No | No | No | No |
| **03 — Educator Copilot** | Yes | Yes | Partial | No | No | fixture | No | Yes | No | No | No | No |
| **04 — Assessment, Grading & Feedback** | Yes | Yes | Yes | No | No | fixture + live(local) | No | Yes | No | No | No | No |
| **05 — Student Success & Engagement** | Yes | Yes | Yes | No | No | fixture + live(local) | No | Yes | No | No | No | No |
| **06 — Pathway Navigator** | Yes | Yes | Partial | No | No | fixture | No | Yes | No | No | No | No |
| **07 — Document & Accessibility Services** | Yes | Yes | Partial | No | No | fixture | No | Yes | No | No | No | No |
| **08 — Operations / IT Service Desk** | Yes | Yes | Partial | No | No | fixture | No | Yes | No | No | No | No |

### Column notes (why these answers)

- **Arch = Yes (all):** every agent has architecture, workflow, tool grants, and compliance design written and reviewed; the shared six-layer platform is documented in `docs/SUITE-ARCHITECTURE.md` and `docs/WHY-THE-MCP-LAYER.md`.
- **Unit = Yes (all):** the platform and governance suites pass (`platform_core/tests`, `governance/tests`, `infra/lambdas/agentcore_provisioner`) — 74 tests pass (as of 2026-07-07) via `python -m pytest platform_core/tests governance/tests infra/lambdas/agentcore_provisioner -q --ignore=governance/tests/test_hitl_gates.py`; the full `make test` suite (platform + governance + all 8 agents) is 120 tests green. Each agent additionally ships a `tests/` suite.
- **LocalInt = Yes** for the platform and **01/04/05** (they have `demo/demo_live.py` + `tests/test_live_path.py` running the agent end-to-end over real HTTP through the gateway). **Partial** for 02/03/06/07/08: they run end-to-end in `EXTRACT_MODE=demo` against fixtures and have test suites, but no local-HTTP live path yet.
- **AWSDeploy = No (all):** no independently-proven deploy in a clean AWS account. Templates parse and lint (`docs/AWS-DEPLOYMENT-VALIDATION.md`), and Agent 01 has a one-command `make golden-path-01` path, but a verified clean-account stand-up is **Gap 1** in the second review — customer/engagement-owned.
- **RealModel = No (all):** tests and demos use deterministic fixtures and a demo-aware generator. Inference auto-selects Bedrock → Anthropic → demo, but no real-model invocation is asserted in-repo.
- **Conn:** **fixture + live(local)** for the platform and **01/04/05** (local stand-in service of record over real HTTP, `CONNECTOR_MODE=live`); **fixture** for the rest. No row has a real SIS/LMS/ERP/CRM/ITSM connector.
- **ProdId = No (all):** `verify_jwt` is hardened to reject unverified claims outside demo mode (`platform_core/edu_agent_platform/auth.py`), but a real IdP federation (Cognito ↔ Okta/Entra/Google, MFA, group-sourced roles) has not been stood up or tested here. **Gap 5 / P3.**
- **Approval = Yes (all):** consequential actions use transaction-bound, signed, single-use, expiring approvals (`mcp_gateway/approvals.py`, `approval_store.py`); separation of duties (requestor ≠ approver) is enforced for enrollment/financial commits (`gateway._separation_ok` + `policy.SEPARATION_REQUIRED_TOOLS`). Tested in `test_approvals.py`, `test_gateway_hardening.py`. This is a platform control every agent inherits — hence Yes on every row.
- **Audit = No (all):** the gateway emits a PII-masked append-only audit and the data-plane template provisions WORM S3 + append-only DynamoDB, but **one integrated end-to-end audit deployment** (audit written from a deployed agent to deployed immutable storage and verified) has not been done. **Gap 6.** The mechanism is tested in-process; the *deployed integration* is the gap.
- **A11y = No (all):** a deterministic WCAG pre-flight ships in `governance/accessibility/`, and the conformance *plan* exists (`docs/assurance/ACCESSIBILITY-CONFORMANCE-PLAN.md`), but formal WCAG 2.x conformance testing (axe-core + manual screen-reader + PDF/UA) has not been performed. Customer-owned.
- **Sec = Partial (platform/01) / No (others):** the platform and the Agent 01 golden path went through the CISO-style review and remediation captured in `docs/PRODUCTION-READINESS-ACTION-PLAN.md` and `docs/SECOND-REVIEW-ACTION-PLAN.md` (two real bypasses closed, IaC/CI hardened, four code gaps closed this pass, threat model + IAM matrix landed). That is a **Partial** — an internal review, **not** an independent penetration test, which remains open for every row.
- **ProdOK = No (all):** nothing here is production-approved. Production requires customer security/privacy review, IdP integration, live connectors, accessibility conformance, a penetration test, and institutional sign-off.

## Bottom line

**The shared platform controls are built and unit-tested, and the Agent 01 golden-path scaffolding is
demonstrated locally (with 01/04/05 exercising a live-HTTP connector path) — but no agent is
AWS-deployed in a clean account, invokes a real model, uses production identity, or is
production-approved; those remain customer/engagement work.** In maturity-ladder terms: **Documented +
Demonstrated** across all eight agents, **Deployable-by-design** (templates parse; Agent 01 has a
one-command path), and **not yet Production-ready** anywhere.

## Where each downstream document must agree

| Document | Must say |
|---|---|
| `README.md` (Maturity & Roadmap) | Platform controls built+tested; Agent 01 golden-path scaffolding demonstrated; AWS-deploy/production = customer work. |
| `SUITE-STATUS.md` | 8 agents to Demonstrated depth; 01/04/05 live-HTTP path; **no** AWS-deployed claim. |
| Per-agent `README.md` (01–08) | Demonstrated locally; **not** AWS-deployed; not "not yet runnable." |
| `docs/AWS-DEPLOYMENT-VALIDATION.md` | Templates parse/lint; edge.yaml + observability.yaml now ship as templates but remain un-deployed-as-tested. |

*See also: [`docs/SECOND-REVIEW-ACTION-PLAN.md`](SECOND-REVIEW-ACTION-PLAN.md) (gap-by-gap status) and [`docs/PRODUCTION-READINESS-ACTION-PLAN.md`](PRODUCTION-READINESS-ACTION-PLAN.md) (full P0–P4 register).*

## Platform capability update (June 2026)

| Capability | Status | Evidence |
|---|---|---|
| End-to-end "one complete path" (identity → gateway → scoped token → connector → signed single-use approval → result → masked append-only audit) | **Demonstrated in-repo (Agent 01)** | `01-student-family-concierge/demo/golden_transaction.py` + `tests/test_end_to_end.py`; evidence bundle at `demo/evidence/golden_transaction_evidence.json` |
| Production HITL reviewer (authenticate → entitlement → exact action → separation of duties → signed single-use approval → replay rejected → audit) | **Reference service + UI built** | `platform_core/edu_agent_platform/reviewer/` + `platform_core/tests/test_reviewer.py` (5 tests); `reviewer/app.py` (Streamlit) |
| Clean-account AWS deploy of the above (live AgentCore endpoint, real IdP) | **Customer-engagement (open)** | `make golden-path-01` + `runbooks/agent-deploy/01-GOLDEN-PATH.md` |

| Unified one-shot deploy (regional app + us-east-1 edge in one command) | **Target ships** | `scripts/deploy_full.sh` + `make deploy-all-01`; verified `bash -n` / `make -n` / templates parse |
| Reviewer ↔ Step Functions `waitForTaskToken` resume (SendTaskSuccess/Failure) | **Built + tested** | `reviewer/review_service.py` (`StepFunctionsTaskCallback`); `platform_core/tests/test_reviewer.py` |
