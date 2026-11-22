"""
Universal AI assistant connector for CodeShave.
Automatically discovers installed AI editors/assistants (Claude Desktop, Cursor,
Windsurf, Antigravity, VS Code) and registers the CodeShave MCP server with zero manual JSON editing.
"""

from __future__ import annotations

import json
import os
import platform
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class ClientTarget:
    key: str
    display_name: str
    config_paths: List[Path]


def get_home_dir() -> Path:
    return Path.home()


def get_claude_desktop_paths() -> List[Path]:
    """Finds all potential Claude Desktop config paths across platforms, including Windows Store."""
    system = platform.system()
    paths: List[Path] = []

    if system == "Windows":
        appdata = os.environ.get("APPDATA")
        localappdata = os.environ.get("LOCALAPPDATA")

        # 1. Standard Win32 installer path
        if appdata:
            paths.append(Path(appdata) / "Claude" / "claude_desktop_config.json")

        # 2. Windows Store / AppContainer MSIX sandboxed path
        if localappdata:
            packages_dir = Path(localappdata) / "Packages"
            if packages_dir.exists():
                for p in packages_dir.glob("Claude_*"):
                    store_config = p / "LocalCache" / "Roaming" / "Claude" / "claude_desktop_config.json"
                    paths.append(store_config)

    elif system == "Darwin":  # macOS
        paths.append(get_home_dir() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json")
    else:  # Linux
        paths.append(get_home_dir() / ".config" / "Claude" / "claude_desktop_config.json")

    return paths


def get_cursor_paths() -> List[Path]:
    """Finds Cursor MCP configuration paths."""
    paths: List[Path] = [
        get_home_dir() / ".cursor" / "mcp.json",
    ]
    if platform.system() == "Windows":
        appdata = os.environ.get("APPDATA")
        if appdata:
            paths.append(
                Path(appdata) / "Cursor" / "User" / "globalStorage" / "rooveterinaryinc.cursor-mcp" / "mcp.json"
            )
    return paths


def get_windsurf_paths() -> List[Path]:
    """Finds Windsurf MCP configuration paths."""
    return [
        get_home_dir() / ".codeium" / "windsurf" / "mcp_config.json",
    ]


def get_antigravity_paths() -> List[Path]:
    """Finds Antigravity MCP configuration paths."""
    return [
        get_home_dir() / ".gemini" / "antigravity" / "mcp_config.json",
    ]


def get_vscode_paths() -> List[Path]:
    """Finds VS Code MCP configuration paths (global or workspace)."""
    paths: List[Path] = [
        Path.cwd() / ".vscode" / "mcp.json",
    ]
    if platform.system() == "Windows":
        appdata = os.environ.get("APPDATA")
        if appdata:
            paths.append(Path(appdata) / "Code" / "User" / "globalStorage" / "mcp.json")
    return paths


def get_supported_targets() -> Dict[str, ClientTarget]:
    return {
        "claude": ClientTarget("claude", "Claude Desktop", get_claude_desktop_paths()),
        "cursor": ClientTarget("cursor", "Cursor IDE", get_cursor_paths()),
        "windsurf": ClientTarget("windsurf", "Windsurf Editor", get_windsurf_paths()),
        "antigravity": ClientTarget("antigravity", "Antigravity", get_antigravity_paths()),
        "vscode": ClientTarget("vscode", "VS Code", get_vscode_paths()),
    }


def read_config_json(path: Path) -> Tuple[dict, bool]:
    """Reads JSON config file, creating an empty template if it doesn't exist."""
    if not path.exists():
        return {"mcpServers": {}}, False
    try:
        content = path.read_text(encoding="utf-8")
        if not content.strip():
            return {"mcpServers": {}}, True
        data = json.loads(content)
        if not isinstance(data, dict):
            return {"mcpServers": {}}, True
        if "mcpServers" not in data or not isinstance(data["mcpServers"], dict):
            data["mcpServers"] = {}
        return data, True
    except Exception:
        return {"mcpServers": {}}, True


def write_config_json(path: Path, data: dict, dry_run: bool = False) -> None:
    """Safely writes JSON configuration, ensuring parent directories exist."""
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(data, indent=2) + "\n"
    path.write_text(content, encoding="utf-8")


def check_target_status(target: ClientTarget) -> List[Tuple[Path, bool, bool]]:
    """Returns [(path, exists_on_disk, codeshave_configured), ...]."""
    results = []
    for path in target.config_paths:
        exists = path.exists()
        configured = False
        if exists:
            data, _ = read_config_json(path)
            configured = "codeshave" in data.get("mcpServers", {})
        results.append((path, exists, configured))
    return results


def connect_target(
    target: ClientTarget,
    command: str = "uvx",
    args: Optional[List[str]] = None,
    dry_run: bool = False,
) -> List[Tuple[Path, str]]:
    """Injects codeshave MCP server entry into target config file(s)."""
    server_args = args if args is not None else ["codeshave", "mcp"]
    server_config = {
        "command": command,
        "args": server_args,
    }

    actions: List[Tuple[Path, str]] = []
    paths_to_update = target.config_paths

    # If multiple paths (e.g. Windows Store vs standard Claude), pick existing ones
    # or write to the primary standard one.
    existing_paths = [p for p in paths_to_update if p.exists() or p.parent.exists()]
    if not existing_paths and paths_to_update:
        existing_paths = [paths_to_update[0]]

    for path in existing_paths:
        data, existed = read_config_json(path)
        mcp_servers = data.setdefault("mcpServers", {})

        if "codeshave" in mcp_servers and mcp_servers["codeshave"] == server_config:
            actions.append((path, "already-configured"))
            continue

        mcp_servers["codeshave"] = server_config
        write_config_json(path, data, dry_run=dry_run)
        action_name = "updated" if existed else "created"
        actions.append((path, action_name))

    return actions


def disconnect_target(target: ClientTarget, dry_run: bool = False) -> List[Tuple[Path, str]]:
    """Removes codeshave MCP server entry from target config file(s)."""
    actions: List[Tuple[Path, str]] = []
    for path in target.config_paths:
        if not path.exists():
            continue
        data, _ = read_config_json(path)
        mcp_servers = data.get("mcpServers", {})
        if "codeshave" in mcp_servers:
            del mcp_servers["codeshave"]
            write_config_json(path, data, dry_run=dry_run)
            actions.append((path, "removed"))
        else:
            actions.append((path, "not-present"))
    return actions
