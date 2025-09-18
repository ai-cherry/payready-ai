#!/bin/bash
# Cross-platform date context provider for AI CLIs
# Updated: September 18, 2025

# Function to get date N days ago (cross-platform)
get_date_ago() {
    local days=$1

    # Try GNU date (Linux)
    if date -d "$days days ago" +%Y-%m-%d 2>/dev/null; then
        return
    fi

    # Try BSD date (macOS)
    if date -v-${days}d +%Y-%m-%d 2>/dev/null; then
        return
    fi

    # Fallback: use Python if available
    if command -v python3 >/dev/null 2>&1; then
        python3 -c "from datetime import datetime, timedelta; print((datetime.now() - timedelta(days=$days)).strftime('%Y-%m-%d'))"
        return
    fi

    # Last resort: return unknown
    echo "unknown"
}

# Get git branch safely
get_git_branch() {
    if [ -d .git ] || git rev-parse --git-dir >/dev/null 2>&1; then
        git branch --show-current 2>/dev/null || echo "detached"
    else
        echo "none"
    fi
}

# Get timezone safely
get_timezone() {
    if date +%Z 2>/dev/null | grep -q "^[A-Z]"; then
        date +%Z
    else
        echo "UTC"
    fi
}

# Export environment variables
echo "export DATE_CONTEXT='$(date +%Y-%m-%d 2>/dev/null || echo "unknown")'"
echo "export TIME_CONTEXT='$(date +%H:%M:%S 2>/dev/null || echo "unknown")'"
echo "export TIMEZONE_CONTEXT='$(get_timezone)'"
echo "export UNIX_TIMESTAMP='$(date +%s 2>/dev/null || echo "0")'"
echo "export CUTOFF_DATE='$(get_date_ago 100)'"
echo "export WEEK_NUMBER='$(date +%V 2>/dev/null || echo "unknown")'"
echo "export DAY_OF_WEEK='$(date +%A 2>/dev/null || echo "unknown")'"
echo "export GIT_BRANCH='$(get_git_branch)'"

# Create comprehensive AI context block
cat <<EOF
export AI_CONTEXT='<env>
Today'"'"'s date: $(date +%Y-%m-%d 2>/dev/null || echo "unknown")
Current time: $(date +%H:%M:%S 2>/dev/null) $(get_timezone)
Timezone: $(get_timezone)
Unix timestamp: $(date +%s 2>/dev/null || echo "0")
Day of week: $(date +%A 2>/dev/null || echo "unknown")
Week number: $(date +%V 2>/dev/null || echo "unknown")
Cutoff date (100 days ago): $(get_date_ago 100)
Platform: $(uname -s 2>/dev/null || echo "unknown")
Working directory: $(pwd)
Git branch: $(get_git_branch)
User: $(whoami 2>/dev/null || echo "unknown")
</env>'
EOF

# Validation check
if [ "$(get_date_ago 100)" = "unknown" ]; then
    echo "# WARNING: Date calculation failed. Install GNU coreutils or Python 3 for full functionality" >&2
fi