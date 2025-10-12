# Contributing to BlueTrace

Thank you for your interest in contributing to BlueTrace! This document provides guidelines and instructions for contributing.

## Code of Conduct

This project follows a Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to support@bluetrace.dev.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Environment details (OS, Python version, etc.)
- Logs or error messages

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- A clear and descriptive title
- Detailed description of the proposed functionality
- Use cases and examples
- Why this enhancement would be useful

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`make test`)
5. Run linters (`make lint`)
6. Format code (`make format`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to your branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

#### PR Guidelines

- Follow the existing code style
- Add tests for new features
- Maintain 90%+ test coverage
- Update documentation as needed
- Keep PRs focused on a single feature/fix
- Write clear commit messages

## Development Setup

See [README.md](README.md) for detailed setup instructions.

```bash
# Backend
cd backend
poetry install
make dev

# Run tests
make test

# Docs
cd docs
npm install
npm run dev
```

## Coding Standards

### Python (Backend)

- Follow PEP 8
- Use type hints (mypy strict mode)
- Format with Black (line length: 100)
- Lint with Ruff
- Write docstrings for public functions
- Keep functions small and focused

### TypeScript/React (Docs)

- Follow Airbnb style guide
- Use TypeScript for type safety
- Format with Prettier
- Lint with ESLint

## Testing

- Write unit tests for all new features
- Maintain 90%+ code coverage
- Use pytest fixtures appropriately
- Test both success and error paths

```bash
# Run all tests
cd backend
make test

# Run specific test file
poetry run pytest tests/test_auth.py

# Check coverage
poetry run pytest --cov=app --cov-report=html
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings to Python functions/classes
- Update API documentation in `/docs` for endpoint changes
- Include examples in documentation

## Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters
- Reference issues and PRs when relevant

Examples:
```
Add rate limiting to tides endpoint

Implement Redis-based sliding window rate limiter for the tides API
endpoint. Closes #123.
```

## Release Process

Releases are managed by maintainers:

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create and push tag: `git tag -a v1.0.0 -m "Release v1.0.0"`
4. GitHub Actions will build and push Docker images

## Questions?

Feel free to ask questions by:
- Opening a GitHub issue
- Emailing support@bluetrace.dev
- Joining our community chat (coming soon)

Thank you for contributing! 🌊

