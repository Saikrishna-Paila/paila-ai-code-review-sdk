"""
Paila CLI
=========

Command-line interface for Paila code review.

Usage:
    paila review ./src
    paila review main.py --format json
    paila review . --ai
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from . import __version__
from .reviewer import Reviewer
from .config import Config
from .reporters import TerminalReporter, JSONReporter, MarkdownReporter, HTMLReporter


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="paila",
        description="AI-Powered Code Review SDK",
        epilog="Created by Saikrishna Paila"
    )

    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"Paila SDK v{__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Review command
    review_parser = subparsers.add_parser(
        "review",
        help="Review code for issues"
    )
    review_parser.add_argument(
        "path",
        type=str,
        help="File or directory to review"
    )
    review_parser.add_argument(
        "--format", "-f",
        choices=["terminal", "json", "markdown", "html"],
        default="terminal",
        help="Output format (default: terminal)"
    )
    review_parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file path"
    )
    review_parser.add_argument(
        "--analyzers", "-a",
        type=str,
        help="Comma-separated list of analyzers to use"
    )
    review_parser.add_argument(
        "--min-severity",
        choices=["critical", "high", "medium", "low", "info"],
        default="info",
        help="Minimum severity to report"
    )
    review_parser.add_argument(
        "--no-parallel",
        action="store_true",
        help="Disable parallel processing"
    )
    review_parser.add_argument(
        "--ai",
        action="store_true",
        help="Enable AI-powered explanations"
    )
    review_parser.add_argument(
        "--strict",
        action="store_true",
        help="Use strict configuration"
    )
    review_parser.add_argument(
        "--relaxed",
        action="store_true",
        help="Use relaxed configuration"
    )
    review_parser.add_argument(
        "--security-only",
        action="store_true",
        help="Only run security analyzer"
    )

    # Check command (quick check)
    check_parser = subparsers.add_parser(
        "check",
        help="Quick check with pass/fail exit code"
    )
    check_parser.add_argument(
        "path",
        type=str,
        help="File or directory to check"
    )
    check_parser.add_argument(
        "--fail-on",
        choices=["critical", "high", "medium", "low", "info"],
        default="high",
        help="Minimum severity to fail on"
    )

    # Init command
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize Paila configuration file"
    )

    return parser


def get_reporter(format_type: str):
    """Get the appropriate reporter."""
    reporters = {
        "terminal": TerminalReporter(),
        "json": JSONReporter(),
        "markdown": MarkdownReporter(),
        "html": HTMLReporter(),
    }
    return reporters.get(format_type, TerminalReporter())


def cmd_review(args) -> int:
    """Handle the review command."""
    path = Path(args.path)

    if not path.exists():
        print(f"Error: Path not found: {args.path}")
        return 1

    # Create config
    if args.strict:
        config = Config.strict()
    elif args.relaxed:
        config = Config.relaxed()
    elif args.security_only:
        config = Config.security_only()
    else:
        config = Config()

    # Override analyzers if specified
    if args.analyzers:
        config.analyzers = args.analyzers.split(",")

    # Set minimum severity
    from .models import Severity
    config.min_severity = Severity(args.min_severity)

    # AI settings
    if args.ai:
        config.ai_enabled = True

    # Create reviewer
    reviewer = Reviewer(config=config)

    # Run review
    print(f"Reviewing: {path}")
    print()

    try:
        if path.is_file():
            result = reviewer.review_file(path)
        else:
            result = reviewer.review_directory(
                path,
                parallel=not args.no_parallel
            )
    except Exception as e:
        print(f"Error: {e}")
        return 1

    # Format output
    reporter = get_reporter(args.format)
    output = reporter.format(result)

    # Write output
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Report written to: {args.output}")
    else:
        print(output)

    # Return exit code based on issues
    if hasattr(result, "total_issues"):
        return 0 if result.total_issues == 0 else 1
    else:
        return 0 if len(result.issues) == 0 else 1


def cmd_check(args) -> int:
    """Handle the check command."""
    path = Path(args.path)

    if not path.exists():
        print(f"Error: Path not found: {args.path}")
        return 1

    # Create reviewer
    reviewer = Reviewer()

    # Run review
    try:
        if path.is_file():
            result = reviewer.review_file(path)
            issues = result.issues
        else:
            result = reviewer.review_directory(path)
            issues = []
            for f in result.files:
                issues.extend(f.issues)
    except Exception as e:
        print(f"Error: {e}")
        return 1

    # Filter by fail-on severity
    severity_order = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
        "info": 4,
    }
    fail_level = severity_order.get(args.fail_on, 1)

    failing_issues = [
        i for i in issues
        if severity_order.get(i.severity.value, 4) <= fail_level
    ]

    if failing_issues:
        print(f"FAILED: {len(failing_issues)} issue(s) at {args.fail_on} or above")
        for issue in failing_issues[:5]:
            print(f"  - [{issue.severity.value.upper()}] {issue.message}")
        if len(failing_issues) > 5:
            print(f"  ... and {len(failing_issues) - 5} more")
        return 1
    else:
        print("PASSED: No issues found at the specified severity level")
        return 0


def cmd_init(args) -> int:
    """Handle the init command."""
    config_content = """# Paila Configuration
# See https://github.com/saikrishnapaila/paila for documentation

[paila]
# Analyzers to enable
analyzers = ["complexity", "security", "smells"]

# Minimum severity to report
min_severity = "info"

# Complexity thresholds
max_complexity = 10
max_nesting_depth = 4
max_function_lines = 50
max_parameters = 5
max_line_length = 120
max_file_lines = 500

# Ignore patterns
ignore_patterns = [
    "__pycache__",
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
]

# AI settings (optional)
# ai_enabled = false
# ai_model = "claude-sonnet-4-20250514"
"""

    config_file = Path(".paila.toml")

    if config_file.exists():
        print("Configuration file already exists: .paila.toml")
        return 1

    config_file.write_text(config_content)
    print("Created: .paila.toml")
    print("Customize this file for your project settings.")
    return 0


def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "review":
        return cmd_review(args)
    elif args.command == "check":
        return cmd_check(args)
    elif args.command == "init":
        return cmd_init(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
