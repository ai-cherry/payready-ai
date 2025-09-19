"""Typer-based unified CLI routing Codex, Claude, and Agno agents."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import typer

from .agents import AgentResult, run_agno, run_claude, run_codex
from .agents.context import load_context
from .config import Settings, configure_logging, load_settings

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


def main_entry() -> None:
    """Console-script entry point."""

    app()


__all__ = ["app", "main_entry"]
