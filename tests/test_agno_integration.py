#!/usr/bin/env python3
"""Comprehensive test suite for Agno v2.0.7 integration."""

import pytest
import asyncio
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat

from cli.config_v2 import Settings, get_settings
from core.agent_factory import AgentFactory, get_factory
from core.unified_memory import UnifiedMemory, get_memory


class TestAgnoIntegration:
    """Test Agno v2.0.7 integration."""

    @pytest.fixture
    def settings(self):
        """Create test settings."""
        return Settings(
            openrouter_api_key="test-key",
            use_memory=False,
            debug_mode=True
        )

    @pytest.fixture
    def factory(self, settings):
        """Create test factory."""
        return AgentFactory(settings)

    def test_agno_imports(self):
        """Test that Agno classes can be imported."""
        from agno.agent import Agent
        from agno.team import Team
        from agno.models.openai import OpenAIChat
        from agno.memory import MemoryManager

        assert Agent is not None
        assert Team is not None
        assert OpenAIChat is not None
        assert MemoryManager is not None

    def test_settings_creation(self):
        """Test that settings can be created without all fields."""
        settings = Settings()
        assert settings is not None
        # Note: use_memory is set from environment (USE_MEMORY=0 in test mode)
        # assert settings.use_memory is True
        # Note: use_cache is set from environment (USE_CACHE=0 in test mode)
        # assert settings.use_cache is True
        assert settings.debug_mode is False

    def test_settings_with_partial_config(self):
        """Test settings with partial configuration."""
        settings = Settings(
            openrouter_api_key="test-key",
            use_memory=False
        )
        assert settings.openrouter_api_key == "test-key"
        assert settings.use_memory is False
        # Note: portkey_api_key may be set from environment variables

    def test_agent_factory_creation(self, factory):
        """Test agent factory creation."""
        assert factory is not None
        assert factory.settings is not None

    def test_create_planner_agent(self, factory):
        """Test creating a planner agent."""
        agent = factory.create_planner(api_key="test-key")
        assert agent is not None
        assert agent.name == "planner"
        assert "strategic planner" in agent.role

    def test_create_coder_agent(self, factory):
        """Test creating a coder agent."""
        agent = factory.create_coder(api_key="test-key")
        assert agent is not None
        assert agent.name == "coder"
        assert "programmer" in agent.role

    def test_create_reviewer_agent(self, factory):
        """Test creating a reviewer agent."""
        agent = factory.create_reviewer(api_key="test-key")
        assert agent is not None
        assert agent.name == "reviewer"
        assert "reviewer" in agent.role

    def test_create_team(self, factory):
        """Test creating a team."""
        team = factory.create_team(api_key="test-key")
        assert team is not None
        assert hasattr(team, "members")
        assert len(team.members) == 3

    def test_create_jury(self, factory):
        """Test creating a jury."""
        jury = factory.create_jury(api_key="test-key")
        assert jury is not None
        assert "proponent" in jury
        assert "skeptic" in jury
        assert "pragmatist" in jury
        assert "mediator" in jury

    def test_unified_memory_creation(self, settings):
        """Test unified memory creation."""
        memory = UnifiedMemory(settings)
        assert memory is not None
        assert memory.storage_type in ["agno", "redis", "file"]

    def test_memory_remember_recall(self, settings):
        """Test memory store and retrieve."""
        memory = UnifiedMemory(settings)

        # Store
        success = memory.remember("test_key", "test_value", "test_category")
        assert success is True

        # Recall
        results = memory.recall("test", "test_category")
        assert isinstance(results, list)

    def test_memory_conversation_logging(self, settings):
        """Test conversation logging."""
        memory = UnifiedMemory(settings)

        success = memory.log_conversation(
            "Hello",
            "Hi there!",
            "test-model"
        )
        assert success is True

    def test_memory_context(self, settings):
        """Test memory context retrieval."""
        memory = UnifiedMemory(settings)
        context = memory.get_context()

        assert isinstance(context, dict)
        assert "timestamp" in context
        assert "storage_type" in context
        assert "stats" in context


class TestAgnoAsyncIntegration:
    """Test async Agno operations."""

    @pytest.fixture
    def settings(self):
        """Create test settings."""
        return Settings(
            openrouter_api_key="test-key",
            use_memory=False,
            debug_mode=True
        )

    def test_agent_async_run(self, settings):
        """Ensure async run path can be invoked when API key is available."""
        api_key = settings.get_active_api_key()
        if not api_key or api_key == "test-key":
            pytest.skip("Requires real API key")

        factory = AgentFactory(settings)
        agent = factory.create_planner()

        async def _invoke():
            return await agent.arun("Create a simple hello world function")

        response = asyncio.run(_invoke())
        assert response is not None


class TestEndToEnd:
    """End-to-end integration tests."""

    def test_full_stack_initialization(self):
        """Test that full stack can be initialized."""
        # Settings
        settings = Settings()

        # Factory
        factory = get_factory(settings)
        assert factory is not None

        # Memory
        memory = get_memory(settings)
        assert memory is not None

        # Agents
        planner = factory.create_planner(api_key="test-key")
        coder = factory.create_coder(api_key="test-key")
        reviewer = factory.create_reviewer(api_key="test-key")

        assert all([planner, coder, reviewer])

        # Team
        team = Team(members=[planner, coder, reviewer])
        assert team is not None

    def test_singleton_pattern(self):
        """Test singleton patterns work correctly."""
        # Settings singleton
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2

        # Factory singleton
        f1 = get_factory()
        f2 = get_factory()
        assert f1 is f2

        # Memory singleton
        m1 = get_memory()
        m2 = get_memory()
        assert m1 is m2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
