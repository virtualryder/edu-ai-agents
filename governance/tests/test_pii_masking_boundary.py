"""student PII (FERPA) masking boundary proof (offline) — raw identifiers (SSN, email, phone) survive
NONE of the offline boundaries the agent writes to: the model prompt, and the audit record (which
feeds the DynamoDB audit table and the S3 Object-Lock evidence export). The masker is applied before
any model/audit write. The *runtime* capture (a real record in a deployed store + CloudWatch logs) is
the deploy-time proof — see the hero SECURITY-EVIDENCE-PACK.md and RUNTIME-EVIDENCE-RUNBOOK.md."""
import json

from edu_agent_platform.pii_masker import mask
from edu_agent_platform.mcp_gateway.audit import GatewayAuditLog

PII = "Contact SSN 123-45-6789, email jane.doe@example.com, phone (555) 123-4567."
RAW = ["123-45-6789", "jane.doe@example.com", "123-4567"]


def _assert_no_raw(text):
    leaked = [t for t in RAW if t in text]
    assert not leaked, f"raw regulated data leaked past the masker: {leaked}"


def test_masker_removes_common_identifiers():
    _assert_no_raw(mask(PII))


def test_prompt_boundary_is_masked():
    prompt = f"Draft a response strictly from this record:\n{mask(PII)}"
    _assert_no_raw(prompt)


def test_audit_boundary_is_masked():
    log = GatewayAuditLog()
    log.record({"decision": "ALLOW", "tool": "kb.search_policies",
                "args": {"note": PII, "from": "reply to jane.doe@example.com"}})
    _assert_no_raw(json.dumps(log.records[0]))


def test_masker_idempotent():
    once = mask(PII)
    assert mask(once) == once
