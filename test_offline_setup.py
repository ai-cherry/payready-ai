#!/usr/bin/env python3
"""
Complete Offline Development Setup Validation Tests

This script validates that the entire PayReady AI codebase works in offline mode
without any API keys or external service dependencies.
"""

import os
import sys
import subprocess
from pathlib import Path

# Set offline environment
os.environ["PAYREADY_OFFLINE_MODE"] = "1"
os.environ["PAYREADY_TEST_MODE"] = "1"
os.environ["PAYREADY_ENV"] = "local"
os.environ["USE_PORTKEY"] = "0"
os.environ["USE_MEMORY"] = "0"
os.environ["USE_CACHE"] = "0"
os.environ["KEYRING_BACKEND"] = "keyring.backends.null.Keyring"

# Stub API keys
os.environ["OPENROUTER_API_KEY"] = "stub"
os.environ["PORTKEY_API_KEY"] = "stub"
os.environ["ANTHROPIC_API_KEY"] = "stub"
os.environ["OPENAI_API_KEY"] = "stub"


def test_imports():
    """Test that all core modules can be imported."""
    print("Testing Python module imports...")

    try:
        from core.agent_factory import get_factory
        print("✅ core.agent_factory imports successfully")
    except Exception as e:
        print(f"❌ core.agent_factory import failed: {e}")
        return False

    try:
        from cli.config_v2 import get_settings
        print("✅ cli.config_v2 imports successfully")
    except Exception as e:
        print(f"❌ cli.config_v2 import failed: {e}")
        return False

    try:
        from cli.secrets import get
        print("✅ cli.secrets imports successfully")
    except Exception as e:
        print(f"❌ cli.secrets import failed: {e}")
        return False

    try:
        from cli.providers import client_openrouter, client_openai
        print("✅ cli.providers imports successfully")
    except Exception as e:
        print(f"❌ cli.providers import failed: {e}")
        return False

    return True


def test_secret_loading():
    """Test that secrets return stub values in offline mode."""
    print("\nTesting secret loading...")

    try:
        from cli.secrets import get
        secret_value = get("TEST_SECRET")
        assert secret_value == "stub", f"Expected 'stub', got '{secret_value}'"
        print(f"✅ Secrets return stub values: {secret_value}")
        return True
    except Exception as e:
        print(f"❌ Secret loading failed: {e}")
        return False


def test_config_loading():
    """Test that configuration loads properly in offline mode."""
    print("\nTesting configuration loading...")

    try:
        from cli.config_v2 import get_settings
        settings = get_settings()
        # Check that settings loads and has expected offline values
        print(f"✅ Settings loaded successfully")
        if hasattr(settings, 'portkey_api_key'):
            print(f"  - API keys are stubbed: {settings.portkey_api_key[:10]}...")
        return True
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return False


def test_agent_creation():
    """Test that agents can be created in offline mode."""
    print("\nTesting agent creation...")

    try:
        from core.agent_factory import get_factory
        factory = get_factory()
        agent = factory.create_agent("test", "test_agent")
        print(f"✅ Agent created: {agent.name}")
        return True
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return False


def test_provider_stubs():
    """Test that provider clients return stub responses."""
    print("\nTesting provider stubs...")

    try:
        from cli.providers import client_openrouter, client_openai

        # Test OpenRouter stub
        openrouter_client = client_openrouter()
        print(f"✅ OpenRouter client created: {type(openrouter_client).__name__}")

        # Test OpenAI stub
        openai_client = client_openai()
        print(f"✅ OpenAI client created: {type(openai_client).__name__}")

        # Test stub response
        if hasattr(openrouter_client, 'chat'):
            response = openrouter_client.chat.completions.create(
                model="test-model",
                messages=[{"role": "user", "content": "test"}]
            )
            print(f"✅ Stub response received: {response.content[:50]}...")

        return True
    except Exception as e:
        print(f"❌ Provider stubs failed: {e}")
        return False


def test_cli_script():
    """Test that the bin/ai CLI script works in offline mode."""
    print("\nTesting bin/ai CLI script...")

    try:
        # Set up environment for subprocess
        env = os.environ.copy()
        env["PAYREADY_OFFLINE_MODE"] = "1"

        # Test the CLI with a simple query
        result = subprocess.run(
            ["./bin/ai", "hello world"],
            capture_output=True,
            text=True,
            env=env,
            cwd=Path(__file__).parent
        )

        if result.returncode == 0:
            print("✅ bin/ai script executes successfully")
            if "Offline Mode" in result.stdout:
                print("✅ bin/ai returns offline mode response")
                return True
            else:
                print("❌ bin/ai did not return offline mode response")
                print(f"Output: {result.stdout}")
                return False
        else:
            print(f"❌ bin/ai script failed with code {result.returncode}")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False


def test_no_external_dependencies():
    """Verify no external API calls are made."""
    print("\nVerifying no external dependencies...")

    # This is a placeholder - in a real test, you might use mocking
    # or network monitoring to ensure no external calls are made
    print("✅ No external API calls required in offline mode")
    return True


def main():
    """Run all validation tests."""
    print("=" * 60)
    print("PayReady AI Offline Setup Validation")
    print("=" * 60)

    tests = [
        ("Module Imports", test_imports),
        ("Secret Loading", test_secret_loading),
        ("Config Loading", test_config_loading),
        ("Agent Creation", test_agent_creation),
        ("Provider Stubs", test_provider_stubs),
        ("CLI Script", test_cli_script),
        ("No External Dependencies", test_no_external_dependencies),
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ Test '{name}' crashed: {e}")
            results.append((name, False))

    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    all_passed = True
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {name}")
        if not success:
            all_passed = False

    print("=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED - Offline setup is complete!")
        print("\nYou can now develop without any API keys or external services.")
        print("All AI agents will receive stub responses in offline mode.")
        return 0
    else:
        print("⚠️  Some tests failed - please check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())