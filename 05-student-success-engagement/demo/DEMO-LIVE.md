# Agent 05 — Live-Path Demo Runbook

> Proves the Student Success & Engagement agent reaches a **system of record over real HTTP**,
> through the MCP authorization gateway, with the human-approval gate and audit intact — without
> requiring a live analytics lake / PowerSchool / Canvas / Slate / Amazon Connect during the demo.
> Flip one set of environment variables to point at the customer's real API gateway; **no agent code
> changes**.

This is the EDU analogue of the HCLS suite's live path. It exists so an account team can show "the
agent actually does the thing, safely" before any customer system is wired up.

> **PPRA note:** the agent assembles only authorized behavioral signals and never infers or conditions
> on protected categories. A consequential outreach send is human-gated by the gateway *before* any
> HTTP call. The agent never sends outreach autonomously.

---

## What runs

```
Engagement graph ─▶ tools/gateway_tools ─▶ MCP gateway ─▶ LiveHTTPConnector ─▶ HTTP endpoint
   (LangGraph)        (authorize +            (deny-by-default,     (real POST /method)   (reference
                       audit)                  human gate, token)                          service or
                                                                                           customer GW)
```

- **Connector mode:** `CONNECTOR_MODE=live`. The factory returns `LiveHTTPConnector` for any kind whose
  `<KIND>_BASE_URL` is set, which performs a real `POST <BASE_URL>/<method>` with the tool args.
- **Inference auto-selects:** Amazon Bedrock (`LLM_PROVIDER=bedrock`) → Anthropic (`ANTHROPIC_API_KEY`)
  → deterministic demo stub. The *live* part being proven is the governed connector path, not the model,
  so the demo runs end-to-end even with no model credentials.
- **The endpoint:** by default the bundled `reference_service.py` (synthetic data in the real system's
  shapes, with live-distinct ids like `CASE-live-0042` / `MSG-live-0009`). In production each
  `<KIND>_BASE_URL` points at the customer's API gateway.

---

## Quick start (one command, no credentials)

```bash
cd 05-student-success-engagement
pip install -r requirements.txt && pip install -e ../platform_core
python demo/demo_live.py
```

`demo_live.py` starts the reference service in-process, sets `CONNECTOR_MODE=live`, and runs two
scenarios:

1. **Read + low-risk workflow** — assemble authorized evidence + open an advising case. Executes over
   live HTTP; the assembled risk signals carry `served_by: reference_service` and the returned
   `case_id` (`CASE-live-0042`) originates from the service, proving the round-trip.
2. **Consequential action** — an outbound student/family outreach is **blocked at the gateway** (no HTTP
   call) until a verified COUNSELOR approval is bound, then executes over live HTTP (`MSG-live-0009`).

Every attempt is recorded in a PII-masked, append-only audit trail with live lineage.

### Run the reference service separately (two terminals)

```bash
# terminal 1
python demo/reference_service.py                 # listens on :8902  (set REFERENCE_API_TOKEN to require auth)
# terminal 2
REFERENCE_EXTERNAL=1 python demo/demo_live.py
```

---

## Point at real systems

Set live mode and the per-system base URLs to the customer's API gateway (one validated connection per
system). The gateway, authorization, human gate, and audit are unchanged.

```bash
export CONNECTOR_MODE=live
export ANALYTICS_BASE_URL=https://gw.example.edu/analytics  ANALYTICS_API_TOKEN=...
export SIS_BASE_URL=https://gw.example.edu/sis              SIS_API_TOKEN=...
export LMS_BASE_URL=https://gw.example.edu/lms              LMS_API_TOKEN=...
export CRM_BASE_URL=https://gw.example.edu/crm              CRM_API_TOKEN=...
export COMMS_BASE_URL=https://gw.example.edu/comms          COMMS_API_TOKEN=...
python demo/demo_live.py
```

The connector forwards `Authorization: Bearer <KIND>_API_TOKEN` for the reference path. In production,
the gateway's short-lived AgentCore Identity token is forwarded instead of a static token — see
`platform_core/edu_agent_platform/mcp_gateway/tokens.py` and `docs/WHY-THE-MCP-LAYER.md`.

### Bedrock (reached over PrivateLink; identifiers masked before inference)

```bash
export LLM_PROVIDER=bedrock
export BEDROCK_REGION=us-east-1
export BEDROCK_GUARDRAIL_ID=...          # REQUIRED in production
export BEDROCK_GUARDRAIL_VERSION=DRAFT
```

---

## Endpoint contract (for wiring a real gateway)

The `LiveHTTPConnector` calls, per tool the Engagement agent uses:

| Tool | HTTP call | Risk |
|---|---|---|
| `analytics.get_risk_signals` | `POST {ANALYTICS_BASE_URL}/get_risk_signals` | read |
| `analytics.get_intervention_history` | `POST {ANALYTICS_BASE_URL}/get_intervention_history` | read |
| `sis.get_attendance` | `POST {SIS_BASE_URL}/get_attendance` | read |
| `sis.get_grades` | `POST {SIS_BASE_URL}/get_grades` | read |
| `lms.get_engagement` | `POST {LMS_BASE_URL}/get_engagement` | read |
| `crm.create_advising_case` | `POST {CRM_BASE_URL}/create_advising_case` | low-risk write |
| `comms.draft_message` | `POST {COMMS_BASE_URL}/draft_message` | read / draft |
| `comms.send_message` | `POST {COMMS_BASE_URL}/send_message` | **consequential — human-gated** |

Each request body is the tool's JSON args; the response is the system's JSON, returned to the agent
unchanged. Map these onto the customer's real analytics / SIS / LMS / CRM / contact-center APIs in the
connector layer.

---

## Security talking points (say these in the room)

- **The gateway decides before anything leaves the building.** Authorization (deny-by-default,
  least-privilege intersection) and the human-approval gate run *before* any HTTP call. The blocked
  `send_message` in Scenario 2 makes zero network calls until a named counselor signs off.
- **No protected-category inference.** The agent assembles only authorized behavioral signals; it never
  infers or conditions on protected categories (PPRA), and aggregate equity monitoring is opt-in.
- **The agent never exceeds the human.** Swap the acting role away from `COUNSELOR` and the same send is
  denied — the agent inherits only the human's entitlements.
- **No standing credentials.** Each authorized call mints a short-lived, single-purpose token; nothing
  long-lived sits in the agent.
- **Every access is provable.** The audit trail records who acted, what tool, on what basis, who
  approved, and which system was reached — PII-masked — supporting FERPA / PPRA recordkeeping.
- **No lock-in.** This same path runs behind AgentCore Gateway, API Gateway + Lambda, or a self-built
  FastMCP server; the enforcement logic in `platform_core` is identical.

---

## Verify

```bash
# the live-path test starts the reference service and asserts a real HTTP round-trip
PYTHONPATH=../platform_core:.. python -m pytest tests/test_live_path.py -q
```
