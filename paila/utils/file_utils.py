"""
File Utilities
==============

Utilities for file operations.
"""

import os
import hashlib
from pathlib import Path
from typing import List, Optional, Iterator


def read_file(file_path: str, encoding: Optional[str] = None) -> str:
    """
    Read a file with automatic encoding detection.

    Args:
        file_path: Path to the file
        encoding: Encoding to use (auto-detect if None)

    Returns:
        File contents as string
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if encoding is None:
        encoding = get_file_encoding(file_path)

    try:
        return path.read_text(encoding=encoding)
    except UnicodeDecodeError:
        # Fallback to latin-1 which can read any byte sequence
        return path.read_text(encoding="latin-1")


def find_python_files(
    directory: str,
    recursive: bool = True,
    ignore_patterns: Optional[List[str]] = None
) -> Iterator[Path]:
    """
    Find all Python files in a directory.

    Args:
        directory: Directory to search
        recursive: Whether to search subdirectories
        ignore_patterns: Patterns to ignore

    Yields:
        Path objects for each Python file
    """
    if ignore_patterns is None:
        ignore_patterns = [
            "__pycache__",
            ".git",
            "node_modules",
            ".venv",
            "venv",
            ".tox",
            "dist",
            "build",
            "*.egg-info",
        ]

    dir_path = Path(directory)

    if not dir_path.exists():
        return

    pattern = "**/*.py" if recursive else "*.py"

    for path in dir_path.glob(pattern):
        # Check ignore patterns
        path_str = str(path)
        should_ignore = any(pattern in path_str for pattern in ignore_patterns)

        if not should_ignore:
            yield path


def is_binary_file(file_path: str) -> bool:
    """
    Check if a file is binary (not text).

    Args:
        file_path: Path to the file

    Returns:
        True if binary, False if text
    """
    path = Path(file_path)

    if not path.exists():
        return False

    # Check by reading first 8KB
    try:
        with open(path, "rb") as f:
            chunk = f.read(8192)

        # Check for null bytes (common in binary files)
        if b"\x00" in chunk:
            return True

        # Try to decode as text
        try:
            chunk.decode("utf-8")
            return False
        except UnicodeDecodeError:
            return True

    except Exception:
        return True


def get_file_encoding(file_path: str) -> str:
    """
    Detect file encoding.

    Args:
        file_path: Path to the file

    Returns:
        Detected encoding (defaults to utf-8)
    """
    path = Path(file_path)

    if not path.exists():
        return "utf-8"

    # Check for BOM markers
    try:
        with open(path, "rb") as f:
            bom = f.read(4)

        if bom.startswith(b"\xef\xbb\xbf"):
            return "utf-8-sig"
        elif bom.startswith(b"\xff\xfe\x00\x00"):
            return "utf-32-le"
        elif bom.startswith(b"\x00\x00\xfe\xff"):
            return "utf-32-be"
        elif bom.startswith(b"\xff\xfe"):
            return "utf-16-le"
        elif bom.startswith(b"\xfe\xff"):
            return "utf-16-be"

    except Exception:
        pass

    # Check for encoding declaration in Python files
    if file_path.endswith(".py"):
        try:
            with open(path, "rb") as f:
                first_lines = f.read(512).decode("ascii", errors="ignore")

            for line in first_lines.split("\n")[:2]:
                if "coding" in line:
                    # Parse: # -*- coding: utf-8 -*-
                    import re
                    match = re.search(r"coding[=:]\s*([-\w.]+)", line)
                    if match:
                        return match.group(1)
        except Exception:
            pass

    return "utf-8"


def calculate_file_hash(file_path: str, algorithm: str = "sha256") -> str:
    """
    Calculate hash of a file.

    Args:
        file_path: Path to the file
        algorithm: Hash algorithm (md5, sha1, sha256)

    Returns:
        Hex digest of the hash
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    hash_func = hashlib.new(algorithm)

    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_func.update(chunk)

    return hash_func.hexdigest()


def get_relative_path(file_path: str, base_path: str) -> str:
    """
    Get relative path from base.

    Args:
        file_path: Full file path
        base_path: Base directory path

    Returns:
        Relative path
    """
    try:
        return str(Path(file_path).relative_to(base_path))
    except ValueError:
        return file_path


def ensure_directory(path: str) -> Path:
    """
    Ensure directory exists, create if needed.

    Args:
        path: Directory path

    Returns:
        Path object
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_file_size(file_path: str) -> int:
    """
    Get file size in bytes.

    Args:
        file_path: Path to file

    Returns:
        Size in bytes
    """
    return Path(file_path).stat().st_size


def get_file_info(file_path: str) -> dict:
    """
    Get comprehensive file information.

    Args:
        file_path: Path to file

    Returns:
        Dictionary with file info
    """
    path = Path(file_path)

    if not path.exists():
        return {"exists": False}

    stat = path.stat()

    return {
        "exists": True,
        "name": path.name,
        "extension": path.suffix,
        "size": stat.st_size,
        "modified": stat.st_mtime,
        "is_file": path.is_file(),
        "is_dir": path.is_dir(),
        "is_binary": is_binary_file(file_path) if path.is_file() else None,
        "encoding": get_file_encoding(file_path) if path.is_file() and not is_binary_file(file_path) else None,
    }
