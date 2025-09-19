"""Test & Debug stage for Diamond v5."""

from __future__ import annotations

from textwrap import dedent
from typing import Any, Dict

from core.agent_factory import get_factory
from core.runtime import SHELL, python_tool
from core.jury import triad_with_mediator
from core.reflexion import lessons_for
from core.schemas.artifacts import TestReport


def _build_agents(model_override: str | None) -> Dict[str, Any]:
    factory = get_factory()
    default_model = model_override or "anthropic/claude-opus-4.1"
    py_tool = python_tool()
    return {
        "proponent": factory.create_agent(
            "Test-Proponent",
            "Execute regression tests, capture coverage, log failures.",
            tools=[py_tool, SHELL],
            model_id=default_model,
        ),
        "skeptic": factory.create_agent(
            "Test-Skeptic",
            "Hunt flaky tests, performance regressions, missing assertions.",
            tools=[py_tool, SHELL],
            model_id=default_model,
        ),
        "pragmatist": factory.create_agent(
            "Test-Pragmatist",
            "Summarise ship/no-ship decision with triage plan.",
            tools=[py_tool, SHELL],
            model_id=default_model,
        ),
        "mediator": factory.create_agent(
            "Test-Mediator",
            "Emit test_report.json (ship, junit_path, coverage, flakes, confidence).",
            model_id=default_model,
        ),
    }


async def run_test_debug(
    goal: str,
    context: Dict[str, Any],
    *,
    consensus_free: bool = False,
    model_override: str | None = None,
    **_: Dict[str, Any],
) -> Dict[str, Any]:
    integrate_snapshot = context["results"].get("integrate", {}).get("mediator", "")
    hints = lessons_for("test_debug", goal)
    hint_block = "\n".join(f"- {hint['hint']}" for hint in hints) or "- None found"

    prompt = dedent(
        f"""
        Goal: {goal}
        Integration excerpt: {integrate_snapshot[:800]}.
        Produce test_report.json capturing ship decision, junit_path, coverage{{pct, xml}},
        flakes[], confidence. Detail commands executed and diagnostics.
        Reflexion hints:\n{hint_block}
        """
    )
    if consensus_free:
        prompt += "\nConsensus-free: rely on actual test output to justify ship/no-ship."

    agents = _build_agents(model_override)

    return await triad_with_mediator(
        agents["proponent"],
        agents["skeptic"],
        agents["pragmatist"],
        agents["mediator"],
        prompt=prompt,
        stage="Test Debug",
        inputs={
            "goal": goal,
            "context": context,
            "consensus_free": consensus_free,
        },
        schema=TestReport,
    )
