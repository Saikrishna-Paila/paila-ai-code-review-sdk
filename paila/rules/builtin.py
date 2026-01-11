"""
Built-in Rules
==============

Pre-defined rules for common code review checks.
"""

import ast
import re
from typing import List, Optional

from .base import Rule, RuleSet, RuleBuilder
from ..models import Issue, Severity


class SecurityRules(RuleSet):
    """
    Built-in security rules.

    Includes rules for:
    - SQL injection
    - Command injection
    - Hardcoded secrets
    - Dangerous functions
    """

    def __init__(self):
        super().__init__(name="security")
        self._add_rules()

    def _add_rules(self):
        # SQL Injection - String formatting
        self.add(
            RuleBuilder("security/sql-injection-format")
            .name("SQL Injection (String Format)")
            .description("Detects SQL queries built with string formatting")
            .severity(Severity.CRITICAL)
            .category("security")
            .pattern(
                r'["\']SELECT\s.*%s|["\']INSERT\s.*%s|["\']UPDATE\s.*%s|["\']DELETE\s.*%s',
                message="Potential SQL injection via string formatting",
                suggestion="Use parameterized queries instead"
            )
            .tags("sql", "injection", "owasp")
            .build()
        )

        # SQL Injection - f-strings
        self.add(
            RuleBuilder("security/sql-injection-fstring")
            .name("SQL Injection (f-string)")
            .description("Detects SQL queries built with f-strings")
            .severity(Severity.CRITICAL)
            .category("security")
            .pattern(
                r'f["\'](?:SELECT|INSERT|UPDATE|DELETE)\s.*\{',
                message="Potential SQL injection via f-string",
                suggestion="Use parameterized queries instead"
            )
            .tags("sql", "injection", "owasp")
            .build()
        )

        # Command Injection
        self.add(
            RuleBuilder("security/command-injection")
            .name("Command Injection")
            .description("Detects shell commands built with user input")
            .severity(Severity.CRITICAL)
            .category("security")
            .pattern(
                r'os\.system\s*\([^)]*\+|subprocess\.(?:call|run|Popen)\s*\([^)]*shell\s*=\s*True',
                message="Potential command injection vulnerability",
                suggestion="Use subprocess with list arguments instead of shell=True"
            )
            .tags("command", "injection", "owasp")
            .build()
        )

        # Hardcoded passwords
        self.add(
            RuleBuilder("security/hardcoded-password")
            .name("Hardcoded Password")
            .description("Detects hardcoded passwords in code")
            .severity(Severity.HIGH)
            .category("security")
            .pattern(
                r'(?:password|passwd|pwd)\s*=\s*["\'][^"\']+["\']',
                message="Hardcoded password detected",
                suggestion="Use environment variables or a secrets manager"
            )
            .tags("secrets", "credentials")
            .build()
        )

        # Hardcoded API keys
        self.add(
            RuleBuilder("security/hardcoded-api-key")
            .name("Hardcoded API Key")
            .description("Detects hardcoded API keys")
            .severity(Severity.HIGH)
            .category("security")
            .pattern(
                r'(?:api_key|apikey|api_secret|secret_key)\s*=\s*["\'][a-zA-Z0-9_-]{20,}["\']',
                message="Hardcoded API key detected",
                suggestion="Use environment variables or a secrets manager"
            )
            .tags("secrets", "credentials")
            .build()
        )

        # eval() usage
        self.add(
            RuleBuilder("security/eval-usage")
            .name("Eval Usage")
            .description("Detects use of eval() function")
            .severity(Severity.HIGH)
            .category("security")
            .pattern(
                r'\beval\s*\(',
                message="Use of eval() detected - potential code injection",
                suggestion="Use ast.literal_eval() for safe evaluation"
            )
            .tags("dangerous", "injection")
            .build()
        )

        # exec() usage
        self.add(
            RuleBuilder("security/exec-usage")
            .name("Exec Usage")
            .description("Detects use of exec() function")
            .severity(Severity.HIGH)
            .category("security")
            .pattern(
                r'\bexec\s*\(',
                message="Use of exec() detected - potential code injection",
                suggestion="Avoid exec() with dynamic code"
            )
            .tags("dangerous", "injection")
            .build()
        )

        # pickle usage
        self.add(
            RuleBuilder("security/pickle-loads")
            .name("Pickle Loads")
            .description("Detects unsafe pickle deserialization")
            .severity(Severity.MEDIUM)
            .category("security")
            .pattern(
                r'pickle\.loads?\s*\(',
                message="Pickle deserialization is unsafe with untrusted data",
                suggestion="Use JSON or other safe serialization formats"
            )
            .tags("serialization", "unsafe")
            .build()
        )


class ComplexityRules(RuleSet):
    """
    Built-in complexity rules.

    Includes rules for:
    - Function length
    - Parameter count
    - Nesting depth
    """

    def __init__(self, config: Optional[dict] = None):
        super().__init__(name="complexity")
        self.config = config or {}
        self._add_rules()

    def _add_rules(self):
        # Too many parameters
        max_params = self.config.get("max_parameters", 5)

        def check_params(code, file_path, tree):
            issues = []
            if tree is None:
                try:
                    tree = ast.parse(code)
                except SyntaxError:
                    return issues

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    param_count = len(node.args.args)
                    if param_count > max_params:
                        issues.append(Issue(
                            type="too_many_parameters",
                            severity=Severity.LOW,
                            file=file_path,
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Function '{node.name}' has {param_count} parameters (max: {max_params})",
                            suggestion="Consider using a configuration object or breaking into smaller functions",
                            rule="complexity/too-many-params",
                        ))
            return issues

        self.add(Rule(
            id="complexity/too-many-params",
            name="Too Many Parameters",
            description=f"Functions should have at most {max_params} parameters",
            severity=Severity.LOW,
            category="complexity",
            checker=check_params,
        ))

        # Deep nesting
        max_depth = self.config.get("max_nesting_depth", 4)

        def check_nesting(code, file_path, tree):
            issues = []
            if tree is None:
                try:
                    tree = ast.parse(code)
                except SyntaxError:
                    return issues

            def get_depth(node, current=0):
                max_d = current
                nesting_nodes = (ast.If, ast.For, ast.While, ast.With, ast.Try)
                for child in ast.iter_child_nodes(node):
                    if isinstance(child, nesting_nodes):
                        child_depth = get_depth(child, current + 1)
                    else:
                        child_depth = get_depth(child, current)
                    max_d = max(max_d, child_depth)
                return max_d

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    depth = get_depth(node)
                    if depth > max_depth:
                        issues.append(Issue(
                            type="deep_nesting",
                            severity=Severity.MEDIUM,
                            file=file_path,
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Function '{node.name}' has nesting depth {depth} (max: {max_depth})",
                            suggestion="Use early returns or extract nested logic",
                            rule="complexity/deep-nesting",
                        ))
            return issues

        self.add(Rule(
            id="complexity/deep-nesting",
            name="Deep Nesting",
            description=f"Nesting should not exceed {max_depth} levels",
            severity=Severity.MEDIUM,
            category="complexity",
            checker=check_nesting,
        ))


class StyleRules(RuleSet):
    """
    Built-in style rules.

    Includes rules for:
    - Naming conventions
    - Import order
    - Line length
    """

    def __init__(self, config: Optional[dict] = None):
        super().__init__(name="style")
        self.config = config or {}
        self._add_rules()

    def _add_rules(self):
        # Line length
        max_length = self.config.get("max_line_length", 120)

        def check_line_length(code, file_path, tree):
            issues = []
            for i, line in enumerate(code.split("\n"), 1):
                if len(line) > max_length:
                    # Skip URLs and long imports
                    if "http://" in line or "https://" in line:
                        continue
                    if line.strip().startswith(("import ", "from ")):
                        continue

                    issues.append(Issue(
                        type="line_too_long",
                        severity=Severity.INFO,
                        file=file_path,
                        line=i,
                        column=max_length,
                        message=f"Line is {len(line)} characters (max: {max_length})",
                        suggestion="Break line into multiple lines",
                        rule="style/line-length",
                    ))
            return issues

        self.add(Rule(
            id="style/line-length",
            name="Line Too Long",
            description=f"Lines should not exceed {max_length} characters",
            severity=Severity.INFO,
            category="style",
            checker=check_line_length,
        ))

        # Trailing whitespace
        self.add(
            RuleBuilder("style/trailing-whitespace")
            .name("Trailing Whitespace")
            .description("Lines should not have trailing whitespace")
            .severity(Severity.INFO)
            .category("style")
            .pattern(
                r'[ \t]+$',
                message="Trailing whitespace",
                suggestion="Remove trailing whitespace"
            )
            .tags("whitespace")
            .build()
        )

        # Multiple blank lines
        def check_blank_lines(code, file_path, tree):
            issues = []
            lines = code.split("\n")

            consecutive = 0
            for i, line in enumerate(lines, 1):
                if not line.strip():
                    consecutive += 1
                else:
                    consecutive = 0

                if consecutive > 2:
                    issues.append(Issue(
                        type="multiple_blank_lines",
                        severity=Severity.INFO,
                        file=file_path,
                        line=i,
                        column=0,
                        message="Too many consecutive blank lines",
                        suggestion="Use at most 2 consecutive blank lines",
                        rule="style/blank-lines",
                    ))
            return issues

        self.add(Rule(
            id="style/blank-lines",
            name="Multiple Blank Lines",
            description="Avoid more than 2 consecutive blank lines",
            severity=Severity.INFO,
            category="style",
            checker=check_blank_lines,
        ))

        # Missing final newline
        def check_final_newline(code, file_path, tree):
            issues = []
            if code and not code.endswith("\n"):
                issues.append(Issue(
                    type="no_final_newline",
                    severity=Severity.INFO,
                    file=file_path,
                    line=len(code.split("\n")),
                    column=0,
                    message="File does not end with a newline",
                    suggestion="Add a newline at the end of the file",
                    rule="style/final-newline",
                ))
            return issues

        self.add(Rule(
            id="style/final-newline",
            name="Missing Final Newline",
            description="Files should end with a newline",
            severity=Severity.INFO,
            category="style",
            checker=check_final_newline,
        ))
