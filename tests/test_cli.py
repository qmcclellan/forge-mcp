"""Tests for the forge-mcp CLI argument parser."""

from __future__ import annotations

import pytest

from forge_mcp import __version__
from forge_mcp.cli import build_parser


def test_version_flag(capsys):
    parser = build_parser()
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--version"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert f"forge-mcp {__version__}" in captured.out


def test_forge_root_arg():
    parser = build_parser()
    args = parser.parse_args(["--forge-root", "/some/path"])
    assert args.forge_root == "/some/path"


def test_forge_root_default_is_none():
    parser = build_parser()
    args = parser.parse_args([])
    assert args.forge_root is None


def test_unknown_args_rejected():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["--not-a-real-flag"])


def test_main_exits_with_code_1_on_missing_root(monkeypatch, capsys):
    """main() must exit 1 when FORGE_REPOSITORY_ROOT is unset and --forge-root not given."""
    monkeypatch.delenv("FORGE_REPOSITORY_ROOT", raising=False)
    from forge_mcp.__main__ import main
    with pytest.raises(SystemExit) as exc_info:
        main([])
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "forge-mcp" in captured.err


def test_main_exits_with_code_1_on_invalid_root(monkeypatch, tmp_path, capsys):
    """main() must exit 1 when the path is not a Forge repository."""
    monkeypatch.setenv("FORGE_REPOSITORY_ROOT", str(tmp_path / "does-not-exist"))
    from forge_mcp.__main__ import main
    with pytest.raises(SystemExit) as exc_info:
        main([])
    assert exc_info.value.code == 1
