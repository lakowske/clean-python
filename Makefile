# Makefile for clean-python template
# This provides convenient shortcuts for common development tasks

SHELL := /bin/bash
PYTHON := python3
VENV_DIR := .venv
VENV_PYTHON := $(VENV_DIR)/bin/python

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

.PHONY: help install test lint format type-check docs clean all pre-commit

# Default target
help:
	@echo "Available targets:"
	@echo "  help         - Show this help message"
	@echo "  install      - Install development dependencies using uv"
	@echo "  test         - Run tests with coverage"
	@echo "  lint         - Run linting checks"
	@echo "  format       - Format code with ruff"
	@echo "  type-check   - Run type checking with mypy"
	@echo "  docs         - Build documentation"
	@echo "  clean        - Clean build artifacts"
	@echo "  pre-commit   - Run all pre-commit checks"
	@echo "  all          - Run all checks (lint, format, type-check, test)"

# Create virtual environment using uv
$(VENV_DIR):
	@echo -e "$(YELLOW)Creating virtual environment with uv...$(NC)"
	uv venv $(VENV_DIR)
	@echo -e "$(GREEN)✓ Virtual environment created at $(VENV_DIR)$(NC)"

# Install dependencies using uv
install: $(VENV_DIR)
	@echo "Installing development dependencies with uv..."
	uv pip install --python $(VENV_PYTHON) -e ".[dev]"

# Run tests with coverage
test:
	$(VENV_DIR)/bin/pytest --cov=src --cov-report=term-missing --cov-fail-under=80 --cov-report=html

# Run linting
lint:
	$(VENV_DIR)/bin/ruff check .

# Format code
format:
	$(VENV_DIR)/bin/ruff format .

# Run type checking
type-check:
	@if [ -f "$(VENV_DIR)/bin/pre-commit" ]; then \
		$(VENV_DIR)/bin/pre-commit run mypy --all-files; \
	else \
		$(VENV_DIR)/bin/mypy src tests; \
	fi

# Build documentation
docs:
	@if [ -f "mkdocs.yml" ]; then \
		$(VENV_DIR)/bin/mkdocs build; \
	else \
		echo "No mkdocs.yml found. Run 'mkdocs new .' to initialize docs."; \
	fi

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf site/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# Run pre-commit checks
pre-commit:
	$(VENV_DIR)/bin/pre-commit run --all-files

# Run all checks
all: lint format type-check test
	@echo "All checks passed!"
