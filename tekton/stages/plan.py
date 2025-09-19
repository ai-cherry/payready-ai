"""Plan stage for Diamond v5."""

from __future__ import annotations

from textwrap import dedent
from typing import Any, Dict

from core.runtime import base_agent, SHELL
from core.jury import triad_with_mediator
from core.reflexion import lessons_for
from core.schemas.artifacts import PlanArtifact


def _build_agents(model_override: str | None) -> Dict[str, Any]:
    return {
        "proponent": base_agent(
            "Plan-Proponent",
            "Draft the plan artifact with milestones and acceptance criteria.",
            tools=(SHELL,),
            model=model_override or "openai/gpt-4o",
        ),
        "skeptic": base_agent(
            "Plan-Skeptic",
            "Stress-test feasibility, highlight missing risks, push for clarity.",
            tools=(SHELL,),
            model=model_override or "anthropic/claude-opus-4.1",
        ),
        "pragmatist": base_agent(
            "Plan-Pragmatist",
            "Ensure plan is executable, reversible, and timeboxed.",
            tools=(SHELL,),
            model=model_override or "anthropic/claude-opus-4.1",
        ),
        "mediator": base_agent(
            "Plan-Mediator",
            "Produce plan.json compliant with PlanArtifact schema.",
            model=model_override or "anthropic/claude-opus-4.1",
        ),
    }


async def run_plan(
    goal: str,
    context: Dict[str, Any],
    *,
    model_override: str | None = None,
    **_: Dict[str, Any],
) -> Dict[str, Any]:
    hints = lessons_for("plan", goal)
    hint_block = "\n".join(f"- {hint['hint']}" for hint in hints) or "- None found"

    prompt = dedent(
        f"""
        Goal: {goal}
        Craft plan.json following PlanArtifact schema (goals, milestones, acceptance_criteria,
        risks, slos, dri, timeline, confidence).
        Use bullet lists with concrete deliverables and explicit acceptance tests.
        Integrate any prior backlog or research info from context if present.
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
        stage="Plan",
        inputs={"goal": goal, "context": context},
        schema=PlanArtifact,
    )
