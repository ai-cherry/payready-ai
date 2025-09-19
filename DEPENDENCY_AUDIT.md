# PayReady AI Dependency & Environment Audit
Generated: September 18, 2025

## Executive Summary
Comprehensive audit of dependency declarations and environment configurations reveals a functioning but fragmented system with multiple configuration patterns, hard-coded secrets in templates, and inconsistencies between runtime loaders and environment templates.

## 1. Dependency Table

### Python Dependencies (pyproject.toml)
| Package | Version | Purpose | Required |
|---------|---------|---------|----------|
| **Core Framework** ||||
| fastapi | ≥0.104.0 | Web framework | Yes |
| uvicorn[standard] | ≥0.24.0 | ASGI server | Yes |
| pydantic | ≥2.5.0 | Data validation | Yes |
| typer | ≥0.12.3 | CLI framework | Yes |
| click | ≥8.1.0 | CLI utilities | Yes |
| rich | ≥13.5.0 | Terminal formatting | Yes |
| **AI/LLM** ||||
| openai | ≥1.0.0 | OpenAI API client | Yes |
| anthropic | ≥0.25.0 | Anthropic API client | Yes |
| langgraph | ≥0.2.0 | LangChain graph | Yes |
| tiktoken | ≥0.5.0 | Token counting | Yes |
| agentops | ≥0.3.0 | Agent monitoring | Optional |
| **Data Storage** ||||
| redis | ≥5.0.0 | Cache/session store | Yes |
| milvus-lite | ≥2.4.1 | Vector database | Optional |
| psycopg[binary] | ≥3.2 | PostgreSQL client | Optional |
| **ML/Embeddings** ||||
| sentence-transformers | ≥3.0.0 | Text embeddings | Optional |
| pandas | ≥2.2.0 | Data processing | Yes |
| **Web/Scraping** ||||
| httpx | ≥0.27.2 | HTTP client | Yes |
| requests | ≥2.31.0 | HTTP requests | Yes |
| beautifulsoup4 | ≥4.12.0 | HTML parsing | Optional |
| lxml | ≥4.9.0 | XML/HTML parser | Optional |
| **Utilities** ||||
| python-dotenv | ≥1.0.0 | Environment loading | Yes |
| pyyaml | ≥6.0.1 | YAML parsing | Yes |
| orjson | ≥3.9.0 | Fast JSON | Yes |
| cryptography | ≥41.0.0 | Encryption | Yes |
| tqdm | ≥4.65.0 | Progress bars | Yes |
| **Dev Tools** (optional-dependencies) ||||
| pytest | ≥7.4.0 | Testing | Dev only |
| black | ≥23.0.0 | Code formatting | Dev only |
| ruff | ≥0.5.0 | Linting | Dev only |
| mypy | ≥1.5.0 | Type checking | Dev only |

### External Tools (Referenced in scripts/configs)
| Tool | Location | Purpose | Required |
|------|----------|---------|----------|
| jq | bin/ai | JSON processing | Yes |
| curl | bin/ai | HTTP requests | Yes |
| codex | bin/ai, agents.toml | GPT-5 Codex binary | Optional |
| tmux | scripts/init_session.sh | Terminal multiplexer | Optional |
| direnv | .envrc | Environment loader | Optional |
| git | Multiple scripts | Version control | Yes |
| make | Makefile | Build automation | Dev only |

## 2. Environment Variable Matrix

### Core LLM Routing (Portkey/OpenRouter)
| Variable | Purpose | Required | Defined In | Consumed By |
|----------|---------|----------|------------|-------------|
| PORTKEY_API_KEY | Primary gateway auth | Yes* | ports.env, env.llm.template | cli/config.py, bin/ai |
| PORTKEY_VIRTUAL_KEY | Default virtual key | Yes* | ports.env | cli/config.py |
| PORTKEY_BASE_URL | Gateway endpoint | No | ports.env | cli/config.py, bin/ai |
| OPENROUTER_API_KEY | Fallback gateway | Yes* | ports.env, env.llm.template | cli/config.py, bin/ai |
| PORTKEY_VK_XAI | X.AI routing | No | env.llm.template, .env.example | bin/ai |
| PORTKEY_VK_ANTHROPIC | Anthropic routing | No | env.llm.template, .env.example | bin/ai |
| PORTKEY_VK_OPENAI | OpenAI routing | No | env.llm.template, .env.example | bin/ai |
| PORTKEY_VK_PERPLEXITY | Perplexity routing | No | env.llm.template, .env.example | bin/ai |
| PORTKEY_VK_GROQ | Groq routing | No | env.llm.template, .env.example | bin/ai |
| PORTKEY_VK_DEEPSEEK | DeepSeek routing | No | env.llm.template, .env.example | bin/ai |
*At least one of PORTKEY_API_KEY or OPENROUTER_API_KEY required

### Research/Web Providers
| Variable | Purpose | Required | Defined In | Consumed By |
|----------|---------|----------|------------|-------------|
| BRAVE_API_KEY | Brave search | Optional | research.env.example | cli/config.py |
| SERPER_API_KEY | Serper search | Optional | research.env.example | cli/config.py |
| TAVILY_API_KEY | Tavily search | Optional | research.env.example | cli/config.py |
| PERPLEXITY_API_KEY | Perplexity search | Optional | research.env.example, env.llm.template | cli/config.py |
| EXA_API_KEY | Exa search | Optional | research.env.example, env.llm.template | cli/config.py |
| FIRECRAWL_API_KEY | Web scraping | Optional | research.env.example | cli/config.py |
| APIFY_API_TOKEN | Web automation | Optional | research.env.example, env.llm.template | cli/config.py |
| ZENROWS_API_KEY | Web scraping | Optional | research.env.example, env.llm.template | cli/config.py |
| BROWSERLESS_API_KEY | Browser automation | Optional | research.env.example | cli/config.py |

### Memory & Storage Systems
| Variable | Purpose | Required | Defined In | Consumed By |
|----------|---------|----------|------------|-------------|
| REDIS_URL | Redis connection URL | No | env.services.template | Unknown |
| AGNO__REDIS_URL | Agno Redis URL | No | .env.example | Unknown |
| MEM0_API_KEY | Mem0 memory API | No | env.services.template | Unknown |
| MEM0_BASE_URL | Mem0 endpoint | No | env.services.template | Unknown |
| MILVUS_URI | Milvus vector DB | No | env.services.template, .env.example | Unknown |
| MILVUS_API_KEY | Milvus auth | No | env.services.template | Unknown |
| NEON_DATABASE_URL | Postgres URL | No | env.services.template, .env.example | Unknown |
| AGNO__PG_DSN | Postgres DSN | No | .env.example | Unknown |

### Monitoring & Observability
| Variable | Purpose | Required | Defined In | Consumed By |
|----------|---------|----------|------------|-------------|
| LANGCHAIN_API_KEY | LangSmith monitoring | No | env.services.template | Unknown |
| LANGCHAIN_TRACING_V2 | Enable tracing | No | env.services.template | Unknown |
| LANGCHAIN_PROJECT | Project name | No | env.services.template | Unknown |
| AGENTOPS_API_KEY | AgentOps monitoring | No | env.services.template | Unknown |
| AGNO_API_KEY | Agno platform | No | env.services.template | Unknown |

### External Services
| Variable | Purpose | Required | Defined In | Consumed By |
|----------|---------|----------|------------|-------------|
| SLACK_BOT_TOKEN | Slack integration | No | env.services.template, .env.example | BI module |
| APOLLO_IO_API_KEY | Apollo.io API | No | env.services.template, .env.example | BI module |
| N8N_API_KEY | Workflow automation | No | env.services.template | Unknown |
| PULUMI_ACCESS_TOKEN | IaC deployment | No | env.services.template | Unknown |
| NEO4J_CLIENT_ID | Graph DB auth | No | env.services.template | Unknown |
| NEO4J_CLIENT_SECRET | Graph DB secret | No | env.services.template | Unknown |

## 3. Configuration Consistency Analysis

### ✅ Consistent Elements
- `cli/config.py` properly loads from `ports.env` and `research.env`
- Portkey configuration aligned between loader and templates
- Research provider keys properly optional

### ❌ Inconsistencies & Issues

1. **Multiple ENV file patterns:**
   - `.envrc` expects `env.core`, `env.llm`, `env.services` in `~/.config/payready/`
   - `cli/config.py` expects `ports.env`, `research.env` in `config/`
   - Templates use `env.llm.template`, `env.services.template`
   - `.env.example` provides yet another pattern

2. **Runtime loader gaps:**
   - `cli/config.py` doesn't load from `env.services.template` variables
   - No runtime support for Milvus, Mem0, Neo4j configurations
   - `bin/ai` script loads all `env.*` files but `cli/config.py` only loads specific ones

3. **Hard-coded secrets in templates:**
   - `env.services.template` contains actual API keys (Redis, Mem0, Milvus, LangChain, etc.)
   - Should be placeholders like in `env.llm.template`

4. **Virtual key fallbacks:**
   - `bin/ai` has hard-coded fallback virtual keys (e.g., `xai-vk-e65d0f`)
   - These should be documented or removed

5. **Model name mismatches:**
   - `agents.toml` references `openai/gpt-5-codex`
   - `bin/ai` references models like `openai/gpt-5-mini`, `openai/gpt-4.1-mini`
   - September 2025 model names may be incorrect/placeholder

## 4. Optional vs Required Analysis

### Required Core Dependencies
- Portkey or OpenRouter API key (at least one)
- Python ≥3.11
- Core Python packages (fastapi, pydantic, typer, etc.)
- System tools: jq, curl, git

### Optional Features
| Feature | Dependencies | ENV Variables |
|---------|--------------|---------------|
| RAG/Embeddings | sentence-transformers, milvus-lite | MILVUS_* |
| Web Research | beautifulsoup4, lxml | BRAVE_API_KEY, etc. |
| BI Analytics | psycopg, pandas | SLACK_BOT_TOKEN, APOLLO_IO_API_KEY |
| Memory Systems | redis | MEM0_*, REDIS_* |
| Monitoring | agentops | LANGCHAIN_*, AGENTOPS_* |
| GPT-5 Codex | codex binary | (uses ChatGPT auth) |

## 5. Gaps & Risks

### 🔴 Critical Issues
1. **Hard-coded secrets** in `env.services.template` - Security risk
2. **Configuration fragmentation** - Multiple patterns cause confusion
3. **No requirements.txt** - Python deps only in pyproject.toml

### 🟡 Medium Risks
1. **Undocumented dependencies** - codex binary, tmux plugins not documented
2. **Model name confusion** - Future-dated model names (Sept 2025)
3. **Missing validation** - No env variable validation at startup

### 🟢 Minor Issues
1. **Duplicate env definitions** across multiple templates
2. **Inconsistent placeholder format** - Some use `<KEY>`, others empty strings
3. **No version pinning** for external tools (jq, curl)

## 6. Recommendations

### Immediate Actions
1. **Remove hard-coded secrets** from `env.services.template` - replace with placeholders
2. **Consolidate env patterns:**
   - Use single location: `~/.config/payready/`
   - Standardize on 3 files: `env.core`, `env.llm`, `env.services`
   - Update `cli/config.py` to match `.envrc` pattern

3. **Create requirements.txt** from pyproject.toml for compatibility:
   ```bash
   pip-compile pyproject.toml -o requirements.txt
   ```

### Short-term Improvements
1. **Document all dependencies:**
   - Add DEPENDENCIES.md with external tool requirements
   - Document minimum versions for jq, curl, etc.
   - Explain optional features and their requirements

2. **Implement env validation:**
   - Add startup checks in `cli/config.py`
   - Provide clear error messages for missing required vars
   - Add `ai doctor` command to validate environment

3. **Standardize placeholders:**
   - Use consistent format: `${VARIABLE_NAME}`
   - Add comments explaining each variable's purpose

### Long-term Architecture
1. **Single source of truth:**
   - Move all config to `pyproject.toml` or dedicated config package
   - Generate env templates programmatically
   - Use Pydantic settings throughout

2. **Feature flags:**
   - Implement proper feature detection
   - Auto-disable features with missing dependencies
   - Provide clear feature status reporting

3. **Secrets management:**
   - Integrate with secret managers (AWS Secrets, 1Password CLI)
   - Never store actual keys in repo
   - Implement key rotation reminders

## Conclusion
The PayReady AI system is functional but needs consolidation. Priority should be removing hard-coded secrets, standardizing configuration patterns, and documenting dependencies clearly before freezing the tooling.