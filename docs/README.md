# Documentation Index — EDU AI Agent Suite

*The map of every document in this repository, grouped by who reads it. New here? Start at the top.*

> **Maturity is governed by one file:** [`STATUS-MANIFEST.md`](STATUS-MANIFEST.md). Every status table
> and maturity statement elsewhere derives from it. If two docs disagree, the manifest is correct.

## Start here

| Document | What it is |
|---|---|
| [`../README.md`](../README.md) | Project overview, quick start, the eight agents, stakeholder positioning, step-by-step AWS deploy, maturity ladder. |
| [`STATUS-MANIFEST.md`](STATUS-MANIFEST.md) | **Authoritative** per-agent / per-control capability matrix. The single source of truth for maturity. |
| [`../SUITE-STATUS.md`](../SUITE-STATUS.md) | State + changelog: what is built and verified, the live-connector reference path, recent hardening passes. |
| [`../SOLUTION-FIELD-GUIDE.md`](../SOLUTION-FIELD-GUIDE.md) | SI/SA qualification and adoption path. |
| [`FAQ.md`](FAQ.md) | Common questions from CIOs, CISOs, and architects. |

## Architecture

| Document | What it is |
|---|---|
| [`SUITE-ARCHITECTURE.md`](SUITE-ARCHITECTURE.md) | The shared six-layer platform and per-agent graphs. |
| [`WHY-THE-MCP-LAYER.md`](WHY-THE-MCP-LAYER.md) | Why a deny-by-default MCP authorization gateway sits between agents and tools. |
| [`AWS-DEPLOYMENT-REFERENCE.md`](AWS-DEPLOYMENT-REFERENCE.md) | Master deploy path: request-flow walkthrough, architecture diagram, control mapping. |
| [`WELL-ARCHITECTED-GENAI-LENS.md`](WELL-ARCHITECTED-GENAI-LENS.md) | The suite against the AWS Well-Architected GenAI lens. |
| [`../ENTERPRISE-PLATFORM.md`](../ENTERPRISE-PLATFORM.md) | The platform story — API modernization, the MCP gateway, governance spine. |

## Deploy

| Document | What it is |
|---|---|
| [`DEPLOYMENT-HANDBOOK.md`](DEPLOYMENT-HANDBOOK.md) | Console + CLI walkthrough from an empty AWS account to a running agent. |
| [`../runbooks/agent-deploy/01-GOLDEN-PATH.md`](../runbooks/agent-deploy/01-GOLDEN-PATH.md) | Copy-pasteable golden-path runbook for Agent 01 with verification at each step. |
| [`../runbooks/agent-deploy/`](../runbooks/agent-deploy/) | Per-agent deploy runbooks (01–08). |
| [`../runbooks/README.md`](../runbooks/README.md) | Runbook index (deploy + operations: DR, HITL queue, incident, model degradation). |
| [`AWS-DEPLOYMENT-VALIDATION.md`](AWS-DEPLOYMENT-VALIDATION.md) | What the automated deployability checks cover (templates parse/lint) — and what they do not. |
| [`AWS-FUNDING-AND-PREREQUISITES.md`](AWS-FUNDING-AND-PREREQUISITES.md) | Account, funding, and prerequisite setup. |
| [`CREATE-A-NEW-AGENT.md`](CREATE-A-NEW-AGENT.md) | How to scaffold a ninth agent on the shared platform. |
| [`../infra/lambdas/agentcore_provisioner/README.md`](../infra/lambdas/agentcore_provisioner/README.md) | AgentCore provisioner custom resource. |
| [`../infra/terraform/README.md`](../infra/terraform/README.md) | Terraform parity. |

## Governance

| Document | What it is |
|---|---|
| [`../governance/README.md`](../governance/README.md) | The EDU compliance spine: grounding, prompt registry, evals, fairness, red team, HITL gates. |
| [`SHARED-RESPONSIBILITY-MATRIX.md`](SHARED-RESPONSIBILITY-MATRIX.md) | Who owns what (Dev / Customer / AWS) across the control set. |
| Control mappings | `../governance/controls/control_mappings.py` — obligation → platform/AWS control map (FERPA, COPPA, IDEA/504, ADA Title II, GLBA, Title VI, NIST AI RMF). |

## Assurance

| Document | What it is |
|---|---|
| [`assurance/README.md`](assurance/README.md) | Index of the customer assurance package. |
| [`assurance/THREAT-MODEL.md`](assurance/THREAT-MODEL.md) | STRIDE threat model. |
| [`assurance/IAM-MATRIX.md`](assurance/IAM-MATRIX.md) | Entitlements computed from `policy.py`. |
| [`assurance/PRIVACY-IMPACT-ASSESSMENT-TEMPLATE.md`](assurance/PRIVACY-IMPACT-ASSESSMENT-TEMPLATE.md) | FERPA/COPPA PIA template. |
| [`assurance/ACCESSIBILITY-CONFORMANCE-PLAN.md`](assurance/ACCESSIBILITY-CONFORMANCE-PLAN.md) | WCAG 2.x conformance plan (pre-flight today; formal testing is customer-owned). |
| [`STAKEHOLDER-SECURITY-BRIEFINGS.md`](STAKEHOLDER-SECURITY-BRIEFINGS.md) | Briefings for CISO / privacy / board audiences. |

## Plans

| Document | What it is |
|---|---|
| [`PRODUCTION-READINESS-ACTION-PLAN.md`](PRODUCTION-READINESS-ACTION-PLAN.md) | The full honest gap register (P0–P4) and remediation roadmap. |
| [`SECOND-REVIEW-ACTION-PLAN.md`](SECOND-REVIEW-ACTION-PLAN.md) | The second-review delta: 10 gaps + 5 priorities mapped to status, files, and verification. |

## GTM / field

| Document | What it is |
|---|---|
| [`../gtm/BATTLECARD.md`](../gtm/BATTLECARD.md) | Competitive battlecard. |
| [`../gtm/DEMO-STORYBOARD.md`](../gtm/DEMO-STORYBOARD.md) | Demo narrative. |
| [`../gtm/SOW-TEMPLATE.md`](../gtm/SOW-TEMPLATE.md) | Statement-of-work template. |
| [`../gtm/TEASER-DECK.md`](../gtm/TEASER-DECK.md) · [`../gtm/DECK-CONTENT-SPEC.md`](../gtm/DECK-CONTENT-SPEC.md) · [`../gtm/EDU-DECK-SOURCES.md`](../gtm/EDU-DECK-SOURCES.md) | Deck content, spec, and sourced metrics. |
| [`../gtm/roi-calculator/README.md`](../gtm/roi-calculator/README.md) | ROI calculator. |
| [`../decks/README.md`](../decks/README.md) | The eight agent decks + suite overview (.pptx) and how they are built. |
| [`../offerings/`](../offerings/) | POC, pilot, managed-service, assessment offerings; competitive positioning; cost/ROI model; TPRM packet. |
| [`SA-SE-ENABLEMENT-GUIDE.md`](SA-SE-ENABLEMENT-GUIDE.md) | Solutions-architect / solutions-engineer enablement. |

## Security

| Document | What it is |
|---|---|
| [`../SECURITY.md`](../SECURITY.md) | Vulnerability-disclosure policy. |

## Per-agent docs

Each agent directory (`01-…` through `08-…`) contains its own `README.md`, plus `docs/`
(`aws-deployment-guide.md`, `edu-compliance.md`, `integration-guide.md`, `roi-analysis.md`).
Agents 01, 04, and 05 also carry a `demo/DEMO-LIVE.md` describing the local-HTTP live-connector path.
Per-agent maturity is governed by [`STATUS-MANIFEST.md`](STATUS-MANIFEST.md).
