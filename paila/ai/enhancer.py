"""
AI Enhancer
===========

Enhances code review results with AI-powered explanations and fixes.
"""

import os
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from .prompts import ReviewPrompts
from ..models import Issue, FileResult, ReviewResult


@dataclass
class AIExplanation:
    """AI-generated explanation for an issue."""
    explanation: str
    impact: str
    priority: str


@dataclass
class AIFix:
    """AI-generated fix for an issue."""
    fixed_code: str
    explanation: str


class AIEnhancer:
    """
    Enhances code review results with AI-powered insights.

    Usage:
        enhancer = AIEnhancer(api_key="your-key")

        # Explain an issue
        explanation = enhancer.explain_issue(issue)

        # Suggest a fix
        fix = enhancer.suggest_fix(issue)

        # Enhance entire result
        enhanced = enhancer.enhance_result(result)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-20250514",
        provider: str = "anthropic",
    ):
        """
        Initialize the AI Enhancer.

        Args:
            api_key: API key (uses ANTHROPIC_API_KEY or OPENAI_API_KEY env var if not provided)
            model: Model to use
            provider: AI provider ("anthropic" or "openai")
        """
        self.provider = provider
        self.model = model
        self._client = None

        # Get API key
        if api_key:
            self.api_key = api_key
        elif provider == "anthropic":
            self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        else:
            self.api_key = os.environ.get("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError(
                f"API key required. Set {provider.upper()}_API_KEY environment variable "
                f"or pass api_key parameter."
            )

    @property
    def client(self):
        """Lazy-load the API client."""
        if self._client is None:
            self._client = self._create_client()
        return self._client

    def _create_client(self):
        """Create the appropriate API client."""
        if self.provider == "anthropic":
            try:
                import anthropic
                return anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "anthropic package required. Install with: pip install anthropic"
                )
        else:
            try:
                import openai
                return openai.OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "openai package required. Install with: pip install openai"
                )

    def _call_ai(self, prompt: str, max_tokens: int = 1024) -> str:
        """Call the AI API with a prompt."""
        if self.provider == "anthropic":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        else:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content

    def explain_issue(self, issue: Issue, code_context: str = "") -> AIExplanation:
        """
        Get AI explanation for an issue.

        Args:
            issue: The issue to explain
            code_context: Additional code context

        Returns:
            AIExplanation with details
        """
        prompt = ReviewPrompts.EXPLAIN_ISSUE.format(
            issue_type=issue.type,
            severity=issue.severity.value,
            message=issue.message,
            rule=issue.rule or "N/A",
            code=issue.code or code_context,
            file=issue.file,
            line=issue.line,
        )

        response = self._call_ai(prompt)

        # Parse response into structured format
        return AIExplanation(
            explanation=response,
            impact=ReviewPrompts.EXPLAIN_SEVERITY.get(issue.severity.value, ""),
            priority=issue.severity.value,
        )

    def suggest_fix(self, issue: Issue, code_context: str = "") -> AIFix:
        """
        Get AI-suggested fix for an issue.

        Args:
            issue: The issue to fix
            code_context: Additional code context

        Returns:
            AIFix with corrected code
        """
        prompt = ReviewPrompts.SUGGEST_FIX.format(
            issue_type=issue.type,
            severity=issue.severity.value,
            message=issue.message,
            rule=issue.rule or "N/A",
            code=issue.code or code_context,
            suggestion=issue.suggestion or "No suggestion provided",
        )

        response = self._call_ai(prompt)

        # Parse response
        fixed_code = ""
        explanation = response

        if "FIXED CODE:" in response:
            parts = response.split("FIXED CODE:")
            if len(parts) > 1:
                code_part = parts[1]
                if "```" in code_part:
                    # Extract code from markdown code block
                    start = code_part.find("```")
                    end = code_part.find("```", start + 3)
                    if end > start:
                        fixed_code = code_part[start:end+3]
                        # Remove language identifier if present
                        if fixed_code.startswith("```python"):
                            fixed_code = "```" + fixed_code[9:]

                if "EXPLANATION:" in code_part:
                    explanation = code_part.split("EXPLANATION:")[-1].strip()

        return AIFix(
            fixed_code=fixed_code,
            explanation=explanation,
        )

    def enhance_issue(self, issue: Issue, code_context: str = "") -> Dict[str, Any]:
        """
        Enhance an issue with AI explanation and fix.

        Args:
            issue: The issue to enhance
            code_context: Additional code context

        Returns:
            Dictionary with enhanced issue data
        """
        explanation = self.explain_issue(issue, code_context)
        fix = self.suggest_fix(issue, code_context)

        return {
            "issue": issue,
            "ai_explanation": explanation.explanation,
            "ai_impact": explanation.impact,
            "ai_fix": fix.fixed_code,
            "ai_fix_explanation": fix.explanation,
        }

    def enhance_result(
        self,
        result: FileResult,
        max_issues: int = 10
    ) -> Dict[str, Any]:
        """
        Enhance a file result with AI insights.

        Args:
            result: FileResult to enhance
            max_issues: Maximum number of issues to enhance (to limit API calls)

        Returns:
            Enhanced result dictionary
        """
        enhanced_issues = []

        # Sort by severity to enhance most important first
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        sorted_issues = sorted(
            result.issues,
            key=lambda i: severity_order.get(i.severity.value, 5)
        )

        for issue in sorted_issues[:max_issues]:
            try:
                enhanced = self.enhance_issue(issue)
                enhanced_issues.append(enhanced)
            except Exception as e:
                # If AI call fails, include issue without enhancement
                enhanced_issues.append({
                    "issue": issue,
                    "ai_error": str(e),
                })

        return {
            "file": result.file,
            "metrics": result.metrics,
            "enhanced_issues": enhanced_issues,
            "total_issues": len(result.issues),
            "enhanced_count": len([e for e in enhanced_issues if "ai_error" not in e]),
        }

    def summarize_review(self, result: ReviewResult) -> str:
        """
        Generate an AI summary of the review.

        Args:
            result: ReviewResult to summarize

        Returns:
            AI-generated summary
        """
        # Build severity breakdown
        severity_lines = []
        for sev in ["critical", "high", "medium", "low", "info"]:
            count = result.issues_by_severity.get(sev, 0)
            if count > 0:
                severity_lines.append(f"- {sev.upper()}: {count}")
        severity_breakdown = "\n".join(severity_lines) if severity_lines else "None"

        # Build type breakdown
        type_lines = []
        for issue_type, count in sorted(
            result.issues_by_type.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]:
            type_lines.append(f"- {issue_type}: {count}")
        type_breakdown = "\n".join(type_lines) if type_lines else "None"

        # Get top issues
        all_issues: List[Issue] = []
        for f in result.files:
            all_issues.extend(f.issues)

        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        sorted_issues = sorted(
            all_issues,
            key=lambda i: severity_order.get(i.severity.value, 5)
        )[:5]

        top_issues_lines = []
        for issue in sorted_issues:
            top_issues_lines.append(
                f"- [{issue.severity.value.upper()}] {issue.message} ({issue.file}:{issue.line})"
            )
        top_issues = "\n".join(top_issues_lines) if top_issues_lines else "None"

        prompt = ReviewPrompts.SUMMARIZE_REVIEW.format(
            file_count=len([f for f in result.files if not f.skipped]),
            total_issues=result.total_issues,
            severity_breakdown=severity_breakdown,
            type_breakdown=type_breakdown,
            top_issues=top_issues,
        )

        return self._call_ai(prompt)

    def review_code_with_ai(self, code: str, file_path: str = "<string>") -> str:
        """
        Perform a full AI code review.

        Args:
            code: Source code to review
            file_path: File path for context

        Returns:
            AI-generated review
        """
        prompt = ReviewPrompts.REVIEW_CODE.format(
            code=code,
            file_path=file_path,
        )

        return self._call_ai(prompt, max_tokens=2048)
