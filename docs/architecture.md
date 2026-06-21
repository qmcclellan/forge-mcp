# forge-mcp Architecture

## Module responsibilities

| Module | Purpose |
|---|---|
| `__init__.py` | Package version (`__version__`) |
| `version.py` | Re-exports `__version__` for external callers |
| `__main__.py` | Entry point: parse args, validate root at startup, run MCP server |
| `cli.py` | `build_parser()` — argparse definition, separated for testability |
| `config.py` | `get_forge_root()` — reads `FORGE_REPOSITORY_ROOT`, validates, returns `Path` |
| `errors.py` | Exception hierarchy + `structured_error()` helper |
| `limits.py` | Size/count limits + regex constants |
| `models.py` | `TemplateMetadata` typed wrapper for `template.json` content |
| `paths.py` | Path safety: `safe_join`, `check_readable_file`, `validate_*`, `APPROVED_DOCUMENTS` |
| `repository.py` | `ForgeRepository` — all file I/O against the Forge root |
| `services.py` | `ForgeKnowledge` — static knowledge + structured MCP responses |
| `server.py` | FastMCP instance + 10 `@mcp.tool()` handlers |

## Data flow

```
Claude Code
  │
  └─► MCP (stdio)
        │
        └─► server.py :: @mcp.tool() handlers
              │
              └─► services.py :: ForgeKnowledge
                    │
                    ├─► repository.py :: ForgeRepository  (file I/O)
                    │       │
                    │       └─► paths.py  (safety checks for every read)
                    │
                    └─► static mappings  (traceable to Forge source)
```

## Startup validation

`main()` in `__main__.py`:
1. Parse `--forge-root` (sets env var if provided)
2. Call `get_forge_root()` — fails with exit code 1 if root is invalid
3. Import and run `mcp.run()` over stdio

This ensures forge-mcp never accepts MCP connections against an unconfigured or invalid Forge root.

## Separation from Forge

- forge-mcp reads from a configured Forge root path.
- forge-mcp does not import any Forge Python modules.
- forge-mcp does not execute forge CLI commands.
- Forge's source is treated as read-only documentation.
- Static mappings in `services.py` are derived from Forge source (traceable to specific files/functions) and covered by tests.

## Security layer

Every user-controlled value (template name, relative path, document ID) passes through `paths.py` before any file I/O. `ForgeRepository` never accepts raw user strings; it calls path validators first.
