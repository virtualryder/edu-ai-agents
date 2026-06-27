"""
MCP authorization policy — the heart of the AgentCore Gateway decision.

It is **deny-by-default** and enforces **least privilege as an intersection**:
a tool call is permitted only if BOTH the calling agent is granted the tool AND
the acting user is entitled to it. An agent can never do more than the human on
whose behalf it acts — even if the agent's own grant list is broader.

  permitted(tool) ⇔ tool ∈ AGENT_TOOL_GRANTS[agent] ∩ ⋃ ROLE_ENTITLEMENTS[user_roles]

CONSEQUENTIAL (high-risk) tools additionally require human approval before
execution. Routine reads and *low-risk workflow* writes (open a draft, create an
advising case, schedule an appointment, file an IT ticket) do not — that is the
bounded-agent model: the agent may initiate low-risk workflows but must escalate
consequential ones to a named, authorized human.

The CONSEQUENTIAL set encodes the EDU bright line: an agent never autonomously
posts a final grade, changes an enrollment record, sends a sensitive
determination/outreach, or runs a privileged IT remediation — those bind a
verified human approver into the record before execution.

In production these tables are expressed as Amazon Bedrock AgentCore Gateway
targets + AgentCore Identity scopes (or API Gateway + Lambda authorizer + STS +
Cognito + Cedar/OPA, or a self-built FastMCP server) fed by the institution's
IdP; here they are explicit Python so the model is testable and the intersection
semantics are unambiguous. Tool names ("<connector_kind>.<operation>") map 1:1 to
AgentCore Gateway target names.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, Iterable, List, Tuple

# ── Tool registry: tool name -> (connector_kind, method, consequential) ───────
# consequential=True => requires a human-approval gate before execution.
TOOL_REGISTRY: Dict[str, Tuple[str, str, bool]] = {
    # ── Student Information System (SIS) ──────────────────────────────────────
    "sis.get_student_profile":        ("sis", "get_student_profile", False),
    "sis.get_schedule":               ("sis", "get_schedule", False),
    "sis.check_application_status":   ("sis", "check_application_status", False),
    "sis.get_attendance":             ("sis", "get_attendance", False),
    "sis.get_grades":                 ("sis", "get_grades", False),
    "sis.get_graduation_requirements": ("sis", "get_graduation_requirements", False),
    "sis.get_transfer_credits":       ("sis", "get_transfer_credits", False),
    "sis.update_enrollment_record":   ("sis", "update_enrollment_record", True),   # consequential
    # ── CRM / advising / scheduling ───────────────────────────────────────────
    "crm.get_case":                   ("crm", "get_case", False),
    "crm.create_advising_case":       ("crm", "create_advising_case", False),       # low-risk workflow
    "crm.schedule_appointment":       ("crm", "schedule_appointment", False),       # low-risk workflow
    # ── Knowledge base (approved institutional content) ───────────────────────
    "kb.search_policies":             ("kb", "search_policies", False),
    "kb.search_course_material":      ("kb", "search_course_material", False),
    # ── Communications ────────────────────────────────────────────────────────
    "comms.draft_message":            ("comms", "draft_message", False),            # draft only
    "comms.send_message":             ("comms", "send_message", True),              # consequential (family/student outreach)
    # ── Learning Management System (LMS) ──────────────────────────────────────
    "lms.get_roster":                 ("lms", "get_roster", False),
    "lms.get_course_content":         ("lms", "get_course_content", False),
    "lms.get_assignments":            ("lms", "get_assignments", False),
    "lms.get_engagement":             ("lms", "get_engagement", False),
    "lms.identify_missing_submissions": ("lms", "identify_missing_submissions", False),
    "lms.create_assignment_draft":    ("lms", "create_assignment_draft", False),    # draft only
    "lms.create_rubric_draft":        ("lms", "create_rubric_draft", False),        # draft only
    "lms.post_announcement_draft":    ("lms", "post_announcement_draft", False),     # draft only
    "lms.update_assignment_due_date": ("lms", "update_assignment_due_date", True),   # consequential (affects a learner)
    "lms.publish_content":            ("lms", "publish_content", True),             # consequential (to students)
    # ── Assessment ────────────────────────────────────────────────────────────
    "assessment.evaluate_rubric":     ("assessment", "evaluate_rubric", False),     # analysis only
    "assessment.draft_feedback":      ("assessment", "draft_feedback", False),
    "assessment.summarize_class_patterns": ("assessment", "summarize_class_patterns", False),
    "assessment.release_grade":       ("assessment", "release_grade", True),        # consequential — bright line
    # ── Student-success analytics ─────────────────────────────────────────────
    "analytics.get_risk_signals":     ("analytics", "get_risk_signals", False),
    "analytics.get_intervention_history": ("analytics", "get_intervention_history", False),
    # ── Degree / pathway rules + labor market ─────────────────────────────────
    "rules.run_degree_audit":         ("rules", "run_degree_audit", False),
    "rules.check_prerequisites":      ("rules", "check_prerequisites", False),
    "labor.get_career_pathways":      ("labor", "get_career_pathways", False),
    # ── Document pipeline / accessibility ─────────────────────────────────────
    "docpipe.classify_document":      ("docpipe", "classify_document", False),
    "docpipe.extract_fields":         ("docpipe", "extract_fields", False),
    "docpipe.validate_completeness":  ("docpipe", "validate_completeness", False),
    "docpipe.transform_accessible":   ("docpipe", "transform_accessible", False),
    "docpipe.translate_content":      ("docpipe", "translate_content", False),
    # ── IT service management (ITSM) ──────────────────────────────────────────
    "itsm.get_ticket":                ("itsm", "get_ticket", False),
    "itsm.create_ticket":             ("itsm", "create_ticket", False),             # low-risk workflow
    "itsm.run_diagnostic":            ("itsm", "run_diagnostic", False),
    "itsm.reset_password":            ("itsm", "reset_password", True),             # consequential (privileged)
    "itsm.restart_service":           ("itsm", "restart_service", True),           # consequential (privileged)
    # ── Staff admin / ERP (HR / finance / procurement / facilities) ───────────
    "erp.search_policy":              ("erp", "search_policy", False),
    "erp.draft_document":             ("erp", "draft_document", False),
    "erp.initiate_approval":          ("erp", "initiate_approval", True),          # consequential (financial/procurement)
}

CONSEQUENTIAL_TOOLS: FrozenSet[str] = frozenset(
    t for t, (_, _, c) in TOOL_REGISTRY.items() if c
)

# ── What each AGENT is allowed to call (its job description as code) ───────────
AGENT_TOOL_GRANTS: Dict[str, FrozenSet[str]] = {
    "01-student-family-concierge": frozenset({
        "sis.get_student_profile", "sis.get_schedule", "sis.check_application_status",
        "kb.search_policies", "crm.get_case", "crm.create_advising_case",
        "crm.schedule_appointment", "comms.draft_message", "comms.send_message",
    }),
    "02-tutor-study-companion": frozenset({
        "kb.search_course_material", "lms.get_course_content", "lms.get_assignments",
    }),
    "03-educator-copilot": frozenset({
        "lms.get_roster", "lms.get_course_content", "lms.get_assignments",
        "lms.get_engagement", "lms.identify_missing_submissions", "kb.search_course_material",
        "lms.create_assignment_draft", "lms.create_rubric_draft", "lms.post_announcement_draft",
        "lms.update_assignment_due_date", "lms.publish_content",
    }),
    "04-assessment-grading-feedback": frozenset({
        "lms.get_assignments", "assessment.evaluate_rubric", "assessment.draft_feedback",
        "assessment.summarize_class_patterns", "assessment.release_grade",
    }),
    "05-student-success-engagement": frozenset({
        "analytics.get_risk_signals", "analytics.get_intervention_history",
        "sis.get_attendance", "sis.get_grades", "lms.get_engagement",
        "crm.create_advising_case", "comms.draft_message", "comms.send_message",
    }),
    "06-pathway-navigator": frozenset({
        "sis.get_student_profile", "sis.get_graduation_requirements", "sis.get_transfer_credits",
        "rules.run_degree_audit", "rules.check_prerequisites", "labor.get_career_pathways",
        "kb.search_policies", "crm.schedule_appointment",
    }),
    "07-document-accessibility-services": frozenset({
        "docpipe.classify_document", "docpipe.extract_fields", "docpipe.validate_completeness",
        "docpipe.transform_accessible", "docpipe.translate_content",
        "sis.update_enrollment_record", "comms.draft_message",
    }),
    "08-operations-service-desk": frozenset({
        "itsm.get_ticket", "itsm.create_ticket", "itsm.run_diagnostic",
        "itsm.reset_password", "itsm.restart_service",
        "erp.search_policy", "erp.draft_document", "erp.initiate_approval",
        "kb.search_policies",
    }),
}

# ── What each USER ROLE is entitled to (the human's real permissions) ─────────
# Roles derive from IdP group membership (see auth.py). The intersection with the
# agent grant is what actually executes — so a STUDENT driving the Concierge can
# only ever reach the read/low-risk tools a student is entitled to, never a
# registrar's enrollment write, even though the agent is granted more.
ROLE_ENTITLEMENTS: Dict[str, FrozenSet[str]] = {
    "STUDENT": frozenset({
        "sis.get_student_profile", "sis.get_schedule", "sis.check_application_status",
        "sis.get_grades", "sis.get_graduation_requirements", "sis.get_transfer_credits",
        "kb.search_policies", "kb.search_course_material", "lms.get_course_content",
        "lms.get_assignments", "crm.schedule_appointment", "crm.create_advising_case",
        "rules.run_degree_audit", "rules.check_prerequisites", "labor.get_career_pathways",
        "docpipe.transform_accessible", "docpipe.translate_content",
        "itsm.get_ticket", "itsm.create_ticket", "comms.draft_message",
    }),
    # Guardian: a scoped subset. Where FERPA rights have transferred (age 18 /
    # postsecondary), auth.py / the gateway drops the guardian's entitlements.
    "GUARDIAN": frozenset({
        "sis.get_student_profile", "sis.get_schedule", "sis.check_application_status",
        "sis.get_attendance", "kb.search_policies", "crm.schedule_appointment",
        "docpipe.translate_content", "comms.draft_message", "itsm.create_ticket",
    }),
    "EDUCATOR": frozenset({
        "lms.get_roster", "lms.get_course_content", "lms.get_assignments", "lms.get_engagement",
        "lms.identify_missing_submissions", "kb.search_course_material",
        "lms.create_assignment_draft", "lms.create_rubric_draft", "lms.post_announcement_draft",
        "lms.update_assignment_due_date", "lms.publish_content",
        "assessment.evaluate_rubric", "assessment.draft_feedback",
        "assessment.summarize_class_patterns", "assessment.release_grade",
        "sis.get_grades", "sis.get_attendance", "analytics.get_risk_signals",
        "comms.draft_message",
    }),
    "COUNSELOR": frozenset({
        "analytics.get_risk_signals", "analytics.get_intervention_history",
        "sis.get_attendance", "sis.get_grades", "sis.get_student_profile",
        "sis.get_graduation_requirements", "sis.get_transfer_credits",
        "crm.create_advising_case", "crm.schedule_appointment", "crm.get_case",
        "comms.draft_message", "comms.send_message",
        "rules.run_degree_audit", "rules.check_prerequisites", "labor.get_career_pathways",
        "kb.search_policies",
    }),
    "REGISTRAR": frozenset({
        "sis.get_student_profile", "sis.get_schedule", "sis.get_grades",
        "sis.get_graduation_requirements", "sis.get_transfer_credits",
        "sis.update_enrollment_record", "crm.get_case",
        "docpipe.classify_document", "docpipe.extract_fields", "docpipe.validate_completeness",
    }),
    "FINANCIAL_AID": frozenset({
        "sis.check_application_status", "sis.get_student_profile", "crm.get_case",
        "crm.create_advising_case", "comms.draft_message", "comms.send_message",
        "kb.search_policies",
    }),
    "ENROLLMENT_STAFF": frozenset({
        "docpipe.classify_document", "docpipe.extract_fields", "docpipe.validate_completeness",
        "docpipe.transform_accessible", "docpipe.translate_content",
        "sis.update_enrollment_record", "comms.draft_message", "kb.search_policies",
    }),
    "ADMINISTRATOR": frozenset({
        "sis.get_student_profile", "sis.get_schedule", "sis.check_application_status",
        "analytics.get_risk_signals", "analytics.get_intervention_history",
        "crm.get_case", "crm.create_advising_case", "comms.draft_message", "comms.send_message",
        "kb.search_policies", "erp.search_policy",
    }),
    "IT_STAFF": frozenset({
        "itsm.get_ticket", "itsm.create_ticket", "itsm.run_diagnostic", "kb.search_policies",
    }),
    "IT_ADMIN": frozenset({  # IT staff + the privileged remediations
        "itsm.get_ticket", "itsm.create_ticket", "itsm.run_diagnostic",
        "itsm.reset_password", "itsm.restart_service", "kb.search_policies",
    }),
    "STAFF": frozenset({
        "erp.search_policy", "erp.draft_document", "kb.search_policies", "itsm.create_ticket",
    }),
    "STAFF_APPROVER": frozenset({  # staff + financial/procurement approval authority
        "erp.search_policy", "erp.draft_document", "erp.initiate_approval",
        "kb.search_policies", "itsm.create_ticket",
    }),
}


@dataclass
class PolicyDecision:
    allowed: bool
    tool: str
    reason: str
    requires_approval: bool = False
    connector_kind: str = ""
    method: str = ""
    effective_scope: List[str] = field(default_factory=list)  # exactly this tool


def user_entitlements(roles: Iterable[str]) -> FrozenSet[str]:
    out: set = set()
    for r in roles:
        out |= ROLE_ENTITLEMENTS.get(r, frozenset())
    return frozenset(out)


def decide(agent_id: str, user_roles: Iterable[str], tool: str) -> PolicyDecision:
    """Deny-by-default authorization with least-privilege intersection."""
    if tool not in TOOL_REGISTRY:
        return PolicyDecision(False, tool, f"unknown tool {tool!r}")

    connector_kind, method, consequential = TOOL_REGISTRY[tool]
    agent_grants = AGENT_TOOL_GRANTS.get(agent_id, frozenset())
    if tool not in agent_grants:
        return PolicyDecision(
            False, tool,
            f"agent {agent_id!r} is not granted {tool!r} (agent over-reach denied)",
            connector_kind=connector_kind, method=method,
        )

    ent = user_entitlements(user_roles)
    if tool not in ent:
        return PolicyDecision(
            False, tool,
            f"acting user (roles={list(user_roles)}) is not entitled to {tool!r} "
            f"(an agent may never exceed the user's own permissions)",
            connector_kind=connector_kind, method=method,
        )

    return PolicyDecision(
        True, tool,
        "permitted by agent grant ∩ user entitlement",
        requires_approval=tool in CONSEQUENTIAL_TOOLS,
        connector_kind=connector_kind, method=method,
        effective_scope=[tool],
    )


# ── end of policy.py ──────────────────────────────────────────────────────────
# Authorization model summary (deny-by-default, least-privilege intersection):
#   permitted(tool) ⇔ tool ∈ AGENT_TOOL_GRANTS[agent] ∩ ROLE_ENTITLEMENTS[roles]
# Consequential tools additionally require a verified human approval at runtime.
# See mcp_gateway/gateway.py for enforcement and audit.py for the trail.


# ── Record-level authorization ────────────────────────────────────────────────
# Authorization above answers "may this agent+user call this tool?". It does NOT
# answer "may this user reach THIS student's record?". RECORD_SCOPED_TOOLS operate
# on one identifiable student; a self-scoped principal (a student, or a guardian)
# may only target their own — or, for a guardian, an explicitly linked — student.
# Staff roles operate at institutional scope here; a customer narrows that to
# assigned students/sections by populating an entitlement claim (see docs).
RECORD_SCOPED_TOOLS: FrozenSet[str] = frozenset({
    "sis.get_student_profile", "sis.get_schedule", "sis.check_application_status",
    "sis.get_attendance", "sis.get_grades", "sis.get_graduation_requirements",
    "sis.get_transfer_credits", "sis.update_enrollment_record", "crm.get_case",
})
_RECORD_ARG_KEYS = ("student_id", "record_id", "student", "sid", "case_student_id")
_SELF_SCOPED_ROLES: FrozenSet[str] = frozenset({"STUDENT", "GUARDIAN"})


def _target_record_id(args: Dict[str, object]) -> str:
    for k in _RECORD_ARG_KEYS:
        v = (args or {}).get(k)
        if v:
            return str(v)
    return ""


def record_scope_ok(user_roles: Iterable[str], claims: Dict[str, object],
                    tool: str, args: Dict[str, object]) -> Tuple[bool, str]:
    """
    Return (ok, reason). Enforces that a self-scoped principal can only reach their
    own / linked student record on a record-scoped tool. Open (ok=True) for tools
    that aren't record-scoped or calls that name no specific record.
    """
    if tool not in RECORD_SCOPED_TOOLS:
        return True, "not record-scoped"
    target = _target_record_id(args or {})
    if not target:
        return True, "no explicit record target"
    roleset = set(user_roles)
    if roleset - _SELF_SCOPED_ROLES:  # any staff role -> institutional scope
        return True, "staff institutional scope"
    own = str(claims.get("student_id") or claims.get("sub") or "")
    linked = {str(s) for s in (claims.get("students") or [])}
    if target in ({own} | linked):
        return True, "record owner / linked"
    return False, (f"record-scope: principal may not access record {target!r} "
                   f"(self-scoped to own/linked records)")
