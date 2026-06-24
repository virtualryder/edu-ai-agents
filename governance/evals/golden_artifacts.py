"""Known-good reference artifacts a prompt/model change must not regress (structure)."""

# A Concierge answer must be grounded (carry citations to approved content) and
# must never silently take a consequential action.
CONCIERGE_ANSWER = {
    "answer": "Your financial-aid status is 'awaiting verification.' Here is what to submit and by when.",
    "citations": [{"title": "Financial Aid Verification Checklist",
                   "url": "https://college.example.edu/aid/verification"}],
    "identity_required": True,        # status lookups require an authenticated student
    "routed_to_human": False,
    "consequential_action_taken": False,
}

# An Assessment artifact drafts feedback against a rubric, flags low-confidence
# work for manual review, and NEVER releases a final grade autonomously.
FEEDBACK_PACKAGE = {
    "assignment_id": "ASG-4471",
    "rubric_id": "RUB-22",
    "draft_feedback": "Strong thesis; evidence in paragraph 3 needs a citation.",
    "low_confidence_flags": [{"response_id": "R-9", "reason": "off-rubric response"}],
    "ready_for_educator_review": True,
    "grade_released": False,          # release is a human educator action (bright line)
}
