#!/usr/bin/env bash
# PayReady AI - Local Environment Setup Script
# Run this to set up a fresh local environment

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[SETUP]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

log "PayReady AI Local Setup"
log "======================="

# 1. Check Python version
log "Checking Python version..."
if command -v python3 >/dev/null 2>&1; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    if [[ $(echo "$PYTHON_VERSION >= 3.11" | bc) -eq 1 ]]; then
        log "✅ Python $PYTHON_VERSION found"
    else
        error "Python 3.11+ required (found $PYTHON_VERSION)"
    fi
else
    error "Python 3 not found"
fi

# 2. Create/activate virtual environment
log "Setting up virtual environment..."
if [[ ! -d .venv ]]; then
    python3 -m venv .venv
    log "Created .venv"
fi
source .venv/bin/activate
log "✅ Virtual environment activated"

# 3. Install dependencies
log "Installing dependencies..."
pip install --upgrade pip >/dev/null 2>&1
pip install -e . >/dev/null 2>&1 || {
    warn "Some optional dependencies failed to install"
    log "Retrying with core dependencies only..."
    pip install -e . --no-deps >/dev/null 2>&1
    pip install pydantic pydantic-settings httpx openai anthropic keyring redis >/dev/null 2>&1
}
log "✅ Dependencies installed"

# 4. Create config directory
log "Setting up configuration..."
CONFIG_DIR="$HOME/.config/payready"
mkdir -p "$CONFIG_DIR"
chmod 700 "$CONFIG_DIR"

# 5. Create memory directory
mkdir -p .project/memory/logs
log "✅ Directories created"

# 6. Set permissions
if ls "$CONFIG_DIR"/env.* >/dev/null 2>&1; then
    chmod 600 "$CONFIG_DIR"/env.*
    log "✅ Permissions set on config files"
fi

# 7. Check for API keys
log "Checking API keys..."
HAS_KEY=false
for key_name in OPENROUTER_API_KEY AIMLAPI_KEY ANTHROPIC_API_KEY OPENAI_API_KEY; do
    if [[ -n "${!key_name:-}" ]] || grep -q "$key_name" "$CONFIG_DIR"/env.* 2>/dev/null; then
        log "✅ Found $key_name"
        HAS_KEY=true
        break
    fi
done

if [[ "$HAS_KEY" == "false" ]]; then
    warn "No API keys found!"
    echo ""
    read -p "Would you like to configure API keys now? (y/N) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ./bin/ai config setup
    else
        warn "Run './bin/ai config setup' to configure API keys later"
    fi
fi

# 8. Make scripts executable
chmod +x bin/ai scripts/*.sh scripts/*.py 2>/dev/null || true
log "✅ Scripts are executable"

# 9. Run verification
log "Running verification..."
python scripts/verify_env.py

# 10. Quick test
log "Testing CLI..."
if ./bin/ai --help >/dev/null 2>&1; then
    log "✅ CLI is working"
else
    error "CLI test failed"
fi

log ""
log "========================================="
log "✅ Setup Complete!"
log "========================================="
log ""
log "Next steps:"
log "  1. Source environment: source .venv/bin/activate"
log "  2. Test the CLI: ./bin/ai 'hello world'"
log "  3. Configure keys: ./bin/ai config setup"
log ""
log "For help: ./bin/ai --help"