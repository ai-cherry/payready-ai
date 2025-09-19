"""Release stage for Diamond v5."""

from __future__ import annotations

from textwrap import dedent
from typing import Any, Dict

from core.agent_factory import get_factory
from core.runtime import SHELL
from core.jury import triad_with_mediator
from core.reflexion import lessons_for
from core.schemas.artifacts import ReleaseReport


def _build_agents(model_override: str | None) -> Dict[str, Any]:
    factory = get_factory()
    default_model = model_override or "anthropic/claude-opus-4.1"
    return {
        "proponent": factory.create_agent(
            "Release-Proponent",
            "Document release cadence, metrics, comms plan.",
            tools=[SHELL],
            model_id=default_model,
        ),
        "skeptic": factory.create_agent(
            "Release-Skeptic",
            "Verify rollback, incident response, oncall readiness.",
            tools=[SHELL],
            model_id=default_model,
        ),
        "pragmatist": factory.create_agent(
            "Release-Pragmatist",
            "Coordinate stakeholders, approvals, and handoffs.",
            tools=[SHELL],
            model_id=default_model,
        ),
        "mediator": factory.create_agent(
            "Release-Mediator",
            "Emit release_report.json (environment, version, metrics, health, rollback_cmds, links, confidence).",
            model_id=default_model,
        ),
    }


async def run_release(
    goal: str,
    context: Dict[str, Any],
    *,
    model_override: str | None = None,
    **_: Dict[str, Any],
) -> Dict[str, Any]:
    test_snapshot = context["results"].get("test_debug", {}).get("mediator", "")
    hints = lessons_for("release", goal)
    hint_block = "\n".join(f"- {hint['hint']}" for hint in hints) or "- None found"

    prompt = dedent(
        f"""
        Goal: {goal}
        Test report excerpt: {str(test_snapshot)[:800]}.
        Produce release_report.json capturing environment, version, canary_metrics,
        health[], rollback_cmds[], links[], confidence. Include comms checklist.
        Reflexion hints:\n{hint_block}
        """
    )

    agents = _build_agents(model_override)

    return await triad_with_mediator(
        agents["proponent"],
        agents["skeptic"],
        agents["pragmatist"],
        agents["mediator"],
        prompt=prompt,
        stage="Release",
        inputs={"goal": goal, "context": context},
        schema=ReleaseReport,
    )
