# Logging replaced print() calls — see ARCHITECTURE_AUDIT_REPORT.md
"""Agent factory for creating properly configured Agno v2.0.7 agents."""

import os
from typing import Optional, List, Dict, Any
from pathlib import Path

from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
# Import our robust memory manager instead of agno's direct import
from core.memory_manager import (
    get_memory_manager,
    save_session_id,
    load_session_id,
    create_session_id,
    MemoryPatterns
)
from agno.tools import Toolkit
from agno.tools.python import PythonTools

import logging
logger = logging.getLogger(__name__)

# Optional imports
try:
    from agno.models.anthropic import Claude
except ImportError:
    Claude = None

try:
    from agno.models.groq import Groq
except ImportError:
    Groq = None

from cli.config_v2 import Settings, get_settings


class AgentFactory:
    """Factory for creating and managing Agno agents."""

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize factory with settings."""
        self.settings = settings or get_settings()
        self._agents_cache = {}
        self._memory_manager = None

    @staticmethod
    def _stub_mode() -> bool:
        """Return True when local test or offline mode should accept stub keys."""
        return (
            os.getenv("PAYREADY_OFFLINE_MODE") == "1"
            or os.getenv("PAYREADY_TEST_MODE") == "1"
        )

    def get_memory_manager(self) -> Any:
        """Get or create shared memory manager with Redis/file fallback."""
        if not self.settings.use_memory and os.getenv("PAYREADY_OFFLINE_MODE") != "1":
            return None

        if self._memory_manager is None:
            # Use our robust memory manager with fallback
            self._memory_manager = get_memory_manager(self.settings)

            # Initialize or restore session ID
            self._session_id = load_session_id()
            if not self._session_id:
                self._session_id = create_session_id("payready")
                save_session_id(self._session_id)
                logger.info("Created new session: %s", self._session_id)
            else:
                logger.info("Restored session: %s", self._session_id)

        return self._memory_manager

    def get_session_id(self) -> str:
        """Get the current session ID."""
        if not hasattr(self, '_session_id'):
            self.get_memory_manager()  # This will initialize session ID
        return self._session_id

    def _validate_api_key(self, key: Optional[str]) -> bool:
        """Validate API key format."""
        if self._stub_mode():
            return True

        if not key or len(key) < 4:  # More lenient
            return False

        # Accept test keys
        if key in ['test-key', 'stub']:
            return True

        valid_prefixes = [
            'sk-',      # OpenAI
            'sk-ant-',  # Anthropic
            'sk-or-',   # OpenRouter
            'pk-',      # Portkey
            'vk-',      # Virtual key
            'gsk_',     # Groq
            'stub',     # Stub keys
        ]
        return any(str(key).startswith(prefix) for prefix in valid_prefixes)

    def create_model(self, model_id: str, api_key: Optional[str] = None) -> Any:
        """Create appropriate model instance based on ID."""
        # Use provided key or fallback to settings
        if not api_key:
            api_key = self.settings.get_active_api_key()

        if not api_key:
            if self._stub_mode():
                api_key = "stub"
            else:
                raise ValueError("No API key available")

        # Determine provider and create model
        model_lower = model_id.lower()

        if Claude and ("claude" in model_lower or "anthropic" in model_lower):
            return Claude(
                id=model_id,
                api_key=api_key
            )
        elif Groq and ("groq" in model_lower or "llama" in model_lower):
            return Groq(
                id=model_id,
                api_key=api_key
            )
        else:
            # Default to OpenAI-compatible (works with OpenRouter)
            return OpenAIChat(
                id=model_id,
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1"
            )

    def create_python_tools(self) -> PythonTools:
        """Create Python execution tools."""
        return PythonTools(
            base_dir=Path(self.settings.project_root)
        )

    def create_agent(
        self,
        name: str,
        role: str,
        model_id: Optional[str] = None,
        tools: Optional[List] = None,
        instructions: Optional[List[str]] = None,
        use_memory: Optional[bool] = None,
        api_key: Optional[str] = None
    ) -> Agent:
        """Create a configured agent."""

        # Cache key
        cache_key = f"{name}_{role}_{model_id}"
        if cache_key in self._agents_cache:
            return self._agents_cache[cache_key]

        # Default model based on role
        if not model_id:
            model_map = {
                "planner": self.settings.agents.agno.planner_model,
                "coder": self.settings.agents.agno.coder_model,
                "reviewer": self.settings.agents.agno.reviewer_model,
                "mediator": self.settings.agents.agno.mediator_model,
            }
            model_id = model_map.get(role.split()[0], "openai/gpt-4o-mini")

        # API key validation
        if not api_key:
            api_key = self.settings.get_active_api_key()

        if self._stub_mode():
            api_key = api_key or "stub"
            logger.debug("Creating agent '%s' with stub credentials", name)
        else:
            # Accept "test-key" for testing purposes
            if api_key == "test-key":
                logger.debug("Using test-key for agent '%s'", name)
            elif not api_key:
                raise ValueError(
                    f"No valid API key for agent '{name}'. "
                    f"Configure one of: OPENROUTER_API_KEY, OPENAI_API_KEY, "
                    f"ANTHROPIC_API_KEY, or PORTKEY_API_KEY"
                )
            elif not self._validate_api_key(api_key):
                raise ValueError(f"Invalid API key format for agent '{name}': {api_key[:8]}...")
            logger.info("Creating agent '%s' with validated credentials", name)

        # Create model
        model = self.create_model(model_id, api_key)

        # Setup tools
        toolkit = None
        if tools:
            toolkit = Toolkit(name=f"{name}_tools")
            for tool in tools:
                if hasattr(tool, '__call__'):
                    toolkit.register(tool)

        # Setup memory
        memory = None
        if use_memory is None:
            use_memory = self.settings.use_memory
        if use_memory:
            memory = self.get_memory_manager()

        # Default instructions
        if not instructions:
            instructions = [
                f"You are {name}, a {role}",
                "Provide clear, structured, actionable responses",
                "Use markdown formatting for clarity",
                "Be concise but thorough"
            ]

        # Create agent with session ID for persistence
        agent_params = {
            "name": name,
            "role": role,
            "model": model,
            "tools": [toolkit] if toolkit else [],
            "instructions": instructions,
            "markdown": True,
            "debug_mode": self.settings.debug_mode
        }

        # Add memory if available
        if memory:
            agent_params["memory_manager"] = memory
            # Note: session_id is stored separately, not passed to Agent constructor
            logger.info("Agent '%s' using memory manager", name)

        agent = Agent(**agent_params)

        # Cache for reuse
        self._agents_cache[cache_key] = agent
        return agent

    def create_planner(self, api_key: Optional[str] = None) -> Agent:
        """Create a planner agent."""
        return self.create_agent(
            name="planner",
            role="strategic planner who decomposes complex tasks",
            model_id=self.settings.agents.agno.planner_model,
            instructions=[
                "Break down complex tasks into clear, numbered steps",
                "Consider dependencies and order of operations",
                "Identify potential risks and mitigation strategies",
                "Estimate time and resources needed for each step",
                "Output a structured plan with clear milestones"
            ],
            api_key=api_key
        )

    def create_coder(self, api_key: Optional[str] = None) -> Agent:
        """Create a coder agent."""
        return self.create_agent(
            name="coder",
            role="expert programmer who implements robust solutions",
            model_id=self.settings.agents.agno.coder_model,
            tools=[self.create_python_tools()],
            instructions=[
                "Write clean, well-documented, production-quality code",
                "Follow best practices and established design patterns",
                "Include comprehensive error handling and input validation",
                "Add unit tests and integration tests for your code",
                "Consider performance, security, and maintainability"
            ],
            api_key=api_key
        )

    def create_reviewer(self, api_key: Optional[str] = None) -> Agent:
        """Create a reviewer agent."""
        return self.create_agent(
            name="reviewer",
            role="senior code reviewer who ensures quality and standards",
            model_id=self.settings.agents.agno.reviewer_model,
            instructions=[
                "Review code for correctness, efficiency, and elegance",
                "Check for security vulnerabilities and potential bugs",
                "Ensure code follows project standards and conventions",
                "Verify test coverage and edge case handling",
                "Provide specific, actionable, constructive feedback"
            ],
            api_key=api_key
        )

    def create_mediator(self, api_key: Optional[str] = None) -> Agent:
        """Create a mediator agent for consensus."""
        return self.create_agent(
            name="mediator",
            role="impartial judge who synthesizes multiple perspectives",
            model_id=self.settings.agents.agno.mediator_model,
            instructions=[
                "Consider all perspectives fairly and objectively",
                "Identify areas of agreement and key points of disagreement",
                "Synthesize a balanced consensus position",
                "Provide clear rationale for all decisions",
                "Suggest compromises when views conflict"
            ],
            api_key=api_key
        )

    def create_team(
        self,
        agents: Optional[List[Agent]] = None,
        api_key: Optional[str] = None,
        share_memory: bool = True
    ) -> Team:
        """Create a team of agents with shared memory.

        Args:
            agents: List of agents (creates default team if None)
            api_key: API key for agents
            share_memory: Whether agents share memory context
        """
        if not agents:
            # Default team: planner, coder, reviewer
            agents = [
                self.create_planner(api_key),
                self.create_coder(api_key),
                self.create_reviewer(api_key)
            ]

        # Team only accepts members parameter
        team = Team(members=agents)

        # Log memory sharing status
        if share_memory and (self.settings.use_memory or os.getenv("PAYREADY_OFFLINE_MODE") == "1"):
            memory = self.get_memory_manager()
            if memory:
                logger.info("Team created with shared memory context")

        return team

    def create_jury(
        self,
        api_key: Optional[str] = None
    ) -> Dict[str, Agent]:
        """Create a jury of agents for consensus decisions."""
        return {
            "proponent": self.create_agent(
                "proponent",
                "advocate who champions the proposed solution",
                instructions=[
                    "Advocate strongly for the benefits of the proposal",
                    "Highlight positive outcomes and opportunities",
                    "Address concerns constructively"
                ],
                api_key=api_key
            ),
            "skeptic": self.create_agent(
                "skeptic",
                "critical thinker who identifies risks and issues",
                instructions=[
                    "Identify potential problems and risks",
                    "Question assumptions and challenge claims",
                    "Suggest alternative approaches"
                ],
                api_key=api_key
            ),
            "pragmatist": self.create_agent(
                "pragmatist",
                "practical realist who focuses on implementation",
                instructions=[
                    "Focus on practical implementation concerns",
                    "Consider resource constraints and timelines",
                    "Suggest realistic compromises"
                ],
                api_key=api_key
            ),
            "mediator": self.create_mediator(api_key)
        }


# Singleton factory instance
_factory_instance = None


def get_factory(settings: Optional[Settings] = None) -> AgentFactory:
    """Get or create factory singleton."""
    global _factory_instance
    if (_factory_instance is None):
        _factory_instance = AgentFactory(settings)
    return _factory_instance


# Convenience functions
def create_planner_agent(api_key: Optional[str] = None) -> Agent:
    """Create a planner agent."""
    return get_factory().create_planner(api_key)


def create_coder_agent(api_key: Optional[str] = None) -> Agent:
    """Create a coder agent."""
    return get_factory().create_coder(api_key)


def create_reviewer_agent(api_key: Optional[str] = None) -> Agent:
    """Create a reviewer agent."""
    return get_factory().create_reviewer(api_key)


def create_development_team(api_key: Optional[str] = None) -> Team:
    """Create a standard development team."""
    return get_factory().create_team(api_key=api_key)


__all__ = [
    "AgentFactory",
    "get_factory",
    "create_planner_agent",
    "create_coder_agent",
    "create_reviewer_agent",
    "create_development_team",
]
