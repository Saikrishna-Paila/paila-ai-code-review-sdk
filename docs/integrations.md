# Integrations

Integrate Paila SDK with your development workflow.

## GitHub Integration

### GitHub Actions

Add code review to your CI/CD pipeline:

```yaml
# .github/workflows/code-review.yml
name: Code Review

on:
  pull_request:
    branches: [main, develop]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Paila
        run: pip install paila

      - name: Run Code Review
        run: paila check ./src --fail-on high

      - name: Generate Report
        if: always()
        run: paila review ./src --format markdown --output review.md

      - name: Upload Report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: code-review-report
          path: review.md
```

### Post Review as PR Comment

```yaml
# .github/workflows/pr-review.yml
name: PR Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Paila
        run: pip install paila

      - name: Run Review
        id: review
        run: |
          paila review ./src --format json --output review.json
          echo "issues=$(cat review.json | jq '.summary.total_issues')" >> $GITHUB_OUTPUT

      - name: Comment on PR
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const review = JSON.parse(fs.readFileSync('review.json', 'utf8'));

            const body = `## 🔍 Paila Code Review

            **Score:** ${review.summary.score}/100 (Grade: ${review.summary.grade})
            **Issues Found:** ${review.summary.total_issues}

            | Severity | Count |
            |----------|-------|
            | Critical | ${review.issues_by_severity.critical || 0} |
            | High | ${review.issues_by_severity.high || 0} |
            | Medium | ${review.issues_by_severity.medium || 0} |
            | Low | ${review.issues_by_severity.low || 0} |
            `;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            });
```

---

## GitLab CI Integration

```yaml
# .gitlab-ci.yml
code-review:
  stage: test
  image: python:3.11
  script:
    - pip install paila
    - paila check ./src --fail-on high
  artifacts:
    when: always
    paths:
      - review.json
    reports:
      codequality: review.json
```

---

## Pre-commit Hook

### Using pre-commit Framework

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: paila
        name: Paila Code Review
        entry: paila check
        language: system
        types: [python]
        args: [--fail-on, medium]
```

Install and run:

```bash
pip install pre-commit
pre-commit install
```

### Manual Git Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash

echo "Running Paila code review..."

# Get staged Python files
FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')

if [ -z "$FILES" ]; then
    exit 0
fi

# Run Paila on staged files
for file in $FILES; do
    paila check "$file" --fail-on high
    if [ $? -ne 0 ]; then
        echo "Code review failed for $file"
        exit 1
    fi
done

echo "Code review passed!"
exit 0
```

Make it executable:

```bash
chmod +x .git/hooks/pre-commit
```

---

## VS Code Integration

### Task Configuration

```json
// .vscode/tasks.json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Paila: Review Current File",
      "type": "shell",
      "command": "paila review ${file}",
      "problemMatcher": [],
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Paila: Review Workspace",
      "type": "shell",
      "command": "paila review ${workspaceFolder}/src --format html --output ${workspaceFolder}/review.html",
      "problemMatcher": []
    }
  ]
}
```

### Keyboard Shortcut

```json
// .vscode/keybindings.json
[
  {
    "key": "ctrl+shift+r",
    "command": "workbench.action.tasks.runTask",
    "args": "Paila: Review Current File"
  }
]
```

---

## Programmatic Integration

### In Your Python Application

```python
from paila import Reviewer, Config

def check_code_quality(code: str) -> dict:
    """Check code quality before processing."""
    reviewer = Reviewer(config=Config.strict())
    result = reviewer.review_code(code)

    return {
        "passed": len(result.issues) == 0,
        "score": 100 - (len(result.issues) * 5),
        "issues": [
            {
                "type": issue.type,
                "message": issue.message,
                "line": issue.line,
            }
            for issue in result.issues
        ]
    }

# Use it
code = '''
def process(data):
    return data
'''

quality = check_code_quality(code)
if not quality["passed"]:
    print(f"Code has {len(quality['issues'])} issues")
```

### REST API Wrapper

```python
from flask import Flask, request, jsonify
from paila import Reviewer

app = Flask(__name__)
reviewer = Reviewer()

@app.route('/review', methods=['POST'])
def review_code():
    code = request.json.get('code', '')
    file_path = request.json.get('file_path', 'code.py')

    result = reviewer.review_code(code, file_path)

    return jsonify({
        'score': result.metrics.lines_of_code,
        'issues': [
            {
                'type': i.type,
                'severity': i.severity.value,
                'message': i.message,
                'line': i.line,
            }
            for i in result.issues
        ]
    })

if __name__ == '__main__':
    app.run(port=5000)
```

---

## Docker Integration

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN pip install paila

ENTRYPOINT ["paila"]
CMD ["--help"]
```

Use it:

```bash
docker build -t paila .
docker run -v $(pwd):/code paila review /code/src
```

---

## Jupyter Notebook Integration

```python
# In a Jupyter cell
from paila import review_code
from IPython.display import display, HTML

def review_cell(code: str):
    """Review code and display results in notebook."""
    result = review_code(code)

    html = f"""
    <div style="padding: 10px; background: #f5f5f5; border-radius: 5px;">
        <h4>Code Review Results</h4>
        <p><strong>Issues:</strong> {len(result.issues)}</p>
        <p><strong>Functions:</strong> {result.metrics.functions}</p>
        <ul>
    """

    for issue in result.issues:
        color = {'critical': 'red', 'high': 'orange', 'medium': 'yellow'}.get(
            issue.severity.value, 'gray'
        )
        html += f'<li style="color: {color}">[{issue.severity.value}] {issue.message}</li>'

    html += "</ul></div>"

    display(HTML(html))

# Usage
review_cell("""
def process(x):
    return x * 3.14159
""")
```
