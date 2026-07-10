# Release Packet — EDU (K-12 & Higher Education)

*What ships with a tagged release, so a customer, an assessor, or an AWS reviewer gets a repeatable
evidence bundle — not just source. A release packet is assembled per version into `release/<version>/`.
Reference accelerator — see [`NOT-CLAIMS.md`](NOT-CLAIMS.md); this is evidence, not a certification.*

## Versioning (two numbers)

- **AGP (governance contract):** **1.0** — the controls in [`AGP-CONFORMANCE.md`](AGP-CONFORMANCE.md).
- **Implementation package (`edu-agent-platform`):** semantic version, moves with code (may change without an AGP change).

A release records both. A CISO reviews AGP once; each release shows the implementation still conforms.

## What a release packet contains

| Artifact | What it proves | Produced by |
|---|---|---|
| **Test report** | The offline suite passes (no API key, no AWS) | `pytest -q` |
| **SAST (bandit)** | No high-severity code security findings | `bandit -r platform_core governance -ll` |
| **Dependency audit (pip-audit)** | No known-vulnerable dependencies; audited against the pinned lockfile (`platform_core/requirements-lock.txt`) — **BLOCKING** in CI (no silent fallback: a missing lockfile or a CVE fails the job) | `pip-audit -r platform_core/requirements-lock.txt` |
| **IaC lint/scan (cfn-lint, checkov)** | CloudFormation is valid; no high IaC misconfigurations | `cfn-lint`, `checkov -d infra` |
| **SBOM (CycloneDX)** | A complete software bill of materials for supply-chain review | `cyclonedx-py` |
| **Clean-account deploy report** | The golden path deployed, ran, and tore down in a clean account | `evidence/CLEAN-ACCOUNT-ACCEPTANCE.md` |
| **Negative-demo result** | The platform refuses the 10 deny cases | `demo/negative_demo.py` (hero) |
| **Known limitations** | An honest scope statement | hero `ASSURANCE-PACKET.md` §Known limitations, `NOT-CLAIMS.md` |
| **Upgrade notes** | What changed and any migration steps | `CHANGELOG.md` (+ AGP migration notes) |

The CI **supply-chain** job already runs gitleaks (secret scan), bandit, pip-audit, checkov, Terraform
validate, CycloneDX SBOM, and Trivy on every push — a release packet is the pinned, collected snapshot
of those for a version.

## How to assemble one

```bash
# from the portfolio root (tools install in CI; missing tools are recorded as SKIPPED)
tools/build_release_packet.sh <path-to-this-repo> 1.0.0
# -> writes release/1.0.0/ with MANIFEST.md + the artifacts above
```

## Upgrade notes

Each release appends to [`CHANGELOG.md`](CHANGELOG.md). If a release adopts a new **AGP** version, the
migration note lives in the Aegis versioning doc (`docs/14-GOVERNANCE-PATTERN-VERSIONING.md`) and is
referenced here. Package-only releases (no AGP change) note code changes and any config/env deltas.

> A release packet is **evidence for a specific commit**, not a promise of production-readiness. The
> customer still owns validation, IdP integration, production connectors, and operations
> (see [`OPERATING-MODEL.md`](OPERATING-MODEL.md)).
