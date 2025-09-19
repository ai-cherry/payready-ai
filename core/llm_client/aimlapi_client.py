"""AIMLAPI client - backup LLM provider."""

import os
import requests
from typing import List, Dict, Optional

class AIMLAPIClient:
    def __init__(self):
        self.api_key = os.getenv("AIMLAPI_KEY")
        self.base_url = os.getenv("AIMLAPI_BASE_URL", "https://api.aimlapi.com/v1")

    def chat(self, model: str, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send chat completion request to AIMLAPI."""
        if not self.api_key:
            raise RuntimeError("AIMLAPI_KEY not configured")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
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
    """Convenience function for backward compatibility."""
    client = AIMLAPIClient()
    return client.chat(model, messages, **kwargs)

__all__ = ["AIMLAPIClient", "chat"]