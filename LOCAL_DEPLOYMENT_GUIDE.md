# PayReady AI - Local Deployment Guide

## 🚀 Quick Start

```bash
# Deploy in offline mode (no API keys needed)
./deploy_local.sh offline

# Activate the environment
source activate.sh

# Test the CLI
ai "Hello, what can you do?"
```

## 📦 What's Deployed

### Components Initialized:
- ✅ Python virtual environment (.venv)
- ✅ All dependencies installed
- ✅ Agent factory with stub responses
- ✅ Memory manager with file storage
- ✅ Session persistence
- ✅ CLI commands (ai, tekton, payready)

### Directory Structure Created:
```
~/.payready/
├── memory/        # Memory storage
└── sessions/      # Session persistence

~/payready-ai/
├── artifacts/     # Generated artifacts
├── logs/         # Application logs
└── .venv/        # Python environment
```

### Configuration:
- Mode: Offline (stub responses)
- Memory: File-based storage
- Sessions: Persistent across restarts
- API Keys: Not required (using stubs)

## 🎮 Usage

### CLI Commands

After running `source activate.sh`:

```bash
# Basic query
ai "Explain Docker containers"

# Plan a project
ai "Create a plan for building a REST API"

# Test the system
ai test

# Check configuration
ai config list
```

### Python API

```python
from core.agent_factory import get_factory

# Create agents
factory = get_factory()
planner = factory.create_planner()
coder = factory.create_coder()
reviewer = factory.create_reviewer()

# Create a team
team = factory.create_team()
```

### Tekton CLI (Diamond v5 Stages)

```bash
# Run a goal through all stages
tekton --goal "Build a todo app" --output artifacts/todo

# Note: Requires artifact stub completion for all stages
```

## 🔧 Configuration

### Switch to Development Mode

```bash
# Deploy with real API capabilities
./deploy_local.sh dev

# Configure API keys in config/env.dev
export OPENROUTER_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
```

### Enable Redis (Optional)

```bash
# Install Redis
brew install redis

# Start Redis
brew services start redis

# Redeploy
./deploy_local.sh dev
```

## 📊 System Status

Check deployment status:

```bash
# View configuration
cat ~/.config/payready/config.yaml

# Check session
cat ~/.payready/session_id.txt

# Monitor logs
tail -f logs/*.log

# Test components
python -c "
from core.agent_factory import get_factory
from core.memory_manager import get_memory_manager
from cli.config_v2 import get_settings

settings = get_settings()
factory = get_factory()
memory = get_memory_manager(settings)

print('✅ All systems operational')
"
```

## 🛠️ Troubleshooting

### Common Issues

1. **"Module not found" errors**
   ```bash
   source activate.sh
   pip install -e .
   ```

2. **CLI not working**
   ```bash
   chmod +x bin/ai
   source activate.sh
   ```

3. **Memory errors**
   ```bash
   mkdir -p ~/.payready/memory
   chmod 755 ~/.payready/memory
   ```

4. **API key warnings**
   - Normal in offline mode
   - Configure real keys for dev mode

## 🔄 Updates

Pull latest changes and redeploy:

```bash
git pull
./deploy_local.sh offline
source activate.sh
```

## 📚 Next Steps

1. **Explore the CLI**: Try different queries with `ai`
2. **Build Agents**: Create custom agents with the factory
3. **Test Memory**: Save and recall information across sessions
4. **Develop Features**: The system is ready for development

## 💡 Tips

- **Offline Mode**: Perfect for development and testing
- **Persistence**: Sessions and memory survive restarts
- **Extensible**: Add new agents and capabilities easily
- **Debug Mode**: Set `AI_DEBUG=true` for verbose output

## 📝 Files Created by Deployment

- `deploy_local.sh` - Main deployment script
- `activate.sh` - Environment activation
- `start_services.sh` - Service startup (if API server exists)
- `~/.config/payready/config.yaml` - System configuration
- `~/.payready/session_id.txt` - Current session ID

## ✅ Deployment Verification

Your deployment is successful if:
- ✅ `ai "test"` returns a response
- ✅ No import errors when creating agents
- ✅ Memory manager initializes
- ✅ Session ID is created

---
*Deployment Date: 2025-09-19*
*Mode: Offline (Stub Responses)*
*Ready for Development!*