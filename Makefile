# Django Development Tools Makefile

.PHONY: help install format lint test test-cov check graph shell server clean

# Default target
help:
	@echo "🔧 Django Development Tools"
	@echo ""
	@echo "Available commands:"
	@echo "  make install     Install development dependencies"
	@echo "  make format      Format code with Black and isort"
	@echo "  make lint        Lint code with flake8"
	@echo "  make test        Run tests with pytest"
	@echo "  make test-cov    Run tests with coverage report"
	@echo "  make check       Run all code quality checks"
	@echo "  make graph       Generate model relationship graph"
	@echo "  make shell       Start Django shell with extensions"
	@echo "  make server      Start Django development server"
	@echo "  make clean       Clean up temporary files"
	@echo ""
	@echo "Examples:"
	@echo "  make format"
	@echo "  make check"
	@echo "  make test-cov"
	@echo "  make server"

# Install development dependencies
install:
	@echo "📦 Installing development dependencies..."
	python3 -m pip install django-debug-toolbar django-extensions pytest pytest-django factory-boy black flake8 isort djangorestframework

# Format code
format:
	@echo "🎨 Formatting code..."
	black .
	isort .

# Lint code
lint:
	@echo "🔍 Linting code..."
	flake8 .

# Run tests
test:
	@echo "🧪 Running tests..."
	pytest

# Run tests with coverage
test-cov:
	@echo "🧪 Running tests with coverage..."
	pytest --cov=apps --cov-report=html --cov-report=term-missing

# Run all code quality checks
check: format lint test
	@echo "✅ All code quality checks completed!"

# Generate model graph
graph:
	@echo "📊 Generating model relationship graph..."
	python manage.py graph_models -a -o models.png

# Start Django shell
shell:
	@echo "🐍 Starting Django shell..."
	python manage.py shell_plus

# Start Django server
server:
	@echo "🚀 Starting Django development server..."
	python manage.py runserver 0.0.0.0:3000

# Clean up temporary files
clean:
	@echo "🧹 Cleaning up temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -f models.png
	rm -rf test_media/
	rm -rf test_static/
