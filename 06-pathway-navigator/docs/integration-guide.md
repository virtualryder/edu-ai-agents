# Pathway Navigator — Integration Guide
### Agent 06 — connectors, identity/role mapping, tools and grants, and the gateway flow

> **No agent calls a system of record directly.** The Navigator reads the SIS, the scheduling system, and the advising system only through gateway-authorized connectors, and every call carries the verified identity of the human on whose behalf the agent acts. This guide documents the connectors the Navigator binds to, how the five roles map to entitlements, which tools are read and which are write, and how a single call traverses the MCP authorization gateway. The platform-wide rationale is `../../docs/WHY-THE-MCP-LAYER.md`; the reference enforcement logic is `../../platform_core/edu_agent_platform/mcp_gateway/`.

---

## 1. Connectors and systems of record

The SIS remains the system of record for transcripts, program declarations, and academic standing; the advising system owns cases; the scheduling system owns appointments. The Navigator never holds credentials to any of them — it invokes the connector framework (`../../platform_core/edu_agent_platform/connectors/`) through the gateway.

| Connector | Backends (live) | Navigator usage |
|---|---|---|
| **SIS** | PowerSchool, Infinite Campus, Banner, Workday Student | Read transcript, program, catalog year, standing |
| **Scheduling** | Institution scheduling system | Read availability; write appointment booking |
| **Advising / case management** | Institution advising/case system | Write advising case; attach proposed plan |
| **Knowledge base** | Bedrock Knowledge Bases | Read grounded program, catalog, policy content |
| **Labor-market / RWD** | Governed data layer (Layer 4) | Read credential/career/labor-market data (no PII join) |
| **Rules engine** | Deterministic Lambda + Neptune/Aurora | Authoritative degree-audit, prerequisite, articulation logic |

The connector interface (`invoke(method, args)`) is identical in demo (deterministic JSON fixtures) and production (live APIs). The gateway does not know which backend is live, so authorization, masking, and audit behave the same in both modes.

---

## 2. Identity and role mapping

Identity is forwarded from the institution's own IdP (Okta / Entra / Google Workspace / AD via IAM Identity Center or Cognito) as verified claims, including role and — where relevant — guardian relationship and age-of-majority state. Authorization is **deny-by-default with least-privilege intersection**: `permitted(tool) ⇔ tool ∈ AGENT_TOOL_GRANTS[06-pathway-navigator] ∩ ROLE_ENTITLEMENTS[user_roles]`. The agent can never do more than the human it acts for.

| Role | What the Navigator may do | Scope / limits |
|---|---|---|
| **Student** | Explore options, run their own degree audit, check prerequisites, map their own transfer credit, explore careers, book a counselor appointment | Identity-scoped to the student's own record; writes gated |
| **Guardian** | The above on behalf of a minor student | Bounded by FERPA rights that transfer at 18 / postsecondary enrollment — guardian access drops to nothing the moment rights have transferred |
| **Educator** | Read a student's audit/program to support a conversation | Only for students in the educator's authorized relationship |
| **Counselor** | All read tools; create advising cases; attach proposed plans; **approve** plans at the HITL gate | The counselor is the named reviewer whose identity binds writes |
| **Administrator** | Aggregate/operational read; configuration | No access to an individual student's record beyond their authorized scope |

Guardian scoping is the FERPA-critical case: at 18 or postsecondary enrollment, rights transfer to the student, and the IdP role mapping carries that state so a guardian agent cannot surface records the parent no longer has a right to see.

---

## 3. Tools and grants — READ separated from WRITE

Read and write are separate tools with separate grants. The agent receives no direct database credentials and no unrestricted API access. Reads pass straight through the gateway; writes block at the HITL gate until a verified reviewer identity is bound into the record.

| Tool | Kind | Connector | Grant / gate |
|---|---|---|---|
| `sis.get_student_transcript` | **READ** | SIS | Identity-scoped; own record only |
| `sis.get_student_program` | **READ** | SIS | Identity-scoped |
| `rules.run_degree_audit` | **READ** (deterministic) | Rules engine | Authoritative; not the LLM |
| `rules.check_prerequisites` | **READ** (deterministic) | Rules engine | Authoritative; not the LLM |
| `rules.map_transfer_credit` | **READ** (deterministic) | Rules engine | Authoritative; not the LLM |
| `kb.search_program_policy` | **READ** | Knowledge base | Grounding-verified |
| `labor.get_career_pathway_data` | **READ** | RWD layer | Governed; no PII join |
| `scheduling.find_counselor_availability` | **READ** | Scheduling | Identity-scoped |
| `scheduling.book_counselor_appointment` | **WRITE** | Scheduling | **HITL gate** |
| `advising.create_advising_case` | **WRITE** | Advising | **HITL gate** |
| `advising.attach_proposed_plan` | **WRITE** | Advising | **HITL gate**; agent never marks a plan "approved" |

The rules-engine tools are reads in the authorization sense — they retrieve an authoritative determination — but they are **deterministic**, not LLM output. The LLM consumes their result to explain it; it never overrides it. This is how the option/recommendation/approved-plan distinction is kept honest: an "option" reflects what the rules engine says is possible, a "recommendation" adds the LLM's grounded suggestion with assumptions surfaced, and only a counselor's HITL approval converts an attached proposed plan into an approved plan.

---

## 4. Gateway flow — one call, end to end

Every tool call traverses the AgentCore Gateway in the same order, whether read or write:

1. **Identity verification** — verified IdP claims; deny on missing subject.
2. **Deny-by-default authorization with least-privilege intersection** — the tool must be in the Navigator's grants *and* the acting role's entitlements.
3. **Student-PII masking** — inbound results (e.g., a transcript) are masked to stable pseudonyms before entering a prompt or audit record.
4. **Human approval gate** — for the three write tools, the graph suspends (LangGraph `interrupt_before` / Step Functions `waitForTaskToken`) until a named counselor's reviewer identity is bound into the record; reads pass straight through.
5. **Short-lived scoped token** — minted per call via AgentCore Identity / STS; no standing service accounts.
6. **Connector invocation** — one validated connection per system.
7. **PII-masked append-only audit** — every attempt (ALLOW / DENY / PENDING_APPROVAL / ERROR) logged with lineage to the system of record, satisfying FERPA's recordkeeping of disclosures.

Reads (transcript retrieval, degree audit, prerequisite check, transfer mapping, career data) flow through steps 1–3, 5–7 without pausing. Only the consequential writes — booking a counselor, opening a case, attaching a proposed plan — pause at step 4. This is exactly the control academic leadership requires, and it is enforced by the framework, not by trusting the model. See `../../docs/WHY-THE-MCP-LAYER.md` and `docs`-adjacent `edu-compliance.md` for the bright-line and HITL detail.

---

**Maturity: Demonstrated locally — not AWS-deployed.** This agent runs end-to-end locally (demo mode + tests); a clean-account AWS deploy, real-model invocation, production identity, live connectors, and production sign-off remain customer/engagement work. Authoritative status: [`../../docs/STATUS-MANIFEST.md`](../../docs/STATUS-MANIFEST.md).
