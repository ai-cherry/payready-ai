"""Code stage for Diamond v5."""

from __future__ import annotations

from textwrap import dedent
from typing import Any, Dict

from core.agent_factory import get_factory
from core.runtime import SHELL, GIT, python_tool
from core.jury import triad_with_mediator
from core.reflexion import lessons_for


def _build_agents(model_override: str | None) -> Dict[str, Any]:
    factory = get_factory()

    return {
        "proponent": factory.create_agent(
            "Code-Proponent",
            "Implement backlog items with tests and diff.",
            tools=[GIT, python_tool(), SHELL],
            model_id=model_override or "x-ai/grok-2-mini",
        ),
        "skeptic": factory.create_agent(
            "Code-Skeptic",
            "Identify bugs, perf and security issues in the diff.",
            tools=[SHELL],
            model_id=model_override or "anthropic/claude-opus-4.1",
        ),
        "pragmatist": factory.create_agent(
            "Code-Pragmatist",
            "Minimize surface area, enforce DX, ensure rollback path.",
            tools=[GIT, SHELL],
            model_id=model_override or "anthropic/claude-opus-4.1",
        ),
        "mediator": factory.create_agent(
            "Code-Mediator",
            "Emit diff.patch plus metadata (commands_run, risk_notes).",
            model_id=model_override or "anthropic/claude-opus-4.1",
        ),
    }


async def run_code(
    goal: str,
    context: Dict[str, Any],
    *,
    consensus_free: bool = False,
    model_override: str | None = None,
    **_: Dict[str, Any],
) -> Dict[str, Any]:
    backlog_snapshot = context["results"].get("plan_update", {}).get("mediator", "")
    hints = lessons_for("code", goal)
    hint_block = "\n".join(f"- {hint['hint']}" for hint in hints) or "- None found"

    prompt = dedent(
        f"""
        Goal: {goal}
        Backlog excerpt: {backlog_snapshot[:800]}
        Produce a unified diff patch (diff.patch) with accompanying JSON metadata
        summarising commands_run[], tests_executed[], risk_notes[], confidence.
        In consensus-free mode, runtime signals (tests passing) outweigh rhetoric.
        Reflexion hints:\n{hint_block}
        """
    )
    if consensus_free:
        prompt += "\nConsensus-free: prioritise executable validation (pytest, coverage)."

    agents = _build_agents(model_override)

    return await triad_with_mediator(
        agents["proponent"],
        agents["skeptic"],
        agents["pragmatist"],
        agents["mediator"],
        prompt=prompt,
        stage="Code",
        inputs={
            "goal": goal,
            "context": context,
            "consensus_free": consensus_free,
        },
    )
