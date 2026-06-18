# Canvas / LMS LTI 1.3 Reference

> How an **LTI 1.3 / LTI Advantage** launch from Canvas (or Blackboard, Schoology, Moodle, D2L)
> becomes the verified identity the MCP gateway authorizes against — so an LMS-embedded agent
> (02 Tutor, 03 Educator Copilot, or any course panel) inherits exactly the launching user's role
> and never more. This is the Layer-1 (Experience) bridge in `docs/SUITE-ARCHITECTURE.md`.

## Why LTI 1.3 (not a bolted-on login)

Agents surface **inside the LMS the user already lives in**. LTI 1.3 is the institution-approved
interoperability standard: the LMS (the "platform") performs an OIDC-based, signed launch into your
tool, carrying the user's identity, course context, and roles in a signed `id_token` (JWT). That JWT
is the trustworthy identity — we map it to `acting_user_claims` and hand it to the same governed
gateway path every other surface uses. No separate password, no shadow user store.

## The launch flow

```
Canvas (Platform)                         This tool (LTI Tool)                 MCP Gateway / Agent
─────────────────                         ────────────────────                ───────────────────
1. user clicks the tool in a course
2. OIDC login init  ───────────────────▶  GET /login (iss, login_hint,
                                             target_link_uri)
3. ◀── redirect to platform auth ───────  redirect with state + nonce
4. POST id_token (signed JWT)  ─────────▶  POST /launch
                                           validate: JWKS signature, iss/aud,
                                             exp/iat, nonce (replay protection)
                                           claims_from_launch(id_token)  ─────▶ acting_user_claims
                                           build_graph().invoke(seed) ────────▶ gateway authorizes
                                                                                 (deny-by-default +
                                                                                  human gate) → agent
```

## Role mapping (`lti_launch.py`)

LTI role URIs → EDU gateway roles, most-privileged-wins when a launch carries several:

| LTI role | Gateway role |
|---|---|
| `…membership#Instructor` / `TeachingAssistant` / `ContentDeveloper` | `EDUCATOR` |
| `…membership#Learner` / institution `Student` | `STUDENT` |
| `…membership#Mentor` | `GUARDIAN` |
| institution / system `Administrator` | `ADMINISTRATOR` |
| institution `Staff` | `STAFF` |

Unknown/empty roles default to **STUDENT** (least privilege). The mapped role flows into
`custom:edu_role`, which the gateway reads for its deny-by-default least-privilege intersection — so a
Learner launch into the Educator Copilot can read course material but **cannot** release a grade or
publish content, exactly as policy dictates.

## EDU age signals carry through the launch

FERPA rights-transfer and COPPA are honored from the LMS launch: if the platform sends LTI **custom
claims** `under_13` or `rights_transferred`, `claims_from_launch` propagates them. The gateway then
drops the `GUARDIAN` role when `rights_transferred` is true, and the model layer applies heightened
Guardrails for `under_13`. Configure these as custom variables in the LMS tool registration.

## Try it (dev, no platform keys)

```bash
# Role-mapping + claim-construction tests (no agent stack needed)
python -m pytest aws-native-reference/_shared/canvas_lti/test_lti_roles.py -q

# Decode a launch token WITHOUT signature verification for local dev only:
export LTI_DEV=1   # NEVER in production
python -c "from lti_launch import launch_to_agent; ..."   # see launch_to_agent()
```

## Production checklist

- Register the tool in Canvas Developer Keys (LTI 1.3): set the OIDC login URL (`/login`), the
  redirect/launch URL (`/launch`), and the public JWKS URL for your tool.
- **Validate every launch**: JWKS signature (RS256), `iss`/`aud`, `exp`/`iat`, and a stored `nonce`
  (replay protection) — `decode_id_token(..., jwks_url=, audience=)` with PyJWT[crypto]; never enable
  `LTI_DEV` in production.
- Persist `state`/`nonce` server-side (the in-memory reference set is illustrative only).
- Front `/login` + `/launch` with the institution's gateway; keep the agent invocation on the governed
  path so authorization, the human gate, and the audit trail apply.
- Map LMS custom variables for `under_13` / `rights_transferred` at tool registration.
- Meet WCAG 2.2 AA in the embedded panel (Layer-1 requirement).

## Files

- `lti_launch.py` — role mapping, claim construction, id_token decode/validate, `launch_to_agent()`,
  and a dependency-free WSGI reference handler (`/login`, `/launch`).
- `test_lti_roles.py` — role-mapping, age-signal, dev-decode, and gateway-integration tests.
