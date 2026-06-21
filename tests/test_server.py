"""Server import smoke tests and startup validation."""

from __future__ import annotations


def test_server_module_importable():
    import forge_mcp.server  # noqa: F401


def test_mcp_instance_exists():
    from forge_mcp.server import mcp
    assert mcp is not None


def test_server_version_matches_package():
    from forge_mcp import __version__
    from forge_mcp.server import mcp
    assert mcp._mcp_server.version == __version__


def test_server_name():
    from forge_mcp.server import mcp
    assert mcp.name == "forge-mcp"


def test_all_modules_importable():
    import forge_mcp.cli
    import forge_mcp.config
    import forge_mcp.errors
    import forge_mcp.limits
    import forge_mcp.models
    import forge_mcp.paths
    import forge_mcp.repository
    import forge_mcp.server  # noqa: F401
    import forge_mcp.services  # noqa: F401
    import forge_mcp.version  # noqa: F401


def test_package_version_string():
    from forge_mcp import __version__
    assert isinstance(__version__, str)
    assert __version__ == "0.1.1"
