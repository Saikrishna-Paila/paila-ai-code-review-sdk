"""
Utilities for Paila SDK
=======================

Helper functions and utilities used throughout the SDK.
"""

from .file_utils import (
    read_file,
    find_python_files,
    is_binary_file,
    get_file_encoding,
    calculate_file_hash,
)

from .text_utils import (
    truncate_text,
    highlight_line,
    indent_code,
    normalize_whitespace,
    count_lines,
)

from .hash_utils import (
    hash_code,
    hash_file,
)

__all__ = [
    # File utilities
    "read_file",
    "find_python_files",
    "is_binary_file",
    "get_file_encoding",
    "calculate_file_hash",

    # Text utilities
    "truncate_text",
    "highlight_line",
    "indent_code",
    "normalize_whitespace",
    "count_lines",

    # Hash utilities
    "hash_code",
    "hash_file",
]
