# CLI Reference

Complete command-line interface documentation for Paila SDK.

## Installation

```bash
pip install paila
```

## Commands

### paila review

Review code for issues.

```bash
paila review <path> [options]
```

**Arguments:**
- `<path>`: File or directory to review

**Options:**
| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--format` | `-f` | Output format (terminal, json, markdown, html) | terminal |
| `--output` | `-o` | Output file path | stdout |
| `--analyzers` | `-a` | Comma-separated analyzers | all |
| `--min-severity` | | Minimum severity (critical, high, medium, low, info) | info |
| `--no-parallel` | | Disable parallel processing | false |
| `--ai` | | Enable AI explanations | false |
| `--strict` | | Use strict configuration | false |
| `--relaxed` | | Use relaxed configuration | false |
| `--security-only` | | Only security checks | false |

**Examples:**

```bash
# Review a file
paila review main.py

# Review a directory
paila review ./src

# Review with JSON output
paila review ./src --format json

# Save report to file
paila review ./src --format markdown --output REVIEW.md

# Generate HTML report
paila review ./src --format html --output report.html

# Only security checks
paila review ./src --security-only

# Strict mode
paila review ./src --strict

# Only high and critical issues
paila review ./src --min-severity high

# Specific analyzers
paila review ./src --analyzers security,complexity

# With AI explanations
paila review ./src --ai
```

---

### paila check

Quick check with pass/fail exit code. Useful for CI/CD.

```bash
paila check <path> [options]
```

**Arguments:**
- `<path>`: File or directory to check

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--fail-on` | Minimum severity to fail (critical, high, medium, low, info) | high |

**Exit Codes:**
- `0`: Passed (no issues at or above fail-on level)
- `1`: Failed (issues found at or above fail-on level)

**Examples:**

```bash
# Fail on high or critical
paila check ./src --fail-on high

# Fail only on critical
paila check ./src --fail-on critical

# Fail on any issue
paila check ./src --fail-on info

# Use in CI/CD
paila check ./src --fail-on high && echo "Passed!" || echo "Failed!"
```

---

### paila init

Initialize Paila configuration file.

```bash
paila init
```

Creates a `.paila.toml` file in the current directory with default settings.

**Example:**

```bash
cd my-project
paila init
# Created: .paila.toml
```

---

### paila --version

Show version information.

```bash
paila --version
# Paila SDK v0.1.0
```

---

### paila --help

Show help information.

```bash
paila --help
paila review --help
paila check --help
```

---

## Configuration File

When `paila` runs, it looks for `.paila.toml` in the current directory.

```toml
[paila]
analyzers = ["complexity", "security", "smells"]
min_severity = "info"
max_complexity = 10
max_nesting_depth = 4
max_function_lines = 50
max_parameters = 5
max_line_length = 120
max_file_lines = 500

ignore_patterns = [
    "__pycache__",
    ".git",
    "node_modules",
    ".venv",
]

ignore_files = [
    "__init__.py",
    "setup.py",
]

ai_enabled = false
ai_model = "claude-sonnet-4-20250514"
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | API key for Claude AI |
| `OPENAI_API_KEY` | API key for OpenAI |
| `PAILA_CONFIG` | Path to configuration file |

---

## Output Formats

### Terminal (default)

```
╔══════════════════════════════════════════════════════════╗
║  PAILA CODE REVIEW REPORT                                ║
╚══════════════════════════════════════════════════════════╝

📋 SUMMARY
----------------------------------------
  Files analyzed: 5
  Total issues: 12
  Score: 75/100 (Grade: C)

🎯 ISSUES BY SEVERITY
----------------------------------------
  🚨 CRITICAL: 1
  ❌ HIGH: 2
  ⚠️  MEDIUM: 4
```

### JSON

```json
{
  "summary": {
    "total_files": 5,
    "total_issues": 12,
    "score": 75,
    "grade": "C"
  },
  "issues": [...]
}
```

### Markdown

```markdown
# 📋 Paila Code Review Report

## Summary
| Metric | Value |
|--------|-------|
| Score | 75/100 |
```

### HTML

Standalone HTML file with inline CSS, viewable in any browser.

---

## Integration Examples

### Git Pre-commit Hook

```bash
#!/bin/bash
paila check ./src --fail-on high
```

### GitHub Actions

```yaml
- name: Code Review
  run: paila check ./src --fail-on high
```

### Makefile

```makefile
lint:
	paila check ./src --fail-on medium

review:
	paila review ./src --format html --output review.html
```

---

## Troubleshooting

### No output / Empty results

- Check if files match supported languages (`.py`)
- Check ignore patterns aren't too broad
- Verify path is correct

### Too many issues

- Use `--min-severity` to filter
- Use `--relaxed` for higher thresholds
- Add patterns to `ignore_patterns`

### AI features not working

- Set `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`
- Install AI dependencies: `pip install paila[ai]`
- Check API key is valid

### Performance issues

- Disable parallel with `--no-parallel` for debugging
- Exclude large generated files
- Use `--analyzers` to run only needed analyzers
