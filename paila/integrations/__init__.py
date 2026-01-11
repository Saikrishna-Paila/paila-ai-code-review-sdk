"""
Integrations for Paila SDK
==========================

External service integrations for CI/CD and version control.
"""

from .github import GitHubIntegration
from .gitlab import GitLabIntegration
from .base import BaseIntegration

__all__ = [
    "BaseIntegration",
    "GitHubIntegration",
    "GitLabIntegration",
]
