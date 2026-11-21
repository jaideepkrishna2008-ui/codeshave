"""
Standard Model Context Protocol (MCP) server for CodeShave.
Runs over standard I/O (stdio) and integrates with Claude Desktop, Cursor, and Windsurf.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict

from codeshave import __version__
from codeshave.estimator import compute_savings
from codeshave.parser import compress_source


def create_tool_definitions() -> list[Dict[str, Any]]:
    return [
        {
            "name": "shave_code",
            "description": "Compress raw Python source code into a syntax-valid AST skeleton for prompts.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {
                        "type": "string",
                        "description": "Raw Python code to compress",
                    },
                    "preserve_docstrings": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether to preserve function and class docstrings",
                    },
                },
                "required": ["source_code"],
            },
        },
        {
            "name": "shave_file",
            "description": "Read a file from disk and return its compressed AST skeleton.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute or relative path to the Python file",
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
        preserve_docs = args.get("preserve_docstrings", True)
        skeleton = compress_source(code, preserve_docstrings=preserve_docs)
        report = compute_savings(code, skeleton)
        text = (
            f"# Compressed by CodeShave ({report.summary_line()})\n\n"
            f"```python\n{skeleton}\n```"
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
        skeleton = compress_source(code, preserve_docstrings=preserve_docs)
        report = compute_savings(code, skeleton)
        text = (
            f"# File: {p.name} ({report.summary_line()})\n\n"
            f"```python\n{skeleton}\n```"
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
    """Standard stdio JSON-RPC 2.0 loop."""
    sys.stderr.write(f"⚡ CodeShave MCP Server v{__version__} listening on stdio...\n")
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue

        try:
            req = json.loads(line)
        except Exception:
            continue

        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        if method == "initialize":
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "codeshave", "version": __version__},
                },
            }
        elif method == "tools/list":
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": create_tool_definitions()},
            }
        elif method == "tools/call":
            result = handle_call_tool(params)
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": result,
            }
        else:
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": "Method not found"},
            }

        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()
