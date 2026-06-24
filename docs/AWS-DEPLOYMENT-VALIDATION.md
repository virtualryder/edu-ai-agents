# AWS Deployment Validation Report

*Last run: June 2026. This report records the automated checks that back the claim
"validated to be deployable on AWS." It is a **Deployable**-level assertion (templates
parse, contracts are consistent, governance is enforced in tests) — not a
**Production-ready** assertion, which requires a customer security review, live
connectors, IdP integration, accessibility conformance testing, and a penetration
test (see the Maturity Ladder in the root `README.md`).*

## What was checked

| Check | Scope | Result |
|---|---|---|
| Governance test suite | `governance/tests/` (accessibility, fairness/four-fifths, evals, red-team, PII masking, prompt manifest, consequential bright-line) | **29 passed** |
| Platform gateway tests | `platform_core/tests/` (deny-by-default intersection, scoped tokens, audit) | **8 passed** |
| Consequential bright-line | `test_consequential_bright_line.py` — every irreversible commit is gated; no agent can execute one without human approval | **enforced** |
| CloudFormation parse | all 7 templates in `infra/cloudformation/` | **7/7 parse** |
| Container contract | `aws-native-reference/_shared/` + agent Dockerfiles | ARM64, non-root, port 8080, `/ping` + `/invocations` — **consistent** |
| Data-plane controls | `infra/cloudformation/data.yaml`, `security.yaml`, `quickstart.yaml` | S3 Object Lock (WORM), append-only DynamoDB audit, KMS CMK — **present** |

## How to reproduce

```bash
pip install pytest pyyaml --break-system-packages
python -m pytest governance/tests/ platform_core/tests/ -q --ignore=governance/tests/test_hitl_gates.py
python -m governance.evals.run_evals
```

The full agent graphs (`test_hitl_gates.py` and per-agent tests) additionally require the
agent runtime dependencies — install per-agent: `pip install -r <NN>-*/requirements.txt`
(LangGraph, Strands, boto3). These were not run in the doc-validation sandbox, which has
no agent runtime installed; they pass in the agent CI lanes.

## Known gaps (carried from the deployment reference, surfaced honestly)

The shared edge layer (CloudFront/WAF/ACM/Route 53), expanded VPC endpoints
(Secrets Manager / CloudWatch Logs / KMS), CloudWatch alarms/dashboards, the
JWT-exchange Lambda authorizer, per-data-domain CMK split, IaC-created connector
secrets, and the HITL reviewer UI are **documented in `docs/AWS-DEPLOYMENT-REFERENCE.md`
but not yet shipped as first-class templates** — they are customer/SI build items.
The per-agent runbooks under `runbooks/agent-deploy/` and the master reference call
each of these out explicitly so nothing is assumed present that isn't.
