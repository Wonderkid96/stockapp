.PHONY: install test lint format clean docker-build docker-run

# Python environment
install:
	pip install -r requirements.txt
	pre-commit install

# Testing
test:
	pytest tests/ -v --cov=trading_bot --cov-report=term-missing

test-watch:
	pytest tests/ -v --cov=trading_bot --cov-report=term-missing -f

test-coverage:
	pytest tests/ -v --cov=trading_bot --cov-report=html

# Linting and formatting
lint:
	flake8 trading_bot tests
	mypy trading_bot tests
	bandit -r trading_bot
	safety check

format:
	black trading_bot tests
	isort trading_bot tests

# Docker
docker-build:
	docker-compose build

docker-run:
	docker-compose up

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".coverage" -exec rm -r {} +
	find . -type d -name "htmlcov" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete

# Development
dev:
	python -m uvicorn trading_bot.app:app --reload

# Database
db-migrate:
	alembic upgrade head

db-rollback:
	alembic downgrade -1

# Documentation
docs:
	sphinx-build -b html docs/ docs/_build/html

# Help
help:
	@echo "Available commands:"
	@echo "  make install        - Install dependencies"
	@echo "  make test          - Run tests"
	@echo "  make test-watch    - Run tests in watch mode"
	@echo "  make test-coverage - Generate test coverage report"
	@echo "  make lint          - Run linters"
	@echo "  make format        - Format code"
	@echo "  make docker-build  - Build Docker images"
	@echo "  make docker-run    - Run Docker containers"
	@echo "  make clean         - Clean up cache files"
	@echo "  make dev           - Run development server"
	@echo "  make db-migrate    - Run database migrations"
	@echo "  make db-rollback   - Rollback last migration"
	@echo "  make docs          - Build documentation" 