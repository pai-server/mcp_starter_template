# Makefile for MCP Agents Starter with UV
.PHONY: help install dev-install sync test lint format clean run-cli run-web build info update

# Default target
help: ## Show this help message
	@echo "🛠️  MCP Agents Starter - UV Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the project dependencies
	uv sync

dev-install: ## Install development dependencies
	uv sync --dev
	uv run pre-commit install

sync: ## Synchronize environment with lockfile
	uv sync

test: ## Run tests with pytest
	uv run pytest -v

test-cov: ## Run tests with coverage
	uv run pytest --cov=src --cov-report=html --cov-report=term-missing

lint: ## Run linting (ruff, black, mypy)
	uv run ruff check src/ scripts/ tests/
	uv run black --check src/ scripts/ tests/
	uv run mypy src/

format: ## Format code with black and ruff
	uv run ruff check --fix src/ scripts/ tests/
	uv run black src/ scripts/ tests/

clean: ## Clean up cache and build artifacts
	uv cache clean
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

run-cli: ## Start the CLI application
	uv run python scripts/cli.py

run-web: ## Start the web application
	uv run streamlit run scripts/streamlit.py --server.port 8505

build: ## Build distribution packages
	uv build

info: ## Show project and environment information
	@echo "📊 Project Information"
	@echo "====================="
	@echo "UV Version: $$(uv --version)"
	@echo "Python Version: $$(uv run python --version)"
	@echo "Project: $$(uv run python -c 'import tomllib; print(tomllib.load(open(\"pyproject.toml\", \"rb\"))[\"project\"][\"name\"])')"
	@echo "Environment: $$(pwd)/.venv"
	@echo ""
	@echo "📦 Dependencies:"
	@uv tree --depth 1

update: ## Update dependencies
	uv lock --upgrade
	uv sync

dev-script: ## Run the development utility script
	uv run scripts/dev.py

# Quick development workflow
dev: dev-install format lint test ## Full development setup and checks 