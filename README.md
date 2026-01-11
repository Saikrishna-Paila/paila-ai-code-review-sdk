<div align="center">

<!-- BANNER -->
<img src="assets/banner.svg" alt="Paila SDK Banner" width="800"/>

<br/>

<!-- LOGO BADGE -->
<img src="assets/logo.svg" alt="Paila Logo" width="120"/>

# PAILA SDK

### AI-Powered Code Review SDK for Python

<br/>

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Version](https://img.shields.io/badge/Version-0.1.0-blue?style=for-the-badge)]()
[![Tests](https://img.shields.io/badge/Tests-49%20Passing-success?style=for-the-badge&logo=pytest&logoColor=white)]()

<br/>

[![Claude](https://img.shields.io/badge/Claude-Anthropic-cc785c?style=flat-square&logo=anthropic&logoColor=white)](https://anthropic.com)
[![OpenAI](https://img.shields.io/badge/GPT--4-OpenAI-412991?style=flat-square&logo=openai&logoColor=white)](https://openai.com)
[![Groq](https://img.shields.io/badge/Llama-Groq-f55036?style=flat-square&logo=meta&logoColor=white)](https://groq.com)

<br/>

**[📖 Documentation](#-documentation)** · **[🚀 Quick Start](#-quick-start)** · **[💡 Examples](#-examples)** · **[🤝 Contributing](#-contributing)**

<br/>

---

<br/>

<img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&weight=500&size=22&pause=1000&color=9F7AEA&center=true&vCenter=true&random=false&width=600&lines=Find+Security+Vulnerabilities;Detect+Code+Complexity;Catch+Code+Smells;Get+AI-Powered+Suggestions" alt="Typing SVG" />

<br/>

</div>

---

## 🎯 What is Paila?

**Paila** (named after creator **Saikrishna Paila**) is a powerful, extensible code review SDK that automatically analyzes Python code for:

- 🔒 **Security Vulnerabilities** - SQL injection, command injection, hardcoded secrets
- 📊 **Complexity Issues** - Cyclomatic complexity, deep nesting, long functions
- 🦨 **Code Smells** - Missing docstrings, magic numbers, dead code
- 🤖 **AI-Powered Insights** - Explanations and fix suggestions from Claude, GPT-4, or Llama

<br/>

<div align="center">

```
┌────────────────────────────────────────────────────────────────────────┐
│                                                                        │
│                         🔍  PAILA SDK                                  │
│                    AI-Powered Code Review                              │
│                                                                        │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│     📁 Your Code                                                       │
│          │                                                             │
│          ▼                                                             │
│    ┌─────────────────────────────────────────────────────────┐        │
│    │              🔬 ANALYZERS                                │        │
│    ├─────────────┬─────────────┬─────────────────────────────┤        │
│    │ 🔒 Security │ 📊 Complex  │ 🦨 Code Smells              │        │
│    │             │             │                              │        │
│    │ • SQL Inj   │ • Cyclom.   │ • Missing Docs               │        │
│    │ • Cmd Inj   │ • Nesting   │ • Magic Numbers              │        │
│    │ • Secrets   │ • Length    │ • Unused Vars                │        │
│    │ • Eval/Exec │ • Params    │ • Empty Except               │        │
│    └─────────────┴─────────────┴─────────────────────────────┘        │
│          │                                                             │
│          ▼                                                             │
│    ┌─────────────────────────────────────────────────────────┐        │
│    │           🤖 AI ENHANCEMENT (Optional)                   │        │
│    │                                                          │        │
│    │    Claude  │  GPT-4  │  Llama/Mixtral (Groq)            │        │
│    │              │                                           │        │
│    │    💡 Explanations    🔧 Fix Suggestions                 │        │
│    └─────────────────────────────────────────────────────────┘        │
│          │                                                             │
│          ▼                                                             │
│    ┌─────────────────────────────────────────────────────────┐        │
│    │              📤 OUTPUT FORMATS                           │        │
│    ├─────────────┬─────────────┬─────────────┬───────────────┤        │
│    │ 🖥️ Terminal │ 📄 JSON     │ 📝 Markdown │ 🌐 HTML       │        │
│    └─────────────┴─────────────┴─────────────┴───────────────┘        │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

</div>

---

## ✨ Features

<table>
<tr>
<td width="50%" valign="top">

### 🔒 Security Analysis

| Detection | Severity |
|-----------|----------|
| SQL Injection (f-string, concat, format) | 🔴 Critical |
| Command Injection (os.system, subprocess) | 🔴 Critical |
| Hardcoded Passwords & API Keys | 🟠 High |
| `eval()` / `exec()` Usage | 🟠 High |
| Pickle Deserialization | 🟡 Medium |
| Insecure Hash (MD5/SHA1) | 🟡 Medium |
| Path Traversal | 🟠 High |

</td>
<td width="50%" valign="top">

### 📊 Complexity Analysis

| Detection | Severity |
|-----------|----------|
| High Cyclomatic Complexity | 🟡 Medium |
| Deep Nesting (>4 levels) | 🟡 Medium |
| Long Functions (>50 lines) | 🔵 Low |
| Too Many Parameters (>5) | 🔵 Low |
| God Classes | 🟡 Medium |
| Large Files (>500 lines) | 🔵 Low |

</td>
</tr>
<tr>
<td width="50%" valign="top">

### 🦨 Code Smell Detection

| Detection | Severity |
|-----------|----------|
| Missing Docstrings | ℹ️ Info |
| Magic Numbers | 🔵 Low |
| Empty/Bare Except Blocks | 🟡 Medium |
| Mutable Default Arguments | 🟡 Medium |
| Unused Variables/Imports | 🔵 Low |
| Star Imports (`from x import *`) | 🔵 Low |
| TODO/FIXME Comments | ℹ️ Info |
| Print Statements | 🔵 Low |

</td>
<td width="50%" valign="top">

### 🤖 AI Integration

| Provider | Models | Speed |
|----------|--------|-------|
| **Anthropic** | Claude Opus, Sonnet, Haiku | ⚡⚡⚡ |
| **OpenAI** | GPT-4o, GPT-4, GPT-3.5 | ⚡⚡⚡ |
| **Groq** | Llama 3.3, Mixtral, Gemma | ⚡⚡⚡⚡ |

**Features:**
- 💡 Intelligent explanations for each issue
- 🔧 Auto-fix suggestions
- 📋 Review summaries

</td>
</tr>
</table>

---

## 📦 Installation

```bash
# 📥 Basic installation
pip install paila

# 🤖 With AI support (recommended)
pip install paila[ai]

# 🛠️ Full installation (AI + dev tools)
pip install paila[ai,dev]
```

<details>
<summary><b>📋 From Source</b></summary>

```bash
git clone https://github.com/saikrishnapaila/paila-ai-code-review-sdk.git
cd paila
pip install -e ".[dev]"
```

</details>

**Requirements:** Python 3.9+

---

## 🚀 Quick Start

### 1️⃣ Review Code String

```python
from paila import review_code

code = """
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return execute(query)
"""

result = review_code(code)

print(f"🎯 Score: {result.score}/100 (Grade: {result.grade})")
print(f"📊 Issues: {len(result.issues)}")

for issue in result.issues:
    print(f"  [{issue.severity.value}] {issue.message}")
```

**Output:**
```
🎯 Score: 85/100 (Grade: B)
📊 Issues: 2
  [critical] Potential SQL injection: SQL query built with f-string
  [info] Function 'get_user' is missing a docstring
```

### 2️⃣ Review a File

```python
from paila import Reviewer

reviewer = Reviewer()
result = reviewer.review_file("my_code.py")

print(f"Score: {result.score}/100")
for issue in result.issues:
    print(f"  Line {issue.line}: {issue.message}")
```

### 3️⃣ Review Entire Project

```python
from paila import Reviewer

reviewer = Reviewer()
result = reviewer.review_directory("./src")

# Print summary
print("=" * 40)
print("       📊 CODE REVIEW SUMMARY")
print("=" * 40)
print(f"  Score:  {result.score}/100 ({result.grade})")
print(f"  Files:  {len(result.files)}")
print(f"  Issues: {result.total_issues}")
print("=" * 40)
```

---

## 💻 CLI Usage

```bash
# 📄 Review a file
paila review main.py

# 📁 Review a directory
paila review ./src

# 💾 Save as JSON
paila review ./src --format json --output report.json

# 🌐 Save as HTML
paila review ./src --format html --output report.html

# ✅ CI/CD check (exit code 1 on issues)
paila check ./src --fail-on high

# 🔒 Security only
paila review ./src --security-only

# 🤖 With AI explanations
paila review ./src --ai

# ⚙️ Initialize config
paila init
```

<details>
<summary><b>📋 All CLI Options</b></summary>

| Option | Description |
|--------|-------------|
| `--format`, `-f` | Output format: `terminal`, `json`, `markdown`, `html` |
| `--output`, `-o` | Save report to file |
| `--analyzers`, `-a` | Analyzers: `security,complexity,smells` |
| `--min-severity` | Filter: `critical`, `high`, `medium`, `low`, `info` |
| `--strict` | Use strict configuration |
| `--relaxed` | Use relaxed configuration |
| `--security-only` | Only run security checks |
| `--ai` | Enable AI explanations |
| `--no-parallel` | Disable parallel processing |

</details>

---

## ⚙️ Configuration

### Using Config Object

```python
from paila import Reviewer, Config

config = Config(
    # Analyzers to use
    analyzers=["security", "complexity", "smells"],

    # Complexity thresholds
    max_complexity=10,
    max_nesting_depth=4,
    max_function_lines=50,
    max_parameters=5,

    # Ignore patterns
    ignore_paths=["test_", "migrations/", "__pycache__"],

    # AI settings
    ai_enabled=True,
    ai_model="claude-sonnet-4-20250514",
)

reviewer = Reviewer(config=config)
```

### Preset Configurations

```python
from paila import Reviewer, Config

# 🔒 Strict - Lower thresholds, catches more
reviewer = Reviewer(config=Config.strict())

# 🟢 Relaxed - Higher thresholds, fewer warnings
reviewer = Reviewer(config=Config.relaxed())

# 🛡️ Security Only - Just security checks
reviewer = Reviewer(config=Config.security_only())
```

### Config File (`.paila.yaml`)

```yaml
analyzers:
  - complexity
  - security
  - smells

max_complexity: 10
max_nesting_depth: 4
max_function_lines: 50
max_parameters: 5

ignore_paths:
  - __pycache__
  - .git
  - node_modules
  - venv

ai_enabled: false
ai_model: claude-sonnet-4-20250514
```

---

## 📤 Output Formats

<table>
<tr>
<td width="25%" align="center">

### 🖥️ Terminal

![Terminal](https://img.shields.io/badge/Format-Terminal-green?style=flat-square)

Colored output with icons

</td>
<td width="25%" align="center">

### 📄 JSON

![JSON](https://img.shields.io/badge/Format-JSON-blue?style=flat-square)

Structured data for CI/CD

</td>
<td width="25%" align="center">

### 📝 Markdown

![Markdown](https://img.shields.io/badge/Format-Markdown-orange?style=flat-square)

GitHub-ready reports

</td>
<td width="25%" align="center">

### 🌐 HTML

![HTML](https://img.shields.io/badge/Format-HTML-red?style=flat-square)

Beautiful web reports

</td>
</tr>
</table>

```python
from paila import review_code
from paila.reporters import TerminalReporter, JSONReporter, MarkdownReporter, HTMLReporter

result = review_code("def foo(): pass")

# Terminal
TerminalReporter().print(result)

# JSON
JSONReporter().report(result, "report.json")

# Markdown
MarkdownReporter().report(result, "REVIEW.md")

# HTML
HTMLReporter().report(result, "report.html")
```

---

## 🤖 AI Integration

### Enable AI Features

```python
from paila.ai import AIEnhancer

# Using Claude (Anthropic)
enhancer = AIEnhancer(provider="anthropic")

# Using GPT-4 (OpenAI)
enhancer = AIEnhancer(provider="openai")

# Using Llama/Mixtral (Groq) - Ultra fast!
enhancer = AIEnhancer(provider="groq")
```

### Get AI Explanations

```python
from paila import Reviewer
from paila.ai import AIEnhancer

reviewer = Reviewer()
result = reviewer.review_file("code.py")

enhancer = AIEnhancer()

for issue in result.issues:
    # Get detailed explanation
    explanation = enhancer.explain_issue(issue)
    print(f"💡 {explanation}")

    # Get fix suggestion
    fix = enhancer.suggest_fix(issue)
    print(f"🔧 {fix}")
```

### AI Provider Comparison

| Provider | Speed | Cost | Best For |
|----------|-------|------|----------|
| **Groq** (Llama 3.3) | ⚡⚡⚡⚡ Fastest | 💰 Cheapest | High volume, fast feedback |
| **Anthropic** (Claude) | ⚡⚡⚡ Fast | 💰💰 Medium | Best explanations |
| **OpenAI** (GPT-4) | ⚡⚡⚡ Fast | 💰💰 Medium | General purpose |

---

## 🔌 CI/CD Integration

### GitHub Actions

```yaml
name: Code Review
on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Paila
        run: pip install paila

      - name: Run Code Review
        run: paila check ./src --fail-on high

      - name: Generate Report
        if: always()
        run: paila review ./src --format markdown --output review.md

      - name: Upload Report
        uses: actions/upload-artifact@v4
        with:
          name: code-review
          path: review.md
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: paila
        name: Paila Code Review
        entry: paila check
        language: system
        types: [python]
        args: [--fail-on, medium]
```

### GitLab CI

```yaml
code-review:
  stage: test
  script:
    - pip install paila
    - paila check ./src --fail-on high
  artifacts:
    when: always
    paths:
      - review.json
```

---

## 🛠️ Custom Analyzers

Create your own analyzer:

```python
from paila.analyzers import BaseAnalyzer
from paila.models import Issue, Severity

class TodoAnalyzer(BaseAnalyzer):
    """Finds TODO comments with assignees."""

    name = "todo"
    description = "Detects TODO comments"

    def analyze(self, code, file_path, tree=None):
        issues = []

        for i, line in enumerate(code.split("\n"), 1):
            if "TODO" in line and "@" not in line:
                issues.append(Issue(
                    type="todo_no_assignee",
                    severity=Severity.INFO,
                    file=file_path,
                    line=i,
                    message="TODO without assignee",
                    suggestion="Add assignee: # TODO(@username): description",
                    rule="custom/todo-assignee",
                ))

        return issues

# Use it
reviewer = Reviewer(custom_analyzers=[TodoAnalyzer()])
```

---

## 📚 API Reference

### Core Classes

```python
# Main reviewer
from paila import Reviewer, Config, review, review_code

# Data models
from paila.models import Issue, Metrics, FileResult, ReviewResult, Severity

# Analyzers
from paila.analyzers import (
    BaseAnalyzer,
    ComplexityAnalyzer,
    SecurityAnalyzer,
    SmellAnalyzer
)

# Reporters
from paila.reporters import (
    TerminalReporter,
    JSONReporter,
    MarkdownReporter,
    HTMLReporter
)

# AI
from paila.ai import AIEnhancer
from paila.ai.providers import AnthropicProvider, OpenAIProvider, GroqProvider

# Rules
from paila.rules import Rule, RuleSet, RuleBuilder

# Integrations
from paila.integrations import GitHubIntegration, GitLabIntegration
```

### Quick Reference

```python
# Review code string
result = review_code("def foo(): pass")

# Review file
reviewer = Reviewer()
result = reviewer.review_file("main.py")

# Review directory
result = reviewer.review_directory("./src")

# Smart review (auto-detect)
result = reviewer.review("./src")

# Get score and grade
print(f"Score: {result.score}/100")
print(f"Grade: {result.grade}")

# Iterate issues
for issue in result.issues:
    print(f"[{issue.severity}] {issue.file}:{issue.line}")
    print(f"  {issue.message}")
    print(f"  Fix: {issue.suggestion}")
```

---

## 📁 Project Structure

```
paila/
├── __init__.py           # Main exports
├── reviewer.py           # Core Reviewer class
├── config.py             # Configuration
├── models.py             # Data models (Issue, Metrics, etc.)
├── cli.py                # CLI interface
│
├── analyzers/            # Code analyzers
│   ├── base.py           # Base analyzer class
│   ├── complexity.py     # Complexity checks
│   ├── security.py       # Security checks
│   └── smells.py         # Code smell checks
│
├── reporters/            # Output formatters
│   ├── terminal.py       # Terminal output
│   ├── json_reporter.py  # JSON output
│   ├── markdown.py       # Markdown output
│   └── html.py           # HTML output
│
├── ai/                   # AI integration
│   ├── enhancer.py       # AI enhancer
│   └── providers/        # AI providers
│       ├── anthropic_provider.py
│       ├── openai_provider.py
│       └── groq_provider.py
│
├── integrations/         # External integrations
│   ├── github.py         # GitHub integration
│   └── gitlab.py         # GitLab integration
│
├── rules/                # Custom rules
│   ├── base.py           # Rule classes
│   └── builtin.py        # Built-in rules
│
├── parsers/              # Code parsers
│   └── python_parser.py  # Python AST parser
│
└── utils/                # Utilities
    ├── file_utils.py
    ├── text_utils.py
    └── hash_utils.py
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=paila --cov-report=html

# Run specific test file
pytest tests/test_analyzers.py -v
```

**Current Status:** ✅ 49 tests passing

---

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](docs/contributing.md) for guidelines.

```bash
# Clone repo
git clone https://github.com/saikrishnapaila/paila-ai-code-review-sdk.git
cd paila

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Format code
black paila/

# Lint
ruff check paila/
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Built with inspiration from:
- [SonarQube](https://www.sonarqube.org/) - Enterprise code quality
- [CodeRabbit](https://coderabbit.ai/) - AI code reviews
- [Pylint](https://pylint.org/) - Python static analysis
- [Bandit](https://bandit.readthedocs.io/) - Security linting

---

<div align="center">

<br/>

**Made with ❤️ by [Saikrishna Paila](https://github.com/saikrishnapaila)**

<br/>

[![Star](https://img.shields.io/badge/⭐_Star_on_GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/saikrishnapaila/paila-ai-code-review-sdk)

<br/>

<sub>If you find Paila useful, please consider giving it a ⭐</sub>

<br/>

---

<br/>

<img src="https://img.shields.io/badge/Project_3_of_12-12_AI_Projects_2026-blueviolet?style=flat-square" alt="Project 3 of 12"/>

</div>
