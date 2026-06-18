"""
Prompt registry — versioned, hash-pinned prompts (no silent prompt drift).

In a model-risk posture, the prompt is part of the model. A prompt change can
change a student-facing output, so prompts must be versioned, hash-pinned, and
change-controlled like code. This registry:

  * computes a stable SHA-256 over each registered prompt,
  * checks it against governance/prompt_manifest.json (the pinned versions), and
  * fails CI if a prompt changed without a manifest bump (deliberate, reviewed).

Agents register their prompts at import time:

    from governance.prompt_registry import register
    FAMILY_MESSAGE_PROMPT = register("01-student-family-concierge", "family_message", v=1, text=\"\"\"...\"\"\")

CI runs `verify_manifest()` (governance/tests). Bumping a prompt = update the
text, bump `v`, run `python -m governance.prompt_registry --update`, commit the
manifest diff alongside the prompt diff so the change is auditable.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict

_MANIFEST = Path(__file__).resolve().parent / "prompt_manifest.json"

# In-process registry: key -> {"version", "sha256", "agent", "name"}
_REGISTRY: Dict[str, Dict[str, object]] = {}


def _sha(text: str) -> str:
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()


def register(agent: str, name: str, v: int, text: str) -> str:
    """Register a prompt and return its text (so call sites assign normally)."""
    key = f"{agent}:{name}"
    _REGISTRY[key] = {"version": v, "sha256": _sha(text), "agent": agent, "name": name}
    return text


def current_registry() -> Dict[str, Dict[str, object]]:
    return dict(_REGISTRY)


def load_manifest() -> Dict[str, Dict[str, object]]:
    if _MANIFEST.exists():
        data = json.loads(_MANIFEST.read_text())
        return {k: v for k, v in data.items() if not k.startswith("_")}
    return {}


def write_manifest() -> None:
    payload = {
        "_comment": (
            "Hash-pinned prompt versions. Bump via: python -m governance.prompt_registry "
            "--update. CI fails if a registered prompt's text changes without a manifest "
            "bump (deliberate, reviewed change control)."
        ),
        **{k: v for k, v in sorted(_REGISTRY.items())},
    }
    _MANIFEST.write_text(json.dumps(payload, indent=2) + "\n")


def verify_manifest() -> Dict[str, str]:
    """
    Return {key: problem} for any registered prompt whose hash/version does not
    match the manifest. Empty dict means CI passes.
    """
    manifest = load_manifest()
    problems: Dict[str, str] = {}
    for key, meta in _REGISTRY.items():
        pinned = manifest.get(key)
        if not pinned:
            problems[key] = "prompt not in manifest (add it with --update)"
        elif pinned.get("sha256") != meta["sha256"]:
            problems[key] = (
                f"prompt text changed without manifest bump "
                f"(manifest v{pinned.get('version')} -> registered v{meta['version']})"
            )
    return problems


def _discover() -> None:
    """Import each agent's prompt module so prompts self-register.

    Each agent ships an identically-named `agent` package, so we purge it (and
    `tools`) from sys.modules between agents to force a fresh import per agent.
    """
    import importlib
    import sys
    from pathlib import Path as _P

    repo = _P(__file__).resolve().parent.parent
    sys.path.insert(0, str(repo))
    sys.path.insert(0, str(repo / "platform_core"))
    for p in sorted(repo.glob("[0-9][0-9]-*/agent")):
        agent_root = str(p.parent)
        sys.path.insert(0, agent_root)
        # Purge any previously-imported agent's modules so the import is fresh.
        for mod in [m for m in list(sys.modules) if m == "agent" or m.startswith("agent.")
                    or m == "tools" or m.startswith("tools.")]:
            del sys.modules[mod]
        try:
            importlib.import_module("agent.prompts")
        except Exception:
            pass
        finally:
            if agent_root in sys.path:
                sys.path.remove(agent_root)


if __name__ == "__main__":
    import sys

    # Use the imported module instance (not __main__) so prompts that do
    # `from governance.prompt_registry import register` populate the SAME registry.
    from governance import prompt_registry as pr

    pr._discover()
    if "--update" in sys.argv:
        pr.write_manifest()
        print(f"Wrote manifest with {len(pr._REGISTRY)} prompts -> {pr._MANIFEST}")
    else:
        issues = pr.verify_manifest()
        for k, v in issues.items():
            print("DRIFT", k, "-", v)
        print(f"\n{len(pr._REGISTRY) - len(issues)}/{len(pr._REGISTRY)} prompts match manifest")
        raise SystemExit(1 if issues else 0)
