#!/usr/bin/env python3
"""Quick environment sanity check for Diamond v5."""

from __future__ import annotations

import os
from pathlib import Path

REQUIRED_ANY = ["PORTKEY_API_KEY", "OPENROUTER_API_KEY"]
REQUIRED_VIRTUAL_KEYS = [
    "PORTKEY_VK_XAI",
    "PORTKEY_VK_ANTHROPIC",
    "PORTKEY_VK_OPENAI",
    "PORTKEY_VK_PERPLEXITY",
]
OPTIONAL_SERVICES = [
    "AGNO__REDIS_URL",
    "AGNO__PG_DSN",
    "AGNO__WEAVIATE_URL",
    "MILVUS_URI",
]


def main() -> None:
    missing = []

    if not any(os.getenv(key) for key in REQUIRED_ANY):
        missing.extend(REQUIRED_ANY)

    missing.extend(key for key in REQUIRED_VIRTUAL_KEYS if not os.getenv(key))

    if missing:
        print("Environment check failed. Missing keys:")
        for key in missing:
            print(f"  - {key}")
        raise SystemExit(1)

    print("✓ Core LLM routing keys present.")

    for key in OPTIONAL_SERVICES:
        if os.getenv(key):
            print(f"✓ {key} set")
        else:
            print(f"• {key} not set (optional)")

    codex_config = Path.home() / ".codex" / "config.toml"
    if codex_config.exists():
        print(f"✓ Codex config located at {codex_config}")
    else:
        print("• Codex config not found; run `codex exec` to initialise ChatGPT login.")


if __name__ == "__main__":
    main()
