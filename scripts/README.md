# Scripts Overview

| Script | Description |
|--------|-------------|
| `dev.sh` | Bootstraps/reattaches the tmux session, sources `config/ports.env`, and prepares `.project/memory`. |
| `init_session.sh` | Reconfigures the active tmux session with `prompt`, `events`, and `logs` windows. |
| `command_logger.sh` | Source inside a shell to append executed commands to session memory. |
| `ingest_memory.py` | Placeholder for pushing memory artefacts into a vector store. |
| `smoke_cli.sh` | Runs a dry-run Agno smoke test against a temporary memory directory. |
| `rotate_memory.sh` | Prunes run directories older than `RETENTION_DAYS` (default 14). |

Run `chmod +x scripts/*.sh` if your checkout does not preserve execute bits.
