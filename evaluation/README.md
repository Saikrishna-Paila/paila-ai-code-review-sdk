# Paila SDK Evaluation

This folder contains all the test scripts and results from evaluating the Paila SDK.

## Structure

```
evaluation/
├── README.md                    # This file
├── RESULTS.md                   # Detailed test results summary
├── run_all_tests.py             # Master test runner
│
├── 01_test_core_modules.py      # Test Reviewer, Config, Models
├── 02_test_analyzers.py         # Test Security, Complexity, Smells
├── 03_test_reporters.py         # Test Terminal, JSON, Markdown, HTML
├── 04_test_ai_providers.py      # Test Anthropic, OpenAI, Groq
├── 05_test_integrations.py      # Test GitHub, GitLab
├── 06_test_parsers_utils.py     # Test Parsers and Utils
├── 07_test_rules.py             # Test Rule, RuleSet, RuleBuilder
└── 08_test_cli.py               # Test CLI commands
```

## Running Tests

### Run All Evaluation Tests

```bash
cd evaluation
python run_all_tests.py
```

### Run Individual Test

```bash
python 01_test_core_modules.py
python 02_test_analyzers.py
# ... etc
```

### Run Pytest Unit Tests

```bash
pytest ../tests/ -v
```

## Test Coverage

| Test Suite | What's Tested |
|------------|---------------|
| Core Modules | Reviewer, Config presets, Models (Issue, Metrics, FileResult, ReviewResult) |
| Analyzers | SecurityAnalyzer (7 rules), ComplexityAnalyzer (2 rules), SmellAnalyzer (10+ detections) |
| Reporters | TerminalReporter, JSONReporter, MarkdownReporter, HTMLReporter |
| AI Providers | AnthropicProvider, OpenAIProvider, GroqProvider, Message, AIResponse |
| Integrations | GitHubIntegration, GitLabIntegration |
| Parsers & Utils | PythonParser, file_utils, text_utils, hash_utils |
| Rules | Rule, RuleSet, RuleBuilder, SecurityRules, ComplexityRules, StyleRules |
| CLI | review, check, init commands with all options |

## Results

**All 9 test suites passed:**

- ✅ Core Modules
- ✅ Analyzers
- ✅ Reporters
- ✅ AI Providers
- ✅ Integrations
- ✅ Parsers & Utils
- ✅ Rules
- ✅ CLI
- ✅ Pytest (49 tests)

See [RESULTS.md](RESULTS.md) for detailed test output.
