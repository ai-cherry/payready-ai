# PayReady AI Portkey Virtual Key Configuration
**Date**: September 18, 2025
**Version**: 3.0.0

## Virtual Key Mapping Strategy

Portkey virtual keys enable secure, centralized API key management with intelligent routing. This configuration optimizes for:
- **Intent-based routing**: Different models for different tasks
- **Cost optimization**: Use cheaper models when appropriate
- **Fallback resilience**: Multiple providers for redundancy
- **Performance**: Fast models for interactive use, powerful models for complex tasks

## Available Virtual Keys

```bash
# Your Portkey Virtual Keys (from dashboard)
ANTHROPIC-VK: anthropic-vk-b42804
DEEPSEEK-VK: deepseek-vk-24102f
GROQ-VK: groq-vk-6b9b52
PERPLEXITY-VK: perplexity-vk-56c172
TOGETHERAI-VK: together-ai-670469
OPENAI-VK: openai-vk-e36279
MILVUS-VK: milvus-vk-34fa02
GITHUB-VK: github-vk-a5b609
COHERE-VK: cohere-vk-496fa9
HUGGINGFACE-VK: huggingface-vk-28240e
STABILITY-VK: stability-vk-a575fb
MISTRAL-VK: mistral-vk-f92861
QDRANT-VK: qdrant-vk-d2b62a
XAI-VK: xai-vk-e65d0f
```

## Recommended Configuration

### 1. Update bin/ai Script

Modify the `get_virtual_key()` function to use optimal providers:

```bash
get_virtual_key() {
    local intent="$1"
    
    case "$intent" in
        code)
            # X.AI Grok - Best for code generation (Sept 2025)
            echo "${PORTKEY_VK_XAI:-xai-vk-e65d0f}"
            ;;
        analyze)
            # Claude Opus 4.1 - Best for analysis
            echo "${PORTKEY_VK_ANTHROPIC:-anthropic-vk-b42804}"
            ;;
        design)
            # OpenAI GPT-5 - Best for architecture
            echo "${PORTKEY_VK_OPENAI:-openai-vk-e36279}"
            ;;
        search)
            # Perplexity - Has real-time web access
            echo "${PORTKEY_VK_PERPLEXITY:-perplexity-vk-56c172}"
            ;;
        fast)
            # Groq - Ultra-fast inference
            echo "${PORTKEY_VK_GROQ:-groq-vk-6b9b52}"
            ;;
        deep)
            # DeepSeek v3 - Complex reasoning
            echo "${PORTKEY_VK_DEEPSEEK:-deepseek-vk-24102f}"
            ;;
        *)
            # Default to X.AI for general tasks
            echo "${PORTKEY_VK_XAI:-xai-vk-e65d0f}"
            ;;
    esac
}
```

### 2. Update Model Selection

Align models with virtual keys in `select_model()`:

```bash
select_model() {
    local intent="$1"
    
    case "$intent" in
        design)
            echo "openai/gpt-5-mini"  # Or gpt-4o for cost savings
            ;;
        analyze)
            echo "anthropic/claude-opus-4.1"
            ;;
        search)
            echo "perplexity/llama-3.3-sonar-large-128k-online"
            ;;
        code)
            echo "x-ai/grok-2-mini"  # Fast code generation
            ;;
        deep)
            echo "deepseek/deepseek-chat-v3"
            ;;
        fast)
            echo "groq/llama-3.2-90b-text-preview"
            ;;
        *)
            echo "x-ai/grok-2-mini"
            ;;
    esac
}
```

### 3. Environment File Structure

```bash
# ~/.config/payready/env.llm
# Primary Portkey Configuration
export PORTKEY_API_KEY="your-portkey-api-key"

# Virtual Keys for Intent-Based Routing
export PORTKEY_VK_XAI="xai-vk-e65d0f"
export PORTKEY_VK_ANTHROPIC="anthropic-vk-b42804"
export PORTKEY_VK_OPENAI="openai-vk-e36279"
export PORTKEY_VK_PERPLEXITY="perplexity-vk-56c172"
export PORTKEY_VK_GROQ="groq-vk-6b9b52"
export PORTKEY_VK_DEEPSEEK="deepseek-vk-24102f"

# Specialized Services
export PORTKEY_VK_COHERE="cohere-vk-496fa9"      # Embeddings
export PORTKEY_VK_MILVUS="milvus-vk-34fa02"      # Vector DB
export PORTKEY_VK_GITHUB="github-vk-a5b609"      # GitHub models
export PORTKEY_VK_STABILITY="stability-vk-a575fb" # Image gen

# Fallback
export PORTKEY_VK_TOGETHER="together-ai-670469"   # Aggregator
export OPENROUTER_API_KEY="sk-or-v1-xxx"         # Direct fallback
```

## Usage Patterns

### Quick Responses (Groq)
```bash
ai --intent fast "explain this error"
```

### Code Generation (X.AI Grok)
```bash
ai "write a Python function to parse JSON"
```

### Deep Analysis (Claude Opus)
```bash
ai --intent analyze "review this architecture"
```

### Web Search (Perplexity)
```bash
ai --intent search "latest React 19 features September 2025"
```

### Complex Reasoning (DeepSeek)
```bash
ai --intent deep "solve this algorithmic problem"
```

## Cost Optimization Tips

1. **Default to Grok-2-mini**: Fast and cost-effective for most tasks
2. **Use Groq for interactive**: Sub-second responses for chat
3. **Reserve Claude Opus**: Only for complex analysis
4. **Perplexity for search**: Has built-in web access, saves tokens
5. **DeepSeek for math/algorithms**: Specialized for reasoning

## Monitoring & Debugging

```bash
# Test virtual key routing
ai test

# Debug mode to see which key is used
AI_DEBUG=true ai "test query"

# Check Portkey dashboard for:
# - Usage by virtual key
# - Cost breakdown
# - Response times
# - Error rates
```

## Fallback Strategy

1. **Primary**: Portkey with virtual key
2. **Secondary**: Together AI (aggregator)
3. **Tertiary**: OpenRouter direct
4. **Emergency**: Direct provider APIs (if configured)

## Security Notes

- Virtual keys can be rotated without changing code
- Set rate limits per virtual key in Portkey dashboard
- Monitor usage to detect anomalies
- Use conditional routing for user tiers

## Next Steps

1. Configure each virtual key in Portkey dashboard with:
   - Appropriate provider API key
   - Rate limits
   - Cost budgets
   - Fallback rules

2. Test each intent path:
   ```bash
   for intent in code analyze design search fast deep; do
       echo "Testing $intent..."
       ai --intent $intent "hello world"
   done
   ```

3. Monitor performance and adjust routing as needed