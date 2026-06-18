"""Prompt registry: every registered prompt is hash-pinned in the manifest (no drift)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from governance import prompt_registry


def test_all_prompts_pinned_in_manifest():
    prompt_registry._discover()  # import every agent's prompts so they self-register
    assert prompt_registry.current_registry(), "no prompts registered — discovery failed"
    problems = prompt_registry.verify_manifest()
    assert not problems, "prompt drift / missing manifest entries:\n" + "\n".join(
        f"  {k}: {v}" for k, v in problems.items()
    )
