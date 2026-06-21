"""Structured exceptions and safe error helpers for forge-mcp."""

from __future__ import annotations

from typing import Any


class ForgeMCPError(Exception):
    """Base exception for forge-mcp."""


class ForgeRootError(ForgeMCPError):
    """Raised when the Forge repository root is invalid, missing, or unrecognizable."""


class TemplateNotFoundError(ForgeMCPError):
    """Raised when a requested template does not exist."""


class DocumentNotFoundError(ForgeMCPError):
    """Raised when a requested document identifier is unknown or the file is absent."""


class PathViolationError(ForgeMCPError):
    """Raised when a path fails confinement, traversal, symlink, binary, or size checks."""


def structured_error(code: str, message: str) -> dict[str, Any]:
    """Return a safe structured error dict without leaking host paths."""
    return {"error": {"code": code, "message": message}}
