# PayReady AI Documentation Index
**Last Updated**: September 18, 2025
**Repository**: https://github.com/ai-cherry/payready-ai
**Status**: Living Documentation

## 📚 Documentation Structure

### 1. ARCHITECTURE
Technical architecture and system design documents.

- **[CLI Unified AI Architecture](ARCHITECTURE/CLI_UNIFIED_AI_ARCHITECTURE.md)**
  - Unified CLI system integrating Claude, Codex, Agno
  - Intelligent routing and context management
  - *Status: Active*

- **[AI Coding Standards](ARCHITECTURE/AI_CODING_STANDARDS.md)**
  - Coding rules for AI-generated code
  - Prompt engineering templates
  - AI persona configurations
  - *Status: Active*

### 2. GUIDES
How-to guides and tutorials for developers and users.

- **Setup Guide** (Coming Soon)
  - Installation instructions
  - Environment configuration
  - First-time setup

- **Development Guide** (Coming Soon)
  - Contributing guidelines
  - Testing procedures
  - Debugging tips

### 3. REFERENCES
API documentation and configuration references.

- **[CLI Reference](REFERENCES/CLI_REFERENCE.md)**
  - Command documentation
  - Usage examples
  - Options and flags
  - *Status: Active*

### 4. OPERATIONS
Live operational documents (auto-updated).

- **[Current State](OPERATIONS/CURRENT_STATE.md)**
  - Real-time system status
  - Active files and changes
  - Environment information
  - *Status: Living (Auto-updated)*

- **[Audit Report](OPERATIONS/AUDIT_REPORT.md)**
  - Latest code audit results
  - Security findings
  - Performance metrics
  - *Status: Generated Weekly*

### 5. DECISIONS
Architecture Decision Records (ADRs).

- **ADR-001: Unified CLI Design** (Coming Soon)
- **ADR-002: Date Filtering Strategy** (Coming Soon)
- **ADR-003: Documentation System** (Coming Soon)

## 🔧 System Documentation

### Core Systems

| Document | Description | Location |
|----------|-------------|----------|
| [README](../README.md) | Project overview and quick start | Root |
| [Documentation System](DOCUMENTATION_SYSTEM.md) | How our docs work | docs/ |
| [Audit Action Plan](../AUDIT_ACTION_PLAN.md) | Security and quality improvements | Root |

### Configuration Files

| File | Purpose | Location |
|------|---------|----------|
| `.envrc` | direnv configuration | Root |
| `.gitignore` | Git exclusions | Root |
| `requirements.txt` | Python dependencies | Root |
| `pyproject.toml` | Project metadata | Root |

## 🌐 GitHub Integration

### Repository Information
- **URL**: https://github.com/ai-cherry/payready-ai
- **Owner**: ai-cherry
- **Name**: payready-ai
- **Visibility**: Public

### Authentication
- **SSH Key**: Configured (SHA256:xiXai+mgRQm9sElzmUDVYqtCZhU/6lam2w1nRqG5G/M)
- **PAT**: Configured in `~/.config/payready/env.github`

### Branches
- **main**: Primary development branch
- **production**: Stable releases (coming soon)
- **develop**: Feature integration (coming soon)

## 📊 Documentation Metrics

| Category | Files | Status | Coverage |
|----------|-------|--------|----------|
| Architecture | 2 | Active | 90% |
| Guides | 0 | Planned | 0% |
| References | 1 | Active | 60% |
| Operations | 2 | Living | 100% |
| Decisions | 0 | Planned | 0% |

**Total Documentation**: 5 active files

## 🔄 Update Schedule

| Document Type | Update Frequency | Method |
|---------------|------------------|--------|
| Living Docs | Real-time | Automatic |
| Architecture | As needed | Manual |
| References | With changes | Semi-auto |
| Guides | Quarterly | Manual |
| ADRs | Per decision | Manual |

## 🛠️ Documentation Tools

### Management Commands
```bash
# List all documentation
ai docs list

# Search documentation
ai docs search "term"

# Update live docs
ai docs update

# Validate consistency
ai docs validate

# Generate changelog
ai docs changelog
```

### Quick Access
```bash
# View specific document
ai docs show CLI_REFERENCE

# Open documentation index
ai docs show INDEX

# View current system state
ai docs show CURRENT_STATE
```

## 📝 Contributing to Documentation

### Adding New Documents
1. Choose appropriate category (ARCHITECTURE, GUIDES, etc.)
2. Use provided templates
3. Update this INDEX.md
4. Run validation: `ai docs validate`

### Document Standards
- **Format**: Markdown (.md)
- **Headers**: Include metadata (Version, Status, Author, Date)
- **Structure**: Clear sections with proper hierarchy
- **Links**: Relative paths within docs/
- **Code**: Syntax highlighted with language tags

### Review Process
1. Create documentation in appropriate category
2. Update INDEX.md
3. Run `ai docs validate`
4. Commit with descriptive message
5. Create PR for review

## 🔍 Search Documentation

```bash
# Search all docs for a term
ai docs search "router"

# Search specific category
ai docs search "architecture" --category ARCHITECTURE

# Find documents by status
ai docs list --status active
```

## 📈 Improvement Tracking

### Documentation Gaps
- [ ] Setup Guide needed
- [ ] Development Guide needed
- [ ] Deployment Guide needed
- [ ] API Reference expansion
- [ ] ADRs for key decisions

### Enhancement Ideas
- [ ] Add diagrams to architecture docs
- [ ] Create video tutorials
- [ ] Add interactive examples
- [ ] Implement doc versioning
- [ ] Add search indexing

## 🆘 Help & Support

- **Documentation Issues**: Create issue at [GitHub Issues](https://github.com/ai-cherry/payready-ai/issues)
- **Quick Help**: Run `ai help` or `ai docs help`
- **Contact**: Via GitHub repository

---

*This index is the central navigation point for all PayReady AI documentation. Keep it updated as new documents are added.*