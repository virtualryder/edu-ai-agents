# Agent 04 — Live-Path Demo Runbook

> Proves the Assessment, Grading & Feedback agent reaches a **system of record over real HTTP**,
> through the MCP authorization gateway, with the human-approval gate and audit intact — without
> requiring a live Canvas / Banner / assessment engine during the demo. Flip one set of environment
> variables to point at the customer's real API gateway; **no agent code changes**.

This is the EDU analogue of the HCLS suite's live path. It exists so an account team can show "the
agent actually does the thing, safely" before any customer system is wired up.

> **Bright line:** the educator owns the grade. The agent evaluates against the rubric and drafts
> feedback; releasing a final/high-stakes grade is a consequential action the gateway human-gates
> *before* any HTTP call. The agent never releases a grade autonomously.

---

## What runs

```
Grading graph ─▶ tools/gateway_tools ─▶ MCP gateway ─▶ LiveHTTPConnector ─▶ HTTP endpoint
   (LangGraph)        (authorize +          (deny-by-default,     (real POST /method)   (reference
                       audit)                human gate, token)                          service or
                                                                                         customer GW)
```

- **Connector mode:** `CONNECTOR_MODE=live`. The factory returns `LiveHTTPConnector` for any kind whose
  `<KIND>_BASE_URL` is set, which performs a real `POST <BASE_URL>/<method>` with the tool args.
- **Inference auto-selects:** Amazon Bedrock (`LLM_PROVIDER=bedrock`) → Anthropic (`ANTHROPIC_API_KEY`)
  → deterministic demo stub. The *live* part being proven is the governed connector path, not the model,
  so the demo runs end-to-end even with no model credentials.
- **The endpoint:** by default the bundled `reference_service.py` (synthetic data in the real system's
  shapes, with live-distinct ids like `GR-live-0001`). In production each `<KIND>_BASE_URL` points at
  the customer's API gateway.

---

## Quick start (one command, no credentials)

```bash
cd 04-assessment-grading-feedback
pip install -r requirements.txt && pip install -e ../platform_core
python demo/demo_live.py
```

`demo_live.py` starts the reference service in-process, sets `CONNECTOR_MODE=live`, and runs two
scenarios:

1. **Read / analysis workflow** — evaluate an essay against the rubric + draft feedback. Executes over
   live HTTP; the returned evaluation carries `served_by: reference_service` and a high confidence
   (~0.86), so the normal path is `APPROVE_DRAFT`, proving the round-trip.
2. **Consequential action** — releasing a final grade is **blocked at the gateway** (no HTTP call)
   until a verified EDUCATOR approval is bound, then executes over live HTTP (`GR-live-0001`).

Every attempt is recorded in a PII-masked, append-only audit trail with live lineage.

### Run the reference service separately (two terminals)

```bash
# terminal 1
python demo/reference_service.py                 # listens on :8901  (set REFERENCE_API_TOKEN to require auth)
# terminal 2
REFERENCE_EXTERNAL=1 python demo/demo_live.py
```

---

## Point at real systems

Set live mode and the per-system base URLs to the customer's API gateway (one validated connection per
system). The gateway, authorization, human gate, and audit are unchanged.

```bash
export CONNECTOR_MODE=live
export LMS_BASE_URL=https://gw.example.edu/lms              LMS_API_TOKEN=...
export ASSESSMENT_BASE_URL=https://gw.example.edu/assessment ASSESSMENT_API_TOKEN=...
python demo/demo_live.py
```

The connector forwards `Authorization: Bearer <KIND>_API_TOKEN` for the reference path. In production,
the gateway's short-lived AgentCore Identity token is forwarded instead of a static token — see
`platform_core/edu_agent_platform/mcp_gateway/tokens.py` and `docs/WHY-THE-MCP-LAYER.md`.

### Bedrock (in-account inference, no student-PII egress)

```bash
export LLM_PROVIDER=bedrock
export BEDROCK_REGION=us-east-1
export BEDROCK_GUARDRAIL_ID=...          # REQUIRED in production
export BEDROCK_GUARDRAIL_VERSION=DRAFT
```

---

## Endpoint contract (for wiring a real gateway)

The `LiveHTTPConnector` calls, per tool the Grading agent uses:

| Tool | HTTP call | Risk |
|---|---|---|
| `lms.get_assignments` | `POST {LMS_BASE_URL}/get_assignments` | read |
| `assessment.evaluate_rubric` | `POST {ASSESSMENT_BASE_URL}/evaluate_rubric` | read / analysis |
| `assessment.draft_feedback` | `POST {ASSESSMENT_BASE_URL}/draft_feedback` | read / analysis |
| `assessment.summarize_class_patterns` | `POST {ASSESSMENT_BASE_URL}/summarize_class_patterns` | read |
| `assessment.release_grade` | `POST {ASSESSMENT_BASE_URL}/release_grade` | **consequential — human-gated** |

Each request body is the tool's JSON args; the response is the system's JSON, returned to the agent
unchanged. Map these onto the customer's real LMS / assessment APIs in the connector layer.

---

## Security talking points (say these in the room)

- **The gateway decides before anything leaves the building.** Authorization (deny-by-default,
  least-privilege intersection) and the human-approval gate run *before* any HTTP call. The blocked
  `release_grade` in Scenario 2 makes zero network calls until a named educator signs off.
- **The educator owns the grade.** The agent scores against the rubric and drafts feedback; it never
  asserts or releases a final grade autonomously. Releasing requires a verified EDUCATOR approval.
- **The agent never exceeds the human.** Swap the acting role away from `EDUCATOR` and the release is
  denied — the agent inherits only the human's entitlements.
- **No standing credentials.** Each authorized call mints a short-lived, single-purpose token; nothing
  long-lived sits in the agent.
- **Every access is provable.** The audit trail records who acted, what tool, on what basis, who
  approved, and which system was reached — PII-masked — supporting FERPA / grade recordkeeping.
- **No lock-in.** This same path runs behind AgentCore Gateway, API Gateway + Lambda, or a self-built
  FastMCP server; the enforcement logic in `platform_core` is identical.

---

## Verify

```bash
# the live-path test starts the reference service and asserts a real HTTP round-trip
PYTHONPATH=../platform_core:.. python -m pytest tests/test_live_path.py -q
```
