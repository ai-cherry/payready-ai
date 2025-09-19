"""Utilities for loading contextual memory for agent prompts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def _read_tail(path: Path, limit: int = 50) -> List[Dict[str, Any]]:
    """Return the most recent JSONL entries from a file."""

    if not path.exists():
        return []

    lines = path.read_text(encoding="utf-8").splitlines()[-limit:]
    records: List[Dict[str, Any]] = []
    for line in lines:
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def summaries_from_runs(memory_dir: Path, limit: int = 5) -> List[Dict[str, Any]]:
    """Return metadata summaries from the most recent run directories."""

    runs_dir = memory_dir / "runs"
    if not runs_dir.exists():
        return []

    run_dirs = sorted(
        [path for path in runs_dir.iterdir() if path.is_dir() and not path.is_symlink()],
        key=lambda item: item.name,
        reverse=True,
    )

    summaries: List[Dict[str, Any]] = []
    for run_path in run_dirs[:limit]:
        metadata_path = run_path / "metadata.json"
        if metadata_path.exists():
            try:
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                metadata = {}
        else:
            metadata = {}
        metadata.setdefault("run_id", run_path.name)
        summaries.append(metadata)
    return summaries


def load_context(memory_dir: Path, context_file: Optional[Path] = None) -> Dict[str, Any]:
    """Aggregate available memory artefacts for agent consumption."""

    session_log = memory_dir / "session-log.md"
    session_markdown = session_log.read_text(encoding="utf-8") if session_log.exists() else ""

    events = _read_tail(memory_dir / "events.jsonl")
    recent_runs = summaries_from_runs(memory_dir)

    extra_context: Optional[str] = None
    if context_file is not None and context_file.exists():
        extra_context = context_file.read_text(encoding="utf-8")

    return {
        "session_markdown": session_markdown,
        "events": events,
        "recent_runs": recent_runs,
        "extra_context": extra_context,
    }


__all__ = ["load_context", "summaries_from_runs"]
