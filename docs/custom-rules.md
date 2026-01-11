# Custom Rules

Create your own analyzers and rules to extend Paila SDK.

## Creating a Custom Analyzer

### Basic Structure

```python
from paila.analyzers import BaseAnalyzer
from paila.models import Issue, Severity

class MyAnalyzer(BaseAnalyzer):
    """My custom analyzer."""

    name = "my_analyzer"
    description = "Detects custom issues"

    def analyze(self, code, file_path, tree=None):
        """
        Analyze code and return issues.

        Args:
            code: Source code string
            file_path: Path to the file
            tree: Pre-parsed AST (optional)

        Returns:
            List of Issue objects
        """
        issues = []

        # Parse AST if not provided
        if tree is None:
            tree = self.parse_code(code)

        if tree is None:
            return issues  # Could not parse

        # Your analysis logic here
        # ...

        return issues
```

### Using the Analyzer

```python
from paila import Reviewer

reviewer = Reviewer(custom_analyzers=[MyAnalyzer()])
result = reviewer.review("./src")
```

## Example: Naming Convention Analyzer

```python
import ast
import re
from paila.analyzers import BaseAnalyzer
from paila.models import Issue, Severity


class NamingAnalyzer(BaseAnalyzer):
    """Enforces naming conventions."""

    name = "naming"
    description = "Checks naming conventions"

    # Patterns for different naming styles
    SNAKE_CASE = re.compile(r'^[a-z_][a-z0-9_]*$')
    PASCAL_CASE = re.compile(r'^[A-Z][a-zA-Z0-9]*$')
    UPPER_CASE = re.compile(r'^[A-Z_][A-Z0-9_]*$')

    def analyze(self, code, file_path, tree=None):
        issues = []

        if tree is None:
            tree = self.parse_code(code)
        if tree is None:
            return issues

        for node in ast.walk(tree):
            # Check function names (should be snake_case)
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith('_'):  # Skip private
                    if not self.SNAKE_CASE.match(node.name):
                        issues.append(Issue(
                            type="naming_convention",
                            severity=Severity.LOW,
                            file=file_path,
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Function '{node.name}' should use snake_case",
                            code=f"def {node.name}(...):",
                            suggestion="Rename to snake_case: my_function_name",
                            rule="naming/function-snake-case",
                        ))

            # Check class names (should be PascalCase)
            elif isinstance(node, ast.ClassDef):
                if not self.PASCAL_CASE.match(node.name):
                    issues.append(Issue(
                        type="naming_convention",
                        severity=Severity.LOW,
                        file=file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        message=f"Class '{node.name}' should use PascalCase",
                        code=f"class {node.name}:",
                        suggestion="Rename to PascalCase: MyClassName",
                        rule="naming/class-pascal-case",
                    ))

            # Check constants (module level UPPER_CASE)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        # Assume module-level ALL_CAPS are constants
                        name = target.id
                        if name.isupper() and not self.UPPER_CASE.match(name):
                            issues.append(Issue(
                                type="naming_convention",
                                severity=Severity.INFO,
                                file=file_path,
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Constant '{name}' has invalid format",
                                suggestion="Use UPPER_SNAKE_CASE for constants",
                                rule="naming/constant-upper-case",
                            ))

        return issues
```

## Example: Docstring Format Analyzer

```python
import ast
from paila.analyzers import BaseAnalyzer
from paila.models import Issue, Severity


class DocstringAnalyzer(BaseAnalyzer):
    """Checks docstring format and content."""

    name = "docstring"
    description = "Validates docstring format"

    def analyze(self, code, file_path, tree=None):
        issues = []

        if tree is None:
            tree = self.parse_code(code)
        if tree is None:
            return issues

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                docstring = ast.get_docstring(node)

                if docstring:
                    # Check for Args section
                    if node.args.args and 'Args:' not in docstring:
                        if len(node.args.args) > 1 or \
                           (len(node.args.args) == 1 and node.args.args[0].arg != 'self'):
                            issues.append(Issue(
                                type="docstring_format",
                                severity=Severity.INFO,
                                file=file_path,
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Function '{node.name}' docstring missing Args section",
                                suggestion="Add 'Args:' section documenting parameters",
                                rule="docstring/missing-args",
                            ))

                    # Check for Returns section
                    has_return = any(
                        isinstance(n, ast.Return) and n.value is not None
                        for n in ast.walk(node)
                    )
                    if has_return and 'Returns:' not in docstring:
                        issues.append(Issue(
                            type="docstring_format",
                            severity=Severity.INFO,
                            file=file_path,
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Function '{node.name}' docstring missing Returns section",
                            suggestion="Add 'Returns:' section documenting return value",
                            rule="docstring/missing-returns",
                        ))

        return issues
```

## Example: Import Order Analyzer

```python
import ast
from paila.analyzers import BaseAnalyzer
from paila.models import Issue, Severity


class ImportOrderAnalyzer(BaseAnalyzer):
    """Checks import ordering (stdlib, third-party, local)."""

    name = "import_order"
    description = "Validates import order"

    STDLIB_MODULES = {
        'os', 'sys', 'json', 'typing', 'pathlib', 'collections',
        'datetime', 'functools', 'itertools', 're', 'ast', 'io',
        'abc', 'contextlib', 'dataclasses', 'enum', 'logging',
        # Add more as needed
    }

    def analyze(self, code, file_path, tree=None):
        issues = []

        if tree is None:
            tree = self.parse_code(code)
        if tree is None:
            return issues

        imports = []

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name.split('.')[0]
                    imports.append((node.lineno, 'import', module))

            elif isinstance(node, ast.ImportFrom):
                module = (node.module or '').split('.')[0]
                imports.append((node.lineno, 'from', module))

        # Check order
        last_type = None
        for line, _, module in imports:
            if module in self.STDLIB_MODULES:
                current_type = 'stdlib'
            elif module.startswith('.'):
                current_type = 'local'
            else:
                current_type = 'third_party'

            if last_type and self._is_wrong_order(last_type, current_type):
                issues.append(Issue(
                    type="import_order",
                    severity=Severity.INFO,
                    file=file_path,
                    line=line,
                    column=0,
                    message=f"Import '{module}' is out of order",
                    suggestion="Order: stdlib, third-party, local (separated by blank lines)",
                    rule="imports/wrong-order",
                ))

            last_type = current_type

        return issues

    def _is_wrong_order(self, last, current):
        order = {'stdlib': 0, 'third_party': 1, 'local': 2}
        return order.get(current, 0) < order.get(last, 0)
```

## Using Multiple Custom Analyzers

```python
from paila import Reviewer

reviewer = Reviewer(
    custom_analyzers=[
        NamingAnalyzer(),
        DocstringAnalyzer(),
        ImportOrderAnalyzer(),
    ]
)

result = reviewer.review("./src")
```

## Helper Methods from BaseAnalyzer

```python
class BaseAnalyzer:
    # Parse code into AST
    def parse_code(self, code: str) -> Optional[ast.AST]:
        ...

    # Get a specific line of code
    def get_code_line(self, code: str, line_number: int) -> str:
        ...

    # Get a code snippet
    def get_code_snippet(self, code: str, start_line: int,
                         end_line: int = None, max_lines: int = 5) -> str:
        ...
```

## Best Practices

1. **Use meaningful issue types**: Make them descriptive and consistent
2. **Set appropriate severity**: Don't make everything CRITICAL
3. **Provide suggestions**: Help users fix the issue
4. **Include rule names**: For filtering and documentation
5. **Handle edge cases**: Check for None, empty code, parse failures
6. **Use metadata**: Store extra info for reporting
7. **Test your analyzer**: Write unit tests for different scenarios
