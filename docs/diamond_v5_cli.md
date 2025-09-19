# Diamond v5 (Tekton) Quickstart

The staged Plan → Release workflow lives in the Tekton toolkit. Trigger it via
the `payready tekton` subcommand (defined in `payready/cli.py`). The Typer-based
`payready-cli` adapters for Claude/Codex/Agno share the same `.project/memory`
store, so artifacts and journals remain consistent regardless of which entrypoint
you use.

## Prerequisites
- Python 3.10+
- `codex` CLI installed and logged in (for GPT-5 Codex)
- Portkey account with virtual keys for each provider
- Optional: Redis, Postgres (Neon), Weaviate or Milvus for memory/RAG

## Environment
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env.local  # fill in keys
```

## Commands
```bash
# Full run
payready tekton --goal "Improve webhook reliability"

# Run via the Typer front door
# Inspect stage wiring without running
payready tekton --goal "..." --explain

# Start from research, stop after threat stage
payready tekton --goal "..." --from research --to threat

# Consensus-free code & test stages (use runtime signals over debate)
payready tekton --goal "..." --consensus-free code test_debug

# Force a specific model for all stages (except Codex)
payready tekton --goal "..." --model anthropic/claude-opus-4.1
```

Artifacts land in `artifacts/` (plan.json, research.json, backlog.json, diff.patch,
review.json, threat.json, integration.json, test_report.json, release_report.json)
and the same metadata is mirrored under `.project/memory/runs/<timestamp>/` for
replay via `payready-cli` tooling.

## Model Routing
- `openai/gpt-5-codex` → Codex CLI (ChatGPT login)
- All other models → Portkey virtual keys
- You can override the default via `--model` or by setting `LLM_MODEL`

Set `LLM_MODEL` in `.env.local` to change the default route.
