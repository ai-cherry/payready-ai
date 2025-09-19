# Tekton Architecture

Tekton is PayReady’s builder-facing toolchain. It owns the Diamond v5 swarm,
repository-aware automation, and the forthcoming UI for engineering visibility.
SOPHIA remains the business intelligence dashboard; Tekton operates independently
and exposes its own API and interface.

## Components

- **Diamond runner (`payready tekton`)** – launches staged swarm runs, dry-runs
  stage ordering, and maps command-line options to runtime configuration (stage
  bounds, consensus-free, model overrides, output directories).
- **Typer front door (`payready-cli`)** – routes single prompts to Claude, Codex,
  or the Agno swarm while writing memory artifacts alongside the Diamond runner.
- **Runtime (`tekton/swarm.py`)** – orchestrates Plan→Release stages, streams
structured events, persists artifacts, and shares context between stages.
- **Agents (`tekton/stages/*.py`)** – construct triads per stage, invoke the
mediator debate loop, and validate artifacts against `core/schemas/artifacts.py`.
- **Legacy Prompt Runner (`payready prompt`)** – wraps the Bash shell in `bin/ai`
  for direct natural-language requests; retained for backwards compatibility.
- **Storage** – Redis for shared memory, Neon/Postgres for run history, Milvus or
Weaviate for RAG indexing, filesystem artifacts in `artifacts/`.

## UI Direction

Tekton’s UI arrives in two layers:

1. **REST + Event Service (`services/tekton_api/`, planned)**
   - `/runs` create/inspect Tekton runs, `/runs/{id}/events` stream progress via
     Server-Sent Events or WebSockets.
   - `/config` read/write model profiles, consensus settings, and artifact targets.
   - `/system/checks` perform environment verification (Portkey/Codex credentials,
     Redis/Postgres reachability, repo status, sandbox guards).
   - Background worker (async task queue) executes swarm runs and emits
     `RunStarted`, `StageProgress`, `StageBlocked`, `ArtifactCreated`, `RunFinished`.

2. **Front-End Clients**
   - **Web Dashboard (React/Next.js or FastAPI + HTMX)** for launch forms, live
     stage timeline, artifact viewers, diff inspection, repo health widgets, and
     configuration panels (per-stage model selection, consensus preferences).
   - **Terminal TUI (Textual)** reusing the same API for headless environments,
     with progress columns, streaming transcripts, and artifact shortcuts.

## Separation from SOPHIA

- SOPHIA routes through `gateway/` and `orchestrator/`; it presents BI chat,
  connector calls, and executive dashboards.
- Tekton does **not** reuse SOPHIA’s API; it operates via the `payready` command
  and its own REST service. Shared infrastructure (Redis, Neon, Milvus) is namespaced.
- Documentation is split: SOPHIA docs live under `docs/sofia/`; Tekton docs live
  in `docs/tekton/`.

## Roadmap Highlights

- Finish evented runtime and persist artifacts + telemetry to Neon.
- Build the `services/tekton_api` FastAPI layer with SSE/WebSocket streaming.
- Deliver Tekton dashboard MVP with run launcher, live stage status, artifact
  browser, and repo visibility (git status, diff summaries, outstanding reviews).
- Add profile-based model selection (per stage, per swarm) backed by config
  storage and surfaced in both CLI and UI.
- Harden CLI parity: automatic memory persistence, consensus-free toggles in
  advanced settings, and human-readable error surfacing with `--debug` traces.
