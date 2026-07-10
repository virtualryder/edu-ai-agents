"""AGP conformance: platform-core declares the Aegis Governance Pattern version it implements.

See the Aegis repo docs/14-GOVERNANCE-PATTERN-VERSIONING.md. This guards the
"governance once, agents as add-ons" contract: the suite must advertise a concrete
AGP version and an implementation version, both machine-readable.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import edu_agent_platform as m


def test_declares_agp_version():
    assert m.AEGIS_GOVERNANCE_PATTERN_VERSION == "1.0"


def test_declares_impl_version():
    assert isinstance(m.__version__, str) and m.__version__.count(".") >= 2
