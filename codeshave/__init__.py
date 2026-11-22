"""
CodeShave
============
High-speed, zero-loss AST code context compressor for AI coding assistants and LLMs.
Reduces prompt tokens by 60-80% while retaining 100% syntactically valid Python code.

Author: Jaideep Krishna A (@jaideepkrishna2008-ui)
License: MIT
"""

from codeshave.parser import compress_source, extract_symbols
from codeshave.languages import compress_code, detect_language, SUPPORTED_EXTENSIONS
from codeshave.estimator import estimate_tokens, compute_savings
from codeshave.graph import DependencyResolver
from codeshave.formatters import format_bundle

__version__ = "0.2.2"
__all__ = [
    "compress_code",
    "compress_source",
    "detect_language",
    "extract_symbols",
    "estimate_tokens",
    "compute_savings",
    "DependencyResolver",
    "format_bundle",
    "SUPPORTED_EXTENSIONS",
]
