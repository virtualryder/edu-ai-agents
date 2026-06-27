"""
Streamlit HITL reviewer UI — staff review and approve consequential agent actions.

    streamlit run platform_core/edu_agent_platform/reviewer/app.py

This is the thin presentation layer over `ReviewService` (which holds all the logic
the tests assert): it authenticates the reviewer, shows the EXACT proposed action and
arguments, enforces entitlement + separation of duties, and — on approval — issues a
signed, transaction-bound, single-use approval the gateway accepts exactly once. In
production the reviewer identity comes from Cognito/JWT (not the sidebar) and the queue
is backed by DynamoDB + the Step Functions task token.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

try:
    import streamlit as st
except Exception:  # pragma: no cover - UI dependency optional
    raise SystemExit("Streamlit is required: pip install streamlit")

from edu_agent_platform.reviewer import ReviewService


@st.cache_resource
def _service() -> ReviewService:
    svc = ReviewService()
    # Seed a demo item so the queue is non-empty on first run.
    svc.enqueue(agent_id="01-student-family-concierge", requester_sub="u-staff-7",
                tool="comms.send_message",
                args={"student_id": "S-100", "channel": "email",
                      "body": "Your registration window opens Monday."},
                summary="Outbound family message — registration reminder")
    return svc


def main() -> None:
    st.set_page_config(page_title="EDU Agent — HITL Reviewer", page_icon="✅")
    st.title("Human-in-the-loop Reviewer")
    st.caption("Consequential agent actions require a named, entitled human to approve.")

    with st.sidebar:
        st.subheader("Reviewer (demo identity)")
        sub = st.text_input("Reviewer ID (sub)", "u-super-1")
        role = st.selectbox("Role", ["ADMINISTRATOR", "COUNSELOR", "REGISTRAR",
                                     "FINANCIAL_AID", "STUDENT"])
        st.info("Production: identity comes from Cognito/JWT, not this form.")
    claims = {"sub": sub, "custom:edu_role": role}

    svc = _service()
    pending = svc.list_pending(claims)
    st.subheader(f"Pending for you ({len(pending)})")
    if not pending:
        st.write("Nothing awaiting your approval (queue is entitlement-filtered).")

    for item in pending:
        with st.container(border=True):
            st.markdown(f"**{item['summary']}**")
            st.write(f"Agent: `{item['agent_id']}` · Tool: `{item['tool']}` · "
                     f"Requested by: `{item['requested_by']}`")
            st.json(item["arguments"])
            st.caption(f"args-sha256: {item['args_sha256'][:16]}… · "
                       f"separation-of-duties required: {item['separation_of_duties_required']}")
            c1, c2 = st.columns(2)
            if c1.button("Approve", key=f"a-{item['id']}"):
                dec = svc.decide(claims, item["id"], approve=True)
                (st.success if dec.approved else st.error)(dec.reason)
                if dec.approved:
                    st.code(f"signed approval issued (single-use nonce "
                            f"{dec.approval['binding']['nonce'][:8]}…)")
            if c2.button("Decline", key=f"d-{item['id']}"):
                st.warning(svc.decide(claims, item["id"], approve=False).reason)


if __name__ == "__main__":
    main()
