# Unified AI Integration Architecture
**Version**: 2.0.0
**Last Updated**: 2025-09-18
**Author**: PayReady AI Team
**Status**: Active

## Overview
PayReady AI implements a unified architecture integrating Claude CLI, Codex (GPT-5), and Agno agents into a cohesive development environment with intelligent routing, live context management, and comprehensive documentation.

## System Architecture

### Core Components

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
    │                │                │              │
    └────────────────┴────────────────┴──────────────┘
                     │
         ┌───────────▼───────────┐
         │   Context Manager     │
         │  (Redis/File-based)   │
         └───────────────────────┘
```

### 1. Intelligent Router (`ai-router.py`)
**Purpose**: Route natural language queries to appropriate AI tool

**Features**:
- Weighted intent detection with confidence scoring
- Pattern matching for complex queries
- Ambiguous query detection and clarification
- Fallback handling for unavailable tools

**Implementation**:
```python
def calculate_intent_score(query: str, tool_config: Dict) -> float:
    score = 0.0
    # Weighted keyword matching
    for keyword, weight in tool_config['primary_triggers'].items():
        if keyword in query.lower():
            score += weight
    # Regex pattern bonus
    for pattern in tool_config['patterns']:
        if re.search(pattern, query.lower()):
            score += 15
    return score
```

### 2. Context Manager (`services/context_manager.py`)
**Purpose**: Maintain shared state and context across all AI tools

**Features**:
- Real-time project state tracking
- Git integration for change monitoring
- Active file detection (24-hour window)
- Cross-platform date handling
- Redis with file-based fallback

**Data Structure**:
```json
{
  "timestamp": "2025-09-18T13:00:00",
  "date": "2025-09-18",
  "cutoff_date": "2025-06-10",
  "project_root": "/Users/lynnmusil/payready-ai",
  "active_files": [...],
  "recent_changes": [...],
  "git_status": {...},
  "environment": {...}
}
```

### 3. Date Context System (`bin/get-date-context.sh`)
**Purpose**: Provide consistent date/time context across all tools

**Features**:
- Cross-platform compatibility (GNU/BSD date)
- Python fallback for date calculations
- 100-day cutoff for web searches
- Environment variable export

### 4. Documentation System (`bin/ai-docs`)
**Purpose**: Living documentation management

**Categories**:
- ARCHITECTURE: System design & technical architecture
- GUIDES: How-to guides & tutorials
- REFERENCES: API docs, configuration references
- OPERATIONS: Live operational docs (auto-updated)
- DECISIONS: Architecture Decision Records (ADRs)

**Commands**:
- `list [category]`: List documentation
- `show <doc>`: Display specific document
- `search <query>`: Search documentation
- `update`: Update live documents
- `validate`: Check consistency
- `changelog`: Generate from git history

## Integration Points

### 1. Environment Management (direnv)
```bash
# .envrc
[[ -f ~/.config/payready/env.llm ]] && dotenv ~/.config/payready/env.llm
[[ -f ~/.config/payready/env.github ]] && dotenv ~/.config/payready/env.github
eval $(./bin/get-date-context.sh)
export PATH="$PWD/bin:$PATH"
```

### 2. API Keys Configuration
```
~/.config/payready/
├── env.llm        # OpenAI, Anthropic keys
├── env.web        # Perplexity, Brave, Exa keys
├── env.github     # GitHub PAT and settings
└── env.agno       # Agno configuration
```

### 3. Git Integration
- Automatic documentation updates on commit
- Changelog generation from commit history
- GitHub authentication via PAT and SSH

## Web Access Implementation

### Supported APIs
1. **Perplexity**: Real-time web search
2. **Brave Search**: Privacy-focused search
3. **Exa**: Semantic search
4. **ZenRows**: Web scraping (removed)
5. **Apify**: Automation platform

### Date Filtering
All web searches enforce strict 2025-only filtering:
```bash
# codex-current script
QUERY="$1 site:* after:${CUTOFF_DATE} 2025"
```

## Error Handling & Resilience

### 1. Fallback Chains
- Claude CLI → Codex (if unavailable)
- Redis → File storage (if Redis down)
- GNU date → BSD date → Python (cross-platform)

### 2. Timeout Protection
- 30-second timeout on all external commands
- Graceful degradation on API failures

### 3. Debug Mode
```bash
DEBUG=true ai "your query"
DEBUG=true codex "your prompt"
```

## Security Considerations

1. **API Key Storage**:
   - Stored in `~/.config/payready/` with 600 permissions
   - Never committed to version control
   - Loaded via direnv on directory entry

2. **GitHub Authentication**:
   - Personal Access Token for HTTPS
   - ED25519 SSH key for secure connections
   - Token-based authentication for API calls

## Performance Optimizations

1. **Caching**:
   - Redis TTL: 1 hour for context data
   - Git status cached for 60 seconds

2. **Parallel Processing**:
   - Batch tool calls where possible
   - Concurrent file operations

3. **Lazy Loading**:
   - Context manager singleton pattern
   - On-demand API initialization

## Usage Examples

### Natural Language Interface
```bash
# Code generation
ai "write a FastAPI endpoint for user authentication"

# Code analysis
ai "refactor the payment processing module"

# Web search (2025 only)
ai "search latest Python 3.13 features"

# Documentation
ai docs list
ai docs search "architecture"
ai docs update
```

### Direct Tool Access
```bash
# Codex (GPT-5)
codex "implement binary search in Python"
codex gpt-5 "explain quantum computing"

# Web search with date filtering
codex-current "FastAPI best practices September 2025"

# Documentation management
ai-docs show UNIFIED_AI_INTEGRATION_ARCHITECTURE
ai-docs validate
```

### Explicit Routing
```bash
ai "claude: analyze the authentication flow"
ai "web: latest AI developments"
ai "agno: deploy to production"
```

## Monitoring & Logging

### Log Locations
- Router logs: `/tmp/ai-router.log`
- Context manager: Python logging to stderr
- Git operations: Standard git logs

### Health Checks
```bash
# Test GitHub connection
./bin/git-setup test

# Check context manager
python3 -m services.context_manager

# Validate documentation
ai docs validate
```

## Future Enhancements

1. **Planned Features**:
   - [ ] Multi-model consensus for complex decisions
   - [ ] Automatic code review on git push
   - [ ] Slack integration for team notifications
   - [ ] Performance metrics dashboard

2. **Optimization Opportunities**:
   - [ ] Implement request batching
   - [ ] Add response caching layer
   - [ ] Optimize context manager queries

3. **Integration Expansions**:
   - [ ] Jenkins/GitHub Actions CI/CD
   - [ ] Kubernetes deployment configs
   - [ ] Terraform infrastructure as code

## Troubleshooting

### Common Issues

1. **Empty Codex responses**:
   ```bash
   DEBUG=true codex "your query"
   ```

2. **direnv errors**:
   ```bash
   direnv allow
   ```

3. **Date calculation failures**:
   - Install GNU coreutils: `brew install coreutils`
   - Or ensure Python 3 is available

4. **API authentication issues**:
   - Check keys in `~/.config/payready/env.*`
   - Verify API quotas and limits

## References

- [Context Manager Documentation](./CONTEXT_MANAGER.md)
- [CLI Reference](../REFERENCES/CLI_REFERENCE.md)
- [Setup Guide](../GUIDES/SETUP_GUIDE.md)
- [API Documentation](../REFERENCES/API_REFERENCE.md)

---
*This is a living document. Last auto-update: 2025-09-18*