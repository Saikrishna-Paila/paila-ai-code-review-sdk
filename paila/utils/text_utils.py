"""
Text Utilities
==============

Utilities for text manipulation and formatting.
"""

import re
from typing import List, Optional, Tuple


def truncate_text(text: str, max_length: int = 80, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def highlight_line(
    code: str,
    line_number: int,
    context: int = 2,
    marker: str = ">>>"
) -> str:
    """
    Highlight a specific line with context.

    Args:
        code: Source code
        line_number: Line to highlight (1-indexed)
        context: Number of context lines before/after
        marker: Marker for the highlighted line

    Returns:
        Formatted string with highlighted line
    """
    lines = code.split("\n")

    if line_number < 1 or line_number > len(lines):
        return ""

    start = max(0, line_number - context - 1)
    end = min(len(lines), line_number + context)

    result = []
    for i in range(start, end):
        line_num = i + 1
        line = lines[i]

        if line_num == line_number:
            result.append(f"{marker} {line_num:4d} | {line}")
        else:
            result.append(f"    {line_num:4d} | {line}")

    return "\n".join(result)


def indent_code(code: str, spaces: int = 4) -> str:
    """
    Indent all lines of code.

    Args:
        code: Code to indent
        spaces: Number of spaces to indent

    Returns:
        Indented code
    """
    indent = " " * spaces
    lines = code.split("\n")
    return "\n".join(indent + line for line in lines)


def dedent_code(code: str) -> str:
    """
    Remove common leading whitespace.

    Args:
        code: Code to dedent

    Returns:
        Dedented code
    """
    lines = code.split("\n")

    # Find minimum indentation (ignoring empty lines)
    min_indent = float("inf")
    for line in lines:
        if line.strip():
            indent = len(line) - len(line.lstrip())
            min_indent = min(min_indent, indent)

    if min_indent == float("inf"):
        return code

    # Remove common indentation
    return "\n".join(
        line[int(min_indent):] if line.strip() else line
        for line in lines
    )


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text.

    - Converts tabs to spaces
    - Removes trailing whitespace
    - Normalizes line endings

    Args:
        text: Text to normalize

    Returns:
        Normalized text
    """
    # Convert tabs to 4 spaces
    text = text.replace("\t", "    ")

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove trailing whitespace from each line
    lines = [line.rstrip() for line in text.split("\n")]

    # Remove trailing empty lines
    while lines and not lines[-1]:
        lines.pop()

    return "\n".join(lines)


def count_lines(code: str) -> dict:
    """
    Count different types of lines.

    Args:
        code: Source code

    Returns:
        Dictionary with line counts
    """
    lines = code.split("\n")

    total = len(lines)
    blank = 0
    comment = 0
    code_lines = 0

    in_multiline_string = False
    multiline_char = None

    for line in lines:
        stripped = line.strip()

        # Track multiline strings
        if not in_multiline_string:
            if '"""' in stripped or "'''" in stripped:
                char = '"""' if '"""' in stripped else "'''"
                count = stripped.count(char)
                if count == 1:
                    in_multiline_string = True
                    multiline_char = char
        else:
            if multiline_char in stripped:
                in_multiline_string = False
                multiline_char = None

        if not stripped:
            blank += 1
        elif stripped.startswith("#"):
            comment += 1
        else:
            code_lines += 1

    return {
        "total": total,
        "blank": blank,
        "comment": comment,
        "code": code_lines,
    }


def extract_line_range(code: str, start: int, end: int) -> str:
    """
    Extract a range of lines.

    Args:
        code: Source code
        start: Start line (1-indexed)
        end: End line (1-indexed)

    Returns:
        Extracted lines
    """
    lines = code.split("\n")
    start_idx = max(0, start - 1)
    end_idx = min(len(lines), end)
    return "\n".join(lines[start_idx:end_idx])


def find_line_number(code: str, pattern: str) -> Optional[int]:
    """
    Find line number containing pattern.

    Args:
        code: Source code
        pattern: Pattern to search for

    Returns:
        Line number (1-indexed) or None
    """
    for i, line in enumerate(code.split("\n"), 1):
        if pattern in line:
            return i
    return None


def split_into_chunks(
    code: str,
    max_lines: int = 100,
    overlap: int = 10
) -> List[Tuple[int, str]]:
    """
    Split code into overlapping chunks.

    Args:
        code: Source code
        max_lines: Maximum lines per chunk
        overlap: Number of overlapping lines

    Returns:
        List of (start_line, chunk) tuples
    """
    lines = code.split("\n")
    chunks = []

    i = 0
    while i < len(lines):
        end = min(i + max_lines, len(lines))
        chunk = "\n".join(lines[i:end])
        chunks.append((i + 1, chunk))

        i = end - overlap
        if i >= len(lines) - overlap:
            break

    return chunks


def format_code_block(code: str, language: str = "python") -> str:
    """
    Format code as a markdown code block.

    Args:
        code: Source code
        language: Language for syntax highlighting

    Returns:
        Formatted code block
    """
    return f"```{language}\n{code}\n```"


def strip_comments(code: str) -> str:
    """
    Remove comments from Python code.

    Args:
        code: Python source code

    Returns:
        Code without comments
    """
    # Remove single-line comments
    lines = []
    for line in code.split("\n"):
        # Find # not in string
        in_string = False
        string_char = None
        result = []

        i = 0
        while i < len(line):
            char = line[i]

            if not in_string:
                if char in '"\'':
                    # Check for triple quotes
                    if line[i:i+3] in ('"""', "'''"):
                        in_string = True
                        string_char = line[i:i+3]
                        result.append(line[i:i+3])
                        i += 3
                        continue
                    else:
                        in_string = True
                        string_char = char
                elif char == '#':
                    # Comment starts here
                    break

            else:
                # In string
                if char == '\\':
                    result.append(char)
                    if i + 1 < len(line):
                        result.append(line[i+1])
                        i += 2
                        continue
                elif len(string_char) == 3 and line[i:i+3] == string_char:
                    result.append(string_char)
                    in_string = False
                    string_char = None
                    i += 3
                    continue
                elif len(string_char) == 1 and char == string_char:
                    in_string = False
                    string_char = None

            result.append(char)
            i += 1

        lines.append("".join(result).rstrip())

    return "\n".join(lines)
