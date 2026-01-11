"""
GitLab Integration
==================

Integration with GitLab for MR comments and pipelines.
"""

import os
import json
from typing import Optional, List, Dict, Any
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import quote

from .base import BaseIntegration
from ..models import ReviewResult, Issue


class GitLabIntegration(BaseIntegration):
    """
    GitLab integration for posting review comments on merge requests.

    Usage:
        gitlab = GitLabIntegration(token="glpat-xxx")
        gitlab.post_review(result, project_id=123, mr_iid=45)
    """

    name = "gitlab"

    def __init__(
        self,
        token: Optional[str] = None,
        base_url: str = "https://gitlab.com/api/v4",
    ):
        """
        Initialize GitLab integration.

        Args:
            token: GitLab personal access token or CI_JOB_TOKEN
            base_url: GitLab API base URL
        """
        self.token = token or os.environ.get("GITLAB_TOKEN") or os.environ.get("CI_JOB_TOKEN")
        self.base_url = base_url.rstrip("/")

        if not self.token:
            raise ValueError(
                "GitLab token required. Set GITLAB_TOKEN environment variable "
                "or pass token parameter."
            )

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None
    ) -> Any:
        """Make API request to GitLab."""
        url = f"{self.base_url}{endpoint}"

        headers = {
            "PRIVATE-TOKEN": self.token,
            "Content-Type": "application/json",
        }

        body = json.dumps(data).encode() if data else None

        request = Request(url, data=body, headers=headers, method=method)

        try:
            with urlopen(request) as response:
                content = response.read().decode()
                return json.loads(content) if content else {}
        except HTTPError as e:
            error_body = e.read().decode()
            raise Exception(f"GitLab API error: {e.code} - {error_body}")

    def post_review(
        self,
        result: ReviewResult,
        project_id: int,
        mr_iid: int,
        include_inline: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post review as MR comment.

        Args:
            result: Review result
            project_id: GitLab project ID
            mr_iid: Merge request IID
            include_inline: Include inline discussions

        Returns:
            API response data
        """
        # Post summary comment
        comment_body = self.format_comment(result)
        comment_response = self._post_note(project_id, mr_iid, comment_body)

        responses = {"summary_comment": comment_response}

        # Post inline discussions for critical/high issues
        if include_inline:
            inline_responses = self._post_inline_discussions(
                project_id, mr_iid, result
            )
            responses["inline_discussions"] = inline_responses

        return responses

    def _post_note(
        self,
        project_id: int,
        mr_iid: int,
        body: str
    ) -> Dict[str, Any]:
        """Post a note on an MR."""
        endpoint = f"/projects/{project_id}/merge_requests/{mr_iid}/notes"
        return self._request("POST", endpoint, {"body": body})

    def _post_inline_discussions(
        self,
        project_id: int,
        mr_iid: int,
        result: ReviewResult
    ) -> List[Dict[str, Any]]:
        """Post inline discussions for issues."""
        responses = []

        # Get MR details
        mr_info = self._request(
            "GET",
            f"/projects/{project_id}/merge_requests/{mr_iid}"
        )

        # Get diff refs
        diff_refs = mr_info.get("diff_refs", {})
        head_sha = diff_refs.get("head_sha")
        base_sha = diff_refs.get("base_sha")

        if not head_sha or not base_sha:
            return responses

        # Collect critical and high severity issues
        critical_issues = []
        for file_result in result.files:
            for issue in file_result.issues:
                if issue.severity.value in ["critical", "high"]:
                    critical_issues.append(issue)

        # Post discussions
        for issue in critical_issues[:20]:
            try:
                comment_body = self.format_inline_comment(issue)
                response = self._request(
                    "POST",
                    f"/projects/{project_id}/merge_requests/{mr_iid}/discussions",
                    {
                        "body": comment_body,
                        "position": {
                            "base_sha": base_sha,
                            "start_sha": base_sha,
                            "head_sha": head_sha,
                            "position_type": "text",
                            "new_path": issue.file,
                            "new_line": issue.line,
                        }
                    }
                )
                responses.append(response)
            except Exception as e:
                responses.append({"error": str(e), "issue": issue.message})

        return responses

    def get_changed_files(
        self,
        project_id: int,
        mr_iid: int,
        **kwargs
    ) -> List[str]:
        """
        Get list of changed files in an MR.

        Args:
            project_id: GitLab project ID
            mr_iid: Merge request IID

        Returns:
            List of changed file paths
        """
        endpoint = f"/projects/{project_id}/merge_requests/{mr_iid}/changes"
        response = self._request("GET", endpoint)

        changes = response.get("changes", [])
        return [c.get("new_path") or c.get("old_path") for c in changes if c]

    def update_commit_status(
        self,
        project_id: int,
        sha: str,
        result: ReviewResult,
        name: str = "paila"
    ) -> Dict[str, Any]:
        """
        Update commit status with review results.

        Args:
            project_id: GitLab project ID
            sha: Commit SHA
            result: Review result
            name: Status name

        Returns:
            API response
        """
        # Determine state
        if result.issues_by_severity.get("critical", 0) > 0:
            state = "failed"
        elif result.issues_by_severity.get("high", 0) > 0:
            state = "failed"
        else:
            state = "success"

        description = f"Score: {result.score}/100 - {result.total_issues} issues"

        endpoint = f"/projects/{project_id}/statuses/{sha}"
        return self._request("POST", endpoint, {
            "state": state,
            "name": name,
            "description": description[:255],  # GitLab limit
        })

    def get_mr_info(
        self,
        project_id: int,
        mr_iid: int
    ) -> Dict[str, Any]:
        """
        Get merge request information.

        Args:
            project_id: GitLab project ID
            mr_iid: Merge request IID

        Returns:
            MR information dictionary
        """
        endpoint = f"/projects/{project_id}/merge_requests/{mr_iid}"
        return self._request("GET", endpoint)

    def get_project_id_by_path(self, project_path: str) -> int:
        """
        Get project ID from path.

        Args:
            project_path: Project path (e.g., "group/project")

        Returns:
            Project ID
        """
        encoded_path = quote(project_path, safe="")
        endpoint = f"/projects/{encoded_path}"
        response = self._request("GET", endpoint)
        return response.get("id")

    @classmethod
    def from_ci_environment(cls) -> "GitLabIntegration":
        """
        Create integration from GitLab CI environment variables.

        Returns:
            Configured GitLabIntegration instance
        """
        ci_server_url = os.environ.get("CI_SERVER_URL", "https://gitlab.com")
        base_url = f"{ci_server_url}/api/v4"

        return cls(base_url=base_url)
