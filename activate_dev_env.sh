#!/bin/bash
# PayReady AI Development Environment Activator
# Source this file to set up complete offline development environment

# Activate virtual environment if it exists
if [[ -f ".venv/bin/activate" ]]; then
    source .venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "⚠️  No virtual environment found at .venv/bin/activate"
fi

# Load offline environment with exports
set -a
source config/env.local
set +a

echo "✅ Offline environment loaded (PAYREADY_OFFLINE_MODE=$PAYREADY_OFFLINE_MODE)"
echo "✅ Development environment ready"
echo ""
echo "Usage:"
echo "  ./bin/ai \"your query here\"  # CLI with stub responses"
echo "  python -c \"from core.agent_factory import get_factory; print('Test')\"  # Python modules"
echo "  pytest tests/  # Run test suite"
