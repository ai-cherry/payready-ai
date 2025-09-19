"""Agno team adapter coordinating planner, coder, and reviewer agents using real Agno v2.0.7."""

from __future__ import annotations

import json
import asyncio
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import typer

from ._io import append_jsonl, append_text, new_run_dir
from .metadata import collect_repo_state, provider_metadata, redact_payload, redact_text
from .result import AgentResult

# Use new config and factory
try:
    from ..config_v2 import Settings, get_settings
except ImportError:
    from ..config import Settings
    def get_settings():
        return Settings()

try:
    from ...core.agent_factory import AgentFactory, get_factory
except ImportError:
    AgentFactory = None
    def get_factory(settings=None):
        return None

SESSION_SECTION_TEMPLATE = """### {timestamp} · Agno Swarm

Task: {task}
Outcome: {status}
Decisions: {decisions}
Tests: {tests}
Notes: {notes}
"""


def _context_blob(context: Dict[str, Any], max_chars: int) -> str:
    sections: list[str] = []
    if context.get("session_markdown"):
        sections.append(context["session_markdown"][-max_chars:])
    events = context.get("events") or []
    if events:
        formatted = "\n".join(
            f"- {event.get('timestamp', '')} {event.get('agent', '')}: {event.get('output_preview', '')}"
            for event in events[-10:]
        )
        sections.append(f"Recent Events\n{formatted}")
    if context.get("extra_context"):
        sections.append(f"Extra Context\n{context['extra_context']}")
    blob = "\n\n".join(sections)
    if len(blob) > max_chars:
        blob = blob[-max_chars:]
    return blob


def _serialize_result(result: Any) -> Dict[str, Any]:
    if result is None:
        return {"result": None}
    if isinstance(result, dict):
        return result
    if hasattr(result, "model_dump"):
        return result.model_dump()  # type: ignore[no-any-return]
    if hasattr(result, "dict"):
        return result.dict()  # type: ignore[no-any-return]
    return {"result": str(result)}


def _extract_list(payload: Any, keys: Iterable[str]) -> list[str]:
    if payload is None:
        return []
    for key in keys:
        if isinstance(payload, dict) and key in payload:
            value = payload[key]
        else:
            value = getattr(payload, key, None)
        if isinstance(value, list):
            return [str(item) for item in value]
    return []


def _create_agents(settings: Settings, model_override: Optional[str]):
    """Create agents using the factory pattern with real Agno v2.0.7."""

    # Try to use the new factory
    if AgentFactory:
        factory = get_factory(settings)
        if factory:
            api_key = settings.get_active_api_key() if hasattr(settings, 'get_active_api_key') else None
            if not api_key:
                api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")

            planner = factory.create_planner(api_key)
            coder = factory.create_coder(api_key)
            reviewer = factory.create_reviewer(api_key)
            return planner, coder, reviewer

    # Fallback to direct creation
    from agno.agent import Agent
    from agno.models.openai import OpenAIChat

    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("No API key available")

    agno_cfg = getattr(settings.agents, 'agno', None) if hasattr(settings, 'agents') else None
    if not agno_cfg:
        # Use defaults
        planner_model = "openai/gpt-4o-mini"
        coder_model = "openai/gpt-4o-mini"
        reviewer_model = "openai/gpt-4o-mini"
    else:
        planner_model = model_override or agno_cfg.planner_model
        coder_model = model_override or agno_cfg.coder_model
        reviewer_model = model_override or agno_cfg.reviewer_model

    def create_agent(name: str, role: str, model_id: str) -> Agent:
        model = OpenAIChat(
            id=model_id,
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        return Agent(
            name=name,
            role=role,
            model=model,
            instructions=[
                f"You are {name}, a {role}",
                "Provide clear, structured outputs",
                "Use markdown formatting"
            ],
            markdown=True
        )

    planner = create_agent("planner", "strategic planner who breaks down tasks", planner_model)
    coder = create_agent("coder", "expert programmer who implements solutions", coder_model)
    reviewer = create_agent("reviewer", "code reviewer who ensures quality", reviewer_model)
    return planner, coder, reviewer


def run(
    *,
    task: str,
    memory_dir: Path,
    context: Dict[str, Any],
    settings: Settings,
    model_override: Optional[str] = None,
    dry_run: bool = False,
) -> AgentResult:
    agno_cfg = settings.agents.agno
    run_dir = new_run_dir(memory_dir)
    prompt_path = run_dir / "prompt.md"
    response_path = run_dir / "response.md"
    metadata_path = run_dir / "metadata.json"

    context_blob = _context_blob(context, agno_cfg.max_context_chars)
    prompt_payload = {
        "task": task,
        "context": context_blob,
    }
    prompt_path.write_text(
        json.dumps(redact_payload(prompt_payload), indent=2), encoding="utf-8"
    )

    start_ts = datetime.now(timezone.utc)

    if dry_run:
        summary = (
            "Dry run: planner would decompose the task into steps, "
            "coder executes each with tests, reviewer enforces policy."
        )
        response_path.write_text(summary, encoding="utf-8")
        metadata = {
            "agent": "agno",
            "success": True,
            "dry_run": True,
            "summary": summary,
        }
        metadata.update(collect_repo_state(memory_dir.parent))
        metadata_path.write_text(json.dumps(redact_payload(metadata), indent=2), encoding="utf-8")
        append_text(
            memory_dir / "session-log.md",
            redact_text(
                SESSION_SECTION_TEMPLATE.format(
                    timestamp=start_ts.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    task=task,
                    status="DRY-RUN",
                    decisions="(skipped)",
                    tests="(skipped)",
                    notes=summary,
                )
            ),
        )
        append_jsonl(
            memory_dir / "events.jsonl",
            redact_payload(
                {
                    "timestamp": start_ts.isoformat(),
                    "agent": "agno",
                    "command": "agno",
                    "output_preview": summary[:800],
                    "metadata": metadata,
                }
            ),
        )
        return AgentResult(output=redact_text(summary), metadata=metadata, run_dir=run_dir)

    # Use real Agno Team API (Swarm doesn't exist in Agno v2.0.7)
    try:
        from agno.team import Team
    except ImportError as exc:
        metadata = {
            "agent": "agno",
            "success": False,
            "error": "Neither Agno package nor stub implementation available.",
        }
        metadata.update(collect_repo_state(memory_dir.parent))
        metadata_path.write_text(json.dumps(redact_payload(metadata), indent=2), encoding="utf-8")
        append_jsonl(
            memory_dir / "events.jsonl",
            redact_payload(
                {
                    "timestamp": start_ts.isoformat(),
                    "agent": "agno",
                    "command": "agno",
                    "output_preview": metadata["error"],
                    "metadata": metadata,
                }
            ),
        )
        append_text(
            memory_dir / "session-log.md",
            redact_text(
                SESSION_SECTION_TEMPLATE.format(
                    timestamp=start_ts.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    task=task,
                    status="FAILED",
                    decisions="-",
                    tests="-",
                    notes=metadata["error"],
                )
            ),
        )
        raise typer.Exit(code=1) from exc

    try:
        planner, coder, reviewer = _create_agents(settings, model_override)
    except ImportError as exc:
        metadata = {
            "agent": "agno",
            "success": False,
            "error": str(exc),
        }
        metadata.update(collect_repo_state(memory_dir.parent))
        metadata_path.write_text(json.dumps(redact_payload(metadata), indent=2), encoding="utf-8")
        append_jsonl(
            memory_dir / "events.jsonl",
            redact_payload(
                {
                    "timestamp": start_ts.isoformat(),
                    "agent": "agno",
                    "command": "agno",
                    "output_preview": metadata["error"],
                    "metadata": metadata,
                }
            ),
        )
        append_text(
            memory_dir / "session-log.md",
            redact_text(
                SESSION_SECTION_TEMPLATE.format(
                    timestamp=start_ts.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    task=task,
                    status="FAILED",
                    decisions="-",
                    tests="-",
                    notes=metadata["error"],
                )
            ),
        )
        raise typer.Exit(code=1) from exc
    # Create team with real Agno v2.0.7 API
    team = Team(members=[planner, coder, reviewer])

    try:
        # Run team workflow asynchronously
        async def run_team_workflow():
            results = {}

            # Planning phase
            plan_prompt = f"Break down this task into clear implementation steps:\n{task}\n\nContext:\n{context_blob}"
            plan_response = await planner.arun(plan_prompt)
            results["plan"] = plan_response.content if hasattr(plan_response, 'content') else str(plan_response)

            # Coding phase
            code_prompt = f"Implement this based on the plan:\nTask: {task}\nPlan:\n{results['plan']}\n\nContext:\n{context_blob}"
            code_response = await coder.arun(code_prompt)
            results["code"] = code_response.content if hasattr(code_response, 'content') else str(code_response)

            # Review phase
            review_prompt = f"Review this implementation:\nTask: {task}\nCode:\n{results['code']}"
            review_response = await reviewer.arun(review_prompt)
            results["review"] = review_response.content if hasattr(review_response, 'content') else str(review_response)

            return {
                "success": True,
                "summary": f"Completed task with Agno team workflow",
                "decisions": [results["plan"][:200] + "..."],
                "tests": [results["review"][:200] + "..."],
                "results": results
            }

        result = asyncio.run(run_team_workflow())
    except Exception as exc:  # pragma: no cover - runtime safety
        metadata = {
            "agent": "agno",
            "success": False,
            "error": str(exc),
        }
        metadata.update(provider_metadata("agno", model_override or agno_cfg.coder_model))
        metadata.update(collect_repo_state(memory_dir.parent))
        metadata_path.write_text(json.dumps(redact_payload(metadata), indent=2), encoding="utf-8")
        append_jsonl(
            memory_dir / "events.jsonl",
            redact_payload(
                {
                    "timestamp": start_ts.isoformat(),
                    "agent": "agno",
                    "command": "agno",
                    "output_preview": metadata["error"],
                    "metadata": metadata,
                }
            ),
        )
        append_text(
            memory_dir / "session-log.md",
            redact_text(
                SESSION_SECTION_TEMPLATE.format(
                    timestamp=start_ts.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    task=task,
                    status="FAILED",
                    decisions="-",
                    tests="-",
                    notes=metadata["error"],
                )
            ),
        )
        raise typer.Exit(code=1) from exc

    serialized = _serialize_result(result)
    artifact_path = run_dir / "artifact.json"
    sanitized_serialized = redact_payload(serialized)
    artifact_path.write_text(json.dumps(sanitized_serialized, indent=2), encoding="utf-8")
    response_path.write_text(json.dumps(sanitized_serialized, indent=2), encoding="utf-8")

    decisions = [redact_text(item) for item in _extract_list(result, ("decisions", "actions", "steps"))]
    tests = [redact_text(item) for item in _extract_list(result, ("tests", "validation", "checks"))]

    summary = sanitized_serialized.get("summary") if isinstance(sanitized_serialized, dict) else None
    if not summary:
        summary = redact_text(result.summary) if hasattr(result, "summary") else "Agno swarm completed."

    metadata = {
        "agent": "agno",
        "success": True,
        "summary": summary,
        "artifact_path": str(artifact_path),
        "decisions": decisions,
        "tests": tests,
    }
    metadata.update(provider_metadata("agno", model_override or agno_cfg.coder_model))
    metadata.update(collect_repo_state(memory_dir.parent))
    metadata_path.write_text(json.dumps(redact_payload(metadata), indent=2), encoding="utf-8")

    decisions_text = ", ".join(decisions[:5]) if decisions else "(none recorded)"
    tests_text = ", ".join(tests[:5]) if tests else "(none recorded)"
    append_text(
        memory_dir / "session-log.md",
        redact_text(
            SESSION_SECTION_TEMPLATE.format(
                timestamp=start_ts.strftime("%Y-%m-%d %H:%M:%S UTC"),
                task=task,
                status="OK",
                decisions=decisions_text,
                tests=tests_text,
                notes=summary,
            )
        ),
    )
    append_jsonl(
        memory_dir / "events.jsonl",
        redact_payload(
            {
                "timestamp": start_ts.isoformat(),
                "agent": "agno",
                "command": "agno",
                "output_preview": summary[:800],
                "metadata": metadata,
            }
        ),
    )

    return AgentResult(output=redact_text(summary), metadata=metadata, run_dir=run_dir)


__all__ = ["run"]
