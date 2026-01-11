"""Tests for reporters."""

import pytest
import json
from paila.models import Issue, Metrics, FileResult, ReviewResult, Severity
from paila.reporters import (
    TerminalReporter,
    JSONReporter,
    MarkdownReporter,
    HTMLReporter,
)


@pytest.fixture
def sample_issue():
    """Create a sample issue for testing."""
    return Issue(
        type="test_issue",
        severity=Severity.MEDIUM,
        file="test.py",
        line=10,
        column=5,
        message="This is a test issue",
        code="x = 42",
        suggestion="Fix this issue",
        rule="test/rule",
    )


@pytest.fixture
def sample_metrics():
    """Create sample metrics for testing."""
    return Metrics(
        lines_of_code=100,
        total_lines=120,
        blank_lines=10,
        comment_lines=10,
        functions=5,
        classes=2,
        avg_complexity=3.5,
        max_complexity=8,
    )


@pytest.fixture
def sample_file_result(sample_issue, sample_metrics):
    """Create a sample file result for testing."""
    return FileResult(
        file="test.py",
        issues=[sample_issue],
        metrics=sample_metrics,
    )


@pytest.fixture
def sample_review_result(sample_file_result):
    """Create a sample review result for testing."""
    return ReviewResult(
        files=[sample_file_result],
        total_issues=1,
        issues_by_severity={"medium": 1},
        issues_by_type={"test_issue": 1},
        issues_by_file={"test.py": sample_file_result.issues},
        metrics=sample_file_result.metrics,
    )


class TestTerminalReporter:
    """Tests for TerminalReporter."""

    def test_format_file_result(self, sample_file_result):
        """Test formatting a file result."""
        reporter = TerminalReporter()
        output = reporter.format(sample_file_result)

        assert "test.py" in output
        assert "test issue" in output.lower()

    def test_format_review_result(self, sample_review_result):
        """Test formatting a review result."""
        reporter = TerminalReporter()
        output = reporter.format(sample_review_result)

        assert "PAILA" in output
        assert "Score" in output or "score" in output.lower()

    def test_no_colors(self, sample_file_result):
        """Test output without colors."""
        reporter = TerminalReporter(use_colors=False)
        output = reporter.format(sample_file_result)

        # Should not contain ANSI escape codes
        assert "\033[" not in output

    def test_no_icons(self, sample_file_result):
        """Test output without icons."""
        reporter = TerminalReporter(use_icons=False)
        output = reporter.format(sample_file_result)

        # Check that output is still valid
        assert "test.py" in output


class TestJSONReporter:
    """Tests for JSONReporter."""

    def test_format_file_result(self, sample_file_result):
        """Test formatting a file result as JSON."""
        reporter = JSONReporter()
        output = reporter.format(sample_file_result)

        # Should be valid JSON
        data = json.loads(output)
        assert data["file"] == "test.py"
        assert len(data["issues"]) == 1

    def test_format_review_result(self, sample_review_result):
        """Test formatting a review result as JSON."""
        reporter = JSONReporter()
        output = reporter.format(sample_review_result)

        data = json.loads(output)
        assert "summary" in data
        assert data["summary"]["total_issues"] == 1

    def test_includes_metadata(self, sample_file_result):
        """Test that metadata is included."""
        reporter = JSONReporter(include_metadata=True)
        output = reporter.format(sample_file_result)

        data = json.loads(output)
        assert "_metadata" in data
        assert data["_metadata"]["generator"] == "paila"

    def test_no_metadata(self, sample_file_result):
        """Test without metadata."""
        reporter = JSONReporter(include_metadata=False)
        output = reporter.format(sample_file_result)

        data = json.loads(output)
        assert "_metadata" not in data


class TestMarkdownReporter:
    """Tests for MarkdownReporter."""

    def test_format_file_result(self, sample_file_result):
        """Test formatting a file result as Markdown."""
        reporter = MarkdownReporter()
        output = reporter.format(sample_file_result)

        assert "# Code Review" in output
        assert "test.py" in output
        assert "## Issues" in output

    def test_format_review_result(self, sample_review_result):
        """Test formatting a review result as Markdown."""
        reporter = MarkdownReporter()
        output = reporter.format(sample_review_result)

        assert "# " in output  # Has headers
        assert "## Summary" in output
        assert "Score" in output

    def test_includes_table(self, sample_review_result):
        """Test that tables are included."""
        reporter = MarkdownReporter()
        output = reporter.format(sample_review_result)

        assert "|" in output  # Has table syntax

    def test_includes_code_blocks(self, sample_file_result):
        """Test that code blocks are included."""
        reporter = MarkdownReporter()
        output = reporter.format(sample_file_result)

        assert "```" in output  # Has code blocks


class TestHTMLReporter:
    """Tests for HTMLReporter."""

    def test_format_file_result(self, sample_file_result):
        """Test formatting a file result as HTML."""
        reporter = HTMLReporter()
        output = reporter.format(sample_file_result)

        assert "<!DOCTYPE html>" in output
        assert "<html" in output
        assert "test.py" in output

    def test_format_review_result(self, sample_review_result):
        """Test formatting a review result as HTML."""
        reporter = HTMLReporter()
        output = reporter.format(sample_review_result)

        assert "<!DOCTYPE html>" in output
        assert "Paila" in output

    def test_includes_styles(self, sample_file_result):
        """Test that CSS styles are included."""
        reporter = HTMLReporter()
        output = reporter.format(sample_file_result)

        assert "<style>" in output
        assert "</style>" in output

    def test_valid_html(self, sample_file_result):
        """Test that output is valid HTML structure."""
        reporter = HTMLReporter()
        output = reporter.format(sample_file_result)

        assert output.count("<html") == 1
        assert output.count("</html>") == 1
        assert output.count("<body>") == 1
        assert output.count("</body>") == 1
