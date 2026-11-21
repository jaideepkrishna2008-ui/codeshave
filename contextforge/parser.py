"""
AST-based code compression and skeleton extraction.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Optional, Set


@dataclass
class SymbolInfo:
    name: str
    kind: str  # 'class', 'function', 'async_function', 'variable'
    line_number: int
    docstring: Optional[str] = None
    parameters: list[str] = field(default_factory=list)
    return_type: Optional[str] = None


class SkeletonTransformer(ast.NodeTransformer):
    """
    Transforms a Python Abstract Syntax Tree (AST) into a structural skeleton.
    Strips executable implementation bodies while preserving:
      - Function/method signatures, parameter type annotations, and default values
      - Return type annotations
      - Decorators
      - Class hierarchies, base classes, and class-level type annotations
      - Module-level constants, type aliases, and public exports (__all__)
      - Docstrings (optional)
    """

    def __init__(self, preserve_docstrings: bool = True, preserve_private: bool = True):
        self.preserve_docstrings = preserve_docstrings
        self.preserve_private = preserve_private

    def _create_ellipsis_body(self, docstring: Optional[str]) -> list[ast.stmt]:
        body: list[ast.stmt] = []
        if self.preserve_docstrings and docstring:
            body.append(ast.Expr(value=ast.Constant(value=docstring)))
        body.append(ast.Expr(value=ast.Constant(value=Ellipsis)))
        return body

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Optional[ast.FunctionDef]:
        if not self.preserve_private and node.name.startswith("_") and not node.name.startswith("__"):
            return None
        docstring = ast.get_docstring(node)
        node.body = self._create_ellipsis_body(docstring)
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Optional[ast.AsyncFunctionDef]:
        if not self.preserve_private and node.name.startswith("_") and not node.name.startswith("__"):
            return None
        docstring = ast.get_docstring(node)
        node.body = self._create_ellipsis_body(docstring)
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> Optional[ast.ClassDef]:
        if not self.preserve_private and node.name.startswith("_") and not node.name.startswith("__"):
            return None

        docstring = ast.get_docstring(node)
        new_body: list[ast.stmt] = []
        if self.preserve_docstrings and docstring:
            new_body.append(ast.Expr(value=ast.Constant(value=docstring)))

        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                transformed = self.visit(child)
                if transformed:
                    new_body.append(transformed)
            elif isinstance(child, ast.ClassDef):
                transformed = self.visit(child)
                if transformed:
                    new_body.append(transformed)
            elif isinstance(child, (ast.AnnAssign, ast.Assign)):
                # Keep class-level type definitions and constants
                new_body.append(child)

        if not new_body:
            new_body.append(ast.Expr(value=ast.Constant(value=Ellipsis)))

        node.body = new_body
        return node


class ModuleSkeletonFilter(ast.NodeTransformer):
    """
    Cleans top-level statements to retain only definitions, exports, and imports.
    """

    def __init__(self, transformer: SkeletonTransformer):
        self.transformer = transformer

    def visit_Module(self, node: ast.Module) -> ast.Module:
        new_body: list[ast.stmt] = []
        module_doc = ast.get_docstring(node)
        if self.transformer.preserve_docstrings and module_doc:
            new_body.append(ast.Expr(value=ast.Constant(value=module_doc)))

        for stmt in node.body:
            if isinstance(stmt, (ast.Import, ast.ImportFrom)):
                new_body.append(stmt)
            elif isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                transformed = self.transformer.visit(stmt)
                if transformed:
                    new_body.append(transformed)
            elif isinstance(stmt, ast.AnnAssign):
                # Type annotations (e.g. x: int = 1 or my_type: TypeAlias)
                new_body.append(stmt)
            elif isinstance(stmt, ast.Assign):
                # Check for __all__ or UPPERCASE_CONSTANTS
                is_constant_or_export = False
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        if target.id == "__all__" or target.id.isupper():
                            is_constant_or_export = True
                            break
                if is_constant_or_export:
                    new_body.append(stmt)

        node.body = new_body
        return node


def compress_source(
    source_code: str,
    preserve_docstrings: bool = True,
    preserve_private: bool = True,
) -> str:
    """
    Parses raw source code into an AST and returns a syntactically valid,
    cleanly unparsed structural skeleton.
    """
    tree = ast.parse(source_code)
    transformer = SkeletonTransformer(
        preserve_docstrings=preserve_docstrings,
        preserve_private=preserve_private,
    )
    module_filter = ModuleSkeletonFilter(transformer)
    compressed_tree = module_filter.visit(tree)
    ast.fix_missing_locations(compressed_tree)
    return ast.unparse(compressed_tree)


def extract_symbols(source_code: str) -> list[SymbolInfo]:
    """
    Extracts all classes, functions, and top-level definitions with metadata.
    """
    tree = ast.parse(source_code)
    symbols: list[SymbolInfo] = []

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            symbols.append(
                SymbolInfo(
                    name=node.name,
                    kind="class",
                    line_number=node.lineno,
                    docstring=ast.get_docstring(node),
                )
            )
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            kind = "async_function" if isinstance(node, ast.AsyncFunctionDef) else "function"
            params = [arg.arg for arg in node.args.args]
            ret_type = ast.unparse(node.returns) if node.returns else None
            symbols.append(
                SymbolInfo(
                    name=node.name,
                    kind=kind,
                    line_number=node.lineno,
                    docstring=ast.get_docstring(node),
                    parameters=params,
                    return_type=ret_type,
                )
            )

    return symbols
