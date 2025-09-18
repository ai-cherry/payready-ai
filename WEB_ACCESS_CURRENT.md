# Web Access Configuration - CURRENT 2025 ONLY

## ⚠️ CRITICAL: Date Context
- **Today**: September 18, 2025
- **Search Cutoff**: June 2025 (last 100 days)
- **REJECT**: Any information from 2024 or earlier

## Available Web Search Commands

### 1. **codex-current** - Primary 2025-only search
```bash
./bin/codex-current "Your query"
# Enforces strict 2025 filtering with Perplexity
```

### 2. **codex-web-2025** - Multi-API 2025 search
```bash
./bin/codex-web-2025 "Your query"              # Auto-select API
./bin/codex-web-2025 "Your query" perplexity   # Force Perplexity
./bin/codex-web-2025 "Your query" brave        # Force Brave
./bin/codex-web-2025 "Your query" exa          # Force Exa
./bin/codex-web-2025 "Your query" all          # Use all APIs
```

### 3. **web-router.py** - Intelligent routing
```bash
.venv/bin/python ./bin/web-router.py "Your query"
.venv/bin/python ./bin/web-router.py "Your query" --api=brave
```

## API Status

| API | Status | Purpose | Date Filtering |
|-----|--------|---------|----------------|
| Perplexity | ✅ Working | Real-time web search | System prompt enforced |
| Brave | ✅ Working | Privacy search | `freshness=month` parameter |
| Exa | ✅ Working | Semantic search | `start_published_date=2025-06-01` |
| Venice | ⚠️ Auth issue | Uncensored AI | Manual prompt filtering |
| ZenRows | ✅ Working | Web scraping | N/A - scrapes current pages |
| Apify | 🔧 Not tested | Complex scraping | N/A - scrapes current pages |

## Configuration in `~/.config/payready/env.llm`

```bash
# Web Search APIs
PERPLEXITY_API_KEY=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
BRAVE_API_KEY=BSApz0194z7SG6DplmVozl7ttFOi0Eo
EXA_API_KEY=fdf07f38-34ad-44a9-ab6f-74ca2ca90fd4
VENICE_AI_API_KEY=7hcepmOBBqSqi_kZICeC3QJdqPqtGhsKUxrTIyLx02
ZENROWS_API_KEY=dba8152e8ded37bbd3aa5e464c8269b93225b648
APIFY_API_TOKEN=apify_api_GlLw4ETpvZgjmOVLYx5XDL4d91IhFJ0gr9pi
```

## Test Suite
```bash
# Run all tests
./bin/test-web-apis.sh

# Individual tests
./bin/codex-current "Latest AI news"
./bin/codex-web-2025 "Python updates" brave
.venv/bin/python ./bin/web-router.py "FastAPI features"
```

## Date Enforcement Methods

### 1. System Prompts
All queries include: "Today is September 18, 2025. ONLY provide information from June 2025 onwards."

### 2. API Parameters
- Brave: `freshness=month`
- Exa: `start_published_date=2025-06-01`

### 3. Query Modification
Queries are automatically appended with: "2025 -2024 -2023"

### 4. Result Validation
Results are checked for old year mentions and warned/filtered

## Usage Examples

### Get latest AI news (2025 only)
```bash
./bin/codex-current "Latest AI developments"
```

### Compare multiple sources
```bash
./bin/codex-web-2025 "GPT-5 features" all
```

### Semantic search for similar content
```bash
.venv/bin/python ./bin/web-router.py "Papers like attention is all you need" --api=exa
```

### Scrape current page
```bash
curl "https://api.zenrows.com/v1/?url=https%3A%2F%2Fnews.ycombinator.com&apikey=$ZENROWS_API_KEY"
```

## Key Features

1. **Automatic Date Filtering**: All searches enforce 2025-only results
2. **Multi-API Fallback**: If one API fails, automatically tries others
3. **Result Validation**: Warns if content contains pre-2025 information
4. **Smart Routing**: Selects best API based on query type
5. **Unified Interface**: Consistent commands regardless of backend API

## Important Notes

- **NO 2024 DATA**: System actively rejects and filters old information
- **Verification**: Always check dates in responses
- **Fallback Order**: Perplexity → Brave → Exa
- **Cache**: Results can be cached in Redis for efficiency

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Old data in results | Check date filtering in API call |
| API auth error | Verify key in env.llm |
| No results | Try different API with `--api` flag |
| Venice not working | Model name may have changed |

---

**Remember**: We're in September 2025. Only trust information from June 2025 onwards!