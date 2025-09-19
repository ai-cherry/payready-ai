"""Claude adapter using Portkey for OpenAI-compatible access."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import httpx
import typer

from ._io import append_jsonl, append_text, new_run_dir
from .metadata import collect_repo_state, provider_metadata, redact_payload, redact_text
from .result import AgentResult
from ..config import Settings

SESSION_SECTION_TEMPLATE = """### {timestamp} · Claude

Prompt: {prompt}
Model: {model}
Temperature: {temperature}
Outcome: {status}
Notes: {notes}
"""


def _build_context_blob(context: Dict[str, Any], max_chars: int) -> str:
    sections: list[str] = []
    session_markdown = (context.get("session_markdown") or "").strip()
    if session_markdown:
        sections.append(f"Session Journal\n{session_markdown[-max_chars:]}")

    events = context.get("events") or []
    if events:
        formatted = "\n".join(
            f"- {event.get('timestamp', '')}: {event.get('agent', '')} → {event.get('output_preview', '')}"
            for event in events[-10:]
        )
        sections.append(f"Recent Events\n{formatted}")

    runs = context.get("recent_runs") or []
    if runs:
        formatted_runs = "\n".join(
            f"- {run.get('run_id')}: {run.get('summary', run.get('status', 'n/a'))}" for run in runs
        )
        sections.append(f"Recent Runs\n{formatted_runs}")

    extra = context.get("extra_context")
    if extra:
        sections.append(f"Extra Context\n{extra}")

    blob = "\n\n".join(filter(None, sections))
    if len(blob) > max_chars:
        blob = blob[-max_chars:]
    return blob


def run(
    *,
    prompt: str,
    memory_dir: Path,
    context: Dict[str, Any],
    settings: Settings,
    model_override: Optional[str] = None,
    temperature_override: Optional[float] = None,
) -> AgentResult:
    claude_cfg = settings.agents.claude
    model = model_override or claude_cfg.model
    temperature = temperature_override if temperature_override is not None else claude_cfg.temperature

    run_dir = new_run_dir(memory_dir)
    prompt_path = run_dir / "prompt.md"
    response_path = run_dir / "response.md"
    metadata_path = run_dir / "metadata.json"

    context_blob = _build_context_blob(context, claude_cfg.max_context_chars)
    composed_prompt = prompt
    if context_blob:
        composed_prompt = f"Context:\n{context_blob}\n\nTask:\n{prompt}"

    sanitized_prompt = redact_text(composed_prompt)
    prompt_path.write_text(sanitized_prompt, encoding="utf-8")

    headers = {
        "x-portkey-api-key": settings.portkey.api_key,
        "x-portkey-virtual-key": settings.portkey.virtual_key,
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "temperature": temperature,
        "max_tokens": claude_cfg.max_tokens,
        "messages": [
            {"role": "system", "content": claude_cfg.system_prompt},
            {"role": "user", "content": composed_prompt},
        ],
    }

    start_ts = datetime.now(timezone.utc)
    start = time.perf_counter()

    client = httpx.Client(
        timeout=httpx.Timeout(connect=5.0, read=claude_cfg.http_timeout),
    )
    response = None
    try:
        for attempt in range(4):
            try:
                response = client.post(
                    settings.portkey.base_url.rstrip("/") + "/chat/completions",
                    headers=headers,
                    json=payload,
                )
                if response.status_code in {429, 500, 502, 503, 504}:
                    time.sleep(0.5 * (2 ** attempt))
                    continue
                response.raise_for_status()
                break
            except httpx.HTTPError as exc:  # pragma: no cover - network errors difficult to mock fully
                if attempt == 3:
                    raise
                time.sleep(0.5 * (2 ** attempt))
        else:
            response = client.post(
                settings.portkey.base_url.rstrip("/") + "/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
    except httpx.HTTPError as exc:
        duration = time.perf_counter() - start
        metadata = {
            "agent": "claude",
            "model": model,
            "temperature": temperature,
            "duration_sec": duration,
            "success": False,
            "error": str(exc),
        }
        metadata_path.write_text(json.dumps(redact_payload(metadata), indent=2), encoding="utf-8")
        event_payload = {
            "timestamp": start_ts.isoformat(),
            "agent": "claude",
            "command": "claude",
            "output_preview": f"HTTP error: {exc}",
            "metadata": {
                **metadata,
                **collect_repo_state(memory_dir.parent),
            },
        }
        append_jsonl(memory_dir / "events.jsonl", redact_payload(event_payload))
        append_text(
            memory_dir / "session-log.md",
            redact_text(
                SESSION_SECTION_TEMPLATE.format(
                    timestamp=start_ts.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    prompt=prompt,
                    model=model,
                    temperature=temperature,
                    status="FAILED",
                    notes=str(exc),
                )
            ),
        )
        raise typer.Exit(code=1) from exc
    finally:
        client.close()

    duration = time.perf_counter() - start
    data = response.json()
    message = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    sanitized_response = redact_text(message)
    response_path.write_text(sanitized_response, encoding="utf-8")

    usage = data.get("usage", {})
    metadata = {
        "agent": "claude",
        "model": model,
        "temperature": temperature,
        "duration_sec": duration,
        "success": True,
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
        "summary": sanitized_response[:200].strip(),
    }
    metadata.update(provider_metadata("portkey", model, usage))
    metadata.update(collect_repo_state(memory_dir.parent))
    metadata_path.write_text(json.dumps(redact_payload(metadata), indent=2), encoding="utf-8")

    append_text(
        memory_dir / "session-log.md",
        redact_text(
            SESSION_SECTION_TEMPLATE.format(
                timestamp=start_ts.strftime("%Y-%m-%d %H:%M:%S UTC"),
                prompt=prompt,
                model=model,
                temperature=temperature,
                status="OK",
                notes=metadata["summary"],
            )
        ),
    )
    event_payload = {
        "timestamp": start_ts.isoformat(),
        "agent": "claude",
        "command": "claude",
        "output_preview": sanitized_response[:800],
        "metadata": metadata,
    }
    append_jsonl(memory_dir / "events.jsonl", redact_payload(event_payload))

    return AgentResult(output=sanitized_response, metadata=metadata, run_dir=run_dir)


__all__ = ["run"]
