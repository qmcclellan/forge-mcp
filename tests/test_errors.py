"""Tests for structured error helpers and exception hierarchy."""

from forge_mcp.errors import (
    DocumentNotFoundError,
    ForgeMCPError,
    ForgeRootError,
    PathViolationError,
    TemplateNotFoundError,
    structured_error,
)


def test_structured_error_shape():
    result = structured_error("SOME_CODE", "something went wrong")
    assert result == {"error": {"code": "SOME_CODE", "message": "something went wrong"}}


def test_structured_error_returns_dict():
    assert isinstance(structured_error("X", "y"), dict)


def test_exception_hierarchy():
    assert issubclass(ForgeRootError, ForgeMCPError)
    assert issubclass(TemplateNotFoundError, ForgeMCPError)
    assert issubclass(DocumentNotFoundError, ForgeMCPError)
    assert issubclass(PathViolationError, ForgeMCPError)


def test_structured_error_does_not_leak_path():
    result = structured_error("ERR", "file not found")
    msg = result["error"]["message"]
    assert "/srv" not in msg
    assert "/home" not in msg
