"""
GitHub Integration
==================

Integration with GitHub for PR comments and checks.
"""

import os
import json
from typing import Optional, List, Dict, Any
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from .base import BaseIntegration
from ..models import ReviewResult, Issue


class GitHubIntegration(BaseIntegration):
    """
    GitHub integration for posting review comments.

    Usage:
        github = GitHubIntegration(token="ghp_xxx")
        github.post_review(result, owner="user", repo="repo", pr_number=123)
    """

    name = "github"

    def __init__(
        self,
        token: Optional[str] = None,
        base_url: str = "https://api.github.com",
    ):
        """
        Initialize GitHub integration.

        Args:
            token: GitHub personal access token or GITHUB_TOKEN
            base_url: GitHub API base URL (for Enterprise)
        """
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.base_url = base_url.rstrip("/")

        if not self.token:
            raise ValueError(
                "GitHub token required. Set GITHUB_TOKEN environment variable "
                "or pass token parameter."
            )

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make API request to GitHub."""
        url = f"{self.base_url}{endpoint}"

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
        }

        body = json.dumps(data).encode() if data else None

        request = Request(url, data=body, headers=headers, method=method)

        try:
            with urlopen(request) as response:
                return json.loads(response.read().decode())
        except HTTPError as e:
            error_body = e.read().decode()
            raise Exception(f"GitHub API error: {e.code} - {error_body}")

    def post_review(
        self,
        result: ReviewResult,
        owner: str,
        repo: str,
        pr_number: int,
        include_inline: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post review as PR comment.

        Args:
            result: Review result
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            include_inline: Include inline comments on specific lines

        Returns:
            API response data
        """
        # Post summary comment
        comment_body = self.format_comment(result)
        comment_response = self._post_comment(
            owner, repo, pr_number, comment_body
        )

        responses = {"summary_comment": comment_response}

        # Post inline comments for critical/high issues
        if include_inline:
            inline_responses = self._post_inline_comments(
                owner, repo, pr_number, result
            )
            responses["inline_comments"] = inline_responses

        return responses

    def _post_comment(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        body: str
    ) -> Dict[str, Any]:
        """Post a comment on a PR."""
        endpoint = f"/repos/{owner}/{repo}/issues/{pr_number}/comments"
        return self._request("POST", endpoint, {"body": body})

    def _post_inline_comments(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        result: ReviewResult
    ) -> List[Dict[str, Any]]:
        """Post inline comments for issues."""
        responses = []

        # Get PR details for commit SHA
        pr_info = self._request(
            "GET",
            f"/repos/{owner}/{repo}/pulls/{pr_number}"
        )
        commit_sha = pr_info.get("head", {}).get("sha")

        if not commit_sha:
            return responses

        # Collect critical and high severity issues
        critical_issues = []
        for file_result in result.files:
            for issue in file_result.issues:
                if issue.severity.value in ["critical", "high"]:
                    critical_issues.append(issue)

        # Post review comments
        for issue in critical_issues[:20]:  # Limit to 20 inline comments
            try:
                comment_body = self.format_inline_comment(issue)
                response = self._request(
                    "POST",
                    f"/repos/{owner}/{repo}/pulls/{pr_number}/comments",
                    {
                        "body": comment_body,
                        "commit_id": commit_sha,
                        "path": issue.file,
                        "line": issue.line,
                    }
                )
                responses.append(response)
            except Exception as e:
                # Continue if one comment fails
                responses.append({"error": str(e), "issue": issue.message})

        return responses

    def get_changed_files(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        **kwargs
    ) -> List[str]:
        """
        Get list of changed files in a PR.

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number

        Returns:
            List of changed file paths
        """
        endpoint = f"/repos/{owner}/{repo}/pulls/{pr_number}/files"
        files = self._request("GET", endpoint)

        return [f["filename"] for f in files if f.get("filename")]

    def create_check_run(
        self,
        owner: str,
        repo: str,
        head_sha: str,
        result: ReviewResult,
        name: str = "Paila Code Review"
    ) -> Dict[str, Any]:
        """
        Create a check run with review results.

        Args:
            owner: Repository owner
            repo: Repository name
            head_sha: Commit SHA
            result: Review result
            name: Check run name

        Returns:
            API response
        """
        # Determine conclusion
        if result.issues_by_severity.get("critical", 0) > 0:
            conclusion = "failure"
        elif result.issues_by_severity.get("high", 0) > 0:
            conclusion = "failure"
        else:
            conclusion = "success"

        # Build output
        summary = f"Score: {result.score}/100 (Grade: {result.grade})\n"
        summary += f"Total issues: {result.total_issues}"

        annotations = []
        for file_result in result.files:
            for issue in file_result.issues[:50]:  # Limit annotations
                annotations.append({
                    "path": issue.file,
                    "start_line": issue.line,
                    "end_line": issue.end_line or issue.line,
                    "annotation_level": self._severity_to_level(issue.severity.value),
                    "message": issue.message,
                    "title": issue.type,
                })

        endpoint = f"/repos/{owner}/{repo}/check-runs"
        return self._request("POST", endpoint, {
            "name": name,
            "head_sha": head_sha,
            "status": "completed",
            "conclusion": conclusion,
            "output": {
                "title": f"Code Review: {result.grade}",
                "summary": summary,
                "annotations": annotations[:50],  # GitHub limit
            }
        })

    def _severity_to_level(self, severity: str) -> str:
        """Convert severity to GitHub annotation level."""
        mapping = {
            "critical": "failure",
            "high": "failure",
            "medium": "warning",
            "low": "notice",
            "info": "notice",
        }
        return mapping.get(severity, "notice")

    def get_pr_info(
        self,
        owner: str,
        repo: str,
        pr_number: int
    ) -> Dict[str, Any]:
        """
        Get pull request information.

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number

        Returns:
            PR information dictionary
        """
        endpoint = f"/repos/{owner}/{repo}/pulls/{pr_number}"
        return self._request("GET", endpoint)
