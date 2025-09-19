"""Threat & Compliance stage for Diamond v5."""

from __future__ import annotations

from textwrap import dedent
from typing import Any, Dict

from core.runtime import base_agent, SHELL
from core.jury import triad_with_mediator
from core.reflexion import lessons_for
from core.schemas.artifacts import ThreatArtifact


def _build_agents(model_override: str | None) -> Dict[str, Any]:
    default_model = model_override or "anthropic/claude-opus-4.1"
    return {
        "proponent": base_agent(
            "Threat-Proponent",
            "Construct threat model, STRIDE analysis, and mitigations.",
            tools=(SHELL,),
            model=default_model,
        ),
        "skeptic": base_agent(
            "Threat-Skeptic",
            "Red-team secrets, PII exposure, supply chain, logging gaps.",
            tools=(SHELL,),
            model=default_model,
        ),
        "pragmatist": base_agent(
            "Threat-Pragmatist",
            "Operationalise controls: CI gates, audits, rollback drills, runbooks.",
            tools=(SHELL,),
            model=default_model,
        ),
        "mediator": base_agent(
            "Threat-Mediator",
            "Emit threat.json following ThreatArtifact schema.",
            model=default_model,
        ),
    }


async def run_threat(
    goal: str,
    context: Dict[str, Any],
    *,
    model_override: str | None = None,
    **_: Dict[str, Any],
) -> Dict[str, Any]:
    review_snapshot = context["results"].get("review", {}).get("mediator", "")
    hints = lessons_for("threat", goal)
    hint_block = "\n".join(f"- {hint['hint']}" for hint in hints) or "- None found"

    prompt = dedent(
        f"""
        Goal: {goal}
        Review artifact excerpt: {review_snapshot[:800]}.
        Produce threat.json with fields: dfd, risks[], mitigations[], controls[],
        rollback_plan, compliance{{logging, pii, retention}}, confidence.
        Ensure mitigations include SAST/DAST, secrets scanning, license/PII checks.
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
        stage="Threat",
        inputs={"goal": goal, "context": context},
        schema=ThreatArtifact,
    )
