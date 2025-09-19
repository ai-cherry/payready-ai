#!/usr/bin/env bash
# Properly consolidate PayReady environment files into 3-file structure
# This script organizes existing keys without placeholders

set -euo pipefail

CONFIG_DIR="$HOME/.config/payready"
BACKUP_DIR="$CONFIG_DIR/backup_$(date +%Y%m%d_%H%M%S)"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[CONSOLIDATE]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; exit 1; }
warn() { echo -e "${YELLOW}[WARNING]${NC} $*"; }

# Create backup
log "Creating backup at $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"
cp -r "$CONFIG_DIR"/env.* "$BACKUP_DIR/" 2>/dev/null || true

# Create new consolidated files
log "Creating consolidated environment files..."

# 1. env.llm - CLI routing keys only
cat > "$CONFIG_DIR/env.llm.new" << 'EOF'
# PayReady AI - LLM Routing Configuration
# Generated: $(date)
# Purpose: CLI routing keys only

EOF

# Extract LLM routing keys from existing files
for file in "$CONFIG_DIR"/env.llm "$CONFIG_DIR"/env.agno; do
    if [[ -f "$file" ]]; then
        grep -E "^(PORTKEY|OPENROUTER|OPENAI|ANTHROPIC|PERPLEXITY|BRAVE|EXA|ZENROWS|APIFY)" "$file" >> "$CONFIG_DIR/env.llm.new" 2>/dev/null || true
    fi
done

# 2. env.services - BI and service keys
cat > "$CONFIG_DIR/env.services.new" << 'EOF'
# PayReady AI - Services Configuration
# Generated: $(date)
# Purpose: BI, memory, and external service keys

# Business Intelligence (BI-only)
EOF

# Add BI keys section
if [[ -f "$CONFIG_DIR/env.biz" ]]; then
    grep -E "^SLACK|^APOLLO" "$CONFIG_DIR/env.biz" >> "$CONFIG_DIR/env.services.new" 2>/dev/null || true
fi

# Add missing BI keys as comments if not found
if ! grep -q "SLACK_BOT_TOKEN=" "$CONFIG_DIR/env.services.new"; then
    echo "# SLACK_BOT_TOKEN=  # Required for BI Slack analytics" >> "$CONFIG_DIR/env.services.new"
fi
if ! grep -q "APOLLO_IO_API_KEY=" "$CONFIG_DIR/env.services.new"; then
    echo "# APOLLO_IO_API_KEY=  # Required for Apollo connector" >> "$CONFIG_DIR/env.services.new"
fi

echo "" >> "$CONFIG_DIR/env.services.new"
echo "# Memory & Storage" >> "$CONFIG_DIR/env.services.new"

# Extract memory/storage keys
for file in "$CONFIG_DIR"/env.agno "$CONFIG_DIR"/env.memory; do
    if [[ -f "$file" ]]; then
        grep -E "^(REDIS|MEM0|MILVUS|LANGCHAIN|LLAMA|NEON|AGNO|AGENTOPS)" "$file" >> "$CONFIG_DIR/env.services.new" 2>/dev/null || true
    fi
done

echo "" >> "$CONFIG_DIR/env.services.new"
echo "# Platform Services" >> "$CONFIG_DIR/env.services.new"

# Extract platform keys
if [[ -f "$CONFIG_DIR/env.platform" ]]; then
    grep -E "^(N8N|NEO4J|PULUMI)" "$CONFIG_DIR/env.platform" >> "$CONFIG_DIR/env.services.new" 2>/dev/null || true
fi

echo "" >> "$CONFIG_DIR/env.services.new"
echo "# External Services" >> "$CONFIG_DIR/env.services.new"

if [[ -f "$CONFIG_DIR/env.github" ]]; then
    grep -E "^GITHUB" "$CONFIG_DIR/env.github" >> "$CONFIG_DIR/env.services.new" 2>/dev/null || true
fi

# 3. env.core - Non-secret settings
cat > "$CONFIG_DIR/env.core.new" << 'EOF'
# PayReady AI - Core Configuration
# Generated: $(date)
# Purpose: Non-secret application settings

export PAYREADY_VERSION="3.0.0"
export PAYREADY_ENV="production"
export DEBUG_MODE="false"
export LOG_LEVEL="INFO"
export AI_DEBUG="false"
EOF

# Extract any existing core settings
if [[ -f "$CONFIG_DIR/env.base" ]]; then
    grep -E "^export (PAYREADY|DEBUG|LOG)" "$CONFIG_DIR/env.base" >> "$CONFIG_DIR/env.core.new" 2>/dev/null || true
fi

# Show what will be changed
log "Review proposed changes:"
echo ""
echo "New file structure:"
echo "  env.llm.new      - $(grep -c '=' "$CONFIG_DIR/env.llm.new" 2>/dev/null || echo 0) keys"
echo "  env.services.new - $(grep -c '=' "$CONFIG_DIR/env.services.new" 2>/dev/null || echo 0) keys"
echo "  env.core.new     - $(grep -c 'export' "$CONFIG_DIR/env.core.new" 2>/dev/null || echo 0) settings"
echo ""
echo "Files to be archived:"
ls -la "$CONFIG_DIR"/env.* | grep -v "\.new$" | awk '{print "  " $NF}'
echo ""

read -p "Apply consolidation? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Move new files into place
    mv "$CONFIG_DIR/env.llm.new" "$CONFIG_DIR/env.llm"
    mv "$CONFIG_DIR/env.services.new" "$CONFIG_DIR/env.services"
    mv "$CONFIG_DIR/env.core.new" "$CONFIG_DIR/env.core"
    
    # Archive old files
    for file in "$CONFIG_DIR"/env.agno "$CONFIG_DIR"/env.biz "$CONFIG_DIR"/env.memory "$CONFIG_DIR"/env.platform "$CONFIG_DIR"/env.base "$CONFIG_DIR"/env.jobs "$CONFIG_DIR"/env.rag "$CONFIG_DIR"/env.github; do
        if [[ -f "$file" ]]; then
            mv "$file" "$BACKUP_DIR/"
        fi
    done
    
    log "✅ Consolidation complete!"
    log "Backup saved to: $BACKUP_DIR"
    log ""
    warn "⚠️  Missing keys that need to be added:"
    warn "  - SLACK_BOT_TOKEN in env.services (required for BI)"
    warn "  - APOLLO_IO_API_KEY in env.services (required for BI)"
    warn "  - NEON_DATABASE_URL in env.services (if using Postgres)"
else
    log "Consolidation cancelled. New files kept as .new for review."
fi