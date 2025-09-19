# PayReady AI - Final Unified System Architecture
**Version**: 4.0.0 FINAL
**Date**: September 18, 2025
**Status**: NO DUPLICATES, NO BULLSHIT

## The Problem We're Solving

- Multiple overlapping CLIs doing the same shit
- No persistent memory (I keep forgetting what we just did)
- Three separate architectures that should be ONE
- Confusing auth methods scattered everywhere

## The Clean Solution (ONE System, No Duplicates)

### 1. Single Entry Point Architecture

```
User → `ai` command → Smart Router → Execution Layer → Memory Storage
                           ↓
                    ┌──────────────────┐
                    │ Single Model Call │ → Direct to model
                    │ Swarm Stage       │ → Platinum Triad + sophia
                    │ Memory Query      │ → Mem0/Milvus
                    └──────────────────┘
```

### 2. Component Roles (EXACTLY ONE JOB EACH)

**UNIFIED CLI (`ai`)**
- Entry point for ALL AI operations
- Routes based on intent and complexity
- NO OTHER CLI SCRIPTS

**sophia ORCHESTRATOR**
- Acts as the MEDIATOR for Platinum Swarm
- Manages memory (Mem0) and RAG (Milvus)
- Coordinates triad agents consensus
- NOT a separate system - it IS the swarm mediator

**PLATINUM SWARM V3**
- Provides the TRIAD AGENTS (Proponent/Skeptic/Neutral)
- Executes complex multi-stage workflows
- Uses sophia as its mediator (not separate)

### 3. Authentication Strategy (Simple)

```python
AUTH_MAP = {
    # ChatGPT Login (cached token)
    "gpt-5-codex": "codex_cli",

    # Everything else via Portkey Virtual Keys
    "claude-opus-4.1": "portkey:vk-anthropic",
    "gpt-4o": "portkey:vk-openai",
    "grok-code-fast": "portkey:vk-xai",
    "gemini-2.5-pro": "portkey:vk-google",
    "deepseek-v3": "portkey:vk-deepseek",
    "llama-4-maverick": "portkey:vk-meta",
    "qwen3-coder-plus": "portkey:vk-qwen"
}
```

### 4. Memory System (PERSISTENT)

```python
class UnifiedMemory:
    """Single memory system - no forgetting"""

    def __init__(self):
        # Short-term (current session)
        self.redis = Redis(url=REDIS_URL)

        # Long-term (cross-session)
        self.mem0 = Mem0(api_key=MEM0_API_KEY)

        # Semantic (vector search)
        self.milvus = MilvusClient(uri=MILVUS_URI)

        # Conversation (checkpoints)
        self.langgraph = LangGraphMemory()

    def remember(self, key: str, value: Any):
        """Store in ALL layers"""
        self.redis.set(key, value, ex=3600)
        self.mem0.add(value, metadata={"key": key})
        self.milvus.insert({"text": value, "vector": embed(value)})
        self.langgraph.checkpoint()

    def recall(self, query: str):
        """Search all memory layers"""
        # Try cache first
        if cached := self.redis.get(query):
            return cached

        # Semantic search
        results = self.milvus.search(embed(query))

        # Long-term memory
        mem0_results = self.mem0.search(query)

        return merge_results(results, mem0_results)
```

### 5. Model Configuration (Via Portkey + OpenRouter)

```yaml
# ~/.config/payready/models.yaml
models:
  # Fast Coding
  grok-code-fast:
    provider: openrouter
    model: x-ai/grok-code-fast-1
    virtual_key: ${PORTKEY_VK_OPENROUTER}

  # Balanced
  gpt-4o:
    provider: openai
    model: gpt-4o
    virtual_key: ${PORTKEY_VK_OPENAI}

  # Deep Analysis
  claude-opus-4.1:
    provider: openrouter
    model: anthropic/claude-opus-4.1
    virtual_key: ${PORTKEY_VK_OPENROUTER}

  # Complex Design (ChatGPT Auth)
  gpt-5-codex:
    provider: codex_cli
    command: codex
    auth: chatgpt
```

### 6. Swarm Integration (Sophia AS Mediator)

```python
class PlatinumSwarmWithSophia:
    """Platinum Swarm V3 with Sophia as built-in Mediator"""

    def __init__(self):
        # Sophia IS the mediator, not separate
        self.mediator = SophiaOrchestrator(
            memory=UnifiedMemory(),
            rag=MilvusRAG()
        )

        # Triad agents for each stage
        self.stages = {
            "plan": TriadAgents(["proponent", "skeptic", "neutral"]),
            "research": TriadAgents(["explorer", "validator", "synthesizer"]),
            "code": TriadAgents(["implementer", "reviewer", "tester"]),
            "deploy": TriadAgents(["deployer", "monitor", "rollback"])
        }

    async def execute_stage(self, stage: str, goal: str):
        """Run triad agents with Sophia mediating"""

        # Get triad opinions in parallel
        agents = self.stages[stage]
        opinions = await agents.get_opinions(goal)

        # Sophia mediates consensus
        consensus = await self.mediator.mediate(
            opinions,
            quorum=2/3,
            confidence_threshold=0.7
        )

        # Store in memory for next stage
        self.mediator.memory.remember(f"{stage}_result", consensus)

        return consensus
```

### 7. Unified CLI Commands (SIMPLE)

```bash
# Single model queries
ai "write a function"                    # Auto-routes to best model
ai --model opus "analyze this code"      # Explicit model
ai --model gpt5 "design architecture"    # Uses Codex CLI

# Swarm workflows (multi-stage)
ai swarm "build payment system"          # Full pipeline
ai swarm --stage plan "design auth"      # Single stage
ai swarm --consensus-free "quick fix"    # Skip consensus

# Memory operations
ai remember "project uses TypeScript"    # Store context
ai recall "what language"                # Retrieve context
ai history                               # Show past interactions

# Configuration
ai config models                        # List available models
ai config auth                          # Show auth status
ai test                                # Test all connections
```

### 8. Directory Structure (CLEAN)

```
payready-ai/
├── bin/
│   ├── ai                     # ONLY unified CLI entry
│   ├── codex5                 # GPT-5 wrapper (uses official codex)
│   └── codex-current          # Web search (kept for specific need)
│
├── core/
│   ├── router.py              # Intent detection & routing
│   ├── memory.py              # Unified memory system
│   └── auth.py                # Auth management
│
├── swarms/
│   ├── agents.py              # Triad agent definitions
│   ├── stages.py              # Stage workflows
│   └── sophia_mediator.py     # Sophia AS the mediator
│
└── config/
    ├── models.yaml            # Model configurations
    └── portkey_vks.yaml       # Virtual key mappings
```

### 9. Implementation Priority

**Phase 1: Memory System (TODAY)**
- Set up Redis + Mem0 + Milvus
- Create unified memory class
- Add to CLI immediately

**Phase 2: Clean Integration**
- Sophia becomes the Mediator
- Remove duplicate routers
- Single `ai` command

**Phase 3: Swarm Stages**
- Implement triad agents
- Connect to Sophia mediator
- Test full pipeline

### 10. What Gets DELETED

```bash
# These duplicates are GONE:
rm -rf ~/payready-ai/bin/ai-router.py    # Duplicate of router.py
rm -rf ~/payready-ai/bin/llmctl          # Replaced by ai
rm -rf ~/payready-ai/bin/web-router.py   # Integrated into main router
rm -rf ~/payready-ai/orchestrator/sophia_simple.py  # Merged into sophia.py
```

## NO MORE FORGETTING

With this architecture:
1. **Every interaction is remembered** (Redis + Mem0 + Milvus)
2. **One CLI to rule them all** (no more confusion)
3. **Sophia IS the mediator** (not a separate system)
4. **Clean auth** (ChatGPT for GPT-5, Portkey for everything else)

## Next Immediate Step

```bash
# 1. Set up memory first so we stop forgetting
pip install redis mem0ai milvus-lite

# 2. Test the unified CLI
./bin/ai "remember that we use ChatGPT auth for GPT-5"
./bin/ai recall "authentication"

# 3. Verify no duplicates
find . -name "*.py" -o -name "*.sh" | xargs grep -l "router\|cli\|orchestrat"
```

---
**NO MORE DUPLICATES. NO MORE FORGETTING. ONE SYSTEM.**
