"""Codex adapter invoking local CLI with subprocess."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import typer

from ._io import append_jsonl, append_text, new_run_dir
from .metadata import collect_repo_state, provider_metadata, redact_payload, redact_text
from .result import AgentResult
from ..config import Settings

SESSION_SECTION_TEMPLATE = """### {timestamp} · Codex

Prompt: {prompt}
Model: {model}
Outcome: {status}
Notes: {notes}
"""


def _compose_stdin(prompt: str, context: Dict[str, Any], max_chars: int) -> str:
    session = (context.get("session_markdown") or "")
    events = context.get("events") or []
    runs = context.get("recent_runs") or []

    sections: list[str] = []
    if session:
        sections.append(f"Session Journal:\n{session[-max_chars:]}")
    if events:
        formatted = "\n".join(
            f"- {event.get('timestamp', '')} {event.get('agent', '')}: {event.get('output_preview', '')}"
            for event in events[-10:]
        )
        sections.append(f"Recent Events:\n{formatted}")
    if runs:
        formatted_runs = "\n".join(
            f"- {run.get('run_id')}: {run.get('summary', run.get('status', 'n/a'))}" for run in runs
        )
        sections.append(f"Recent Runs:\n{formatted_runs}")
    if context.get("extra_context"):
        sections.append(f"Extra Context:\n{context['extra_context']}")

    context_blob = "\n\n".join(sections)
    if context_blob and len(context_blob) > max_chars:
        context_blob = context_blob[-max_chars:]

    if context_blob:
        return f"{context_blob}\n\nTask:\n{prompt}\n"
    return prompt


def run(
    *,
    prompt: str,
    memory_dir: Path,
    context: Dict[str, Any],
    settings: Settings,
    model_override: Optional[str] = None,
) -> AgentResult:
    codex_cfg = settings.agents.codex
    model = model_override or codex_cfg.model
    binary = os.getenv("CODEX_BIN", codex_cfg.binary)
    if shutil.which(binary) is None:
        typer.secho(f"Codex binary not found: {binary}", err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1)
    run_dir = new_run_dir(memory_dir)
    stdin_payload = _compose_stdin(prompt, context, codex_cfg.max_context_chars)

    command = [binary, "--model", model, *codex_cfg.flags]

    prompt_path = run_dir / "prompt.md"
    prompt_path.write_text(redact_text(stdin_payload), encoding="utf-8")
    stdout_path = run_dir / "stdout.txt"
    stderr_path = run_dir / "stderr.txt"
    metadata_path = run_dir / "metadata.json"

    start_ts = datetime.now(timezone.utc)
    start = time.perf_counter()

    result = subprocess.run(
        command,
        input=stdin_payload.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=codex_cfg.timeout_sec,
        check=False,
    )

    duration = time.perf_counter() - start
    stdout = result.stdout.decode("utf-8", errors="replace")
    stderr = result.stderr.decode("utf-8", errors="replace")

    sanitized_stdout = redact_text(stdout)
    sanitized_stderr = redact_text(stderr)
    stdout_path.write_text(sanitized_stdout, encoding="utf-8")
    if stderr:
        stderr_path.write_text(sanitized_stderr, encoding="utf-8")

    success = result.returncode == 0

    metadata = {
        "agent": "codex",
        "model": model,
        "success": success,
        "duration_sec": duration,
        "returncode": result.returncode,
        "stderr_preview": sanitized_stderr[:400],
        "summary": sanitized_stdout[:200].strip(),
    }
    metadata.update(provider_metadata("codex-cli", model))
    metadata.update(collect_repo_state(memory_dir.parent))
    metadata_path.write_text(json.dumps(redact_payload(metadata), indent=2), encoding="utf-8")

    status = "OK" if success else "FAILED"
    notes = metadata["summary"] if success else metadata.get("stderr_preview", "")
    append_text(
        memory_dir / "session-log.md",
        redact_text(
            SESSION_SECTION_TEMPLATE.format(
                timestamp=start_ts.strftime("%Y-%m-%d %H:%M:%S UTC"),
                prompt=prompt,
                model=model,
                status=status,
                notes=notes,
            )
        ),
    )
    event_payload = {
        "timestamp": start_ts.isoformat(),
        "agent": "codex",
        "command": "codex",
        "output_preview": (sanitized_stdout or sanitized_stderr)[:800],
        "metadata": metadata,
    }
    append_jsonl(memory_dir / "events.jsonl", redact_payload(event_payload))

    if not success:
        raise typer.Exit(code=result.returncode)

    return AgentResult(output=sanitized_stdout, metadata=metadata, run_dir=run_dir)


__all__ = ["run"]
