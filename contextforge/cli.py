"""
CLI interface for ContextForge.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import List

from contextforge import __version__
from contextforge.estimator import compute_savings, estimate_tokens
from contextforge.formatters import FileContextItem, format_bundle
from contextforge.graph import DependencyResolver
from contextforge.parser import compress_source


DEFAULT_EXCLUDES = {
    ".git",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "dist",
    "node_modules",
    "tests",
}


def find_python_files(target: Path, excludes: set[str]) -> List[Path]:
    """Recursively finds all Python files excluding common build/test folders."""
    if target.is_file():
        return [target]

    found: List[Path] = []
    for p in sorted(target.rglob("*.py")):
        parts = set(p.parts)
        if parts.intersection(excludes):
            continue
        found.append(p)
    return found


def handle_pack(args: argparse.Namespace) -> int:
    target = Path(args.path).resolve()
    if not target.exists():
        sys.stderr.write(f"Error: Target path '{args.path}' does not exist.\n")
        return 1

    start_time = time.perf_counter()
    excludes = DEFAULT_EXCLUDES.copy()
    if args.exclude:
        for ex in args.exclude.split(","):
            excludes.add(ex.strip())

    files = find_python_files(target, excludes)
    if not files:
        sys.stderr.write("No Python files found to process.\n")
        return 1

    # Dependency resolution ordering
    if target.is_dir() and not args.no_sort:
        resolver = DependencyResolver(target)
        files = resolver.sort_files_by_dependency(files)

    items: List[FileContextItem] = []
    total_orig_tokens = 0
    total_comp_tokens = 0

    if args.stats or not args.output:
        sys.stderr.write(f"\n⚡ ContextForge v{__version__} — AST Structural Compressor\n")
        sys.stderr.write(f"Scanning: {target}\n\n")
        header = f"{'FILE':<45} {'ORIGINAL':<12} {'SKELETON':<12} {'SAVINGS':<10}"
        sys.stderr.write(header + "\n")
        sys.stderr.write("─" * len(header) + "\n")

    for f in files:
        rel_path = f.relative_to(target) if target.is_dir() else f.name
        try:
            content = f.read_text(encoding="utf-8")
            compressed = compress_source(
                content,
                preserve_docstrings=not args.no_docs,
                preserve_private=not args.no_private,
            )
            orig_t = estimate_tokens(content)
            comp_t = estimate_tokens(compressed)

            total_orig_tokens += orig_t
            total_comp_tokens += comp_t

            items.append(
                FileContextItem(
                    relative_path=str(rel_path).replace("\\", "/"),
                    original_code=content,
                    compressed_code=compressed,
                    original_tokens=orig_t,
                    compressed_tokens=comp_t,
                )
            )

            pct = ((1.0 - comp_t / orig_t) * 100.0) if orig_t > 0 else 0.0
            if args.stats or not args.output:
                path_str = str(rel_path).replace("\\", "/")
                if len(path_str) > 43:
                    path_str = "..." + path_str[-40:]
                sys.stderr.write(
                    f"{path_str:<45} {orig_t:>8,} t {comp_t:>8,} t {pct:>8.1f}%\n"
                )
        except Exception as exc:
            sys.stderr.write(f"Skipping {rel_path}: {exc}\n")

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    saved = max(0, total_orig_tokens - total_comp_tokens)
    overall_pct = (saved / total_orig_tokens * 100.0) if total_orig_tokens > 0 else 0.0
    dollars_saved = (saved / 1_000_000.0) * 3.00

    if args.stats or not args.output:
        sys.stderr.write("─" * len(header) + "\n")
        sys.stderr.write(
            f"TOTALS ({len(items)} files in {elapsed_ms:.1f}ms):\n"
            f"  • Original:     {total_orig_tokens:,} tokens\n"
            f"  • Compressed:   {total_comp_tokens:,} tokens\n"
            f"  • Reduction:    {saved:,} tokens saved ({overall_pct:.1f}% savings)\n"
            f"  • Est. Value:   ${dollars_saved:.4f} per prompt call\n\n"
        )

    bundled = format_bundle(items, output_format=args.format)

    if args.output:
        out_p = Path(args.output).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(bundled, encoding="utf-8")
        sys.stderr.write(f"✔ Bundle saved successfully to: {out_p}\n")
    else:
        sys.stdout.write(bundled)

    return 0


def handle_inspect(args: argparse.Namespace) -> int:
    target = Path(args.path).resolve()
    if not target.is_file():
        sys.stderr.write(f"Error: Target '{args.path}' must be an existing file.\n")
        return 1

    content = target.read_text(encoding="utf-8")
    compressed = compress_source(content, preserve_docstrings=not args.no_docs)
    report = compute_savings(content, compressed)

    sys.stdout.write(f"# Compressed AST Skeleton for {target.name}\n")
    sys.stdout.write(f"# {report.summary_line()}\n\n")
    sys.stdout.write(compressed + "\n")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="contextforge",
        description="⚡ ContextForge: Zero-loss AST code context compressor for AI coding assistants.",
    )
    parser.add_argument("-v", "--version", action="version", version=f"contextforge {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Pack command
    pack_p = subparsers.add_parser("pack", help="Compress codebase directory into an LLM context bundle")
    pack_p.add_argument("path", help="Source file or directory to compress")
    pack_p.add_argument("-o", "--output", help="Output file path (default: stdout)")
    pack_p.add_argument(
        "-f",
        "--format",
        choices=["md", "xml", "json"],
        default="md",
        help="Context bundle format (default: md)",
    )
    pack_p.add_argument("--no-docs", action="store_true", help="Omit docstrings for maximum token savings")
    pack_p.add_argument("--no-private", action="store_true", help="Omit private functions (_func)")
    pack_p.add_argument("--no-sort", action="store_true", help="Disable dependency topological ordering")
    pack_p.add_argument("--exclude", help="Comma-separated directories to exclude")
    pack_p.add_argument("--stats", action="store_true", help="Force display of summary metrics")

    # Inspect command
    inspect_p = subparsers.add_parser("inspect", help="Inspect compressed skeleton of a single file")
    inspect_p.add_argument("path", help="Target Python file")
    inspect_p.add_argument("--no-docs", action="store_true", help="Omit docstrings")

    args = parser.parse_args()

    if args.command == "pack":
        sys.exit(handle_pack(args))
    elif args.command == "inspect":
        sys.exit(handle_inspect(args))


if __name__ == "__main__":
    main()
