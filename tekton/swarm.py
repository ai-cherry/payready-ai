"""Workflow definition and runner for the Diamond v5 swarm."""

from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, Iterable

from .stages import (
    plan,
    research,
    plan_update,
    code,
    review,
    threat,
    integrate,
    test_debug,
    release,
)

STAGES = OrderedDict(
    [
        ("plan", plan.run_plan),
        ("research", research.run_research),
        ("plan_update", plan_update.run_plan_update),
        ("code", code.run_code),
        ("review", review.run_review),
        ("threat", threat.run_threat),
        ("integrate", integrate.run_integrate),
        ("test_debug", test_debug.run_test_debug),
        ("release", release.run_release),
    ]
)


def describe() -> Dict[str, Any]:
    return {"name": "diamond_v5", "stages": list(STAGES.keys())}


ARTIFACT_FILENAMES = {
    "plan": "plan.json",
    "research": "research.json",
    "plan_update": "backlog.json",
    "threat": "threat.json",
    "integrate": "integration.json",
    "test_debug": "test_report.json",
    "release": "release_report.json",
}


async def run(
    *,
    goal: str,
    start: str = "plan",
    end: str = "release",
    consensus_free: Iterable[str] | None = None,
    resume: str | None = None,
    model_override: str | None = None,
    output_dir: Path,
) -> Dict[str, Any]:
    if start not in STAGES:
        raise ValueError(f"Unknown start stage: {start}")
    if end not in STAGES:
        raise ValueError(f"Unknown end stage: {end}")

    consensus_free_set = {s.lower() for s in (consensus_free or [])}
    results: Dict[str, Any] = {}
    context = {"goal": goal, "results": results, "resume": resume}

    capture = False
    for name, fn in STAGES.items():
        if name == start:
            capture = True
        if not capture:
            continue

        stage_kwargs: Dict[str, Any] = {
            "goal": goal,
            "context": context,
            "model_override": model_override,
        }
        if name in {"code", "test_debug"}:
            stage_kwargs["consensus_free"] = name in consensus_free_set

        result = await fn(**stage_kwargs)
        artifact = result.get("artifact")
        if artifact is not None:
            filename = ARTIFACT_FILENAMES.get(name, f"{name}.json")
            destination = output_dir / filename
            destination.parent.mkdir(parents=True, exist_ok=True)
            # Pydantic v2 compatibility
            if hasattr(artifact, 'model_dump_json'):
                # Pydantic v2
                destination.write_text(artifact.model_dump_json(indent=2))
            else:
                # Pydantic v1 fallback
                destination.write_text(artifact.json(indent=2))
            result["artifact_path"] = str(destination)

        results[name] = result
        if name == end:
            break

    return {"goal": goal, "results": results}


__all__ = ["run", "describe", "STAGES"]
