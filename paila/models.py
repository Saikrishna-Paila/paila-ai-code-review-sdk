"""
Data Models for Paila SDK
=========================

Core data structures used throughout the SDK.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime


class Severity(str, Enum):
    """Issue severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

    def __str__(self):
        return self.value

    @property
    def color(self) -> str:
        """Get color for terminal output."""
        colors = {
            "critical": "red",
            "high": "red",
            "medium": "yellow",
            "low": "blue",
            "info": "dim",
        }
        return colors.get(self.value, "white")

    @property
    def emoji(self) -> str:
        """Get emoji for the severity."""
        emojis = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🔵",
            "info": "ℹ️",
        }
        return emojis.get(self.value, "•")


class IssueType(str, Enum):
    """Types of issues that can be detected."""
    # Security
    SQL_INJECTION = "sql_injection"
    COMMAND_INJECTION = "command_injection"
    XSS = "xss"
    PATH_TRAVERSAL = "path_traversal"
    HARDCODED_SECRET = "hardcoded_secret"
    INSECURE_RANDOM = "insecure_random"
    EVAL_USAGE = "eval_usage"
    PICKLE_USAGE = "pickle_usage"
    INSECURE_HASH = "insecure_hash"

    # Complexity
    HIGH_COMPLEXITY = "high_complexity"
    DEEP_NESTING = "deep_nesting"
    LONG_FUNCTION = "long_function"
    TOO_MANY_PARAMS = "too_many_params"
    LONG_LINE = "long_line"
    LARGE_FILE = "large_file"

    # Code Smells
    MAGIC_NUMBER = "magic_number"
    DUPLICATE_CODE = "duplicate_code"
    DEAD_CODE = "dead_code"
    MISSING_DOCSTRING = "missing_docstring"
    EMPTY_EXCEPT = "empty_except"
    BARE_EXCEPT = "bare_except"
    TODO_COMMENT = "todo_comment"
    COMMENTED_CODE = "commented_code"
    INCONSISTENT_NAMING = "inconsistent_naming"
    UNUSED_IMPORT = "unused_import"
    UNUSED_VARIABLE = "unused_variable"
    STAR_IMPORT = "star_import"
    MUTABLE_DEFAULT = "mutable_default"
    PRINT_STATEMENT = "print_statement"

    def __str__(self):
        return self.value


@dataclass
class Issue:
    """
    Represents a single issue found during code review.

    Attributes:
        type: Type of issue (e.g., SQL_INJECTION, HIGH_COMPLEXITY)
        severity: How severe the issue is (critical, high, medium, low, info)
        file: Path to the file containing the issue
        line: Line number where the issue was found
        column: Column number (optional)
        message: Human-readable description of the issue
        code: The problematic code snippet
        suggestion: How to fix the issue
        rule: Name of the rule that detected this issue
        ai_explanation: AI-generated explanation (if AI enabled)
        ai_fix: AI-generated fix suggestion (if AI enabled)
    """
    type: str
    severity: Severity
    file: str
    line: int
    message: str
    code: str = ""
    column: int = 0
    end_line: Optional[int] = None
    end_column: Optional[int] = None
    suggestion: str = ""
    rule: str = ""
    ai_explanation: Optional[str] = None
    ai_fix: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": str(self.type),
            "severity": str(self.severity),
            "file": self.file,
            "line": self.line,
            "column": self.column,
            "end_line": self.end_line,
            "end_column": self.end_column,
            "message": self.message,
            "code": self.code,
            "suggestion": self.suggestion,
            "rule": self.rule,
            "ai_explanation": self.ai_explanation,
            "ai_fix": self.ai_fix,
            "metadata": self.metadata,
        }

    def __str__(self) -> str:
        return f"[{self.severity}] {self.type} at {self.file}:{self.line} - {self.message}"


@dataclass
class Metrics:
    """
    Code quality metrics for a file or project.

    Attributes:
        lines_of_code: Total lines of code (excluding blanks and comments)
        total_lines: Total lines including blanks and comments
        blank_lines: Number of blank lines
        comment_lines: Number of comment lines
        functions: Number of functions/methods
        classes: Number of classes
        avg_complexity: Average cyclomatic complexity
        max_complexity: Maximum cyclomatic complexity in any function
        maintainability_index: Maintainability index (0-100)
        comment_ratio: Ratio of comments to code
        duplication_ratio: Percentage of duplicated code
    """
    lines_of_code: int = 0
    total_lines: int = 0
    blank_lines: int = 0
    comment_lines: int = 0
    functions: int = 0
    classes: int = 0
    avg_complexity: float = 0.0
    max_complexity: int = 0
    maintainability_index: float = 100.0
    comment_ratio: float = 0.0
    duplication_ratio: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "lines_of_code": self.lines_of_code,
            "total_lines": self.total_lines,
            "blank_lines": self.blank_lines,
            "comment_lines": self.comment_lines,
            "functions": self.functions,
            "classes": self.classes,
            "avg_complexity": round(self.avg_complexity, 2),
            "max_complexity": self.max_complexity,
            "maintainability_index": round(self.maintainability_index, 2),
            "comment_ratio": round(self.comment_ratio, 2),
            "duplication_ratio": round(self.duplication_ratio, 2),
        }


@dataclass
class FileResult:
    """Result of reviewing a single file."""
    file: str
    issues: List[Issue] = field(default_factory=list)
    metrics: Optional[Metrics] = None
    skipped: bool = False
    error: Optional[str] = None

    @property
    def issue_count(self) -> int:
        return len(self.issues)

    @property
    def critical_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.CRITICAL)

    @property
    def high_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.HIGH)

    @property
    def score(self) -> int:
        """Calculate score from issues found."""
        score = 100
        severity_deductions = {
            Severity.CRITICAL: 15,
            Severity.HIGH: 10,
            Severity.MEDIUM: 5,
            Severity.LOW: 2,
            Severity.INFO: 0,
        }
        for issue in self.issues:
            score -= severity_deductions.get(issue.severity, 0)
        return max(0, min(100, score))

    @property
    def grade(self) -> str:
        """Calculate letter grade from score."""
        score = self.score
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file": self.file,
            "score": self.score,
            "grade": self.grade,
            "issues": [i.to_dict() for i in self.issues],
            "metrics": self.metrics.to_dict() if self.metrics else None,
            "skipped": self.skipped,
            "error": self.error,
        }


@dataclass
class ReviewResult:
    """
    Complete result of a code review.

    This is the main output of the Reviewer.review_directory() method.
    """
    files: List[FileResult] = field(default_factory=list)
    total_issues: int = 0
    issues_by_severity: Dict[str, int] = field(default_factory=dict)
    issues_by_type: Dict[str, int] = field(default_factory=dict)
    issues_by_file: Dict[str, List[Issue]] = field(default_factory=dict)
    metrics: Optional[Metrics] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    duration_seconds: float = 0.0

    @property
    def score(self) -> int:
        """Calculate overall score from issues."""
        score = 100

        # Deduct points for issues
        severity_deductions = {
            "critical": 15,
            "high": 10,
            "medium": 5,
            "low": 2,
            "info": 0,
        }

        for sev, count in self.issues_by_severity.items():
            deduction = severity_deductions.get(sev, 0)
            score -= deduction * count

        return max(0, min(100, score))

    @property
    def grade(self) -> str:
        """Calculate letter grade from score."""
        score = self.score
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    @property
    def summary(self) -> str:
        """Generate a human-readable summary."""
        file_count = len([f for f in self.files if not f.skipped])

        lines = [
            "=" * 60,
            "              PAILA CODE REVIEW REPORT",
            "=" * 60,
            "",
            f"  Score: {self.score}/100 (Grade: {self.grade})",
            f"  Files reviewed: {file_count}",
            f"  Total issues: {self.total_issues}",
            "",
            "  Issue breakdown:",
        ]

        for sev in ["critical", "high", "medium", "low", "info"]:
            count = self.issues_by_severity.get(sev, 0)
            emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵", "info": "ℹ️"}.get(sev, "•")
            lines.append(f"    {emoji} {sev.title()}: {count}")

        if self.metrics:
            lines.extend([
                "",
                "  Metrics:",
                f"    Lines of code:    {self.metrics.lines_of_code}",
                f"    Avg complexity:   {self.metrics.avg_complexity:.1f}",
            ])

        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "score": self.score,
            "grade": self.grade,
            "timestamp": self.timestamp,
            "duration_seconds": self.duration_seconds,
            "total_issues": self.total_issues,
            "issues_by_severity": self.issues_by_severity,
            "issues_by_type": self.issues_by_type,
            "metrics": self.metrics.to_dict() if self.metrics else None,
            "files": [f.to_dict() for f in self.files],
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        import json
        return json.dumps(self.to_dict(), indent=indent)


def calculate_grade(score: int) -> str:
    """Calculate letter grade from score."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def calculate_score(issues: List[Issue], metrics: Optional[Metrics] = None) -> int:
    """
    Calculate overall score from issues and metrics.

    Score starts at 100 and is reduced based on issues found.
    """
    score = 100

    # Deduct points for issues
    severity_deductions = {
        Severity.CRITICAL: 15,
        Severity.HIGH: 10,
        Severity.MEDIUM: 5,
        Severity.LOW: 2,
        Severity.INFO: 0,
    }

    for issue in issues:
        score -= severity_deductions.get(issue.severity, 0)

    if metrics:
        # Deduct for poor maintainability
        if metrics.maintainability_index < 50:
            score -= 10
        elif metrics.maintainability_index < 65:
            score -= 5

        # Deduct for high complexity
        if metrics.max_complexity > 20:
            score -= 10
        elif metrics.max_complexity > 10:
            score -= 5

    return max(0, min(100, score))
