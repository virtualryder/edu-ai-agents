"""
The EDU bright line, enforced in code.

EDU agents are *bounded*: they may retrieve, analyze, draft, recommend, and
initiate low-risk workflows, but they must never autonomously COMMIT a
consequential, system-of-record action. This suite encodes that as a gateway
invariant rather than a documentation promise:

  1. Every irreversible "final commit" tool is registered consequential, so the
     authorization gateway will ALWAYS demand a named human approver before it
     executes — there is no agent/role combination that can commit one outright.
  2. Any consequential tool an agent is granted resolves, when permitted, to an
     ALLOW-with-approval decision (requires_approval=True) — the agent can hand a
     human the action, never take it.

This is defense-in-depth: even a mis-scoped human role cannot let the agent skip
the gate, because the requirement to approve is bound to the tool, not the role.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "platform_core"))

from edu_agent_platform.mcp_gateway.policy import (
    AGENT_TOOL_GRANTS,
    CONSEQUENTIAL_TOOLS,
    ROLE_ENTITLEMENTS,
    TOOL_REGISTRY,
    decide,
)

# The irreversible system-of-record commits an agent must never make alone.
BRIGHT_LINE_COMMITS = {
    "assessment.release_grade",        # posting a final grade
    "sis.update_enrollment_record",    # a registrar commit
    "erp.initiate_approval",           # a financial / procurement commit
    "lms.publish_content",             # publishing to students
    "lms.update_assignment_due_date",  # changing a deadline that affects learners
    "comms.send_message",              # student / family outreach
    "itsm.reset_password",             # privileged remediation
    "itsm.restart_service",            # privileged remediation
}


def test_bright_line_commits_are_registered_consequential():
    for tool in BRIGHT_LINE_COMMITS:
        assert tool in TOOL_REGISTRY, f"{tool} missing from the tool registry"
        assert tool in CONSEQUENTIAL_TOOLS, (
            f"{tool} is a final commit but is not flagged consequential — "
            f"the gateway would let an agent execute it without a human gate"
        )


def test_no_agent_can_commit_a_consequential_action_without_approval():
    for agent_id, grants in AGENT_TOOL_GRANTS.items():
        for tool in grants:
            if tool not in CONSEQUENTIAL_TOOLS:
                continue
            roles = [r for r, ent in ROLE_ENTITLEMENTS.items() if tool in ent]
            assert roles, f"no role is entitled to consequential tool {tool!r}"
            d = decide(agent_id, [roles[0]], tool)
            assert d.allowed and d.requires_approval, (
                f"{agent_id} can execute consequential tool {tool!r} "
                f"without an approval gate"
            )


def test_every_granted_consequential_tool_appears_in_the_bright_line():
    """No agent is granted a consequential tool we have not consciously gated."""
    granted_consequential = {
        t for grants in AGENT_TOOL_GRANTS.values() for t in grants if t in CONSEQUENTIAL_TOOLS
    }
    undocumented = granted_consequential - BRIGHT_LINE_COMMITS
    assert not undocumented, (
        f"consequential tools granted to an agent but not in BRIGHT_LINE_COMMITS: {undocumented}"
    )
