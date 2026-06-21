"""Shared fixtures for forge-mcp tests."""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "forge-public-safe"


@pytest.fixture
def forge_fixture_root() -> Path:
    """Return the path to the public-safe Forge test fixture."""
    return FIXTURE_ROOT


@pytest.fixture
def forge_env(monkeypatch: pytest.MonkeyPatch, forge_fixture_root: Path) -> Path:
    """Set FORGE_REPOSITORY_ROOT to the test fixture and return the root."""
    monkeypatch.setenv("FORGE_REPOSITORY_ROOT", str(forge_fixture_root))
    return forge_fixture_root
