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
    """Parse the mcp requirement from the COMMITTED pyproject.toml.

    Deliberately not importlib.metadata.requires("forge-mcp"): that reads
    INSTALLED distribution metadata, which is recorded at install time and does
    not track later pyproject edits. With an editable install plus stray
    build-artifact egg-infos, several forge-mcp distributions can be
    discoverable at once and the first one wins, so the same assertion passed or
    failed depending on which artifacts happened to exist. The committed file is
    the thing this guard exists to protect, so it is the thing it reads.
    """
    import sys
    from pathlib import Path

    if sys.version_info >= (3, 11):
        import tomllib
    else:  # Python 3.10 is still supported; tomllib arrived in 3.11.
        import tomli as tomllib

    from packaging.requirements import Requirement

    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    assert pyproject.is_file(), f"committed pyproject.toml not found at {pyproject}"

    declared = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    for raw in declared["project"]["dependencies"]:
        requirement = Requirement(raw)
        if requirement.name == "mcp":
            return requirement
    raise AssertionError("pyproject declares no mcp dependency")


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


def test_declared_mcp_requirement_keeps_the_cli_extra():
    """The `cli` extra is part of the contract, not incidental.

    Dropping it would still satisfy the version bounds while changing what is
    installed, so the extra is asserted separately from the specifier.
    """
    assert _declared_mcp_requirement().extras == {"cli"}


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
