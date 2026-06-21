# forge-mcp

Read-only MCP server that gives Claude Code structured knowledge about the Forge repository, including its templates, project structure, documentation, validation rules, doctor checks, and generated-project conventions.

Forge remains the authoritative application. forge-mcp reads Forge; it does not modify it.

## v0.1.1 has no write tools.

## Tools

| Tool | Purpose |
|---|---|
| `get_forge_overview` | Forge version, CLI entry point, capabilities, templates, doc availability |
| `list_templates` | Available local templates with metadata |
| `get_template_summary` | One template: purpose, language, files, variables, output structure |
| `list_template_files` | Sorted file listing for one template |
| `read_template_file` | Read a text file inside a template |
| `get_project_structure` | Generated-project conventions per template type |
| `get_validation_commands` | Validation commands as inert strings (never executed) |
| `read_forge_document` | Read approved Forge docs by stable identifier |
| `explain_forge_doctor` | Doctor checks, required/optional, overall success rule |
| `get_template_change_checklist` | Source-backed process for changing a Forge template |

## Requirements

- Python 3.10+
- Forge repository at a known path
- `FORGE_REPOSITORY_ROOT` environment variable or `--forge-root` CLI argument

## Installation

```bash
cd forge-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

```bash
# Set the Forge root and run the server over stdio
FORGE_REPOSITORY_ROOT=/srv/workspaces/projects/portfolio/forge forge-mcp

# Or pass it explicitly
forge-mcp --forge-root /srv/workspaces/projects/portfolio/forge

# Version check
forge-mcp --version
python -m forge_mcp --version
```

## Claude Code setup

See `docs/claude-code-setup.md` and `examples/claude-code.mcp.json`.

## Development

```bash
python -m pytest -q
python -m ruff check src/ tests/
```

## Document availability

`get_forge_overview` distinguishes between documents that are approved in the allowlist and documents that are currently present on disk:

- `available_documents` — approved identifiers whose files exist in the Forge repository right now
- `unavailable_documents` — approved identifiers configured in the allowlist but whose files are absent

Both fields are always present. Both are sorted alphabetically by identifier. The union of the two sets always equals the full approved-document allowlist.

`read_forge_document` accepts only approved identifiers. It returns a structured error with code `DOCUMENT_NOT_FOUND` when the identifier is unknown or the file is absent, and `DOCUMENT_ERROR` for other read failures (binary content, size limit, encoding). It never accepts arbitrary paths.

## Security

forge-mcp is strictly read-only. See `docs/security-boundary.md`.

## Separation

Forge is a separate repository and application. forge-mcp does not modify Forge.
forge-mcp does not import Forge modules, execute Forge commands, or touch Forge's Git history.
