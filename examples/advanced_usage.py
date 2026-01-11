"""
Advanced Usage Examples for Paila SDK
=====================================

This file demonstrates advanced features of the Paila SDK.
"""

from pathlib import Path
from paila import Reviewer, Config
from paila.analyzers import BaseAnalyzer
from paila.models import Issue, Severity
from paila.reporters import JSONReporter, MarkdownReporter, HTMLReporter, TerminalReporter


def example_custom_analyzer():
    """Example: Creating a custom analyzer."""
    print("=" * 50)
    print("Custom Analyzer Example")
    print("=" * 50)

    class ProfanityAnalyzer(BaseAnalyzer):
        """Checks for inappropriate words in code."""

        name = "profanity"
        description = "Detects inappropriate variable names"

        # Words to flag (example only!)
        BAD_WORDS = {"foo", "bar", "baz", "temp", "tmp"}

        def analyze(self, code, file_path, tree=None):
            issues = []

            if tree is None:
                tree = self.parse_code(code)
            if tree is None:
                return issues

            import ast

            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    if node.id.lower() in self.BAD_WORDS:
                        issues.append(Issue(
                            type="poor_naming",
                            severity=Severity.LOW,
                            file=file_path,
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Poor variable name: '{node.id}'",
                            code=self.get_code_line(code, node.lineno),
                            suggestion="Use descriptive variable names",
                            rule="custom/poor-naming",
                        ))

            return issues

    # Use custom analyzer
    code = '''
def process():
    foo = 1
    bar = 2
    temp = foo + bar
    return temp
'''

    reviewer = Reviewer(custom_analyzers=[ProfanityAnalyzer()])
    result = reviewer.review_code(code)

    print(f"Issues from custom analyzer: {len(result.issues)}")
    for issue in result.issues:
        if issue.type == "poor_naming":
            print(f"  - {issue.message}")
    print()


def example_reporters():
    """Example: Using different reporters."""
    print("=" * 50)
    print("Reporters Example")
    print("=" * 50)

    code = '''
def calculate(x, y):
    # TODO: add validation
    result = x * 3.14159 + y
    return result
'''

    reviewer = Reviewer()
    result = reviewer.review_code(code, "calc.py")

    # Terminal output
    print("Terminal Format:")
    print("-" * 40)
    terminal = TerminalReporter(use_colors=False, use_icons=False)
    print(terminal.format(result)[:500])
    print("...")
    print()

    # JSON output
    print("JSON Format (first 300 chars):")
    print("-" * 40)
    json_reporter = JSONReporter(indent=2)
    json_output = json_reporter.format(result)
    print(json_output[:300] + "...")
    print()

    # Markdown output
    print("Markdown Format (first 300 chars):")
    print("-" * 40)
    md_reporter = MarkdownReporter()
    md_output = md_reporter.format(result)
    print(md_output[:300] + "...")
    print()


def example_filtering():
    """Example: Filtering issues by severity."""
    print("=" * 50)
    print("Filtering Example")
    print("=" * 50)

    code = '''
import os

def risky(user_input):
    # TODO: fix security
    query = "SELECT * FROM users WHERE id = " + user_input
    os.system("ls " + user_input)
    password = "secret123"

try:
    do_something()
except:
    pass
'''

    # All issues
    reviewer = Reviewer()
    result = reviewer.review_code(code)
    print(f"All issues: {len(result.issues)}")

    # Only high and critical
    config = Config(min_severity=Severity.HIGH)
    reviewer = Reviewer(config=config)
    result = reviewer.review_code(code)
    print(f"High/Critical only: {len(result.issues)}")

    # Only security issues
    config = Config.security_only()
    reviewer = Reviewer(config=config)
    result = reviewer.review_code(code)
    print(f"Security only: {len(result.issues)}")
    print()


def example_metrics():
    """Example: Analyzing code metrics."""
    print("=" * 50)
    print("Metrics Example")
    print("=" * 50)

    code = '''
"""
Module for data processing.
"""

import json
from typing import List, Dict

# Constants
MAX_ITEMS = 100
DEFAULT_TIMEOUT = 30


class DataProcessor:
    """Processes data items."""

    def __init__(self, config: Dict):
        """Initialize processor."""
        self.config = config
        self.items: List = []

    def process(self, data: List) -> List:
        """Process all items."""
        results = []
        for item in data:
            if self._validate(item):
                result = self._transform(item)
                results.append(result)
        return results

    def _validate(self, item) -> bool:
        """Validate single item."""
        return item is not None

    def _transform(self, item):
        """Transform single item."""
        return {"data": item, "processed": True}


def main():
    """Main entry point."""
    processor = DataProcessor({})
    data = [1, 2, 3, None, 4, 5]
    results = processor.process(data)
    print(f"Processed {len(results)} items")


if __name__ == "__main__":
    main()
'''

    from paila.analyzers import ComplexityAnalyzer

    analyzer = ComplexityAnalyzer()
    metrics = analyzer.calculate_metrics(code)

    print("Code Metrics:")
    print(f"  Total lines: {metrics['total_lines']}")
    print(f"  Code lines: {metrics['code_lines']}")
    print(f"  Blank lines: {metrics['blank_lines']}")
    print(f"  Comment lines: {metrics['comment_lines']}")
    print(f"  Functions: {metrics['functions']}")
    print(f"  Classes: {metrics['classes']}")
    print(f"  Avg complexity: {metrics['avg_complexity']}")
    print(f"  Max complexity: {metrics['max_complexity']}")
    print()


def example_batch_processing():
    """Example: Processing multiple code snippets."""
    print("=" * 50)
    print("Batch Processing Example")
    print("=" * 50)

    code_samples = {
        "auth.py": '''
def login(username, password):
    query = f"SELECT * FROM users WHERE name = '{username}'"
    return execute(query)
''',
        "utils.py": '''
def helper():
    pass

def process(items=[]):
    items.append(1)
    return items
''',
        "main.py": '''
def main():
    """Main function."""
    print("Hello, World!")
    return 0
''',
    }

    reviewer = Reviewer()
    all_issues = []

    for filename, code in code_samples.items():
        result = reviewer.review_code(code, filename)
        all_issues.extend(result.issues)
        print(f"{filename}: {len(result.issues)} issues")

    print()
    print(f"Total issues across all files: {len(all_issues)}")

    # Group by severity
    by_severity = {}
    for issue in all_issues:
        sev = issue.severity.value
        by_severity[sev] = by_severity.get(sev, 0) + 1

    print("By severity:", by_severity)
    print()


if __name__ == "__main__":
    example_custom_analyzer()
    example_reporters()
    example_filtering()
    example_metrics()
    example_batch_processing()

    print("=" * 50)
    print("All advanced examples completed!")
    print("=" * 50)
