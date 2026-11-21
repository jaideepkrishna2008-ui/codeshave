"""
Dependency graph and topological file ordering.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Dict, List, Set


class DependencyResolver:
    """
    Parses import dependencies across a collection of files and sorts them
    so base interfaces and models precede dependent consumers.
    """

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir.resolve()

    def extract_local_imports(self, filepath: Path) -> Set[str]:
        """Extracts locally resolved module import names from a Python file."""
        imports: Set[str] = set()
        try:
            tree = ast.parse(filepath.read_text(encoding="utf-8"))
        except Exception:
            return imports

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])

        return imports

    def sort_files_by_dependency(self, filepaths: List[Path]) -> List[Path]:
        """
        Orders files topologically. Foundational files (like models, schemas, utils)
        are placed first, providing better priming context for LLM understanding.
        """
        graph: Dict[Path, Set[Path]] = {f: set() for f in filepaths}
        module_to_path: Dict[str, Path] = {
            f.stem: f for f in filepaths
        }

        for path in filepaths:
            imported_names = self.extract_local_imports(path)
            for name in imported_names:
                if name in module_to_path and module_to_path[name] != path:
                    graph[path].add(module_to_path[name])

        # Topological sort (Kahn's algorithm / DFS)
        visited: Set[Path] = set()
        visiting: Set[Path] = set()
        ordered: List[Path] = []

        def dfs(node: Path):
            if node in visiting:
                return  # Cycle detected; break gracefully
            if node not in visited:
                visiting.add(node)
                for dep in graph.get(node, []):
                    dfs(dep)
                visiting.remove(node)
                visited.add(node)
                ordered.append(node)

        for p in filepaths:
            if p not in visited:
                dfs(p)

        return ordered
