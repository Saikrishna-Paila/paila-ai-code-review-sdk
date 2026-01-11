"""
Base Rule Classes
=================

Base classes for defining custom rules.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass, field
import ast
import re

from ..models import Issue, Severity


@dataclass
class Rule:
    """
    A single code review rule.

    Attributes:
        id: Unique rule identifier (e.g., "security/sql-injection")
        name: Human-readable rule name
        description: What this rule checks for
        severity: Default severity level
        category: Rule category (security, complexity, style, etc.)
        checker: Function that checks for violations
        enabled: Whether the rule is enabled
        config: Additional rule configuration
    """
    id: str
    name: str
    description: str
    severity: Severity
    category: str
    checker: Callable[[str, str, Optional[ast.AST]], List[Issue]]
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    def check(
        self,
        code: str,
        file_path: str,
        tree: Optional[ast.AST] = None
    ) -> List[Issue]:
        """
        Check code for violations of this rule.

        Args:
            code: Source code
            file_path: File path
            tree: Pre-parsed AST

        Returns:
            List of issues found
        """
        if not self.enabled:
            return []

        return self.checker(code, file_path, tree)

    def __repr__(self) -> str:
        return f"Rule(id='{self.id}', enabled={self.enabled})"


class RuleSet:
    """
    A collection of rules.

    Usage:
        rules = RuleSet()
        rules.add(my_rule)
        issues = rules.check_all(code, file_path)
    """

    def __init__(self, name: str = "default"):
        """
        Initialize a rule set.

        Args:
            name: Name for this rule set
        """
        self.name = name
        self._rules: Dict[str, Rule] = {}

    def add(self, rule: Rule) -> None:
        """Add a rule to the set."""
        self._rules[rule.id] = rule

    def remove(self, rule_id: str) -> None:
        """Remove a rule by ID."""
        if rule_id in self._rules:
            del self._rules[rule_id]

    def enable(self, rule_id: str) -> None:
        """Enable a rule."""
        if rule_id in self._rules:
            self._rules[rule_id].enabled = True

    def disable(self, rule_id: str) -> None:
        """Disable a rule."""
        if rule_id in self._rules:
            self._rules[rule_id].enabled = False

    def get(self, rule_id: str) -> Optional[Rule]:
        """Get a rule by ID."""
        return self._rules.get(rule_id)

    @property
    def rules(self) -> List[Rule]:
        """Get all rules."""
        return list(self._rules.values())

    @property
    def enabled_rules(self) -> List[Rule]:
        """Get enabled rules only."""
        return [r for r in self._rules.values() if r.enabled]

    def by_category(self, category: str) -> List[Rule]:
        """Get rules by category."""
        return [r for r in self._rules.values() if r.category == category]

    def by_severity(self, severity: Severity) -> List[Rule]:
        """Get rules by severity."""
        return [r for r in self._rules.values() if r.severity == severity]

    def check_all(
        self,
        code: str,
        file_path: str,
        tree: Optional[ast.AST] = None
    ) -> List[Issue]:
        """
        Check code against all enabled rules.

        Args:
            code: Source code
            file_path: File path
            tree: Pre-parsed AST

        Returns:
            List of all issues found
        """
        issues = []

        for rule in self.enabled_rules:
            try:
                rule_issues = rule.check(code, file_path, tree)
                issues.extend(rule_issues)
            except Exception as e:
                # Don't let one rule failure stop others
                pass

        return issues

    def __len__(self) -> int:
        return len(self._rules)

    def __iter__(self):
        return iter(self._rules.values())

    def __repr__(self) -> str:
        return f"RuleSet(name='{self.name}', rules={len(self._rules)})"


class RuleBuilder:
    """
    Builder for creating rules easily.

    Usage:
        rule = (RuleBuilder("my-rule")
            .name("My Custom Rule")
            .description("Checks for something")
            .severity(Severity.MEDIUM)
            .pattern(r"bad_pattern")
            .build())
    """

    def __init__(self, rule_id: str):
        """Initialize the builder with rule ID."""
        self._id = rule_id
        self._name = rule_id
        self._description = ""
        self._severity = Severity.LOW
        self._category = "custom"
        self._checker = None
        self._enabled = True
        self._config = {}
        self._tags = []

    def name(self, name: str) -> "RuleBuilder":
        """Set the rule name."""
        self._name = name
        return self

    def description(self, desc: str) -> "RuleBuilder":
        """Set the description."""
        self._description = desc
        return self

    def severity(self, sev: Severity) -> "RuleBuilder":
        """Set the severity."""
        self._severity = sev
        return self

    def category(self, cat: str) -> "RuleBuilder":
        """Set the category."""
        self._category = cat
        return self

    def checker(self, func: Callable) -> "RuleBuilder":
        """Set the checker function."""
        self._checker = func
        return self

    def pattern(
        self,
        pattern: str,
        message: str = "Pattern matched",
        suggestion: str = ""
    ) -> "RuleBuilder":
        """
        Create a pattern-based checker.

        Args:
            pattern: Regex pattern to match
            message: Issue message
            suggestion: Fix suggestion
        """
        regex = re.compile(pattern)

        def pattern_checker(code, file_path, tree):
            issues = []
            for i, line in enumerate(code.split("\n"), 1):
                if regex.search(line):
                    issues.append(Issue(
                        type=self._id,
                        severity=self._severity,
                        file=file_path,
                        line=i,
                        column=0,
                        message=message,
                        code=line.strip(),
                        suggestion=suggestion,
                        rule=self._id,
                    ))
            return issues

        self._checker = pattern_checker
        return self

    def ast_checker(
        self,
        node_type: type,
        condition: Callable[[ast.AST], bool],
        message: str,
        suggestion: str = ""
    ) -> "RuleBuilder":
        """
        Create an AST-based checker.

        Args:
            node_type: AST node type to check
            condition: Function that returns True for violations
            message: Issue message
            suggestion: Fix suggestion
        """
        def ast_checker_func(code, file_path, tree):
            issues = []

            if tree is None:
                try:
                    tree = ast.parse(code)
                except SyntaxError:
                    return issues

            for node in ast.walk(tree):
                if isinstance(node, node_type) and condition(node):
                    issues.append(Issue(
                        type=self._id,
                        severity=self._severity,
                        file=file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        message=message,
                        suggestion=suggestion,
                        rule=self._id,
                    ))

            return issues

        self._checker = ast_checker_func
        return self

    def enabled(self, enabled: bool) -> "RuleBuilder":
        """Set whether enabled by default."""
        self._enabled = enabled
        return self

    def config(self, **kwargs) -> "RuleBuilder":
        """Set configuration options."""
        self._config.update(kwargs)
        return self

    def tags(self, *tags: str) -> "RuleBuilder":
        """Add tags to the rule."""
        self._tags.extend(tags)
        return self

    def build(self) -> Rule:
        """Build and return the rule."""
        if self._checker is None:
            raise ValueError("Rule must have a checker function")

        return Rule(
            id=self._id,
            name=self._name,
            description=self._description,
            severity=self._severity,
            category=self._category,
            checker=self._checker,
            enabled=self._enabled,
            config=self._config,
            tags=self._tags,
        )
