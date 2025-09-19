"""Agno swarm adapter coordinating planner, coder, and reviewer agents."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import typer

from ._io import append_jsonl, append_text, new_run_dir
from .metadata import collect_repo_state, provider_metadata, redact_payload, redact_text
from .result import AgentResult
from ..config import Settings

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
    try:
        from agno import Agent
    except ImportError as exc:  # pragma: no cover - dependency missing in some envs
        raise ImportError("Agno package not installed") from exc

    llm_overrides = {}
    if model_override:
        llm_overrides = {"model": model_override}

    def _agent(name: str, role: str, model: str) -> Any:
        kwargs = {
            "name": name,
            "role": role,
            "llm": {
                "api_key_env": "PORTKEY_API_KEY",
                "base_url_env": "OPENAI_BASE_URL",
                "model": model,
            },
            "markdown": True,
        }
        kwargs["llm"].update(llm_overrides)
        return Agent(**kwargs)

    agno_cfg = settings.agents.agno
    planner = _agent("Planner", "Break the task into executable steps.", agno_cfg.planner_model)
    coder = _agent("Coder", "Implement the plan and produce artifacts.", agno_cfg.coder_model)
    reviewer = _agent("Reviewer", "Review outputs for correctness and risk.", agno_cfg.reviewer_model)
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

    try:
        from agno.swarm import Swarm
    except ImportError as exc:  # pragma: no cover - dependency missing in some envs
        metadata = {
            "agent": "agno",
            "success": False,
            "error": "Agno swarm package not installed.",
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
    swarm = Swarm(planner=planner, worker=coder, reviewer=reviewer)

    try:
        result = swarm.run(task=task, context=context_blob)
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
