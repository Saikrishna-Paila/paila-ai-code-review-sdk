"""
Configuration for Paila SDK
===========================

Customize what and how Paila analyzes your code.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Set
from pathlib import Path
import os


@dataclass
class Config:
    """
    Configuration for the code reviewer.

    Example:
        config = Config(
            languages=["python", "javascript"],
            max_complexity=10,
            min_severity="medium",
            ignore_paths=["tests/", "node_modules/"]
        )
        reviewer = Reviewer(config=config)
    """

    # =========================================================================
    # Languages
    # =========================================================================
    languages: List[str] = field(default_factory=lambda: ["python"])

    # =========================================================================
    # Analyzers to run
    # =========================================================================
    analyzers: List[str] = field(default_factory=lambda: [
        "complexity",
        "security",
        "smells",
    ])

    # =========================================================================
    # Severity filtering
    # =========================================================================
    min_severity: str = "info"  # Minimum severity to report

    # =========================================================================
    # Complexity thresholds
    # =========================================================================
    max_complexity: int = 10  # Max cyclomatic complexity
    max_nesting_depth: int = 4  # Max nesting levels
    max_function_lines: int = 50  # Max lines per function
    max_file_lines: int = 500  # Max lines per file
    max_line_length: int = 120  # Max characters per line
    max_parameters: int = 5  # Max function parameters

    # =========================================================================
    # Maintainability thresholds
    # =========================================================================
    min_maintainability: float = 20.0  # Minimum maintainability index

    # =========================================================================
    # Ignore patterns
    # =========================================================================
    ignore_paths: List[str] = field(default_factory=lambda: [
        "node_modules/",
        ".git/",
        "__pycache__/",
        ".venv/",
        "venv/",
        "env/",
        ".env/",
        "dist/",
        "build/",
        ".eggs/",
        "*.egg-info/",
        ".tox/",
        ".pytest_cache/",
        ".mypy_cache/",
        ".coverage",
        "htmlcov/",
    ])

    ignore_files: List[str] = field(default_factory=lambda: [
        "*.pyc",
        "*.pyo",
        "*.so",
        "*.dll",
        "*.exe",
        "*.log",
        "*.lock",
        "*.min.js",
        "*.min.css",
    ])

    # Files/patterns to always include even if in ignore list
    include_patterns: List[str] = field(default_factory=list)

    # =========================================================================
    # AI Settings
    # =========================================================================
    ai_enabled: bool = False
    ai_model: str = "claude-sonnet-4-20250514"
    ai_api_key: Optional[str] = None  # Will try env var if not set
    ai_explain: bool = True  # Generate explanations
    ai_fix: bool = True  # Generate fix suggestions
    ai_max_issues: int = 20  # Max issues to send to AI (cost control)

    # =========================================================================
    # Output settings
    # =========================================================================
    output_format: str = "terminal"  # terminal, json, markdown, html
    verbose: bool = False
    show_code_snippets: bool = True
    max_code_snippet_lines: int = 5

    # =========================================================================
    # Caching
    # =========================================================================
    cache_enabled: bool = True
    cache_dir: Optional[str] = None

    def __post_init__(self):
        """Validate configuration after initialization."""
        # Get AI API key from environment if not provided
        if self.ai_enabled and not self.ai_api_key:
            self.ai_api_key = (
                os.getenv("ANTHROPIC_API_KEY") or
                os.getenv("OPENAI_API_KEY") or
                os.getenv("PAILA_API_KEY")
            )

        # Validate min_severity
        valid_severities = {"critical", "high", "medium", "low", "info"}
        if self.min_severity.lower() not in valid_severities:
            raise ValueError(
                f"Invalid min_severity: {self.min_severity}. "
                f"Must be one of: {valid_severities}"
            )

        # Validate output_format
        valid_formats = {"terminal", "json", "markdown", "html"}
        if self.output_format.lower() not in valid_formats:
            raise ValueError(
                f"Invalid output_format: {self.output_format}. "
                f"Must be one of: {valid_formats}"
            )

    @property
    def severity_order(self) -> List[str]:
        """Get severity levels in order."""
        return ["critical", "high", "medium", "low", "info"]

    @property
    def min_severity_index(self) -> int:
        """Get index of minimum severity to report."""
        return self.severity_order.index(self.min_severity.lower())

    def should_report_severity(self, severity: str) -> bool:
        """Check if a severity level should be reported."""
        severity_index = self.severity_order.index(severity.lower())
        return severity_index <= self.min_severity_index

    def should_ignore_path(self, path: str) -> bool:
        """Check if a path should be ignored."""
        path_obj = Path(path)

        # Check include patterns first (override ignore)
        for pattern in self.include_patterns:
            if path_obj.match(pattern):
                return False

        # Check ignore paths
        for ignore in self.ignore_paths:
            if ignore in path or path_obj.match(ignore):
                return True

        # Check ignore files
        for ignore in self.ignore_files:
            if path_obj.match(ignore):
                return True

        return False

    def get_file_extensions(self) -> Set[str]:
        """Get file extensions to analyze based on languages."""
        extension_map = {
            "python": {".py", ".pyw"},
            "javascript": {".js", ".jsx", ".mjs"},
            "typescript": {".ts", ".tsx"},
            "java": {".java"},
            "go": {".go"},
            "rust": {".rs"},
            "c": {".c", ".h"},
            "cpp": {".cpp", ".hpp", ".cc", ".cxx"},
            "csharp": {".cs"},
            "ruby": {".rb"},
            "php": {".php"},
        }

        extensions = set()
        for lang in self.languages:
            if lang.lower() in extension_map:
                extensions.update(extension_map[lang.lower()])

        return extensions

    def to_dict(self) -> dict:
        """Convert config to dictionary."""
        return {
            "languages": self.languages,
            "analyzers": self.analyzers,
            "min_severity": self.min_severity,
            "max_complexity": self.max_complexity,
            "max_nesting_depth": self.max_nesting_depth,
            "max_function_lines": self.max_function_lines,
            "max_file_lines": self.max_file_lines,
            "max_line_length": self.max_line_length,
            "max_parameters": self.max_parameters,
            "min_maintainability": self.min_maintainability,
            "ignore_paths": self.ignore_paths,
            "ai_enabled": self.ai_enabled,
            "ai_model": self.ai_model,
            "output_format": self.output_format,
        }

    @classmethod
    def from_file(cls, path: str) -> "Config":
        """Load configuration from a file (YAML or JSON)."""
        import json
        from pathlib import Path

        path_obj = Path(path)

        if not path_obj.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        content = path_obj.read_text()

        if path.endswith(".json"):
            data = json.loads(content)
        elif path.endswith((".yml", ".yaml")):
            try:
                import yaml
                data = yaml.safe_load(content)
            except ImportError:
                raise ImportError("PyYAML required for YAML config files")
        else:
            raise ValueError(f"Unsupported config format: {path}")

        return cls(**data)

    @classmethod
    def strict(cls) -> "Config":
        """Create a strict configuration for rigorous code review."""
        return cls(
            min_severity="low",
            max_complexity=7,
            max_nesting_depth=3,
            max_function_lines=30,
            max_file_lines=300,
            max_line_length=100,
            max_parameters=4,
            min_maintainability=50.0,
        )

    @classmethod
    def relaxed(cls) -> "Config":
        """Create a relaxed configuration for less strict review."""
        return cls(
            min_severity="high",
            max_complexity=15,
            max_nesting_depth=6,
            max_function_lines=100,
            max_file_lines=1000,
            max_line_length=150,
            max_parameters=8,
            min_maintainability=10.0,
        )

    @classmethod
    def security_only(cls) -> "Config":
        """Create a configuration for security-focused review only."""
        return cls(
            analyzers=["security"],
            min_severity="medium",
        )
