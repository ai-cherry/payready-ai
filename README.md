# PayReady AI · SOPHIA & Tekton 🚀

PayReady AI now ships two complementary experiences:

- **SOPHIA** – the business intelligence dashboard and orchestration layer for
  executives and analysts.
- **Tekton** – the engineering builder’s toolchain powering the Diamond v5 swarm
  workflow (Plan → Release) with Portkey routing, Codex GPT-5 access, Redis, RAG,
  and the Threat & Compliance gate.

## Key Concepts

- **PayReady app** – this entire repository; SOPHIA and Tekton are sibling surfaces
  that share infrastructure (Redis, Neon, vector stores, auth, logging).
- **Tekton toolkit** – everything engineers touch: the Diamond workflow, the
  unified CLI adapters, shared schemas, memory logs, and supporting scripts under
  `cli/`, `tekton/`, `.project/`, and `scripts/`.
- **PayReady CLI (`payready` command)** – thin dispatcher defined in
  `payready/cli.py`. It exposes historical subcommands:
  - `payready tekton …` → runs the asynchronous Diamond v5 workflow.
  - `payready prompt …` → forwards to the legacy shell wrapper in `bin/ai`.
- **PayReady CLI (Typer, `payready-cli`)** – the new terminal “front door” for
  per-task swarms. Subcommands route to Claude, Codex, or Agno while sharing the
  structured memory store.
- **Diamond workflow** – staged Plan→Release swarm living in `tekton/`. It’s
  currently launched via `payready tekton …` and produces schema-validated
  artifacts per stage.
- **Agent memory** – durable journals, JSONL events, and per-run folders stored
  under `.project/memory/`; all CLI surfaces append here with redaction applied.

## Features ✨

- **Single `payready` Command**: Unified entrypoint with subcommands for Tekton workflows
  and the legacy prompt runner.
- **Tekton Diamond Swarm**: Stage-specific AI agents (Plan → Release) with
  confidence-weighted mediation and artifact persistence.
- **Intelligent Routing**: Portkey/OpenRouter model selection with manual overrides per run.
- **Context-Aware Development**: Shared Redis/Postgres/Milvus layers maintain run history and RAG context.
- **Living Documentation**: Auto-updating artifacts and docs keep SOPHIA and Tekton in sync.
- **Multi-Model Support**: Claude, GPT-5, GPT-5-mini, DeepSeek, Grok, and more.

## Quick Start 🎯

### Prerequisites
- Python 3.11+
- direnv
- Git
- API Keys for OpenAI and other services

### Installation

```bash
# (Use `python -m payready.cli` in place of `payready` if the console script is not installed.)
# Clone the repository
git clone https://github.com/ai-cherry/payready-ai.git
cd payready-ai

# Install dependencies
pip install -e .

# Configure environment
direnv allow

# Add your API keys to ~/.config/payready/env.llm
mkdir -p ~/.config/payready
echo 'export OPENROUTER_API_KEY="your-key-here"' >> ~/.config/payready/env.llm
```

### Basic Usage

```bash
# Launch Tekton Diamond workflow
payready tekton --goal "Improve webhook retries"

# Inspect stage wiring without execution
payready tekton --goal "..." --explain

# Run code/test consensus-free (prefer runtime signals)
payready tekton --goal "..." --consensus-free code test_debug

# Legacy natural language prompt runner
payready prompt "write a Python function to process payments"

# Unified CLI agents (Typer-based)
payready-cli claude "Summarize yesterday's deployment"
payready-cli codex "Generate regression tests" --model openai/gpt-5-codex
payready-cli agno "Draft RAG migration plan" --dry-run
```

## Architecture 🏗️

```
┌──────────────────────────────────────────────┐
│       Diamond Triad Swarm (Plan → Release)   │
│  Proponent / Skeptic / Pragmatist + Mediator │
└──────────────┬───────────────────────────────┘
               │
    ┌──────────┴──────────┬────────────┬───────────────┐
    │                     │            │               │
┌───▼────┐      ┌────────▼───┐  ┌─────▼────┐  ┌──────▼─────┐
│ Portkey │      │  Codex     │  │ Context  │  │ Redis / RAG │
│ Routing │      │ GPT-5 CLI  │  │ Manager  │  │   Memory    │
└────────┘      └────────────┘  └──────────┘  └─────────────┘
```

## Configuration 🔧

### Environment Files
Store configuration in `~/.config/payready/`:
- `env.core` – Core application settings (version, env, logging)
- `env.llm` – Portkey API key, virtual keys, OpenRouter fallback, Codex settings
- `env.services` – Redis/Mem0, vector store, Neon Postgres, BI integrations (e.g. Slack, Salesforce, NetSuite)

### Date Context
All tools include automatic date context with a 100-day cutoff for current information filtering.

## Commands Reference 📚

| Command | Purpose |
|---------|---------|
| `payready tekton --goal "..."` | Run the staged Diamond v5 workflow (Plan → Release) |
| `payready tekton --explain` | Describe Diamond stage ordering & prompts |
| `payready prompt <query>` | Legacy shell CLI (Portkey/OpenRouter routing) |
| `payready prompt config list` | Inspect legacy CLI configuration |
| `payready-cli claude "..."` | Route a single prompt to Claude with shared memory/context |
| `payready-cli codex "..."` | Invoke the Codex CLI with shared memory/context |
| `payready-cli agno "..." --dry-run` | Launch the Agno planner/coder/reviewer swarm |
| `python scripts/index_repo.py` | Rebuild local knowledge base (future RAG pipeline) |

## Documentation 📖

See the `docs/` directory for comprehensive documentation:
- [SOPHIA Architecture](docs/ARCHITECTURE/UNIFIED_AI_INTEGRATION_ARCHITECTURE.md)
- [Tekton Architecture](docs/tekton/ARCHITECTURE.md)
- [Unified CLI Routing](docs/tekton/CLI_ROUTING.md)
- [API Reference](docs/REFERENCES/CLI_REFERENCE.md)
- [Setup Guide](docs/GUIDES/SETUP_GUIDE.md)
- [Terminal Setup Guide](docs/SETUP_TERMINAL.md)

## Development 🛠️

### Running Tests
```bash
pytest tests/
```

### Code Quality
```bash
# Format code
black services/ bin/*.py

# Lint
pylint services/
```

### Debugging
```bash
# Enable verbose routing logs
AI_DEBUG=true payready prompt "design a service"

# Inspect Diamond summary
cat artifacts/diamond_summary.json
```

## Troubleshooting 🔍

### Common Issues

1. **Empty Codex responses**
   - Run with `DEBUG=true` to see full API response
   - Check API key configuration

2. **direnv errors**
   - Run `direnv allow` to approve environment loading

3. **Date calculation errors**
   - Install GNU coreutils: `brew install coreutils`

4. **SSH/GitHub issues**
   - Run `./bin/git-setup test` to verify configuration

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and audit: `./bin/ai-audit`
5. Submit a pull request

## License 📄

[MIT License](LICENSE)

## Support 💬

- Issues: [GitHub Issues](https://github.com/ai-cherry/payready-ai/issues)
- Documentation: Run `ai docs list`

## Roadmap 🗺️

- [ ] Multi-model consensus for complex decisions
- [ ] Automatic code review on git push
- [ ] Slack integration for team notifications
- [ ] Performance metrics dashboard
- [ ] Kubernetes deployment support

---

Built with ❤️ by the PayReady AI Team | Last Updated: September 18, 2025
