"""AGP v1.0 conformance — this pack declares the contract version and ships every required
control module (incl. token budgets, AGP control #7). Fails CI if conformance regresses."""
import importlib


def test_declares_agp_1_0():
    pkg = importlib.import_module("edu_agent_platform")
    assert getattr(pkg, "AEGIS_GOVERNANCE_PATTERN_VERSION", None) == "1.0"


def test_token_budget_module_present():
    m = importlib.import_module("edu_agent_platform.budget")
    assert hasattr(m, "BudgetMeter")


def test_core_control_modules_import():
    for mod in ("edu_agent_platform.mcp_gateway.gateway", "edu_agent_platform.mcp_gateway.policy",
                "edu_agent_platform.mcp_gateway.audit"):
        importlib.import_module(mod)
