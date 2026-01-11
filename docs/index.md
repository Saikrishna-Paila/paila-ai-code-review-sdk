# Paila SDK Documentation

**AI-Powered Code Review SDK for Python**

Created by **Saikrishna Paila**

---

## Table of Contents

1. [Getting Started](getting-started.md)
2. [Configuration](configuration.md)
3. [Analyzers](analyzers.md)
4. [Reporters](reporters.md)
5. [AI Integration](ai-integration.md)
6. [Custom Rules](custom-rules.md)
7. [Integrations](integrations.md)
8. [API Reference](api-reference.md)
9. [CLI Reference](cli-reference.md)
10. [Project Structure](project-structure.md)
11. [Contributing](contributing.md)

---

## What is Paila?

Paila is a comprehensive code review SDK that automatically analyzes Python code for:

- **Security vulnerabilities** - SQL injection, command injection, hardcoded secrets
- **Code complexity** - Cyclomatic complexity, nesting depth, function length
- **Code smells** - Missing docstrings, magic numbers, unused variables
- **Potential bugs** - Empty except blocks, mutable defaults

## Quick Example

```python
from paila import Reviewer

# Create a reviewer
reviewer = Reviewer()

# Review a file
result = reviewer.review_file("my_code.py")

# Print summary
print(f"Score: {result.score}/100")
print(f"Issues found: {len(result.issues)}")

# Review entire project
result = reviewer.review_directory("./src")
print(result.summary)
```

## Features

### Multiple Analyzers
- **ComplexityAnalyzer** - Detects complex, hard-to-maintain code
- **SecurityAnalyzer** - Finds security vulnerabilities
- **SmellAnalyzer** - Identifies code smells and anti-patterns

### Multiple Output Formats
- Terminal (colored output)
- JSON (for CI/CD integration)
- Markdown (for documentation)
- HTML (for web reports)

### AI-Powered Insights
- Explain issues in plain English
- Suggest fixes automatically
- Summarize entire reviews

### Extensible
- Create custom analyzers
- Define custom rules
- Integrate with GitHub/GitLab

---

## Installation

```bash
pip install paila
```

With AI support:
```bash
pip install paila[ai]
```

For development:
```bash
pip install paila[dev]
```

---

## Support

- GitHub Issues: [github.com/saikrishnapaila/paila-ai-code-review-sdk/issues](https://github.com/saikrishnapaila/paila-ai-code-review-sdk/issues)
- Documentation: [github.com/saikrishnapaila/paila-ai-code-review-sdk/docs](https://github.com/saikrishnapaila/paila-ai-code-review-sdk/docs)

---

*Built with Python by Saikrishna Paila*
