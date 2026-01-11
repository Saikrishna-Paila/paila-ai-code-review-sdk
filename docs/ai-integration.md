# AI Integration

Paila SDK integrates with AI models to provide intelligent explanations and fix suggestions.

## Supported Providers

| Provider | Models | API Key Env Var |
|----------|--------|-----------------|
| Anthropic | Claude Sonnet, Opus, Haiku | `ANTHROPIC_API_KEY` |
| OpenAI | GPT-4, GPT-3.5 | `OPENAI_API_KEY` |

## Quick Start

### 1. Set API Key

```bash
export ANTHROPIC_API_KEY="your-api-key"
# or
export OPENAI_API_KEY="your-api-key"
```

### 2. Enable AI Features

```python
from paila import Reviewer, Config

config = Config(ai_enabled=True)
reviewer = Reviewer(config=config)
```

## Using AIEnhancer

The `AIEnhancer` class provides AI-powered features:

```python
from paila import Reviewer
from paila.ai import AIEnhancer

# Create reviewer and get results
reviewer = Reviewer()
result = reviewer.review_file("my_code.py")

# Create AI enhancer
enhancer = AIEnhancer()  # Uses ANTHROPIC_API_KEY by default

# Explain an issue
for issue in result.issues:
    explanation = enhancer.explain_issue(issue)
    print(f"Issue: {issue.message}")
    print(f"Explanation: {explanation.explanation}")
    print()
```

## Explaining Issues

Get detailed explanations for issues:

```python
from paila.ai import AIEnhancer

enhancer = AIEnhancer()

# Get explanation
explanation = enhancer.explain_issue(issue)

print(explanation.explanation)  # Detailed explanation
print(explanation.impact)       # Impact description
print(explanation.priority)     # Priority level
```

## Suggesting Fixes

Get AI-generated fix suggestions:

```python
from paila.ai import AIEnhancer

enhancer = AIEnhancer()

# Get fix suggestion
fix = enhancer.suggest_fix(issue)

print(fix.fixed_code)    # Corrected code
print(fix.explanation)   # Why this fix works
```

## Enhancing Results

Enhance an entire review with AI insights:

```python
from paila.ai import AIEnhancer

enhancer = AIEnhancer()

# Enhance file result
enhanced = enhancer.enhance_result(result, max_issues=10)

for item in enhanced["enhanced_issues"]:
    issue = item["issue"]
    print(f"Issue: {issue.message}")
    print(f"AI Explanation: {item.get('ai_explanation', 'N/A')}")
    print(f"AI Fix: {item.get('ai_fix', 'N/A')}")
    print()
```

## Summarizing Reviews

Get an executive summary of the review:

```python
from paila.ai import AIEnhancer

enhancer = AIEnhancer()

# Get summary
summary = enhancer.summarize_review(result)
print(summary)
```

## Full AI Code Review

Perform a complete AI-powered review:

```python
from paila.ai import AIEnhancer

enhancer = AIEnhancer()

code = '''
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return execute(query)
'''

# Full AI review
ai_review = enhancer.review_code_with_ai(code, "db.py")
print(ai_review)
```

## Configuration Options

### Provider Selection

```python
# Use Anthropic (default)
enhancer = AIEnhancer(provider="anthropic")

# Use OpenAI
enhancer = AIEnhancer(provider="openai")
```

### Model Selection

```python
# Anthropic models
enhancer = AIEnhancer(
    provider="anthropic",
    model="claude-sonnet-4-20250514"  # or claude-opus-4-20250514
)

# OpenAI models
enhancer = AIEnhancer(
    provider="openai",
    model="gpt-4"  # or gpt-3.5-turbo
)
```

### API Key

```python
# Explicit API key
enhancer = AIEnhancer(api_key="your-key")

# Or use environment variable (recommended)
# ANTHROPIC_API_KEY or OPENAI_API_KEY
```

## CLI with AI

```bash
# Enable AI in CLI
paila review ./src --ai
```

## Cost Optimization

AI features make API calls which cost money. Tips to optimize:

1. **Limit issues enhanced**: Use `max_issues` parameter
2. **Use efficient models**: Claude Haiku or GPT-3.5 for simple tasks
3. **Cache results**: Store AI responses for repeated reviews
4. **Batch reviews**: Process multiple issues in one call when possible

```python
# Limit to top 5 issues
enhanced = enhancer.enhance_result(result, max_issues=5)
```

## Error Handling

```python
from paila.ai import AIEnhancer

try:
    enhancer = AIEnhancer()
    explanation = enhancer.explain_issue(issue)
except ValueError as e:
    print(f"Configuration error: {e}")
except ImportError as e:
    print(f"Missing package: {e}")
except Exception as e:
    print(f"API error: {e}")
```

## Custom Prompts

Access and customize prompts:

```python
from paila.ai.prompts import ReviewPrompts

# View available prompts
print(ReviewPrompts.EXPLAIN_ISSUE)
print(ReviewPrompts.SUGGEST_FIX)
print(ReviewPrompts.REVIEW_CODE)
print(ReviewPrompts.SUMMARIZE_REVIEW)
```
