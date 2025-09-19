"""Backwards-compatible entrypoint delegating to Tekton CLI."""

from __future__ import annotations

from tekton.cli import main, parse_args  # noqa: F401

__all__ = ["main", "parse_args"]
