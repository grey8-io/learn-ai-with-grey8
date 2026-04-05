SHELL := /bin/bash

.PHONY: help \
        dev dev-local dev-web dev-tutor dev-ollama \
        setup setup-ollama setup-hooks \
        test test-tutor test-web test-ace \
        lint \
        ace-generate ace-curate ace-reflect \
        clean \
        docker-up docker-down \
        docs

.DEFAULT_GOAL := help

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------

help: ## Show this help message
	@echo "learn-ai-with-grey8 — available targets:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ---------------------------------------------------------------------------
# Development
# ---------------------------------------------------------------------------

dev: ## Start all services via Docker Compose
	docker compose -f docker/docker-compose.yml up

dev-local: dev-ollama ## Start all services locally (no Docker)
	@echo "Starting tutor and web in background..."
	cd tutor && uvicorn tutor.main:app --reload --host 0.0.0.0 --port 8000 &
	cd platform/web && npm run dev &
	@wait

dev-web: ## Start Next.js frontend only
	cd platform/web && npm run dev

dev-tutor: ## Start FastAPI tutor engine only
	cd tutor && uvicorn tutor.main:app --reload --host 0.0.0.0 --port 8000

dev-ollama: ## Start Ollama serve
	ollama serve

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

setup: setup-ollama setup-hooks ## Full initial setup: deps, model pull, hooks
	cd tutor && pip install -e ".[dev]"
	cd ace && pip install -e ".[dev]"
	cd platform/web && npm install
	@echo ""
	@echo "Setup complete. Run 'make dev' (Docker) or 'make dev-local' (no Docker) to start."

setup-ollama: ## Pull Ollama model and verify
	bash local-dev/scripts/setup-ollama.sh

setup-hooks: ## Install git hooks for auto-syncing curriculum context
	bash scripts/setup-hooks.sh

# ---------------------------------------------------------------------------
# Testing
# ---------------------------------------------------------------------------

test: test-tutor test-web test-ace ## Run all tests

test-tutor: ## Run tutor engine tests (pytest)
	cd tutor && pytest

test-web: ## Run web platform tests (jest)
	cd platform/web && npm test

test-ace: ## Run ACE framework tests (pytest)
	cd ace && pytest

# ---------------------------------------------------------------------------
# Linting
# ---------------------------------------------------------------------------

lint: ## Run all linters
	cd tutor && ruff check .
	cd ace && ruff check .
	cd platform/web && npm run lint

# ---------------------------------------------------------------------------
# ACE Framework CLI
# ---------------------------------------------------------------------------

ace-generate: ## Run ACE generate pipeline
	cd ace && python -m ace.cli generate

ace-curate: ## Run ACE curate pipeline
	cd ace && python -m ace.cli curate

ace-reflect: ## Run ACE reflect pipeline
	cd ace && python -m ace.cli reflect

# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

clean: ## Remove generated files and caches
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".turbo" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "coverage" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "Cleaned."

# ---------------------------------------------------------------------------
# Documentation
# ---------------------------------------------------------------------------

docs: ## Serve documentation locally at http://localhost:4000
	@echo "Serving docs at http://localhost:4000 ..."
	@npx --yes docsify-cli serve docs --port 4000

# ---------------------------------------------------------------------------
# Docker
# ---------------------------------------------------------------------------

docker-up: ## Start Docker Compose stack (detached)
	docker compose -f docker/docker-compose.yml up -d

docker-down: ## Stop Docker Compose stack
	docker compose -f docker/docker-compose.yml down
