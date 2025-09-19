#!/usr/bin/env bash
# shellcheck disable=SC2142
# Source this script inside a shell to capture executed commands.

PAYREADY_PROJECT_ROOT="${PAYREADY_PROJECT_ROOT:-$(git rev-parse --show-toplevel)}"
PAYREADY_MEMORY_DIR="${PAYREADY_MEMORY_DIR:-${PAYREADY_PROJECT_ROOT}/.project/memory}"
mkdir -p "${PAYREADY_MEMORY_DIR}"
touch "${PAYREADY_MEMORY_DIR}/session-log.md" "${PAYREADY_MEMORY_DIR}/events.jsonl"

_payready_log_command() {
  local command_text="$1"
  local exit_code="$2"
  python3 - "$PAYREADY_MEMORY_DIR" "$command_text" "$exit_code" "$PAYREADY_PROJECT_ROOT" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

memory_dir = Path(sys.argv[1])
raw_command = sys.argv[2]
exit_code = int(sys.argv[3])
project_root = Path(sys.argv[4])

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from cli.agents.metadata import collect_repo_state, redact_text, redact_payload  # type: ignore

command_text = redact_text(raw_command)

timestamp = datetime.now(timezone.utc)

session_path = memory_dir / "session-log.md"
events_path = memory_dir / "events.jsonl"

entry = f"- {timestamp.isoformat()} shell › {command_text} (exit={exit_code})\n"
entry = redact_text(entry)
with session_path.open("a", encoding="utf-8") as handle:
    handle.write(entry)

event = {
    "timestamp": timestamp.isoformat(),
    "agent": "shell",
    "command": command_text,
    "output_preview": "",
    "metadata": {
        "exit_code": exit_code,
        **collect_repo_state(project_root),
    },
}
with events_path.open("a", encoding="utf-8") as handle:
    json.dump(redact_payload(event), handle, ensure_ascii=False)
    handle.write("\n")
PY
}

if [[ -n "${ZSH_VERSION:-}" ]]; then
  function preexec() {
    _PAYREADY_LAST_COMMAND="$1"
  }
  function precmd() {
    local exit_status=$?
    if [[ -n "${_PAYREADY_LAST_COMMAND:-}" ]]; then
      _payready_log_command "${_PAYREADY_LAST_COMMAND}" "$exit_status"
      unset _PAYREADY_LAST_COMMAND
    fi
  }
else
  payready_original_prompt_command="${PROMPT_COMMAND:-}"
  payready_bash_logger() {
    local status=$?
    local cmd=$(history 1 | sed -E 's/^ *[0-9]+ +//')
    if [[ -n "$cmd" ]]; then
      _payready_log_command "$cmd" "$status"
    fi
    return $status
  }
  if [[ -n "$payready_original_prompt_command" ]]; then
    PROMPT_COMMAND="payready_bash_logger; $payready_original_prompt_command"
  else
    PROMPT_COMMAND="payready_bash_logger"
  fi
fi
