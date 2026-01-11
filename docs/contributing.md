# Contributing to Paila SDK

Thank you for your interest in contributing to Paila SDK! This guide will help you get started.

## Getting Started

### 1. Fork and Clone

```bash
# Fork on GitHub, then:
git clone https://github.com/YOUR-USERNAME/paila.git
cd paila
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### 3. Run Tests

```bash
pytest tests/ -v
```

---

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/my-new-feature
# or
git checkout -b fix/bug-description
```

### 2. Make Changes

- Write code
- Add tests
- Update documentation

### 3. Run Checks

```bash
# Format code
black paila/

# Lint
ruff check paila/

# Type check
mypy paila/

# Run tests
pytest tests/ -v

# Run all checks
make check
```

### 4. Commit

```bash
git add .
git commit -m "feat: add new feature"
```

Use conventional commit messages:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `test:` - Tests
- `refactor:` - Code refactoring
- `chore:` - Maintenance

### 5. Push and Create PR

```bash
git push origin feature/my-new-feature
```

Then create a Pull Request on GitHub.

---

## Project Structure

```
paila/
├── __init__.py          # Package exports
├── reviewer.py          # Main Reviewer class
├── config.py            # Configuration
├── models.py            # Data models
├── cli.py               # CLI interface
├── analyzers/           # Code analyzers
│   ├── base.py          # Base analyzer class
│   ├── complexity.py    # Complexity analyzer
│   ├── security.py      # Security analyzer
│   └── smells.py        # Code smell analyzer
├── reporters/           # Output formatters
│   ├── base.py          # Base reporter
│   ├── terminal.py      # Terminal output
│   ├── json_reporter.py # JSON output
│   ├── markdown.py      # Markdown output
│   └── html.py          # HTML output
├── ai/                  # AI integration
│   ├── enhancer.py      # AI enhancer
│   ├── prompts.py       # AI prompts
│   └── providers/       # AI providers
├── parsers/             # Code parsers
├── rules/               # Custom rules
├── integrations/        # External integrations
└── utils/               # Utility functions

tests/
├── test_reviewer.py
├── test_analyzers.py
└── test_reporters.py

docs/
├── index.md
├── getting-started.md
└── ...
```

---

## Adding a New Analyzer

1. Create file in `paila/analyzers/`:

```python
# paila/analyzers/my_analyzer.py
from .base import BaseAnalyzer
from ..models import Issue, Severity

class MyAnalyzer(BaseAnalyzer):
    name = "my_analyzer"
    description = "Description of what it detects"

    def analyze(self, code, file_path, tree=None):
        issues = []
        # Your analysis logic
        return issues
```

2. Export in `paila/analyzers/__init__.py`:

```python
from .my_analyzer import MyAnalyzer

__all__ = [..., "MyAnalyzer"]
```

3. Add tests in `tests/test_analyzers.py`

4. Update documentation

---

## Adding a New Reporter

1. Create file in `paila/reporters/`:

```python
# paila/reporters/my_reporter.py
from .base import BaseReporter

class MyReporter(BaseReporter):
    name = "my_format"
    extension = ".ext"

    def format(self, result):
        # Format result
        return "formatted output"
```

2. Export in `paila/reporters/__init__.py`

3. Add to CLI options if needed

4. Add tests and documentation

---

## Code Style

### Python Style

- Follow PEP 8
- Use type hints
- Max line length: 88 (Black default)
- Use docstrings for public APIs

### Formatting

```bash
# Auto-format with Black
black paila/

# Sort imports
isort paila/
```

### Linting

```bash
# Lint with Ruff
ruff check paila/

# Fix auto-fixable issues
ruff check paila/ --fix
```

---

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Tests

```bash
# By file
pytest tests/test_reviewer.py -v

# By class
pytest tests/test_analyzers.py::TestSecurityAnalyzer -v

# By name pattern
pytest tests/ -k "security" -v
```

### Test Coverage

```bash
pytest tests/ --cov=paila --cov-report=html
open htmlcov/index.html
```

### Writing Tests

```python
import pytest
from paila import Reviewer

class TestMyFeature:
    def test_basic_case(self):
        reviewer = Reviewer()
        result = reviewer.review_code("def foo(): pass")
        assert result is not None

    def test_edge_case(self):
        # Test edge cases
        pass

    @pytest.fixture
    def my_fixture(self):
        return "test data"
```

---

## Documentation

- Keep docs in `docs/` directory
- Use Markdown format
- Include code examples
- Update API reference for new features

---

## Pull Request Guidelines

1. **One feature per PR** - Keep PRs focused
2. **Include tests** - All new features need tests
3. **Update docs** - Document new features
4. **Pass CI** - All checks must pass
5. **Descriptive title** - Use conventional commit format
6. **Link issues** - Reference related issues

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Refactoring

## Testing
Describe how you tested

## Checklist
- [ ] Tests pass
- [ ] Linting passes
- [ ] Documentation updated
```

---

## Release Process

1. Update version in `paila/__init__.py`
2. Update CHANGELOG.md
3. Create release branch
4. Create GitHub release
5. Publish to PyPI

---

## Code of Conduct

- Be respectful
- Be constructive
- Be inclusive

---

## Questions?

- Open a GitHub issue
- Start a discussion

Thank you for contributing!

*— Saikrishna Paila*
