#!/usr/bin/env bash
# Consolidate environment files from 9 to 3 as documented

set -euo pipefail

CONFIG_DIR="$HOME/.config/payready"
BACKUP_DIR="$CONFIG_DIR/backup_$(date +%Y%m%d_%H%M%S)"

echo "PayReady AI Environment Consolidation"
echo "======================================"
echo

# Create backup
echo "1. Creating backup..."
mkdir -p "$BACKUP_DIR"
cp "$CONFIG_DIR"/env.* "$BACKUP_DIR/" 2>/dev/null || true
echo "   ✓ Backed up to $BACKUP_DIR"

# Create consolidated env.core
echo "2. Creating env.core..."
cat > "$CONFIG_DIR/env.core" << 'EOF'
# PayReady AI Core Configuration
export PAYREADY_VERSION="3.0.0"
export PAYREADY_ENV="production"
export DEBUG_MODE="false"
export LOG_LEVEL="INFO"

# From env.base
export PROJECT_NAME="payready-ai"

# From env.jobs
export JOB_QUEUE="default"

# From env.biz
export BUSINESS_DOMAIN="ai"
EOF
echo "   ✓ Created env.core"

# Preserve env.llm but ensure it has OpenRouter key
echo "3. Updating env.llm..."
if ! grep -q "OPENROUTER_API_KEY" "$CONFIG_DIR/env.llm" 2>/dev/null; then
    echo "" >> "$CONFIG_DIR/env.llm"
    echo "# ADD YOUR KEY HERE - Required for fallback routing" >> "$CONFIG_DIR/env.llm"
    echo 'export OPENROUTER_API_KEY="sk-or-v1-YOUR_KEY_HERE"' >> "$CONFIG_DIR/env.llm"
fi
echo "   ✓ Updated env.llm"

# Create consolidated env.services
echo "4. Creating env.services..."
cat > "$CONFIG_DIR/env.services" << 'EOF'
# PayReady AI Services Configuration

# Memory System
export REDIS_URL="redis://localhost:6379"
export MEM0_API_KEY="${MEM0_API_KEY:-}"

# RAG System
export MILVUS_URI="milvus.db"
export MILVUS_DIM="384"
export EMBED_MODEL="all-MiniLM-L6-v2"
export COLLECTION_NAME="payready_docs"

# External Services
export GITHUB_TOKEN="${GITHUB_TOKEN:-}"

# Platform Services (from env.platform)
export PLATFORM_API_URL="https://api.payready.com"
export PLATFORM_ENV="development"

# Copy existing values if available
EOF

# Migrate existing values
if [[ -f "$CONFIG_DIR/env.memory" ]]; then
    grep "MEM0_API_KEY\|MILVUS_API_KEY" "$CONFIG_DIR/env.memory" >> "$CONFIG_DIR/env.services" 2>/dev/null || true
fi

if [[ -f "$CONFIG_DIR/env.github" ]]; then
    grep "GITHUB_TOKEN" "$CONFIG_DIR/env.github" >> "$CONFIG_DIR/env.services" 2>/dev/null || true
fi

echo "   ✓ Created env.services"

# Set proper permissions
echo "5. Setting secure permissions..."
chmod 600 "$CONFIG_DIR"/env.*
echo "   ✓ All files secured (600 permissions)"

# Remove old files (optional - uncomment to execute)
echo "6. Old files to remove (manual step):"
echo "   rm $CONFIG_DIR/env.base"
echo "   rm $CONFIG_DIR/env.jobs"
echo "   rm $CONFIG_DIR/env.biz"
echo "   rm $CONFIG_DIR/env.platform"
echo "   rm $CONFIG_DIR/env.memory"
echo "   rm $CONFIG_DIR/env.rag"
echo "   rm $CONFIG_DIR/env.agno"
echo "   rm $CONFIG_DIR/env.github"

echo
echo "======================================"
echo "Consolidation complete!"
echo
echo "You now have 3 environment files:"
echo "  - env.core     : Core application settings"
echo "  - env.llm      : AI model API keys"
echo "  - env.services : External service configurations"
echo
echo "⚠️  IMPORTANT: Add your OpenRouter API key to env.llm"
echo "Run: echo 'export OPENROUTER_API_KEY=\"sk-or-v1-YOUR_KEY\"' >> ~/.config/payready/env.llm"