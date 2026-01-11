"""
Hash Utilities
==============

Utilities for hashing code and detecting duplicates.
"""

import hashlib
import re
from typing import List, Dict, Set, Optional, Tuple


def hash_code(code: str, normalize: bool = True) -> str:
    """
    Generate hash of code content.

    Args:
        code: Source code
        normalize: Whether to normalize whitespace before hashing

    Returns:
        SHA256 hash hex digest
    """
    if normalize:
        code = _normalize_for_hash(code)

    return hashlib.sha256(code.encode()).hexdigest()


def hash_file(file_path: str, normalize: bool = True) -> str:
    """
    Generate hash of a file's code content.

    Args:
        file_path: Path to file
        normalize: Whether to normalize whitespace

    Returns:
        SHA256 hash hex digest
    """
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    return hash_code(code, normalize)


def _normalize_for_hash(code: str) -> str:
    """
    Normalize code for consistent hashing.

    - Remove comments
    - Normalize whitespace
    - Remove blank lines
    """
    lines = []

    for line in code.split("\n"):
        # Remove trailing whitespace
        line = line.rstrip()

        # Remove inline comments (simple approach)
        if "#" in line:
            # Be careful not to remove # inside strings
            # This is a simplified version
            if not _in_string(line, line.index("#")):
                line = line[:line.index("#")].rstrip()

        # Skip blank lines and comment-only lines
        if line.strip():
            lines.append(line)

    return "\n".join(lines)


def _in_string(line: str, pos: int) -> bool:
    """Check if position is inside a string."""
    in_single = False
    in_double = False

    for i, char in enumerate(line):
        if i >= pos:
            break

        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double

    return in_single or in_double


def hash_function(code: str, func_name: str) -> Optional[str]:
    """
    Hash a specific function from code.

    Args:
        code: Source code
        func_name: Function name to hash

    Returns:
        Hash of the function or None if not found
    """
    import ast

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == func_name:
                # Extract function source
                lines = code.split("\n")
                func_lines = lines[node.lineno - 1:node.end_lineno]
                func_code = "\n".join(func_lines)
                return hash_code(func_code)

    return None


def find_duplicate_code(
    files: Dict[str, str],
    min_lines: int = 5
) -> List[Dict]:
    """
    Find duplicate code blocks across files.

    Args:
        files: Dictionary mapping file paths to code
        min_lines: Minimum lines for a duplicate

    Returns:
        List of duplicate info dictionaries
    """
    # Extract code blocks from each file
    blocks: Dict[str, List[Tuple[str, int, str]]] = {}  # hash -> [(file, line, code)]

    for file_path, code in files.items():
        lines = code.split("\n")

        for i in range(len(lines) - min_lines + 1):
            block = "\n".join(lines[i:i + min_lines])
            block_hash = hash_code(block)

            if block_hash not in blocks:
                blocks[block_hash] = []

            blocks[block_hash].append((file_path, i + 1, block))

    # Find duplicates (hashes with multiple occurrences)
    duplicates = []

    for block_hash, occurrences in blocks.items():
        if len(occurrences) > 1:
            # Filter out trivial matches (empty lines, etc.)
            code = occurrences[0][2]
            if code.strip() and len(code.strip().split("\n")) >= min_lines:
                duplicates.append({
                    "hash": block_hash,
                    "occurrences": [
                        {"file": f, "line": l}
                        for f, l, _ in occurrences
                    ],
                    "code": code,
                    "lines": min_lines,
                })

    return duplicates


def calculate_similarity(code1: str, code2: str) -> float:
    """
    Calculate similarity ratio between two code snippets.

    Uses simple token-based comparison.

    Args:
        code1: First code snippet
        code2: Second code snippet

    Returns:
        Similarity ratio (0.0 to 1.0)
    """
    # Tokenize
    tokens1 = set(_tokenize(code1))
    tokens2 = set(_tokenize(code2))

    if not tokens1 or not tokens2:
        return 0.0

    # Jaccard similarity
    intersection = len(tokens1 & tokens2)
    union = len(tokens1 | tokens2)

    return intersection / union if union > 0 else 0.0


def _tokenize(code: str) -> List[str]:
    """Simple tokenization for similarity comparison."""
    # Split on non-alphanumeric characters
    tokens = re.findall(r'\b\w+\b', code.lower())
    return tokens


def fingerprint_code(code: str, chunk_size: int = 50) -> List[str]:
    """
    Generate fingerprints for code chunks.

    Useful for detecting similar code even when not exact duplicates.

    Args:
        code: Source code
        chunk_size: Size of each chunk in characters

    Returns:
        List of fingerprint hashes
    """
    # Normalize
    normalized = _normalize_for_hash(code)

    # Remove all whitespace for fingerprinting
    compact = "".join(normalized.split())

    fingerprints = []
    for i in range(0, len(compact) - chunk_size + 1, chunk_size // 2):
        chunk = compact[i:i + chunk_size]
        fp = hashlib.md5(chunk.encode()).hexdigest()[:8]
        fingerprints.append(fp)

    return fingerprints
