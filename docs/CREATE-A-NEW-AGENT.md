# Create a New Agent
### How to author a new bounded, governed agent in the EDU suite — end to end

> This is the developer runbook for adding a 9th (or Nth) agent. It complements
> `docs/DEPLOYMENT-HANDBOOK.md` (which deploys an existing agent to AWS). Every agent
> inherits the shared platform — the MCP gateway, student-PII masking, grounding,
> the HITL framework, and the audit trail — so authoring one is mostly: declare what
> systems it may touch, write its LangGraph workflow, and wire its tools through the
> gateway. The four invariants in `CONTRIBUTING.md` must hold.

Use Agent 01 (`01-student-family-concierge/`) as the reference implementation throughout.

---

## 0. Decide the agent's contract first

Answer these before writing code — they drive everything else:

1. **What systems of record does it touch?** (SIS, LMS, CRM, ITSM, ERP, analytics, docpipe, …)
2. **Which tools (operations) does it call**, and which are **reads / low-risk writes / consequential**?
   Consequential = the bright line: anything that posts a grade, changes enrollment, sends a sensitive
   message, or runs a privileged remediation. Those are human-gated.
3. **Which user role(s) drive it?** (student, guardian, educator, counselor, registrar, …)
4. **What is its workflow?** Map it to the standard node flow:
   `intake → (retrieval/analysis) → draft/analyze → checks → routing_decision → human_review_gate → finalize`.

---

## 1. Register the agent's tools and grants (the governance contract)

Edit `platform_core/edu_agent_platform/mcp_gateway/policy.py`:

1. **Add any new tools** to `TOOL_REGISTRY` as `"kind.operation": ("kind", "operation", consequential_bool)`.
   `consequential=True` means the human-approval gate fires before execution. Reuse existing tools where you can.
2. **Add the agent's grant set** to `AGENT_TOOL_GRANTS` under your new agent id (use the folder name,
   e.g. `"09-attendance-concierge"`). List only the tools it needs (least privilege).
3. **Ensure the driving role is entitled** to those tools in `ROLE_ENTITLEMENTS`. The gateway permits a
   call only if it is in **both** the agent grant **and** the user's role entitlement
   (`permitted ⇔ agent_grant ∩ role_entitlement`). If a new role is needed, add it (and map it in the IdP
   per the deployment handbook).
4. If you added a connector **kind**, add it to `_KNOWN_KINDS` in
   `platform_core/edu_agent_platform/connectors/factory.py` and add fixture responses for each new
   `kind.operation` in `connectors/fixtures.py` (this is what makes the demo + tests run offline).

> The platform's gateway/policy tests (`platform_core/tests/test_gateway.py`) exercise the intersection;
> add a case if your agent introduces a notable new consequential tool.

---

## 2. Scaffold the agent directory

Create `NN-your-agent/` mirroring Agent 01:

```
NN-your-agent/
├── agent/
│   ├── __init__.py
│   ├── state.py          # TypedDict(total=False): acting_user_claims, recommended_action,
│   │                     #   revision_count, messages, current_step, completed_steps, errors,
│   │                     #   audit_trail, approval, action_request + your fields; a RecommendedAction enum
│   ├── prompts.py        # SYSTEM_PROMPT + register(agent_id, name, v=1, text=...) per prompt
│   ├── nodes.py          # intake, retrieval/analysis, draft/analyze, checks, routing_decision,
│   │                     #   human_review_gate, finalize — each appends an audit entry
│   ├── graph.py          # build_graph(use_memory=True); HUMAN_GATE_NODE="human_review_gate";
│   │                     #   interrupt_before=[HUMAN_GATE_NODE] when use_memory
│   └── persistence.py    # copy verbatim from Agent 01 (MemorySaver / PostgresSaver)
├── tools/
│   ├── __init__.py
│   └── gateway_tools.py  # AGENT_ID = folder name; MCPGateway(); _invoke wrapper.
│                         #   read tools return res.result; consequential tools take approval=
├── data/
│   ├── __init__.py
│   └── fixtures/{__init__.py, sample_requests.json}
├── app.py                # Streamlit demo (copy Agent 01, retitle)
├── requirements.txt      # copy Agent 01, retitle
├── Dockerfile            # copy Agent 01, retitle
├── .env.example          # copy Agent 01, retitle
└── tests/
    ├── __init__.py
    └── test_graph.py
```

### The conventions that make tests (and the platform) work

- **`build_graph(use_memory=True)` must compile with `interrupt_before=[HUMAN_GATE_NODE]`** where
  `HUMAN_GATE_NODE = "human_review_gate"`. This is the framework-enforced HITL gate.
- **`routing_decision` is a pure read** of `state["recommended_action"]` (set inside the `checks` node);
  never mutate state in the path function. Bounded revision loops back to the draft node **at most once**.
- **All system-of-record access goes through `tools/gateway_tools.py`**, which calls the MCP gateway —
  never a vendor SDK or DB directly. Reads return `res.result`; consequential tools accept an `approval`
  kwarg and must not execute without it.
- **Draft text via the demo-aware helper**: `from edu_agent_platform.generation import generate` with a
  deterministic `demo_fn` built only from state (keeps it grounded and runnable with no API key).
- **Ground every learner/family-facing draft**: `from governance.grounding import verify_grounding` in
  `checks`; route ungrounded output to a bounded revision or escalate.
- **Every node appends an audit entry**; `finalize` binds the `approval` for consequential tools.

---

## 3. Register prompts in the manifest (model change-control)

Prompts are hash-pinned. After writing `agent/prompts.py` (each prompt wrapped in
`register(agent_id, name, v=1, text=...)`), regenerate the manifest:

```bash
python -m governance.prompt_registry --update      # writes governance/prompt_manifest.json
```

CI (`.github/workflows/ci.yml`) fails if a registered prompt changes without a manifest bump.

---

## 4. Write the test suite

`tests/test_graph.py` should assert (copy Agent 01's and adapt the seed to your state):

- An end-to-end run (`build_graph(use_memory=False).invoke(seed)`) populates the draft/analysis output,
  `completed_steps`, and `audit_trail`.
- `recommended_action` is a valid enum value.
- `build_graph(use_memory=True)` **interrupts before `HUMAN_GATE_NODE`**
  (`get_state(cfg).next == (HUMAN_GATE_NODE,)`, cfg `{"configurable":{"thread_id":"t-1"}}`).
- Any consequential tool does **not** execute without an approval, and does execute with a bound one.

Run it (each agent runs in its own process — agents share the package name `agent`):

```bash
PYTHONPATH=platform_core:. EXTRACT_MODE=demo CONNECTOR_MODE=fixture \
  python -m pytest NN-your-agent/tests -q -p no:cacheprovider
```

The cross-cutting HITL test (`governance/tests/test_hitl_gates.py`) auto-discovers every `NN-*/agent`
folder, so your new agent is included automatically — run it to confirm the gate can't be bypassed.

---

## 5. (Optional) Author docs and a live path

- Add the four per-agent docs under `NN-your-agent/docs/` (README + aws-deployment-guide + integration-guide
  + edu-compliance + roi-analysis) — mirror an existing agent.
- For a live demo, add `demo/` (reference_service.py + demo_live.py + DEMO-LIVE.md) and
  `tests/test_live_path.py`, mirroring Agent 01 / 04 / 05.

---

## 6. Build and deploy the new agent on AWS

The new agent inherits the entire deployment path — no new infrastructure is required:

```bash
# prove the runtime artifact locally (no cloud)
scripts/local_smoke.sh NN-your-agent

# container path: build ARM64 image -> ECR, then deploy the governed stack
IMAGE=$(scripts/build_and_push_image.sh --agent NN-your-agent --region us-east-1 \
        | sed -n 's/^ContainerImageUri=//p')
scripts/deploy.sh --env prod --agent-id NN-short --mode container \
  --template-bucket my-cfn-bucket --idp-metadata https://idp/.../metadata \
  --image "$IMAGE" --region us-east-1
```

Then complete the deployment-handbook steps that are agent-specific: **register the new agent's
AgentCore Gateway targets** (one per system of record it uses, Step "Register AgentCore Gateway
targets"), **store its connector secrets**, run the **smoke test**, and the **HITL walkthrough**.

---

## 7. Checklist before you call it done

- [ ] Tools + grants + role entitlements added to `policy.py`; intersection is least-privilege.
- [ ] New connector kinds/methods added to `factory.py` + `fixtures.py` (demo runs offline).
- [ ] `build_graph` interrupts before `human_review_gate`; `routing_decision` is a pure read.
- [ ] All SoR access flows through `gateway_tools.py`; consequential tools require approval.
- [ ] Prompts registered; `prompt_manifest.json` regenerated; CI drift check passes.
- [ ] `tests/test_graph.py` green; `governance/tests/test_hitl_gates.py` green (auto-includes the agent).
- [ ] `scripts/local_smoke.sh NN-your-agent` returns SMOKE OK.
- [ ] The bright line holds: the agent never autonomously decides a grade, admission, discipline,
      financial-aid award, special-ed eligibility, or placement.
```
