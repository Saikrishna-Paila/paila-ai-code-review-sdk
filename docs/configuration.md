# Configuration

Paila SDK can be configured in multiple ways to suit your project needs.

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `analyzers` | list | `["complexity", "security", "smells"]` | Analyzers to enable |
| `min_severity` | Severity | `INFO` | Minimum severity to report |
| `max_complexity` | int | `10` | Max cyclomatic complexity |
| `max_nesting_depth` | int | `4` | Max nesting depth |
| `max_function_lines` | int | `50` | Max lines per function |
| `max_parameters` | int | `5` | Max function parameters |
| `max_line_length` | int | `120` | Max characters per line |
| `max_file_lines` | int | `500` | Max lines per file |
| `ignore_patterns` | list | `["__pycache__", ".git", ...]` | Patterns to ignore |
| `ignore_files` | list | `["__init__.py", "setup.py"]` | Files to ignore |
| `ai_enabled` | bool | `False` | Enable AI features |
| `ai_model` | str | `"claude-sonnet-4-20250514"` | AI model to use |

## Using Config Object

### Basic Configuration

```python
from paila import Reviewer, Config

config = Config(
    analyzers=["security", "complexity"],
    max_complexity=8,
    max_nesting_depth=3,
)

reviewer = Reviewer(config=config)
```

### Preset Configurations

```python
from paila import Reviewer, Config

# Strict mode - lower thresholds, catches more issues
reviewer = Reviewer(config=Config.strict())

# Relaxed mode - higher thresholds, fewer false positives
reviewer = Reviewer(config=Config.relaxed())

# Security only - just security checks
reviewer = Reviewer(config=Config.security_only())
```

### Custom Ignore Patterns

```python
config = Config(
    ignore_patterns=[
        "__pycache__",
        ".git",
        "node_modules",
        "venv",
        "migrations",
        "*.generated.py",
    ],
    ignore_files=[
        "__init__.py",
        "setup.py",
        "conftest.py",
    ],
)
```

## Configuration File

Create a `.paila.toml` file in your project root:

```toml
[paila]
# Analyzers to enable
analyzers = ["complexity", "security", "smells"]

# Minimum severity to report
min_severity = "info"

# Complexity thresholds
max_complexity = 10
max_nesting_depth = 4
max_function_lines = 50
max_parameters = 5
max_line_length = 120
max_file_lines = 500

# Patterns to ignore
ignore_patterns = [
    "__pycache__",
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
    "*.egg-info",
]

# Specific files to ignore
ignore_files = [
    "__init__.py",
    "setup.py",
    "conftest.py",
]

# AI settings (optional)
ai_enabled = false
ai_model = "claude-sonnet-4-20250514"
# ai_api_key = "your-key"  # Or use ANTHROPIC_API_KEY env var
```

### Generate Config File

```bash
paila init
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | API key for Claude AI |
| `OPENAI_API_KEY` | API key for OpenAI |
| `PAILA_CONFIG` | Path to config file |

## Severity Levels

```python
from paila.models import Severity

# Filter by severity
config = Config(min_severity=Severity.MEDIUM)  # Ignore LOW and INFO
config = Config(min_severity=Severity.HIGH)    # Only HIGH and CRITICAL
```

Severity levels (from most to least severe):
1. `CRITICAL` - Security vulnerabilities, must fix immediately
2. `HIGH` - Significant issues, fix soon
3. `MEDIUM` - Best practice violations
4. `LOW` - Minor improvements
5. `INFO` - Informational notes

## Per-Analyzer Configuration

Each analyzer respects the global configuration:

```python
config = Config(
    # Affects ComplexityAnalyzer
    max_complexity=10,
    max_nesting_depth=4,
    max_function_lines=50,
    max_parameters=5,
    max_line_length=120,
    max_file_lines=500,

    # Affects all analyzers
    min_severity=Severity.LOW,
)
```

## Programmatic Configuration

```python
from paila import Config

# Start with defaults
config = Config()

# Modify settings
config.max_complexity = 15
config.analyzers = ["security"]
config.ignore_patterns.append("tests/")

# Use with reviewer
reviewer = Reviewer(config=config)
```
