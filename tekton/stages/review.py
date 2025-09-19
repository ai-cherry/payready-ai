"""Review stage for Diamond v5."""

from __future__ import annotations

from textwrap import dedent
from typing import Any, Dict

from core.runtime import base_agent, SHELL, GIT
from core.jury import triad_with_mediator
from core.reflexion import lessons_for


def _build_agents(model_override: str | None) -> Dict[str, Any]:
    default_model = model_override or "anthropic/claude-opus-4.1"
    return {
        "proponent": base_agent(
            "Review-Proponent",
            "Summarise diff impact and readiness for merge.",
            tools=(GIT, SHELL),
            model=default_model,
        ),
        "skeptic": base_agent(
            "Review-Skeptic",
            "Log blocking issues, coverage gaps, regressions.",
            tools=(GIT, SHELL),
            model=default_model,
        ),
        "pragmatist": base_agent(
            "Review-Pragmatist",
            "Enumerate fixes or approvals with rollback clarity.",
            tools=(GIT, SHELL),
            model=default_model,
        ),
        "mediator": base_agent(
            "Review-Mediator",
            "Emit review.json with status, issues, fixlist, confidence.",
            model=default_model,
        ),
    }


async def run_review(
    goal: str,
    context: Dict[str, Any],
    *,
    model_override: str | None = None,
    **_: Dict[str, Any],
) -> Dict[str, Any]:
    diff_snapshot = context["results"].get("code", {}).get("mediator", "")
    hints = lessons_for("review", goal)
    hint_block = "\n".join(f"- {hint['hint']}" for hint in hints) or "- None found"

    prompt = dedent(
        f"""
        Goal: {goal}
        Evaluate diff + metadata: {diff_snapshot[:800]}.
        Produce review.json => status(ok|revise|block), issues[], fixlist[], risks[],
        confidence. Capture any dissent explicitly.
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
        stage="Review",
        inputs={"goal": goal, "context": context},
    )
