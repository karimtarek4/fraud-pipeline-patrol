.PHONY: help install install-dev test test-verbose lint format security clean pre-commit setup-hooks validate-dags

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	uv pip install -e .

install-dev: ## Install development dependencies
	uv pip install -e ".[dev,ci]"

setup-hooks: ## Install pre-commit hooks
	pre-commit install

test: ## Run tests
	python run_all_tests.py

lint: ## Run linting checks
	flake8 .
	mypy .

format: ## Format code
	black .
	isort .

format-check: ## Check code formatting without making changes
	black --check .
	isort --check-only .

security: ## Run security scans
	bandit -r .
	safety check

pre-commit: ## Run pre-commit on all files
	pre-commit run --all-files

setup: install-dev setup-hooks ## Full development setup
