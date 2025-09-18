# PayReady AI Scaling & Growth Architecture
**Version**: 1.0.0
**Last Updated**: 2025-09-18
**Repository**: https://github.com/ai-cherry/payready-ai
**Status**: Active

## Overview
This document outlines the architectural patterns, scaffolding, and structural improvements designed to support the growth and scaling of PayReady AI's unified CLI system.

## 1. Project Structure for Scale

### 1.1 Current Structure
```
payready-ai/
├── bin/                 # CLI executables
├── services/            # Core services
├── docs/                # Documentation
├── gateway/             # API gateway
├── orchestrator/        # Workflow orchestration
└── local_rag/           # Local knowledge base
```

### 1.2 Proposed Scalable Structure
```
payready-ai/
├── apps/                      # Application layer
│   ├── cli/                  # CLI application
│   │   ├── commands/          # Command implementations
│   │   ├── routers/           # Routing logic
│   │   └── personas/          # AI personas
│   ├── api/                  # REST API application
│   │   ├── endpoints/         # API endpoints
│   │   ├── middleware/        # API middleware
│   │   └── schemas/           # Request/response schemas
│   └── web/                  # Web interface (future)
│       ├── frontend/          # React/Vue frontend
│       └── backend/           # Web backend
├── core/                      # Core business logic
│   ├── agents/                # AI agent implementations
│   │   ├── claude/
│   │   ├── codex/
│   │   ├── web/
│   │   └── agno/
│   ├── routing/               # Intelligent routing
│   ├── context/               # Context management
│   └── prompts/               # Prompt templates
├── infrastructure/            # Infrastructure code
│   ├── docker/                # Container definitions
│   ├── kubernetes/            # K8s manifests
│   ├── terraform/             # IaC definitions
│   └── monitoring/            # Observability configs
├── shared/                    # Shared libraries
│   ├── utils/                 # Utility functions
│   ├── constants/             # Constants and configs
│   ├── models/                # Data models
│   └── exceptions/            # Custom exceptions
├── plugins/                   # Plugin system
│   ├── official/              # Official plugins
│   └── community/             # Community plugins
├── tests/                     # Test suites
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   ├── e2e/                   # End-to-end tests
│   └── performance/           # Performance tests
└── scripts/                   # Build and deploy scripts
    ├── build/
    ├── deploy/
    └── migrate/
```

## 2. Modular Component Architecture

### 2.1 Plugin System

```python
# plugins/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class AIPlugin(ABC):
    """Base class for AI plugins"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version"""
        pass

    @abstractmethod
    async def execute(self, query: str, context: Dict[str, Any]) -> str:
        """Execute plugin logic"""
        pass

    @abstractmethod
    def can_handle(self, query: str) -> float:
        """Return confidence score (0-1) for handling query"""
        pass

    def get_fallback(self) -> Optional['AIPlugin']:
        """Return fallback plugin if this fails"""
        return None
```

### 2.2 Agent Registry

```python
# core/agents/registry.py
from typing import Dict, Type, Optional
import importlib
import pkgutil

class AgentRegistry:
    """Dynamic agent registration and discovery"""

    def __init__(self):
        self._agents: Dict[str, Type[AIAgent]] = {}
        self._instances: Dict[str, AIAgent] = {}

    def register(self, name: str, agent_class: Type[AIAgent]):
        """Register an agent"""
        self._agents[name] = agent_class

    def get(self, name: str) -> Optional[AIAgent]:
        """Get or create agent instance"""
        if name not in self._instances and name in self._agents:
            self._instances[name] = self._agents[name]()
        return self._instances.get(name)

    def discover_agents(self, package):
        """Auto-discover and register agents from package"""
        for importer, modname, ispkg in pkgutil.iter_modules(package.__path__):
            module = importlib.import_module(f"{package.__name__}.{modname}")
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, AIAgent):
                    self.register(attr.name, attr)

# Global registry
agent_registry = AgentRegistry()
```

## 3. Configuration Management

### 3.1 Hierarchical Configuration

```yaml
# config/base.yaml
app:
  name: PayReady AI
  version: 2.0.0

routing:
  default_timeout: 30
  max_retries: 3
  confidence_threshold: 0.6

agents:
  claude:
    enabled: true
    fallback: codex
  codex:
    enabled: true
    models:
      - gpt-5-mini
      - gpt-5
  web:
    enabled: true
    date_filter: 100  # days
  agno:
    enabled: false  # Disabled by default

# config/development.yaml
extends: base.yaml
app:
  debug: true
  log_level: DEBUG

# config/production.yaml
extends: base.yaml
app:
  debug: false
  log_level: INFO
monitoring:
  enabled: true
  metrics_port: 9090
```

### 3.2 Dynamic Configuration

```python
# shared/config.py
from typing import Any, Dict
import yaml
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ConfigManager:
    """Dynamic configuration management with hot reload"""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self._config: Dict[str, Any] = {}
        self._observers = []
        self.load_config()
        self.watch_changes()

    def load_config(self):
        """Load configuration from YAML files"""
        env = os.getenv("PAYREADY_ENV", "development")
        base_config = self._load_yaml("base.yaml")
        env_config = self._load_yaml(f"{env}.yaml")
        self._config = self._merge_configs(base_config, env_config)

    def _load_yaml(self, filename: str) -> Dict:
        path = os.path.join(self.config_dir, filename)
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value by dot notation"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def reload(self):
        """Reload configuration"""
        self.load_config()
        self._notify_observers()

config = ConfigManager()
```

## 4. Service Mesh Architecture

### 4.1 Microservices Design

```python
# infrastructure/services.py
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ServiceDefinition:
    name: str
    host: str
    port: int
    health_check: str
    dependencies: List[str]
    replicas: int = 1
    load_balancer: str = "round_robin"

SERVICES = {
    "router": ServiceDefinition(
        name="router",
        host="router-service",
        port=8000,
        health_check="/health",
        dependencies=["claude", "codex", "web"],
        replicas=3
    ),
    "claude": ServiceDefinition(
        name="claude",
        host="claude-service",
        port=8001,
        health_check="/health",
        dependencies=["context_manager"],
        replicas=2
    ),
    "codex": ServiceDefinition(
        name="codex",
        host="codex-service",
        port=8002,
        health_check="/health",
        dependencies=["context_manager"],
        replicas=2
    ),
    "context_manager": ServiceDefinition(
        name="context_manager",
        host="context-service",
        port=8003,
        health_check="/health",
        dependencies=["redis"],
        replicas=1
    ),
}
```

### 4.2 Service Discovery

```python
# infrastructure/discovery.py
import consul
from typing import Optional, List

class ServiceDiscovery:
    """Service discovery using Consul"""

    def __init__(self, consul_host: str = "localhost", consul_port: int = 8500):
        self.consul = consul.Consul(host=consul_host, port=consul_port)

    def register_service(self, service: ServiceDefinition):
        """Register service with Consul"""
        self.consul.agent.service.register(
            name=service.name,
            service_id=f"{service.name}-{os.getpid()}",
            address=service.host,
            port=service.port,
            check=consul.Check.http(
                f"http://{service.host}:{service.port}{service.health_check}",
                interval="10s"
            )
        )

    def discover_service(self, name: str) -> Optional[str]:
        """Discover service endpoint"""
        _, services = self.consul.health.service(name, passing=True)
        if services:
            service = services[0]
            address = service['Service']['Address']
            port = service['Service']['Port']
            return f"http://{address}:{port}"
        return None
```

## 5. Observability & Monitoring

### 5.1 Metrics Collection

```python
# infrastructure/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time
from functools import wraps

# Metrics
request_count = Counter('ai_requests_total', 'Total AI requests', ['tool', 'status'])
request_duration = Histogram('ai_request_duration_seconds', 'Request duration', ['tool'])
active_requests = Gauge('ai_active_requests', 'Active requests', ['tool'])
cache_hits = Counter('ai_cache_hits_total', 'Cache hits', ['cache_type'])
error_count = Counter('ai_errors_total', 'Total errors', ['tool', 'error_type'])

def track_metrics(tool: str):
    """Decorator to track metrics"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            active_requests.labels(tool=tool).inc()
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                request_count.labels(tool=tool, status='success').inc()
                return result
            except Exception as e:
                request_count.labels(tool=tool, status='error').inc()
                error_count.labels(tool=tool, error_type=type(e).__name__).inc()
                raise
            finally:
                duration = time.time() - start_time
                request_duration.labels(tool=tool).observe(duration)
                active_requests.labels(tool=tool).dec()

        return wrapper
    return decorator
```

### 5.2 Distributed Tracing

```python
# infrastructure/monitoring/tracing.py
from opentelemetry import trace
from opentelemetry.exporter.jaeger import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Setup tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Configure Jaeger exporter
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

def trace_operation(name: str):
    """Decorator for tracing operations"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(name) as span:
                span.set_attribute("function", func.__name__)
                try:
                    result = await func(*args, **kwargs)
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
        return wrapper
    return decorator
```

## 6. Caching Strategy

### 6.1 Multi-Level Cache

```python
# core/caching/cache.py
from typing import Optional, Any
import hashlib
import json
import redis
from functools import lru_cache

class MultiLevelCache:
    """Multi-level caching system"""

    def __init__(self):
        self.memory_cache = {}  # L1: In-memory
        self.redis_client = redis.Redis()  # L2: Redis
        self.disk_cache_dir = "/tmp/payready_cache"  # L3: Disk

    def _generate_key(self, query: str, context: dict) -> str:
        """Generate cache key"""
        data = json.dumps({"query": query, "context": context}, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()

    async def get(self, query: str, context: dict) -> Optional[Any]:
        """Get from cache (checks all levels)"""
        key = self._generate_key(query, context)

        # L1: Memory
        if key in self.memory_cache:
            return self.memory_cache[key]

        # L2: Redis
        value = self.redis_client.get(key)
        if value:
            self.memory_cache[key] = value
            return json.loads(value)

        # L3: Disk
        disk_path = f"{self.disk_cache_dir}/{key}"
        if os.path.exists(disk_path):
            with open(disk_path, 'r') as f:
                value = json.load(f)
                self.memory_cache[key] = value
                self.redis_client.setex(key, 3600, json.dumps(value))
                return value

        return None

    async def set(self, query: str, context: dict, value: Any, ttl: int = 3600):
        """Set in cache (all levels)"""
        key = self._generate_key(query, context)

        # L1: Memory
        self.memory_cache[key] = value

        # L2: Redis
        self.redis_client.setex(key, ttl, json.dumps(value))

        # L3: Disk (for longer persistence)
        disk_path = f"{self.disk_cache_dir}/{key}"
        with open(disk_path, 'w') as f:
            json.dump(value, f)
```

## 7. Testing Framework

### 7.1 Test Structure

```python
# tests/conftest.py
import pytest
from unittest.mock import Mock, AsyncMock
from core.agents import AgentRegistry
from core.context import ContextManager

@pytest.fixture
def mock_agent_registry():
    """Mock agent registry for testing"""
    registry = AgentRegistry()
    registry.register("test_agent", Mock())
    return registry

@pytest.fixture
def mock_context():
    """Mock context for testing"""
    return {
        "date": "2025-09-18",
        "project_root": "/test/project",
        "git_status": {"branch": "main", "clean": True}
    }

@pytest.fixture
async def async_client():
    """Async test client"""
    from apps.api import create_app
    app = create_app(test_mode=True)
    async with app.test_client() as client:
        yield client
```

### 7.2 Performance Testing

```python
# tests/performance/test_routing.py
import asyncio
import time
from statistics import mean, stdev

async def test_routing_performance(mock_agent_registry):
    """Test routing performance under load"""
    router = Router(mock_agent_registry)
    queries = ["test query"] * 1000

    start = time.time()
    results = await asyncio.gather(*[
        router.route(query) for query in queries
    ])
    duration = time.time() - start

    assert duration < 10  # Should handle 1000 queries in < 10s
    assert len(results) == 1000
    print(f"Throughput: {1000/duration:.2f} queries/sec")
```

## 8. Deployment Patterns

### 8.1 Blue-Green Deployment

```yaml
# kubernetes/deployment-blue-green.yaml
apiVersion: v1
kind: Service
metadata:
  name: payready-ai
spec:
  selector:
    app: payready-ai
    version: ${ACTIVE_VERSION}  # blue or green
  ports:
    - port: 80
      targetPort: 8000

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payready-ai-blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: payready-ai
      version: blue
  template:
    metadata:
      labels:
        app: payready-ai
        version: blue
    spec:
      containers:
      - name: app
        image: payready-ai:blue
        ports:
        - containerPort: 8000

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payready-ai-green
spec:
  replicas: 0  # Scale up during deployment
  selector:
    matchLabels:
      app: payready-ai
      version: green
  template:
    metadata:
      labels:
        app: payready-ai
        version: green
    spec:
      containers:
      - name: app
        image: payready-ai:green
        ports:
        - containerPort: 8000
```

### 8.2 Canary Deployment

```python
# infrastructure/canary.py
import random
from typing import Callable

class CanaryDeployment:
    """Canary deployment controller"""

    def __init__(self, stable_version: str, canary_version: str, canary_percent: int = 10):
        self.stable_version = stable_version
        self.canary_version = canary_version
        self.canary_percent = canary_percent

    def route_request(self, request_handler_stable: Callable, request_handler_canary: Callable):
        """Route request based on canary percentage"""
        if random.randint(1, 100) <= self.canary_percent:
            return request_handler_canary()
        return request_handler_stable()

    def adjust_traffic(self, new_percent: int):
        """Adjust canary traffic percentage"""
        self.canary_percent = min(100, max(0, new_percent))

    def promote_canary(self):
        """Promote canary to stable"""
        self.stable_version = self.canary_version
        self.canary_percent = 0
```

## 9. Security Architecture

### 9.1 API Key Management

```python
# core/security/keys.py
from cryptography.fernet import Fernet
import os
import json

class SecureKeyManager:
    """Secure API key management"""

    def __init__(self):
        self.key = os.getenv("ENCRYPTION_KEY") or Fernet.generate_key()
        self.cipher = Fernet(self.key)
        self.key_store_path = os.path.expanduser("~/.config/payready/keys.enc")

    def store_key(self, service: str, api_key: str):
        """Store encrypted API key"""
        keys = self._load_keys()
        keys[service] = self.cipher.encrypt(api_key.encode()).decode()
        self._save_keys(keys)

    def get_key(self, service: str) -> Optional[str]:
        """Retrieve and decrypt API key"""
        keys = self._load_keys()
        if service in keys:
            encrypted = keys[service].encode()
            return self.cipher.decrypt(encrypted).decode()
        return None

    def rotate_keys(self):
        """Rotate encryption keys"""
        old_cipher = self.cipher
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)

        # Re-encrypt all keys
        keys = self._load_keys()
        for service, encrypted_key in keys.items():
            decrypted = old_cipher.decrypt(encrypted_key.encode())
            keys[service] = self.cipher.encrypt(decrypted).decode()
        self._save_keys(keys)
```

## 10. Development Workflow

### 10.1 Git Hooks

```bash
# .githooks/pre-commit
#!/bin/bash
set -e

echo "Running pre-commit checks..."

# Format Python code
black apps/ core/ shared/ tests/

# Sort imports
isort apps/ core/ shared/ tests/

# Run linting
pylint apps/ core/ shared/

# Run type checking
mypy apps/ core/ shared/

# Run tests
pytest tests/unit/ -v

# Update documentation
python scripts/update_docs.py

echo "Pre-commit checks passed!"
```

### 10.2 CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Run tests
      run: |
        pytest tests/ --cov=apps --cov=core --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Build Docker image
      run: |
        docker build -t payready-ai:${{ github.sha }} .
        docker tag payready-ai:${{ github.sha }} payready-ai:latest

    - name: Push to registry
      if: github.ref == 'refs/heads/main'
      run: |
        docker push payready-ai:${{ github.sha }}
        docker push payready-ai:latest

  deploy:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/payready-ai app=payready-ai:${{ github.sha }}
        kubectl rollout status deployment/payready-ai
```

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [ ] Restructure project directories
- [ ] Implement plugin system
- [ ] Set up configuration management
- [ ] Create test framework

### Phase 2: Services (Weeks 3-4)
- [ ] Refactor into microservices
- [ ] Implement service discovery
- [ ] Add health checks
- [ ] Set up load balancing

### Phase 3: Observability (Weeks 5-6)
- [ ] Add metrics collection
- [ ] Implement distributed tracing
- [ ] Set up logging aggregation
- [ ] Create dashboards

### Phase 4: Deployment (Weeks 7-8)
- [ ] Containerize services
- [ ] Create Kubernetes manifests
- [ ] Set up CI/CD pipeline
- [ ] Implement blue-green deployment

### Phase 5: Optimization (Weeks 9-10)
- [ ] Add multi-level caching
- [ ] Optimize routing algorithms
- [ ] Implement rate limiting
- [ ] Performance tuning

---

*This scaling architecture provides the foundation for growing PayReady AI from a CLI tool to an enterprise-ready platform.*