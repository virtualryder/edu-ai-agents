# Suite Status

**Phase:** Foundation + Demonstrated/Deployable-by-design.

## Maturity
Documented + **Demonstrated** (runs end-to-end in `EXTRACT_MODE=demo`, no API key) + **Deployable-by-design**
(CloudFormation + Terraform, AgentCore container contract). Production-readiness (CSV, IdP integration,
live connectors, WCAG 2.2 AA conformance, penetration test) is the engagement.

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
  `<KIND>_BASE_URL` at the customer gateway to hit real systems with no code change.
- **Canvas / LMS LTI 1.3 reference** (`aws-native-reference/_shared/canvas_lti/`): maps an LTI launch's
  roles + age signals to gateway identity (`custom:edu_role`, FERPA rights-transfer, COPPA under-13),
  with a reference launch handler and role-mapping tests — the Layer-1 bridge for LMS-embedded agents.
- **CI** (`.github/workflows/ci.yml`): platform+governance tests, each agent per-process, LTI tests,
  prompt-manifest drift check, compile-all, and cfn-lint — matrixed on Python 3.11/3.12, no secrets.
- **AWS deployment**: CloudFormation (6 templates, validated) + Terraform parity; AgentCore Runtime
  container server (`/invocations` + `/ping`, ARM64) — smoke-tested locally; `Makefile` entrypoints.
- **Field & GTM**: positioning, MCP-layer explainer (+ 3 gateway options), six-layer architecture,
  compliance spine, 8 offerings docs, 13 stakeholder briefings, runbooks, deployment handbook.
- **Executive collateral**: `EDU-Agentic-AI-Suite-Executive-Overview.pptx` (+ PDF) and `EDU-One-Pager.pptx` (+ PDF).

## Test evidence (no API key, fixtures)
- `platform_core/tests` + `governance/tests`: **26 passed** (gateway intersection, HITL enforcement across
  all agents, masking, grounding, red team, fairness, prompt-manifest).
- 8 agent graph suites (run per-agent — each ships an identically-named `agent` package), incl. live-path
  tests over real HTTP for 01/04/05: 01:8 - 02:5 - 03:5 - 04:7 - 05:8 - 06:4 - 07:4 - 08:6 = **47 passed**.
- Canvas LTI role-mapping: **7 passed**. Suite total green: **80 tests** (26 + 47 + 7), no API key.
- AgentCore container: `/ping` healthy, `/invocations` runs an agent end-to-end with full audit trail.
- `make test` runs platform+governance once, then each agent in its own process; CI mirrors this.

## Marquee proof points (web-verified)
UA-Pulaski Tech (94.5% adoption / +253% admissions engagement), Highline College (75% reduction),
UT Austin UT Sage (Bedrock stack), Illinois Tech (4-6 weeks to ~1 day).

## Next
- Extend the live-connector path to the higher-governance agents (04, 05) and a live LMS (Canvas LTI) reference.
- Per-agent tailored handbook PDFs; 5-slide customer teaser.
- CI workflow wiring (`make test` + `prompt_registry --update` drift check).
