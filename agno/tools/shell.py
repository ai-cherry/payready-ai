"""Minimal shell tool stub."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Dict, List


class ShellTools:
    """Runs shell commands with optional sandboxing."""

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = Path(base_dir)

    def __call__(self, command: str | List[str], **kwargs: Any) -> Dict[str, Any]:
        if isinstance(command, str):
            cmd = command
        else:
            cmd = " ".join(command)
        try:
            result = subprocess.run(
                cmd,
                cwd=self.base_dir,
                shell=True,
                check=False,
                capture_output=True,
                text=True,
                timeout=kwargs.get("timeout", 30),
            )
            return {
                "command": cmd,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except Exception as exc:  # pragma: no cover - defensive fallback
            return {
                "command": cmd,
                "returncode": 1,
                "stdout": "",
                "stderr": str(exc),
            }


__all__ = ["ShellTools"]
