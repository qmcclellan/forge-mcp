"""Argument parser for the forge-mcp CLI."""

from __future__ import annotations

import argparse

from . import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="forge-mcp",
        description="Read-only MCP server for Forge repository knowledge.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"forge-mcp {__version__}",
    )
    parser.add_argument(
        "--forge-root",
        metavar="PATH",
        default=None,
        help=(
            "Forge repository root path. "
            "Sets FORGE_REPOSITORY_ROOT for this invocation. "
            "Required if FORGE_REPOSITORY_ROOT is not set in the environment."
        ),
    )
    return parser
