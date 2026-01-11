# Project Structure

## Overview

The Paila SDK is organized into logical modules for maintainability and extensibility.

```
03-paila-sdk/
│
├── paila/                          # Main SDK package
│   ├── __init__.py                 # Package exports & version
│   ├── reviewer.py                 # Core Reviewer class
│   ├── config.py                   # Configuration management
│   ├── models.py                   # Data models (Issue, Metrics, etc.)
│   ├── cli.py                      # Command-line interface
│   │
│   ├── analyzers/                  # Code analysis modules
│   │   ├── __init__.py             # Analyzer exports
│   │   ├── base.py                 # BaseAnalyzer abstract class
│   │   ├── complexity.py           # Cyclomatic complexity checks
│   │   ├── security.py             # Security vulnerability detection
│   │   └── smells.py               # Code smell detection
│   │
│   ├── reporters/                  # Output formatting modules
│   │   ├── __init__.py             # Reporter exports
│   │   ├── base.py                 # BaseReporter abstract class
│   │   ├── terminal.py             # Colored terminal output
│   │   ├── json_reporter.py        # JSON format output
│   │   ├── markdown.py             # Markdown format output
│   │   └── html.py                 # HTML report generation
│   │
│   ├── ai/                         # AI integration
│   │   ├── __init__.py             # AI module exports
│   │   ├── enhancer.py             # AI enhancement orchestrator
│   │   ├── prompts.py              # AI prompt templates
│   │   └── providers/              # AI provider implementations
│   │       ├── __init__.py         # Provider exports & factory
│   │       ├── base.py             # BaseProvider abstract class
│   │       ├── anthropic_provider.py  # Claude integration
│   │       ├── openai_provider.py     # GPT integration
│   │       └── groq_provider.py       # Llama/Mixtral integration
│   │
│   ├── integrations/               # External service integrations
│   │   ├── __init__.py             # Integration exports
│   │   ├── base.py                 # BaseIntegration abstract class
│   │   ├── github.py               # GitHub API integration
│   │   └── gitlab.py               # GitLab API integration
│   │
│   ├── rules/                      # Custom rule system
│   │   ├── __init__.py             # Rule exports
│   │   ├── base.py                 # Rule, RuleSet, RuleBuilder classes
│   │   └── builtin.py              # Built-in security/style rules
│   │
│   ├── parsers/                    # Code parsing utilities
│   │   ├── __init__.py             # Parser exports
│   │   ├── base.py                 # BaseParser abstract class
│   │   └── python_parser.py        # Python AST parser
│   │
│   └── utils/                      # Utility functions
│       ├── __init__.py             # Utility exports
│       ├── file_utils.py           # File operations
│       ├── text_utils.py           # Text manipulation
│       └── hash_utils.py           # Hashing & deduplication
│
├── tests/                          # Unit tests (pytest)
│   ├── __init__.py
│   ├── test_reviewer.py            # Reviewer tests
│   ├── test_analyzers.py           # Analyzer tests
│   └── test_reporters.py           # Reporter tests
│
├── evaluation/                     # SDK evaluation & verification
│   ├── README.md                   # Evaluation overview
│   ├── RESULTS.md                  # Test results summary
│   ├── run_all_tests.py            # Master test runner
│   ├── 01_test_core_modules.py     # Core module tests
│   ├── 02_test_analyzers.py        # Analyzer tests
│   ├── 03_test_reporters.py        # Reporter tests
│   ├── 04_test_ai_providers.py     # AI provider tests
│   ├── 05_test_integrations.py     # Integration tests
│   ├── 06_test_parsers_utils.py    # Parser & utility tests
│   ├── 07_test_rules.py            # Rule system tests
│   └── 08_test_cli.py              # CLI tests
│
├── docs/                           # Documentation
│   ├── index.md                    # Documentation home
│   ├── getting-started.md          # Quick start guide
│   ├── configuration.md            # Configuration reference
│   ├── analyzers.md                # Analyzer documentation
│   ├── reporters.md                # Reporter documentation
│   ├── ai-integration.md           # AI feature docs
│   ├── custom-rules.md             # Custom rule creation
│   ├── integrations.md             # CI/CD integration
│   ├── api-reference.md            # API documentation
│   ├── cli-reference.md            # CLI documentation
│   ├── project-structure.md        # This file
│   └── contributing.md             # Contribution guidelines
│
├── examples/                       # Usage examples
│   ├── basic_usage.py              # Simple usage example
│   └── advanced_usage.py           # Advanced features example
│
├── pyproject.toml                  # Project configuration (pip)
├── README.md                       # Main documentation
├── HOW_WE_BUILT_THIS.md           # Development guide
└── LICENSE                         # MIT License
```

---

## Module Descriptions

### Core Modules

| File | Purpose |
|------|---------|
| `reviewer.py` | Main `Reviewer` class that coordinates all analysis |
| `config.py` | `Config` class with presets (strict, relaxed, security_only) |
| `models.py` | Data classes: `Issue`, `Metrics`, `FileResult`, `ReviewResult`, `Severity` |
| `cli.py` | Command-line interface using argparse |

### Analyzers (`analyzers/`)

| File | What it Detects |
|------|-----------------|
| `security.py` | SQL injection, command injection, hardcoded secrets, eval/exec usage |
| `complexity.py` | Cyclomatic complexity, deep nesting, long functions, too many parameters |
| `smells.py` | Missing docstrings, magic numbers, bare except, mutable defaults |

### Reporters (`reporters/`)

| File | Output Format |
|------|---------------|
| `terminal.py` | Colored terminal output with icons |
| `json_reporter.py` | Structured JSON for CI/CD |
| `markdown.py` | GitHub-flavored Markdown |
| `html.py` | Standalone HTML reports |

### AI Providers (`ai/providers/`)

| File | AI Service |
|------|------------|
| `anthropic_provider.py` | Claude (Opus, Sonnet, Haiku) |
| `openai_provider.py` | GPT-4o, GPT-4, GPT-3.5 |
| `groq_provider.py` | Llama 3.3, Mixtral, Gemma |

### Integrations (`integrations/`)

| File | Service |
|------|---------|
| `github.py` | GitHub PR comments, check runs |
| `gitlab.py` | GitLab MR comments, commit status |

### Rules (`rules/`)

| File | Purpose |
|------|---------|
| `base.py` | `Rule`, `RuleSet`, `RuleBuilder` classes |
| `builtin.py` | Pre-defined `SecurityRules`, `ComplexityRules`, `StyleRules` |

### Utilities (`utils/`)

| File | Functions |
|------|-----------|
| `file_utils.py` | `read_file()`, `find_python_files()`, `is_binary_file()` |
| `text_utils.py` | `truncate_text()`, `highlight_line()`, `count_lines()` |
| `hash_utils.py` | `hash_code()`, `hash_file()`, `find_duplicate_code()` |

---

## File Count Summary

| Category | Files |
|----------|-------|
| Core package (`paila/`) | 25 |
| Tests (`tests/`) | 4 |
| Evaluation (`evaluation/`) | 11 |
| Documentation (`docs/`) | 12 |
| Examples (`examples/`) | 2 |
| Config files | 3 |
| **Total** | **57** |

---

## Import Structure

```python
# Main imports
from paila import Reviewer, Config, review, review_code
from paila.models import Issue, Metrics, FileResult, ReviewResult, Severity

# Analyzers
from paila.analyzers import BaseAnalyzer, SecurityAnalyzer, ComplexityAnalyzer, SmellAnalyzer

# Reporters
from paila.reporters import TerminalReporter, JSONReporter, MarkdownReporter, HTMLReporter

# AI
from paila.ai import AIEnhancer
from paila.ai.providers import AnthropicProvider, OpenAIProvider, GroqProvider

# Rules
from paila.rules import Rule, RuleSet, RuleBuilder, SecurityRules, StyleRules

# Integrations
from paila.integrations import GitHubIntegration, GitLabIntegration

# Utilities
from paila.utils import read_file, hash_code, truncate_text
from paila.parsers import PythonParser
```
