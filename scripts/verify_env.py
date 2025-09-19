#!/usr/bin/env python3
"""Verify environment setup for PayReady AI CLI."""

import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_python():
    """Check Python version."""
    print("Python Version Check:")
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print(f"  ✅ Python {version.major}.{version.minor}.{version.micro}")
    else:
        print(f"  ❌ Python {version.major}.{version.minor} (need 3.11+)")
    print()

def check_imports():
    """Check critical imports."""
    print("Import Check:")
    imports = [
        ("agno", "Agno framework"),
        ("pydantic", "Pydantic"),
        ("httpx", "HTTPX"),
        ("redis", "Redis"),
        ("keyring", "Keyring"),
        ("openai", "OpenAI"),
        ("anthropic", "Anthropic"),
    ]

    for module, name in imports:
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError as e:
            print(f"  ❌ {name}: {e}")
    print()

def check_api_keys():
    """Check API key configuration."""
    print("API Keys Check:")

    # Try to load settings
    try:
        from cli.config_v2 import get_settings
        settings = get_settings()

        keys = {
            "OpenRouter": settings.openrouter_api_key,
            "Portkey": settings.portkey_api_key,
            "Anthropic": settings.anthropic_api_key,
            "OpenAI": settings.openai_api_key,
        }

        has_valid = False
        for name, key in keys.items():
            if key:
                print(f"  ✅ {name}: {key[:10]}...")
                has_valid = True
            else:
                print(f"  ⚠️  {name}: Not configured")

        if not has_valid:
            print("  ❌ No valid API keys found!")

    except Exception as e:
        print(f"  ❌ Failed to load settings: {e}")
    print()

def check_directories():
    """Check required directories."""
    print("Directory Check:")
    dirs = [
        Path.home() / ".config/payready",
        Path(".project/memory"),
        Path("config"),
    ]

    for dir_path in dirs:
        if dir_path.exists():
            print(f"  ✅ {dir_path}")
        else:
            print(f"  ⚠️  {dir_path} (missing)")
    print()

def check_cli():
    """Check CLI executable."""
    print("CLI Check:")
    cli_path = Path("bin/ai")
    if cli_path.exists() and cli_path.stat().st_mode & 0o111:
        print(f"  ✅ {cli_path} (executable)")
    else:
        print(f"  ❌ {cli_path} (not executable or missing)")
    print()

def main():
    """Run all checks."""
    print("=" * 60)
    print("PayReady AI Environment Verification")
    print("=" * 60)
    print()

    check_python()
    check_imports()
    check_api_keys()
    check_directories()
    check_cli()

    print("=" * 60)
    print("Verification complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()