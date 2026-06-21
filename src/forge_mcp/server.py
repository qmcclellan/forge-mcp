"""MCP server exposing read-only Forge repository knowledge.

v0.1.0 exports exactly 10 read-only tools. No write tools exist.
All tool calls are confined to the configured Forge repository root.
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from . import __version__
from .config import get_forge_root
from .errors import DocumentNotFoundError, ForgeMCPError, structured_error
from .repository import ForgeRepository
from .services import ForgeKnowledge

mcp = FastMCP("forge-mcp")
mcp._mcp_server.version = __version__


def _knowledge() -> ForgeKnowledge:
    """Create a ForgeKnowledge instance bound to the configured root."""
    root = get_forge_root()
    return ForgeKnowledge(ForgeRepository(root))


@mcp.tool()
def get_forge_overview() -> dict[str, Any]:
    """Return Forge purpose, version, CLI entry point, major capabilities, known templates, and documentation paths."""
    try:
        return _knowledge().get_overview()
    except ForgeMCPError as exc:
        return structured_error("FORGE_ROOT_ERROR", str(exc))


@mcp.tool()
def list_templates() -> dict[str, Any]:
    """Return locally available Forge templates with stable identifiers and concise metadata."""
    try:
        return _knowledge().list_templates()
    except ForgeMCPError as exc:
        return structured_error("FORGE_ROOT_ERROR", str(exc))


@mcp.tool()
def get_template_summary(template: str) -> dict[str, Any]:
    """Return one template's purpose, language, runtime, files, variables, optional artifacts, and expected output structure."""
    try:
        return _knowledge().get_template_summary(template)
    except ForgeMCPError as exc:
        code = "TEMPLATE_NOT_FOUND" if "not found" in str(exc).lower() else "FORGE_ERROR"
        return structured_error(code, str(exc))


@mcp.tool()
def list_template_files(template: str) -> dict[str, Any]:
    """Return a bounded, sorted, relative file listing for one template."""
    try:
        return _knowledge().list_template_files(template)
    except ForgeMCPError as exc:
        code = "TEMPLATE_NOT_FOUND" if "not found" in str(exc).lower() else "FORGE_ERROR"
        return structured_error(code, str(exc))


@mcp.tool()
def read_template_file(template: str, rel_path: str) -> dict[str, Any]:
    """Read an approved text file inside a selected template. Rejects binary files, oversized files, path traversal, absolute paths, and symlinks."""
    try:
        return _knowledge().read_template_file(template, rel_path)
    except ForgeMCPError as exc:
        code = "PATH_VIOLATION" if "PathViolation" in type(exc).__name__ else "FORGE_ERROR"
        return structured_error(code, str(exc))


@mcp.tool()
def get_project_structure() -> dict[str, Any]:
    """Explain common generated-project conventions and template-specific layout based on Forge source, templates, and documentation."""
    try:
        return _knowledge().get_project_structure()
    except ForgeMCPError as exc:
        return structured_error("FORGE_ROOT_ERROR", str(exc))


@mcp.tool()
def get_validation_commands() -> dict[str, Any]:
    """Return documented Forge validation commands as inert strings. The executed field is always false — these are never run by forge-mcp."""
    try:
        return _knowledge().get_validation_commands()
    except ForgeMCPError as exc:
        return structured_error("FORGE_ROOT_ERROR", str(exc))


@mcp.tool()
def read_forge_document(document_id: str) -> dict[str, Any]:
    """Read approved Forge documentation using a stable document identifier. Approved identifiers: readme, runbook, architecture, artifact-publishing, template-registry-runbook, interview-talk-track, forge-yaml-example."""
    try:
        return _knowledge().read_forge_document(document_id)
    except DocumentNotFoundError as exc:
        return structured_error("DOCUMENT_NOT_FOUND", str(exc))
    except ForgeMCPError as exc:
        return structured_error("DOCUMENT_ERROR", str(exc))


@mcp.tool()
def explain_forge_doctor() -> dict[str, Any]:
    """Explain what forge doctor checks, which checks are required or optional, and how overall success is calculated."""
    try:
        return _knowledge().explain_doctor()
    except ForgeMCPError as exc:
        return structured_error("FORGE_ROOT_ERROR", str(exc))


@mcp.tool()
def get_template_change_checklist() -> dict[str, Any]:
    """Return the source-backed process for safely adding or changing a Forge template, including validation, tests, documentation, and artifact steps."""
    try:
        return _knowledge().get_template_change_checklist()
    except ForgeMCPError as exc:
        return structured_error("FORGE_ROOT_ERROR", str(exc))
