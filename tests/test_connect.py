import json
import pytest
from pathlib import Path
from codeshave.connect import (
    ClientTarget,
    connect_target,
    disconnect_target,
    check_target_status,
    read_config_json,
    write_config_json,
)


def test_read_nonexistent_config(tmp_path: Path):
    cfg_file = tmp_path / "config.json"
    data, exists = read_config_json(cfg_file)
    assert not exists
    assert "mcpServers" in data


def test_write_and_read_config(tmp_path: Path):
    cfg_file = tmp_path / "nested" / "config.json"
    initial_data = {"mcpServers": {"other_server": {"command": "npx", "args": ["test"]}}}
    write_config_json(cfg_file, initial_data)
    assert cfg_file.exists()

    data, exists = read_config_json(cfg_file)
    assert exists
    assert "other_server" in data["mcpServers"]


def test_connect_target_merges_without_overwriting(tmp_path: Path):
    cfg_file = tmp_path / "claude_desktop_config.json"
    initial_data = {
        "preferences": {"theme": "dark"},
        "mcpServers": {
            "existing_tool": {"command": "node", "args": ["index.js"]}
        }
    }
    write_config_json(cfg_file, initial_data)

    target = ClientTarget("test_target", "Test Assistant", [cfg_file])
    actions = connect_target(target, command="uvx", args=["codeshave", "mcp"])

    assert len(actions) == 1
    assert actions[0][1] == "updated"

    # Verify content
    updated_data, _ = read_config_json(cfg_file)
    assert updated_data["preferences"]["theme"] == "dark"
    assert "existing_tool" in updated_data["mcpServers"]
    assert "codeshave" in updated_data["mcpServers"]
    assert updated_data["mcpServers"]["codeshave"]["command"] == "uvx"
    assert updated_data["mcpServers"]["codeshave"]["args"] == ["codeshave", "mcp"]


def test_connect_idempotent(tmp_path: Path):
    cfg_file = tmp_path / "config.json"
    target = ClientTarget("test", "Test", [cfg_file])

    # First connect
    connect_target(target)
    # Second connect
    actions = connect_target(target)
    assert actions[0][1] == "already-configured"


def test_disconnect_target(tmp_path: Path):
    cfg_file = tmp_path / "config.json"
    target = ClientTarget("test", "Test", [cfg_file])

    connect_target(target)
    status_before = check_target_status(target)
    assert status_before[0][2] is True  # configured

    disconnect_target(target)
    status_after = check_target_status(target)
    assert status_after[0][2] is False  # not configured
