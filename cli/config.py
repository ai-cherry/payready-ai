"""Configuration loader for the unified CLI."""

from __future__ import annotations

import logging
import logging.config
from pathlib import Path
from typing import Any, Dict, Optional

import tomllib
from pydantic import BaseModel, BaseSettings, Field, ValidationError


class PortkeyConfig(BaseModel):
    api_key: str
    virtual_key: str
    base_url: str = Field(default="https://api.portkey.ai/v1")


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
    portkey_api_key: str = Field(..., alias="PORTKEY_API_KEY")
    portkey_virtual_key: str = Field(..., alias="PORTKEY_VIRTUAL_KEY")
    portkey_base_url: str = Field(default="https://api.portkey.ai/v1", alias="PORTKEY_BASE_URL")
    openrouter_api_key: Optional[str] = Field(default=None, alias="OPENROUTER_API_KEY")

    class Config:
        extra = "allow"
        case_sensitive = True


class Settings(BaseModel):
    portkey: PortkeyConfig
    openrouter_api_key: Optional[str]
    agents: AgentsConfig
    logging_config: Path = Path("config/logging.toml")


def _load_env_file(path: Path) -> Dict[str, str]:
    if not path.exists():
        raise FileNotFoundError(f"Missing configuration file: {path}")
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


def _load_agents_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing configuration file: {path}")
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    return data


def load_settings(
    ports_path: Optional[Path] = None,
    agents_path: Optional[Path] = None,
) -> Settings:
    ports_file = ports_path or Path("config") / "ports.env"
    agents_file = agents_path or Path("config") / "agents.toml"

    env_data = _load_env_file(ports_file)
    try:
        env_settings = EnvSettings(**env_data)
    except ValidationError as exc:
        raise RuntimeError(f"Invalid ports.env configuration: {exc}") from exc

    agents_data = _load_agents_file(agents_file)
    try:
        agents_config = AgentsConfig(**agents_data)
    except ValidationError as exc:
        raise RuntimeError(f"Invalid agents.toml configuration: {exc}") from exc

    portkey_cfg = PortkeyConfig(
        api_key=env_settings.portkey_api_key,
        virtual_key=env_settings.portkey_virtual_key,
        base_url=env_settings.portkey_base_url,
    )

    return Settings(
        portkey=portkey_cfg,
        openrouter_api_key=env_settings.openrouter_api_key,
        agents=agents_config,
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
