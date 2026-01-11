# API Reference

Complete API documentation for Paila SDK.

---

## Core Classes

### Reviewer

Main class for code review.

```python
class Reviewer:
    def __init__(
        self,
        config: Optional[Config] = None,
        custom_analyzers: Optional[List[BaseAnalyzer]] = None,
    ) -> None
```

**Parameters:**
- `config`: Configuration options (uses defaults if not provided)
- `custom_analyzers`: Additional custom analyzers to use

**Methods:**

#### review_code

```python
def review_code(
    self,
    code: str,
    file_path: str = "<string>",
) -> FileResult
```

Review a code string.

**Parameters:**
- `code`: Source code to review
- `file_path`: Virtual file path for the code

**Returns:** `FileResult`

#### review_file

```python
def review_file(self, file_path: Union[str, Path]) -> FileResult
```

Review a single file.

**Parameters:**
- `file_path`: Path to the file to review

**Returns:** `FileResult`

**Raises:** `FileNotFoundError` if file doesn't exist

#### review_directory

```python
def review_directory(
    self,
    directory: Union[str, Path],
    recursive: bool = True,
    parallel: bool = True,
    max_workers: int = 4,
) -> ReviewResult
```

Review all files in a directory.

**Parameters:**
- `directory`: Path to directory
- `recursive`: Whether to include subdirectories
- `parallel`: Whether to process files in parallel
- `max_workers`: Number of parallel workers

**Returns:** `ReviewResult`

#### review

```python
def review(
    self,
    path: Union[str, Path],
    **kwargs
) -> Union[FileResult, ReviewResult]
```

Smart review - automatically detects if path is file or directory.

**Parameters:**
- `path`: Path to file or directory
- `**kwargs`: Additional arguments for `review_directory`

**Returns:** `FileResult` for files, `ReviewResult` for directories

---

### Config

Configuration class for Paila.

```python
@dataclass
class Config:
    languages: List[str] = field(default_factory=lambda: ["python"])
    analyzers: List[str] = field(default_factory=lambda: ["complexity", "security", "smells"])
    min_severity: Severity = Severity.INFO
    max_complexity: int = 10
    max_nesting_depth: int = 4
    max_function_lines: int = 50
    max_parameters: int = 5
    max_line_length: int = 120
    max_file_lines: int = 500
    ignore_patterns: List[str] = field(default_factory=list)
    ignore_files: List[str] = field(default_factory=list)
    ai_enabled: bool = False
    ai_model: str = "claude-sonnet-4-20250514"
    ai_api_key: Optional[str] = None
    verbose: bool = False
```

**Class Methods:**

```python
@classmethod
def strict(cls) -> "Config"      # Strict settings
@classmethod
def relaxed(cls) -> "Config"     # Relaxed settings
@classmethod
def security_only(cls) -> "Config"  # Security only
```

---

## Data Models

### Issue

Represents a single issue found during code review.

```python
@dataclass
class Issue:
    type: str
    severity: Severity
    file: str
    line: int
    message: str
    code: str = ""
    column: int = 0
    end_line: Optional[int] = None
    end_column: Optional[int] = None
    suggestion: str = ""
    rule: str = ""
    ai_explanation: Optional[str] = None
    ai_fix: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
```

**Methods:**
- `to_dict() -> Dict[str, Any]`: Convert to dictionary

### Severity

Issue severity levels.

```python
class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"
```

**Properties:**
- `color: str`: Color for terminal output
- `emoji: str`: Emoji representation

### Metrics

Code quality metrics.

```python
@dataclass
class Metrics:
    lines_of_code: int = 0
    total_lines: int = 0
    blank_lines: int = 0
    comment_lines: int = 0
    functions: int = 0
    classes: int = 0
    avg_complexity: float = 0.0
    max_complexity: int = 0
    maintainability_index: float = 100.0
    comment_ratio: float = 0.0
    duplication_ratio: float = 0.0
```

**Methods:**
- `to_dict() -> Dict[str, Any]`: Convert to dictionary

### FileResult

Result of reviewing a single file.

```python
@dataclass
class FileResult:
    file: str
    issues: List[Issue] = field(default_factory=list)
    metrics: Optional[Metrics] = None
    skipped: bool = False
    error: Optional[str] = None
```

**Properties:**
- `issue_count: int`: Number of issues
- `critical_count: int`: Number of critical issues
- `high_count: int`: Number of high severity issues

### ReviewResult

Complete result of a code review.

```python
@dataclass
class ReviewResult:
    files: List[FileResult] = field(default_factory=list)
    total_issues: int = 0
    issues_by_severity: Dict[str, int] = field(default_factory=dict)
    issues_by_type: Dict[str, int] = field(default_factory=dict)
    issues_by_file: Dict[str, List[Issue]] = field(default_factory=dict)
    metrics: Optional[Metrics] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    duration_seconds: float = 0.0
```

**Properties:**
- `score: int`: Overall score (0-100)
- `grade: str`: Letter grade (A-F)
- `summary: str`: Human-readable summary

**Methods:**
- `to_dict() -> Dict[str, Any]`: Convert to dictionary
- `to_json(indent: int = 2) -> str`: Convert to JSON string

---

## Analyzers

### BaseAnalyzer

Abstract base class for all analyzers.

```python
class BaseAnalyzer(ABC):
    name: str = "base"
    description: str = "Base analyzer"

    def __init__(self, config: Optional[Config] = None) -> None

    @abstractmethod
    def analyze(
        self,
        code: str,
        file_path: str,
        tree: Optional[ast.AST] = None
    ) -> List[Issue]

    def parse_code(self, code: str) -> Optional[ast.AST]
    def get_code_line(self, code: str, line_number: int) -> str
    def get_code_snippet(self, code: str, start_line: int,
                         end_line: Optional[int] = None,
                         max_lines: int = 5) -> str
```

### ComplexityAnalyzer

```python
class ComplexityAnalyzer(BaseAnalyzer):
    name = "complexity"
    description = "Analyzes code complexity"

    def calculate_metrics(self, code: str,
                         tree: Optional[ast.AST] = None) -> Dict[str, Any]
```

### SecurityAnalyzer

```python
class SecurityAnalyzer(BaseAnalyzer):
    name = "security"
    description = "Detects security vulnerabilities"
```

### SmellAnalyzer

```python
class SmellAnalyzer(BaseAnalyzer):
    name = "smells"
    description = "Detects code smells"
```

---

## Reporters

### BaseReporter

Abstract base class for reporters.

```python
class BaseReporter(ABC):
    name: str = "base"
    extension: str = ".txt"

    @abstractmethod
    def format(self, result: Union[FileResult, ReviewResult]) -> str

    def report(self, result: Union[FileResult, ReviewResult],
               output: Optional[Union[str, Path, IO]] = None) -> str
```

### TerminalReporter

```python
class TerminalReporter(BaseReporter):
    def __init__(self, use_colors: bool = True, use_icons: bool = True)
    def print(self, result: Union[FileResult, ReviewResult]) -> None
```

### JSONReporter

```python
class JSONReporter(BaseReporter):
    def __init__(self, indent: int = 2, include_metadata: bool = True)
```

### MarkdownReporter

```python
class MarkdownReporter(BaseReporter):
    def __init__(self, include_badges: bool = True, include_toc: bool = False)
```

### HTMLReporter

```python
class HTMLReporter(BaseReporter):
    pass
```

---

## AI Module

### AIEnhancer

```python
class AIEnhancer:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-20250514",
        provider: str = "anthropic",
    )

    def explain_issue(self, issue: Issue,
                      code_context: str = "") -> AIExplanation
    def suggest_fix(self, issue: Issue,
                    code_context: str = "") -> AIFix
    def enhance_issue(self, issue: Issue,
                      code_context: str = "") -> Dict[str, Any]
    def enhance_result(self, result: FileResult,
                       max_issues: int = 10) -> Dict[str, Any]
    def summarize_review(self, result: ReviewResult) -> str
    def review_code_with_ai(self, code: str,
                            file_path: str = "<string>") -> str
```

---

## Convenience Functions

```python
def review(path: Union[str, Path], **kwargs) -> Union[FileResult, ReviewResult]
def review_code(code: str, **kwargs) -> FileResult
def calculate_grade(score: int) -> str
def calculate_score(issues: List[Issue], metrics: Optional[Metrics] = None) -> int
```
