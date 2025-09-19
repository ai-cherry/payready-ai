# Logging replaced print() calls — see ARCHITECTURE_AUDIT_REPORT.md
"""Runtime helpers using real Agno v2.0.7 classes."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Optional, Any, Dict
import sys
import logging

# Real Agno imports
from agno.agent import Agent
from agno.memory import MemoryManager
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude
from agno.models.groq import Groq
from agno.tools.python import PythonTools
from agno.tools import Toolkit
from agno.tools.shell import ShellTools

logger = logging.getLogger(__name__)

# Default model configuration
DEFAULT_MODEL = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")


@lru_cache(maxsize=1)
def get_memory_manager() -> Optional[MemoryManager]:
    """Get shared memory manager instance."""
    try:
        return MemoryManager()
    except Exception as e:
        # Optional memory backend may fail during startup; log for diagnostics
        logger.warning("MemoryManager initialization failed: %s", e)
        return None


def create_python_tools() -> PythonTools:
    """Create Python execution tools."""
    return PythonTools(base_dir=Path.cwd())


def create_shell_tools() -> ShellTools:
    """Create shell execution tools with CWD isolation."""
    return ShellTools(base_dir=Path.cwd())


def select_model(model_name: str = None, api_key: str = None):
    """Select appropriate model based on name."""
    model_name = model_name or DEFAULT_MODEL

    if "claude" in model_name.lower():
        return Claude(
            id=model_name,
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        )
    elif "groq" in model_name.lower() or "llama" in model_name.lower():
        return Groq(
            id=model_name,
            api_key=api_key or os.getenv("GROQ_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        )
    else:
        # Default to OpenAI-compatible
        return OpenAIChat(
            id=model_name,
            api_key=api_key or os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY"),
            base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        )


def base_agent(
    name: str,
    role: str,
    *,
    tools: Iterable = (),
    model: Optional[str] = None,
    memory: Optional[MemoryManager] = None,
    api_key: Optional[str] = None,
    instructions: Optional[list] = None,
) -> Agent:
    """Create a pre-configured Agno agent."""

    # Select appropriate model
    model_instance = select_model(model, api_key)

    # Build tools toolkit (always pass a sequence to Agent)
    toolkits: list[Toolkit] = []
    if tools:
        if isinstance(tools, Toolkit):
            toolkits.append(tools)
        else:
            toolkit = Toolkit(name=f"{name}_tools")
            for tool in tools:
                if hasattr(tool, "__call__"):
                    toolkit.register(tool)
            toolkits.append(toolkit)

    # Create agent with Agno v2.0.7 API
    agent = Agent(
        name=name,
        role=role,
        model=model_instance,
        tools=toolkits or None,
        memory_manager=memory or get_memory_manager(),
        instructions=instructions or [
            f"You are {name}, a {role}",
            "Provide clear, actionable responses",
            "Use tools when appropriate"
        ],
        markdown=True,
        show_tool_calls=True,
        debug_mode=os.getenv("AI_DEBUG", "false").lower() == "true"
    )

    return agent


def create_planner_agent(api_key: Optional[str] = None) -> Agent:
    """Create a planner agent."""
    return base_agent(
        name="planner",
        role="strategic planner who decomposes tasks",
        model="openai/gpt-4o",
        api_key=api_key,
        instructions=[
            "Break down complex tasks into clear steps",
            "Consider dependencies and order of operations",
            "Identify potential risks and mitigation strategies",
            "Output a structured plan with numbered steps"
        ]
    )


def create_coder_agent(api_key: Optional[str] = None) -> Agent:
    """Create a coder agent."""
    return base_agent(
        name="coder",
        role="expert programmer who implements solutions",
        model="anthropic/claude-3.5-sonnet",
        api_key=api_key,
        tools=[create_python_tools()],
        instructions=[
            "Write clean, well-documented code",
            "Follow best practices and design patterns",
            "Include error handling and validation",
            "Add comprehensive tests for your code"
        ]
    )


def create_reviewer_agent(api_key: Optional[str] = None) -> Agent:
    """Create a reviewer agent."""
    return base_agent(
        name="reviewer",
        role="code reviewer who ensures quality",
        model="openai/gpt-4o",
        api_key=api_key,
        instructions=[
            "Review code for correctness and efficiency",
            "Check for security vulnerabilities",
            "Ensure code follows project standards",
            "Provide specific, actionable feedback"
        ]
    )


def create_mediator_agent(api_key: Optional[str] = None) -> Agent:
    """Create a mediator agent for consensus."""
    return base_agent(
        name="mediator",
        role="impartial judge who synthesizes perspectives",
        model="anthropic/claude-opus",
        api_key=api_key,
        instructions=[
            "Consider all perspectives fairly",
            "Identify areas of agreement and disagreement",
            "Synthesize a balanced consensus position",
            "Provide clear rationale for decisions"
        ]
    )


# Exported tool instances for compatibility with Tekton stages
SHELL = create_shell_tools()
GIT = create_shell_tools()


def python_tool():
    """Return a PythonTools instance for compatibility."""
    return create_python_tools()


# Compatibility exports
__all__ = [
    "Agent",
    "base_agent",
    "create_planner_agent",
    "create_coder_agent",
    "create_reviewer_agent",
    "create_mediator_agent",
    "select_model",
    "get_memory_manager",
    "create_python_tools",
    "create_shell_tools",
    "SHELL",
    "GIT",
    "python_tool",
]
