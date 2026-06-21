# forge-mcp Security Boundary

## v0.1.0 is strictly read-only.

## Forge / forge-mcp separation

- Forge is the authoritative application at a separately configured repository path.
- forge-mcp reads Forge through one explicitly configured root.
- forge-mcp does not import Forge modules.
- forge-mcp does not execute Forge commands or any other shell commands.
- forge-mcp does not modify templates, documentation, or Git state.
- forge-mcp does not initialize repositories or create projects.
- forge-mcp does not perform network requests during normal tool use.
- forge-mcp does not access Nexus.

## Forge root configuration

- `FORGE_REPOSITORY_ROOT` environment variable or `--forge-root` CLI argument.
- Fails closed: raises an error at startup if the variable is unset, the path is missing, or the path does not contain `forge/cli.py` and `templates/` (required sentinels).
- Never falls back to the current working directory.
- The root is resolved once at startup and validated before the MCP server accepts connections.

## Path confinement

Every file read resolves through `safe_join()`, which verifies the resolved path remains under its designated sub-root (templates root or Forge root). The checks applied to every user-controlled path or file:

- Reject absolute paths
- Reject `..` traversal components
- Reject NUL bytes (`\x00`)
- Reject invalid template identifiers (must match `^[a-z][a-z0-9-]{0,63}$`)
- Reject symlinks (both in `list_template_files` and `check_readable_file`)
- Catch symlink escape: `safe_join` resolves through symlinks; if the final path is outside the root, it raises `PathViolationError`
- Reject binary files (NUL bytes in first 8 KB)
- Reject non-UTF-8 files
- Reject files larger than 64 KB

## Approved document identifiers

`read_forge_document` only accepts the following stable identifiers. Arbitrary file paths are not accepted.

- `readme` → `README.md`
- `runbook` → `docs/runbook.md`
- `architecture` → `docs/architecture.md`
- `artifact-publishing` → `docs/artifact-publishing.md`
- `template-registry-runbook` → `docs/template-registry-runbook.md`
- `interview-talk-track` → `docs/interview-talk-track.md`
- `forge-yaml-example` → `examples/forge.yaml`

## Bounded output

- Per-file read limit: 64 KB
- File list entry limit: 200 entries
- Response size guard: 256 KB

## What is never exposed

- `.git/` directory contents
- Environment variables or credentials
- Nexus passwords
- Host filesystem paths beyond the Forge root
- Generated-project directories (v0.1.0)
- Forge's `.venv/`, `dist/`, `__pycache__/`

## Error handling

All errors return structured safe dicts: `{"error": {"code": "...", "message": "..."}}`. Messages avoid leaking absolute host paths.

## No subprocess execution

forge-mcp does not call `subprocess`, `os.system`, `os.popen`, or any other shell execution mechanism. The `get_validation_commands` tool returns inert documentation strings with an explicit `"executed": false` field.
