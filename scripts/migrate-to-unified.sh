#!/usr/bin/env bash
# Migration Script - Consolidate PayReady AI to Unified Architecture
# Version: 1.0.0
# Date: September 18, 2025

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Directories
PAYREADY_HOME="${HOME}/payready-ai"
CONFIG_DIR="${HOME}/.config/payready"
BACKUP_DIR="${CONFIG_DIR}.backup.$(date +%Y%m%d_%H%M%S)"

# ============================================================================
# Helper Functions
# ============================================================================

log() {
    echo -e "${GREEN}[MIGRATE]${NC} $*"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
}

error() {
    echo -e "${RED}[ERROR]${NC} $*"
    exit 1
}

confirm() {
    read -p "$(echo -e "${YELLOW}$1${NC} [y/N]: ")" -n 1 -r
    echo
    [[ $REPLY =~ ^[Yy]$ ]]
}

# ============================================================================
# Pre-flight Checks
# ============================================================================

preflight_check() {
    log "Running pre-flight checks..."

    # Check if running from correct directory
    if [[ ! -d "$PAYREADY_HOME" ]]; then
        error "PayReady AI directory not found at $PAYREADY_HOME"
    fi

    # Check for required tools
    for tool in jq curl git; do
        if ! command -v $tool &>/dev/null; then
            error "Required tool '$tool' not installed"
        fi
    done

    # Check for existing configuration
    if [[ ! -d "$CONFIG_DIR" ]]; then
        error "Configuration directory not found at $CONFIG_DIR"
    fi

    log "Pre-flight checks passed ✓"
}

# ============================================================================
# Backup Current Configuration
# ============================================================================

backup_current() {
    log "Backing up current configuration to $BACKUP_DIR..."

    # Create backup
    cp -r "$CONFIG_DIR" "$BACKUP_DIR"

    # Backup bin directory
    if [[ -d "$PAYREADY_HOME/bin" ]]; then
        mkdir -p "$BACKUP_DIR/bin"
        cp -r "$PAYREADY_HOME/bin" "$BACKUP_DIR/"
    fi

    # Create restore script
    cat > "$BACKUP_DIR/restore.sh" <<'EOF'
#!/usr/bin/env bash
# Restore script for PayReady AI configuration

BACKUP_DIR="$(dirname "$0")"
CONFIG_DIR="${HOME}/.config/payready"
PAYREADY_HOME="${HOME}/payready-ai"

echo "Restoring from backup..."
rm -rf "$CONFIG_DIR"
cp -r "$BACKUP_DIR/$(basename $CONFIG_DIR)" "$CONFIG_DIR"

if [[ -d "$BACKUP_DIR/bin" ]]; then
    rm -rf "$PAYREADY_HOME/bin"
    cp -r "$BACKUP_DIR/bin" "$PAYREADY_HOME/"
fi

echo "Restore complete!"
EOF
    chmod +x "$BACKUP_DIR/restore.sh"

    log "Backup complete ✓"
}

# ============================================================================
# Consolidate Environment Files
# ============================================================================

consolidate_env() {
    log "Consolidating environment files..."

    # Create unified auth configuration
    cat > "$CONFIG_DIR/auth.conf" <<EOF
# PayReady AI Unified Authentication Configuration
# Generated: $(date)

# ============================================================================
# Primary Authentication
# ============================================================================

# Portkey Gateway (for all API-based models)
PORTKEY_API_KEY=${PORTKEY_API_KEY}

# ============================================================================
# Virtual Keys (Portkey)
# ============================================================================

# Production Keys
VK_CLAUDE_OPUS=${PORTKEY_VK_ANTHROPIC}
VK_GPT4O=${PORTKEY_VK_OPENAI}
VK_PERPLEXITY=${PORTKEY_VK_PERPLEXITY}
VK_XAI=${PORTKEY_VK_XAI}
VK_DEEPSEEK=${PORTKEY_VK_DEEPSEEK}
VK_GROQ=${PORTKEY_VK_GROQ}

# Default Virtual Key
VK_DEFAULT=${PORTKEY_VK_OPENAI}

# ============================================================================
# Authentication Methods
# ============================================================================

# Model-specific auth methods
AUTH_GPT5=chatgpt       # Use Codex CLI with ChatGPT login
AUTH_CLAUDE=portkey     # Use Portkey virtual key
AUTH_GPT4=portkey       # Use Portkey virtual key
AUTH_DEFAULT=portkey    # Default to Portkey

# ============================================================================
# Direct API Keys (Fallback Only)
# ============================================================================

# These are only used when Portkey is unavailable
OPENAI_API_KEY_DIRECT=${OPENAI_API_KEY}
ANTHROPIC_API_KEY_DIRECT=${ANTHROPIC_API_KEY:-}

EOF

    # Create consolidated services configuration
    cat > "$CONFIG_DIR/services.conf" <<EOF
# PayReady AI Services Configuration
# Generated: $(date)

# ============================================================================
# Web Search APIs
# ============================================================================

PERPLEXITY_API_KEY=${PERPLEXITY_API_KEY}
BRAVE_API_KEY=${BRAVE_API_KEY}
EXA_API_KEY=${EXA_API_KEY:-}
ZENROWS_API_KEY=${ZENROWS_API_KEY:-}
APIFY_API_TOKEN=${APIFY_API_TOKEN:-}

# ============================================================================
# Infrastructure Services
# ============================================================================

# Vector Storage & RAG
MILVUS_URI=${MILVUS_URI:-}
MILVUS_API_KEY=${MILVUS_API_KEY:-}
WEAVIATE_URL=${WEAVIATE_URL:-}
WEAVIATE_API_KEY=${WEAVIATE_API_KEY:-}

# Memory Services
MEM0_API_KEY=${MEM0_API_KEY:-}
LANGCHAIN_API_KEY=${LANGCHAIN_API_KEY:-}

# Monitoring
AGENTOPS_API_KEY=${AGENTOPS_API_KEY:-}
LANGSMITH_API_KEY=${LANGSMITH_API_KEY:-}

# ============================================================================
# Development Services
# ============================================================================

GITHUB_TOKEN=${GITHUB_TOKEN:-}
GITHUB_USERNAME=${GITHUB_USERNAME:-}
NEON_API_KEY=${NEON_API_KEY:-}
REDIS_URL=${REDIS_URL:-}

EOF

    log "Environment consolidation complete ✓"
}

# ============================================================================
# Install Unified CLI
# ============================================================================

install_unified_cli() {
    log "Installing unified CLI..."

    # Make scripts executable
    chmod +x "$PAYREADY_HOME/bin/ai-unified"

    # Create convenience symlinks
    ln -sf "$PAYREADY_HOME/bin/ai-unified" "$PAYREADY_HOME/bin/ai-new"

    # Create wrapper for backward compatibility
    cat > "$PAYREADY_HOME/bin/ai-compat" <<'EOF'
#!/usr/bin/env bash
# Compatibility wrapper for old commands

case "$1" in
    codex*)
        shift
        exec ai-unified --model gpt4o "$@"
        ;;
    claude*)
        shift
        exec ai-unified --model opus "$@"
        ;;
    gpt5*)
        shift
        exec ai-unified --model gpt5 "$@"
        ;;
    *)
        exec ai-unified "$@"
        ;;
esac
EOF
    chmod +x "$PAYREADY_HOME/bin/ai-compat"

    log "Unified CLI installed ✓"
}

# ============================================================================
# Setup Portkey Virtual Keys
# ============================================================================

setup_portkey() {
    log "Verifying Portkey configuration..."

    # Test Portkey connection
    if curl -s -I https://api.portkey.ai/v1/models \
        -H "x-portkey-api-key: ${PORTKEY_API_KEY}" | grep -q "200"; then
        log "Portkey connection verified ✓"
    else
        warn "Portkey connection failed - check your API key"
    fi

    # Create virtual key test script
    cat > "$PAYREADY_HOME/bin/test-vkeys.sh" <<'EOF'
#!/usr/bin/env bash
# Test all virtual keys

source ~/.config/payready/auth.conf

echo "Testing Virtual Keys..."

for vk_var in $(env | grep ^VK_ | cut -d= -f1); do
    vk_value="${!vk_var}"
    echo -n "  $vk_var: "

    response=$(curl -s -X POST https://api.portkey.ai/v1/chat/completions \
        -H "x-portkey-api-key: ${PORTKEY_API_KEY}" \
        -H "Content-Type: application/json" \
        -d "{
            \"model\": \"gpt-3.5-turbo\",
            \"messages\": [{\"role\": \"user\", \"content\": \"Say OK\"}],
            \"virtual_key\": \"$vk_value\",
            \"max_tokens\": 10
        }")

    if echo "$response" | grep -q "OK\|ok\|Ok"; then
        echo "✓"
    else
        echo "✗"
    fi
done
EOF
    chmod +x "$PAYREADY_HOME/bin/test-vkeys.sh"

    log "Portkey setup complete ✓"
}

# ============================================================================
# Configure GPT-5 ChatGPT Auth
# ============================================================================

setup_gpt5_auth() {
    log "Configuring GPT-5-Codex authentication..."

    # Ensure Codex CLI is installed
    if ! command -v codex &>/dev/null; then
        warn "Codex CLI not installed"
        if confirm "Install Codex CLI now?"; then
            npm install -g @openai/codex
        fi
    fi

    # Create/update Codex config
    mkdir -p ~/.codex
    cat > ~/.codex/config.toml <<EOF
# Codex Configuration for GPT-5 Access
preferred_auth_method = "chatgpt"
model = "gpt-5-codex"
model_reasoning_effort = "high"
auto_update = true
EOF

    log "GPT-5 authentication configured ✓"
    log "Run 'codex' to complete ChatGPT login when ready"
}

# ============================================================================
# Create Aliases
# ============================================================================

create_aliases() {
    log "Creating command aliases..."

    # Detect shell
    SHELL_RC=""
    if [[ -f ~/.zshrc ]]; then
        SHELL_RC=~/.zshrc
    elif [[ -f ~/.bashrc ]]; then
        SHELL_RC=~/.bashrc
    fi

    if [[ -n "$SHELL_RC" ]]; then
        cat >> "$SHELL_RC" <<'EOF'

# PayReady AI Unified CLI Aliases
alias ai='ai-unified'
alias ai-code='ai-unified --model gpt4o'
alias ai-review='ai-unified --model opus'
alias ai-design='ai-unified --model gpt5'
alias ai-search='ai-unified --model perplexity'

# Backward compatibility
alias codex='ai-unified --model gpt4o'
alias codex5='ai-unified --model gpt5'

EOF
        log "Aliases added to $SHELL_RC ✓"
    fi
}

# ============================================================================
# Cleanup Old Files
# ============================================================================

cleanup_old() {
    log "Cleaning up deprecated files..."

    # Create deprecated directory
    mkdir -p "$PAYREADY_HOME/deprecated"

    # Move old scripts
    for script in codex-web codex-web-2025 codex-real-web; do
        if [[ -f "$PAYREADY_HOME/bin/$script" ]]; then
            mv "$PAYREADY_HOME/bin/$script" "$PAYREADY_HOME/deprecated/"
            log "  Moved $script to deprecated/"
        fi
    done

    log "Cleanup complete ✓"
}

# ============================================================================
# Run Tests
# ============================================================================

run_tests() {
    log "Running integration tests..."

    # Test unified CLI
    if "$PAYREADY_HOME/bin/ai-unified" test &>/dev/null; then
        log "  Unified CLI: ✓"
    else
        warn "  Unified CLI: ✗"
    fi

    # Test virtual keys
    if [[ -x "$PAYREADY_HOME/bin/test-vkeys.sh" ]]; then
        "$PAYREADY_HOME/bin/test-vkeys.sh"
    fi

    log "Tests complete ✓"
}

# ============================================================================
# Generate Documentation
# ============================================================================

generate_docs() {
    log "Generating documentation..."

    cat > "$PAYREADY_HOME/MIGRATION_COMPLETE.md" <<'EOF'
# PayReady AI Migration Complete

## What Changed

1. **Unified CLI**: All AI operations now go through `ai` command
2. **Simplified Auth**: Portkey for API models, ChatGPT for GPT-5
3. **Consolidated Config**: Two main files instead of 9
4. **Smart Routing**: Automatic model selection based on intent

## Quick Start

```bash
# Basic usage
ai "write a function"              # Auto-selects best model
ai "design a system"               # Uses GPT-5-Codex
ai "analyze this code"             # Uses Claude Opus 4.1

# Explicit model selection
ai --model opus "complex analysis"
ai --model gpt5 "architecture design"

# Configuration
ai config list                     # Show configuration
ai auth status                     # Check authentication
ai test                           # Test all connections
```

## Authentication

- **GPT-5-Codex**: Run `codex` once to login with ChatGPT
- **All Others**: Configured via Portkey virtual keys

## Backward Compatibility

Old commands are aliased:
- `codex` → `ai --model gpt4o`
- `codex5` → `ai --model gpt5`

## Restore Previous Setup

If needed, run: `$BACKUP_DIR/restore.sh`

## Support

See `/docs/ARCHITECTURE/UNIFIED_SYSTEM_PLAN.md` for full details.
EOF

    log "Documentation generated ✓"
}

# ============================================================================
# Main Migration Flow
# ============================================================================

main() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}     PayReady AI - Migration to Unified Architecture${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo

    # Confirmation
    if ! confirm "This will migrate your PayReady AI setup. Continue?"; then
        echo "Migration cancelled"
        exit 0
    fi

    # Run migration steps
    preflight_check
    backup_current
    consolidate_env
    install_unified_cli
    setup_portkey
    setup_gpt5_auth
    create_aliases
    cleanup_old
    run_tests
    generate_docs

    # Summary
    echo
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}                  Migration Complete! 🎉${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo
    echo "Next steps:"
    echo "  1. Run 'source ~/.zshrc' to load aliases"
    echo "  2. Run 'codex' to login with ChatGPT for GPT-5"
    echo "  3. Test with: ai 'Hello, world!'"
    echo
    echo "Backup saved to: $BACKUP_DIR"
    echo
}

# Run if not sourced
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi