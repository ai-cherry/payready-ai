"""Adaptive Agno import that prefers the real package when available."""

from __future__ import annotations

import os
import sys
from pathlib import Path
import importlib
import importlib.util


def _load_real_agno():
    """Attempt to import the real Agno package outside the repo tree."""

    if os.getenv("PAYREADY_FORCE_AGNO_STUBS", "0") == "1":
        return None

    project_root = Path(__file__).resolve().parent.parent
    original_sys_path = list(sys.path)

    try:
        # Temporarily remove the repo root so site-packages can be discovered first
        sys.path = [p for p in sys.path if Path(p).resolve() != project_root]
        spec = importlib.util.find_spec("agno")
        if spec and spec.loader and spec.origin:
            # Ensure we did not just rediscover this stub module
            if Path(spec.origin).resolve() != Path(__file__).resolve():
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
    except Exception:
        return None
    finally:
        sys.path = original_sys_path

    return None


_real_agno = _load_real_agno()

if _real_agno is not None:
    # Mirror key attributes so downstream imports behave exactly as the real package
    sys.modules[__name__] = _real_agno
    globals().update({
        "__all__": getattr(_real_agno, "__all__", []),
        "__path__": getattr(_real_agno, "__path__", []),
        "__file__": getattr(_real_agno, "__file__", __file__),
        "__package__": _real_agno.__package__ or "agno",
    })
    for attr in dir(_real_agno):
        if attr.startswith("__") and attr not in {"__all__", "__path__", "__file__", "__package__"}:
            continue
        globals()[attr] = getattr(_real_agno, attr)

    # Pre-populate common submodules so caller imports resolve to the real package
    for submodule in (
        "agent",
        "team",
        "memory",
        "tools",
        "tools.python",
        "models",
        "models.openai",
        "models.anthropic",
        "models.groq",
    ):
        full_name = f"{__name__}.{submodule}"
        if full_name in sys.modules:
            continue
        try:
            sys.modules[full_name] = importlib.import_module(full_name)
        except Exception:
            # Some optional providers might not exist; ignore quietly
            pass
else:
    # Fall back to local stubs for offline development
    from .agent import Agent  # noqa: F401
    from .team import Team  # noqa: F401
    from .memory import MemoryManager, UserMemory  # noqa: F401

    __all__ = [
        "Agent",
        "Team",
        "MemoryManager",
        "UserMemory",
    ]
