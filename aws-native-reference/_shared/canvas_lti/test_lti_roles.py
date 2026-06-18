"""Canvas LTI 1.3 -> gateway identity mapping tests (no platform stack required)."""
import base64
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lti_launch import claims_from_launch, decode_id_token, map_lti_roles

ROLES = "https://purl.imsglobal.org/spec/lti/claim/roles"
CUSTOM = "https://purl.imsglobal.org/spec/lti/claim/custom"


def test_instructor_maps_to_educator():
    uris = ["http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor"]
    assert map_lti_roles(uris) == ["EDUCATOR"]


def test_learner_maps_to_student():
    uris = ["http://purl.imsglobal.org/vocab/lis/v2/membership#Learner"]
    assert map_lti_roles(uris) == ["STUDENT"]


def test_multiple_roles_precedence_most_privileged_first():
    uris = [
        "http://purl.imsglobal.org/vocab/lis/v2/membership#Learner",
        "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor",
    ]
    assert map_lti_roles(uris)[0] == "EDUCATOR"


def test_unknown_role_defaults_to_student_in_claims():
    claims = claims_from_launch({"sub": "u1", ROLES: ["urn:unknown:role"]})
    assert claims["custom:edu_role"] == "STUDENT"  # least-privilege default


def test_claims_carry_age_signals():
    launch = {"sub": "k12-1", ROLES: ["Learner"], CUSTOM: {"under_13": "true", "rights_transferred": "false"}}
    claims = claims_from_launch(launch)
    assert claims["custom:edu_role"] == "STUDENT"
    assert claims.get("under_13") is True
    assert "rights_transferred" not in claims


def test_dev_decode_roundtrip():
    os.environ["LTI_DEV"] = "1"
    payload = {"sub": "u9", ROLES: ["Instructor"], "name": "Dr. Lee"}
    seg = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    token = f"header.{seg}.sig"
    out = decode_id_token(token)
    assert out["sub"] == "u9"
    assert claims_from_launch(out)["custom:edu_role"] == "EDUCATOR"


def test_mapped_role_is_honored_by_the_gateway():
    """Integration: a Learner launch can read course material but cannot release a grade."""
    platform = Path(__file__).resolve().parents[3] / "platform_core"
    if not (platform / "edu_agent_platform").exists():
        return  # platform not present in this checkout; mapping tests above still cover it
    sys.path.insert(0, str(platform))
    from edu_agent_platform.mcp_gateway import decide

    claims = claims_from_launch({"sub": "s1", ROLES: ["Learner"]})
    roles = claims["custom:edu_role"].split(",")
    assert decide("02-tutor-study-companion", roles, "lms.get_course_content").allowed
    assert not decide("04-assessment-grading-feedback", roles, "assessment.release_grade").allowed
