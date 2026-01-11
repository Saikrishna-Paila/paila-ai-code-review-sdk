"""
JSON Reporter
=============

JSON output for review results.
"""

import json
from typing import Union, Any, Dict
from datetime import datetime

from .base import BaseReporter
from ..models import FileResult, ReviewResult, Severity


class JSONReporter(BaseReporter):
    """
    Reports results in JSON format.

    Useful for:
    - CI/CD integration
    - API responses
    - Data processing pipelines
    """

    name = "json"
    extension = ".json"

    def __init__(self, indent: int = 2, include_metadata: bool = True):
        """
        Initialize JSON reporter.

        Args:
            indent: JSON indentation level
            include_metadata: Include additional metadata in output
        """
        self.indent = indent
        self.include_metadata = include_metadata

    def format(self, result: Union[FileResult, ReviewResult]) -> str:
        """Format result as JSON string."""
        data = self._to_dict(result)
        return json.dumps(data, indent=self.indent, default=str)

    def _to_dict(self, result: Union[FileResult, ReviewResult]) -> Dict[str, Any]:
        """Convert result to dictionary."""
        if isinstance(result, FileResult):
            return self._file_result_to_dict(result)
        else:
            return self._review_result_to_dict(result)

    def _file_result_to_dict(self, result: FileResult) -> Dict[str, Any]:
        """Convert FileResult to dictionary."""
        data: Dict[str, Any] = {
            "file": result.file,
            "score": result.score,
            "grade": result.grade,
            "skipped": result.skipped,
            "issue_count": len(result.issues),
            "issues": [self._issue_to_dict(i) for i in result.issues],
        }

        if result.metrics:
            data["metrics"] = {
                "lines_of_code": result.metrics.lines_of_code,
                "total_lines": result.metrics.total_lines,
                "blank_lines": result.metrics.blank_lines,
                "comment_lines": result.metrics.comment_lines,
                "functions": result.metrics.functions,
                "classes": result.metrics.classes,
                "avg_complexity": result.metrics.avg_complexity,
                "max_complexity": result.metrics.max_complexity,
            }

        if self.include_metadata:
            data["_metadata"] = {
                "generator": "paila",
                "version": "0.1.0",
                "timestamp": datetime.utcnow().isoformat(),
            }

        return data

    def _review_result_to_dict(self, result: ReviewResult) -> Dict[str, Any]:
        """Convert ReviewResult to dictionary."""
        data: Dict[str, Any] = {
            "summary": {
                "total_files": len(result.files),
                "files_analyzed": len([f for f in result.files if not f.skipped]),
                "total_issues": result.total_issues,
                "score": result.score,
                "grade": result.grade,
            },
            "issues_by_severity": result.issues_by_severity,
            "issues_by_type": result.issues_by_type,
        }

        if result.metrics:
            data["metrics"] = {
                "lines_of_code": result.metrics.lines_of_code,
                "total_lines": result.metrics.total_lines,
                "functions": result.metrics.functions,
                "classes": result.metrics.classes,
                "avg_complexity": result.metrics.avg_complexity,
            }

        # Include files with issues
        data["files"] = []
        for file_result in result.files:
            if not file_result.skipped:
                file_data = {
                    "file": file_result.file,
                    "issue_count": len(file_result.issues),
                    "issues": [self._issue_to_dict(i) for i in file_result.issues],
                }
                if file_result.metrics:
                    file_data["metrics"] = {
                        "lines_of_code": file_result.metrics.lines_of_code,
                        "functions": file_result.metrics.functions,
                        "classes": file_result.metrics.classes,
                        "avg_complexity": file_result.metrics.avg_complexity,
                    }
                data["files"].append(file_data)

        if self.include_metadata:
            data["_metadata"] = {
                "generator": "paila",
                "version": "0.1.0",
                "timestamp": datetime.utcnow().isoformat(),
            }

        return data

    def _issue_to_dict(self, issue) -> Dict[str, Any]:
        """Convert Issue to dictionary."""
        return {
            "type": issue.type,
            "severity": issue.severity.value,
            "message": issue.message,
            "file": issue.file,
            "line": issue.line,
            "column": issue.column,
            "code": issue.code,
            "suggestion": issue.suggestion,
            "rule": issue.rule,
            "metadata": issue.metadata,
        }
