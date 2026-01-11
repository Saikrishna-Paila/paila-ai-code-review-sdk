"""
Markdown Reporter
=================

Markdown output for review results.
"""

from typing import Union, List
from datetime import datetime

from .base import BaseReporter
from ..models import FileResult, ReviewResult, Issue, Severity


class MarkdownReporter(BaseReporter):
    """
    Reports results in Markdown format.

    Useful for:
    - GitHub PR comments
    - Documentation
    - Static site generation
    """

    name = "markdown"
    extension = ".md"

    SEVERITY_BADGES = {
        Severity.CRITICAL: "![Critical](https://img.shields.io/badge/-Critical-red)",
        Severity.HIGH: "![High](https://img.shields.io/badge/-High-orange)",
        Severity.MEDIUM: "![Medium](https://img.shields.io/badge/-Medium-yellow)",
        Severity.LOW: "![Low](https://img.shields.io/badge/-Low-blue)",
        Severity.INFO: "![Info](https://img.shields.io/badge/-Info-lightgrey)",
    }

    def __init__(self, include_badges: bool = True, include_toc: bool = False):
        """
        Initialize Markdown reporter.

        Args:
            include_badges: Include severity badges
            include_toc: Include table of contents
        """
        self.include_badges = include_badges
        self.include_toc = include_toc

    def format(self, result: Union[FileResult, ReviewResult]) -> str:
        """Format result as Markdown string."""
        if isinstance(result, FileResult):
            return self._format_file_result(result)
        else:
            return self._format_review_result(result)

    def _format_file_result(self, result: FileResult) -> str:
        """Format a single file result."""
        lines = []

        lines.append(f"# Code Review: {result.file}")
        lines.append("")

        if result.skipped:
            lines.append("*File was skipped*")
            return "\n".join(lines)

        # Summary
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- **Issues found:** {len(result.issues)}")

        if result.metrics:
            lines.append(f"- **Lines of code:** {result.metrics.lines_of_code}")
            lines.append(f"- **Functions:** {result.metrics.functions}")
            lines.append(f"- **Classes:** {result.metrics.classes}")
            if result.metrics.avg_complexity > 0:
                lines.append(f"- **Average complexity:** {result.metrics.avg_complexity}")

        lines.append("")

        # Issues
        if result.issues:
            lines.append("## Issues")
            lines.append("")

            for issue in result.issues:
                lines.extend(self._format_issue_md(issue))

        return "\n".join(lines)

    def _format_review_result(self, result: ReviewResult) -> str:
        """Format a full review result."""
        lines = []

        # Header
        lines.append("# 📋 Paila Code Review Report")
        lines.append("")
        lines.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        lines.append("")

        # Table of Contents
        if self.include_toc:
            lines.append("## Table of Contents")
            lines.append("")
            lines.append("- [Summary](#summary)")
            lines.append("- [Score](#score)")
            lines.append("- [Issues by Severity](#issues-by-severity)")
            lines.append("- [Issues by Type](#issues-by-type)")
            lines.append("- [Files](#files)")
            lines.append("- [Detailed Issues](#detailed-issues)")
            lines.append("")

        # Summary
        lines.append("## Summary")
        lines.append("")

        file_count = len([f for f in result.files if not f.skipped])
        lines.append(f"| Metric | Value |")
        lines.append(f"|--------|-------|")
        lines.append(f"| Files Analyzed | {file_count} |")
        lines.append(f"| Total Issues | {result.total_issues} |")

        if result.metrics:
            lines.append(f"| Lines of Code | {result.metrics.lines_of_code} |")
            lines.append(f"| Functions | {result.metrics.functions} |")
            lines.append(f"| Classes | {result.metrics.classes} |")
            if result.metrics.avg_complexity > 0:
                lines.append(f"| Avg Complexity | {result.metrics.avg_complexity} |")

        lines.append("")

        # Score
        lines.append("## Score")
        lines.append("")

        score = result.score
        grade = result.grade

        # Create a visual score bar
        filled = int(score / 10)
        empty = 10 - filled
        score_bar = "█" * filled + "░" * empty

        lines.append(f"**{score}/100** (Grade: **{grade}**)")
        lines.append("")
        lines.append(f"`{score_bar}`")
        lines.append("")

        # Issues by Severity
        if result.issues_by_severity:
            lines.append("## Issues by Severity")
            lines.append("")
            lines.append("| Severity | Count |")
            lines.append("|----------|-------|")

            for severity_name in ["critical", "high", "medium", "low", "info"]:
                count = result.issues_by_severity.get(severity_name, 0)
                if count > 0:
                    if self.include_badges:
                        sev = Severity(severity_name)
                        badge = self.SEVERITY_BADGES.get(sev, "")
                        lines.append(f"| {badge} {severity_name.title()} | {count} |")
                    else:
                        lines.append(f"| {severity_name.title()} | {count} |")

            lines.append("")

        # Issues by Type
        if result.issues_by_type:
            lines.append("## Issues by Type")
            lines.append("")
            lines.append("| Type | Count |")
            lines.append("|------|-------|")

            for issue_type, count in sorted(
                result.issues_by_type.items(),
                key=lambda x: x[1],
                reverse=True
            ):
                lines.append(f"| `{issue_type}` | {count} |")

            lines.append("")

        # Files with Issues
        files_with_issues = [f for f in result.files if f.issues and not f.skipped]

        if files_with_issues:
            lines.append("## Files")
            lines.append("")
            lines.append("| File | Issues |")
            lines.append("|------|--------|")

            for file_result in files_with_issues:
                issue_count = len(file_result.issues)
                lines.append(f"| `{file_result.file}` | {issue_count} |")

            lines.append("")

        # Detailed Issues
        all_issues: List[Issue] = []
        for f in result.files:
            all_issues.extend(f.issues)

        if all_issues:
            lines.append("## Detailed Issues")
            lines.append("")

            # Group by file
            issues_by_file = {}
            for issue in all_issues:
                if issue.file not in issues_by_file:
                    issues_by_file[issue.file] = []
                issues_by_file[issue.file].append(issue)

            for file_path, issues in issues_by_file.items():
                lines.append(f"### 📁 {file_path}")
                lines.append("")

                for issue in issues:
                    lines.extend(self._format_issue_md(issue))

        # Footer
        lines.append("---")
        lines.append("")
        lines.append("*Generated by [Paila SDK](https://github.com/saikrishnapaila/paila) - AI-Powered Code Review*")

        return "\n".join(lines)

    def _format_issue_md(self, issue: Issue) -> List[str]:
        """Format a single issue in Markdown."""
        lines = []

        # Severity badge
        if self.include_badges:
            badge = self.SEVERITY_BADGES.get(issue.severity, "")
            lines.append(f"#### {badge} {issue.message}")
        else:
            lines.append(f"#### [{issue.severity.value.upper()}] {issue.message}")

        lines.append("")

        # Location
        lines.append(f"- **Location:** `{issue.file}:{issue.line}:{issue.column}`")
        lines.append(f"- **Rule:** `{issue.rule}`")

        # Code snippet
        if issue.code:
            lines.append("")
            lines.append("```python")
            lines.append(issue.code)
            lines.append("```")

        # Suggestion
        if issue.suggestion:
            lines.append("")
            lines.append(f"> 💡 **Suggestion:** {issue.suggestion}")

        lines.append("")
        return lines
