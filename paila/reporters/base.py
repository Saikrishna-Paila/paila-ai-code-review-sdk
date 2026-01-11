"""
Base Reporter
=============

Abstract base class for all reporters.
"""

from abc import ABC, abstractmethod
from typing import Union, Optional, IO
from pathlib import Path

from ..models import FileResult, ReviewResult


class BaseReporter(ABC):
    """
    Base class for all report generators.

    To create a custom reporter:

        class MyReporter(BaseReporter):
            def format(self, result):
                # Format the result
                return "formatted output"
    """

    name: str = "base"
    extension: str = ".txt"

    @abstractmethod
    def format(self, result: Union[FileResult, ReviewResult]) -> str:
        """
        Format the review result as a string.

        Args:
            result: FileResult or ReviewResult to format

        Returns:
            Formatted string output
        """
        pass

    def report(
        self,
        result: Union[FileResult, ReviewResult],
        output: Optional[Union[str, Path, IO]] = None
    ) -> str:
        """
        Generate report and optionally write to file.

        Args:
            result: Review result to report
            output: Output file path or file object (optional)

        Returns:
            Formatted report string
        """
        formatted = self.format(result)

        if output is not None:
            if isinstance(output, (str, Path)):
                with open(output, "w", encoding="utf-8") as f:
                    f.write(formatted)
            else:
                output.write(formatted)

        return formatted

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
