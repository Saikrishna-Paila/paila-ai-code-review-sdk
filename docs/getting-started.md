# Getting Started with Paila SDK

This guide will help you get up and running with Paila SDK in minutes.

## Installation

### Basic Installation

```bash
pip install paila
```

### With AI Support

```bash
pip install paila[ai]
```

### For Development

```bash
pip install paila[dev]
```

### From Source

```bash
git clone https://github.com/saikrishnapaila/paila.git
cd paila
pip install -e .
```

## Your First Code Review

### 1. Review a Code String

```python
from paila import review_code

code = """
def calculate(x):
    return x * 3.14159
"""

result = review_code(code)

print(f"Issues found: {len(result.issues)}")
for issue in result.issues:
    print(f"  [{issue.severity.value}] {issue.message}")
```

### 2. Review a File

```python
from paila import Reviewer

reviewer = Reviewer()
result = reviewer.review_file("my_code.py")

print(f"Score: {result.metrics.lines_of_code} lines analyzed")
print(f"Issues: {len(result.issues)}")
```

### 3. Review a Directory

```python
from paila import Reviewer

reviewer = Reviewer()
result = reviewer.review_directory("./src")

print(result.summary)
```

## Using the CLI

### Review Files

```bash
# Review a single file
paila review main.py

# Review a directory
paila review ./src

# Review with specific format
paila review ./src --format json --output report.json
```

### Quick Check

```bash
# Check and fail on high severity issues
paila check ./src --fail-on high
```

### Initialize Config

```bash
# Create a .paila.toml configuration file
paila init
```

## Understanding Results

### FileResult

When you review a single file, you get a `FileResult`:

```python
result = reviewer.review_file("my_code.py")

print(result.file)           # File path
print(result.issues)         # List of Issue objects
print(result.metrics)        # Code metrics
print(result.skipped)        # Was file skipped?
```

### ReviewResult

When you review a directory, you get a `ReviewResult`:

```python
result = reviewer.review_directory("./src")

print(result.score)              # 0-100 score
print(result.grade)              # A, B, C, D, or F
print(result.total_issues)       # Total issue count
print(result.issues_by_severity) # Issues grouped by severity
print(result.summary)            # Human-readable summary
```

### Issue Object

Each issue contains:

```python
for issue in result.issues:
    print(issue.type)        # Issue type (e.g., "sql_injection")
    print(issue.severity)    # Severity (critical, high, medium, low, info)
    print(issue.file)        # File path
    print(issue.line)        # Line number
    print(issue.message)     # Description
    print(issue.suggestion)  # How to fix
    print(issue.rule)        # Rule that detected it
```

## Next Steps

- [Configure Paila](configuration.md) - Customize settings
- [Learn about Analyzers](analyzers.md) - Understand what gets detected
- [Output Formats](reporters.md) - Generate reports
- [AI Integration](ai-integration.md) - Get AI-powered explanations
