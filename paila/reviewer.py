"""
Reviewer - Core Class
=====================

The main entry point for code review. Coordinates analyzers
and generates comprehensive review results.
"""

import ast
import os
from pathlib import Path
from typing import List, Optional, Union, Dict, Any, Set
from concurrent.futures import ThreadPoolExecutor, as_completed

from .config import Config
from .models import Issue, Metrics, ReviewResult, FileResult, Severity
from .analyzers import (
    BaseAnalyzer,
    ComplexityAnalyzer,
    SecurityAnalyzer,
    SmellAnalyzer,
)


class Reviewer:
    """
    Main code review class that coordinates all analyzers.

    Usage:
        # Simple usage
        reviewer = Reviewer()
        result = reviewer.review_file("my_code.py")
        print(result.summary)

        # Review entire directory
        result = reviewer.review_directory("./src")
        print(result.to_markdown())

        # Custom configuration
        config = Config.strict()
        reviewer = Reviewer(config=config)

        # Custom analyzers
        reviewer = Reviewer(custom_analyzers=[MyCustomAnalyzer()])
    """

    def __init__(
        self,
        config: Optional[Config] = None,
        custom_analyzers: Optional[List[BaseAnalyzer]] = None,
    ):
        """
        Initialize the Reviewer.

        Args:
            config: Configuration options (uses defaults if not provided)
            custom_analyzers: Additional custom analyzers to use
        """
        self.config = config or Config()
        self._analyzers: List[BaseAnalyzer] = []
        self._setup_analyzers(custom_analyzers)

    def _setup_analyzers(
        self,
        custom_analyzers: Optional[List[BaseAnalyzer]] = None
    ) -> None:
        """Set up the analyzers based on configuration."""
        # Built-in analyzers
        analyzer_map = {
            "complexity": ComplexityAnalyzer,
            "security": SecurityAnalyzer,
            "smells": SmellAnalyzer,
        }

        for name, analyzer_class in analyzer_map.items():
            if name in self.config.analyzers:
                self._analyzers.append(analyzer_class(config=self.config))

        # Add custom analyzers
        if custom_analyzers:
            for analyzer in custom_analyzers:
                if isinstance(analyzer, BaseAnalyzer):
                    self._analyzers.append(analyzer)

    @property
    def analyzers(self) -> List[str]:
        """Get list of active analyzer names."""
        return [a.name for a in self._analyzers]

    def review_code(
        self,
        code: str,
        file_path: str = "<string>",
    ) -> FileResult:
        """
        Review a code string.

        Args:
            code: Source code to review
            file_path: Virtual file path for the code

        Returns:
            FileResult with issues and metrics
        """
        issues: List[Issue] = []

        # Parse code once for all analyzers
        tree = self._parse_code(code)

        # Run all analyzers
        for analyzer in self._analyzers:
            try:
                analyzer_issues = analyzer.analyze(code, file_path, tree)
                # Filter by severity
                filtered = self._filter_by_severity(analyzer_issues)
                issues.extend(filtered)
            except Exception as e:
                # Don't let one analyzer failure stop others
                if self.config.verbose:
                    print(f"Warning: {analyzer.name} failed: {e}")

        # Calculate metrics
        metrics = self._calculate_metrics(code, tree)

        return FileResult(
            file=file_path,
            issues=issues,
            metrics=metrics,
        )

    def review_file(self, file_path: Union[str, Path]) -> FileResult:
        """
        Review a single file.

        Args:
            file_path: Path to the file to review

        Returns:
            FileResult with issues and metrics
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not self._should_analyze_file(path):
            return FileResult(
                file=str(path),
                issues=[],
                metrics=Metrics(),
                skipped=True,
            )

        try:
            code = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            code = path.read_text(encoding="latin-1")

        result = self.review_code(code, str(path))
        return result

    def review_directory(
        self,
        directory: Union[str, Path],
        recursive: bool = True,
        parallel: bool = True,
        max_workers: int = 4,
    ) -> ReviewResult:
        """
        Review all files in a directory.

        Args:
            directory: Path to directory
            recursive: Whether to include subdirectories
            parallel: Whether to process files in parallel
            max_workers: Number of parallel workers

        Returns:
            ReviewResult with aggregated results
        """
        dir_path = Path(directory)

        if not dir_path.exists():
            raise NotADirectoryError(f"Directory not found: {directory}")

        if not dir_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory}")

        # Collect files
        files = self._collect_files(dir_path, recursive)

        if not files:
            return ReviewResult(
                files=[],
                total_issues=0,
                issues_by_severity={},
                issues_by_type={},
            )

        # Process files
        file_results: List[FileResult] = []

        if parallel and len(files) > 1:
            file_results = self._process_parallel(files, max_workers)
        else:
            file_results = self._process_sequential(files)

        # Aggregate results
        return self._aggregate_results(file_results)

    def review(
        self,
        path: Union[str, Path],
        **kwargs
    ) -> Union[FileResult, ReviewResult]:
        """
        Smart review - automatically detects if path is file or directory.

        Args:
            path: Path to file or directory
            **kwargs: Additional arguments for review_directory

        Returns:
            FileResult for files, ReviewResult for directories
        """
        p = Path(path)

        if p.is_file():
            return self.review_file(p)
        elif p.is_dir():
            return self.review_directory(p, **kwargs)
        else:
            raise ValueError(f"Invalid path: {path}")

    # Private methods

    def _parse_code(self, code: str) -> Optional[ast.AST]:
        """Parse Python code into AST."""
        try:
            return ast.parse(code)
        except SyntaxError:
            return None

    def _filter_by_severity(self, issues: List[Issue]) -> List[Issue]:
        """Filter issues by minimum severity level."""
        severity_order = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 1,
            Severity.MEDIUM: 2,
            Severity.LOW: 3,
            Severity.INFO: 4,
        }

        min_level = severity_order.get(self.config.min_severity, 4)

        return [
            issue for issue in issues
            if severity_order.get(issue.severity, 4) <= min_level
        ]

    def _should_analyze_file(self, path: Path) -> bool:
        """Check if file should be analyzed."""
        # Check extension
        suffix = path.suffix.lower()
        if suffix not in {".py", ".pyi"}:
            return False

        # Check ignore paths/patterns
        path_str = str(path)
        for pattern in self.config.ignore_paths:
            if pattern in path_str:
                return False

        # Check specific ignore files
        for pattern in self.config.ignore_files:
            if path.match(pattern):
                return False

        return True

    def _collect_files(
        self,
        directory: Path,
        recursive: bool = True
    ) -> List[Path]:
        """Collect all Python files in directory."""
        files: List[Path] = []

        if recursive:
            pattern = "**/*.py"
        else:
            pattern = "*.py"

        for path in directory.glob(pattern):
            if self._should_analyze_file(path):
                files.append(path)

        return sorted(files)

    def _process_sequential(self, files: List[Path]) -> List[FileResult]:
        """Process files sequentially."""
        results = []
        for file_path in files:
            try:
                result = self.review_file(file_path)
                results.append(result)
            except Exception as e:
                if self.config.verbose:
                    print(f"Error processing {file_path}: {e}")
        return results

    def _process_parallel(
        self,
        files: List[Path],
        max_workers: int
    ) -> List[FileResult]:
        """Process files in parallel."""
        results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(self.review_file, f): f
                for f in files
            }

            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    if self.config.verbose:
                        print(f"Error processing {file_path}: {e}")

        return results

    def _calculate_metrics(
        self,
        code: str,
        tree: Optional[ast.AST]
    ) -> Metrics:
        """Calculate code metrics."""
        lines = code.split("\n")
        total_lines = len(lines)
        blank_lines = sum(1 for line in lines if not line.strip())
        comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
        code_lines = total_lines - blank_lines - comment_lines

        # Count functions and classes from AST
        functions = 0
        classes = 0
        complexity_values = []

        if tree:
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions += 1
                    complexity_values.append(
                        self._calculate_function_complexity(node)
                    )
                elif isinstance(node, ast.ClassDef):
                    classes += 1

        avg_complexity = (
            sum(complexity_values) / len(complexity_values)
            if complexity_values else 0
        )
        max_complexity = max(complexity_values) if complexity_values else 0

        return Metrics(
            lines_of_code=code_lines,
            total_lines=total_lines,
            blank_lines=blank_lines,
            comment_lines=comment_lines,
            functions=functions,
            classes=classes,
            avg_complexity=round(avg_complexity, 2),
            max_complexity=max_complexity,
        )

    def _calculate_function_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity for a function."""
        complexity = 1

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.IfExp)):
                complexity += 1
            elif isinstance(child, (ast.For, ast.AsyncFor, ast.While)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.With, ast.AsyncWith)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, ast.comprehension):
                complexity += len(child.ifs)

        return complexity

    def _aggregate_results(
        self,
        file_results: List[FileResult]
    ) -> ReviewResult:
        """Aggregate file results into a ReviewResult."""
        all_issues: List[Issue] = []
        issues_by_severity: Dict[str, int] = {}
        issues_by_type: Dict[str, int] = {}
        issues_by_file: Dict[str, List[Issue]] = {}

        total_lines = 0
        total_code_lines = 0
        total_functions = 0
        total_classes = 0
        complexity_values = []

        for result in file_results:
            if result.skipped:
                continue

            all_issues.extend(result.issues)
            issues_by_file[result.file] = result.issues

            # Aggregate metrics
            if result.metrics:
                total_lines += result.metrics.total_lines
                total_code_lines += result.metrics.lines_of_code
                total_functions += result.metrics.functions
                total_classes += result.metrics.classes
                if result.metrics.avg_complexity > 0:
                    complexity_values.append(result.metrics.avg_complexity)

        # Count by severity
        for issue in all_issues:
            sev = issue.severity.value
            issues_by_severity[sev] = issues_by_severity.get(sev, 0) + 1

        # Count by type
        for issue in all_issues:
            issues_by_type[issue.type] = issues_by_type.get(issue.type, 0) + 1

        # Calculate overall metrics
        avg_complexity = (
            sum(complexity_values) / len(complexity_values)
            if complexity_values else 0
        )

        overall_metrics = Metrics(
            lines_of_code=total_code_lines,
            total_lines=total_lines,
            functions=total_functions,
            classes=total_classes,
            avg_complexity=round(avg_complexity, 2),
        )

        return ReviewResult(
            files=file_results,
            total_issues=len(all_issues),
            issues_by_severity=issues_by_severity,
            issues_by_type=issues_by_type,
            issues_by_file=issues_by_file,
            metrics=overall_metrics,
        )

    def __repr__(self) -> str:
        return f"Reviewer(analyzers={self.analyzers})"


# Convenience functions for quick usage

def review(path: Union[str, Path], **kwargs) -> Union[FileResult, ReviewResult]:
    """
    Quick review function.

    Args:
        path: Path to file or directory
        **kwargs: Configuration options

    Returns:
        Review result
    """
    config = Config(**{k: v for k, v in kwargs.items() if hasattr(Config, k)})
    reviewer = Reviewer(config=config)
    return reviewer.review(path)


def review_code(code: str, **kwargs) -> FileResult:
    """
    Quick review of code string.

    Args:
        code: Source code string
        **kwargs: Configuration options

    Returns:
        FileResult with issues
    """
    config = Config(**{k: v for k, v in kwargs.items() if hasattr(Config, k)})
    reviewer = Reviewer(config=config)
    return reviewer.review_code(code)
