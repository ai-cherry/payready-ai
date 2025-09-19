#!/usr/bin/env python3
"""
PayReady AI CLI - Python wrapper for unified CLI
Provides a clean entry point for pyproject.toml
"""

import os
import sys
import subprocess
from pathlib import Path


def main():
    """Main entry point for PayReady AI CLI."""
    # Find the bin/ai script relative to this file
    script_dir = Path(__file__).parent
    ai_script = script_dir / "bin" / "ai"

    if not ai_script.exists():
        print(f"Error: AI script not found at {ai_script}", file=sys.stderr)
        sys.exit(1)

    # Only chmod if not already executable
    if not os.access(ai_script, os.X_OK):
        ai_script.chmod(0o755)

    # Pass through all arguments to the bash script
    try:
        result = subprocess.run(
            [str(ai_script)] + sys.argv[1:],
            check=False,  # Don't raise on non-zero exit
            text=True
        )
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(130)  # Standard exit code for Ctrl+C
    except Exception as e:
        print(f"Error running AI CLI: {e}", file=sys.stderr)
        sys.exit(1)


def memory():
    """Entry point for memory commands."""
    script_dir = Path(__file__).parent
    memory_script = script_dir / "core" / "memory.py"

    if not memory_script.exists():
        print(f"Error: Memory script not found at {memory_script}", file=sys.stderr)
        sys.exit(1)

    try:
        result = subprocess.run(
            [sys.executable, str(memory_script)] + sys.argv[1:],
            check=False,
            text=True
        )
        sys.exit(result.returncode)
    except Exception as e:
        print(f"Error running memory system: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()