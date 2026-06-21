# forge-mcp v0.1.0 Tool Contract

All tools are read-only. No write tools exist.

## `get_forge_overview`

Returns Forge version, description, CLI entry point, major capabilities, available templates, CLI commands, template variables, project metadata path, and available documents.

No parameters.

## `list_templates`

Returns `{templates: [{name, language, runtime, description, tags}], count: int}`.

Sorted alphabetically. No parameters.

## `get_template_summary`

**Parameters:** `template: str` — template name (e.g. `python-worker`)

Returns `{name, language, runtime, description, tags, recommended_use, required_files, optional_artifacts, template_variables, smoke_test_command, all_template_files, generated_output_structure}`.

Errors: `TEMPLATE_NOT_FOUND`, `FORGE_ERROR`, `PATH_VIOLATION`.

## `list_template_files`

**Parameters:** `template: str`

Returns `{template, files: [str], count: int}`. File paths are sorted. Bounded to 200 entries.

## `read_template_file`

**Parameters:** `template: str`, `rel_path: str`

Reads one text file inside a template. Rejects binary, oversized, symlinks, traversal, absolute paths.

Returns `{template, path, content: str}`.

Errors: `PATH_VIOLATION`, `FORGE_ERROR`.

## `get_project_structure`

Returns descriptions of common conventions and per-template generated output layouts, rendering conventions, and output lane notes.

No parameters.

## `get_validation_commands`

Returns `{executed: false, note: str, commands: [{purpose, command, working_directory}]}`.

`executed` is always `false`. Commands are never run by forge-mcp.

No parameters.

## `read_forge_document`

**Parameters:** `document_id: str`

Approved identifiers: `readme`, `runbook`, `architecture`, `artifact-publishing`, `template-registry-runbook`, `interview-talk-track`, `forge-yaml-example`.

Returns `{document_id, path, content: str}`.

Errors: `DOCUMENT_ERROR`.

## `explain_forge_doctor`

Returns description, usage, checks dict, required/optional check lists, overall success rule, output formats, and source reference.

No parameters.

## `get_template_change_checklist`

Returns description, source references, required metadata fields, and numbered checklist steps.

No parameters.

---

## Error schema

All errors return: `{"error": {"code": "ERROR_CODE", "message": "..."}}`

## Tool count guarantee

Exactly 10 tools in v0.1.0. Verified by `tests/test_tool_contract.py`.
