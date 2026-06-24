"""
Compliance control mappings — which platform control satisfies which obligation.

Each entry ties an education regulatory regime to the concrete platform/AWS
control that addresses it, plus the maturity (Implemented / Configurable /
Customer). A CISO or privacy officer reads this to see why the architecture is
defensible; a solution architect reads it to know what they must still configure
per customer. Authoritative sources are tracked in docs/ and gtm/EDU-DECK-SOURCES.md.

  * Implemented  — the control exists in this repo's code/IaC and is tested.
  * Configurable — the control is supported by the architecture but must be wired
                   to the customer's accounts, IdP, connectors, or data.
  * Customer     — the obligation is owned by the institution (policy, consent,
                   data-governance) and the platform only provides evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class ControlMapping:
    regime: str
    obligation: str
    platform_control: str
    aws_service: str
    status: str  # Implemented | Configurable | Customer


MAPPINGS: List[ControlMapping] = [
    ControlMapping(
        "FERPA (20 U.S.C. 1232g)", "Protect personally identifiable information in education records; vendor acts under 'school official / direct control'",
        "Deny-by-default gateway (agent-grant ∩ user-entitlement); security-trimmed retrieval; student-PII masking at the audit boundary; tamper-evident access logging",
        "AgentCore Gateway/Identity + Bedrock Knowledge Bases ACL propagation + DynamoDB append-only + CloudTrail", "Configurable"),
    ControlMapping(
        "COPPA (children under 13)", "Heightened protection and verifiable parental consent for under-13 learners",
        "Heightened masking for minors; guardian-role entitlements; consent gating before family outreach; no secondary use",
        "Gateway policy + masker + KMS CMK", "Configurable"),
    ControlMapping(
        "PPRA", "Restrict collection/disclosure of protected survey and personal information",
        "Purpose-bound tool scopes; no collection outside granted tools; audit of every access",
        "Gateway policy + CloudTrail", "Configurable"),
    ControlMapping(
        "IDEA / Section 504", "Protect special-education records (IEP / 504 accommodations); humans own eligibility and placement",
        "Least-privilege access to accommodation data; masking; bright-line — agent drafts, a named human decides eligibility/placement (HITL gate)",
        "Gateway + masker + Step Functions HITL", "Configurable"),
    ControlMapping(
        "ADA Title II / Section 508 / WCAG 2.1 AA", "Accessible web/mobile and document output (AI-generated content in scope; deadlines 2027/2028)",
        "Accessibility pre-flight on generated content (alt text, heading order, link purpose, plain-language grade); accessible-format transformation in Agent 07",
        "governance/accessibility + CI (axe-core target) + Textract/Translate/Polly", "Implemented"),
    ControlMapping(
        "GLBA Safeguards Rule (financial aid data)", "Safeguard student financial information handled under Title IV",
        "Encryption in transit/at rest; least-privilege; masking of financial identifiers; access logging",
        "KMS CMK + Gateway + S3 Object Lock", "Configurable"),
    ControlMapping(
        "State student-privacy laws (e.g., SOPIPA, NY Ed Law §2-d)", "Limit vendor use of student data; deletion; security; transparency",
        "No secondary use of student data; data-class isolation; deletion/retention config; full audit of agent actions",
        "Gateway + DynamoDB audit + S3 lifecycle/retention", "Configurable"),
    ControlMapping(
        "Title VI / OCR (disparate impact)", "Education programs must not produce unjustified disparate impact on protected groups",
        "Four-fifths disparate-impact screen and representativeness check on any flag/rank workflow; outcomes routed to human equity review; no automated adverse action",
        "governance/fairness + HITL gate", "Implemented"),
    ControlMapping(
        "NIST AI RMF 1.0", "Govern / Map / Measure / Manage AI risk",
        "Grounding verification; hash-pinned prompt registry; structural evals; red-team scenarios; fairness screens; framework-enforced HITL gates",
        "governance/* + CloudWatch", "Implemented"),
    ControlMapping(
        "Records retention & auditability", "Retain records and AI decision traces; support legal hold and tamper-evidence",
        "Append-only audit (deny Update/Delete); WORM finalized snapshots; prompt/trace capture; retention configuration",
        "DynamoDB append-only + S3 Object Lock (COMPLIANCE mode)", "Configurable"),
    ControlMapping(
        "PCI DSS (tuition / meal-account payments)", "Protect cardholder data",
        "Card masking (Luhn); no card data in prompts or audit; tokenized payment connector",
        "Gateway + masker + payment provider", "Configurable"),
]


def by_regime(regime: str) -> List[ControlMapping]:
    return [m for m in MAPPINGS if m.regime.lower().startswith(regime.lower())]
