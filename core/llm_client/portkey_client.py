"""Minimal Portkey client wrapper used by the Diamond CLI."""

from __future__ import annotations

import os
from typing import List, Dict

import requests


def chat(model: str, messages: List[Dict[str, str]], *, virtual_key: str | None = None, timeout: int = 120) -> str:
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.portkey.ai/v1")
    api_key = os.getenv("PORTKEY_API_KEY")
    if not api_key:
        raise RuntimeError("PORTKEY_API_KEY is not configured.")

    url = f"{base_url}/chat/completions"
    headers = {
        "x-portkey-api-key": api_key,
        "Content-Type": "application/json",
    }
    body = {
        "model": model,
        "messages": messages,
    }
    if virtual_key:
        body["virtual_key"] = virtual_key
    response = requests.post(url, json=body, headers=headers, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()


__all__ = ["chat"]
