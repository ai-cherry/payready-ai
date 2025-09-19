# PayReady AI Development Environment Report
Generated: September 18, 2025

## Environment Variables

### Primary LLM Provider Keys
```bash
# Gateway Routing
PORTKEY_API_KEY=nYraiE8dOR9A1gDwaRNpSSXRkXBc
PORTKEY_VK_ANTHROPIC=anthropic-vk-b42804
PORTKEY_VK_OPENAI=openai-vk-e36279
PORTKEY_VK_XAI=xai-vk-e65d0f
PORTKEY_VK_PERPLEXITY=perplexity-vk-56c172
PORTKEY_VK_GROQ=groq-vk-6b9b52
PORTKEY_VK_DEEPSEEK=deepseek-vk-24102f
PORTKEY_VK_OPENROUTER=openrouter-vk-789abc

# Direct Provider Access
OPENROUTER_API_KEY=sk-or-v1-[REDACTED]
OPENAI_API_KEY=sk-svcacct-[REDACTED]
ANTHROPIC_API_KEY=sk-ant-api03-[REDACTED]
XAI_API_KEY=xai-[REDACTED]
PERPLEXITY_API_KEY=pplx-[REDACTED]
```

### Web Research & Scraping
```bash
BRAVE_API_KEY=BSApz0194z7SG6DplmVozl7ttFOi0Eo
SERPER_API_KEY=7b616d4bf53e98d9169e89c25d6f4bf4389a9ed5
TAVILY_API_KEY=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
EXA_API_KEY=fdf07f38-34ad-44a9-ab6f-74ca2ca90fd4
APIFY_API_TOKEN=apify_api_GlLw4ETpvZgjmOVLYx5XDL4d91IhFJ0gr9pi
ZENROWS_API_KEY=dba8152e8ded37bbd3aa5e464c8269b93225b648
```

### Memory & Storage Systems
```bash
# Redis Cloud
REDIS_URL=redis://default:[REDACTED]@redis-15014.force172.us-east-1-1.ec2.redns.redis-cloud.com:15014
REDIS_HOST=redis-15014.force172.us-east-1-1.ec2.redns.redis-cloud.com
REDIS_PORT=15014

# Mem0 Long-term Memory
MEM0_API_KEY=m0-migu5eMnfwT41nhTgVHsCnSAifVtOf3WIFz2vmQc
MEM0_ACCOUNT_ID=org_gHuEO2H7ymIIgivcWeKI2psRFHUnbZ54RQNYVb4T
MEM0_BASE_URL=https://api.mem0.ai/v1

# Milvus Vector Database
MILVUS_API_KEY=d21d225d7b5f192996ff5c89e2b725eb0f969818ffa8c18393a3a92f52fbff837052ccba69993f4165bd209c4764bc9d67bcc923
MILVUS_URI=milvus.db
MILVUS_COLLECTION=payready_vectors

# Neon Postgres
NEON_API_KEY=napi_r3gsuacduzw44nqdqav1u0hr2uv4bb2if48r8627jkxo7e4b2sxn92wsgf6zlxby
NEON_DATABASE_URL=postgresql://neondb_owner:[REDACTED]@rough-union-72390895.us-east-2.aws.neon.tech/neondb?sslmode=require
NEON_PROJECT_ID=rough-union-72390895
NEON_BRANCH_ID=br-green-firefly-afykrx78
```

### Monitoring & Observability
```bash
# LangChain/LangSmith
LANGCHAIN_API_KEY=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
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=payready-ai

# AgentOps
AGENTOPS_API_KEY=9e312405-09fd-46ac-9145-7b2d860f6d65

# Agno Platform
AGNO_API_KEY=phi-0cnOaV2N-MKID0LJTszPjAdj7XhunqMQFG4IwLPG9dI
```

### External Services
```bash
# BI & Analytics
APOLLO_IO_API_KEY=n-I9eHckqmnURzE1Zk82xg
SLACK_BOT_TOKEN=  # Empty

# Infrastructure
PULUMI_ACCESS_TOKEN=pul-f60e05d69c13efa7a73abea7a7bf09c668fbc2dc
N8N_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.[REDACTED]

# Neo4j Graph Database
NEO4J_CLIENT_ID=jPSJvG4itnj6DHbdUwm9dBTjeimb9wXv
NEO4J_CLIENT_SECRET=q5XHZu1GOrsJK7bcOByHCNxZy3LrCF3iVg-fVaHLwyj6N5nRFe_Fif-YORMtWfPy

# GitHub
GITHUB_TOKEN=github_pat_11A5VHXCI0[REDACTED]

# Additional LLM Providers
TOGETHER_AI_API_KEY=tgp_v1_HE_uluFh-fELZDmEP9xKZXuSBT4a8EHd6s9CmSe5WWo
```

### Project-Specific Variables
```bash
PAYREADY_PROJECT_ROOT=/Users/lynnmusil/payready-ai
PAYREADY_PROJECT_NAME=payready-ai
PAYREADY_BUILD_DATE=2025-09-18
PAYREADY_VERSION=3.0.0
PAYREADY_ENV=production
AI_DEBUG=false

# OpenRouter Configuration
OPENROUTER_REFERER=https://payready.ai
OPENROUTER_TITLE=PayReady AI CLI
```

## Key Handling Strategy

### Current Storage Methods
1. **Environment Variables** (Primary)
   - Loaded via direnv from `~/.config/payready/env.*` files
   - Direct export in shell sessions
   - Accessible to both Python CLI and bash scripts

2. **Config File Locations**
   ```
   ~/.config/payready/
   ├── env.core          # Project metadata
   ├── env.llm           # LLM provider keys
   ├── env.services      # Infrastructure services
   ├── env.agno          # Agno platform
   ├── env.biz           # Business tools
   ├── env.github        # GitHub tokens
   ├── env.memory        # Memory systems
   ├── env.platform      # Platform services
   └── env.rag           # RAG configurations
   ```

3. **Security Measures**
   - Most sensitive files have `600` permissions (user read/write only)
   - Keys stored in plaintext environment files
   - No encryption or vault integration
   - Files excluded from git via patterns

4. **Authentication States**
   - **Codex CLI**: Authenticated via `~/.codex/auth.json`
   - **GitHub**: Personal access token stored
   - **Cloud Services**: All API keys active

## SDK & API Client Integrations

### Python SDKs (via pip/pyproject.toml)
| Package | Version | Language | Integration Method |
|---------|---------|----------|-------------------|
| **AI/LLM Clients** ||||
| openai | ≥1.0.0 | Python | Direct import |
| anthropic | ≥0.25.0 | Python | Direct import |
| agentops | ≥0.3.0 | Python | Direct import |
| tiktoken | ≥0.5.0 | Python | Direct import |
| sentence-transformers | ≥3.0.0 | Python | Direct import |
| langgraph | ≥0.2.0 | Python | Direct import |
| **Data & Storage** ||||
| redis | ≥5.0.0 | Python | Direct import |
| milvus-lite | ≥2.4.1 | Python | Direct import |
| psycopg[binary] | ≥3.2 | Python | PostgreSQL adapter |
| pandas | ≥2.2.0 | Python | Direct import |
| **Web & HTTP** ||||
| httpx | ≥0.27.2 | Python | Async HTTP client |
| requests | ≥2.31.0 | Python | HTTP client |
| beautifulsoup4 | ≥4.12.0 | Python | HTML parsing |
| lxml | ≥4.9.0 | Python | XML/HTML parser |
| **Framework** ||||
| fastapi | ≥0.104.0 | Python | Web framework |
| uvicorn[standard] | ≥0.24.0 | Python | ASGI server |
| pydantic | ≥2.5.0 | Python | Data validation |
| typer | ≥0.12.3 | Python | CLI framework |

### External CLI Tools
| Tool | Purpose | Installation Method | Integration |
|------|---------|-------------------|-------------|
| **codex** | GPT-5 Codex access | Binary download | CLI wrapper in bin/ai |
| **jq** | JSON processing | Homebrew | Required by bin/ai |
| **curl** | HTTP requests | System/Homebrew | Required by bin/ai |
| **tmux** | Terminal multiplexer | Homebrew | Development sessions |
| **direnv** | Environment loader | Homebrew | Auto-loads env files |
| **ripgrep (rg)** | Fast text search | Homebrew | Development tools |
| **fd** | File finder | Homebrew | Development tools |

### Gateway Integration Pattern
```
CLI Request → bin/ai → Portkey Gateway → Provider APIs
                 ↓
           Python CLI → cli/config.py → Direct SDK calls
```

## CLI Tooling Inventory

### System Environment
- **OS**: macOS (Darwin 24.4.0)
- **Architecture**: Apple Silicon (ARM64)
- **Shell**: Bash (default)

### Core Development Tools
```bash
# Language Runtimes
Python 3.13.7                    # Primary runtime
Node.js v24.8.0                  # Frontend/tooling
npm 11.6.0                       # Package manager
Ruby (system)                    # System scripting
Java (system)                    # JVM tools

# Package Managers
pip 25.2                         # Python packages
Homebrew                         # macOS packages
npm 11.6.0                       # Node packages

# Essential CLI Tools
jq                               # JSON processing
curl                             # HTTP client
git                              # Version control
tmux                             # Terminal multiplexer
direnv                           # Environment management
ripgrep (rg)                     # Text search
fd                               # File search
```

### Python Virtual Environment
```bash
# Located at: .venv/
# Key installed binaries:
ai                               # Main CLI entry point
black, blackd                    # Code formatting
pytest                           # Testing
mypy, dmypy                      # Type checking
isort                            # Import sorting
ruff                             # Linting
huggingface-cli, hf              # HuggingFace tools
httpx                            # HTTP CLI
dotenv                           # Environment management
```

### Custom Project Scripts
```bash
# Project bin/
./bin/ai                         # Unified AI CLI (22KB bash script)

# Development scripts/
scripts/dev.sh                   # Tmux development session
scripts/init_session.sh          # Session initialization
scripts/command_logger.sh        # Command logging
scripts/consolidate_env.sh       # Environment consolidation
scripts/migrate-to-unified.sh    # Architecture migration
scripts/rotate_memory.sh         # Memory cleanup
scripts/smoke_cli.sh             # Quick testing
```

## Project-Specific Setup Configuration

### Environment Loading Chain
1. **direnv** automatically loads environment on directory entry
2. **`.envrc`** sources files from `~/.config/payready/`
3. **Scripts** explicitly load `config/ports.env`
4. **Python CLI** loads via `cli/config.py`

### Development Workflow Automation

#### 1. Tmux Development Session (`scripts/dev.sh`)
```bash
# Creates 3-window tmux session:
SESSION_NAME=payready
├── Window 0: prompt (main development)
├── Window 1: events (tail -F .project/memory/events.jsonl)
└── Window 2: logs (tail -F .project/memory/logs/cli.log)

# Environment setup:
PAYREADY_TMUX_STATE=.project/memory/tmux
PAYREADY_PROJECT_ROOT=/Users/lynnmusil/payready-ai
MEMORY_DIR=.project/memory
```

#### 2. Memory & Logging System
```bash
# Project memory structure:
.project/memory/
├── cli.log.jsonl           # CLI command logging
├── events.jsonl            # System events
├── logs/cli.log            # Standard logging
├── runs/                   # Execution records
├── session-log.md          # Session notes
└── tmux/                   # Tmux state
```

#### 3. Environment File Structure
```bash
~/.config/payready/
├── env.core                # PAYREADY_* variables
├── env.llm                 # LLM provider keys
├── env.services            # Infrastructure services
├── env.agno                # Agno platform
├── env.biz                 # Business integrations
├── env.github              # GitHub tokens (600 perms)
├── env.memory              # Memory systems (600 perms)
├── env.platform            # Platform services
├── env.rag                 # RAG configurations
└── backup_20250918_192427/ # Automatic backups
```

### Build & Deployment Setup

#### Makefile Targets
```makefile
run                         # python -m payready.cli tekton --goal "$(GOAL)"
fast                        # Consensus-free execution
planonly                    # Planning phase only
index                       # Repository indexing
route-test                  # Test routing logic
artifacts                   # Test artifacts
lint                        # Code linting (ruff check)
```

#### Project Scripts in pyproject.toml
```toml
[project.scripts]
payready = "payready.cli:main"
tekton = "tekton.cli:main"
ai = "payready_cli:main"
payready-ai = "payready_cli:main"
payready-memory = "payready_cli:memory"
payready-cli = "cli.cli:main_entry"
```

### Directory Structure & Integration Points

#### Core Project Layout
```
/Users/lynnmusil/payready-ai/
├── bin/ai                  # Main CLI entry point
├── cli/                    # Python CLI framework
├── config/                 # Configuration templates
├── core/                   # Core Python modules
├── gateway/                # API gateway
├── orchestrator/           # Task orchestration
├── services/               # Service implementations
├── tools/                  # Utility tools
├── local_rag/              # RAG implementation
├── bi/                     # Business intelligence
├── tekton/                 # Tekton CLI
├── payready/               # Main package
├── swarms/                 # Agent swarms
├── scripts/                # Development scripts
├── .venv/                  # Python virtual environment
├── .project/memory/        # Session memory
└── pyproject.toml          # Python project config
```

#### Cross-Tool Integration Points

1. **Token Sharing**
   - Environment variables accessible to all tools
   - Portkey gateway centralizes LLM access
   - Direct SDK fallbacks for reliability

2. **Configuration Synchronization**
   - `cli/config.py` loads subset of environment
   - `bin/ai` loads all environment files
   - Templates in `config/` for distribution

3. **Memory & State Sharing**
   - `.project/memory/` shared across tools
   - JSON lines format for events
   - Tmux state persistence

4. **Development Tool Chain**
   - direnv → environment loading
   - tmux → session management
   - Custom scripts → workflow automation
   - Python CLI → core functionality
   - Bash wrapper → routing logic

### External Dependencies Management
- **No package-lock.json**: Pure Python project
- **No Dockerfile**: Local development focused
- **No docker-compose.yml**: Single-machine setup
- **Virtual environment**: `.venv/` for Python isolation
- **Homebrew**: System tool management
- **direnv**: Automatic environment loading

## Summary

This is a **local development environment** optimized for AI/LLM experimentation with:

- **39 active API keys** across LLM providers, web services, and infrastructure
- **Multi-modal access patterns**: Portkey gateway + direct SDK access
- **Comprehensive tooling**: Python + Node.js + system tools
- **Session-based workflow**: tmux + memory system + automated logging
- **Configuration flexibility**: Multiple env file patterns for different use cases

The setup prioritizes **rapid experimentation** and **comprehensive integration** over security hardening, reflecting its single-user development context.