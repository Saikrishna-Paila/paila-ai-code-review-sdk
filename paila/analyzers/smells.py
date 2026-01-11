"""
Code Smell Analyzer
===================

Detects code smells and anti-patterns:
- Missing docstrings
- Magic numbers
- Empty except blocks
- TODO/FIXME comments
- Unused imports/variables
- Star imports
"""

import ast
import re
from typing import List, Optional, Set, Dict

from .base import BaseAnalyzer
from ..models import Issue, Severity


class SmellAnalyzer(BaseAnalyzer):
    """
    Analyzes code for code smells and anti-patterns.

    Detects:
    - MISSING_DOCSTRING: Functions/classes without docstrings
    - MAGIC_NUMBER: Unexplained numeric constants
    - EMPTY_EXCEPT: Empty except blocks
    - BARE_EXCEPT: Bare except without exception type
    - TODO_COMMENT: TODO/FIXME comments
    - UNUSED_IMPORT: Imports that are never used
    - STAR_IMPORT: from x import *
    - UNUSED_VARIABLE: Variables that are assigned but never used
    - COMMENTED_CODE: Commented out code blocks
    """

    name = "smells"
    description = "Detects code smells and anti-patterns"

    # Magic numbers to ignore (common acceptable values)
    ALLOWED_MAGIC_NUMBERS = {0, 1, 2, -1, 100, 1000, 0.0, 1.0, 0.5}

    def analyze(
        self,
        code: str,
        file_path: str,
        tree: Optional[ast.AST] = None
    ) -> List[Issue]:
        """Analyze code for code smells."""
        issues = []

        # Parse code if tree not provided
        if tree is None:
            tree = self.parse_code(code)

        if tree is None:
            return issues

        # Run all smell detectors
        issues.extend(self._check_missing_docstrings(code, file_path, tree))
        issues.extend(self._check_magic_numbers(code, file_path, tree))
        issues.extend(self._check_except_blocks(code, file_path, tree))
        issues.extend(self._check_todo_comments(code, file_path))
        issues.extend(self._check_star_imports(code, file_path, tree))
        issues.extend(self._check_unused_imports(code, file_path, tree))
        issues.extend(self._check_unused_variables(code, file_path, tree))
        issues.extend(self._check_commented_code(code, file_path))
        issues.extend(self._check_mutable_defaults(code, file_path, tree))
        issues.extend(self._check_print_statements(code, file_path, tree))

        return issues

    def _check_missing_docstrings(
        self,
        code: str,
        file_path: str,
        tree: ast.AST
    ) -> List[Issue]:
        """Check for missing docstrings in functions and classes."""
        issues = []

        for node in ast.walk(tree):
            # Check functions
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Skip private/magic methods
                if node.name.startswith("_"):
                    continue

                if not self._has_docstring(node):
                    issues.append(Issue(
                        type="missing_docstring",
                        severity=Severity.INFO,
                        file=file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        message=f"Function '{node.name}' is missing a docstring",
                        code=f"def {node.name}(...):",
                        suggestion="Add a docstring describing what this function does",
                        rule="smells/missing-docstring",
                        metadata={"type": "function", "name": node.name}
                    ))

            # Check classes
            elif isinstance(node, ast.ClassDef):
                if not self._has_docstring(node):
                    issues.append(Issue(
                        type="missing_docstring",
                        severity=Severity.INFO,
                        file=file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        message=f"Class '{node.name}' is missing a docstring",
                        code=f"class {node.name}:",
                        suggestion="Add a docstring describing what this class represents",
                        rule="smells/missing-docstring",
                        metadata={"type": "class", "name": node.name}
                    ))

        return issues

    def _check_magic_numbers(
        self,
        code: str,
        file_path: str,
        tree: ast.AST
    ) -> List[Issue]:
        """Check for magic numbers (unexplained numeric constants)."""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                value = node.value

                # Skip allowed values
                if value in self.ALLOWED_MAGIC_NUMBERS:
                    continue

                # Skip if it's a simple assignment (defining a constant)
                parent = self._get_parent(tree, node)
                if isinstance(parent, ast.Assign):
                    # Check if assigning to an UPPERCASE name (constant convention)
                    if (parent.targets and isinstance(parent.targets[0], ast.Name) and
                            parent.targets[0].id.isupper()):
                        continue

                # Skip if in a return statement returning simple values
                if isinstance(parent, ast.Return):
                    continue

                # Skip string indices and small positive integers in context
                if isinstance(value, int) and 0 <= value <= 10:
                    # Skip array indices and slice values
                    if isinstance(parent, (ast.Subscript, ast.Slice)):
                        continue

                line_content = self.get_code_line(code, node.lineno)

                # Skip if it's in a constant definition
                if re.match(r'^[A-Z_]+\s*=', line_content.strip()):
                    continue

                issues.append(Issue(
                    type="magic_number",
                    severity=Severity.LOW,
                    file=file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    message=f"Magic number: {value}",
                    code=line_content,
                    suggestion=f"Define a named constant: MEANINGFUL_NAME = {value}",
                    rule="smells/magic-number",
                    metadata={"value": value}
                ))

        return issues

    def _check_except_blocks(
        self,
        code: str,
        file_path: str,
        tree: ast.AST
    ) -> List[Issue]:
        """Check for problematic except blocks."""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                # Check for bare except (except:)
                if node.type is None:
                    issues.append(Issue(
                        type="bare_except",
                        severity=Severity.MEDIUM,
                        file=file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        message="Bare except clause catches all exceptions including KeyboardInterrupt and SystemExit",
                        code=self.get_code_line(code, node.lineno),
                        suggestion="Specify exception type: except Exception: or more specific",
                        rule="smells/bare-except",
                    ))

                # Check for empty except (except: pass)
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    issues.append(Issue(
                        type="empty_except",
                        severity=Severity.MEDIUM,
                        file=file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        message="Empty except block silently ignores errors",
                        code=self.get_code_line(code, node.lineno),
                        suggestion="Log the error or handle it appropriately",
                        rule="smells/empty-except",
                    ))

                # Check for except Exception as e with just pass
                if (len(node.body) == 1 and isinstance(node.body[0], ast.Pass) and
                        node.name is not None):
                    # Already caught by empty_except, but add note about unused variable
                    pass

        return issues

    def _check_todo_comments(self, code: str, file_path: str) -> List[Issue]:
        """Check for TODO/FIXME/HACK comments."""
        issues = []
        patterns = [
            (r'#\s*TODO\s*:?\s*(.*)', "TODO"),
            (r'#\s*FIXME\s*:?\s*(.*)', "FIXME"),
            (r'#\s*HACK\s*:?\s*(.*)', "HACK"),
            (r'#\s*XXX\s*:?\s*(.*)', "XXX"),
            (r'#\s*BUG\s*:?\s*(.*)', "BUG"),
        ]

        for i, line in enumerate(code.split("\n"), 1):
            for pattern, todo_type in patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    comment = match.group(1).strip() if match.group(1) else ""
                    issues.append(Issue(
                        type="todo_comment",
                        severity=Severity.INFO,
                        file=file_path,
                        line=i,
                        column=match.start(),
                        message=f"{todo_type} comment found" + (f": {comment[:50]}" if comment else ""),
                        code=line.strip(),
                        suggestion="Address this comment or create a ticket to track it",
                        rule="smells/todo-comment",
                        metadata={"todo_type": todo_type, "comment": comment}
                    ))
                    break

        return issues

    def _check_star_imports(
        self,
        code: str,
        file_path: str,
        tree: ast.AST
    ) -> List[Issue]:
        """Check for star imports (from x import *)."""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name == "*":
                        module = node.module or ""
                        issues.append(Issue(
                            type="star_import",
                            severity=Severity.LOW,
                            file=file_path,
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Star import from '{module}'",
                            code=f"from {module} import *",
                            suggestion="Import specific names: from module import name1, name2",
                            rule="smells/star-import",
                            metadata={"module": module}
                        ))

        return issues

    def _check_unused_imports(
        self,
        code: str,
        file_path: str,
        tree: ast.AST
    ) -> List[Issue]:
        """Check for unused imports."""
        issues = []

        # Collect all imports
        imports: Dict[str, int] = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname or alias.name.split(".")[0]
                    imports[name] = node.lineno

            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name != "*":
                        name = alias.asname or alias.name
                        imports[name] = node.lineno

        # Collect all names used in the code
        used_names: Set[str] = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                # Get the root name
                current = node
                while isinstance(current, ast.Attribute):
                    current = current.value
                if isinstance(current, ast.Name):
                    used_names.add(current.id)

        # Find unused imports
        for name, line in imports.items():
            if name not in used_names:
                # Skip common false positives
                if name in {"TYPE_CHECKING", "annotations", "__future__"}:
                    continue

                issues.append(Issue(
                    type="unused_import",
                    severity=Severity.LOW,
                    file=file_path,
                    line=line,
                    column=0,
                    message=f"Unused import: '{name}'",
                    code=self.get_code_line(code, line),
                    suggestion=f"Remove the unused import '{name}'",
                    rule="smells/unused-import",
                    metadata={"name": name}
                ))

        return issues

    def _check_unused_variables(
        self,
        code: str,
        file_path: str,
        tree: ast.AST
    ) -> List[Issue]:
        """Check for unused variables."""
        issues = []

        # This is a simplified check - tracks assignments and uses
        # A full implementation would need proper scope analysis

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                assigned: Dict[str, int] = {}
                used: Set[str] = set()

                for child in ast.walk(node):
                    # Track assignments
                    if isinstance(child, ast.Assign):
                        for target in child.targets:
                            if isinstance(target, ast.Name):
                                # Skip if name starts with _
                                if not target.id.startswith("_"):
                                    assigned[target.id] = target.lineno

                    # Track uses (load context)
                    elif isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                        used.add(child.id)

                # Report unused variables
                for name, line in assigned.items():
                    if name not in used:
                        issues.append(Issue(
                            type="unused_variable",
                            severity=Severity.LOW,
                            file=file_path,
                            line=line,
                            column=0,
                            message=f"Variable '{name}' is assigned but never used",
                            code=self.get_code_line(code, line),
                            suggestion=f"Remove the variable or prefix with underscore: _{name}",
                            rule="smells/unused-variable",
                            metadata={"name": name, "function": node.name}
                        ))

        return issues

    def _check_commented_code(self, code: str, file_path: str) -> List[Issue]:
        """Check for commented out code blocks."""
        issues = []
        lines = code.split("\n")

        # Patterns that suggest commented code (not regular comments)
        code_patterns = [
            r'#\s*(def\s+\w+|class\s+\w+)',  # Commented function/class
            r'#\s*(if\s+|for\s+|while\s+|return\s+)',  # Commented control flow
            r'#\s*\w+\s*=\s*',  # Commented assignment
            r'#\s*(import\s+|from\s+\w+\s+import)',  # Commented import
        ]

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Skip empty lines and regular comments
            if not stripped.startswith("#"):
                continue

            # Skip docstring-like comments and short comments
            if len(stripped) < 10:
                continue

            for pattern in code_patterns:
                if re.match(pattern, stripped):
                    issues.append(Issue(
                        type="commented_code",
                        severity=Severity.INFO,
                        file=file_path,
                        line=i,
                        column=0,
                        message="Commented out code",
                        code=stripped[:60] + "..." if len(stripped) > 60 else stripped,
                        suggestion="Remove commented code or use version control to track history",
                        rule="smells/commented-code",
                    ))
                    break

        return issues

    def _check_mutable_defaults(
        self,
        code: str,
        file_path: str,
        tree: ast.AST
    ) -> List[Issue]:
        """Check for mutable default arguments."""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for default in node.args.defaults + node.args.kw_defaults:
                    if default is None:
                        continue

                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        issues.append(Issue(
                            type="mutable_default",
                            severity=Severity.MEDIUM,
                            file=file_path,
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Mutable default argument in function '{node.name}'",
                            code=f"def {node.name}(...):",
                            suggestion="Use None as default and initialize inside function: if arg is None: arg = []",
                            rule="smells/mutable-default",
                            metadata={"function": node.name}
                        ))
                        break

        return issues

    def _check_print_statements(
        self,
        code: str,
        file_path: str,
        tree: ast.AST
    ) -> List[Issue]:
        """Check for print statements (potential debug code)."""
        issues = []

        # Skip test files
        if "test" in file_path.lower():
            return issues

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "print":
                    issues.append(Issue(
                        type="print_statement",
                        severity=Severity.INFO,
                        file=file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        message="print() statement found (possible debug code)",
                        code=self.get_code_line(code, node.lineno),
                        suggestion="Use logging instead of print for production code",
                        rule="smells/print-statement",
                    ))

        return issues

    # Helper methods
    def _has_docstring(self, node) -> bool:
        """Check if a function or class has a docstring."""
        if node.body:
            first_stmt = node.body[0]
            if isinstance(first_stmt, ast.Expr):
                if isinstance(first_stmt.value, ast.Constant):
                    return isinstance(first_stmt.value.value, str)
        return False

    def _get_parent(self, tree: ast.AST, node: ast.AST) -> Optional[ast.AST]:
        """Get parent node of a given node."""
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                if child is node:
                    return parent
        return None
