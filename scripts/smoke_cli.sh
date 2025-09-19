#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}" )/.." && pwd)"
MEM_DIR="$(mktemp -d)"

echo "Using temporary memory dir: ${MEM_DIR}" >&2
python3 -m cli.cli agno "Smoke test" --memory "${MEM_DIR}" --dry-run
ls "${MEM_DIR}/runs" >&2
