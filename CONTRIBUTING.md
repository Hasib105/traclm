# Contributing to LLM Tracer

Thank you for your interest in contributing to LLM Tracer! This document provides guidelines and instructions for contributing.

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- Git

### Development Setup

1. **Fork and clone the repository**

   ```bash
   git clone https://github.com/yourusername/llm-tracer.git
   cd llm-tracer
   ```

2. **Install dependencies with uv**

   ```bash
   # Install all dependencies including dev extras
   uv sync --all-extras
   ```

3. **Set up pre-commit hooks**

   ```bash
   uv run pre-commit install
   ```

4. **Run the tests to ensure everything works**

   ```bash
   uv run pytest
   ```

## 📝 Development Workflow

### Branch Naming

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions or modifications

### Making Changes

1. Create a new branch from `main`:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and ensure:
   - Code follows the project style (enforced by ruff)
   - Tests pass
   - New features include tests
   - Documentation is updated if needed

3. Run the quality checks:

   ```bash
   # Format code
   uv run ruff format src tests

   # Check for issues
   uv run ruff check src tests

   # Run tests
   uv run pytest

   # Type checking
   uv run mypy src
   ```

4. Commit your changes:

   ```bash
   git commit -m "feat: add your feature description"
   ```

   We follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` - New features
   - `fix:` - Bug fixes
   - `docs:` - Documentation changes
   - `refactor:` - Code refactoring
   - `test:` - Test changes
   - `chore:` - Maintenance tasks

5. Push and create a Pull Request:

   ```bash
   git push origin feature/your-feature-name
   ```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_api.py -v

# Run tests matching a pattern
uv run pytest -k "test_create"
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files with `test_` prefix
- Name test functions with `test_` prefix
- Use pytest fixtures for shared setup
- Aim for high test coverage on new code

## 📖 Code Style

We use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting:

- Line length: 100 characters
- Python 3.10+ syntax
- Import sorting with isort rules
- Type hints are encouraged

## 📋 Pull Request Guidelines

1. **Fill out the PR template** completely
2. **Link related issues** using keywords like "Fixes #123"
3. **Keep PRs focused** - one feature/fix per PR
4. **Update documentation** for user-facing changes
5. **Add tests** for new functionality
6. **Ensure CI passes** before requesting review

## 🐛 Reporting Issues

When reporting issues, please include:

- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Relevant logs or error messages

## 💬 Questions?

Feel free to open an issue for questions or join our discussions.

Thank you for contributing! 🎉
