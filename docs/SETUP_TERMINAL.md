# Terminal Setup Guide

This workflow assumes macOS on Apple Silicon with `tmux`, `direnv`, and Python 3.11+
installed.

## Prerequisites

- Install tmux plugins:
  ```bash
  git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm
  ```
- Install Python dependencies:
  ```bash
  pip install -e .[dev]
  ```
- Populate `config/ports.env` with Portkey/OpenRouter credentials.

## Bootstrapping tmux

```bash
./scripts/dev.sh
```

The script:

1. Exports secrets from `config/ports.env`.
2. Ensures `.project/memory` directories exist.
3. Launches a `tmux` session with windows for `prompt`, `events`, and `logs`.
4. Sources `scripts/command_logger.sh` so shell commands are captured.

Within tmux:

- `prefix + Ctrl-s` to force a snapshot (tmux-resurrect).
- `prefix + Ctrl-r` to restore the last snapshot.
- `prefix + 1/2/3` to navigate windows.

## Command Logging

Source the command logger to capture shell history:

```bash
source scripts/command_logger.sh
```

Every executed command appends to `.project/memory/session-log.md` and
`.project/memory/events.jsonl` with ISO 8601 timestamps and exit codes.

## Running Agents (Typer front door)

```bash
payready-cli claude "Summarize yesterday's deployment"
payready-cli codex "Refactor tekton runtime" --model openai/gpt-5-codex
payready-cli agno "Draft RAG migration plan" --dry-run
payready-cli diamond "Improve webhook reliability"
```

Use `payready tekton …` when you want the full staged Diamond workflow. The legacy
`payready prompt …` command still exists for the historic Bash CLI, but new work
should flow through `payready-cli` or `payready tekton`.

Change the memory directory per-project:

```bash
payready-cli claude "status" --memory /tmp/payready-memory
```

## Maintenance

- Purge old runs: delete folders inside `.project/memory/runs/`.
- Reset journal: truncate `session-log.md` while tmux session is offline.
- Vector ingestion: extend `scripts/ingest_memory.py` to push artefacts into Milvus or
  Weaviate when ready.
