#!/usr/bin/env python3
"""Simple repository indexer stub for Diamond v5."""

from __future__ import annotations

import argparse
from pathlib import Path


def index_repo(root: Path) -> None:
    # TODO: implement embedding pipeline
    print(f"Indexing repository under {root}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".", help="Repository root")
    args = parser.parse_args()
    index_repo(Path(args.root).resolve())


if __name__ == "__main__":
    main()
