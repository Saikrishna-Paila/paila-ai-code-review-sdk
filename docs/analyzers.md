# Analyzers

Paila SDK includes three built-in analyzers that detect different types of issues.

## ComplexityAnalyzer

Detects code that is too complex and hard to maintain.

### Issues Detected

| Issue Type | Severity | Description |
|------------|----------|-------------|
| `high_complexity` | MEDIUM/HIGH | Cyclomatic complexity exceeds threshold |
| `deep_nesting` | MEDIUM | Too many nested blocks |
| `long_function` | LOW | Function has too many lines |
| `too_many_params` | LOW | Function has too many parameters |
| `long_line` | INFO | Line exceeds character limit |
| `large_file` | LOW | File has too many lines |
| `god_class` | MEDIUM | Class has too many methods |

### Configuration

```python
from paila import Config

config = Config(
    max_complexity=10,      # Default: 10
    max_nesting_depth=4,    # Default: 4
    max_function_lines=50,  # Default: 50
    max_parameters=5,       # Default: 5
    max_line_length=120,    # Default: 120
    max_file_lines=500,     # Default: 500
)
```

### Examples

```python
# HIGH COMPLEXITY - Too many decision points
def process(data):
    if data:
        if data.valid:
            for item in data.items:
                if item.active:
                    if item.type == "A":
                        # ...
                    elif item.type == "B":
                        # ...

# DEEP NESTING - Too many levels
def nested():
    if a:
        if b:
            if c:
                if d:
                    if e:  # Too deep!
                        pass

# TOO MANY PARAMS
def configure(a, b, c, d, e, f, g, h):  # 8 parameters!
    pass
```

---

## SecurityAnalyzer

Detects security vulnerabilities and unsafe code patterns.

### Issues Detected

| Issue Type | Severity | Description |
|------------|----------|-------------|
| `sql_injection` | CRITICAL | SQL query built with user input |
| `command_injection` | CRITICAL | Shell command with user input |
| `hardcoded_secret` | HIGH | Passwords/keys in code |
| `eval_usage` | HIGH | Use of eval() or exec() |
| `pickle_usage` | MEDIUM | Unsafe pickle deserialization |
| `insecure_hash` | MEDIUM | MD5/SHA1 for security |
| `path_traversal` | HIGH | Unvalidated file paths |
| `insecure_random` | LOW | random module for security |

### Examples

```python
# SQL INJECTION - CRITICAL
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"  # Dangerous!
    # Fix: Use parameterized queries
    # cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# COMMAND INJECTION - CRITICAL
import os
def run(cmd):
    os.system("ls " + cmd)  # Dangerous!
    # Fix: Use subprocess with list arguments
    # subprocess.run(["ls", cmd], check=True)

# HARDCODED SECRET - HIGH
password = "secret123"  # Don't hardcode!
api_key = "sk-1234567890abcdef"
# Fix: Use environment variables
# password = os.environ.get("DB_PASSWORD")

# EVAL USAGE - HIGH
def calculate(expr):
    return eval(expr)  # Never eval user input!
    # Fix: Use ast.literal_eval for safe evaluation

# PICKLE USAGE - MEDIUM
import pickle
def load(data):
    return pickle.loads(data)  # Unsafe with untrusted data!
    # Fix: Use JSON or other safe formats
```

---

## SmellAnalyzer

Detects code smells and anti-patterns.

### Issues Detected

| Issue Type | Severity | Description |
|------------|----------|-------------|
| `missing_docstring` | INFO | Function/class without docstring |
| `magic_number` | LOW | Unexplained numeric constant |
| `empty_except` | MEDIUM | Except block with just pass |
| `bare_except` | MEDIUM | Except without exception type |
| `todo_comment` | INFO | TODO/FIXME comments |
| `star_import` | LOW | from x import * |
| `unused_import` | LOW | Import never used |
| `unused_variable` | LOW | Variable assigned but not used |
| `commented_code` | INFO | Commented out code |
| `mutable_default` | MEDIUM | Mutable default argument |
| `print_statement` | INFO | print() in production code |

### Examples

```python
# MISSING DOCSTRING
def calculate(x):  # Add a docstring!
    return x * 2

# MAGIC NUMBER
def price(qty):
    return qty * 19.99  # What is 19.99?
    # Fix: UNIT_PRICE = 19.99

# EMPTY EXCEPT - Silently ignores errors
try:
    risky()
except:
    pass  # Bad! At least log the error

# BARE EXCEPT - Catches everything
try:
    risky()
except:  # Catches KeyboardInterrupt too!
    handle()
# Fix: except Exception:

# MUTABLE DEFAULT - Common bug source
def append(item, items=[]):  # Bug!
    items.append(item)
    return items
# Fix: def append(item, items=None):
#          if items is None: items = []

# STAR IMPORT - Pollutes namespace
from os import *  # Don't do this!
# Fix: from os import path, getcwd

# TODO COMMENT - Track these!
# TODO: fix this later
# FIXME: this is broken
```

---

## Enabling/Disabling Analyzers

```python
from paila import Reviewer, Config

# All analyzers (default)
config = Config(analyzers=["complexity", "security", "smells"])

# Security only
config = Config(analyzers=["security"])

# Multiple specific
config = Config(analyzers=["security", "complexity"])
```

## Custom Analyzers

Create your own analyzer:

```python
from paila.analyzers import BaseAnalyzer
from paila.models import Issue, Severity

class MyAnalyzer(BaseAnalyzer):
    name = "my_analyzer"
    description = "My custom checks"

    def analyze(self, code, file_path, tree=None):
        issues = []

        # Your analysis logic here
        if "debug" in code.lower():
            issues.append(Issue(
                type="debug_code",
                severity=Severity.LOW,
                file=file_path,
                line=1,
                column=0,
                message="Debug code found",
                suggestion="Remove debug code before production",
                rule="custom/debug-code",
            ))

        return issues

# Use it
reviewer = Reviewer(custom_analyzers=[MyAnalyzer()])
```

See [Custom Rules](custom-rules.md) for more details.
