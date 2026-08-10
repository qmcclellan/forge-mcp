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


# --- KS-0046: the declared MCP dependency must stay truthful ---
# forge-mcp is a FastMCP consumer. mcp 2.x removed mcp.server.fastmcp, so an
# unconstrained declaration lets a clean install resolve a release this package
# cannot import. These assert the DECLARED requirement from real distribution
# metadata, not a hand-copied string, so an unbounded declaration cannot return
# silently.


def _declared_mcp_requirement():
    from importlib.metadata import requires

    from packaging.requirements import Requirement

    for raw in requires("forge-mcp") or []:
        requirement = Requirement(raw)
        if requirement.marker is None and requirement.name == "mcp":
            return requirement
    raise AssertionError("forge-mcp declares no unconditional mcp requirement")


def test_declared_mcp_requirement_excludes_the_incompatible_major():
    from packaging.version import Version

    specifier = _declared_mcp_requirement().specifier

    # 2.0.0 is the release that removed mcp.server.fastmcp.
    assert not specifier.contains(Version("2.0.0")), (
        "the declared mcp requirement still permits 2.x, which cannot be imported"
    )
    assert not specifier.contains(Version("1.0.0")), (
        "mcp 1.0.0 provides neither mcp.server.fastmcp nor the cli extra"
    )


def test_declared_mcp_requirement_permits_the_supported_releases():
    """The bound must not be so tight that the supported environment is excluded."""
    from packaging.version import Version

    specifier = _declared_mcp_requirement().specifier

    for supported in ("1.28.0", "1.29.0"):
        assert specifier.contains(Version(supported)), (
            f"the declared mcp requirement excludes verified-good {supported}"
        )


def test_installed_mcp_satisfies_the_declared_requirement():
    """The environment actually running the suite must honour the declaration."""
    from importlib.metadata import version

    from packaging.version import Version

    installed = Version(version("mcp"))
    assert _declared_mcp_requirement().specifier.contains(installed), (
        f"installed mcp {installed} does not satisfy the declared requirement"
    )


def test_fastmcp_entry_point_is_importable():
    """The specific API the declaration exists to protect."""
    from mcp.server.fastmcp import FastMCP  # noqa: F401
