"""
HTML Reporter
=============

Beautiful HTML output for review results.
"""

from typing import Union, List
from datetime import datetime

from .base import BaseReporter
from ..models import FileResult, ReviewResult, Issue, Severity


class HTMLReporter(BaseReporter):
    """
    Reports results in HTML format with inline CSS.

    Generates a standalone HTML file that can be viewed
    in any browser.
    """

    name = "html"
    extension = ".html"

    SEVERITY_COLORS = {
        Severity.CRITICAL: "#dc3545",
        Severity.HIGH: "#fd7e14",
        Severity.MEDIUM: "#ffc107",
        Severity.LOW: "#17a2b8",
        Severity.INFO: "#6c757d",
    }

    def format(self, result: Union[FileResult, ReviewResult]) -> str:
        """Format result as HTML string."""
        if isinstance(result, FileResult):
            return self._format_file_result(result)
        else:
            return self._format_review_result(result)

    def _get_styles(self) -> str:
        """Get inline CSS styles."""
        return """
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #333;
                background: #f5f5f5;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                padding: 30px;
            }
            h1 {
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 15px;
                margin-bottom: 25px;
            }
            h2 {
                color: #34495e;
                margin: 25px 0 15px;
                font-size: 1.4em;
            }
            h3 {
                color: #7f8c8d;
                font-size: 1.1em;
                margin: 15px 0 10px;
            }
            .summary-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }
            .summary-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
            }
            .summary-card.score {
                background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            }
            .summary-card .value {
                font-size: 2.5em;
                font-weight: bold;
            }
            .summary-card .label {
                opacity: 0.9;
                font-size: 0.9em;
            }
            .score-bar {
                height: 20px;
                background: #e9ecef;
                border-radius: 10px;
                overflow: hidden;
                margin: 10px 0;
            }
            .score-bar-fill {
                height: 100%;
                background: linear-gradient(90deg, #11998e, #38ef7d);
                transition: width 0.5s ease;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
            }
            th, td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #e9ecef;
            }
            th {
                background: #f8f9fa;
                font-weight: 600;
            }
            tr:hover {
                background: #f8f9fa;
            }
            .severity-badge {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                color: white;
                font-size: 0.85em;
                font-weight: 500;
            }
            .issue-card {
                background: #f8f9fa;
                border-left: 4px solid #ddd;
                padding: 15px;
                margin: 15px 0;
                border-radius: 0 8px 8px 0;
            }
            .issue-card.critical { border-left-color: #dc3545; }
            .issue-card.high { border-left-color: #fd7e14; }
            .issue-card.medium { border-left-color: #ffc107; }
            .issue-card.low { border-left-color: #17a2b8; }
            .issue-card.info { border-left-color: #6c757d; }
            .issue-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }
            .issue-message {
                font-weight: 500;
                color: #2c3e50;
            }
            .issue-location {
                color: #7f8c8d;
                font-size: 0.9em;
            }
            .code-block {
                background: #2d2d2d;
                color: #f8f8f2;
                padding: 15px;
                border-radius: 6px;
                overflow-x: auto;
                font-family: 'Monaco', 'Menlo', monospace;
                font-size: 0.9em;
                margin: 10px 0;
            }
            .suggestion {
                background: #e8f5e9;
                border-left: 4px solid #4caf50;
                padding: 12px;
                margin: 10px 0;
                border-radius: 0 6px 6px 0;
            }
            .suggestion::before {
                content: '💡 ';
            }
            .footer {
                text-align: center;
                padding: 20px;
                color: #7f8c8d;
                border-top: 1px solid #e9ecef;
                margin-top: 30px;
            }
            .footer a {
                color: #3498db;
                text-decoration: none;
            }
        </style>
        """

    def _format_file_result(self, result: FileResult) -> str:
        """Format a single file result."""
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Review - {result.file}</title>
    {self._get_styles()}
</head>
<body>
    <div class="container">
        <h1>📁 Code Review: {result.file}</h1>
"""
        if result.skipped:
            html += "<p><em>File was skipped</em></p>"
        else:
            html += f"""
        <div class="summary-grid">
            <div class="summary-card">
                <div class="value">{len(result.issues)}</div>
                <div class="label">Issues Found</div>
            </div>
"""
            if result.metrics:
                html += f"""
            <div class="summary-card">
                <div class="value">{result.metrics.lines_of_code}</div>
                <div class="label">Lines of Code</div>
            </div>
            <div class="summary-card">
                <div class="value">{result.metrics.functions}</div>
                <div class="label">Functions</div>
            </div>
"""
            html += "</div>"

            if result.issues:
                html += "<h2>Issues</h2>"
                for issue in result.issues:
                    html += self._format_issue_html(issue)

        html += """
        <div class="footer">
            Generated by <a href="https://github.com/saikrishnapaila/paila">Paila SDK</a>
        </div>
    </div>
</body>
</html>
"""
        return html

    def _format_review_result(self, result: ReviewResult) -> str:
        """Format a full review result."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_count = len([f for f in result.files if not f.skipped])
        score = result.score
        grade = result.grade

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Paila Code Review Report</title>
    {self._get_styles()}
</head>
<body>
    <div class="container">
        <h1>📋 Paila Code Review Report</h1>
        <p style="color: #7f8c8d;">Generated on {timestamp}</p>

        <div class="summary-grid">
            <div class="summary-card score">
                <div class="value">{score}/100</div>
                <div class="label">Score (Grade: {grade})</div>
            </div>
            <div class="summary-card">
                <div class="value">{file_count}</div>
                <div class="label">Files Analyzed</div>
            </div>
            <div class="summary-card">
                <div class="value">{result.total_issues}</div>
                <div class="label">Total Issues</div>
            </div>
"""
        if result.metrics:
            html += f"""
            <div class="summary-card">
                <div class="value">{result.metrics.lines_of_code}</div>
                <div class="label">Lines of Code</div>
            </div>
"""
        html += f"""
        </div>

        <h2>Score</h2>
        <div class="score-bar">
            <div class="score-bar-fill" style="width: {score}%"></div>
        </div>
"""

        # Issues by Severity
        if result.issues_by_severity:
            html += """
        <h2>Issues by Severity</h2>
        <table>
            <thead>
                <tr>
                    <th>Severity</th>
                    <th>Count</th>
                </tr>
            </thead>
            <tbody>
"""
            for severity_name in ["critical", "high", "medium", "low", "info"]:
                count = result.issues_by_severity.get(severity_name, 0)
                if count > 0:
                    color = self.SEVERITY_COLORS.get(Severity(severity_name), "#6c757d")
                    html += f"""
                <tr>
                    <td><span class="severity-badge" style="background: {color}">{severity_name.upper()}</span></td>
                    <td>{count}</td>
                </tr>
"""
            html += """
            </tbody>
        </table>
"""

        # Issues by Type
        if result.issues_by_type:
            html += """
        <h2>Issues by Type</h2>
        <table>
            <thead>
                <tr>
                    <th>Type</th>
                    <th>Count</th>
                </tr>
            </thead>
            <tbody>
"""
            for issue_type, count in sorted(
                result.issues_by_type.items(),
                key=lambda x: x[1],
                reverse=True
            ):
                html += f"""
                <tr>
                    <td><code>{issue_type}</code></td>
                    <td>{count}</td>
                </tr>
"""
            html += """
            </tbody>
        </table>
"""

        # Detailed Issues by File
        all_issues: List[Issue] = []
        for f in result.files:
            all_issues.extend(f.issues)

        if all_issues:
            html += "<h2>Detailed Issues</h2>"

            # Group by file
            issues_by_file = {}
            for issue in all_issues:
                if issue.file not in issues_by_file:
                    issues_by_file[issue.file] = []
                issues_by_file[issue.file].append(issue)

            for file_path, issues in issues_by_file.items():
                html += f"<h3>📁 {file_path}</h3>"
                for issue in issues:
                    html += self._format_issue_html(issue)

        html += """
        <div class="footer">
            Generated by <a href="https://github.com/saikrishnapaila/paila">Paila SDK</a> - AI-Powered Code Review
        </div>
    </div>
</body>
</html>
"""
        return html

    def _format_issue_html(self, issue: Issue) -> str:
        """Format a single issue in HTML."""
        severity_class = issue.severity.value.lower()
        color = self.SEVERITY_COLORS.get(issue.severity, "#6c757d")

        html = f"""
        <div class="issue-card {severity_class}">
            <div class="issue-header">
                <span class="issue-message">{issue.message}</span>
                <span class="severity-badge" style="background: {color}">{issue.severity.value.upper()}</span>
            </div>
            <div class="issue-location">
                📍 {issue.file}:{issue.line}:{issue.column} | Rule: <code>{issue.rule}</code>
            </div>
"""
        if issue.code:
            html += f"""
            <div class="code-block">{issue.code}</div>
"""
        if issue.suggestion:
            html += f"""
            <div class="suggestion">{issue.suggestion}</div>
"""
        html += "</div>"
        return html
