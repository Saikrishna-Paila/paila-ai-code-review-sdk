"""
AI Prompts for Code Review
==========================

Structured prompts for AI-powered code analysis.
"""


class ReviewPrompts:
    """Collection of prompts for AI-powered code review."""

    EXPLAIN_ISSUE = """You are a code review expert. Explain the following issue found in Python code.

Issue Type: {issue_type}
Severity: {severity}
Message: {message}
Rule: {rule}

Code Context:
```python
{code}
```

File: {file}:{line}

Please provide:
1. A clear explanation of why this is a problem (2-3 sentences)
2. The potential impact or risk
3. Why this matters for code quality

Keep your response concise and developer-friendly."""

    SUGGEST_FIX = """You are a code review expert. Suggest a fix for the following issue.

Issue Type: {issue_type}
Severity: {severity}
Message: {message}
Rule: {rule}

Original Code:
```python
{code}
```

Current Suggestion: {suggestion}

Please provide:
1. The corrected code that fixes this issue
2. A brief explanation of the changes made (1-2 sentences)

Format your response as:
FIXED CODE:
```python
<your corrected code here>
```

EXPLANATION:
<your brief explanation>"""

    REVIEW_CODE = """You are an expert code reviewer analyzing Python code.
Review the following code and identify any issues.

```python
{code}
```

File: {file_path}

Focus on:
1. Security vulnerabilities
2. Code complexity issues
3. Code smells and anti-patterns
4. Potential bugs
5. Performance issues

For each issue found, provide:
- Type of issue
- Severity (critical/high/medium/low/info)
- Line number
- Description
- Suggested fix

Be thorough but avoid false positives."""

    SUMMARIZE_REVIEW = """You are a code review expert. Summarize the following code review results.

Files Analyzed: {file_count}
Total Issues: {total_issues}

Issues by Severity:
{severity_breakdown}

Issues by Type:
{type_breakdown}

Top Issues:
{top_issues}

Provide a brief executive summary (3-5 sentences) that:
1. Highlights the most critical findings
2. Identifies patterns or recurring issues
3. Suggests prioritization for fixes
4. Gives an overall assessment of code quality

Keep the tone professional and constructive."""

    PRIORITIZE_ISSUES = """You are a code review expert. Help prioritize the following issues.

{issues_list}

Consider:
1. Security impact (critical first)
2. Potential for bugs
3. Ease of fix
4. Technical debt implications

Provide a prioritized list with brief reasoning for each item's priority."""

    EXPLAIN_SEVERITY = {
        "critical": "This is a CRITICAL issue that could lead to security vulnerabilities, data loss, or system crashes. Fix immediately.",
        "high": "This is a HIGH severity issue that significantly impacts code quality or could cause bugs. Fix as soon as possible.",
        "medium": "This is a MEDIUM severity issue that affects maintainability or best practices. Plan to fix soon.",
        "low": "This is a LOW severity issue related to style or minor improvements. Fix when convenient.",
        "info": "This is an informational note. Consider addressing but not critical.",
    }
