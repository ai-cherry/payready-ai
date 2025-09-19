"""Research provider implementations for payready-cli."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

import httpx

from ..agents.metadata import redact_payload
from ..config import ResearchEnvSettings


class ProviderExecutionError(Exception):
    """Raised when a provider request fails."""


class ProviderNotConfigured(Exception):
    """Raised when a provider is not configured with the required credentials."""


@dataclass
class ProviderResponse:
    provider: str
    query: str
    items: List[Dict[str, Any]]
    raw: Dict[str, Any]


class BaseProvider:
    name: str

    def __init__(self, settings: ResearchEnvSettings) -> None:
        self.settings = settings

    def is_configured(self) -> bool:
        raise NotImplementedError

    def search(self, query: str, *, count: int = 5) -> ProviderResponse:
        raise NotImplementedError


class BraveProvider(BaseProvider):
    name = "brave"
    endpoint = "https://api.search.brave.com/res/v1/web/search"

    def __init__(self, settings: ResearchEnvSettings, timeout: float = 20.0) -> None:
        super().__init__(settings)
        self.timeout = timeout

    @property
    def api_key(self) -> Optional[str]:
        return self.settings.brave_api_key

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def search(self, query: str, *, count: int = 5) -> ProviderResponse:
        if not self.is_configured():
            raise ProviderNotConfigured("BRAVE_API_KEY is required for the brave provider.")

        params = {
            "q": query,
            "count": max(1, min(count, 20)),
            "source": "web",
        }
        headers = {
            "X-Subscription-Token": self.api_key,
            "Accept": "application/json",
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(self.endpoint, params=params, headers=headers)
                response.raise_for_status()
        except httpx.HTTPError as exc:  # pragma: no cover - network environment
            raise ProviderExecutionError(str(exc)) from exc

        payload = response.json()
        results: List[Dict[str, Any]] = []
        for entry in payload.get("web", {}).get("results", [])[: params["count"]]:
            results.append(
                {
                    "title": entry.get("title"),
                    "url": entry.get("url"),
                    "summary": entry.get("description"),
                    "open_graph": entry.get("openGraph"),
                }
            )

        return ProviderResponse(
            provider=self.name,
            query=query,
            items=results,
            raw=payload,
        )


class PlaceholderProvider(BaseProvider):
    """Provider stub for services not yet fully implemented."""

    friendly_name: str
    env_keys: Iterable[str]

    def __init__(self, settings: ResearchEnvSettings, friendly_name: str, env_keys: Iterable[str]) -> None:
        super().__init__(settings)
        self.friendly_name = friendly_name
        self.env_keys = env_keys

    def is_configured(self) -> bool:
        for key in self.env_keys:
            if getattr(self.settings, key) is not None:
                return True
        return False

    def search(self, query: str, *, count: int = 5) -> ProviderResponse:
        missing_keys = ", ".join(self.env_keys)
        raise ProviderExecutionError(
            f"{self.friendly_name} provider is not yet integrated. Configure keys ({missing_keys}) "
            "and extend cli/research/providers.py to enable it."
        )


class ProviderRegistry:
    """Resolves research providers based on configuration."""

    def __init__(self, settings: ResearchEnvSettings) -> None:
        self.settings = settings
        self._providers: Dict[str, BaseProvider] = {}
        self._build_registry()

    def _build_registry(self) -> None:
        self._providers["brave"] = BraveProvider(self.settings)
        self._providers["serper"] = PlaceholderProvider(
            self.settings,
            friendly_name="Serper",
            env_keys=("serper_api_key",),
        )
        self._providers["tavily"] = PlaceholderProvider(
            self.settings,
            friendly_name="Tavily",
            env_keys=("tavily_api_key",),
        )
        self._providers["firecrawl"] = PlaceholderProvider(
            self.settings,
            friendly_name="Firecrawl",
            env_keys=("firecrawl_api_key",),
        )
        self._providers["browserless"] = PlaceholderProvider(
            self.settings,
            friendly_name="Browserless",
            env_keys=("browserless_api_key",),
        )
        self._providers["zenrows"] = PlaceholderProvider(
            self.settings,
            friendly_name="ZenRows",
            env_keys=("zenrows_api_key",),
        )
        self._providers["apify"] = PlaceholderProvider(
            self.settings,
            friendly_name="Apify",
            env_keys=("apify_api_token",),
        )
        self._providers["perplexity"] = PlaceholderProvider(
            self.settings,
            friendly_name="Perplexity",
            env_keys=("perplexity_api_key",),
        )
        self._providers["exa"] = PlaceholderProvider(
            self.settings,
            friendly_name="Exa AI",
            env_keys=("exa_api_key",),
        )

    def available(self) -> List[str]:
        return [name for name, provider in self._providers.items() if provider.is_configured()]

    def get(self, name: str) -> BaseProvider:
        key = name.lower()
        if key not in self._providers:
            raise ProviderExecutionError(
                f"Unknown provider '{name}'. Available options: {', '.join(sorted(self._providers.keys()))}."
            )
        provider = self._providers[key]
        if not provider.is_configured() and isinstance(provider, BraveProvider):
            raise ProviderNotConfigured("Configure BRAVE_API_KEY or choose a different provider.")
        return provider

    @property
    def default_provider(self) -> str:
        if self.settings.research_default_provider:
            return self.settings.research_default_provider
        if BraveProvider(self.settings).is_configured():
            return "brave"
        available = self.available()
        return available[0] if available else "brave"


def summarise_items(items: List[Dict[str, Any]], limit: int) -> str:
    if not items:
        return "(no results)"
    snippets = []
    for item in items[:limit]:
        title = item.get("title") or item.get("name") or "(untitled)"
        url = item.get("url") or item.get("link") or "(no url)"
        snippets.append(f"{title} → {url}")
    return " | ".join(snippets)


def redact_response(response: ProviderResponse) -> ProviderResponse:
    return ProviderResponse(
        provider=response.provider,
        query=response.query,
        items=[redact_payload(item) for item in response.items],
        raw=redact_payload(response.raw) if response.raw else {},
    )
