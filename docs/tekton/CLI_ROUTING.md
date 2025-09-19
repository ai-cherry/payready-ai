# PayReady CLI (Typer) – Unified Routing

The `cli` package provides the `payready-cli` Typer command—the primary terminal
front door for Tekton. Subcommands fan out to Claude, Codex, and Agno agents
while sharing the same context and artifact layout as the Diamond workflow.

## Commands

```bash
payready-cli claude "Summarize latest Tekton decisions"
payready-cli codex "Generate tests for tekton.swarm" --model openai/gpt-5-codex
payready-cli agno "Implement blended RAG pipeline" --dry-run
payready-cli research "Latest Portkey governance guidance" --provider brave --count 5
```

Global options:

- `--memory/-m PATH` — Override the memory directory (defaults to `.project/memory`).
- `--context/-c FILE` — Inject additional Markdown/JSON alongside the prompt.

## Flow (all subcommands)

1. CLI callback ensures `.project/memory` exists, loads configuration, and initialises
   logging.
2. `load_context` gathers `session-log.md`, `events.jsonl`, recent run metadata, and
   any `--context` file.
3. Agent adapter writes a new run directory under `.project/memory/runs/<timestamp>/`
   with `prompt.md`, `response.md`, and `metadata.json`.
4. Session journal and JSONL events are appended; rotating log emits diagnostic logs.
5. Command output is streamed to the terminal while the structured artifacts remain
   available for later ingestion or ingestion into RAG.

The legacy `payready` command still exposes `payready tekton` (Diamond) and
`payready prompt` (legacy shell CLI). `payready-cli` is the new preferred entrypoint
for per-task swarms and shares all memory artefacts with the staged workflow.

## Memory Artefacts

- `.project/memory/session-log.md` — markdown narrative of each invocation (PII redacted automatically).
- `.project/memory/events.jsonl` — machine-readable events for agents.
- `.project/memory/runs/<timestamp>/` — per-run payloads for rehydration or audits.
- `.project/memory/logs/cli.log` — log events via `logging.toml` rotating handler.

## Extending

- Add new agent adapters under `cli/agents/` and register them in `cli/cli.py`.
- Expose additional config knobs through `config/agents.toml` and `cli/config.py`.
- Pipe events into RAG by building on `scripts/ingest_memory.py`.
