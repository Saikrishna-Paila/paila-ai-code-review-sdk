"""
Base Parser
===========

Abstract base class for language parsers.
"""

from abc import ABC, abstractmethod
from typing import Optional, Any, List, Dict
from dataclasses import dataclass


@dataclass
class ParsedCode:
    """
    Represents parsed code.

    Attributes:
        tree: The parsed AST/tree
        language: Programming language
        errors: List of parse errors
        tokens: List of tokens (if available)
        comments: Extracted comments
    """
    tree: Any
    language: str
    errors: List[str] = None
    tokens: List[Any] = None
    comments: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.comments is None:
            self.comments = []

    @property
    def is_valid(self) -> bool:
        """Check if parsing was successful."""
        return self.tree is not None and len(self.errors) == 0


class BaseParser(ABC):
    """
    Abstract base class for code parsers.

    To create a parser for a new language:

        class JavaScriptParser(BaseParser):
            language = "javascript"
            extensions = [".js", ".jsx", ".mjs"]

            def parse(self, code):
                # Parse JavaScript code
                return ParsedCode(tree=parsed_tree, language="javascript")
    """

    language: str = "unknown"
    extensions: List[str] = []

    @abstractmethod
    def parse(self, code: str) -> ParsedCode:
        """
        Parse source code.

        Args:
            code: Source code string

        Returns:
            ParsedCode object with AST and metadata
        """
        pass

    def can_parse(self, file_path: str) -> bool:
        """
        Check if this parser can handle the given file.

        Args:
            file_path: Path to the file

        Returns:
            True if this parser supports the file type
        """
        return any(file_path.endswith(ext) for ext in self.extensions)

    def extract_comments(self, code: str) -> List[Dict[str, Any]]:
        """
        Extract comments from source code.

        Args:
            code: Source code string

        Returns:
            List of comment dictionaries with 'line', 'text', 'type' keys
        """
        return []

    def extract_strings(self, code: str) -> List[Dict[str, Any]]:
        """
        Extract string literals from source code.

        Args:
            code: Source code string

        Returns:
            List of string dictionaries with 'line', 'value' keys
        """
        return []

    def get_line(self, code: str, line_number: int) -> str:
        """
        Get a specific line from the code.

        Args:
            code: Source code string
            line_number: Line number (1-indexed)

        Returns:
            The line of code
        """
        lines = code.split("\n")
        if 1 <= line_number <= len(lines):
            return lines[line_number - 1]
        return ""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(language='{self.language}')"
