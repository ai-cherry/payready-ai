"""Configuration loader for the unified CLI - wraps config_v2 for compatibility."""

from __future__ import annotations

import logging
import logging.config
import os
from pathlib import Path
from typing import Any, Dict, Optional

import tomllib
from pydantic import BaseModel, Field, ValidationError
from pydantic_settings import BaseSettings

from .secrets import get as get_secret


def _load_test_mode_env() -> None:
    """Load local environment defaults when PAYREADY_TEST_MODE=1."""
    if os.getenv("PAYREADY_TEST_MODE") != "1":
        return

    env_path = Path(__file__).resolve().parent.parent / "config" / "env.local"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key and not os.getenv(key):
            os.environ[key] = value.strip()

    os.environ.setdefault("PAYREADY_ENV", "local")
    os.environ.setdefault("PAYREADY_OFFLINE_MODE", "1")
    for key in (
        "OPENROUTER_API_KEY",
        "AIMLAPI_API_KEY",
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
    ):
        os.environ.setdefault(key, "stub")


_load_test_mode_env()

# Try to use the new config_v2, fall back to original implementation
try:
    from .config_v2 import Settings as SettingsV2, get_settings
    _USE_V2 = True
except ImportError:
    _USE_V2 = False


class ClaudeAgentConfig(BaseModel):
    model: str
    temperature: float = 0.2
    max_tokens: int = 1000
    max_context_chars: int = 6000
    system_prompt: str = (
        "You are Claude assisting PayReady engineers via the unified CLI. "
        "Follow policies, be concise, and respect provided context."
    )
    http_timeout: float = 45.0


class CodexAgentConfig(BaseModel):
    binary: str = "codex"
    model: str
    flags: list[str] = Field(default_factory=list)
    timeout_sec: float = 300.0
    max_context_chars: int = 4000


class AgnoAgentConfig(BaseModel):
    planner_model: str
    coder_model: str
    reviewer_model: str
    max_context_chars: int = 6000


class AgentsConfig(BaseModel):
    claude: ClaudeAgentConfig
    codex: CodexAgentConfig
    agno: AgnoAgentConfig


class EnvSettings(BaseSettings):
    openrouter_api_key: Optional[str] = Field(default=None, alias="OPENROUTER_API_KEY")
    aimlapi_api_key: Optional[str] = Field(default=None, alias="AIMLAPI_API_KEY")
    aimlapi_base_url: str = Field(default="https://api.aimlapi.com/v1", alias="AIMLAPI_BASE_URL")

    class Config:
        extra = "allow"
        case_sensitive = True


class ResearchEnvSettings(BaseSettings):
    brave_api_key: Optional[str] = Field(default=None, alias="BRAVE_API_KEY")
    serper_api_key: Optional[str] = Field(default=None, alias="SERPER_API_KEY")
    tavily_api_key: Optional[str] = Field(default=None, alias="TAVILY_API_KEY")
    firecrawl_api_key: Optional[str] = Field(default=None, alias="FIRECRAWL_API_KEY")
    browserless_api_key: Optional[str] = Field(default=None, alias="BROWSERLESS_API_KEY")
    zenrows_api_key: Optional[str] = Field(default=None, alias="ZENROWS_API_KEY")
    apify_api_token: Optional[str] = Field(default=None, alias="APIFY_API_TOKEN")
    perplexity_api_key: Optional[str] = Field(default=None, alias="PERPLEXITY_API_KEY")
    exa_api_key: Optional[str] = Field(default=None, alias="EXA_API_KEY")
    research_default_provider: Optional[str] = Field(default=None, alias="RESEARCH_DEFAULT_PROVIDER")
    research_max_results: Optional[int] = Field(default=None, alias="RESEARCH_MAX_RESULTS")

    class Config:
        extra = "allow"
        case_sensitive = True


class Settings(BaseModel):
    openrouter_api_key: Optional[str]
    aimlapi_api_key: Optional[str]
    aimlapi_base_url: str
    agents: AgentsConfig
    logging_config: Path = Path("config/logging.toml")
    research: ResearchEnvSettings


def _load_env_file(path: Path, *, required: bool = True) -> Dict[str, str]:
    if not path.exists():
        if required:
            raise FileNotFoundError(f"Missing configuration file: {path}")
        return {}
    data: Dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"Invalid line in {path}: {raw_line}")
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def _merge_with_env(data: Dict[str, str], model: type[BaseSettings]) -> Dict[str, str]:
    merged = {}
    for field in model.model_fields.values():
        alias = field.alias or field.serialization_alias or field.name
        if alias in os.environ and os.environ[alias]:
            merged[alias] = os.environ[alias]
    merged.update(data)
    return merged


def _load_agents_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing configuration file: {path}")
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    return data


def load_settings(
    ports_path: Optional[Path] = None,
    agents_path: Optional[Path] = None,
    research_path: Optional[Path] = None,
) -> Settings:
    # Try to use new config_v2 if available
    if _USE_V2:
        try:
            v2_settings = get_settings()
            # Convert V2 settings to V1 format for compatibility

            # Load agents config for compatibility
            agents_file = agents_path or Path("config") / "agents.toml"
            if agents_file.exists():
                agents_data = _load_agents_file(agents_file)
                agents_config = AgentsConfig(**agents_data)
            else:
                # Create default agents config
                agents_config = AgentsConfig(
                    claude=ClaudeAgentConfig(model="claude-3-sonnet-20240229"),
                    codex=CodexAgentConfig(model="gpt-4"),
                    agno=AgnoAgentConfig(
                        planner_model=v2_settings.agents.agno.planner_model,
                        coder_model=v2_settings.agents.agno.coder_model,
                        reviewer_model=v2_settings.agents.agno.reviewer_model,
                    ),
                )

            # Create research settings
            research_settings = ResearchEnvSettings(
                brave_api_key=v2_settings.brave_api_key,
                serper_api_key=v2_settings.serper_api_key,
                tavily_api_key=v2_settings.tavily_api_key,
                firecrawl_api_key=v2_settings.firecrawl_api_key,
                browserless_api_key=v2_settings.browserless_api_key,
                zenrows_api_key=v2_settings.zenrows_api_key,
                apify_api_token=v2_settings.apify_api_token,
                perplexity_api_key=v2_settings.perplexity_api_key,
                exa_api_key=v2_settings.exa_api_key,
                research_default_provider=v2_settings.research_default_provider,
                research_max_results=v2_settings.research_max_results,
            )

            return Settings(
                openrouter_api_key=v2_settings.openrouter_api_key,
                aimlapi_api_key=v2_settings.aimlapi_api_key,
                aimlapi_base_url=v2_settings.aimlapi_base_url,
                agents=agents_config,
                research=research_settings,
            )
        except Exception as e:
            # Fall back to original implementation if V2 fails
            print(f"Warning: Failed to use config_v2, falling back: {e}")

    # Original implementation
    ports_file = ports_path or Path("config") / "ports.env"
    agents_file = agents_path or Path("config") / "agents.toml"

    env_data = _load_env_file(ports_file)
    try:
        env_settings = EnvSettings(**_merge_with_env(env_data, EnvSettings))
    except ValidationError as exc:
        raise RuntimeError(f"Invalid ports.env configuration: {exc}") from exc

    agents_data = _load_agents_file(agents_file)
    try:
        agents_config = AgentsConfig(**agents_data)
    except ValidationError as exc:
        raise RuntimeError(f"Invalid agents.toml configuration: {exc}") from exc

    research_file = research_path or Path("config") / "research.env"
    research_data = _load_env_file(research_file, required=False)
    try:
        research_settings = ResearchEnvSettings(**_merge_with_env(research_data, ResearchEnvSettings))
    except ValidationError as exc:
        raise RuntimeError(f"Invalid research.env configuration: {exc}") from exc

    openrouter_key = env_settings.openrouter_api_key or get_secret(
        "OPENROUTER_API_KEY", env="OPENROUTER_API_KEY", required=False
    )

    aimlapi_key = env_settings.aimlapi_api_key or get_secret(
        "AIMLAPI_API_KEY", env="AIMLAPI_API_KEY", required=False
    )

    aimlapi_base_url = env_settings.aimlapi_base_url

    return Settings(
        openrouter_api_key=openrouter_key,
        aimlapi_api_key=aimlapi_key,
        aimlapi_base_url=aimlapi_base_url,
        agents=agents_config,
        research=research_settings,
    )


def configure_logging(memory_dir: Path, config_path: Optional[Path] = None) -> None:
    path = config_path or Path("config") / "logging.toml"
    if not path.exists():
        logging.basicConfig(level=logging.INFO)
        return

    with path.open("rb") as handle:
        config_data = tomllib.load(handle)

    def _inject_memory_dir(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {key: _inject_memory_dir(value) for key, value in obj.items()}
        if isinstance(obj, list):
            return [_inject_memory_dir(item) for item in obj]
        if isinstance(obj, str):
            return obj.replace("${memory_dir}", str(memory_dir))
        return obj

    logging_config = _inject_memory_dir(config_data)
    logging.config.dictConfig(logging_config)  # type: ignore[arg-type]


__all__ = ["Settings", "configure_logging", "load_settings"]
