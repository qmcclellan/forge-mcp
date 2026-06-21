"""Exact exported-tool contract test.

This test asserts the precise v0.1.1 tool names. Any addition, removal, or rename
of a tool is a breaking contract change and must fail here first.
"""

from __future__ import annotations

from forge_mcp.server import mcp

# Exact v0.1.1 tool contract — do not modify without a version bump.
EXPECTED_TOOL_NAMES = frozenset(
    {
        "get_forge_overview",
        "list_templates",
        "get_template_summary",
        "list_template_files",
        "read_template_file",
        "get_project_structure",
        "get_validation_commands",
        "read_forge_document",
        "explain_forge_doctor",
        "get_template_change_checklist",
    }
)


def test_exact_tool_names():
    tools = mcp._tool_manager.list_tools()
    actual = frozenset(t.name for t in tools)
    assert actual == EXPECTED_TOOL_NAMES, (
        f"Tool contract violation.\n"
        f"  Expected: {sorted(EXPECTED_TOOL_NAMES)}\n"
        f"  Actual:   {sorted(actual)}\n"
        f"  Added:    {sorted(actual - EXPECTED_TOOL_NAMES)}\n"
        f"  Removed:  {sorted(EXPECTED_TOOL_NAMES - actual)}"
    )


def test_tool_count():
    tools = mcp._tool_manager.list_tools()
    assert len(tools) == 10, f"Expected 10 tools, got {len(tools)}"


def test_no_write_tools():
    """Guard against write tools being added accidentally."""
    tools = mcp._tool_manager.list_tools()
    names = {t.name for t in tools}
    disallowed_prefixes = ("create_", "write_", "update_", "delete_", "init_", "mutate_")
    for name in names:
        for prefix in disallowed_prefixes:
            assert not name.startswith(prefix), f"Write tool detected: {name}"
