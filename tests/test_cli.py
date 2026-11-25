import sys
from pathlib import Path
import pytest
from codeshave.cli import main
from codeshave.mcp import handle_call_tool, create_tool_definitions


def test_cli_pack_runs_cleanly(tmp_path: Path, monkeypatch, capsys):
    sample_file = tmp_path / "service.py"
    sample_file.write_text("class MyService:\n    def run(self):\n        print('heavy loop')\n")

    out_file = tmp_path / "output.md"

    test_args = ["codeshave", "pack", str(tmp_path), "-o", str(out_file), "-f", "md"]
    monkeypatch.setattr(sys, "argv", test_args)

    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 0
    assert out_file.exists()
    content = out_file.read_text()
    assert "class MyService:" in content
    assert "..." in content
    assert "print('heavy loop')" not in content


def test_cli_pack_with_budget(tmp_path: Path, monkeypatch):
    sample_file = tmp_path / "service.py"
    sample_file.write_text('def f():\n    """Very long docstring that exceeds small budget."""\n    return 1\n')
    out_file = tmp_path / "out.md"

    test_args = ["codeshave", "pack", str(tmp_path), "--budget", "5", "-o", str(out_file)]
    monkeypatch.setattr(sys, "argv", test_args)

    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 0
    content = out_file.read_text()
    assert "def f():" in content


def test_cli_clip_runs_cleanly(tmp_path: Path, monkeypatch, capsys):
    sample_file = tmp_path / "service.py"
    sample_file.write_text("def test_clip():\n    return 42\n")

    test_args = ["codeshave", "clip", str(sample_file)]
    monkeypatch.setattr(sys, "argv", test_args)

    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 0


def test_cli_diff_runs_cleanly(tmp_path: Path, monkeypatch, capsys):
    sample_file = tmp_path / "diff_test.py"
    sample_file.write_text("def my_func():\n    val = 100\n    return val\n")

    test_args = ["codeshave", "diff", str(sample_file)]
    monkeypatch.setattr(sys, "argv", test_args)

    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert "CodeShave Diff" in captured.out


def test_mcp_tools():
    tools = create_tool_definitions()
    names = [t["name"] for t in tools]
    assert "shave_code" in names
    assert "shave_file" in names
    for tool in tools:
        ann = tool.get("annotations")
        assert isinstance(ann, dict)
        assert ann["readOnlyHint"] is True
        assert ann["destructiveHint"] is False
        assert ann["idempotentHint"] is True
        assert ann["openWorldHint"] is False

    # Call shave_code
    res = handle_call_tool({
        "name": "shave_code",
        "arguments": {"source_code": "def hello():\n    print('world')\n"}
    })
    assert res["isError"] is False
    assert "def hello():" in res["content"][0]["text"]


def test_cli_pack_polyglot(tmp_path: Path, monkeypatch):
    (tmp_path / "app.py").write_text("def py_fn():\n    x = 10\n    return x\n")
    (tmp_path / "service.ts").write_text("export function tsFn(): void {\n    console.log('hi');\n}\n")
    (tmp_path / "main.go").write_text("package main\nfunc GoFn() {\n    println(1)\n}\n")

    out_file = tmp_path / "polyglot.md"
    test_args = ["codeshave", "pack", str(tmp_path), "-o", str(out_file), "-f", "md"]
    monkeypatch.setattr(sys, "argv", test_args)

    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 0
    content = out_file.read_text()
    assert "def py_fn():" in content
    assert "export function tsFn(): void {" in content
    assert "func GoFn() {" in content

