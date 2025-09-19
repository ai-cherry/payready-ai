# PayReady AI - Live Development Guide

## 🚀 Quick Start for Real AI Capabilities

```bash
# 1. Setup environment and install dependencies
./scripts/setup_local.sh
source .venv/bin/activate

# 2. Configure your API keys
./bin/ai config setup
# OR set directly in environment:
export PORTKEY_API_KEY="your-portkey-key"
export OPENROUTER_API_KEY="your-openrouter-key"

# 3. Start the service stack
python services/service_stubs.py  # Starts all services on their ports

# 4. Test with real AI
./bin/ai "What can you help me with?"
./bin/ai doctor  # Run system diagnostics
```

## 📡 Service Architecture

```
User → CLI (bin/ai) → Gateway (:8000) → Orchestrator (:8001)
                                    ↓
                        ┌──────────────────────┐
                        │   Portkey/OpenRouter │
                        │   (Real AI Models)   │
                        └──────────────────────┘
                                    ↓
                        ┌──────────────────────┐
                        │   RAG Service (:8787) │
                        │   Domain APIs (:8003) │
                        └──────────────────────┘
```

## 🔑 API Configuration

### Required API Keys for Full Functionality

1. **Portkey** (Primary AI routing):
   ```bash
   export PORTKEY_API_KEY="your-key"
   export PORTKEY_VK_ANTHROPIC="anthropic-virtual-key"
   export PORTKEY_VK_OPENAI="openai-virtual-key"
   ```

2. **OpenRouter** (Fallback routing):
   ```bash
   export OPENROUTER_API_KEY="your-key"
   ```

3. **Direct Provider Keys** (Optional):
   ```bash
   export ANTHROPIC_API_KEY="your-claude-key"
   export OPENAI_API_KEY="your-openai-key"
   export XAI_API_KEY="your-grok-key"
   ```

4. **Business Intelligence** (Optional):
   ```bash
   export SLACK_BOT_TOKEN="xoxb-your-token"
   export APOLLO_API_KEY="your-apollo-key"
   ```

## 🎯 Available Models

The CLI automatically routes to the best model based on your query:

| Model | Provider | Best For |
|-------|----------|----------|
| Claude Opus 4.1 | Anthropic | Complex reasoning, analysis |
| Claude Sonnet 4 | Anthropic | Balanced performance |
| GPT-4.1 Mini | OpenAI | Cost-effective tasks |
| GPT-5 Mini | OpenAI | Advanced reasoning |
| Gemini 2.5 Flash | Google | Fast responses |
| Grok Code Fast | X.AI | Code generation |
| DeepSeek Chat v3 | DeepSeek | Technical queries |
| Llama 4 | Meta | Open-source alternative |

## 🛠️ Development Modes

### 1. **Full Live Mode** (All services, real APIs)
```bash
# Start all services
./scripts/start_services.sh

# Or individually:
uvicorn gateway.main:app --port 8000 --reload &
uvicorn orchestrator.sophia:app --port 8001 --reload &
uvicorn local_rag.api:app --port 8787 --reload &
```

### 2. **Hybrid Mode** (Some real, some stubs)
```bash
# Use stubs for services you're not developing
python services/service_stubs.py &

# Start only the service you're working on
uvicorn gateway.main:app --port 8000 --reload
```

### 3. **Gateway Bypass** (Direct CLI to AI)
```bash
export PAYREADY_BYPASS_GATEWAY=1
./bin/ai "Direct AI query without services"
```

## 📊 Memory & Persistence

### Redis (Session cache)
```bash
brew install redis
brew services start redis
export REDIS_URL="redis://localhost:6379"
```

### Milvus (Vector search)
```bash
# Install Milvus standalone
wget https://github.com/milvus-io/milvus/releases/download/v2.3.0/milvus-standalone-docker-compose.yml
docker-compose up -d
```

### PostgreSQL (BI data)
```bash
# Use Neon cloud DB or local
export DATABASE_URL="postgresql://user:pass@localhost/payready"
```

## 🔍 Testing & Validation

### System Health Check
```bash
./bin/ai doctor
```

### Service Status
```bash
curl http://localhost:8000/health  # Gateway
curl http://localhost:8001/health  # Orchestrator
curl http://localhost:8787/health  # RAG
```

### Integration Test
```bash
./bin/ai test
# Should return real AI responses, not stubs
```

### Debug Mode
```bash
export AI_DEBUG=true
./bin/ai "Show me debug info"
```

## 🚦 Service Endpoints

| Service | Port | Purpose | Health Check |
|---------|------|---------|--------------|
| Gateway | 8000 | API routing, RBAC | `/health` |
| Orchestrator | 8001 | LangGraph workflows | `/health` |
| RAG Service | 8787 | Vector search | `/health` |
| Domain Router | 8003 | Business APIs | `/health` |

## 📝 Common Workflows

### 1. Code Generation
```bash
./bin/ai "Write a Python FastAPI server with authentication"
# Routes to Grok Code Fast or GPT-5 Mini
```

### 2. Business Intelligence
```bash
./bin/ai "Analyze our Slack activity for last week"
# Routes through BI domain service
```

### 3. RAG-Enhanced Queries
```bash
./bin/ai "What does our documentation say about authentication?"
# Uses RAG service for context retrieval
```

### 4. Multi-Agent Workflow
```bash
tekton --goal "Build a todo app with tests" --output artifacts/
# Uses Diamond v5 swarm orchestration
```

## 🐛 Troubleshooting

### API Keys Not Working
```bash
# Verify configuration
./bin/ai config list

# Test specific provider
./bin/ai --model claude-opus "Test Claude"
./bin/ai --model gpt-4 "Test GPT"
```

### Services Not Starting
```bash
# Check port conflicts
lsof -i :8000
lsof -i :8001
lsof -i :8787

# Kill conflicting processes
kill -9 $(lsof -t -i:8000)
```

### Memory Issues
```bash
# Clear Redis cache
redis-cli FLUSHALL

# Reset session
rm ~/.payready/session_id.txt
```

## 🏗️ Architecture Details

### Request Flow
1. CLI parses query and detects intent
2. Gateway validates authentication
3. Orchestrator analyzes request
4. RAG retrieves relevant context
5. LLM generates response
6. Response flows back through chain

### Model Selection Logic
- Code queries → Grok/DeepSeek
- Analysis → Claude Opus
- Creative → GPT-5
- Fast queries → Gemini Flash
- Fallback → OpenRouter auto-routing

### Caching Strategy
- Redis: 15-minute session cache
- Milvus: Permanent vector embeddings
- File system: Conversation history

## 🚀 Production Deployment

For production deployment, see:
- `docs/deployment/kubernetes.yaml` - K8s manifests
- `docs/deployment/docker-compose.yaml` - Docker setup
- `docs/deployment/terraform/` - Infrastructure as code

## 📚 Additional Resources

- [Agno Documentation](https://agno.ai/docs)
- [LangGraph Guide](https://langchain.com/langgraph)
- [Portkey Configuration](https://portkey.ai/docs)
- [OpenRouter Models](https://openrouter.ai/models)

---
*This is your REAL system with actual AI capabilities - not the offline stub mode!*