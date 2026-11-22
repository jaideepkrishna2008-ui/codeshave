"""
CLI interface for CodeShave.
High-speed, zero-loss AST & structural code context compressor for AI coding assistants.
Supports Python, TypeScript, JavaScript, Go, Rust, Java, C++, C#, Swift, and more.
"""

from __future__ import annotations

import argparse
import difflib
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional, Set

from codeshave import __version__
from codeshave.clipboard import copy_to_clipboard
from codeshave.connect import (
    check_target_status,
    connect_target,
    disconnect_target,
    get_supported_targets,
)
from codeshave.estimator import compute_savings, estimate_tokens
from codeshave.formatters import FileContextItem, format_bundle
from codeshave.graph import DependencyResolver
from codeshave.languages import (
    EXTENSION_MAP,
    SUPPORTED_EXTENSIONS,
    compress_code,
    detect_language,
)
from codeshave.mcp import run_mcp_server

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
    "target",
    "bin",
    "obj",
    ".next",
    ".nuxt",
    ".output",
    "coverage",
    ".turbo",
}


def parse_lang_filter(lang_str: Optional[str]) -> Optional[Set[str]]:
    """Converts comma-separated language names or extensions to a set of extensions."""
    if not lang_str:
        return None
    allowed: Set[str] = set()
    for token in lang_str.split(","):
        token = token.strip().lower()
        if not token:
            continue
        if token.startswith("."):
            allowed.add(token)
        else:
            # Match language name in EXTENSION_MAP
            matched = False
            for ext, name in EXTENSION_MAP.items():
                if token in (name, ext.lstrip(".")):
                    allowed.add(ext)
                    matched = True
            if not matched:
                allowed.add(f".{token}")
    return allowed


def find_source_files(
    target: Path, excludes: Set[str], extensions: Optional[Set[str]] = None
) -> List[Path]:
    """Recursively finds all supported source files excluding build and cache folders."""
    allowed_exts = extensions or SUPPORTED_EXTENSIONS
    if target.is_file():
        return [target]

    found: List[Path] = []
    for p in sorted(target.rglob("*")):
        if not p.is_file():
            continue
        if p.suffix.lower() not in allowed_exts:
            continue
        parts = set(p.parts)
        if parts.intersection(excludes):
            continue
        found.append(p)
    return found


def find_git_modified_files(
    repo_path: Path, staged: bool = False, extensions: Optional[Set[str]] = None
) -> List[Path]:
    """Retrieves list of modified source files in git working tree or index."""
    allowed_exts = extensions or SUPPORTED_EXTENSIONS
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
            p = (repo_path / line).resolve()
            if p.is_file() and p.suffix.lower() in allowed_exts:
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

    lang_exts = parse_lang_filter(getattr(args, "lang", None))

    if args.git or args.staged:
        files = find_git_modified_files(target, staged=args.staged, extensions=lang_exts)
        if not files:
            sys.stderr.write("No modified source files detected in git working tree.\n")
            return 0
    else:
        files = find_source_files(target, excludes, extensions=lang_exts)

    if not files:
        sys.stderr.write("No source files found to process.\n")
        return 1

    # Python dependency resolution ordering if applicable
    if target.is_dir() and not args.no_sort:
        try:
            resolver = DependencyResolver(target)
            files = resolver.sort_files_by_dependency(files)
        except Exception:
            pass

    items: List[FileContextItem] = []
    total_orig_tokens = 0
    total_comp_tokens = 0

    preserve_docs = not args.no_docs
    preserve_priv = not args.no_private

    if args.stats or not args.output:
        sys.stderr.write(f"\n⚡ CodeShave v{__version__} — Universal Multi-Language Code Compressor\n")
        sys.stderr.write(f"Scanning: {target}\n\n")
        header = f"{'FILE':<45} {'LANG':<10} {'ORIGINAL':<12} {'SKELETON':<12} {'SAVINGS':<10}"
        sys.stderr.write(header + "\n")
        sys.stderr.write("─" * len(header) + "\n")

    for f in files:
        rel_path = f.relative_to(target) if target.is_dir() else f.name
        try:
            content = f.read_text(encoding="utf-8")
            compressed = compress_code(
                content,
                filename_or_ext=f.name,
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

            lang = detect_language(f.name, content)
            pct = ((1.0 - comp_t / orig_t) * 100.0) if orig_t > 0 else 0.0
            if args.stats or not args.output:
                path_str = str(rel_path).replace("\\", "/")
                if len(path_str) > 43:
                    path_str = "..." + path_str[-40:]
                sys.stderr.write(
                    f"{path_str:<45} {lang:<10} {orig_t:>8,} t {comp_t:>8,} t {pct:>8.1f}%\n"
                )
        except Exception as e:
            sys.stderr.write(f"Warning: Failed to process {rel_path}: {e}\n")

    if not items:
        sys.stderr.write("Error: No files could be compressed.\n")
        return 1

    # Token budget enforcement
    if args.budget and total_comp_tokens > args.budget:
        sys.stderr.write(
            f"\n⚠ Warning: Skeleton tokens ({total_comp_tokens:,}) exceed budget ({args.budget:,}). "
            f"Applying aggressive budget pruning...\n"
        )
        for item in items:
            lines = item.compressed_code.splitlines()
            if len(lines) > 20:
                item.compressed_code = "\n".join(lines[:20]) + "\n... [truncated to fit token budget]"
                item.compressed_tokens = estimate_tokens(item.compressed_code)

        total_comp_tokens = sum(it.compressed_tokens for it in items)

    elapsed = time.perf_counter() - start_time
    total_saved = max(0, total_orig_tokens - total_comp_tokens)
    total_pct = (
        (total_saved / total_orig_tokens) * 100.0 if total_orig_tokens > 0 else 0.0
    )

    if args.stats or not args.output:
        sys.stderr.write("─" * len(header) + "\n")
        sys.stderr.write(
            f"{'TOTAL':<45} {'':<10} {total_orig_tokens:>8,} t {total_comp_tokens:>8,} t {total_pct:>8.1f}%\n\n"
        )
        sys.stderr.write(
            f"✔ Processed {len(items)} files in {elapsed * 1000.0:.1f}ms\n"
            f"✔ Total token savings: {total_saved:,} tokens ({total_pct:.1f}% reduction)\n"
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

    lang_exts = parse_lang_filter(getattr(args, "lang", None))

    if args.git or args.staged:
        files = find_git_modified_files(target, staged=args.staged, extensions=lang_exts)
    elif target.is_file():
        files = [target]
    else:
        files = find_source_files(target, DEFAULT_EXCLUDES, extensions=lang_exts)

    if not files:
        sys.stderr.write("No source files found to clip.\n")
        return 1

    if len(files) == 1 and target.is_file():
        content = target.read_text(encoding="utf-8")
        compressed = compress_code(
            content,
            filename_or_ext=target.name,
            preserve_docstrings=not args.no_docs,
        )
        lang = detect_language(target.name, content)
        report = compute_savings(content, compressed)
        formatted = f"# File: {target.name}\n```{lang}\n{compressed}\n```\n"
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
            comp = compress_code(
                code,
                filename_or_ext=f.name,
                preserve_docstrings=not args.no_docs,
            )
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
    compressed = compress_code(
        content,
        filename_or_ext=target.name,
        preserve_docstrings=not args.no_docs,
    )
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

    lang = detect_language(target.name, content)
    sys.stdout.write(f"\n⚡ CodeShave Diff for {target.name} ({lang.capitalize()})\n")
    sys.stdout.write(f"{report.summary_line()}\n\n")

    for line in diff:
        if line.startswith("+") and not line.startswith("+++"):
            sys.stdout.write(f"\033[32m{line}\033[0m")
        elif line.startswith("-") and not line.startswith("---"):
            sys.stdout.write(f"\033[31m{line}\033[0m")
        elif line.startswith("@@"):
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
    compressed = compress_code(
        content,
        filename_or_ext=target.name,
        preserve_docstrings=not args.no_docs,
    )
    report = compute_savings(content, compressed)
    lang = detect_language(target.name, content)

    sys.stdout.write(f"# Compressed Skeleton for {target.name} ({lang.capitalize()})\n")
    sys.stdout.write(f"# {report.summary_line()}\n\n")
    sys.stdout.write(compressed + "\n")
    return 0


def handle_connect(args: argparse.Namespace) -> int:
    targets = get_supported_targets()
    selected_targets = list(targets.values()) if args.target == "all" else [targets[args.target]]

    if args.status:
        sys.stdout.write("CodeShave AI Assistant Connections:\n")
        sys.stdout.write("====================================\n")
        for target in selected_targets:
            statuses = check_target_status(target)
            sys.stdout.write(f"\n[{target.display_name}]\n")
            for path, exists, configured in statuses:
                status_icon = "✓ Connected" if configured else ("○ Not configured" if exists else "✗ Not detected")
                sys.stdout.write(f"  • {path}: {status_icon}\n")
        return 0

    if args.remove:
        sys.stdout.write("Disconnecting CodeShave MCP:\n")
        for target in selected_targets:
            actions = disconnect_target(target, dry_run=args.dry_run)
            for path, action in actions:
                prefix = "[DRY-RUN] " if args.dry_run else ""
                sys.stdout.write(f"  {prefix}✓ Removed from {target.display_name} ({path})\n")
        return 0

    cmd = getattr(args, "cmd", "uvx")
    mcp_args = ["codeshave", "mcp"] if cmd == "uvx" else ["-m", "codeshave.mcp"]

    sys.stdout.write(f"Connecting CodeShave MCP to AI assistants (Command: {cmd} {' '.join(mcp_args)}):\n")
    sys.stdout.write("=========================================================================\n")

    any_configured = False
    for target in selected_targets:
        actions = connect_target(target, command=cmd, args=mcp_args, dry_run=args.dry_run)
        for path, action in actions:
            prefix = "[DRY-RUN] " if args.dry_run else ""
            if action in ("created", "updated"):
                sys.stdout.write(f"  {prefix}✓ Configured {target.display_name}: {path}\n")
                any_configured = True
            elif action == "already-configured":
                sys.stdout.write(f"  {prefix}✓ {target.display_name} already configured: {path}\n")
                any_configured = True

    if not any_configured:
        sys.stdout.write("\nNo supported assistant directories were detected.\n")
        return 1

    sys.stdout.write("\n✨ Successfully connected! Restart your AI assistants to activate CodeShave.\n")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="codeshave",
        description="⚡ CodeShave: Universal AST & structural code context compressor for AI coding assistants.",
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
    pack_p.add_argument("--lang", help="Filter by language or extension (e.g. 'python', 'ts', 'go,rust')")
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
    clip_p.add_argument("--lang", help="Filter by language or extension")
    clip_p.add_argument("--git", action="store_true", help="Clip only git-modified files")
    clip_p.add_argument("--staged", action="store_true", help="Clip only git staged changes")
    clip_p.add_argument("--no-docs", action="store_true", help="Omit docstrings")

    # Diff command
    diff_p = subparsers.add_parser("diff", help="View colored terminal diff showing shaved lines")
    diff_p.add_argument("path", help="Target source file to diff")
    diff_p.add_argument("--no-docs", action="store_true", help="Omit docstrings")

    # Inspect command
    inspect_p = subparsers.add_parser("inspect", help="Inspect compressed skeleton of a single file")
    inspect_p.add_argument("path", help="Target source file")
    inspect_p.add_argument("--no-docs", action="store_true", help="Omit docstrings")

    # MCP command
    subparsers.add_parser("mcp", help="Launch Model Context Protocol (MCP) stdio server")

    # Connect command
    conn_p = subparsers.add_parser("connect", help="Automatically connect CodeShave to AI assistants (Claude, Cursor, Windsurf, etc.)")
    conn_p.add_argument(
        "target",
        nargs="?",
        default="all",
        choices=["all", "claude", "cursor", "windsurf", "antigravity", "vscode"],
        help="Target AI assistant to configure (default: all)",
    )
    conn_p.add_argument("--status", action="store_true", help="Display MCP connection status across all detected clients")
    conn_p.add_argument("--remove", action="store_true", help="Remove CodeShave from the target assistant(s)")
    conn_p.add_argument("--dry-run", action="store_true", help="Preview configuration changes without writing to disk")
    conn_p.add_argument("--cmd", default="uvx", help="MCP server execution command (default: uvx)")

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
    elif args.command == "connect":
        sys.exit(handle_connect(args))


if __name__ == "__main__":
    main()
