"""Research stage for Diamond v5."""

from __future__ import annotations

from textwrap import dedent
from typing import Any, Dict

from core.runtime import base_agent, SHELL
from core.jury import triad_with_mediator
from core.reflexion import lessons_for
from core.schemas.artifacts import ResearchArtifact


def _build_agents(model_override: str | None) -> Dict[str, Any]:
    return {
        "proponent": base_agent(
            "Research-Proponent",
            "Gather fresh alternatives with citations and pros/cons.",
            tools=(SHELL,),
            model=model_override or "perplexity/llama-3.3-sonar-large-128k-online",
        ),
        "skeptic": base_agent(
            "Research-Skeptic",
            "Pressure-test sources for recency, licensing, architectural fit.",
            tools=(SHELL,),
            model=model_override or "anthropic/claude-opus-4.1",
        ),
        "pragmatist": base_agent(
            "Research-Pragmatist",
            "Summarize decision matrix and filter noise for the goal.",
            tools=(SHELL,),
            model=model_override or "anthropic/claude-opus-4.1",
        ),
        "mediator": base_agent(
            "Research-Mediator",
            "Emit research.json per ResearchArtifact schema.",
            model=model_override or "anthropic/claude-opus-4.1",
        ),
    }


async def run_research(
    goal: str,
    context: Dict[str, Any],
    *,
    model_override: str | None = None,
    **_: Dict[str, Any],
) -> Dict[str, Any]:
    hints = lessons_for("research", goal)
    hint_block = "\n".join(f"- {hint['hint']}" for hint in hints) or "- None found"
    plan_snapshot = context["results"].get("plan", {}).get("mediator", "")

    prompt = dedent(
        f"""
        Goal: {goal}
        Provide research.json with options[], decision_matrix[], chosen, citations[],
        freshness_window_days, confidence. Prior plan context: {plan_snapshot[:800]}.
        Ensure citations include URL + access date. Highlight licensing or compliance
        caveats in decision_matrix.
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
        stage="Research",
        inputs={"goal": goal, "context": context},
        schema=ResearchArtifact,
    )
