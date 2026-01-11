"""
Complexity Analyzer
===================

Analyzes code complexity including:
- Cyclomatic complexity
- Nesting depth
- Function length
- Parameter count
- Line length
"""

import ast
from typing import List, Optional, Dict, Any

from .base import BaseAnalyzer
from ..models import Issue, Severity


class ComplexityAnalyzer(BaseAnalyzer):
    """
    Analyzes code for complexity issues.

    Detects:
    - HIGH_COMPLEXITY: Functions with high cyclomatic complexity
    - DEEP_NESTING: Deeply nested code blocks
    - LONG_FUNCTION: Functions with too many lines
    - TOO_MANY_PARAMS: Functions with too many parameters
    - LONG_LINE: Lines that are too long
    """

    name = "complexity"
    description = "Analyzes code complexity and maintainability"

    def analyze(
        self,
        code: str,
        file_path: str,
        tree: Optional[ast.AST] = None
    ) -> List[Issue]:
        """Analyze code for complexity issues."""
        issues = []

        # Parse code if tree not provided
        if tree is None:
            tree = self.parse_code(code)

        if tree is None:
            return issues  # Could not parse, skip

        # Analyze each function/method
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                issues.extend(self._analyze_function(node, code, file_path))
            elif isinstance(node, ast.ClassDef):
                issues.extend(self._analyze_class(node, code, file_path))

        # Check line lengths
        issues.extend(self._check_line_lengths(code, file_path))

        # Check file length
        issues.extend(self._check_file_length(code, file_path))

        return issues

    def _analyze_function(
        self,
        node: ast.FunctionDef,
        code: str,
        file_path: str
    ) -> List[Issue]:
        """Analyze a single function for complexity issues."""
        issues = []

        # Calculate cyclomatic complexity
        complexity = self._calculate_complexity(node)
        if complexity > self.config.max_complexity:
            issues.append(Issue(
                type="high_complexity",
                severity=Severity.MEDIUM if complexity <= 15 else Severity.HIGH,
                file=file_path,
                line=node.lineno,
                column=node.col_offset,
                message=f"Function '{node.name}' has cyclomatic complexity of {complexity} (max: {self.config.max_complexity})",
                code=f"def {node.name}({self._get_params_str(node)}):",
                suggestion="Consider breaking this function into smaller, more focused functions",
                rule="complexity/high-complexity",
                metadata={"complexity": complexity, "function": node.name}
            ))

        # Check nesting depth
        nesting = self._calculate_nesting_depth(node)
        if nesting > self.config.max_nesting_depth:
            issues.append(Issue(
                type="deep_nesting",
                severity=Severity.MEDIUM,
                file=file_path,
                line=node.lineno,
                column=node.col_offset,
                message=f"Function '{node.name}' has nesting depth of {nesting} (max: {self.config.max_nesting_depth})",
                code=f"def {node.name}(...):",
                suggestion="Extract nested logic into separate functions or use early returns",
                rule="complexity/deep-nesting",
                metadata={"nesting_depth": nesting, "function": node.name}
            ))

        # Check function length
        func_lines = self._count_function_lines(node)
        if func_lines > self.config.max_function_lines:
            issues.append(Issue(
                type="long_function",
                severity=Severity.LOW,
                file=file_path,
                line=node.lineno,
                column=node.col_offset,
                message=f"Function '{node.name}' has {func_lines} lines (max: {self.config.max_function_lines})",
                code=f"def {node.name}(...):",
                suggestion="Break this function into smaller, single-purpose functions",
                rule="complexity/long-function",
                metadata={"lines": func_lines, "function": node.name}
            ))

        # Check parameter count
        param_count = len(node.args.args) + len(node.args.kwonlyargs)
        if node.args.vararg:
            param_count += 1
        if node.args.kwarg:
            param_count += 1

        if param_count > self.config.max_parameters:
            issues.append(Issue(
                type="too_many_params",
                severity=Severity.LOW,
                file=file_path,
                line=node.lineno,
                column=node.col_offset,
                message=f"Function '{node.name}' has {param_count} parameters (max: {self.config.max_parameters})",
                code=f"def {node.name}({self._get_params_str(node)}):",
                suggestion="Consider using a configuration object or breaking into smaller functions",
                rule="complexity/too-many-params",
                metadata={"param_count": param_count, "function": node.name}
            ))

        return issues

    def _analyze_class(
        self,
        node: ast.ClassDef,
        code: str,
        file_path: str
    ) -> List[Issue]:
        """Analyze a class for complexity issues."""
        issues = []

        # Count methods
        method_count = sum(
            1 for child in node.body
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
        )

        if method_count > 20:  # God class threshold
            issues.append(Issue(
                type="god_class",
                severity=Severity.MEDIUM,
                file=file_path,
                line=node.lineno,
                column=node.col_offset,
                message=f"Class '{node.name}' has {method_count} methods, which may indicate a 'God Class'",
                code=f"class {node.name}:",
                suggestion="Consider splitting this class into smaller, focused classes",
                rule="complexity/god-class",
                metadata={"method_count": method_count, "class": node.name}
            ))

        return issues

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """
        Calculate cyclomatic complexity of a function.

        Complexity = 1 + number of decision points

        Decision points:
        - if/elif
        - for
        - while
        - except
        - with
        - and/or in boolean expressions
        - ternary expressions (a if b else c)
        - comprehension conditions
        """
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            # Control flow
            if isinstance(child, (ast.If, ast.IfExp)):
                complexity += 1
            elif isinstance(child, (ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, (ast.While,)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.With, ast.AsyncWith)):
                complexity += 1
            # Boolean operators (each adds a decision point)
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            # Comprehension conditions
            elif isinstance(child, ast.comprehension):
                complexity += len(child.ifs)
            # Assert statements
            elif isinstance(child, ast.Assert):
                complexity += 1

        return complexity

    def _calculate_nesting_depth(self, node: ast.AST) -> int:
        """Calculate maximum nesting depth."""

        def get_depth(node: ast.AST, current_depth: int = 0) -> int:
            max_depth = current_depth

            # Nodes that increase nesting
            nesting_nodes = (
                ast.If, ast.For, ast.AsyncFor, ast.While,
                ast.With, ast.AsyncWith, ast.Try,
                ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef
            )

            for child in ast.iter_child_nodes(node):
                if isinstance(child, nesting_nodes):
                    child_depth = get_depth(child, current_depth + 1)
                else:
                    child_depth = get_depth(child, current_depth)
                max_depth = max(max_depth, child_depth)

            return max_depth

        return get_depth(node)

    def _count_function_lines(self, node: ast.FunctionDef) -> int:
        """Count lines in a function (excluding docstring)."""
        if node.end_lineno is None:
            return 0

        total_lines = node.end_lineno - node.lineno + 1

        # Subtract docstring lines if present
        if (node.body and isinstance(node.body[0], ast.Expr) and
                isinstance(node.body[0].value, ast.Constant) and
                isinstance(node.body[0].value.value, str)):
            docstring_node = node.body[0]
            if docstring_node.end_lineno:
                docstring_lines = docstring_node.end_lineno - docstring_node.lineno + 1
                total_lines -= docstring_lines

        return total_lines

    def _get_params_str(self, node: ast.FunctionDef) -> str:
        """Get a string representation of function parameters."""
        params = []

        for arg in node.args.args:
            params.append(arg.arg)

        if node.args.vararg:
            params.append(f"*{node.args.vararg.arg}")

        for arg in node.args.kwonlyargs:
            params.append(arg.arg)

        if node.args.kwarg:
            params.append(f"**{node.args.kwarg.arg}")

        if len(params) > 3:
            return ", ".join(params[:3]) + ", ..."

        return ", ".join(params)

    def _check_line_lengths(self, code: str, file_path: str) -> List[Issue]:
        """Check for lines that are too long."""
        issues = []
        max_length = self.config.max_line_length

        for i, line in enumerate(code.split("\n"), 1):
            if len(line) > max_length:
                # Skip if it's a URL or import
                if "http://" in line or "https://" in line:
                    continue
                if line.strip().startswith(("import ", "from ")):
                    continue

                issues.append(Issue(
                    type="long_line",
                    severity=Severity.INFO,
                    file=file_path,
                    line=i,
                    column=max_length,
                    message=f"Line is {len(line)} characters (max: {max_length})",
                    code=line[:80] + "..." if len(line) > 80 else line,
                    suggestion="Break this line into multiple lines for better readability",
                    rule="complexity/long-line",
                    metadata={"length": len(line)}
                ))

        return issues

    def _check_file_length(self, code: str, file_path: str) -> List[Issue]:
        """Check if file is too long."""
        issues = []
        lines = code.split("\n")
        line_count = len(lines)

        if line_count > self.config.max_file_lines:
            issues.append(Issue(
                type="large_file",
                severity=Severity.LOW,
                file=file_path,
                line=1,
                column=0,
                message=f"File has {line_count} lines (max: {self.config.max_file_lines})",
                code="",
                suggestion="Consider splitting this file into multiple modules",
                rule="complexity/large-file",
                metadata={"lines": line_count}
            ))

        return issues

    def calculate_metrics(self, code: str, tree: Optional[ast.AST] = None) -> Dict[str, Any]:
        """
        Calculate complexity metrics for the code.

        Returns:
            Dictionary with complexity metrics
        """
        if tree is None:
            tree = self.parse_code(code)

        if tree is None:
            return {"error": "Could not parse code"}

        complexities = []
        function_count = 0
        class_count = 0

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function_count += 1
                complexities.append(self._calculate_complexity(node))
            elif isinstance(node, ast.ClassDef):
                class_count += 1

        avg_complexity = sum(complexities) / len(complexities) if complexities else 0
        max_complexity = max(complexities) if complexities else 0

        lines = code.split("\n")
        blank_lines = sum(1 for line in lines if not line.strip())
        comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
        code_lines = len(lines) - blank_lines - comment_lines

        return {
            "total_lines": len(lines),
            "code_lines": code_lines,
            "blank_lines": blank_lines,
            "comment_lines": comment_lines,
            "functions": function_count,
            "classes": class_count,
            "avg_complexity": round(avg_complexity, 2),
            "max_complexity": max_complexity,
        }
