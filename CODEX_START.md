# 🚀 Codex Startup Instructions

## Quick Start
```bash
cd ~/payready-ai
direnv allow  # Auto-loads all API keys

# Test basic Codex
./bin/codex "Write a Python function"

# Test with specific model
./bin/codex gpt-5 "Explain quantum computing"
```

## Available Commands

### 1. **codex** - Direct GPT-5/Codex Access
```bash
# Basic usage (defaults to gpt-5-mini)
./bin/codex "Your prompt here"

# Specify model
./bin/codex gpt-5 "Your prompt"
./bin/codex gpt-5-nano "Quick task"

# Show available models
./bin/codex --models
```

**Available Models:**
- `gpt-5-mini` - Fastest, best for coding (default)
- `gpt-5` - Full model, highest capability
- `gpt-5-nano` - Smallest, quickest responses
- `gpt-5-chat-latest` - Chat-optimized
- `codex-mini-latest` - Code completion (requires org verification)

### 2. **codex-web** - Simulated Web Context
```bash
# Asks model to simulate web search
./bin/codex-web "Latest React features"
./bin/codex-web gpt-5 "Current Python trends 2025"
```
⚠️ **Note**: This doesn't actually search the web - it prompts the model to act as if it has web access.

### 3. **codex-search** - Real Web Search (via Perplexity)
```bash
# Requires PERPLEXITY_API_KEY in env.llm
./bin/codex-search "Latest FastAPI version and features"
```

### 4. **llmctl** - Smart Routing via Portkey
```bash
# Routes to best model for task type
./bin/llmctl coding "Write a REST API"
./bin/llmctl reasoning "Explain distributed systems"
./bin/llmctl fast "Quick Python snippet"
./bin/llmctl search "Latest AWS features"
```

**Routes:**
- `coding` → gpt-5-mini
- `codex` → codex-mini-latest
- `reasoning` → claude-3.7-sonnet
- `fast` → grok-2
- `search` → perplexity-sonar
- `deep` → deepseek-v3
- `stream` → groq-llama

## Web Access Reality Check

### ❌ What DOESN'T Have Web Access:
- OpenAI API models (gpt-5, gpt-5-mini, etc.)
- Claude API (claude-opus-4-1)
- Direct model APIs don't browse the web

### ✅ What DOES Have Web Access:
- **Claude Code (me)**: I have WebSearch and WebFetch tools
- **Perplexity API**: Real-time web search via `codex-search`
- **ChatGPT Plus**: Web browsing in chat interface (not API)

### 🧠 For Live Brainstorming:

**Option 1: Use Me (Claude Code)**
I have real web access via my tools:
```
Me: Search for latest Next.js features
[I'll use WebSearch to get current info]
```

**Option 2: Perplexity Pipeline**
```bash
# Get current info via Perplexity
./bin/codex-search "Latest Next.js 15 features"

# Then use GPT-5 to expand on it
./bin/codex gpt-5 "Based on Next.js 15 having server actions and partial prerendering, write an example"
```

**Option 3: Manual Context Injection**
```bash
# You provide the context
./bin/codex "Given that Next.js 15 has feature X, write code that..."
```

## Testing All Features

```bash
# Test 1: Basic Codex
./bin/codex "Hello world in Python"
✅ Should output Python code

# Test 2: GPT-5 Full Model
./bin/codex gpt-5 "Explain P vs NP"
✅ Should give detailed explanation

# Test 3: Model List
./bin/codex --models
✅ Should list all available models

# Test 4: Portkey Routing
export PORTKEY_API_KEY="nYraiE8dOR9A1gDwaRNpSSXRkXBc"
./bin/llmctl coding "REST API"
✅ Should route to gpt-5-mini

# Test 5: Test Script
./bin/test-models.sh
✅ Should test gpt-5-mini, gpt-5-codex, claude-opus-4-1
```

## Environment Setup

All keys are in `~/.config/payready/env.*`:

```bash
# Check if keys are loaded
echo $OPENAI_API_KEY     # Should show sk-svcacct-...
echo $PORTKEY_API_KEY    # Should show nYraiE8dOR...

# If not loaded, run:
cd ~/payready-ai
direnv allow
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "OPENAI_API_KEY not set" | Run `direnv allow` in project directory |
| "Model not found" | Check `./bin/codex --models` for available models |
| "gpt-5-codex requires verification" | Use gpt-5 or gpt-5-mini instead |
| "Web search not working" | Models don't have real web access - use me or Perplexity |

## Best Practices for Brainstorming

1. **For Current Info**: Ask me (Claude Code) - I have real web access
2. **For Code Generation**: Use `./bin/codex gpt-5-mini` (optimized for coding)
3. **For Complex Reasoning**: Use `./bin/llmctl reasoning` (routes to Claude)
4. **For Speed**: Use `./bin/codex gpt-5-nano` or `./bin/llmctl fast`

## Summary

- **Codex/GPT-5 models**: Available and working via API ✅
- **Real web access**: Only via Claude Code (me) or Perplexity API ✅
- **All models tested**: gpt-5-mini, gpt-5, gpt-5-nano working ✅
- **Routing configured**: Portkey routes to best model per task ✅

Ready for live brainstorming! 🚀