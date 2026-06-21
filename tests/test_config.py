"""Tests for Forge repository root configuration and validation."""

from __future__ import annotations

import pytest

from forge_mcp.config import get_forge_root
from forge_mcp.errors import ForgeRootError


def test_missing_env_var_raises(monkeypatch):
    monkeypatch.delenv("FORGE_REPOSITORY_ROOT", raising=False)
    with pytest.raises(ForgeRootError, match="FORGE_REPOSITORY_ROOT"):
        get_forge_root()


def test_empty_env_var_raises(monkeypatch):
    monkeypatch.setenv("FORGE_REPOSITORY_ROOT", "")
    with pytest.raises(ForgeRootError):
        get_forge_root()


def test_whitespace_only_env_var_raises(monkeypatch):
    monkeypatch.setenv("FORGE_REPOSITORY_ROOT", "   ")
    with pytest.raises(ForgeRootError):
        get_forge_root()


def test_nonexistent_path_raises(monkeypatch, tmp_path):
    monkeypatch.setenv("FORGE_REPOSITORY_ROOT", str(tmp_path / "does-not-exist"))
    with pytest.raises(ForgeRootError, match="does not exist"):
        get_forge_root()


def test_file_not_directory_raises(monkeypatch, tmp_path):
    f = tmp_path / "forge.txt"
    f.write_text("not a dir")
    monkeypatch.setenv("FORGE_REPOSITORY_ROOT", str(f))
    with pytest.raises(ForgeRootError, match="directory"):
        get_forge_root()


def test_directory_missing_sentinel_raises(monkeypatch, tmp_path):
    # Directory exists but has no forge/cli.py or templates/
    monkeypatch.setenv("FORGE_REPOSITORY_ROOT", str(tmp_path))
    with pytest.raises(ForgeRootError, match="Forge repository"):
        get_forge_root()


def test_directory_missing_templates_raises(monkeypatch, tmp_path):
    (tmp_path / "forge").mkdir()
    (tmp_path / "forge" / "cli.py").write_text("# stub")
    # templates/ directory is absent
    monkeypatch.setenv("FORGE_REPOSITORY_ROOT", str(tmp_path))
    with pytest.raises(ForgeRootError, match="Forge repository"):
        get_forge_root()


def test_valid_fixture_root_succeeds(forge_env):
    root = get_forge_root()
    assert root.is_dir()


def test_returns_resolved_path(forge_env, forge_fixture_root):
    root = get_forge_root()
    assert root == forge_fixture_root.resolve()


def test_never_uses_cwd_as_default(monkeypatch):
    monkeypatch.delenv("FORGE_REPOSITORY_ROOT", raising=False)
    with pytest.raises(ForgeRootError):
        get_forge_root()
