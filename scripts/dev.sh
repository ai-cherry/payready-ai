#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SESSION_NAME="${SESSION_NAME:-payready}"
export PAYREADY_TMUX_STATE="${PROJECT_ROOT}/.project/memory/tmux"
export PAYREADY_PROJECT_ROOT="${PROJECT_ROOT}"
MEMORY_DIR="${PROJECT_ROOT}/.project/memory"

mkdir -p "${MEMORY_DIR}/logs" "${MEMORY_DIR}/runs" "${PAYREADY_TMUX_STATE}"
touch "${MEMORY_DIR}/session-log.md" "${MEMORY_DIR}/events.jsonl" "${MEMORY_DIR}/logs/cli.log"

if [[ -f "${PROJECT_ROOT}/config/ports.env" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "${PROJECT_ROOT}/config/ports.env"
  set +a
fi

if ! tmux has-session -t "${SESSION_NAME}" 2>/dev/null; then
  tmux new-session -d -s "${SESSION_NAME}" -c "${PROJECT_ROOT}" -n prompt "${SHELL:-/bin/bash}"
  tmux new-window -t "${SESSION_NAME}":1 -n events -c "${PROJECT_ROOT}" \
    "tail -F .project/memory/events.jsonl"
  tmux new-window -t "${SESSION_NAME}":2 -n logs -c "${PROJECT_ROOT}" \
    "tail -F .project/memory/logs/cli.log"
  tmux select-window -t "${SESSION_NAME}":0
  tmux send-keys -t "${SESSION_NAME}":0 "source scripts/command_logger.sh" C-m
fi

tmux attach -t "${SESSION_NAME}"
