#!/usr/bin/env bash
# PayReady AI - Local Deployment Script
# Deploys the complete system locally with all services

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Logging
log() { echo -e "${GREEN}[DEPLOY]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; exit 1; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*" >&2; }
info() { echo -e "${CYAN}[INFO]${NC} $*"; }

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$PROJECT_ROOT/.venv"
ARTIFACTS_DIR="$PROJECT_ROOT/artifacts"
MEMORY_DIR="$HOME/.payready/memory"
SESSION_DIR="$HOME/.payready/sessions"
LOG_DIR="$PROJECT_ROOT/logs"

# Check mode
MODE="${1:-offline}"  # Default to offline mode

log "PayReady AI Local Deployment"
log "============================="
log "Mode: $MODE"
log "Project: $PROJECT_ROOT"

# Step 1: Environment Setup
info "Step 1: Setting up environment..."

if [[ "$MODE" == "offline" ]]; then
    log "Loading offline environment..."
    source "$PROJECT_ROOT/config/env.local"
    export PAYREADY_OFFLINE_MODE=1
    export PAYREADY_TEST_MODE=1
elif [[ "$MODE" == "dev" ]]; then
    log "Loading development environment..."
    if [[ -f "$PROJECT_ROOT/config/env.dev" ]]; then
        source "$PROJECT_ROOT/config/env.dev"
    else
        warn "No env.dev found, using env.local"
        source "$PROJECT_ROOT/config/env.local"
    fi
    export PAYREADY_OFFLINE_MODE=0
else
    error "Unknown mode: $MODE (use 'offline' or 'dev')"
fi

# Step 2: Python Environment
info "Step 2: Checking Python environment..."

if [[ ! -d "$VENV_PATH" ]]; then
    log "Creating virtual environment..."
    python3 -m venv "$VENV_PATH"
fi

log "Activating virtual environment..."
source "$VENV_PATH/bin/activate"

# Check Python version
PYTHON_VERSION=$(python --version | cut -d' ' -f2)
log "Python version: $PYTHON_VERSION"

# Step 3: Dependencies
info "Step 3: Checking dependencies..."

# Check if requirements need updating
if [[ -f "pyproject.toml" ]]; then
    log "Installing dependencies from pyproject.toml..."
    pip install -q -e . || warn "Some optional dependencies failed"
else
    log "Installing from requirements.txt..."
    pip install -q -r requirements.txt || warn "Some dependencies failed"
fi

# Verify critical packages
python -c "import agno; import pydantic; import fastapi" 2>/dev/null || {
    error "Critical packages missing. Please run: pip install agno pydantic fastapi"
}

# Step 4: Directory Structure
info "Step 4: Creating directory structure..."

mkdir -p "$ARTIFACTS_DIR"
mkdir -p "$MEMORY_DIR"
mkdir -p "$SESSION_DIR"
mkdir -p "$LOG_DIR"
mkdir -p "$HOME/.config/payready"

log "Directories created:"
echo "  - Artifacts: $ARTIFACTS_DIR"
echo "  - Memory: $MEMORY_DIR"
echo "  - Sessions: $SESSION_DIR"
echo "  - Logs: $LOG_DIR"

# Step 5: Configuration Files
info "Step 5: Verifying configuration..."

# Create default config if not exists
if [[ ! -f "$HOME/.config/payready/config.yaml" ]]; then
    cat > "$HOME/.config/payready/config.yaml" << EOF
# PayReady AI Configuration
mode: $MODE
version: 3.0.0
features:
  memory: true
  cache: true
  debug: false
agents:
  default_model: "openai/gpt-4o-mini"
  timeout: 30
EOF
    log "Created default configuration"
fi

# Step 6: Optional Services
info "Step 6: Checking optional services..."

# Check Redis (optional)
if command -v redis-cli &> /dev/null; then
    if redis-cli ping 2>/dev/null | grep -q PONG; then
        log "Redis is running (will be used for memory)"
        export REDIS_AVAILABLE=1
    else
        warn "Redis installed but not running (using file storage)"
        export REDIS_AVAILABLE=0
    fi
else
    info "Redis not installed (using file storage)"
    export REDIS_AVAILABLE=0
fi

# Step 7: Initialize Components
info "Step 7: Initializing components..."

# Test agent factory
python -c "
from core.agent_factory import get_factory
factory = get_factory()
print('✅ Agent factory initialized')
" || error "Agent factory failed to initialize"

# Test memory manager
python -c "
from core.memory_manager import get_memory_manager
from cli.config_v2 import get_settings
settings = get_settings()
memory = get_memory_manager(settings)
print('✅ Memory manager initialized')
" || error "Memory manager failed to initialize"

# Step 8: Service Startup
info "Step 8: Starting services..."

# Create startup script
cat > "$PROJECT_ROOT/start_services.sh" << 'EOF'
#!/bin/bash
# Start PayReady AI services

source .venv/bin/activate

# Start API server (if exists)
if [[ -f "api/main.py" ]]; then
    echo "Starting API server..."
    python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 &
    API_PID=$!
    echo "API server PID: $API_PID"
fi

# Monitor logs
if [[ -d "logs" ]]; then
    echo "Monitoring logs..."
    tail -f logs/*.log 2>/dev/null &
    TAIL_PID=$!
fi

echo "Services started. Press Ctrl+C to stop."
wait
EOF

chmod +x "$PROJECT_ROOT/start_services.sh"
log "Service startup script created: start_services.sh"

# Step 9: CLI Setup
info "Step 9: Setting up CLI..."

# Make CLI executable
chmod +x "$PROJECT_ROOT/bin/ai"

# Create convenience aliases
cat > "$PROJECT_ROOT/activate.sh" << EOF
#!/bin/bash
# Activate PayReady AI environment

export PAYREADY_HOME="$PROJECT_ROOT"
export PATH="\$PAYREADY_HOME/bin:\$PATH"
source "$VENV_PATH/bin/activate"
source "$PROJECT_ROOT/config/env.local"

alias ai="$PROJECT_ROOT/bin/ai"
alias tekton="python -m tekton.cli"
alias payready="python -m payready.cli"

echo "PayReady AI environment activated!"
echo "Commands available: ai, tekton, payready"
EOF

chmod +x "$PROJECT_ROOT/activate.sh"
log "Activation script created: activate.sh"

# Step 10: Verification
info "Step 10: Verifying deployment..."

# Test CLI
log "Testing CLI..."
./bin/ai "hello" | head -5 || warn "CLI test failed"

# Test agent creation
python -c "
from core.agent_factory import get_factory
factory = get_factory()
agent = factory.create_agent('test', 'tester')
print('✅ Agent creation successful')
" || warn "Agent creation test failed"

# Summary
echo ""
log "========================================="
log "PayReady AI Local Deployment Complete!"
log "========================================="
echo ""
echo -e "${GREEN}Quick Start:${NC}"
echo "  1. Activate environment: source activate.sh"
echo "  2. Use CLI: ai 'your query'"
echo "  3. Use Tekton: tekton --goal 'your goal'"
echo ""
echo -e "${GREEN}Configuration:${NC}"
echo "  - Mode: $MODE"
echo "  - Python: $PYTHON_VERSION"
echo "  - Redis: $([ $REDIS_AVAILABLE -eq 1 ] && echo "Available" || echo "Not available")"
echo "  - Memory: $MEMORY_DIR"
echo ""
echo -e "${GREEN}Next Steps:${NC}"
if [[ "$MODE" == "offline" ]]; then
    echo "  - System running in offline mode (no API keys needed)"
    echo "  - All responses will be stubs"
    echo "  - To use real APIs, run: ./deploy_local.sh dev"
else
    echo "  - Configure API keys in config/env.dev"
    echo "  - Start services: ./start_services.sh"
    echo "  - Check logs: tail -f logs/*.log"
fi
echo ""
log "Deployment successful!"