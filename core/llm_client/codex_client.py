"""Wrapper for the official Codex CLI (ChatGPT-authenticated)."""

from __future__ import annotations

import shutil
import subprocess
from typing import List


class CodexError(RuntimeError):
    """Raised when the Codex CLI returns a non-zero exit code."""


def chat(prompt: str, *, model: str = "gpt-5-codex") -> str:
    """Execute the codex CLI and return stdout."""

    if shutil.which("codex") is None:
        raise CodexError("codex CLI not found in PATH. Run `npm install -g @openai/codex`.")

    cmd: List[str] = ["codex", "exec", "--model", model, prompt]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as exc:  # noqa: PERF203
        stderr = exc.stderr.strip() if exc.stderr else "codex CLI failed"
        raise CodexError(stderr) from exc
    return proc.stdout.strip()


__all__ = ["chat", "CodexError"]
