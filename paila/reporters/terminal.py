"""
Terminal Reporter
=================

Colored terminal output for review results.
"""

from typing import Union, List
from .base import BaseReporter
from ..models import FileResult, ReviewResult, Issue, Severity


class TerminalReporter(BaseReporter):
    """
    Reports results to terminal with colors and formatting.

    Uses ANSI escape codes for colors. Falls back to plain text
    if terminal doesn't support colors.
    """

    name = "terminal"
    extension = ".txt"

    # ANSI color codes
    COLORS = {
        "reset": "\033[0m",
        "bold": "\033[1m",
        "dim": "\033[2m",
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
    }

    SEVERITY_COLORS = {
        Severity.CRITICAL: "red",
        Severity.HIGH: "red",
        Severity.MEDIUM: "yellow",
        Severity.LOW: "cyan",
        Severity.INFO: "dim",
    }

    SEVERITY_ICONS = {
        Severity.CRITICAL: "🚨",
        Severity.HIGH: "❌",
        Severity.MEDIUM: "⚠️ ",
        Severity.LOW: "💡",
        Severity.INFO: "ℹ️ ",
    }

    def __init__(self, use_colors: bool = True, use_icons: bool = True):
        """
        Initialize terminal reporter.

        Args:
            use_colors: Whether to use ANSI colors
            use_icons: Whether to use emoji icons
        """
        self.use_colors = use_colors
        self.use_icons = use_icons

    def _color(self, text: str, color: str) -> str:
        """Apply color to text."""
        if not self.use_colors:
            return text
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['reset']}"

    def _severity_color(self, severity: Severity) -> str:
        """Get color for severity level."""
        return self.SEVERITY_COLORS.get(severity, "white")

    def _severity_icon(self, severity: Severity) -> str:
        """Get icon for severity level."""
        if not self.use_icons:
            return f"[{severity.value.upper()}]"
        return self.SEVERITY_ICONS.get(severity, "•")

    def format(self, result: Union[FileResult, ReviewResult]) -> str:
        """Format result for terminal display."""
        if isinstance(result, FileResult):
            return self._format_file_result(result)
        else:
            return self._format_review_result(result)

    def _format_file_result(self, result: FileResult) -> str:
        """Format a single file result."""
        lines = []

        # Header
        lines.append(self._color("=" * 60, "dim"))
        lines.append(self._color(f"📁 {result.file}", "bold"))
        lines.append(self._color("=" * 60, "dim"))

        if result.skipped:
            lines.append(self._color("  Skipped", "dim"))
            return "\n".join(lines)

        if not result.issues:
            lines.append(self._color("  ✅ No issues found!", "green"))
        else:
            lines.append(f"  Found {len(result.issues)} issue(s)")
            lines.append("")

            for issue in result.issues:
                lines.extend(self._format_issue(issue))

        # Metrics
        if result.metrics:
            lines.append("")
            lines.append(self._color("📊 Metrics:", "bold"))
            m = result.metrics
            lines.append(f"  Lines of code: {m.lines_of_code}")
            lines.append(f"  Functions: {m.functions}")
            lines.append(f"  Classes: {m.classes}")
            if m.avg_complexity > 0:
                lines.append(f"  Avg complexity: {m.avg_complexity}")

        return "\n".join(lines)

    def _format_review_result(self, result: ReviewResult) -> str:
        """Format a full review result."""
        lines = []

        # Header
        lines.append("")
        lines.append(self._color("╔" + "═" * 58 + "╗", "cyan"))
        lines.append(self._color("║" + "  PAILA CODE REVIEW REPORT".center(58) + "║", "cyan"))
        lines.append(self._color("╚" + "═" * 58 + "╝", "cyan"))
        lines.append("")

        # Summary
        lines.append(self._color("📋 SUMMARY", "bold"))
        lines.append(self._color("-" * 40, "dim"))

        file_count = len([f for f in result.files if not f.skipped])
        lines.append(f"  Files analyzed: {file_count}")
        lines.append(f"  Total issues: {result.total_issues}")

        if result.metrics:
            lines.append(f"  Lines of code: {result.metrics.lines_of_code}")

        # Score
        score = result.score
        grade = result.grade

        if score >= 80:
            score_color = "green"
        elif score >= 60:
            score_color = "yellow"
        else:
            score_color = "red"

        lines.append("")
        lines.append(
            f"  Score: {self._color(f'{score}/100', score_color)} "
            f"(Grade: {self._color(grade, score_color)})"
        )

        # Issues by severity
        if result.issues_by_severity:
            lines.append("")
            lines.append(self._color("🎯 ISSUES BY SEVERITY", "bold"))
            lines.append(self._color("-" * 40, "dim"))

            for severity_name in ["critical", "high", "medium", "low", "info"]:
                count = result.issues_by_severity.get(severity_name, 0)
                if count > 0:
                    sev = Severity(severity_name)
                    icon = self._severity_icon(sev)
                    color = self._severity_color(sev)
                    lines.append(
                        f"  {icon} {self._color(severity_name.upper(), color)}: {count}"
                    )

        # Issues by type
        if result.issues_by_type and len(result.issues_by_type) <= 10:
            lines.append("")
            lines.append(self._color("📂 ISSUES BY TYPE", "bold"))
            lines.append(self._color("-" * 40, "dim"))

            for issue_type, count in sorted(
                result.issues_by_type.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]:
                lines.append(f"  • {issue_type}: {count}")

        # File details
        files_with_issues = [f for f in result.files if f.issues and not f.skipped]

        if files_with_issues:
            lines.append("")
            lines.append(self._color("📁 FILES WITH ISSUES", "bold"))
            lines.append(self._color("-" * 40, "dim"))

            for file_result in files_with_issues[:10]:
                issue_count = len(file_result.issues)
                lines.append(f"  • {file_result.file}: {issue_count} issue(s)")

            if len(files_with_issues) > 10:
                remaining = len(files_with_issues) - 10
                lines.append(f"  ... and {remaining} more files")

        # Top issues (first 5)
        all_issues: List[Issue] = []
        for f in result.files:
            all_issues.extend(f.issues)

        # Sort by severity
        severity_order = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 1,
            Severity.MEDIUM: 2,
            Severity.LOW: 3,
            Severity.INFO: 4,
        }
        all_issues.sort(key=lambda i: severity_order.get(i.severity, 5))

        if all_issues:
            lines.append("")
            lines.append(self._color("🔍 TOP ISSUES", "bold"))
            lines.append(self._color("-" * 40, "dim"))

            for issue in all_issues[:5]:
                lines.extend(self._format_issue(issue, compact=True))

            if len(all_issues) > 5:
                remaining = len(all_issues) - 5
                lines.append(f"\n  ... and {remaining} more issues")

        lines.append("")
        lines.append(self._color("─" * 60, "dim"))
        lines.append(
            self._color("  Generated by Paila SDK • https://github.com/saikrishnapaila/paila", "dim")
        )
        lines.append("")

        return "\n".join(lines)

    def _format_issue(self, issue: Issue, compact: bool = False) -> List[str]:
        """Format a single issue."""
        lines = []
        color = self._severity_color(issue.severity)
        icon = self._severity_icon(issue.severity)

        if compact:
            # Compact format for summary
            loc = f"{issue.file}:{issue.line}"
            lines.append(
                f"  {icon} {self._color(issue.message[:50], color)}"
            )
            lines.append(self._color(f"     └─ {loc}", "dim"))
        else:
            # Full format
            lines.append("")
            lines.append(
                f"  {icon} {self._color(issue.severity.value.upper(), color)}: "
                f"{issue.message}"
            )
            lines.append(self._color(f"     Location: {issue.file}:{issue.line}", "dim"))

            if issue.code:
                code_preview = issue.code[:60] + "..." if len(issue.code) > 60 else issue.code
                lines.append(self._color(f"     Code: {code_preview}", "dim"))

            if issue.suggestion:
                lines.append(self._color(f"     💡 {issue.suggestion}", "cyan"))

            if issue.rule:
                lines.append(self._color(f"     Rule: {issue.rule}", "dim"))

        return lines

    def print(self, result: Union[FileResult, ReviewResult]) -> None:
        """Print the formatted result to stdout."""
        print(self.format(result))
