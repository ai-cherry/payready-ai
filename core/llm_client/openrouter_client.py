"""OpenRouter client - primary LLM provider."""

import os
import requests
from typing import List, Dict, Optional

class OpenRouterClient:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"

    def chat(self, model: str, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send chat completion request to OpenRouter."""
        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY not configured")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://payready.ai",
            "X-Title": "PayReady AI",
            "Content-Type": "application/json"
        }

        timeout = kwargs.pop("timeout", 120)

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json={
                "model": model,
                "messages": messages,
                **kwargs
            },
            timeout=timeout
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()

def chat(model: str, messages: List[Dict[str, str]], **kwargs) -> str:
    """Convenience function matching old portkey interface."""
    client = OpenRouterClient()
    return client.chat(model, messages, **kwargs)

__all__ = ["OpenRouterClient", "chat"]