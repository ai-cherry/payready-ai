# CLI Reference
**Last Updated**: 2025-09-18
**Status**: Active

## Unified AI Interface

### Main Commands

#### `ai <query>`
Natural language interface to all AI tools.

**Examples:**
```bash
ai "write a Python function"
ai "search latest AI news"
ai "refactor auth module"
```

#### `ai-router <query> [--debug]`
Enhanced router with confidence scoring.

**Options:**
- `--debug`: Show routing decision details

#### `ai-docs <command>`
Documentation management system.

**Commands:**
- `list [category]`: List documentation
- `show <doc_name>`: Display document
- `search <query>`: Search documentation
- `update`: Update live docs
- `validate`: Check consistency
- `changelog`: Generate changelog

### Specialized Tools

#### `codex [model] <prompt>`
Direct access to GPT-5 models.

**Models:**
- `gpt-5-mini`: Fast, optimized for code
- `gpt-5`: Full capability
- `gpt-5-nano`: Lightweight

#### `codex-current <query>`
Web search with 2025-only filtering.

#### `codex-web-2025 <query> [api]`
Multi-API web search.

**APIs:**
- `perplexity`: Real-time search
- `brave`: Privacy-focused
- `exa`: Semantic search

---
*This reference is automatically generated from CLI help text.*
