"""
Security Analyzer
=================

Detects security vulnerabilities including:
- SQL Injection
- Command Injection
- XSS vulnerabilities
- Hardcoded secrets
- Insecure functions
- Path traversal
"""

import ast
import re
from typing import List, Optional, Set

from .base import BaseAnalyzer
from ..models import Issue, Severity


class SecurityAnalyzer(BaseAnalyzer):
    """
    Analyzes code for security vulnerabilities.

    Detects:
    - SQL_INJECTION: SQL queries built with string concatenation
    - COMMAND_INJECTION: Shell commands with user input
    - HARDCODED_SECRET: Passwords, API keys, tokens in code
    - EVAL_USAGE: Use of eval() or exec()
    - PICKLE_USAGE: Use of pickle with untrusted data
    - INSECURE_HASH: Use of MD5/SHA1 for security
    - PATH_TRAVERSAL: File paths with user input
    - INSECURE_RANDOM: Using random for security purposes
    """

    name = "security"
    description = "Detects security vulnerabilities"

    # Patterns for hardcoded secrets
    SECRET_PATTERNS = [
        (r'password\s*=\s*["\'][^"\']+["\']', "hardcoded password"),
        (r'passwd\s*=\s*["\'][^"\']+["\']', "hardcoded password"),
        (r'pwd\s*=\s*["\'][^"\']+["\']', "hardcoded password"),
        (r'secret\s*=\s*["\'][^"\']+["\']', "hardcoded secret"),
        (r'api_key\s*=\s*["\'][^"\']+["\']', "hardcoded API key"),
        (r'apikey\s*=\s*["\'][^"\']+["\']', "hardcoded API key"),
        (r'token\s*=\s*["\'][^"\']+["\']', "hardcoded token"),
        (r'auth_token\s*=\s*["\'][^"\']+["\']', "hardcoded auth token"),
        (r'access_key\s*=\s*["\'][^"\']+["\']', "hardcoded access key"),
        (r'private_key\s*=\s*["\'][^"\']+["\']', "hardcoded private key"),
    ]

    # SQL keywords for injection detection
    SQL_KEYWORDS = {
        "select", "insert", "update", "delete", "drop", "create",
        "alter", "truncate", "exec", "execute", "union", "where",
        "from", "into", "values", "set", "order", "group", "having"
    }

    # Dangerous functions
    DANGEROUS_FUNCTIONS = {
        "eval": ("EVAL_USAGE", "Use of eval() can execute arbitrary code"),
        "exec": ("EVAL_USAGE", "Use of exec() can execute arbitrary code"),
        "compile": ("EVAL_USAGE", "compile() with exec can execute arbitrary code"),
    }

    # Command execution functions
    COMMAND_FUNCTIONS = {
        "os.system",
        "os.popen",
        "os.popen2",
        "os.popen3",
        "os.popen4",
        "subprocess.call",
        "subprocess.run",
        "subprocess.Popen",
        "commands.getoutput",
        "commands.getstatusoutput",
    }

    # Insecure hash algorithms
    INSECURE_HASHES = {"md5", "sha1", "sha"}

    def analyze(
        self,
        code: str,
        file_path: str,
        tree: Optional[ast.AST] = None
    ) -> List[Issue]:
        """Analyze code for security vulnerabilities."""
        issues = []

        # Parse code if tree not provided
        if tree is None:
            tree = self.parse_code(code)

        if tree is None:
            return issues

        # Check for various vulnerabilities
        issues.extend(self._check_sql_injection(code, file_path, tree))
        issues.extend(self._check_command_injection(code, file_path, tree))
        issues.extend(self._check_hardcoded_secrets(code, file_path))
        issues.extend(self._check_dangerous_functions(code, file_path, tree))
        issues.extend(self._check_insecure_hash(code, file_path, tree))
        issues.extend(self._check_pickle_usage(code, file_path, tree))
        issues.extend(self._check_insecure_random(code, file_path, tree))
        issues.extend(self._check_path_traversal(code, file_path, tree))

        return issues

    def _check_sql_injection(
        self,
        code: str,
        file_path: str,
        tree: ast.AST
    ) -> List[Issue]:
        """Check for SQL injection vulnerabilities."""
        issues = []

        for node in ast.walk(tree):
            # Check for string concatenation with SQL keywords
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
                sql_string = self._extract_sql_pattern(node)
                if sql_string:
                    line = node.lineno
                    issues.append(Issue(
                        type="sql_injection",
                        severity=Severity.CRITICAL,
                        file=file_path,
                        line=line,
                        column=node.col_offset,
                        message="Potential SQL injection: SQL query built with string concatenation",
                        code=self.get_code_line(code, line),
                        suggestion="Use parameterized queries: cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))",
                        rule="security/sql-injection",
                        metadata={"pattern": "string_concat"}
                    ))

            # Check for f-strings with SQL
            if isinstance(node, ast.JoinedStr):
                fstring_content = self._get_fstring_content(node)
                if any(kw in fstring_content.lower() for kw in self.SQL_KEYWORDS):
                    issues.append(Issue(
                        type="sql_injection",
                        severity=Severity.CRITICAL,
                        file=file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        message="Potential SQL injection: SQL query built with f-string",
                        code=self.get_code_line(code, node.lineno),
                        suggestion="Use parameterized queries instead of f-strings for SQL",
                        rule="security/sql-injection",
                        metadata={"pattern": "fstring"}
                    ))

            # Check for format strings with SQL
            if isinstance(node, ast.Call):
                if self._is_format_call(node):
                    format_str = self._get_format_string(node)
                    if format_str and any(kw in format_str.lower() for kw in self.SQL_KEYWORDS):
                        issues.append(Issue(
                            type="sql_injection",
                            severity=Severity.CRITICAL,
                            file=file_path,
                            line=node.lineno,
                            column=node.col_offset,
                            message="Potential SQL injection: SQL query built with .format()",
                            code=self.get_code_line(code, node.lineno),
                            suggestion="Use parameterized queries instead of string formatting",
                            rule="security/sql-injection",
                            metadata={"pattern": "format"}
                        ))

        return issues

    def _check_command_injection(
        self,
        code: str,
        file_path: str,
        tree: ast.AST
    ) -> List[Issue]:
        """Check for command injection vulnerabilities."""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = self._get_full_function_name(node.func)

                if func_name in self.COMMAND_FUNCTIONS:
                    # Check if shell=True is used
                    shell_true = any(
                        isinstance(kw.value, ast.Constant) and kw.value.value is True
                        for kw in node.keywords
                        if kw.arg == "shell"
                    )

                    # Check if command includes variables
                    has_variable_input = self._has_variable_input(node)

                    if shell_true or has_variable_input:
                        severity = Severity.CRITICAL if shell_true else Severity.HIGH
                        issues.append(Issue(
                            type="command_injection",
                            severity=severity,
                            file=file_path,
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Potential command injection in {func_name}()" +
                                    (" with shell=True" if shell_true else ""),
                            code=self.get_code_line(code, node.lineno),
                            suggestion="Avoid shell=True and use a list of arguments. Sanitize all user input.",
                            rule="security/command-injection",
                            metadata={"function": func_name, "shell_true": shell_true}
                        ))

        return issues

    def _check_hardcoded_secrets(self, code: str, file_path: str) -> List[Issue]:
        """Check for hardcoded secrets in code."""
        issues = []

        for i, line in enumerate(code.split("\n"), 1):
            # Skip comments
            if line.strip().startswith("#"):
                continue

            for pattern, description in self.SECRET_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    # Skip if it's a placeholder/example
                    if any(placeholder in line.lower() for placeholder in
                           ["example", "xxx", "your_", "changeme", "placeholder", "<", ">"]):
                        continue

                    issues.append(Issue(
                        type="hardcoded_secret",
                        severity=Severity.HIGH,
                        file=file_path,
                        line=i,
                        column=0,
                        message=f"Potential {description} found",
                        code=self._mask_secret(line.strip()),
                        suggestion="Use environment variables or a secrets manager instead of hardcoding secrets",
                        rule="security/hardcoded-secret",
                        metadata={"secret_type": description}
                    ))
                    break  # One issue per line

        return issues

    def _check_dangerous_functions(
        self,
        code: str,
        file_path: str,
        tree: ast.AST
    ) -> List[Issue]:
        """Check for dangerous function usage."""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = self._get_function_name(node.func)

                if func_name in self.DANGEROUS_FUNCTIONS:
                    issue_type, message = self.DANGEROUS_FUNCTIONS[func_name]
                    issues.append(Issue(
                        type=issue_type.lower(),
                        severity=Severity.HIGH,
                        file=file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        message=message,
                        code=self.get_code_line(code, node.lineno),
                        suggestion=f"Avoid using {func_name}() with untrusted input. Consider safer alternatives.",
                        rule=f"security/{issue_type.lower().replace('_', '-')}",
                        metadata={"function": func_name}
                    ))

        return issues

    def _check_insecure_hash(
        self,
        code: str,
        file_path: str,
        tree: ast.AST
    ) -> List[Issue]:
        """Check for use of insecure hash algorithms."""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = self._get_full_function_name(node.func)

                # Check hashlib.md5(), hashlib.sha1()
                if func_name:
                    for insecure in self.INSECURE_HASHES:
                        if f"hashlib.{insecure}" in func_name or f".{insecure}(" in func_name:
                            issues.append(Issue(
                                type="insecure_hash",
                                severity=Severity.MEDIUM,
                                file=file_path,
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Use of weak hash algorithm: {insecure.upper()}",
                                code=self.get_code_line(code, node.lineno),
                                suggestion="Use SHA-256 or stronger: hashlib.sha256()",
                                rule="security/insecure-hash",
                                metadata={"algorithm": insecure}
                            ))
                            break

        return issues

    def _check_pickle_usage(
        self,
        code: str,
        file_path: str,
        tree: ast.AST
    ) -> List[Issue]:
        """Check for unsafe pickle usage."""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = self._get_full_function_name(node.func)

                if func_name and "pickle.load" in func_name:
                    issues.append(Issue(
                        type="pickle_usage",
                        severity=Severity.HIGH,
                        file=file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        message="Use of pickle.load() can execute arbitrary code",
                        code=self.get_code_line(code, node.lineno),
                        suggestion="Never unpickle data from untrusted sources. Use JSON or other safe formats.",
                        rule="security/pickle-usage",
                        metadata={"function": func_name}
                    ))

        return issues

    def _check_insecure_random(
        self,
        code: str,
        file_path: str,
        tree: ast.AST
    ) -> List[Issue]:
        """Check for use of insecure random for security purposes."""
        issues = []

        # Track if random is imported
        uses_random = "import random" in code or "from random" in code

        if not uses_random:
            return issues

        # Look for random usage in security context
        security_contexts = ["password", "token", "secret", "key", "auth", "session", "csrf"]

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = self._get_full_function_name(node.func)

                if func_name and func_name.startswith("random."):
                    # Check if it's in a security context
                    line = self.get_code_line(code, node.lineno).lower()
                    if any(ctx in line for ctx in security_contexts):
                        issues.append(Issue(
                            type="insecure_random",
                            severity=Severity.HIGH,
                            file=file_path,
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Using {func_name} for security-sensitive operation",
                            code=self.get_code_line(code, node.lineno),
                            suggestion="Use secrets module for cryptographic random: secrets.token_hex(), secrets.token_urlsafe()",
                            rule="security/insecure-random",
                            metadata={"function": func_name}
                        ))

        return issues

    def _check_path_traversal(
        self,
        code: str,
        file_path: str,
        tree: ast.AST
    ) -> List[Issue]:
        """Check for path traversal vulnerabilities."""
        issues = []

        file_operations = {"open", "read", "write", "os.path.join"}

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = self._get_function_name(node.func)

                if func_name in file_operations:
                    # Check if path includes string concatenation or f-string
                    if node.args:
                        first_arg = node.args[0]
                        if isinstance(first_arg, (ast.BinOp, ast.JoinedStr)):
                            issues.append(Issue(
                                type="path_traversal",
                                severity=Severity.MEDIUM,
                                file=file_path,
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Potential path traversal in {func_name}()",
                                code=self.get_code_line(code, node.lineno),
                                suggestion="Validate and sanitize file paths. Use os.path.abspath() and check against allowed directories.",
                                rule="security/path-traversal",
                                metadata={"function": func_name}
                            ))

        return issues

    # Helper methods
    def _extract_sql_pattern(self, node: ast.BinOp) -> Optional[str]:
        """Extract SQL pattern from binary operation."""
        def get_string_value(n):
            if isinstance(n, ast.Constant) and isinstance(n.value, str):
                return n.value
            return ""

        left_str = get_string_value(node.left)
        right_str = get_string_value(node.right)
        combined = (left_str + right_str).lower()

        if any(kw in combined for kw in self.SQL_KEYWORDS):
            return combined
        return None

    def _get_fstring_content(self, node: ast.JoinedStr) -> str:
        """Extract text content from f-string."""
        parts = []
        for value in node.values:
            if isinstance(value, ast.Constant):
                parts.append(str(value.value))
        return "".join(parts)

    def _is_format_call(self, node: ast.Call) -> bool:
        """Check if call is a .format() method."""
        if isinstance(node.func, ast.Attribute):
            return node.func.attr == "format"
        return False

    def _get_format_string(self, node: ast.Call) -> Optional[str]:
        """Get the format string from a .format() call."""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Constant):
                return str(node.func.value.value)
        return None

    def _get_function_name(self, node) -> str:
        """Get simple function name from call node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return ""

    def _get_full_function_name(self, node) -> str:
        """Get full function name including module."""
        parts = []

        def collect_parts(n):
            if isinstance(n, ast.Name):
                parts.append(n.id)
            elif isinstance(n, ast.Attribute):
                collect_parts(n.value)
                parts.append(n.attr)

        collect_parts(node)
        return ".".join(parts)

    def _has_variable_input(self, node: ast.Call) -> bool:
        """Check if function call has variable input."""
        for arg in node.args:
            if isinstance(arg, (ast.Name, ast.BinOp, ast.JoinedStr, ast.Call)):
                return True
        return False

    def _mask_secret(self, line: str) -> str:
        """Mask potential secrets in code display."""
        # Mask anything between quotes that looks like a secret
        masked = re.sub(
            r'(["\'])([^"\']{4})[^"\']*([^"\']{2})\1',
            r'\1\2****\3\1',
            line
        )
        return masked
