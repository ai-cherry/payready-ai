"""Plan stage for Diamond v5."""

from __future__ import annotations

from textwrap import dedent
from typing import Any, Dict

from core.agent_factory import get_factory
from core.runtime import SHELL
from core.jury import triad_with_mediator
from core.reflexion import lessons_for
from core.schemas.artifacts import PlanArtifact


def _build_agents(model_override: str | None) -> Dict[str, Any]:
    factory = get_factory()

    return {
        "proponent": factory.create_agent(
            "Plan-Proponent",
            "Draft the plan artifact with milestones and acceptance criteria.",
            model_id=model_override or "openai/gpt-4o",
            tools=[SHELL],
            instructions=[
                "Create a comprehensive plan with clear milestones",
                "Define explicit acceptance criteria",
                "Consider risks and mitigation strategies"
            ]
        ),
        "skeptic": factory.create_agent(
            "Plan-Skeptic",
            "Stress-test feasibility, highlight missing risks, push for clarity.",
            model_id=model_override or "anthropic/claude-opus-4.1",
            tools=[SHELL],
            instructions=[
                "Challenge assumptions in the plan",
                "Identify missing risks and edge cases",
                "Push for clarity in ambiguous areas"
            ]
        ),
        "pragmatist": factory.create_agent(
            "Plan-Pragmatist",
            "Ensure plan is executable, reversible, and timeboxed.",
            model_id=model_override or "anthropic/claude-opus-4.1",
            tools=[SHELL],
            instructions=[
                "Focus on practical implementation",
                "Ensure tasks are reversible",
                "Validate timelines are realistic"
            ]
        ),
        "mediator": factory.create_agent(
            "Plan-Mediator",
            "Produce plan.json compliant with PlanArtifact schema.",
            model_id=model_override or "anthropic/claude-opus-4.1",
            instructions=[
                "Synthesize all perspectives into consensus",
                "Output structured JSON following PlanArtifact schema",
                "Balance conflicting views fairly"
            ]
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
