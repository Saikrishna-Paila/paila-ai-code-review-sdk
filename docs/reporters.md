# Reporters

Paila SDK supports multiple output formats through reporters.

## Available Reporters

| Reporter | Extension | Use Case |
|----------|-----------|----------|
| `TerminalReporter` | `.txt` | Console output with colors |
| `JSONReporter` | `.json` | CI/CD integration, APIs |
| `MarkdownReporter` | `.md` | Documentation, GitHub |
| `HTMLReporter` | `.html` | Web reports, sharing |

---

## TerminalReporter

Colored console output with icons.

```python
from paila import Reviewer
from paila.reporters import TerminalReporter

reviewer = Reviewer()
result = reviewer.review_directory("./src")

# Create reporter
reporter = TerminalReporter()

# Print to console
reporter.print(result)

# Or get as string
output = reporter.format(result)
print(output)
```

### Options

```python
# Without colors (for logs)
reporter = TerminalReporter(use_colors=False)

# Without emoji icons
reporter = TerminalReporter(use_icons=False)

# Plain text
reporter = TerminalReporter(use_colors=False, use_icons=False)
```

### Sample Output

```
╔══════════════════════════════════════════════════════════╗
║  PAILA CODE REVIEW REPORT                                ║
╚══════════════════════════════════════════════════════════╝

📋 SUMMARY
----------------------------------------
  Files analyzed: 5
  Total issues: 12

  Score: 75/100 (Grade: C)

🎯 ISSUES BY SEVERITY
----------------------------------------
  🚨 CRITICAL: 1
  ❌ HIGH: 2
  ⚠️  MEDIUM: 4
  💡 LOW: 3
  ℹ️  INFO: 2
```

---

## JSONReporter

JSON output for programmatic use.

```python
from paila import Reviewer
from paila.reporters import JSONReporter

reviewer = Reviewer()
result = reviewer.review_directory("./src")

# Create reporter
reporter = JSONReporter()

# Get JSON string
json_output = reporter.format(result)

# Save to file
reporter.report(result, "report.json")
```

### Options

```python
# Custom indentation
reporter = JSONReporter(indent=4)

# Without metadata
reporter = JSONReporter(include_metadata=False)
```

### Sample Output

```json
{
  "summary": {
    "total_files": 5,
    "files_analyzed": 5,
    "total_issues": 12,
    "score": 75,
    "grade": "C"
  },
  "issues_by_severity": {
    "critical": 1,
    "high": 2,
    "medium": 4,
    "low": 3,
    "info": 2
  },
  "files": [
    {
      "file": "src/main.py",
      "issue_count": 3,
      "issues": [
        {
          "type": "sql_injection",
          "severity": "critical",
          "message": "Potential SQL injection",
          "line": 42
        }
      ]
    }
  ],
  "_metadata": {
    "generator": "paila",
    "version": "0.1.0",
    "timestamp": "2024-01-15T10:30:00"
  }
}
```

---

## MarkdownReporter

Markdown output for documentation.

```python
from paila import Reviewer
from paila.reporters import MarkdownReporter

reviewer = Reviewer()
result = reviewer.review_directory("./src")

# Create reporter
reporter = MarkdownReporter()

# Get markdown string
md_output = reporter.format(result)

# Save to file
reporter.report(result, "REVIEW.md")
```

### Options

```python
# With severity badges
reporter = MarkdownReporter(include_badges=True)

# With table of contents
reporter = MarkdownReporter(include_toc=True)
```

### Sample Output

```markdown
# 📋 Paila Code Review Report

*Generated on 2024-01-15 10:30:00*

## Summary

| Metric | Value |
|--------|-------|
| Files Analyzed | 5 |
| Total Issues | 12 |
| Lines of Code | 1,234 |

## Score

**75/100** (Grade: **C**)

`███████░░░`

## Issues by Severity

| Severity | Count |
|----------|-------|
| ![Critical](badge) Critical | 1 |
| ![High](badge) High | 2 |
```

---

## HTMLReporter

Beautiful HTML reports with inline CSS.

```python
from paila import Reviewer
from paila.reporters import HTMLReporter

reviewer = Reviewer()
result = reviewer.review_directory("./src")

# Create reporter
reporter = HTMLReporter()

# Get HTML string
html_output = reporter.format(result)

# Save to file
reporter.report(result, "report.html")
```

### Features

- Standalone HTML (no external CSS/JS needed)
- Responsive design
- Color-coded severity badges
- Visual score bar
- Expandable issue details

---

## CLI Output Formats

```bash
# Terminal (default)
paila review ./src

# JSON
paila review ./src --format json
paila review ./src --format json --output report.json

# Markdown
paila review ./src --format markdown
paila review ./src --format markdown --output REVIEW.md

# HTML
paila review ./src --format html
paila review ./src --format html --output report.html
```

---

## Custom Reporters

Create your own reporter:

```python
from paila.reporters import BaseReporter

class XMLReporter(BaseReporter):
    name = "xml"
    extension = ".xml"

    def format(self, result):
        # Convert result to XML
        xml = '<?xml version="1.0"?>\n'
        xml += '<review>\n'
        xml += f'  <score>{result.score}</score>\n'
        xml += f'  <issues count="{result.total_issues}">\n'

        for file_result in result.files:
            for issue in file_result.issues:
                xml += f'    <issue type="{issue.type}">\n'
                xml += f'      <severity>{issue.severity.value}</severity>\n'
                xml += f'      <message>{issue.message}</message>\n'
                xml += f'      <file>{issue.file}</file>\n'
                xml += f'      <line>{issue.line}</line>\n'
                xml += '    </issue>\n'

        xml += '  </issues>\n'
        xml += '</review>'
        return xml

# Use it
reporter = XMLReporter()
xml_output = reporter.format(result)
reporter.report(result, "report.xml")
```
