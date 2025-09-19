#!/bin/bash
# Activate PayReady AI environment

export PAYREADY_HOME="/Users/lynnmusil/payready-ai"
export PATH="$PAYREADY_HOME/bin:$PATH"
source "/Users/lynnmusil/payready-ai/.venv/bin/activate"
source "/Users/lynnmusil/payready-ai/config/env.local"

alias ai="/Users/lynnmusil/payready-ai/bin/ai"
alias tekton="python -m tekton.cli"
alias payready="python -m payready.cli"

echo "PayReady AI environment activated!"
echo "Commands available: ai, tekton, payready"
