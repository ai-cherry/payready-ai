"""Top-level PayReady command dispatch for SOPHIA and Tekton tooling."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _run_tekton(argv: Iterable[str]) -> int:
    from tekton import cli as tekton_cli

    args = list(argv)
    tekton_cli.main(args if args else None)
    return 0


def _run_prompt(argv: Iterable[str]) -> int:
    script = _project_root() / "bin" / "ai"
    if not script.exists():
        raise FileNotFoundError(f"Tekton prompt wrapper missing: {script}")

    result = subprocess.run([str(script)] + list(argv), check=False)
    return result.returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser("payready", description="Unified PayReady command")
    parser.add_argument(
        "command",
        nargs="?",
        help="Supported subcommands: tekton, prompt",
    )
    parser.add_argument("args", nargs=argparse.REMAINDER)
    return parser


def main(argv: List[str] | None = None) -> None:
    parser = build_parser()
    parsed = parser.parse_args(argv)
    command = parsed.command

    if not command:
        parser.print_help()
        parser.exit()

    remainder = parsed.args

    if command == "tekton":
        exit_code = _run_tekton(remainder)
    elif command == "prompt":
        exit_code = _run_prompt(remainder)
    else:
        parser.print_help()
        parser.exit(status=2, message=f"Unknown command: {command}\n")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
