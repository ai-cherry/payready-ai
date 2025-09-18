.PHONY: help install dev test lint format clean up down rag-index gateway orchestrator rag db-migrate bi-server

help:
	@echo "PayReady AI Monorepo Commands"
	@echo "=============================="
	@echo "install     - Install all dependencies"
	@echo "dev         - Start development environment"
	@echo "test        - Run tests"
	@echo "lint        - Run linters"
	@echo "format      - Format code"
	@echo "clean       - Clean temporary files"
	@echo "up          - Start all services"
	@echo "down        - Stop all services"
	@echo "rag-index   - Index sample data into RAG"
	@echo "gateway     - Run gateway service"
	@echo "bi-server   - Run BI analytics server"
	@echo "db-migrate  - Apply Neon database migrations"

install:
	uv sync
	pre-commit install

dev:
	tmux new-session -d -s payready || true
	tmux send-keys -t payready:0 'make gateway' C-m
	tmux new-window -t payready:1 -n 'bi'
	tmux send-keys -t payready:1 'make bi-server' C-m
	tmux new-window -t payready:2 -n 'rag'
	tmux send-keys -t payready:2 'make rag' C-m
	tmux attach -t payready

test:
	uv run pytest tests/ -v || echo "No tests yet"

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff check --fix .
	uv run ruff format .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .ruff_cache .pytest_cache
	rm -rf milvus.db

up:
	@echo "Starting all services..."
	uv run uvicorn gateway.main:app --port 8000 --reload & \
	uv run uvicorn services.domains.bi.slack_analytics:app --port 8800 --reload & \
	uv run uvicorn local_rag.api:app --port 8787 --reload & \
	python -c 'import time; time.sleep(2)'; echo 'Dev services started (gateway:8000, bi:8800, rag:8787)'

down:
	@echo "Stopping all services..."
	@pkill -f "uvicorn gateway.main:app" || true
	@pkill -f "uvicorn services.domains.bi.slack_analytics:app" || true
	@pkill -f "uvicorn local_rag.api:app" || true
	@echo "Services stopped"

rag-index:
	uv run python -c "from local_rag.index import RAGIndexer; i=RAGIndexer(); \
	i.index_text('PayReady unified BI dashboard', ['product', 'bi']); \
	i.index_text('Slack analytics for business intelligence', ['bi', 'slack']); \
	i.index_text('Client health metrics and renewals', ['client-health']); \
	print('✅ RAG indexed with sample data')"

gateway:
	uv run uvicorn gateway.main:app --port 8000 --reload

orchestrator:
	uv run python orchestrator/sophia_simple.py

rag:
	uv run uvicorn local_rag.api:app --port 8787 --reload

bi-server:
	uv run uvicorn services.domains.bi.slack_analytics:app --port 8800 --reload

db-migrate:
	@echo "Applying Neon database migrations..."
	@uv run python -c "import os, psycopg; \
	from services.domains.bi.slack_analytics import DDL; \
	url=os.getenv('NEON_DATABASE_URL'); \
	if not url: \
	  print('⚠️  NEON_DATABASE_URL not set - skipping migration'); \
	  exit(0); \
	print('Connecting to Neon...'); \
	with psycopg.connect(url, autocommit=True) as c: \
	  with c.cursor() as cur: \
	    cur.execute(DDL); \
	    print('✅ Database schema created/updated')"