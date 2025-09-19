#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(git rev-parse --show-toplevel)"
SESSION_NAME="${1:-$(tmux display-message -p '#S')}"
MEMORY_DIR="${PROJECT_ROOT}/.project/memory"

tmux set-environment -t "${SESSION_NAME}" PAYREADY_PROJECT_ROOT "${PROJECT_ROOT}" 2>/dev/null || true

mkdir -p "${MEMORY_DIR}/logs"
touch "${MEMORY_DIR}/events.jsonl" "${MEMORY_DIR}/logs/cli.log"

tmux rename-window -t "${SESSION_NAME}":0 prompt
if ! tmux list-windows -t "${SESSION_NAME}" | grep -q '^1: events'; then
  tmux new-window -t "${SESSION_NAME}":1 -n events -c "${PROJECT_ROOT}" \
    "tail -F .project/memory/events.jsonl"
fi
if ! tmux list-windows -t "${SESSION_NAME}" | grep -q '^2: logs'; then
  tmux new-window -t "${SESSION_NAME}":2 -n logs -c "${PROJECT_ROOT}" \
    "tail -F .project/memory/logs/cli.log"
fi

tmux select-window -t "${SESSION_NAME}":0
