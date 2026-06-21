"""Command-line entry point for forge-mcp.

Validates the Forge repository root at startup before accepting MCP connections.
"""

from __future__ import annotations

import os
import sys

from .cli import build_parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.forge_root is not None:
        os.environ["FORGE_REPOSITORY_ROOT"] = args.forge_root

    from .config import get_forge_root

    try:
        get_forge_root()
    except Exception as exc:
        print(f"forge-mcp: startup error: {exc}", file=sys.stderr)
        sys.exit(1)

    from .server import mcp

    mcp.run()


if __name__ == "__main__":
    main()
