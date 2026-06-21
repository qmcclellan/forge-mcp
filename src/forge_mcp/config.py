"""Forge repository root configuration for forge-mcp.

forge-mcp requires an explicit FORGE_REPOSITORY_ROOT environment variable or
--forge-root CLI argument. It deliberately has no default path and fails closed
if the variable is unset or the path is not recognizably a Forge repository.
"""

from __future__ import annotations

import os
from pathlib import Path

from .errors import ForgeRootError

_ENV_VAR = "FORGE_REPOSITORY_ROOT"

# Sentinel files that must be present for a directory to be accepted as Forge root.
_SENTINEL_FILES = (
    "forge/cli.py",
    "templates",
)


def get_forge_root() -> Path:
    """Return the validated, resolved Forge repository root.

    Reads FORGE_REPOSITORY_ROOT from the environment. Raises ForgeRootError if
    the variable is unset, the path is missing or not a directory, or the path
    does not contain the expected Forge repository structure.

    Never falls back to CWD or any default path.
    """
    raw = os.environ.get(_ENV_VAR)
    if not raw or not raw.strip():
        raise ForgeRootError(
            f"{_ENV_VAR} is not set. "
            f"Set {_ENV_VAR}=/path/to/forge or pass --forge-root."
        )

    path = Path(raw).expanduser().resolve()

    if not path.exists():
        raise ForgeRootError(
            f"Forge root path does not exist ({_ENV_VAR} is set but path is missing)"
        )

    if not path.is_dir():
        raise ForgeRootError("Forge root must be a directory")

    for sentinel in _SENTINEL_FILES:
        sentinel_path = path / sentinel
        if not sentinel_path.exists():
            raise ForgeRootError(
                f"Path does not appear to be a Forge repository "
                f"(missing expected path: {sentinel})"
            )

    return path
