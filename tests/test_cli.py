import sys
from pathlib import Path
import pytest
from tokenskel.cli import main


def test_cli_pack_runs_cleanly(tmp_path: Path, monkeypatch, capsys):
    sample_file = tmp_path / "service.py"
    sample_file.write_text("class MyService:\n    def run(self):\n        print('heavy loop')\n")

    out_file = tmp_path / "output.md"

    test_args = ["tokenskel", "pack", str(tmp_path), "-o", str(out_file), "-f", "md"]
    monkeypatch.setattr(sys, "argv", test_args)

    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 0
    assert out_file.exists()
    content = out_file.read_text()
    assert "class MyService:" in content
    assert "..." in content
    assert "print('heavy loop')" not in content
