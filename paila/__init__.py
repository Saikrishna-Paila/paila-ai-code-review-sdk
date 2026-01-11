"""
PAILA SDK - AI-Powered Code Review SDK
======================================

Created by Saikrishna Paila

A powerful SDK for automated code review that detects:
- Security vulnerabilities
- Code complexity issues
- Code smells and anti-patterns
- Bugs and potential errors

Quick Start:
    from paila import Reviewer

    reviewer = Reviewer()
    result = reviewer.review("./my-project")

    print(result.summary)
    print(f"Score: {result.score}/100")

With AI:
    reviewer = Reviewer(ai_enabled=True)
    result = reviewer.review("./my-project")

    for issue in result.issues:
        print(issue.ai_explanation)
        print(issue.ai_fix)

GitHub: https://github.com/saikrishnapaila/paila
"""

__version__ = "0.1.0"
__author__ = "Saikrishna Paila"

# Public API
from .reviewer import Reviewer, review, review_code
from .config import Config
from .models import Issue, Metrics, ReviewResult, FileResult, Severity

# Analyzers (for advanced users)
from .analyzers import (
    BaseAnalyzer,
    ComplexityAnalyzer,
    SecurityAnalyzer,
    SmellAnalyzer,
)

__all__ = [
    # Main classes
    "Reviewer",
    "Config",

    # Convenience functions
    "review",
    "review_code",

    # Data models
    "Issue",
    "Metrics",
    "ReviewResult",
    "FileResult",
    "Severity",

    # Analyzers
    "BaseAnalyzer",
    "ComplexityAnalyzer",
    "SecurityAnalyzer",
    "SmellAnalyzer",
]
