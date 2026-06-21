# Claude Code Setup for forge-mcp

## 1. Install forge-mcp

```bash
cd /srv/workspaces/projects/portfolio/forge-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 2. Verify the install

```bash
forge-mcp --version
# forge-mcp 0.1.0
```

## 3. Configure Claude Code

Add forge-mcp to your Claude Code MCP configuration. See `examples/claude-code.mcp.json` for the template.

In your Claude Code settings (or `.claude/mcp.json`):

```json
{
  "mcpServers": {
    "forge-mcp": {
      "command": "/srv/workspaces/projects/portfolio/forge-mcp/.venv/bin/forge-mcp",
      "args": [],
      "env": {
        "FORGE_REPOSITORY_ROOT": "/srv/workspaces/projects/portfolio/forge"
      }
    }
  }
}
```

Or pass the root via `--forge-root`:

```json
{
  "mcpServers": {
    "forge-mcp": {
      "command": "/srv/workspaces/projects/portfolio/forge-mcp/.venv/bin/forge-mcp",
      "args": ["--forge-root", "/srv/workspaces/projects/portfolio/forge"]
    }
  }
}
```

## 4. Verify the server starts

```bash
FORGE_REPOSITORY_ROOT=/srv/workspaces/projects/portfolio/forge \
  forge-mcp --forge-root /srv/workspaces/projects/portfolio/forge
# Should hang waiting for MCP input — Ctrl-C to stop
```

If it exits immediately with an error, check that `FORGE_REPOSITORY_ROOT` points to a valid Forge repository.

## Troubleshooting

**`startup error: FORGE_REPOSITORY_ROOT is not set`** — set the env var or pass `--forge-root`.

**`Path does not appear to be a Forge repository`** — the path must contain `forge/cli.py` and `templates/`.

**`File not found`** — a document you requested does not exist in the configured Forge root. Some approved documents are optional.
