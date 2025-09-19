#!/usr/bin/env python3
"""Placeholder for future vector ingestion of CLI memory artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest memory artifacts into vector store (stub)")
    parser.add_argument(
        "--memory",
        type=Path,
        default=Path(".project") / "memory",
        help="Memory directory to ingest.",
    )
    args = parser.parse_args()
    print(
        "TODO: Implement ingestion of", args.memory,
        "into Milvus/Weaviate. This script currently acts as a placeholder.",
    )


if __name__ == "__main__":
    main()
