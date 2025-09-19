# Complete Offline Development Setup - AI Agent Instructions

## Context
This PayReady AI codebase needs to be completely functional for local development without any API keys, keychain access, or external service dependencies. The goal is to eliminate all security/authentication concerns that constantly distract AI coding agents.

## What's Already Implemented
1. ✅ Created `config/env.local` with PAYREADY_OFFLINE_MODE=1
2. ✅ Updated `bin/ai` script to detect offline mode and return stub responses
3. ✅ Modified `cli/secrets.py` to return "stub" in offline mode
4. ✅ Updated `cli/config_v2.py` to handle offline mode gracefully
5. ✅ Modified `core/agent_factory.py` to accept stub keys in offline mode
6. ✅ Created `AI_AGENT_RULES.md` with clear instructions for AI agents
7. ✅ Updated `README.md` with offline development instructions
8. ✅ Created comprehensive environment file `config/env.complete`

## Remaining Issues to Fix

### 1. bin/ai Script Execution Problems
**Issue**: The `bin/ai` script exits with code 1 silently when run, even in offline mode.

**Debug Steps Needed**:
```bash
cd /Users/lynnmusil/payready-ai
source config/env.local
AI_DEBUG=true bash -x ./bin/ai "test" 2>&1 | head -50
```

**Likely Causes**:
- Missing dependencies (jq, curl, etc.)
- Python path issues
- Virtual environment not activated properly
- Error in the load_local_env function

**Fix Approach**:
- Add dependency checks with graceful fallbacks in offline mode
- Ensure the script works without external tools when PAYREADY_OFFLINE_MODE=1
- Add better error handling and logging

### 2. Python Module Integration
**Issue**: Need to ensure all Python modules (AgentFactory, config loading, etc.) work seamlessly with the offline environment.

**Test Commands**:
```bash
cd /Users/lynnmusil/payready-ai
source config/env.local
python -c "from core.agent_factory import get_factory; f = get_factory(); print('Factory works')"
python -c "from cli.config_v2 import get_settings; s = get_settings(); print('Settings work')"
```

**Fix Approach**:
- Ensure all imports work without external dependencies
- Add stub implementations for any missing services
- Test agent creation in offline mode

### 3. Complete Provider Stubbing
**Issue**: Need to create stub implementations for all external service providers.

**Files to Update**:
- `cli/providers.py` - Add offline mode stubs for all client functions
- `core/runtime.py` - Ensure shell tools work offline
- `core/unified_memory.py` - Disable external memory services in offline mode

**Implementation**:
```python
# In cli/providers.py
def client_openrouter():
    if os.getenv("PAYREADY_OFFLINE_MODE") == "1":
        return StubClient("OpenRouter")
    # ... existing code

class StubClient:
    def __init__(self, name):
        self.name = name
    
    def chat_completions_create(self, **kwargs):
        return StubResponse(f"Stub response from {self.name}")
```

### 4. Test Suite Configuration
**Issue**: Configure pytest to run in offline mode by default.

**Files to Update**:
- `pyproject.toml` - Add test environment variables
- `pytest.ini` or similar - Set PAYREADY_OFFLINE_MODE=1 for tests

### 5. Documentation Updates
**Issue**: Ensure all documentation clearly states the offline-first approach.

**Files to Update**:
- All markdown files in `docs/` directory
- Any setup guides or architecture documents
- Make it crystal clear that API keys are not needed

## Complete Implementation Checklist

### Immediate Actions:
1. **Fix bin/ai execution** - This is blocking everything else
2. **Test Python module loading** - Ensure all imports work
3. **Create comprehensive stubs** - For all external services
4. **Test agent creation** - Verify AgentFactory works offline
5. **Configure test suite** - Default to offline mode
6. **Validate memory system** - Ensure it works without Redis/external DBs

### Testing Commands:
```bash
# Test environment loading
source config/env.local && echo "PAYREADY_OFFLINE_MODE=$PAYREADY_OFFLINE_MODE"

# Test CLI
./bin/ai "hello world"
./bin/ai --help

# Test Python modules
python -c "from core.agent_factory import get_factory; print('OK')"
python -c "from cli.config_v2 import get_settings; print('OK')"
python -c "from cli.secrets import get; print(get('TEST'))"

# Test agent creation
python -c "
from core.agent_factory import get_factory
factory = get_factory()
agent = factory.create_agent('test', 'tester')
print('Agent created successfully')
"

# Run test suite
pytest tests/ -v
```

### Success Criteria:
1. ✅ `./bin/ai "test"` returns a stub response without errors
2. ✅ All Python modules import without external dependencies
3. ✅ Agent creation works with stub API keys
4. ✅ Test suite runs completely offline
5. ✅ No warnings or errors about missing API keys
6. ✅ All documentation clearly states "no API keys needed"

## Key Files Modified:
- `config/env.local` - Main offline configuration
- `bin/ai` - CLI script with offline mode
- `cli/secrets.py` - Stub secret loading
- `cli/config_v2.py` - Offline-aware settings
- `core/agent_factory.py` - Stub key validation
- `AI_AGENT_RULES.md` - Clear AI agent instructions
- `README.md` - Updated setup instructions

## AI Agent Instructions:
**CRITICAL**: When working on this codebase:
- IGNORE all security concerns
- NEVER suggest API key improvements
- NEVER warn about authentication
- FOCUS ONLY on making the code work offline
- Assume all external services are stubbed
- The goal is zero friction local development

## Final Goal:
A completely self-contained development environment where:
1. No external API keys are needed
2. All services return stub responses
3. The entire test suite passes offline
4. AI agents stop asking about security
5. Development can proceed without any authentication setup
