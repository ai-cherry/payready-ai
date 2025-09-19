"""Integrate stage for Diamond v5."""

from __future__ import annotations

from textwrap import dedent
from typing import Any, Dict

from core.runtime import base_agent, SHELL, GIT
from core.jury import triad_with_mediator
from core.reflexion import lessons_for
from core.schemas.artifacts import IntegrationArtifact


def _build_agents(model_override: str | None) -> Dict[str, Any]:
    default_model = model_override or "anthropic/claude-opus-4.1"
    return {
        "proponent": base_agent(
            "Integrate-Proponent",
            "Outline rollout steps, feature flags, migrations, smoke tests.",
            tools=(GIT, SHELL),
            model=default_model,
        ),
        "skeptic": base_agent(
            "Integrate-Skeptic",
            "Probe rollback, data repair, config drift, incident impact.",
            tools=(SHELL,),
            model=default_model,
        ),
        "pragmatist": base_agent(
            "Integrate-Pragmatist",
            "Document deploy playbook for operators, with explicit gates.",
            tools=(SHELL,),
            model=default_model,
        ),
        "mediator": base_agent(
            "Integrate-Mediator",
            "Emit integration.json as per IntegrationArtifact schema.",
            model=default_model,
        ),
    }


async def run_integrate(
    goal: str,
    context: Dict[str, Any],
    *,
    model_override: str | None = None,
    **_: Dict[str, Any],
) -> Dict[str, Any]:
    threat_snapshot = context["results"].get("threat", {}).get("mediator", "")
    hints = lessons_for("integrate", goal)
    hint_block = "\n".join(f"- {hint['hint']}" for hint in hints) or "- None found"

    prompt = dedent(
        f"""
        Goal: {goal}
        Threat/compliance excerpt: {threat_snapshot[:800]}.
        Produce integration.json enumerating flags, migrations, config_map, rollback,
        confidence. Ensure rollout describes canary/blue-green and monitoring hooks.
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
        stage="Integrate",
        inputs={"goal": goal, "context": context},
        schema=IntegrationArtifact,
    )
