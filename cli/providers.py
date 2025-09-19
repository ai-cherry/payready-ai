"""Provider-specific client constructors with keyring-backed auth."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any, Optional

from .secrets import get


class StubResponse:
    """Stub response for offline mode."""
    def __init__(self, content: str):
        self.content = content
        # Create message and choice objects
        message = type('Message', (object,), {'content': content})()
        choice = type('Choice', (object,), {'message': message})()
        self.choices = [choice]
        self.usage = type('Usage', (object,), {
            'total_tokens': 100,
            'prompt_tokens': 50,
            'completion_tokens': 50
        })()
        self.model = "stub-model"
        self.id = "stub-response-id"


class StubClient:
    """Stub client for offline mode."""

    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.chat = self
        self.completions = self
        self.messages = self

    def create(self, **kwargs) -> StubResponse:
        """Create a stub completion response."""
        model = kwargs.get('model', 'unknown')
        messages = kwargs.get('messages', [])
        query = messages[-1].get('content', '') if messages else ''

        response = (
            f"🤖 Offline Mode Response from {self.provider_name}\n\n"
            f"Model: {model}\n"
            f"Query: {query[:100]}...\n\n"
            f"This is a stub response for local development.\n"
            f"The system is running in offline mode without real API calls."
        )
        return StubResponse(response)

    def generate(self, **kwargs) -> StubResponse:
        """Alias for create (some clients use generate)."""
        return self.create(**kwargs)


@lru_cache(maxsize=None)
def _openai_client_from_base(base_env: str):
    # In offline mode, return stub client
    if os.getenv("PAYREADY_OFFLINE_MODE") == "1":
        return StubClient("OpenAI-Compatible")

    from openai import OpenAI

    base_url = os.environ[base_env]
    api_key = get("OPENAI_API_KEY", env="OPENAI_API_KEY")
    return OpenAI(base_url=base_url, api_key=api_key)


@lru_cache(maxsize=None)
def client_openrouter():
    # In offline mode, return stub client
    if os.getenv("PAYREADY_OFFLINE_MODE") == "1":
        return StubClient("OpenRouter")

    os.environ.setdefault("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
    os.environ.setdefault("OPENROUTER_REFERER", "https://payready.ai")
    os.environ.setdefault("OPENROUTER_TITLE", "PayReady AI CLI")
    return _openai_client_from_base("OPENAI_BASE_URL")


@lru_cache(maxsize=None)
def client_openai():
    # In offline mode, return stub client
    if os.getenv("PAYREADY_OFFLINE_MODE") == "1":
        return StubClient("OpenAI")

    from openai import OpenAI

    return OpenAI(api_key=get("OPENAI_API_KEY", env="OPENAI_API_KEY"))


@lru_cache(maxsize=None)
def client_together():
    # In offline mode, return stub client
    if os.getenv("PAYREADY_OFFLINE_MODE") == "1":
        return StubClient("Together")

    from together import Together

    return Together(api_key=get("TOGETHER_API_KEY", env="TOGETHER_API_KEY"))


@lru_cache(maxsize=None)
def client_anthropic():
    # In offline mode, return stub client
    if os.getenv("PAYREADY_OFFLINE_MODE") == "1":
        return StubClient("Anthropic")

    import anthropic

    return anthropic.Anthropic(api_key=get("ANTHROPIC_API_KEY", env="ANTHROPIC_API_KEY"))


@lru_cache(maxsize=None)
def client_xai():
    # In offline mode, return stub client
    if os.getenv("PAYREADY_OFFLINE_MODE") == "1":
        return StubClient("xAI")

    os.environ.setdefault("OPENAI_BASE_URL", "https://api.x.ai/v1")
    return _openai_client_from_base("OPENAI_BASE_URL")


@lru_cache(maxsize=None)
def client_deepseek():
    # In offline mode, return stub client
    if os.getenv("PAYREADY_OFFLINE_MODE") == "1":
        return StubClient("DeepSeek")

    os.environ.setdefault("OPENAI_BASE_URL", "https://api.deepseek.com/v1")
    return _openai_client_from_base("OPENAI_BASE_URL")


__all__ = [
    "client_anthropic",
    "client_deepseek",
    "client_openai",
    "client_openrouter",
    "client_together",
    "client_xai",
]
