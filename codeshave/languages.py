"""
Multi-language code detection and universal AST/structural skeletonization.
Supports Python, TypeScript, JavaScript, Go, Rust, Java, C, C++, C#,
Swift, Kotlin, Dart, PHP, Ruby, Scala, Zig, Shell, and more.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional, Set

from codeshave.parser import compress_source as compress_python_source

# Mapping of file extensions to canonical language identifiers
EXTENSION_MAP: dict[str, str] = {
    # Python
    ".py": "python",
    ".pyw": "python",
    # TypeScript & JavaScript
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    # Systems & Compiled
    ".go": "go",
    ".rs": "rust",
    ".c": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".h": "c",
    ".hpp": "cpp",
    # JVM & .NET
    ".java": "java",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".scala": "scala",
    ".cs": "csharp",
    # Mobile & Web
    ".swift": "swift",
    ".dart": "dart",
    ".php": "php",
    ".zig": "zig",
    # Scripting & Others
    ".rb": "ruby",
    ".sh": "bash",
    ".bash": "bash",
    ".zsh": "bash",
    ".sql": "sql",
}

SUPPORTED_EXTENSIONS: set[str] = set(EXTENSION_MAP.keys())

# Languages that use curly braces { ... } for block structures
CURLY_LANGUAGES: set[str] = {
    "typescript",
    "javascript",
    "go",
    "rust",
    "c",
    "cpp",
    "java",
    "kotlin",
    "scala",
    "csharp",
    "swift",
    "dart",
    "php",
    "zig",
}


def detect_language(path_or_ext: str, source_code: Optional[str] = None) -> str:
    """
    Detects programming language from file extension or source syntax heuristics.
    """
    p = Path(path_or_ext)
    ext = p.suffix.lower()
    if ext in EXTENSION_MAP:
        return EXTENSION_MAP[ext]

    if not source_code:
        return "generic"

    # Heuristic detection from content
    sample = source_code[:1000]
    if re.search(r'^\s*(def |async def |class \w+:|import \w+|from \w+ import)', sample, re.MULTILINE):
        return "python"
    if re.search(r'package\s+\w+|func\s+\(', sample):
        return "go"
    if re.search(r'fn\s+\w+|impl\s+|use\s+std::', sample):
        return "rust"
    if re.search(r'import\s+type\s+|interface\s+\w+|export\s+const\s+|export\s+function', sample):
        return "typescript"
    if re.search(r'public\s+class\s+|public\s+static\s+void\s+main', sample):
        return "java"
    if re.search(r'#include\s+<', sample):
        return "cpp"
    if re.search(r'def\s+\w+.*end|require\s+[\'"]', sample):
        return "ruby"

    return "generic"


def _is_function_header(stmt: str) -> bool:
    """
    Checks if statement leading up to '{' represents a function, method,
    constructor, or execution block whose internal body should be shaved.
    """
    clean = stmt.strip()
    if not clean:
        return False

    # Container structures that MUST keep their definitions / braces
    if re.search(r'\b(class|interface|struct|enum|namespace|trait|impl)\b', clean):
        return False
    if re.match(r'^(import|export)\s*\{', clean):
        return False
    if re.search(r'\btype\s+\w+\s*=\s*$', clean) or re.search(r'\btype\s+\w+\s*=\s*\{', clean):
        return False

    # Function / method indicators
    if ')' in clean or '=>' in clean:
        return True
    if re.search(r'\b(fn|func|function|constructor|get|set)\b', clean):
        return True
    if re.search(r'\b(if|for|while|switch|catch)\s*\(', clean):
        return True

    return False


def skeletonize_curly(source: str) -> str:
    """
    Fast, deterministic curly-brace skeletonizer for C-style languages.
    Preserves all interfaces, type aliases, classes, annotations, imports/exports,
    and function signatures while replacing executable bodies with { /* ... */ }.
    """
    n = len(source)
    i = 0
    result: list[str] = []
    statement_buf: list[str] = []

    in_single_line_comment = False
    in_multi_line_comment = False
    in_string: Optional[str] = None

    while i < n:
        char = source[i]

        # Handle comments
        if not in_string:
            if not in_multi_line_comment and not in_single_line_comment:
                if char == '/' and i + 1 < n and source[i + 1] == '/':
                    in_single_line_comment = True
                    result.append('//')
                    i += 2
                    continue
                elif char == '/' and i + 1 < n and source[i + 1] == '*':
                    in_multi_line_comment = True
                    result.append('/*')
                    i += 2
                    continue
            elif in_single_line_comment:
                result.append(char)
                if char == '\n':
                    in_single_line_comment = False
                    statement_buf = []
                i += 1
                continue
            elif in_multi_line_comment:
                result.append(char)
                if char == '*' and i + 1 < n and source[i + 1] == '/':
                    result.append('/')
                    in_multi_line_comment = False
                    i += 2
                    continue
                i += 1
                continue

        # Handle string literals
        if not in_single_line_comment and not in_multi_line_comment:
            if in_string:
                result.append(char)
                if char == '\\':
                    if i + 1 < n:
                        result.append(source[i + 1])
                        i += 2
                        continue
                elif char == in_string:
                    in_string = None
                i += 1
                continue
            else:
                if char in ('"', "'", '`'):
                    in_string = char
                    result.append(char)
                    i += 1
                    continue

        # Normal code processing
        if char == '{':
            stmt_text = "".join(statement_buf).strip()

            if _is_function_header(stmt_text):
                # Function/method body: Skip from '{' to matching '}'
                depth = 1
                j = i + 1
                inner_str: Optional[str] = None
                inner_s_comm = False
                inner_m_comm = False

                while j < n and depth > 0:
                    c = source[j]
                    if not inner_str:
                        if not inner_m_comm and not inner_s_comm:
                            if c == '/' and j + 1 < n and source[j + 1] == '/':
                                inner_s_comm = True
                                j += 2
                                continue
                            elif c == '/' and j + 1 < n and source[j + 1] == '*':
                                inner_m_comm = True
                                j += 2
                                continue
                            elif c in ('"', "'", '`'):
                                inner_str = c
                                j += 1
                                continue
                            elif c == '{':
                                depth += 1
                            elif c == '}':
                                depth -= 1
                        elif inner_s_comm:
                            if c == '\n':
                                inner_s_comm = False
                        elif inner_m_comm:
                            if c == '*' and j + 1 < n and source[j + 1] == '/':
                                inner_m_comm = False
                                j += 2
                                continue
                    else:
                        if c == '\\':
                            j += 2
                            continue
                        elif c == inner_str:
                            inner_str = None
                    j += 1

                result.append('{ /* ... */ }')
                statement_buf = []
                i = j
                continue
            else:
                # Container block (class, interface, struct, enum, namespace)
                result.append('{')
                statement_buf = []
                i += 1
                continue
        elif char == '}':
            result.append('}')
            statement_buf = []
            i += 1
            continue
        elif char in (';', '\n'):
            statement_buf.append(char)
            result.append(char)
            if char == ';':
                statement_buf = []
            elif char == '\n' and len("".join(statement_buf).strip()) == 0:
                statement_buf = []
            i += 1
            continue
        else:
            statement_buf.append(char)
            result.append(char)
            i += 1

    return "".join(result)


def skeletonize_ruby(source: str) -> str:
    """
    Skeletonizer for Ruby files (def ... end).
    """
    lines = source.splitlines()
    result: list[str] = []
    in_def = False
    def_indent = 0

    for line in lines:
        stripped = line.strip()
        if not in_def:
            if stripped.startswith("def ") or stripped.startswith("def\t"):
                in_def = True
                def_indent = len(line) - len(line.lstrip())
                result.append(line)
                result.append(" " * (def_indent + 2) + "# ...")
                continue
            result.append(line)
        else:
            # Check for matching end
            cur_indent = len(line) - len(line.lstrip())
            if stripped == "end" and cur_indent == def_indent:
                in_def = False
                result.append(line)

    return "\n".join(result)


def compress_code(
    source_code: str,
    filename_or_ext: str = "python",
    preserve_docstrings: bool = True,
    preserve_private: bool = True,
) -> str:
    """
    Universal code compression entry point. Dispatches to Python AST engine
    or universal curly-brace / language-specific skeletonizer.
    """
    lang = detect_language(filename_or_ext, source_code)

    if lang == "python":
        try:
            return compress_python_source(
                source_code,
                preserve_docstrings=preserve_docstrings,
                preserve_private=preserve_private,
            )
        except Exception:
            # Fallback if Python source has a syntax error
            return source_code

    if lang in CURLY_LANGUAGES:
        return skeletonize_curly(source_code)

    if lang == "ruby":
        return skeletonize_ruby(source_code)

    # For generic markup/data/unsupported files, return unchanged or stripped
    return source_code
