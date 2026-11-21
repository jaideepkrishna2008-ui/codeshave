"""
CLI interface for CodeShave.
"""

from __future__ import annotations

import argparse
import difflib
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional

from codeshave import __version__
from codeshave.clipboard import copy_to_clipboard
from codeshave.estimator import compute_savings, estimate_tokens
from codeshave.formatters import FileContextItem, format_bundle
from codeshave.graph import DependencyResolver
from codeshave.mcp import run_mcp_server
from codeshave.parser import compress_source


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


def find_git_modified_files(repo_path: Path, staged: bool = False) -> List[Path]:
    """Retrieves list of modified Python files in git working tree or index."""
    cmd = ["git", "diff", "--name-only"]
    if staged:
        cmd.append("--cached")
    try:
        proc = subprocess.run(
            cmd, cwd=repo_path, capture_output=True, text=True, check=True
        )
        files = []
        for line in proc.stdout.splitlines():
            line = line.strip()
            if line.endswith(".py"):
                p = (repo_path / line).resolve()
                if p.is_file():
                    files.append(p)
        return files
    except Exception:
        return []


def handle_pack(args: argparse.Namespace) -> int:
    target = Path(args.path or ".").resolve()
    if not target.exists():
        sys.stderr.write(f"Error: Target path '{args.path}' does not exist.\n")
        return 1

    start_time = time.perf_counter()
    excludes = DEFAULT_EXCLUDES.copy()
    if args.exclude:
        for ex in args.exclude.split(","):
            excludes.add(ex.strip())

    if args.git or args.staged:
        files = find_git_modified_files(target, staged=args.staged)
        if not files:
            sys.stderr.write("No modified Python files detected in git working tree.\n")
            return 0
    else:
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

    preserve_docs = not args.no_docs
    preserve_priv = not args.no_private

    if args.stats or not args.output:
        sys.stderr.write(f"\n⚡ CodeShave v{__version__} — AST Structural Compressor\n")
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
                preserve_docstrings=preserve_docs,
                preserve_private=preserve_priv,
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

    # Budget constraint handling
    if args.budget and total_comp_tokens > args.budget and preserve_docs:
        sys.stderr.write(
            f"\n⚠ Exceeded token budget ({total_comp_tokens:,} > {args.budget:,}). "
            "Auto-stripping docstrings to fit...\n"
        )
        total_comp_tokens = 0
        for item in items:
            item.compressed_code = compress_source(
                item.original_code,
                preserve_docstrings=False,
                preserve_private=preserve_priv,
            )
            item.compressed_tokens = estimate_tokens(item.compressed_code)
            total_comp_tokens += item.compressed_tokens

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


def handle_clip(args: argparse.Namespace) -> int:
    """Compresses file or directory and copies directly to OS clipboard."""
    target = Path(args.path or ".").resolve()
    if not target.exists():
        sys.stderr.write(f"Error: Target path '{args.path}' does not exist.\n")
        return 1

    if args.git or args.staged:
        files = find_git_modified_files(target, staged=args.staged)
    elif target.is_file():
        files = [target]
    else:
        files = find_python_files(target, DEFAULT_EXCLUDES)

    if not files:
        sys.stderr.write("No Python files found to clip.\n")
        return 1

    if len(files) == 1 and target.is_file():
        content = target.read_text(encoding="utf-8")
        compressed = compress_source(content, preserve_docstrings=not args.no_docs)
        report = compute_savings(content, compressed)
        formatted = f"# File: {target.name}\n```python\n{compressed}\n```\n"
        copy_to_clipboard(formatted)
        sys.stderr.write(
            f"✔ Copied to clipboard! {report.summary_line()} "
            f"(-{report.reduction_percentage:.1f}%)\n"
            f"Ready to paste into ChatGPT, Claude, or Cursor.\n"
        )
        return 0
    else:
        items = []
        total_orig = 0
        total_comp = 0
        for f in files:
            rel = f.relative_to(target) if target.is_dir() else f.name
            code = f.read_text(encoding="utf-8")
            comp = compress_source(code, preserve_docstrings=not args.no_docs)
            ot = estimate_tokens(code)
            ct = estimate_tokens(comp)
            total_orig += ot
            total_comp += ct
            items.append(FileContextItem(str(rel), code, comp, ot, ct))

        bundle = format_bundle(items, output_format="md")
        saved = max(0, total_orig - total_comp)
        pct = (saved / total_orig * 100.0) if total_orig > 0 else 0.0
        copy_to_clipboard(bundle)
        sys.stderr.write(
            f"✔ Copied {len(items)} files to clipboard! "
            f"({total_orig:,} t -> {total_comp:,} t, -{pct:.1f}% saved)\n"
            f"Ready to paste directly into LLM prompt.\n"
        )
        return 0


def handle_diff(args: argparse.Namespace) -> int:
    """Displays a colored terminal diff showing lines shaved from the file."""
    target = Path(args.path).resolve()
    if not target.is_file():
        sys.stderr.write(f"Error: Target '{args.path}' must be an existing file.\n")
        return 1

    content = target.read_text(encoding="utf-8")
    compressed = compress_source(content, preserve_docstrings=not args.no_docs)
    report = compute_savings(content, compressed)

    orig_lines = content.splitlines(keepends=True)
    comp_lines = compressed.splitlines(keepends=True)

    diff = list(
        difflib.unified_diff(
            orig_lines,
            comp_lines,
            fromfile=f"a/{target.name} (original)",
            tofile=f"b/{target.name} (shaved)",
        )
    )

    sys.stdout.write(f"\n⚡ CodeShave Diff for {target.name}\n")
    sys.stdout.write(f"{report.summary_line()}\n\n")

    for line in diff:
        if line.startswith("+") and not line.startswith("+++"):
            # Green
            sys.stdout.write(f"\033[32m{line}\033[0m")
        elif line.startswith("-") and not line.startswith("---"):
            # Red / Shaved
            sys.stdout.write(f"\033[31m{line}\033[0m")
        elif line.startswith("@@"):
            # Cyan
            sys.stdout.write(f"\033[36m{line}\033[0m")
        else:
            sys.stdout.write(line)

    sys.stdout.write("\n")
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
        prog="codeshave",
        description="⚡ CodeShave: Zero-loss AST code context compressor for AI coding assistants.",
    )
    parser.add_argument("-v", "--version", action="version", version=f"codeshave {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Pack command
    pack_p = subparsers.add_parser("pack", help="Compress codebase directory into an LLM context bundle")
    pack_p.add_argument("path", nargs="?", default=".", help="Source file or directory (default: current directory)")
    pack_p.add_argument("-o", "--output", help="Output file path (default: stdout)")
    pack_p.add_argument(
        "-f",
        "--format",
        choices=["md", "xml", "json"],
        default="md",
        help="Context bundle format (default: md)",
    )
    pack_p.add_argument("--budget", type=int, help="Target max token ceiling (auto-compresses to fit)")
    pack_p.add_argument("--git", action="store_true", help="Compress only git-modified files")
    pack_p.add_argument("--staged", action="store_true", help="Compress only git staged changes")
    pack_p.add_argument("--no-docs", action="store_true", help="Omit docstrings for maximum token savings")
    pack_p.add_argument("--no-private", action="store_true", help="Omit private functions (_func)")
    pack_p.add_argument("--no-sort", action="store_true", help="Disable dependency topological ordering")
    pack_p.add_argument("--exclude", help="Comma-separated directories to exclude")
    pack_p.add_argument("--stats", action="store_true", help="Force display of summary metrics")

    # Clip command
    clip_p = subparsers.add_parser("clip", help="Compress and copy directly to OS clipboard (ready to paste)")
    clip_p.add_argument("path", nargs="?", default=".", help="Source file or directory to compress and copy")
    clip_p.add_argument("--git", action="store_true", help="Clip only git-modified files")
    clip_p.add_argument("--staged", action="store_true", help="Clip only git staged changes")
    clip_p.add_argument("--no-docs", action="store_true", help="Omit docstrings")

    # Diff command
    diff_p = subparsers.add_parser("diff", help="View colored terminal diff showing shaved lines")
    diff_p.add_argument("path", help="Target Python file to diff")
    diff_p.add_argument("--no-docs", action="store_true", help="Omit docstrings")

    # Inspect command
    inspect_p = subparsers.add_parser("inspect", help="Inspect compressed skeleton of a single file")
    inspect_p.add_argument("path", help="Target Python file")
    inspect_p.add_argument("--no-docs", action="store_true", help="Omit docstrings")

    # MCP command
    subparsers.add_parser("mcp", help="Launch Model Context Protocol (MCP) stdio server")

    args = parser.parse_args()

    if args.command == "pack":
        sys.exit(handle_pack(args))
    elif args.command == "clip":
        sys.exit(handle_clip(args))
    elif args.command == "diff":
        sys.exit(handle_diff(args))
    elif args.command == "inspect":
        sys.exit(handle_inspect(args))
    elif args.command == "mcp":
        run_mcp_server()


if __name__ == "__main__":
    main()
