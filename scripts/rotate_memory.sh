#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
MEMORY_DIR="${1:-${PROJECT_ROOT}/.project/memory}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"

find "${MEMORY_DIR}/runs" -mindepth 1 -maxdepth 1 -type d -mtime +"${RETENTION_DAYS}" -exec rm -rf {} +
