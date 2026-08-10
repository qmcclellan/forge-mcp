"""Forge knowledge layer: converts repository data into structured MCP responses.

Static mappings in this module are derived from and traceable to Forge source:
- forge/doctor.py     → _DOCTOR_CHECKS
- forge/cli.py        → _FORGE_CLI_COMMANDS, _TEMPLATE_VARIABLES, _OUTPUT_LANE_NOTES
- forge/renderer.py   → _RENDERING_CONVENTIONS
- forge/template_artifacts.py → _REQUIRED_METADATA_FIELDS, _TEMPLATE_CHANGE_CHECKLIST
- templates/*/template.json   → per-template optional artifact notes
"""

from __future__ import annotations

from typing import Any

from .errors import ForgeMCPError
from .paths import APPROVED_DOCUMENTS
from .repository import ForgeRepository

# Traceable to forge/cli.py::create_project() and forge/renderer.py::render_template_dir()
_TEMPLATE_VARIABLES: dict[str, str] = {
    "project_name": "Human-readable display name (positional 'name' argument to forge new)",
    "project_slug": (
        "Machine identity: the generated directory and package base. Defaults to a "
        "kebab-case slug derived from project_name (lowercase, hyphens), and is "
        "overridden by an explicit --slug"
    ),
    "package_name": "Python/Java package identifier derived from project_slug (underscores replace hyphens)",
    "description": "Project description (--description flag; default: 'A generated Forge project.')",
}

# Traceable to forge/cli.py::optional_files set and renderer optional-file filtering
_OPTIONAL_ARTIFACT_FLAGS: dict[str, str] = {
    "Dockerfile.tmpl": "included when --with-docker flag is passed to forge new",
    "docker-compose.yml.tmpl": "included when --with-docker flag is passed to forge new",
    "Jenkinsfile.tmpl": "included when --with-jenkins flag is passed to forge new",
}

# Traceable to forge/cli.py::build_parser()
_FORGE_CLI_COMMANDS: dict[str, str] = {
    "forge doctor": "Check local prerequisites (Python, git, docker, cwd, templates, nexus)",
    "forge doctor --json": "Same as above with JSON output",
    "forge new <name> --template <t>": "Create a new project from a local or Nexus template",
    "forge project inspect <path>": "Inspect a generated project for Forge receipts and files",
    "forge template validate <name>": "Validate template structure and smoke-render a project",
    "forge template validate <name> --skip-smoke": "Validate template structure only",
    "forge template package <name> --version <v>": "Package a template as a versioned .tar.gz artifact",
    "forge template publish <name> --version <v>": "Publish a packaged template to Nexus raw-hosted",
    "forge template pull <name> --version <v>": "Pull and verify a template from Nexus",
    "forge template list": "List Forge templates from Nexus",
    "forge template info <name> --version <v>": "Show detailed template info from Nexus",
}

# Traceable to forge/doctor.py::run_doctor()
_DOCTOR_CHECKS: dict[str, dict[str, Any]] = {
    "python": {
        "required": True,
        "description": "Python >= 3.10 must be the active interpreter",
        "fail_status": "fail",
        "source": "forge/doctor.py: sys.version_info >= (3, 10)",
    },
    "git": {
        "required": True,
        "description": "git must be on PATH (shutil.which('git'))",
        "fail_status": "fail",
        "source": "forge/doctor.py: shutil.which('git')",
    },
    "docker": {
        "required": False,
        "description": "docker must be on PATH (optional; needed only for --with-docker workflows)",
        "fail_status": "warn",
        "source": "forge/doctor.py: shutil.which('docker'), required=False",
    },
    "cwd_writable": {
        "required": True,
        "description": "Current working directory must be writable (os.access(cwd, os.W_OK))",
        "fail_status": "fail",
        "source": "forge/doctor.py: os.access(cwd, os.W_OK)",
    },
    "templates": {
        "required": True,
        "description": "Forge templates/ directory must exist relative to the forge package root",
        "fail_status": "fail",
        "source": "forge/doctor.py: templates_dir.exists() and templates_dir.is_dir()",
    },
    "nexus": {
        "required": False,
        "description": "Always reported as 'skip' in current Forge version; not yet configurable via doctor",
        "fail_status": "skip",
        "source": "forge/doctor.py: status='skip', required=False",
    },
}

# Traceable to forge/cli.py::DEFAULT_TEMPLATE_OUTPUT_DIRS (lane structure, not absolute paths)
_OUTPUT_LANE_NOTES: dict[str, str] = {
    "python-worker": "DEFAULT_PROJECT_ROOT/backend/python/<project_slug>/",
    "java-spring-service": "DEFAULT_PROJECT_ROOT/backend/java/<project_slug>/",
    "node-dashboard": "DEFAULT_PROJECT_ROOT/frontend/node/<project_slug>/",
    "_default_fallback": "DEFAULT_PROJECT_ROOT/scratch/<project_slug>/",
}

# Traceable to forge/renderer.py::render_template_dir()
_RENDERING_CONVENTIONS: dict[str, str] = {
    "variable_syntax": "{{ variable_name }} — double curly braces with spaces",
    "directory_substitution": "__package__ directory is renamed to the package_name value",
    "file_suffix_stripping": ".tmpl suffix is stripped from all rendered output files",
    "optional_file_control": "Dockerfile.tmpl, docker-compose.yml.tmpl, Jenkinsfile.tmpl excluded unless flag passed",
}

# Traceable to forge/template_artifacts.py::REQUIRED_TEMPLATE_METADATA_FIELDS
_REQUIRED_METADATA_FIELDS: list[str] = [
    "name",
    "language",
    "runtime",
    "description",
    "tags",
    "recommended_use",
]

# Traceable to forge/template_artifacts.py::validate_template_structure()
# and forge/cli.py::template validate subcommand
_TEMPLATE_CHANGE_CHECKLIST: list[str] = [
    "1. Edit template files in templates/<name>/ within the Forge repository",
    "2. Ensure template.json has all required fields: name, language, runtime, description, tags, recommended_use",
    "3. Ensure required_files list in template.json names every file that must be present",
    "4. Ensure optional_files list names Dockerfile.tmpl, docker-compose.yml.tmpl, Jenkinsfile.tmpl as applicable",
    "5. Run: forge template validate <name> --skip-smoke  (structure check only, fast)",
    "6. Run: forge template validate <name>  (structure check + smoke render + smoke_test_command)",
    "7. Run: python -m pytest  (full Forge test suite from Forge root)",
    "8. Update template.json description, tags, and recommended_use if template purpose changed",
    "9. Update Forge README.md and docs/runbook.md if adding a new template or changing behavior",
    "10. Package for publishing: forge template package <name> --version <version>",
    "11. Publish to Nexus if configured: forge template publish <name> --version <version>",
]

# Per-language generated project structure (traceable to template files and forge/renderer.py)
_LANGUAGE_OUTPUT_STRUCTURE: dict[str, dict[str, str]] = {
    "python": {
        "README.md": "Generated project README",
        "pyproject.toml": "Python project config with src/ layout and dev extras",
        ".gitignore": "Generated .gitignore",
        "src/<package_name>/__init__.py": "Package init",
        "src/<package_name>/main.py": "Main entry point",
        "tests/test_smoke.py": "Pytest smoke test",
        "docs/runbook.md": "Generated runbook",
        "docs/interview-talk-track.md": "Interview/demo talk track",
    },
    "java": {
        "README.md": "Generated project README",
        "pom.xml": "Maven build file",
        "src/main/java/com/example/<package_name>/Application.java": "Spring application class",
        "src/test/java/com/example/<package_name>/ApplicationSmokeTest.java": "Smoke test",
        ".mvn/maven.config": "Maven config (Nexus mirror reference)",
        ".mvn/settings.xml": "Maven settings with Nexus mirror",
    },
    "node": {
        "README.md": "Generated project README",
        "package.json": "npm package config",
        "index.html": "Entry HTML",
        "src/App.jsx": "Root React component",
        "src/main.jsx": "Vite entry point",
        "src/styles.css": "Stylesheet",
        ".npmrc": "npm config (Nexus npm-public registry)",
    },
}

# Traceable to forge/project_metadata.py::write_project_metadata() and RECEIPT_VERSION
_COMMON_OUTPUT_FILES: dict[str, str] = {
    ".forge/project.json": (
        "Forge metadata receipt, version 2. Fields: receipt_version, project_name, "
        "project_slug, template_name, created_at (UTC ISO 8601 Z), forge_version, "
        "docker_enabled, jenkins_enabled, git_initialized, remote_configured. "
        "Identity semantics are versioned: in a version-2 receipt project_name is "
        "the human-readable display name and project_slug is the machine identity. "
        "Historical receipts have no receipt_version key and store the derived slug "
        "in project_name, because the two were not separable when they were "
        "written; they are valid artifacts and are not migrated. Branch on "
        "receipt_version rather than guessing"
    ),
    "Dockerfile (optional)": "Included when forge new --with-docker is used",
    "docker-compose.yml (optional)": "Included when forge new --with-docker is used",
    "Jenkinsfile (optional)": "Included when forge new --with-jenkins is used",
}


class ForgeKnowledge:
    """Structured knowledge layer over a ForgeRepository."""

    def __init__(self, repo: ForgeRepository) -> None:
        self._repo = repo

    # ------------------------------------------------------------------
    # Overview
    # ------------------------------------------------------------------

    def get_overview(self) -> dict[str, Any]:
        version = self._repo.read_forge_version()
        templates = self._repo.list_template_names()
        available_docs = {
            doc_id: rel_path
            for doc_id, rel_path in sorted(APPROVED_DOCUMENTS.items())
            if self._repo.document_exists(doc_id)
        }
        unavailable_docs = {
            doc_id: rel_path
            for doc_id, rel_path in sorted(APPROVED_DOCUMENTS.items())
            if not self._repo.document_exists(doc_id)
        }
        return {
            "forge_version": version,
            "description": (
                "CLI-first developer-platform tool for creating standardized project lanes "
                "with test scaffolding, documentation, Docker/Jenkins readiness, metadata "
                "receipts, local environment checks, and project inspection."
            ),
            "cli_entry_point": "forge = forge.cli:main",
            "major_capabilities": [
                "Project scaffolding from templates (forge new)",
                "Local template management (forge template validate/package)",
                "Nexus-backed template registry (forge template publish/pull/list/info)",
                "Local environment validation (forge doctor)",
                "Generated project inspection (forge project inspect)",
            ],
            "templates": templates,
            "cli_commands": _FORGE_CLI_COMMANDS,
            "template_variables": _TEMPLATE_VARIABLES,
            "project_metadata_path": ".forge/project.json",
            "available_documents": available_docs,
            "unavailable_documents": unavailable_docs,
        }

    # ------------------------------------------------------------------
    # Templates
    # ------------------------------------------------------------------

    def list_templates(self) -> dict[str, Any]:
        names = self._repo.list_template_names()
        templates = []
        for name in names:
            try:
                meta = self._repo.get_template_metadata(name)
                templates.append(
                    {
                        "name": name,
                        "language": meta.get("language", "unknown"),
                        "runtime": meta.get("runtime", "unknown"),
                        "description": meta.get("description", ""),
                        "tags": meta.get("tags") or [],
                    }
                )
            except ForgeMCPError as exc:
                templates.append({"name": name, "error": str(exc)})
        return {"templates": templates, "count": len(templates)}

    def get_template_summary(self, template: str) -> dict[str, Any]:
        meta = self._repo.get_template_metadata(template)
        files = self._repo.list_template_files(template)
        language = meta.get("language", "unknown")
        optional_files_raw: list[str] = meta.get("optional_files") or []
        optional_artifact_notes = {
            f: _OPTIONAL_ARTIFACT_FLAGS.get(f, "optional artifact")
            for f in optional_files_raw
        }
        output_structure = dict(_COMMON_OUTPUT_FILES)
        output_structure.update(_LANGUAGE_OUTPUT_STRUCTURE.get(language, {}))
        return {
            "name": template,
            "language": language,
            "runtime": meta.get("runtime", "unknown"),
            "description": meta.get("description", ""),
            "tags": meta.get("tags") or [],
            "recommended_use": meta.get("recommended_use", ""),
            "required_files": meta.get("required_files") or [],
            "optional_artifacts": optional_artifact_notes,
            "template_variables": _TEMPLATE_VARIABLES,
            "smoke_test_command": meta.get("smoke_test_command"),
            "all_template_files": files,
            "generated_output_structure": output_structure,
        }

    def list_template_files(self, template: str) -> dict[str, Any]:
        files = self._repo.list_template_files(template)
        return {"template": template, "files": files, "count": len(files)}

    def read_template_file(self, template: str, rel_path: str) -> dict[str, Any]:
        content = self._repo.read_template_file(template, rel_path)
        return {"template": template, "path": rel_path, "content": content}

    # ------------------------------------------------------------------
    # Project structure
    # ------------------------------------------------------------------

    def get_project_structure(self) -> dict[str, Any]:
        names = self._repo.list_template_names()
        template_summaries: dict[str, Any] = {}
        for name in names:
            try:
                meta = self._repo.get_template_metadata(name)
                language = meta.get("language", "unknown")
                template_summaries[name] = {
                    "language": language,
                    "runtime": meta.get("runtime", "unknown"),
                    "description": meta.get("description", ""),
                    "output_structure": dict(
                        _LANGUAGE_OUTPUT_STRUCTURE.get(language, {})
                    ),
                }
            except ForgeMCPError:
                template_summaries[name] = {"language": "unknown"}
        return {
            "description": "Conventions for all Forge-generated projects.",
            "common_to_all_templates": _COMMON_OUTPUT_FILES,
            "rendering_conventions": _RENDERING_CONVENTIONS,
            "template_output_lanes": {
                "note": (
                    "Default output lanes from forge.cli:DEFAULT_TEMPLATE_OUTPUT_DIRS. "
                    "Override per-project with forge new --output-dir <path>."
                ),
                **_OUTPUT_LANE_NOTES,
            },
            "templates": template_summaries,
        }

    # ------------------------------------------------------------------
    # Validation commands (inert — never executed)
    # ------------------------------------------------------------------

    def get_validation_commands(self) -> dict[str, Any]:
        return {
            "executed": False,
            "note": "These are documentation strings only. forge-mcp never executes commands.",
            "commands": [
                {
                    "purpose": "Run the full Forge test suite",
                    "command": "python -m pytest",
                    "working_directory": "<forge-root>",
                },
                {
                    "purpose": "Validate template structure and smoke-render (recommended before publish)",
                    "command": "forge template validate <template>",
                    "working_directory": "<forge-root>",
                },
                {
                    "purpose": "Validate template structure only (faster, skips render)",
                    "command": "forge template validate <template> --skip-smoke",
                    "working_directory": "<forge-root>",
                },
                {
                    "purpose": "Package a template as a versioned artifact",
                    "command": "forge template package <template> --version <version>",
                    "working_directory": "<forge-root>",
                },
                {
                    "purpose": "Check local Forge prerequisites",
                    "command": "forge doctor",
                    "working_directory": "<any>",
                },
                {
                    "purpose": "Check prerequisites with JSON output",
                    "command": "forge doctor --json",
                    "working_directory": "<any>",
                },
            ],
        }

    # ------------------------------------------------------------------
    # Documents
    # ------------------------------------------------------------------

    def read_forge_document(self, doc_id: str) -> dict[str, Any]:
        content = self._repo.read_approved_document(doc_id)
        return {
            "document_id": doc_id,
            "path": APPROVED_DOCUMENTS.get(doc_id, ""),
            "content": content,
        }

    # ------------------------------------------------------------------
    # Doctor
    # ------------------------------------------------------------------

    def explain_doctor(self) -> dict[str, Any]:
        required = sorted(k for k, v in _DOCTOR_CHECKS.items() if v["required"])
        optional = sorted(k for k, v in _DOCTOR_CHECKS.items() if not v["required"])
        return {
            "description": (
                "forge doctor checks local development prerequisites required "
                "to run Forge successfully."
            ),
            "usage": "forge doctor  OR  forge doctor --json",
            "checks": _DOCTOR_CHECKS,
            "required_checks": required,
            "optional_checks": optional,
            "overall_success_rule": (
                "All checks with required=True must report status='ok'. "
                "Optional checks (required=False) that fail produce 'warn' or 'skip' "
                "and do not affect overall success."
            ),
            "output_formats": {
                "text": "forge doctor  — human-readable lines: [status] check_name: detail",
                "json": "forge doctor --json  — {ok: bool, checks: {name: {status, required, detail}}}",
            },
            "source": "forge/doctor.py :: run_doctor()",
        }

    # ------------------------------------------------------------------
    # Template change checklist
    # ------------------------------------------------------------------

    def get_template_change_checklist(self) -> dict[str, Any]:
        return {
            "description": "Source-backed process for safely adding or changing a Forge template.",
            "source_references": [
                "forge/template_artifacts.py :: validate_template_structure()",
                "forge/template_artifacts.py :: REQUIRED_TEMPLATE_METADATA_FIELDS",
                "forge/cli.py :: template validate subcommand",
                "forge/renderer.py :: render_template_dir()",
                "templates/<name>/template.json",
            ],
            "required_metadata_fields": _REQUIRED_METADATA_FIELDS,
            "checklist": _TEMPLATE_CHANGE_CHECKLIST,
        }
