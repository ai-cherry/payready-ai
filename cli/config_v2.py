"""Improved Pydantic Settings with proper optional fields for Agno v2.0.7."""

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import Optional, Dict, Any
import os

try:
    import keyring  # type: ignore
except Exception:  # Keyring not available in some local environments
    keyring = None


def _load_test_mode_env() -> None:
    """Load local environment defaults when PAYREADY_TEST_MODE=1."""
    if os.getenv("PAYREADY_TEST_MODE") != "1":
        return

    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "env.local")
    if not os.path.exists(env_path):
        return

    with open(env_path, encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key and not os.getenv(key.strip()):
                os.environ[key.strip()] = value.strip()

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


def get_from_keyring(service: str, name: str) -> Optional[str]:
    """Get secret from keyring if available."""
    if keyring is None:
        return None
    try:
        return keyring.get_password(service, name)
    except Exception:
        return None


class AIMLAPIConfig(BaseSettings):
    """AIMLAPI configuration with optional fields."""
    api_key: Optional[str] = Field(default=None)
    base_url: str = Field(default="https://api.aimlapi.com/v1")

    @field_validator("api_key", mode="before")
    def load_api_key(cls, v):
        if not v:
            # Try keyring
            v = get_from_keyring("payready", "AIMLAPI_API_KEY")
        return v


class AgnoAgentConfig(BaseSettings):
    """Agno agent configuration."""
    max_context_chars: int = Field(default=2000)
    planner_model: str = Field(default="openai/gpt-4o-mini")
    coder_model: str = Field(default="openai/gpt-4o-mini")
    reviewer_model: str = Field(default="openai/gpt-4o-mini")
    mediator_model: str = Field(default="anthropic/claude-3.5-sonnet")


class AgentConfigs(BaseSettings):
    """All agent configurations."""
    agno: AgnoAgentConfig = Field(default_factory=AgnoAgentConfig)
    claude: Dict[str, Any] = Field(default_factory=lambda: {
        "model": "anthropic/claude-3.5-sonnet",
        "temperature": 0.7
    })
    codex: Dict[str, Any] = Field(default_factory=lambda: {
        "model": "openai/gpt-4o",
        "temperature": 0.5
    })


class ResearchConfig(BaseSettings):
    """Research configuration."""
    max_results: int = Field(default=10)
    timeout_seconds: int = Field(default=30)
    cache_ttl: int = Field(default=3600)


class Settings(BaseSettings):
    """Main settings with all fields optional and proper defaults."""

    # API Keys - all optional
    openrouter_api_key: Optional[str] = Field(default=None, env="OPENROUTER_API_KEY")
    aimlapi_api_key: Optional[str] = Field(default=None, env="AIMLAPI_API_KEY")
    aimlapi_base_url: str = Field(default="https://api.aimlapi.com/v1", env="AIMLAPI_BASE_URL")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    deepseek_api_key: Optional[str] = Field(default=None, env="DEEPSEEK_API_KEY")
    groq_api_key: Optional[str] = Field(default=None, env="GROQ_API_KEY")

    # Research API Keys - all optional
    brave_api_key: Optional[str] = Field(default=None, env="BRAVE_API_KEY")
    serper_api_key: Optional[str] = Field(default=None, env="SERPER_API_KEY")
    tavily_api_key: Optional[str] = Field(default=None, env="TAVILY_API_KEY")
    firecrawl_api_key: Optional[str] = Field(default=None, env="FIRECRAWL_API_KEY")
    browserless_api_key: Optional[str] = Field(default=None, env="BROWSERLESS_API_KEY")
    zenrows_api_key: Optional[str] = Field(default=None, env="ZENROWS_API_KEY")
    apify_api_token: Optional[str] = Field(default=None, env="APIFY_API_TOKEN")
    perplexity_api_key: Optional[str] = Field(default=None, env="PERPLEXITY_API_KEY")
    exa_api_key: Optional[str] = Field(default=None, env="EXA_API_KEY")
    research_default_provider: Optional[str] = Field(default=None, env="RESEARCH_DEFAULT_PROVIDER")
    research_max_results: Optional[int] = Field(default=10, env="RESEARCH_MAX_RESULTS")

    # Service URLs - optional with defaults
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    pg_dsn: Optional[str] = Field(default=None, env="PG_DSN")
    milvus_uri: Optional[str] = Field(default="milvus_local", env="MILVUS_URI")
    mem0_api_key: Optional[str] = Field(default=None, env="MEM0_API_KEY")

    # Feature flags
    use_memory: bool = Field(default=True, env="USE_MEMORY")
    use_cache: bool = Field(default=True, env="USE_CACHE")
    debug_mode: bool = Field(default=False, env="AI_DEBUG")

    # Complex configs with factory defaults
    aimlapi: AIMLAPIConfig = Field(default_factory=AIMLAPIConfig)
    agents: AgentConfigs = Field(default_factory=AgentConfigs)
    research: ResearchConfig = Field(default_factory=ResearchConfig)

    # Project settings
    project_root: str = Field(default_factory=lambda: os.getcwd())
    memory_dir: str = Field(default=".project/memory")

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False
        extra = "ignore"  # Don't fail on extra fields
        validate_assignment = True
        use_enum_values = True

    @field_validator("openrouter_api_key", mode="before")
    def load_openrouter_key(cls, v):
        """Try multiple sources for OpenRouter key."""
        if not v:
            # Try keyring
            v = get_from_keyring("payready", "OPENROUTER_API_KEY")
        if not v:
            # Try environment
            v = os.getenv("OPENROUTER_API_KEY")
        return v

    @field_validator("aimlapi_api_key", mode="before")
    def load_aimlapi_key(cls, v):
        """Try multiple sources for AIMLAPI key."""
        if not v:
            v = get_from_keyring("payready", "AIMLAPI_API_KEY")
        if not v:
            v = os.getenv("AIMLAPI_API_KEY")
        return v

    @field_validator("openrouter_api_key", "aimlapi_api_key", "anthropic_api_key", "openai_api_key", "deepseek_api_key", "groq_api_key", mode="after")
    def validate_api_key_format(cls, v):
        """Warn if API key format looks suspicious."""
        if v and not any(str(v).startswith(prefix) for prefix in [
            'sk-', 'sk-ant-', 'sk-or-', 'gsk_']):
            import warnings
            warnings.warn(f"API key may have invalid format: {str(v)[:8]}...", stacklevel=2)
        return v

    def get_active_api_key(self) -> Optional[str]:
        """Get first valid API key with validation."""
        # In offline mode, always return stub
        if os.getenv("PAYREADY_OFFLINE_MODE") == "1":
            return "stub"
            
        keys = [
            (self.openrouter_api_key, "OpenRouter"),
            (self.aimlapi_api_key, "AIMLAPI"),
            (self.anthropic_api_key, "Anthropic"),
            (self.openai_api_key, "OpenAI"),
            (self.deepseek_api_key, "DeepSeek"),
            (self.groq_api_key, "Groq"),
        ]
        for key, provider in keys:
            if key and key != "test-key" and len(key) > 3:  # More lenient for stubs
                return key
        
        # In offline mode, don't raise error
        if os.getenv("PAYREADY_OFFLINE_MODE") == "1":
            return "stub"
            
        raise ValueError(
            "No valid API key configured. Please set one of:\n"
            "  - OPENROUTER_API_KEY (recommended)\n"
            "  - OPENAI_API_KEY\n"
            "  - ANTHROPIC_API_KEY\n"
            "  Or use: keyring set payready OPENROUTER_API_KEY <your-key>"
        )

    def validate_for_production(self) -> bool:
        """Check if settings are valid for production use."""
        return bool(self.get_active_api_key())


# Singleton instance
_settings_instance = None


def get_settings() -> Settings:
    """Get or create settings singleton."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance


# Export for compatibility
__all__ = [
    "Settings",
    "get_settings",
    "PortkeyConfig",
    "AgnoAgentConfig",
    "AgentConfigs",
    "ResearchConfig",
]
