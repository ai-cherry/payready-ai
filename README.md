# PayReady AI 🚀

Unified AI development environment integrating Claude CLI, Codex (GPT-5), and Agno agents for intelligent code generation, analysis, and automation.

## Features ✨

- **Unified Natural Language Interface**: Single entry point for all AI tools
- **Intelligent Routing**: Automatically routes queries to the most appropriate AI
- **Web Search Integration**: Real-time web search with strict 2025-only filtering
- **Context-Aware Development**: Maintains project state across all tools
- **Living Documentation**: Auto-updating documentation system
- **Multi-Model Support**: Claude, GPT-5, GPT-5-mini, and specialized models

## Quick Start 🎯

### Prerequisites
- Python 3.8+
- direnv
- Git
- API Keys for OpenAI and other services

### Installation

```bash
# Clone the repository
git clone https://github.com/ai-cherry/payready-ai.git
cd payready-ai

# Install dependencies
pip install -r requirements.txt

# Configure environment
direnv allow

# Add your API keys to ~/.config/payready/env.llm
echo 'export OPENAI_API_KEY="your-key-here"' >> ~/.config/payready/env.llm
```

### Basic Usage

```bash
# Natural language interface
./bin/ai "write a Python function to process payments"

# Direct tool access
./bin/codex "implement binary search"
./bin/ai-router "refactor authentication module"

# Documentation management
./bin/ai docs list
./bin/ai docs update

# Code audit
./bin/ai-audit
```

## Architecture 🏗️

```
┌─────────────────────────────────────────────┐
│           Unified AI CLI (`ai`)            │
│  Natural Language Interface & Router        │
└──────────────┬──────────────────────────────┘
               │
    ┌──────────┴──────────┬────────────┬─────────────┐
    │                     │            │             │
┌───▼────┐      ┌────────▼───┐  ┌─────▼────┐  ┌────▼────┐
│ Claude │      │   Codex    │  │   Web    │  │  Agno   │
│  CLI   │      │  (GPT-5)   │  │  Search  │  │  Agent  │
└────────┘      └────────────┘  └──────────┘  └─────────┘
```

## Configuration 🔧

### Environment Files
Store configuration in `~/.config/payready/`:
- `env.llm` - OpenAI and Anthropic API keys
- `env.web` - Web search API keys (Perplexity, Brave, Exa)
- `env.github` - GitHub authentication
- `env.agno` - Agno agent configuration

### Date Context
All tools include automatic date context with a 100-day cutoff for current information filtering.

## Commands Reference 📚

| Command | Description |
|---------|-------------|
| `ai <query>` | Natural language interface |
| `ai docs list` | List all documentation |
| `ai docs search <term>` | Search documentation |
| `ai-audit` | Run comprehensive code audit |
| `codex <prompt>` | Direct GPT-5 access |
| `ai-router <query>` | Enhanced routing with confidence scoring |
| `git-setup` | Configure GitHub integration |

## Documentation 📖

See the `docs/` directory for comprehensive documentation:
- [Architecture](docs/ARCHITECTURE/UNIFIED_AI_INTEGRATION_ARCHITECTURE.md)
- [API Reference](docs/REFERENCES/CLI_REFERENCE.md)
- [Setup Guide](docs/GUIDES/SETUP_GUIDE.md)

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
# Enable debug mode
DEBUG=true ./bin/codex "your query"
DEBUG=true ./bin/ai-router "your query"
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