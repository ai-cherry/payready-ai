"""Tekton command-line entry for Diamond v5 swarm orchestration."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path
from typing import List

from .swarm import describe, run

DEFAULT_OUTPUT = Path("artifacts")


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser("tekton")
    parser.add_argument("swarm", nargs="?", help="Legacy alias; ignored")
    parser.add_argument("--goal", required=True, help="High-level goal/problem statement")
    parser.add_argument(
        "--from", dest="start", default="plan", help="First stage to execute (default: plan)"
    )
    parser.add_argument(
        "--to", dest="end", default="release", help="Last stage to execute (default: release)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Directory for persisted artifacts",
    )
    parser.add_argument(
        "--consensus-free",
        nargs="*",
        default=[],
        help="Stages to run in consensus-free mode (e.g. code test_debug)",
    )
    parser.add_argument(
        "--resume",
        help="Resume a previous run by ID",
    )
    parser.add_argument(
        "--model",
        help="Force a specific model override for all stages",
    )
    parser.add_argument(
        "--explain",
        action="store_true",
        help="Print stage instructions without executing",
    )
    return parser.parse_args(argv)


async def execute(args: argparse.Namespace) -> None:
    if args.explain:
        print(json.dumps(describe(), indent=2))
        return

    args.output.mkdir(parents=True, exist_ok=True)
    result = await run(
        goal=args.goal,
        start=args.start,
        end=args.end,
        consensus_free=args.consensus_free,
        resume=args.resume,
        model_override=args.model,
        output_dir=args.output,
    )

    summary_file = args.output / "diamond_summary.json"
    summary_file.write_text(json.dumps(result, indent=2))
    print(f"✓ Diamond workflow complete. Summary saved to {summary_file}")


def main(argv: List[str] | None = None) -> None:
    args = parse_args(argv)
    if args.model:
        os.environ["LLM_MODEL"] = args.model
    asyncio.run(execute(args))


if __name__ == "__main__":
    main()
