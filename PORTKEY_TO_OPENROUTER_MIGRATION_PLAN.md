# Portkey to OpenRouter Migration Plan

## Executive Summary
Complete removal of Portkey dependencies and virtual keys from the PayReady AI codebase, migrating to a simplified OpenRouter-first architecture with AI/ML API as backup, featuring centralized model selection control.

## Current State Analysis

### Portkey Usage Locations
- **39 files** contain Portkey references
- **19 files** contain virtual key references
- **Core integration points**:
  - `bin/ai` - CLI routing logic
  - `core/llm_client/portkey_client.py` - Dedicated Portkey client
  - `cli/config.py` & `cli/config_v2.py` - Configuration management
  - `orchestrator/sophia.py` - LangGraph orchestration
  - `scripts/doctor.sh` - Health checks
  - Environment files in `~/.config/payready/`

### Current Virtual Keys (15 total)
```
PORTKEY_VK_XAI, PORTKEY_VK_ANTHROPIC, PORTKEY_VK_OPENAI
PORTKEY_VK_PERPLEXITY, PORTKEY_VK_GROQ, PORTKEY_VK_DEEPSEEK
PORTKEY_VK_MISTRAL, PORTKEY_VK_TOGETHER, PORTKEY_VK_COHERE
PORTKEY_VK_GITHUB, PORTKEY_VK_HUGGINGFACE, PORTKEY_VK_STABILITY
PORTKEY_VK_OPENROUTER, PORTKEY_VIRTUAL_KEY
```

## Target Architecture

### Simplified Stack
```
User Request
     ↓
CLI (bin/ai)
     ↓
Model Router (new: core/model_router.py)
     ↓
Provider Client
     ├─ Primary: OpenRouter Client
     └─ Backup: AI/ML API Client
```

### Centralized Model Configuration
```yaml
# config/models.yaml
models:
  # Code generation models
  code:
    primary: "deepseek/deepseek-coder"
    fallback: "anthropic/claude-3-sonnet"
    providers: ["openrouter", "aimlapi"]

  # Analysis models
  analyze:
    primary: "anthropic/claude-3-opus"
    fallback: "openai/gpt-4-turbo"
    providers: ["openrouter", "aimlapi"]

  # Fast responses
  fast:
    primary: "google/gemini-flash"
    fallback: "groq/llama-3-70b"
    providers: ["openrouter"]

  # Creative tasks
  creative:
    primary: "openai/gpt-4"
    fallback: "anthropic/claude-3-sonnet"
    providers: ["openrouter", "aimlapi"]

# Provider endpoints
providers:
  openrouter:
    base_url: "https://openrouter.ai/api/v1"
    api_key_env: "OPENROUTER_API_KEY"

  aimlapi:
    base_url: "https://api.aimlapi.com/v1"
    api_key_env: "AIMLAPI_KEY"
```

## Migration Steps

### Phase 1: Create New Infrastructure (Non-Breaking)

#### 1.1 Create Model Router
```python
# core/model_router.py
import os
import yaml
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ModelConfig:
    primary: str
    fallback: str
    providers: List[str]

class ModelRouter:
    def __init__(self, config_path: str = "config/models.yaml"):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        self.models = {
            k: ModelConfig(**v)
            for k, v in self.config['models'].items()
        }

    def select_model(self, intent: str, provider: Optional[str] = None) -> tuple[str, str]:
        """Returns (model_name, provider_name)"""
        model_config = self.models.get(intent, self.models['fast'])

        if provider and provider in model_config.providers:
            return model_config.primary, provider

        # Try providers in order
        for provider_name in model_config.providers:
            if self._provider_available(provider_name):
                return model_config.primary, provider_name

        # Fallback
        return model_config.fallback, model_config.providers[0]

    def _provider_available(self, provider: str) -> bool:
        key_env = self.config['providers'][provider]['api_key_env']
        return bool(os.getenv(key_env))
```

#### 1.2 Create OpenRouter Client
```python
# core/llm_client/openrouter_client.py
import os
import requests
from typing import List, Dict

class OpenRouterClient:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"

    def chat(self, model: str, messages: List[Dict], **kwargs) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://payready.ai",
            "X-Title": "PayReady AI"
        }

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json={
                "model": model,
                "messages": messages,
                **kwargs
            }
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
```

#### 1.3 Create AI/ML API Client
```python
# core/llm_client/aimlapi_client.py
import os
import requests
from typing import List, Dict

class AIMLAPIClient:
    def __init__(self):
        self.api_key = os.getenv("AIMLAPI_KEY")
        self.base_url = "https://api.aimlapi.com/v1"

    def chat(self, model: str, messages: List[Dict], **kwargs) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json={
                "model": model,
                "messages": messages,
                **kwargs
            }
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
```

### Phase 2: Update Core Components

#### 2.1 Files to Modify

**Priority 1 - Core Routing**
1. `bin/ai` - Remove Portkey checks, use new model router
2. `core/agent_factory.py` - Update to use new clients
3. `cli/config.py` & `cli/config_v2.py` - Remove Portkey configs
4. `core/runtime.py` - Update LLM client initialization

**Priority 2 - Scripts & Tools**
5. `scripts/doctor.sh` - Remove Portkey health checks
6. `scripts/setup_local.sh` - Remove Portkey setup
7. `scripts/verify_env.py` - Remove Portkey validation

**Priority 3 - Documentation**
8. Update all `.md` files to remove Portkey references
9. Update environment templates

#### 2.2 Environment Variable Changes

**Remove:**
- `PORTKEY_API_KEY`
- All `PORTKEY_VK_*` variables
- `PORTKEY_VIRTUAL_KEY`
- `USE_PORTKEY`

**Add:**
- `AIMLAPI_KEY` (for backup provider)
- `MODEL_CONFIG_PATH` (optional, defaults to config/models.yaml)
- `DEFAULT_PROVIDER` (optional, defaults to openrouter)

### Phase 3: Delete Obsolete Files

```bash
# Files to delete
rm core/llm_client/portkey_client.py
rm config/portkey_setup.md
rm config/ports.env  # If only contains Portkey config
```

### Phase 4: Testing & Validation

#### 4.1 Test Commands
```bash
# Test OpenRouter routing
export OPENROUTER_API_KEY="your-key"
unset PORTKEY_API_KEY
./bin/ai "test openrouter routing"

# Test AI/ML API fallback
export AIMLAPI_KEY="your-key"
unset OPENROUTER_API_KEY  # Force fallback
./bin/ai "test aimlapi routing"

# Test model selection
./bin/ai --intent code "write a function"
./bin/ai --intent analyze "analyze this code"
./bin/ai --intent fast "quick answer"
```

#### 4.2 Validation Checklist
- [ ] No Portkey references in codebase
- [ ] No virtual key references
- [ ] OpenRouter client working
- [ ] AI/ML API fallback working
- [ ] Model selection by intent
- [ ] Doctor script updated
- [ ] Tests passing without Portkey

## Implementation Checklist

### Day 1: Setup New Infrastructure
- [ ] Create `core/model_router.py`
- [ ] Create `core/llm_client/openrouter_client.py`
- [ ] Create `core/llm_client/aimlapi_client.py`
- [ ] Create `config/models.yaml`
- [ ] Test new components in isolation

### Day 2: Update Core Components
- [ ] Update `bin/ai` to use model router
- [ ] Update `core/agent_factory.py`
- [ ] Update `cli/config.py` and `cli/config_v2.py`
- [ ] Update `core/runtime.py`
- [ ] Test integrated system

### Day 3: Clean Scripts & Environment
- [ ] Update `scripts/doctor.sh`
- [ ] Update `scripts/setup_local.sh`
- [ ] Update `scripts/verify_env.py`
- [ ] Clean environment files in `~/.config/payready/`
- [ ] Update `.env` templates

### Day 4: Documentation & Cleanup
- [ ] Update all documentation files
- [ ] Delete obsolete Portkey files
- [ ] Update README with new setup instructions
- [ ] Create migration guide for existing users

### Day 5: Testing & Rollout
- [ ] Run full test suite
- [ ] Test all CLI commands
- [ ] Test Tekton pipeline
- [ ] Test agent creation and execution
- [ ] Deploy to production

## Benefits of Migration

1. **Simplification**: Remove 15+ virtual keys and complex routing logic
2. **Cost Reduction**: Eliminate Portkey service fees
3. **Direct Control**: Direct API access to providers
4. **Flexibility**: Easy to add new providers
5. **Maintainability**: Centralized model configuration
6. **Performance**: One less network hop
7. **Debugging**: Simpler request/response flow

## Rollback Plan

If issues arise:
1. Keep Portkey client as legacy fallback initially
2. Add feature flag: `USE_LEGACY_PORTKEY=1`
3. Gradual migration by intent type
4. A/B test with subset of users

## Configuration Examples

### Basic Setup
```bash
# ~/.config/payready/env.llm (new format)
export OPENROUTER_API_KEY="sk-or-v1-xxxxx"
export AIMLAPI_KEY="xxxxx"
export DEFAULT_PROVIDER="openrouter"
export MODEL_CONFIG_PATH="$HOME/.config/payready/models.yaml"
```

### Custom Model Mapping
```yaml
# ~/.config/payready/models.yaml
models:
  custom_task:
    primary: "meta-llama/llama-3-70b"
    fallback: "mistral/mistral-large"
    providers: ["openrouter", "aimlapi"]
```

### CLI Usage (unchanged)
```bash
# Auto-detects intent and routes appropriately
./bin/ai "write a Python function"

# Force specific model
./bin/ai --model "anthropic/claude-3-opus" "complex analysis"

# Force specific provider
./bin/ai --provider aimlapi "test backup provider"
```

## Success Metrics

- Zero Portkey API calls in production
- All tests passing with new architecture
- Response time improvement (measure baseline first)
- Simplified codebase (-500+ lines expected)
- Clear documentation for new setup

## Timeline

- **Week 1**: Implement new infrastructure alongside old
- **Week 2**: Test and validate in staging
- **Week 3**: Gradual production rollout
- **Week 4**: Remove all Portkey code

## Questions to Resolve

1. Should we keep any Portkey code for backwards compatibility?
2. What's the priority order for provider fallback?
3. Should model selection be configurable per user?
4. How to handle provider-specific features (e.g., streaming)?
5. Migration path for existing user configurations?

---

*This plan ensures a smooth transition from Portkey to OpenRouter while maintaining all functionality and improving system simplicity.*