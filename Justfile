# Install just: https://github.com/casey/just

# Default recipe
default:
    @just --list

setup:
    @echo "🚀 Setting up development environment..."
    uv sync --dev
    @echo "✅ Setup complete!"

# Lint code
lint:
    @echo "🔍 Linting code..."
    uv run ruff check --fix --unsafe-fixes src/ tests/
    uv run ruff format
    @echo "✅ Lint complete!"

# Run tests
test:
    @echo "🧪 Running tests..."
    uv run pytest tests/ -v --cov=src/polarsteps_api --cov-report=term-missing --cov-report=html
    @echo "✅ Tests complete!"
