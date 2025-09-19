"""Plan Update stage for Diamond v5."""

from __future__ import annotations

from textwrap import dedent
from typing import Any, Dict

from core.agent_factory import get_factory
from core.runtime import SHELL
from core.jury import triad_with_mediator
from core.reflexion import lessons_for
from core.schemas.artifacts import BacklogArtifact


def _build_agents(model_override: str | None) -> Dict[str, Any]:
    factory = get_factory()
    default_model = model_override or "anthropic/claude-opus-4.1"

    return {
        "proponent": factory.create_agent(
            "Update-Proponent",
            "Translate plan + research into backlog items.",
            tools=[SHELL],
            model_id=default_model,
        ),
        "skeptic": factory.create_agent(
            "Update-Skeptic",
            "Catch missing dependencies and unrealistic slices.",
            tools=[SHELL],
            model_id=default_model,
        ),
        "pragmatist": factory.create_agent(
            "Update-Pragmatist",
            "Ensure tasks are reversible, owner-assigned, and testable.",
            tools=[SHELL],
            model_id=default_model,
        ),
        "mediator": factory.create_agent(
            "Update-Mediator",
            "Produce backlog.json compliant with BacklogArtifact schema.",
            model_id=default_model,
        ),
    }


async def run_plan_update(
    goal: str,
    context: Dict[str, Any],
    *,
    model_override: str | None = None,
    **_: Dict[str, Any],
) -> Dict[str, Any]:
    plan_snapshot = context["results"].get("plan", {}).get("mediator", "")
    research_snapshot = context["results"].get("research", {}).get("mediator", "")
    hints = lessons_for("plan_update", goal)
    hint_block = "\n".join(f"- {hint['hint']}" for hint in hints) or "- None found"

    prompt = dedent(
        f"""
        Goal: {goal}
        Build backlog.json with backlog items referencing plan + research outputs.
        Include at least: item_id, task, rationale, dependencies, owner (if known).
        Use confidence to reflect backlog health. Plan excerpt: {str(plan_snapshot)[:600]}.
        Research excerpt: {str(research_snapshot)[:600]}.
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
        stage="Plan Update",
        inputs={"goal": goal, "context": context},
        schema=BacklogArtifact,
    )
