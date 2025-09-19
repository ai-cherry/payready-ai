"""Secret loader with offline mode support and environment fallbacks."""

from __future__ import annotations

import os
from typing import Optional

SERVICE_NAME = "payready"


def get(name: str, env: Optional[str] = None, required: bool = True, default: Optional[str] = None) -> Optional[str]:
    """Retrieve a secret with offline mode support and environment fallbacks.

    Parameters
    ----------
    name:
        Logical secret name.
    env:
        Optional environment variable name to use as lookup.
    required:
        When True, a missing secret raises ``RuntimeError``. Otherwise ``None`` is returned.
    default:
        Default value to return in offline mode.
    """

    # In offline mode, always return stub values silently
    if os.getenv("PAYREADY_OFFLINE_MODE") == "1":
        return default or "stub"

    # Try environment first
    if env:
        fallback = os.getenv(env)
        if fallback:
            return fallback

    # Try keyring only if not in offline mode and keyring is available
    if os.getenv("KEYRING_BACKEND") != "keyring.backends.null.Keyring":
        try:
            import keyring
            value = keyring.get_password(SERVICE_NAME, name)
            if value:
                return value
        except Exception:
            # Keyring may not be available or configured
            pass

    if required:
        raise RuntimeError(f"Missing secret: {name} (keychain) and {env or 'N/A'} (env)")
    return None


__all__ = ["get", "SERVICE_NAME"]
