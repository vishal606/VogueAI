.PHONY: help install dev test lint migrate docker-up docker-down clean seed

# ── Default ───────────────────────────────────────────────────
help:
	@echo ""
	@echo "Fashion Trend AI — Dev Commands"
	@echo "================================"
	@echo "  make install         Install Python dependencies"
	@echo "  make dev             Start API server with hot-reload"
	@echo "  make worker          Start Celery worker"
	@echo "  make beat            Start Celery beat scheduler"
	@echo "  make flower          Start Flower monitoring UI"
	@echo "  make test            Run all tests"
	@echo "  make test-cov        Run tests with coverage report"
	@echo "  make lint            Run ruff linter"
	@echo "  make format          Auto-format with black + isort"
	@echo "  make migrate         Run Alembic migrations"
	@echo "  make migrate-new     Create new migration"
	@echo "  make docker-up       Start all Docker services"
	@echo "  make docker-down     Stop all Docker services"
	@echo "  make seed            Seed subscription plans"
	@echo "  make clean           Remove cache and temp files"
	@echo ""

# ── Install ───────────────────────────────────────────────────
install:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install pytest pytest-asyncio httpx aiosqlite ruff black isort

# ── Dev Server ────────────────────────────────────────────────
dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug

# ── Celery ────────────────────────────────────────────────────
worker:
	celery -A app.workers.scheduler.celery_app worker --loglevel=info --concurrency=4

beat:
	celery -A app.workers.scheduler.celery_app beat --loglevel=info

flower:
	celery -A app.workers.scheduler.celery_app flower --port=5555

# ── Tests ─────────────────────────────────────────────────────
test:
	pytest tests/ -v --tb=short

test-cov:
	pytest tests/ --cov=app --cov-report=html --cov-report=term-missing -v

test-fast:
	pytest tests/ -v --tb=short -m "not slow and not integration"

# ── Linting / Formatting ──────────────────────────────────────
lint:
	ruff check app/ tests/

format:
	black app/ tests/
	isort app/ tests/

# ── Database ──────────────────────────────────────────────────
migrate:
	alembic upgrade head

migrate-new:
	@read -p "Migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

migrate-down:
	alembic downgrade -1

migrate-history:
	alembic history --verbose

# ── Docker ────────────────────────────────────────────────────
docker-up:
	docker-compose up -d
	@echo "Services started:"
	@echo "  API:      http://localhost:8000"
	@echo "  Docs:     http://localhost:8000/docs"
	@echo "  Flower:   http://localhost:5555"
	@echo "  PgAdmin:  postgresql://localhost:5432"

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f api

docker-rebuild:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

# ── Seed ─────────────────────────────────────────────────────
seed:
	python -c "import asyncio; from app.main import _seed_subscription_plans; asyncio.run(_seed_subscription_plans())"

# ── Scraper ───────────────────────────────────────────────────
scrape:
	python -c "import asyncio; from app.workers.scraper import run_scraper_job; print(asyncio.run(run_scraper_job()))"

# ── Clean ─────────────────────────────────────────────────────
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name ".coverage" -delete 2>/dev/null || true
	@echo "Cleaned up cache files"
