"""
ContextForge
============
High-speed, zero-loss AST code context compressor for AI coding assistants and LLMs.
Reduces prompt tokens by 60-80% while retaining 100% syntactically valid Python code.

Author: Jaideep Krishna A (@jaideepkrishna2008-ui)
License: MIT
"""

from contextforge.parser import compress_source, extract_symbols
from contextforge.estimator import estimate_tokens, compute_savings
from contextforge.graph import DependencyResolver
from contextforge.formatters import format_bundle

__version__ = "0.1.0"
__all__ = [
    "compress_source",
    "extract_symbols",
    "estimate_tokens",
    "compute_savings",
    "DependencyResolver",
    "format_bundle",
]
