"""
Fixture connectors — deterministic, offline backing store for every system.

These let the entire suite run with no AWS account, no vendor credentials, and no
real student data: demos, CI, and the governance eval harness all use these.
Returned shapes mirror the real systems closely enough that agent code is
identical in live mode. All values are synthetic.
"""
from __future__ import annotations

from typing import Any, Dict, List

from .base import GenericConnector


class FixtureGeneric(GenericConnector):
    """Backs every connector kind with canned, safe, synthetic responses."""

    _RESPONSES: Dict[str, Any] = {
        # ── SIS ───────────────────────────────────────────────────────────────
        "sis.get_student_profile": {
            "student_pseudonym": "STU-demo0001", "level": "undergraduate",
            "program": "AA Liberal Arts", "standing": "good", "credits_earned": 42,
        },
        "sis.get_schedule": {
            "term": "Fall 2026",
            "courses": [
                {"course": "ENG-101", "title": "Composition I", "days": "MWF", "time": "09:00"},
                {"course": "MAT-120", "title": "College Algebra", "days": "TR", "time": "11:00"},
            ],
        },
        "sis.check_application_status": {
            "application_pseudonym": "APP-demo0001", "status": "documents_incomplete",
            "missing": ["official transcript", "residency verification"],
            "explanation": "Two items are still needed before a decision can be made.",
        },
        "sis.get_attendance": {"term": "Fall 2026", "present_pct": 78.0, "absences": 9, "tardies": 3},
        "sis.get_grades": {
            "term": "Fall 2026",
            "grades": [{"course": "ENG-101", "grade": "B"}, {"course": "MAT-120", "grade": "C-"}],
            "gpa": 2.6,
        },
        "sis.get_graduation_requirements": {
            "program": "AA Liberal Arts", "total_required": 60, "completed": 42, "remaining": 18,
            "outstanding_areas": ["lab science (4)", "humanities elective (3)"],
        },
        "sis.get_transfer_credits": {
            "evaluated": True,
            "accepted": [{"source": "Prior College", "course": "HIS-105", "credits": 3}],
            "pending": [{"source": "Prior College", "course": "BIO-110", "credits": 4}],
        },
        "sis.update_enrollment_record": {"record_id": "ENR-DRAFT-0001", "status": "UPDATED", "written": True},
        # ── CRM / advising / scheduling ────────────────────────────────────────
        "crm.get_case": {"case_id": "CASE-0001", "type": "advising", "status": "open"},
        "crm.create_advising_case": {"case_id": "CASE-DRAFT-0001", "status": "OPEN", "created": True},
        "crm.schedule_appointment": {"appointment_id": "APPT-0001", "status": "BOOKED",
                                     "with": "advising", "slot": "next available"},
        # ── Knowledge base ─────────────────────────────────────────────────────
        "kb.search_policies": {
            "results": [
                {"title": "Registration & Add/Drop Policy", "ref": "POL-REG-002", "relevance": 0.93},
                {"title": "Financial Aid Satisfactory Academic Progress", "ref": "POL-FA-007", "relevance": 0.89},
            ]
        },
        "kb.search_course_material": {
            "results": [
                {"course": "MAT-120", "title": "Unit 3: Quadratic Functions", "ref": "MAT120-U3", "relevance": 0.95},
            ]
        },
        # ── Communications ─────────────────────────────────────────────────────
        "comms.draft_message": {"draft_id": "MSG-DRAFT-0001", "status": "DRAFT", "channel": "email"},
        "comms.send_message": {"message_id": "MSG-0001", "status": "SENT", "channel": "email"},
        # ── LMS ────────────────────────────────────────────────────────────────
        "lms.get_roster": {"course": "MAT-120", "section": "01", "enrolled": 28},
        "lms.get_course_content": {
            "course": "MAT-120",
            "modules": [{"id": "U3", "title": "Quadratic Functions", "items": 7}],
        },
        "lms.get_assignments": {
            "course": "MAT-120",
            "assignments": [{"id": "A5", "title": "Quadratics Problem Set", "due": "2026-10-02", "points": 20}],
        },
        "lms.get_engagement": {"course": "MAT-120", "last_login_days_ago": 6, "submissions_on_time_pct": 64.0},
        "lms.identify_missing_submissions": {"course": "MAT-120", "missing": [{"assignment": "A5", "count": 5}]},
        "lms.create_assignment_draft": {"assignment_id": "A-DRAFT-0001", "status": "DRAFT", "created": True},
        "lms.create_rubric_draft": {"rubric_id": "RUB-DRAFT-0001", "status": "DRAFT", "criteria": 4},
        "lms.post_announcement_draft": {"announcement_id": "ANN-DRAFT-0001", "status": "DRAFT"},
        "lms.update_assignment_due_date": {"assignment_id": "A5", "status": "UPDATED", "new_due": "2026-10-09"},
        "lms.publish_content": {"content_id": "U3", "status": "PUBLISHED", "published": True},
        # ── Assessment ─────────────────────────────────────────────────────────
        "assessment.evaluate_rubric": {
            "rubric_id": "RUB-101", "criteria_scores": [3, 4, 3, 2], "max_per_criterion": 4,
            "raw_total": 12, "max_total": 16, "confidence": 0.86,
        },
        "assessment.draft_feedback": {
            "feedback_id": "FB-DRAFT-0001", "status": "DRAFT",
            "summary": "Strong thesis; support the third claim with evidence from the text.",
        },
        "assessment.summarize_class_patterns": {
            "course": "MAT-120", "common_misconception": "sign errors when completing the square",
            "suggested_reteach_group": 5,
        },
        "assessment.release_grade": {"grade_id": "GR-0001", "status": "RELEASED", "released": True},
        # ── Analytics (student success) ────────────────────────────────────────
        "analytics.get_risk_signals": {
            "signals": [
                {"type": "attendance", "value": "78%", "severity": "moderate"},
                {"type": "lms_engagement", "value": "6 days since login", "severity": "moderate"},
                {"type": "missing_work", "value": "1 assignment", "severity": "low"},
            ],
            "composite": "watch",
        },
        "analytics.get_intervention_history": {
            "prior": [{"date": "2026-09-15", "type": "advisor outreach", "outcome": "no response"}],
        },
        # ── Degree rules / labor market ────────────────────────────────────────
        "rules.run_degree_audit": {
            "program": "AA Liberal Arts", "complete_pct": 70.0,
            "remaining_requirements": ["lab science (4)", "humanities elective (3)"],
        },
        "rules.check_prerequisites": {"course": "MAT-220", "eligible": False,
                                      "missing_prereq": ["MAT-120 with C or better"]},
        "labor.get_career_pathways": {
            "field": "data analytics",
            "pathways": [{"credential": "AS Data Analytics", "median_wage": "$62,000",
                          "next_steps": ["MAT-120", "CIS-150"]}],
        },
        # ── Document pipeline / accessibility ──────────────────────────────────
        "docpipe.classify_document": {"doc_type": "official_transcript", "confidence": 0.94},
        "docpipe.extract_fields": {
            "doc_type": "official_transcript",
            "fields": {"institution": "Prior College", "gpa": "3.1", "credits": "30"},
            "low_confidence_fields": ["date_of_birth"],
        },
        "docpipe.validate_completeness": {"complete": False, "missing": ["official seal/signature"]},
        "docpipe.transform_accessible": {
            "artifact_id": "ACC-0001", "outputs": ["tagged_pdf", "alt_text", "plain_language"],
            "status": "DRAFT", "review_required": True,
        },
        "docpipe.translate_content": {"artifact_id": "TR-0001", "language": "es", "status": "DRAFT"},
        # ── ITSM ───────────────────────────────────────────────────────────────
        "itsm.get_ticket": {"ticket_id": "INC-0001", "status": "open", "category": "wifi"},
        "itsm.create_ticket": {"ticket_id": "INC-DRAFT-0001", "status": "NEW", "created": True},
        "itsm.run_diagnostic": {"target": "managed-device", "wifi_rssi": -71, "disk_free_pct": 18,
                                "finding": "weak wifi signal; low disk"},
        "itsm.reset_password": {"account": "[STUDENT-ID-REDACTED]", "status": "RESET", "reset": True},
        "itsm.restart_service": {"service": "print-spooler", "status": "RESTARTED"},
        # ── ERP / staff admin ──────────────────────────────────────────────────
        "erp.search_policy": {"results": [{"title": "Procurement Threshold Policy", "ref": "FIN-014"}]},
        "erp.draft_document": {"doc_id": "RFP-DRAFT-0001", "status": "DRAFT", "type": "scope_of_work"},
        "erp.initiate_approval": {"approval_id": "APR-0001", "status": "ROUTED", "routed": True},
    }

    def __getattr__(self, method: str) -> Any:  # dynamic method resolution
        def call(**kwargs: Any) -> Dict[str, Any]:
            key = f"{self.kind}.{method}"
            base = self._RESPONSES.get(key, {"ok": True})
            base = dict(base) if isinstance(base, dict) else {"result": base}
            base["echo"] = kwargs
            return base

        return call
