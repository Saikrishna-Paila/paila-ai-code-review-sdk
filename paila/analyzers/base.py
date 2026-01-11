"""
Base Analyzer
=============

Abstract base class for all analyzers.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, TYPE_CHECKING
import ast

if TYPE_CHECKING:
    from ..models import Issue, Metrics
    from ..config import Config


class BaseAnalyzer(ABC):
    """
    Base class for all code analyzers.

    To create a custom analyzer:

        class MyAnalyzer(BaseAnalyzer):
            name = "my_analyzer"
            description = "Checks for my custom issues"

            def analyze(self, code, file_path, tree):
                issues = []
                # Your analysis logic here
                return issues

    Then use it:
        reviewer = Reviewer(custom_analyzers=[MyAnalyzer()])
    """

    name: str = "base"
    description: str = "Base analyzer"

    def __init__(self, config: Optional["Config"] = None):
        """
        Initialize the analyzer.

        Args:
            config: Configuration options
        """
        from ..config import Config
        self.config = config or Config()

    @abstractmethod
    def analyze(
        self,
        code: str,
        file_path: str,
        tree: Optional[ast.AST] = None
    ) -> List["Issue"]:
        """
        Analyze code and return issues found.

        Args:
            code: Source code as string
            file_path: Path to the file being analyzed
            tree: Pre-parsed AST (optional, will parse if not provided)

        Returns:
            List of Issue objects found
        """
        pass

    def parse_code(self, code: str) -> Optional[ast.AST]:
        """
        Parse code into AST.

        Args:
            code: Source code string

        Returns:
            AST tree or None if parsing fails
        """
        try:
            return ast.parse(code)
        except SyntaxError:
            return None

    def get_code_line(self, code: str, line_number: int) -> str:
        """
        Get a specific line of code.

        Args:
            code: Full source code
            line_number: Line number (1-indexed)

        Returns:
            The line of code (stripped)
        """
        lines = code.split("\n")
        if 1 <= line_number <= len(lines):
            return lines[line_number - 1].strip()
        return ""

    def get_code_snippet(
        self,
        code: str,
        start_line: int,
        end_line: Optional[int] = None,
        max_lines: int = 5
    ) -> str:
        """
        Get a code snippet.

        Args:
            code: Full source code
            start_line: Starting line number (1-indexed)
            end_line: Ending line number (optional)
            max_lines: Maximum lines to include

        Returns:
            Code snippet as string
        """
        lines = code.split("\n")
        if end_line is None:
            end_line = min(start_line + max_lines - 1, len(lines))

        start_idx = max(0, start_line - 1)
        end_idx = min(len(lines), end_line)

        return "\n".join(lines[start_idx:end_idx])

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
