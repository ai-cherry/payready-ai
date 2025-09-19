"""Triad + mediator debate engine with confidence-weighted quorum."""

from __future__ import annotations

import json
from json import JSONDecodeError
from typing import Any, Dict, Optional, Sequence, Tuple, Type

from agno import Agent
from pydantic import BaseModel


def _rubric(stage: str) -> str:
    return (
        f"You are in the {stage} stage.\n"
        "Always answer with JSON containing keys:\n"
        "  position: string\n"
        "  score: {correctness:float, stack_fit:float, ops_risk:float, reversibility:float, recency:float}\n"
        "  risks: [string]\n"
        "  checks: [string]\n"
        "  self_confidence: float in [0,1]\n"
        "  dissent?: optional notes\n"
    )


def _as_messages(data: Sequence[Tuple[str, str]]) -> str:
    return "\n".join(f"[{agent}] {content}" for agent, content in data)


async def triad_with_mediator(
    proponent: Agent,
    skeptic: Agent,
    pragmatist: Agent,
    mediator: Agent,
    *,
    prompt: str,
    stage: str,
    inputs: Dict[str, Any] | None = None,
    rounds: int = 2,
    schema: Optional[Type[BaseModel]] = None,
) -> Dict[str, Any]:
    """Run debate loop and return mediator consensus payload."""

    inputs = inputs or {}
    transcript: list[Tuple[str, str]] = []

    async def _run(agent: Agent, label: str, context: str) -> str:
        message = await agent.run(context, **inputs)
        transcript.append((label, message))
        return message

    context = _rubric(stage) + "\n" + prompt
    position = {
        "A": await _run(proponent, "Proponent", context + "\n" + prompt),
        "B": await _run(skeptic, "Skeptic", context + "\n" + prompt),
        "C": await _run(pragmatist, "Pragmatist", context + "\n" + prompt),
    }

    for _ in range(rounds):
        summary = _as_messages(transcript)
        position["A"] = await _run(proponent, "Proponent", summary)
        position["B"] = await _run(skeptic, "Skeptic", summary)
        position["C"] = await _run(pragmatist, "Pragmatist", summary)

    mediator_prompt = (
        "Reconcile Proponent/Skeptic/Pragmatist using a 2/3 quorum.\n"
        "Weight each vote by its self_confidence (ConfMAD).\n"
        "If confidence < 0.70 or mandatory fields missing, set status='block'.\n"
        "Return JSON with keys: {artifact, status, rationale, dissent, risks, checklist, confidence, votes, loops_run}.\n"
        f"Transcript follows:\n{_as_messages(transcript)}"
    )

    response = await mediator.run(mediator_prompt, **inputs)

    try:
        payload = json.loads(response)
    except (TypeError, JSONDecodeError) as exc:
        raise ValueError(f"Stage '{stage}' mediator output is not valid JSON") from exc

    artifact_model = None
    if schema is not None:
        try:
            artifact_model = schema.parse_obj(payload.get("artifact", payload))
        except Exception as exc:  # noqa: BLE001
            raise ValueError(
                f"Stage '{stage}' mediator output failed {schema.__name__} validation"
            ) from exc

    return {
        "mediator": payload,
        "artifact": artifact_model,
        "transcript": transcript,
    }


__all__ = ["triad_with_mediator"]
