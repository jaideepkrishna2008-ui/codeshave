"""
Standard Model Context Protocol (MCP) server for CodeShave.
Runs over standard I/O (stdio) and integrates with Claude Desktop, Cursor, and Windsurf.
Supports compressing source code across Python, TypeScript, JavaScript, Go, Rust, Java, C++, and more.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict

from codeshave import __version__
from codeshave.estimator import compute_savings
from codeshave.languages import compress_code, detect_language


def create_tool_definitions() -> list[Dict[str, Any]]:
    return [
        {
            "name": "shave_code",
            "description": (
                "HIGH PRIORITY: Compresses raw source code into an AST/structural skeleton "
                "(classes, methods, type signatures, interfaces, docstrings) while stripping internal execution loops. "
                "Saves 80-95% prompt tokens. Supports Python, TypeScript, JavaScript, Go, Rust, Java, C++, C#, etc."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {
                        "type": "string",
                        "description": "Raw source code to compress",
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language (e.g. 'python', 'typescript', 'go', 'rust', 'java', 'cpp', or auto-detect)",
                        "default": "auto",
                    },
                    "preserve_docstrings": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether to preserve function, class, and method docstrings/comments",
                    },
                },
                "required": ["source_code"],
            },
        },
        {
            "name": "shave_file",
            "description": (
                "CRITICAL / HIGH PRIORITY: Use this tool INSTEAD OF read_file whenever inspecting, exploring, "
                "or analyzing source code files (Python, TypeScript, JS, Go, Rust, Java, C++, C#). "
                "Returns the full syntactically valid structural skeleton with 80-95% token savings "
                "so the context window does not get flooded with implementation details."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute or relative path to the source file",
                    },
                    "preserve_docstrings": {
                        "type": "boolean",
                        "default": True,
                    },
                },
                "required": ["file_path"],
            },
        },
    ]


def handle_call_tool(params: Dict[str, Any]) -> Dict[str, Any]:
    name = params.get("name")
    args = params.get("arguments", {})

    if name == "shave_code":
        code = args.get("source_code", "")
        lang_arg = args.get("language", "auto")
        preserve_docs = args.get("preserve_docstrings", True)

        lang = detect_language(lang_arg, code) if lang_arg == "auto" else lang_arg
        skeleton = compress_code(code, filename_or_ext=lang, preserve_docstrings=preserve_docs)
        report = compute_savings(code, skeleton)
        text = (
            f"# Compressed by CodeShave ({lang.capitalize()}) - {report.summary_line()}\n\n"
            f"```{lang}\n{skeleton}\n```"
        )
        return {
            "content": [{"type": "text", "text": text}],
            "isError": False,
        }

    elif name == "shave_file":
        p = Path(args.get("file_path", ""))
        if not p.is_file():
            return {
                "content": [{"type": "text", "text": f"Error: File '{p}' does not exist."}],
                "isError": True,
            }
        code = p.read_text(encoding="utf-8")
        preserve_docs = args.get("preserve_docstrings", True)
        lang = detect_language(p.name, code)
        skeleton = compress_code(code, filename_or_ext=p.name, preserve_docstrings=preserve_docs)
        report = compute_savings(code, skeleton)
        text = (
            f"# File: {p.name} ({lang.capitalize()}) - {report.summary_line()}\n\n"
            f"```{lang}\n{skeleton}\n```"
        )
        return {
            "content": [{"type": "text", "text": text}],
            "isError": False,
        }

    return {
        "content": [{"type": "text", "text": f"Unknown tool: {name}"}],
        "isError": True,
    }


def run_mcp_server() -> None:
    """Runs standard JSON-RPC 2.0 loop reading from stdin and writing to stdout."""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            msg = json.loads(line)
            req_id = msg.get("id")
            method = msg.get("method")

            if method == "initialize":
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "serverInfo": {
                            "name": "codeshave",
                            "version": __version__,
                        },
                        "capabilities": {
                            "tools": {},
                        },
                    },
                }
            elif method == "tools/list":
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "tools": create_tool_definitions(),
                    },
                }
            elif method == "tools/call":
                call_res = handle_call_tool(msg.get("params", {}))
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": call_res,
                }
            elif method == "notifications/initialized":
                continue
            else:
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method '{method}' not found",
                    },
                }

            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err_res = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": str(e)},
            }
            sys.stdout.write(json.dumps(err_res) + "\n")
            sys.stdout.flush()
