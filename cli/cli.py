"""Typer-based unified CLI routing Codex, Claude, and Agno agents."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import typer

from .agents import AgentResult, run_agno, run_claude, run_codex
from .agents._io import append_jsonl, append_text, new_run_dir
from .agents.context import load_context
from .agents.metadata import collect_repo_state, redact_payload, redact_text
from .config import Settings, configure_logging, load_settings
from .research.providers import (
    ProviderExecutionError,
    ProviderNotConfigured,
    ProviderRegistry,
    redact_response,
    summarise_items,
)
from tekton.swarm import run as run_diamond

app = typer.Typer(help="Unified terminal interface for Codex, Claude, and Agno agents.")

DEFAULT_MEMORY_DIR = Path(".project") / "memory"


@dataclass
class CLIState:
    """Runtime information shared across commands."""

    memory_dir: Path
    context_file: Optional[Path]
    settings: Settings


def _ensure_memory_layout(memory_dir: Path) -> None:
    """Create the expected memory directory hierarchy if missing."""

    (memory_dir / "runs").mkdir(parents=True, exist_ok=True)
    (memory_dir / "logs").mkdir(parents=True, exist_ok=True)


@app.callback()
def main(
    ctx: typer.Context,
    memory: Path = typer.Option(
        DEFAULT_MEMORY_DIR,
        "--memory",
        "-m",
        help="Directory used for session memory artifacts.",
    ),
    context: Optional[Path] = typer.Option(
        None,
        "--context",
        "-c",
        help="Optional file with additional context injected before prompts.",
    ),
) -> None:
    """Initialise global state, logging, and shared directories."""

    try:
        settings = load_settings()
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        typer.secho(f"Configuration error: {exc}", err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc
    memory_dir = memory.expanduser().resolve()
    _ensure_memory_layout(memory_dir)
    try:
        configure_logging(memory_dir)
    except Exception as exc:  # pragma: no cover - defensive logging fallback
        typer.secho(f"Failed to configure logging: {exc}", err=True, fg=typer.colors.YELLOW)

    if context is not None:
        context = context.expanduser().resolve()
        if not context.exists():
            raise typer.BadParameter(f"Context file not found: {context}")

    ctx.obj = CLIState(memory_dir=memory_dir, context_file=context, settings=settings)


@app.command(help="Run a prompt through Claude via Portkey.")
def claude(
    ctx: typer.Context,
    prompt: str = typer.Argument(..., help="Natural language request."),
    model: Optional[str] = typer.Option(None, help="Override Claude model."),
    temperature: Optional[float] = typer.Option(None, help="Override sampling temperature."),
) -> None:
    state: CLIState = ctx.ensure_object(CLIState)
    context_payload = load_context(state.memory_dir, state.context_file)

    result: AgentResult = run_claude(
        prompt=prompt,
        memory_dir=state.memory_dir,
        context=context_payload,
        settings=state.settings,
        model_override=model,
        temperature_override=temperature,
    )

    typer.echo(result.output)


@app.command(help="Run a prompt through Codex via subprocess dispatcher.")
def codex(
    ctx: typer.Context,
    prompt: str = typer.Argument(..., help="Prompt forwarded to Codex."),
    model: Optional[str] = typer.Option(None, help="Override Codex model when supported."),
) -> None:
    state: CLIState = ctx.ensure_object(CLIState)
    context_payload = load_context(state.memory_dir, state.context_file)

    result: AgentResult = run_codex(
        prompt=prompt,
        memory_dir=state.memory_dir,
        context=context_payload,
        settings=state.settings,
        model_override=model,
    )

    typer.echo(result.output)


@app.command(help="Launch Agno planner/coder/reviewer swarm for complex tasks.")
def agno(
    ctx: typer.Context,
    task: str = typer.Argument(..., help="High-level task for the swarm."),
    model: Optional[str] = typer.Option(None, help="Override default coder model."),
    dry_run: bool = typer.Option(False, help="Describe the swarm plan without execution."),
) -> None:
    state: CLIState = ctx.ensure_object(CLIState)
    context_payload = load_context(state.memory_dir, state.context_file)

    result: AgentResult = run_agno(
        task=task,
        memory_dir=state.memory_dir,
        context=context_payload,
        settings=state.settings,
        model_override=model,
        dry_run=dry_run,
    )

    if result.output:
        typer.echo(result.output)


@app.command(help="Run external web research with configured providers.")
def research(
    ctx: typer.Context,
    query: str = typer.Argument(..., help="Research question or keywords."),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Provider name (default auto)."),
    count: int = typer.Option(5, "--count", min=1, max=20, help="Maximum number of items to return."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output instead of a summary."),
) -> None:
    state: CLIState = ctx.ensure_object(CLIState)
    registry = ProviderRegistry(state.settings.research)
    resolved_provider = provider or registry.default_provider

    try:
        handler = registry.get(resolved_provider)
    except ProviderNotConfigured as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc
    except ProviderExecutionError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    run_dir = new_run_dir(state.memory_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = run_dir / "prompt.md"
    prompt_path.write_text(redact_text(query), encoding="utf-8")
    response_path = run_dir / "response.json"

    start_ts = datetime.now(timezone.utc)

    try:
        provider_response = handler.search(query, count=count)
    except ProviderNotConfigured as exc:
        metadata = {
            "provider": resolved_provider,
            "query": query,
            "success": False,
            "error": str(exc),
        }
        metadata.update(collect_repo_state(state.memory_dir.parent))
        append_jsonl(
            state.memory_dir / "events.jsonl",
            redact_payload(
                {
                    "timestamp": start_ts.isoformat(),
                    "agent": "research",
                    "command": "research",
                    "output_preview": str(exc)[:800],
                    "metadata": metadata,
                }
            ),
        )
        append_text(
            state.memory_dir / "session-log.md",
            redact_text(
                f"### {start_ts.strftime('%Y-%m-%d %H:%M:%S UTC')} · Research\n"
                f"Provider: {resolved_provider}\nOutcome: FAILED\nNotes: {exc}\n"
            ),
        )
        raise typer.Exit(code=1) from exc
    except ProviderExecutionError as exc:
        metadata = {
            "provider": resolved_provider,
            "query": query,
            "success": False,
            "error": str(exc),
        }
        metadata.update(collect_repo_state(state.memory_dir.parent))
        append_jsonl(
            state.memory_dir / "events.jsonl",
            redact_payload(
                {
                    "timestamp": start_ts.isoformat(),
                    "agent": "research",
                    "command": "research",
                    "output_preview": str(exc)[:800],
                    "metadata": metadata,
                }
            ),
        )
        append_text(
            state.memory_dir / "session-log.md",
            redact_text(
                f"### {start_ts.strftime('%Y-%m-%d %H:%M:%S UTC')} · Research\n"
                f"Provider: {resolved_provider}\nOutcome: FAILED\nNotes: {exc}\n"
            ),
        )
        raise typer.Exit(code=1) from exc

    sanitized = redact_response(provider_response)
    response_payload = {
        "items": sanitized.items,
        "raw": sanitized.raw,
    }
    response_path.write_text(json.dumps(response_payload, indent=2), encoding="utf-8")

    summary = summarise_items(sanitized.items, limit=count)
    metadata = {
        "provider": sanitized.provider,
        "query": sanitized.query,
        "count": count,
        "items_returned": len(sanitized.items),
        "success": True,
        "response_path": str(response_path),
        "run_dir": str(run_dir),
    }
    metadata.update(collect_repo_state(state.memory_dir.parent))

    append_text(
        state.memory_dir / "session-log.md",
        redact_text(
            f"### {start_ts.strftime('%Y-%m-%d %H:%M:%S UTC')} · Research\n"
            f"Provider: {sanitized.provider}\nOutcome: OK\nSummary: {summary}\n"
        ),
    )
    append_jsonl(
        state.memory_dir / "events.jsonl",
        redact_payload(
            {
                "timestamp": start_ts.isoformat(),
                "agent": "research",
                "command": "research",
                "output_preview": summary[:800],
                "metadata": metadata,
            }
        ),
    )

    if json_output:
        typer.echo(json.dumps(response_payload, indent=2))
    else:
        typer.echo(summary)


def _serialise_result(payload: Dict[str, object]) -> Dict[str, object]:
    def _convert(value: object) -> object:
        if hasattr(value, "json") and callable(getattr(value, "json")):
            try:
                return json.loads(value.json())  # type: ignore[no-any-return]
            except Exception:  # pragma: no cover - defensive fallback
                return value
        if isinstance(value, dict):
            return {key: _convert(val) for key, val in value.items()}
        if isinstance(value, list):
            return [_convert(item) for item in value]
        return value

    return _convert(payload)  # type: ignore[return-value]


@app.command(help="Run the staged Diamond v5 workflow (Plan → Release).")
def diamond(
    ctx: typer.Context,
    goal: str = typer.Argument(..., help="High-level goal/problem statement."),
    start: str = typer.Option("plan", "--from", help="First stage to execute."),
    end: str = typer.Option("release", "--to", help="Last stage to execute."),
    consensus_free: List[str] = typer.Option(
        [],
        "--consensus-free",
        help="Stages to run in consensus-free mode (e.g. code test_debug).",
    ),
    resume: Optional[str] = typer.Option(None, help="Resume from a previous run ID."),
    model: Optional[str] = typer.Option(None, help="Override default model for all stages."),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        dir_okay=True,
        file_okay=False,
        help="Directory for persisted artifacts (defaults inside the memory run folder).",
    ),
) -> None:
    state: CLIState = ctx.ensure_object(CLIState)
    run_dir = new_run_dir(state.memory_dir)
    artifact_dir = output.expanduser().resolve() if output else (run_dir / "artifacts")
    artifact_dir.mkdir(parents=True, exist_ok=True)

    start_ts = datetime.now(timezone.utc)
    try:
        result = asyncio.run(
            run_diamond(
                goal=goal,
                start=start,
                end=end,
                consensus_free=tuple(consensus_free),
                resume=resume,
                model_override=model,
                output_dir=artifact_dir,
            )
        )
    except Exception as exc:  # pragma: no cover - defensive guard
        metadata = {
            "workflow": "diamond",
            "goal": goal,
            "start": start,
            "end": end,
            "success": False,
            "error": str(exc),
            "artifact_dir": str(artifact_dir),
        }
        metadata.update(collect_repo_state(state.memory_dir.parent))
        append_jsonl(
            state.memory_dir / "events.jsonl",
            redact_payload(
                {
                    "timestamp": start_ts.isoformat(),
                    "agent": "diamond",
                    "command": "diamond",
                    "output_preview": str(exc)[:800],
                    "metadata": metadata,
                }
            ),
        )
        append_text(
            state.memory_dir / "session-log.md",
            redact_text(
                f"### {start_ts.strftime('%Y-%m-%d %H:%M:%S UTC')} · Diamond\n"
                f"Goal: {goal}\nOutcome: FAILED\nNotes: {exc}\n"
            ),
        )
        raise typer.Exit(code=1) from exc

    serialisable = _serialise_result(result)
    if not isinstance(serialisable, dict):  # pragma: no cover - defensive fallback
        serialisable = {"results": serialisable}
    stages = list(serialisable.get("results", {}).keys())
    summary_path = run_dir / "diamond_summary.json"
    summary_path.write_text(json.dumps(serialisable, indent=2), encoding="utf-8")

    summary_snippet = ", ".join(stages)
    metadata = {
        "workflow": "diamond",
        "goal": goal,
        "start": start,
        "end": end,
        "consensus_free": list(consensus_free),
        "resume": resume,
        "artifact_dir": str(artifact_dir),
        "summary_path": str(summary_path),
        "stages_completed": stages,
        "success": True,
    }
    metadata.update(collect_repo_state(state.memory_dir.parent))

    append_text(
        state.memory_dir / "session-log.md",
        redact_text(
            f"### {start_ts.strftime('%Y-%m-%d %H:%M:%S UTC')} · Diamond\n"
            f"Goal: {goal}\nOutcome: OK\nStages: {summary_snippet}\n"
        ),
    )
    append_jsonl(
        state.memory_dir / "events.jsonl",
        redact_payload(
            {
                "timestamp": start_ts.isoformat(),
                "agent": "diamond",
                "command": "diamond",
                "output_preview": summary_snippet[:800],
                "metadata": metadata,
            }
        ),
    )

    typer.echo(f"Diamond workflow complete. Summary saved to {summary_path}")


def main_entry() -> None:
    """Console-script entry point."""

    app()


__all__ = ["app", "main_entry"]
