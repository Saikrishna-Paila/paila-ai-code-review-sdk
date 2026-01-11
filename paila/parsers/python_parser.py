"""
Python Parser
=============

Parser for Python source code using the ast module.
"""

import ast
import re
import tokenize
import io
from typing import List, Dict, Any, Optional

from .base import BaseParser, ParsedCode


class PythonParser(BaseParser):
    """
    Parser for Python source code.

    Uses Python's built-in ast module for parsing.
    Provides utilities for extracting functions, classes,
    imports, and other code elements.
    """

    language = "python"
    extensions = [".py", ".pyi"]

    def parse(self, code: str) -> ParsedCode:
        """
        Parse Python source code.

        Args:
            code: Python source code

        Returns:
            ParsedCode with AST tree
        """
        errors = []
        tree = None

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            errors.append(f"SyntaxError at line {e.lineno}: {e.msg}")

        comments = self.extract_comments(code)

        return ParsedCode(
            tree=tree,
            language=self.language,
            errors=errors,
            comments=comments,
        )

    def extract_comments(self, code: str) -> List[Dict[str, Any]]:
        """
        Extract comments from Python code.

        Returns:
            List of comment dictionaries
        """
        comments = []

        try:
            tokens = tokenize.generate_tokens(io.StringIO(code).readline)

            for token in tokens:
                if token.type == tokenize.COMMENT:
                    comments.append({
                        "line": token.start[0],
                        "column": token.start[1],
                        "text": token.string[1:].strip(),  # Remove #
                        "type": "line",
                    })
        except tokenize.TokenizeError:
            # Fallback to regex if tokenization fails
            for i, line in enumerate(code.split("\n"), 1):
                match = re.search(r'#\s*(.*)', line)
                if match:
                    comments.append({
                        "line": i,
                        "column": match.start(),
                        "text": match.group(1),
                        "type": "line",
                    })

        return comments

    def extract_strings(self, code: str) -> List[Dict[str, Any]]:
        """
        Extract string literals from Python code.

        Returns:
            List of string dictionaries
        """
        strings = []

        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    strings.append({
                        "line": node.lineno,
                        "column": node.col_offset,
                        "value": node.value,
                    })
        except SyntaxError:
            pass

        return strings

    def extract_functions(self, code: str) -> List[Dict[str, Any]]:
        """
        Extract function definitions.

        Returns:
            List of function info dictionaries
        """
        functions = []

        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions.append({
                        "name": node.name,
                        "line": node.lineno,
                        "end_line": node.end_lineno,
                        "args": [arg.arg for arg in node.args.args],
                        "decorators": [
                            ast.unparse(d) if hasattr(ast, 'unparse') else str(d)
                            for d in node.decorator_list
                        ],
                        "is_async": isinstance(node, ast.AsyncFunctionDef),
                        "docstring": ast.get_docstring(node),
                    })
        except SyntaxError:
            pass

        return functions

    def extract_classes(self, code: str) -> List[Dict[str, Any]]:
        """
        Extract class definitions.

        Returns:
            List of class info dictionaries
        """
        classes = []

        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = [
                        n.name for n in node.body
                        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                    ]

                    bases = []
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            bases.append(base.id)
                        elif isinstance(base, ast.Attribute):
                            bases.append(ast.unparse(base) if hasattr(ast, 'unparse') else str(base))

                    classes.append({
                        "name": node.name,
                        "line": node.lineno,
                        "end_line": node.end_lineno,
                        "bases": bases,
                        "methods": methods,
                        "docstring": ast.get_docstring(node),
                    })
        except SyntaxError:
            pass

        return classes

    def extract_imports(self, code: str) -> List[Dict[str, Any]]:
        """
        Extract import statements.

        Returns:
            List of import info dictionaries
        """
        imports = []

        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append({
                            "type": "import",
                            "module": alias.name,
                            "alias": alias.asname,
                            "line": node.lineno,
                        })

                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append({
                            "type": "from",
                            "module": module,
                            "name": alias.name,
                            "alias": alias.asname,
                            "line": node.lineno,
                            "level": node.level,  # For relative imports
                        })
        except SyntaxError:
            pass

        return imports

    def extract_variables(self, code: str) -> List[Dict[str, Any]]:
        """
        Extract variable assignments.

        Returns:
            List of variable info dictionaries
        """
        variables = []

        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            variables.append({
                                "name": target.id,
                                "line": node.lineno,
                                "is_constant": target.id.isupper(),
                            })

                elif isinstance(node, ast.AnnAssign):
                    if isinstance(node.target, ast.Name):
                        variables.append({
                            "name": node.target.id,
                            "line": node.lineno,
                            "is_constant": node.target.id.isupper(),
                            "has_annotation": True,
                        })
        except SyntaxError:
            pass

        return variables

    def get_code_structure(self, code: str) -> Dict[str, Any]:
        """
        Get complete code structure.

        Returns:
            Dictionary with all extracted elements
        """
        return {
            "functions": self.extract_functions(code),
            "classes": self.extract_classes(code),
            "imports": self.extract_imports(code),
            "variables": self.extract_variables(code),
            "comments": self.extract_comments(code),
            "strings": self.extract_strings(code),
        }

    def count_lines(self, code: str) -> Dict[str, int]:
        """
        Count different types of lines.

        Returns:
            Dictionary with line counts
        """
        lines = code.split("\n")
        total = len(lines)
        blank = sum(1 for line in lines if not line.strip())
        comments = sum(1 for line in lines if line.strip().startswith("#"))
        code_lines = total - blank - comments

        # Count docstring lines (approximate)
        docstring_lines = 0
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
                    docstring = ast.get_docstring(node)
                    if docstring:
                        docstring_lines += docstring.count("\n") + 1
        except SyntaxError:
            pass

        return {
            "total": total,
            "blank": blank,
            "comments": comments,
            "code": code_lines,
            "docstrings": docstring_lines,
        }
