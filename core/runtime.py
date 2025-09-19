"""Shared runtime helpers for Diamond v5 swarms."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Optional
import sys

from agno import Agent
from agno.memory import RedisMemory
from agno.store import PgRunStore
from agno.knowledge import WeaviateKnowledgeBase, MilvusKnowledgeBase
from agno.tools import ShellTool, GitTool, PythonTool

DEFAULT_MODEL = os.getenv("LLM_MODEL", "anthropic/claude-opus-4.1")


@lru_cache(maxsize=1)
def _redis_memory() -> Optional[RedisMemory]:
    url = os.getenv("AGNO__REDIS_URL")
    if not url:
        return None
    return RedisMemory(url=url)


@lru_cache(maxsize=1)
def _run_store() -> Optional[PgRunStore]:
    dsn = os.getenv("AGNO__PG_DSN")
    if not dsn:
        return None
    return PgRunStore(dsn=dsn)


@lru_cache(maxsize=1)
def _knowledge_base():
    if url := os.getenv("AGNO__WEAVIATE_URL"):
        return WeaviateKnowledgeBase(url=url, index="diamond_docs")
    return MilvusKnowledgeBase(
        uri=os.getenv("MILVUS_URI", "milvus_local"), index="diamond_docs"
    )


SHELL = ShellTool(safe=True, timeout=180)
GIT = GitTool()


def python_tool() -> PythonTool:
    """Return a PythonTool bound to the interpreter running this process."""

    python_path = Path(sys.executable).resolve()
    return PythonTool(python=str(python_path))


def base_agent(
    name: str,
    role: str,
    *,
    tools: Iterable = (),
    model: Optional[str] = None,
    memory: Optional[RedisMemory] = None,
):
    """Create a pre-configured Agno agent for swarm stages."""

    return Agent(
        name=name,
        role=role,
        memory=memory or _redis_memory(),
        knowledge=_knowledge_base(),
        tools=list(tools),
        llm={
            "api_key_env": "PORTKEY_API_KEY",
            "base_url_env": "OPENAI_BASE_URL",
            "model": model or DEFAULT_MODEL,
        },
        telemetry={"runs": _run_store()},
        markdown=True,
        show_tool_calls=True,
    )


__all__ = [
    "base_agent",
    "SHELL",
    "GIT",
    "python_tool",
]
