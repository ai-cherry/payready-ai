# PayReady AI Setup Guide
**Version**: 3.0.0
**Last Updated**: 2025-09-18
**Status**: Active

## Prerequisites

### System Requirements
- **Python**: 3.11+ (required)
- **Operating System**: macOS, Linux, Windows
- **RAM**: 2GB minimum, 4GB recommended
- **Disk**: 500MB for dependencies

### Required Tools
- `git` - Version control
- `curl` - API requests
- `jq` - JSON processing
- `direnv` - Environment management (recommended)

### Install Prerequisites

#### macOS (Homebrew)
```bash
brew install python@3.11 git curl jq direnv
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3.11 python3-pip git curl jq direnv
```

#### Windows (PowerShell)
```powershell
# Install Python 3.11+ from python.org
# Install Git from git-scm.com
# Install curl (usually included)
# Install jq from stedolan.github.io/jq/
```

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/ai-cherry/payready-ai.git
cd payready-ai
```

### 2. Install Dependencies
```bash
# Install Python package and dependencies
pip install -e .

# Or using uv (faster)
uv pip install -e .
```

### 3. Environment Setup

#### Option A: Using direnv (Recommended)
```bash
# Enable direnv for automatic environment loading
direnv allow

# This loads configuration from .envrc automatically
```

#### Option B: Manual Environment
```bash
# Create config directory
mkdir -p ~/.config/payready

# Add to your shell profile (.bashrc, .zshrc, etc.)
export PATH="$PWD/bin:$PATH"
export PAYREADY_PROJECT_ROOT="$PWD"
```

### 4. Configure API Keys

#### Essential Configuration
```bash
# Create LLM configuration file
cat > ~/.config/payready/env.llm << 'EOF'
# PRIMARY: Portkey API key for intelligent routing
export PORTKEY_API_KEY="pk_your-portkey-key-here"

# FALLBACK: OpenRouter API key (required for backup routing)
export OPENROUTER_API_KEY="sk-or-v1-your-key-here"

# Optional: Direct provider keys
export ANTHROPIC_API_KEY="sk-ant-your-anthropic-key"
export OPENAI_API_KEY="sk-proj-your-openai-key"

# Portkey Virtual Keys (auto-configured)
export PORTKEY_VK_OPENAI="openai-vk-e36279"
export PORTKEY_VK_ANTHROPIC="anthropic-vk-b42804"
export PORTKEY_VK_OPENROUTER="openrouter-api-b1ca79"
EOF
```

#### Optional Services Configuration
```bash
# Create services configuration file (optional)
cat > ~/.config/payready/env.services << 'EOF'
# Memory System (optional)
export REDIS_URL="redis://localhost:6379"
export MEM0_API_KEY="your-mem0-key"

# External APIs (optional)
export GITHUB_TOKEN="ghp_your-github-token"
EOF
```

#### Core Application Settings
```bash
# Create core configuration file
cat > ~/.config/payready/env.core << 'EOF'
export PAYREADY_VERSION="3.0.0"
export PAYREADY_ENV="production"
export DEBUG_MODE="false"
export LOG_LEVEL="INFO"
EOF
```

## Getting API Keys

### OpenRouter (Required)
1. Visit [openrouter.ai](https://openrouter.ai)
2. Sign up for an account
3. Go to "API Keys" section
4. Create a new API key
5. Copy the key (starts with `sk-or-v1-`)

### Optional Service Keys

#### Anthropic (for direct Claude access)
1. Visit [console.anthropic.com](https://console.anthropic.com)
2. Create account and get API key

#### Mem0 (for enhanced memory)
1. Visit [mem0.ai](https://mem0.ai)
2. Sign up and get API key

#### Redis (for caching)
```bash
# Install Redis locally
brew install redis  # macOS
sudo apt install redis-server  # Ubuntu

# Start Redis
redis-server  # Run in background
```

## Verification

### 1. Test Installation
```bash
# Check if main CLI works
./bin/ai --help

# Expected output: Usage information and available commands
```

### 2. Test API Connectivity
```bash
# Test OpenRouter connection
./bin/ai test

# Expected output: ✓ for successful connections
```

### 3. Test Basic Functionality
```bash
# Test simple query
./bin/ai "say hello"

# Expected output: AI-generated response
```

### 4. Test Memory System
```bash
# Store information
./bin/ai remember "test_key" "test_value"

# Retrieve information
./bin/ai recall "test_key"

# Check memory context
./bin/ai memory context
```

## Troubleshooting

### Common Issues

#### "Command not found: ai"
```bash
# Solution: Add bin directory to PATH
export PATH="$PWD/bin:$PATH"

# Or use full path
./bin/ai "your query"
```

#### "OPENROUTER_API_KEY not set"
```bash
# Solution: Check API key configuration
cat ~/.config/payready/env.llm

# Ensure key is properly exported
echo $OPENROUTER_API_KEY
```

#### "jq: command not found"
```bash
# Solution: Install jq
brew install jq          # macOS
sudo apt install jq      # Ubuntu
```

#### API Connection Errors
```bash
# Check internet connectivity
curl -I https://openrouter.ai

# Test API key manually
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
     https://openrouter.ai/api/v1/models
```

#### Memory System Issues
```bash
# Check if core/memory.py exists
ls -la core/memory.py

# Test memory system directly
python core/memory.py context
```

### Debug Mode
```bash
# Enable verbose output for debugging
./bin/ai --verbose "your query"

# Or set debug environment
export AI_DEBUG=true
./bin/ai "your query"
```

### Log Files
```bash
# Check system logs (if any errors)
tail -f ~/.payready/logs/error.log  # If logging is enabled
```

## Advanced Configuration

### Custom Model Selection
```bash
# Use specific model
./bin/ai --model "anthropic/claude-opus-4.1" "your query"

# Set default model preference in env.llm
echo 'export DEFAULT_MODEL="x-ai/grok-code-fast-1"' >> ~/.config/payready/env.llm
```

### Performance Optimization
```bash
# Enable Redis for better caching
brew install redis
redis-server &

# Set Redis URL
echo 'export REDIS_URL="redis://localhost:6379"' >> ~/.config/payready/env.services
```

### Development Setup
```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Code formatting
black .
ruff check .
```

## Next Steps

After successful setup:

1. **Read Documentation**: Check `docs/INDEX.md` for full documentation
2. **Explore Models**: Try different AI models with `./bin/ai --model <model> "query"`
3. **Memory Features**: Use remember/recall for persistent information
4. **Integration**: Explore Sophia orchestrator and RAG system

## Support

If you encounter issues:

1. **Check Documentation**: See `docs/TROUBLESHOOTING.md` (if available)
2. **GitHub Issues**: Report problems at the repository
3. **Debug Mode**: Use `--verbose` flag for detailed output

---

**You should now have a fully functional PayReady AI installation. Test it with: `./bin/ai "write a hello world function"`**