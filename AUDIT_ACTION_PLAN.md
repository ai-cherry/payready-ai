# PayReady AI Audit Action Plan
**Created**: September 18, 2025
**Priority**: Immediate action required for HIGH priority items

## 🔴 CRITICAL - Fix Immediately (Security & Stability)

### 1. Remove Hardcoded API Keys (HIGH RISK)
**Files affected**: web-router.py, weaviate_index.py, sophia.py, apollo.py

**Action Steps**:
```bash
# Move all API keys to environment files
# Check these files and replace hardcoded keys with:
os.environ.get('API_KEY_NAME')
```

**Commands to fix**:
```bash
# Search for hardcoded keys
grep -r "API_KEY.*=" services/ --include="*.py"
grep -r "sk-" services/ --include="*.py"
```

### 2. Fix Bare Except Clauses
**Files affected**: api.py, simple_index.py, basic_index.py, main.py

**Action**: Replace all bare `except:` with specific exceptions
```python
# BAD
try:
    something()
except:
    pass

# GOOD
try:
    something()
except (ValueError, TypeError) as e:
    logger.error(f"Error: {e}")
```

### 3. Add Error Handling to Main Functions
**Files affected**: web-router.py, index.py

**Action**: Wrap main() functions with try/except
```python
def main():
    try:
        # existing code
    except KeyboardInterrupt:
        print("\nShutdown requested")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
```

## 🟡 IMPORTANT - Fix This Week

### 4. Create Missing Project Files
```bash
# Create README.md
cat > README.md << 'EOF'
# PayReady AI

Unified AI development environment integrating Claude, Codex (GPT-5), and Agno agents.

## Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
direnv allow

# Run unified CLI
./bin/ai "your query"
```

## Features
- Natural language interface to AI tools
- Intelligent routing with confidence scoring
- Web search with 2025-only filtering
- Living documentation system
- Context-aware development

## Documentation
See `docs/` for comprehensive documentation.
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# Project specific
*.log
/tmp/
.DS_Store

# Secrets - NEVER commit
env.*
*.key
*.pem
EOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
# Core dependencies
redis>=4.5.0
requests>=2.31.0
python-dotenv>=1.0.0
pathlib>=1.0.1
pygments>=2.15.0

# AI/ML
openai>=1.0.0
anthropic>=0.25.0

# Web
httpx>=0.24.0
beautifulsoup4>=4.12.0

# Development
pytest>=7.4.0
black>=23.0.0
pylint>=2.17.0
EOF
```

### 5. Add Timeouts to External Calls
**Fix subprocess calls**:
```python
# In context_manager.py and others
result = subprocess.run(
    cmd,
    timeout=30,  # Add this
    capture_output=True
)
```

### 6. Improve Bash Scripts
```bash
# Add to all bash scripts after shebang
set -euo pipefail  # Exit on error, undefined vars, pipe failures
```

## 🟢 NICE TO HAVE - Next Sprint

### 7. Code Quality Improvements
```bash
# Install and configure formatters
pip install black isort pylint

# Format all Python files
black services/ bin/*.py
isort services/ bin/*.py

# Add pre-commit hook
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/psf/black
    rev: 23.0.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
EOF
```

### 8. Documentation Expansion
- Add API documentation
- Create setup guide
- Write deployment instructions
- Document troubleshooting steps

### 9. Performance Optimizations
- Review loops in ai-router.py and web-router.py
- Consider async for I/O operations
- Implement caching where appropriate

## 📋 Implementation Priority Order

1. **TODAY**: Fix security issues (API keys, error handling)
2. **TOMORROW**: Create missing files (README, .gitignore, requirements.txt)
3. **THIS WEEK**: Add timeouts, fix bash scripts
4. **NEXT WEEK**: Code quality, documentation, testing

## 🚀 Quick Fix Commands

```bash
# 1. Create all missing files at once
./bin/ai "create README.md, .gitignore, and requirements.txt files"

# 2. Fix all Python security issues
find services -name "*.py" -exec grep -l "except:" {} \; | xargs -I {} echo "Fix: {}"

# 3. Add error handling to bash scripts
for script in bin/*; do
  if [[ -f "$script" ]] && head -1 "$script" | grep -q "^#!/"; then
    if ! grep -q "set -e" "$script"; then
      echo "Add 'set -euo pipefail' to: $script"
    fi
  fi
done

# 4. Run the audit again to verify fixes
./bin/ai-audit
```

## ✅ Success Metrics

After implementing these fixes:
- [ ] Zero hardcoded API keys
- [ ] Zero bare except clauses
- [ ] All main() functions have error handling
- [ ] All external calls have timeouts
- [ ] README.md exists and is comprehensive
- [ ] .gitignore protects sensitive files
- [ ] requirements.txt lists all dependencies
- [ ] All bash scripts use `set -e`
- [ ] Documentation covers all major features

## 🔄 Continuous Improvement

Schedule weekly audits:
```bash
# Add to crontab or CI/CD
0 9 * * MON /Users/lynnmusil/payready-ai/bin/ai-audit
```

---
*Review this plan weekly and update based on progress and new findings.*