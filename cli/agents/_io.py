"""Utility helpers for persisting agent memory artifacts."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

try:
    import fcntl  # type: ignore[attr-defined]
except ImportError:  # pragma: no cover - Windows fallback
    fcntl = None  # type: ignore


def _locked_write(handle, data: str) -> None:
    if fcntl is not None:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
    handle.write(data)
    handle.flush()
    if fcntl is not None:
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def append_text(path: Path, text: str) -> None:
    """Append UTF-8 text ensuring parent directories exist."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        payload = f"{text}\n" if text and not text.endswith("\n") else text
        _locked_write(handle, payload)


def append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    """Append a JSON line to the target file."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        serialized = json.dumps(payload, ensure_ascii=False)
        _locked_write(handle, f"{serialized}\n")


def new_run_dir(memory_dir: Path) -> Path:
    """Return a new per-run directory inside the memory hierarchy."""

    runs_dir = memory_dir / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    candidate = runs_dir / timestamp
    # Ensure uniqueness if called multiple times within the same microsecond
    if candidate.exists():
        candidate = runs_dir / f"{timestamp}-{uuid4().hex[:8]}"
    candidate.mkdir(parents=True, exist_ok=False)

    latest_link = runs_dir / "latest"
    if latest_link.exists() or latest_link.is_symlink():
        latest_link.unlink()
    try:
        latest_link.symlink_to(candidate, target_is_directory=True)
    except OSError:  # pragma: no cover - filesystems without symlink support
        pass

    return candidate


__all__ = ["append_text", "append_jsonl", "new_run_dir"]
