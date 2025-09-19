"""Minimal Python execution tool stub."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


class PythonTools:
    """Records execution requests to keep agents satisfied during tests."""

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = Path(base_dir)

    def __call__(self, code: str, **_: Any) -> Dict[str, Any]:  # pragma: no cover - simple stub
        return {
            "stdout": "",
            "stderr": "",
            "result": f"Executed code in {self.base_dir}: {code[:40]}...",
        }


__all__ = ["PythonTools"]
