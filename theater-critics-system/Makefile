# Theater Critics System - Makefile
# Comprehensive automation for development, testing, and deployment

.PHONY: help install install-dev test test-unit test-integration test-api test-fast lint format type-check security clean coverage docs build quality pre-commit setup

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
PIP := pip
PROJECT_NAME := theater-critics-system
VENV_DIR := venv
TEST_DIR := tests
COVERAGE_DIR := htmlcov
DOCS_DIR := docs

# Help target
help: ## Show this help message
	@echo "Theater Critics System - Development Commands"
	@echo "============================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation targets
install: ## Install production dependencies
	$(PIP) install -r requirements.txt

install-dev: ## Install development dependencies
	$(PIP) install -r requirements-dev.txt

setup: install-dev ## Complete development environment setup
	pre-commit install
	@echo "✅ Development environment setup complete!"

# Testing targets
test: ## Run all tests with coverage
	$(PYTHON) -m pytest $(TEST_DIR)/ -v --cov=. --cov-report=html --cov-report=term-missing --tb=short

test-unit: ## Run unit tests only
	$(PYTHON) -m pytest $(TEST_DIR)/ -v -m unit --tb=short

test-integration: ## Run integration tests only
	$(PYTHON) -m pytest $(TEST_DIR)/ -v -m integration --tb=short

test-api: ## Run API tests only
	$(PYTHON) -m pytest $(TEST_DIR)/ -v -m api --tb=short

test-fast: ## Run fast tests only (exclude slow tests)
	$(PYTHON) -m pytest $(TEST_DIR)/ -v -m 'not slow' --tb=short

test-watch: ## Run tests in watch mode
	$(PYTHON) -m pytest-watch $(TEST_DIR)/ --runner="python -m pytest --tb=short"

# Code quality targets
lint: ## Run all linting checks
	@echo "🔍 Running flake8..."
	$(PYTHON) -m flake8 . --config=setup.cfg
	@echo "🔍 Running pylint on main modules..."
	$(PYTHON) -m pylint main.py --rcfile=.pylintrc || true
	@echo "🔍 Checking code formatting..."
	$(PYTHON) -m black --check --diff .
	@echo "🔍 Checking import sorting..."
	$(PYTHON) -m isort --check-only --diff .
	@echo "✅ All linting checks complete!"

format: ## Format code with black and isort
	@echo "🎨 Formatting code with black..."
	$(PYTHON) -m black .
	@echo "🎨 Sorting imports with isort..."
	$(PYTHON) -m isort .
	@echo "✅ Code formatting complete!"

type-check: ## Run type checking with mypy
	@echo "🔍 Running type checking..."
	$(PYTHON) -m mypy main.py --config-file=pyproject.toml

security: ## Run security analysis with bandit
	@echo "🔒 Running security analysis..."
	$(PYTHON) -m bandit -r . -x $(TEST_DIR)/ -ll

# Quality suite
quality: lint type-check security test ## Run complete quality suite
	@echo "🏆 All quality checks complete!"

# Pre-commit
pre-commit: ## Run pre-commit hooks on all files
	pre-commit run --all-files

pre-commit-install: ## Install pre-commit hooks
	pre-commit install
	@echo "✅ Pre-commit hooks installed!"

# Coverage
coverage: ## Generate detailed coverage report
	$(PYTHON) -m pytest $(TEST_DIR)/ --cov=. --cov-report=html --cov-report=xml --cov-report=term
	@echo "📊 Coverage report generated in $(COVERAGE_DIR)/"

coverage-open: coverage ## Generate and open coverage report
	open $(COVERAGE_DIR)/index.html

# Performance profiling
profile: ## Run performance profiling
	$(PYTHON) -m cProfile -o profile_stats.prof main.py
	$(PYTHON) -c "import pstats; pstats.Stats('profile_stats.prof').sort_stats('cumulative').print_stats(20)"

# Documentation
docs: ## Generate documentation
	@echo "📚 Generating documentation..."
	mkdir -p $(DOCS_DIR)
	$(PYTHON) -m pydoc -w main
	mv *.html $(DOCS_DIR)/
	@echo "✅ Documentation generated in $(DOCS_DIR)/"

docs-serve: docs ## Generate and serve documentation
	cd $(DOCS_DIR) && $(PYTHON) -m http.server 8080

# Database and analysis
analyze-all: ## Run all analysis modules
	@echo "🎭 Running complete theater analysis suite..."
	$(PYTHON) lyrical_analysis.py
	$(PYTHON) character_arc_analysis.py
	$(PYTHON) emotional_journey_analysis.py
	$(PYTHON) cultural_commentary_analysis.py
	$(PYTHON) production_complexity_analysis.py
	$(PYTHON) thematic_resonance_analysis.py
	@echo "✅ All analyses complete!"

dashboard: ## Start dashboard server
	@echo "🌐 Starting dashboard server..."
	$(PYTHON) -m http.server 8000 --directory .

# Data management
clean-data: ## Clean analysis data files
	@echo "🧹 Cleaning analysis data..."
	find . -name "*_analysis.json" -delete
	@echo "✅ Analysis data cleaned!"

backup-data: ## Backup analysis results
	@echo "💾 Backing up analysis data..."
	mkdir -p backups/$(shell date +%Y%m%d_%H%M%S)
	cp *_analysis.json backups/$(shell date +%Y%m%d_%H%M%S)/ 2>/dev/null || true
	@echo "✅ Data backed up!"

# Cleanup targets
clean: ## Clean temporary files and caches
	@echo "🧹 Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache
	rm -rf $(COVERAGE_DIR)
	rm -rf .mypy_cache
	rm -rf build/
	rm -rf dist/
	rm -f profile_stats.prof
	@echo "✅ Cleanup complete!"

clean-all: clean clean-data ## Clean everything including data
	@echo "🧹 Deep cleaning..."
	rm -rf $(VENV_DIR)
	@echo "✅ Deep cleanup complete!"

# Build targets
build: ## Build distribution packages
	@echo "📦 Building distribution..."
	$(PYTHON) -m build
	@echo "✅ Build complete!"

build-clean: clean build ## Clean build artifacts and rebuild
	@echo "📦 Clean build complete!"

# Development workflow
dev-setup: install-dev pre-commit-install ## Setup development environment
	@echo "🚀 Development environment ready!"

dev-check: format lint test-fast ## Quick development checks
	@echo "✅ Development checks passed!"

dev-test: format lint test ## Full development test suite
	@echo "✅ Full development test suite passed!"

# CI/CD simulation
ci: ## Simulate CI/CD pipeline
	@echo "🤖 Simulating CI/CD pipeline..."
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) security
	$(MAKE) test
	@echo "✅ CI/CD simulation complete!"

# Deployment helpers
deploy-check: quality ## Pre-deployment quality checks
	@echo "🚀 Pre-deployment checks complete!"

# Monitoring and maintenance
health-check: ## Run system health checks
	@echo "🏥 Running health checks..."
	$(PYTHON) -c "import sys; print(f'Python version: {sys.version}')"
	$(PYTHON) -c "import httpx; print('✅ httpx available')"
	$(PYTHON) -c "import asyncio; print('✅ asyncio available')"
	$(PYTHON) -c "import json; print('✅ json available')"
	@echo "✅ Health check complete!"

dependencies-check: ## Check for dependency updates
	@echo "📦 Checking dependencies..."
	$(PIP) list --outdated
	@echo "✅ Dependency check complete!"

# Quick commands
q: test-fast ## Quick test (alias for test-fast)
f: format ## Quick format (alias for format)
l: lint ## Quick lint (alias for lint)

# Performance benchmarks
benchmark: ## Run performance benchmarks
	@echo "⚡ Running performance benchmarks..."
	$(PYTHON) -m timeit -s "from main import SceneData" "SceneData('test', 'test', 'test')"
	@echo "✅ Benchmarks complete!"

# Git helpers
git-hooks: pre-commit-install ## Setup git hooks
	@echo "🔗 Git hooks configured!"

# Database operations (if needed for analysis)
db-reset: ## Reset analysis database (placeholder)
	@echo "🗄️ Database reset placeholder - implement if needed"

# Container operations (if using Docker)
docker-build: ## Build Docker container (placeholder)
	@echo "🐳 Docker build placeholder - implement if needed"

docker-run: ## Run Docker container (placeholder)
	@echo "🐳 Docker run placeholder - implement if needed"

# Final status
status: ## Show project status
	@echo "Theater Critics System Status"
	@echo "============================"
	@echo "Python version: $(shell $(PYTHON) --version)"
	@echo "Project directory: $(shell pwd)"
	@echo "Test files: $(shell find $(TEST_DIR) -name "*.py" | wc -l)"
	@echo "Python files: $(shell find . -name "*.py" -not -path "./$(VENV_DIR)/*" | wc -l)"
	@echo "Analysis files: $(shell ls *_analysis.json 2>/dev/null | wc -l)"
	@echo "============================"