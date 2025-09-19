"""Compatibility shim forwarding to `tekton` package."""

from tekton.swarm import *  # noqa: F401,F403

__all__ = ["describe", "run", "STAGES"]
