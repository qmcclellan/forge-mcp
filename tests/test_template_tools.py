"""Tests for template-related MCP tool handlers using the fixture."""

from __future__ import annotations

from pathlib import Path

import pytest

from forge_mcp.repository import ForgeRepository
from forge_mcp.services import ForgeKnowledge


@pytest.fixture
def knowledge(forge_fixture_root: Path) -> ForgeKnowledge:
    return ForgeKnowledge(ForgeRepository(forge_fixture_root))


# ---------------------------------------------------------------------------
# list_templates
# ---------------------------------------------------------------------------


def test_list_templates_returns_list(knowledge):
    result = knowledge.list_templates()
    assert "templates" in result
    assert "count" in result
    assert isinstance(result["templates"], list)


def test_list_templates_includes_sample_worker(knowledge):
    result = knowledge.list_templates()
    names = [t["name"] for t in result["templates"]]
    assert "sample-worker" in names


def test_list_templates_has_metadata_fields(knowledge):
    result = knowledge.list_templates()
    t = result["templates"][0]
    assert "name" in t
    assert "language" in t
    assert "runtime" in t
    assert "description" in t


def test_list_templates_count_matches(knowledge):
    result = knowledge.list_templates()
    assert result["count"] == len(result["templates"])


def test_list_templates_alphabetical(knowledge):
    result = knowledge.list_templates()
    names = [t["name"] for t in result["templates"]]
    assert names == sorted(names)


# ---------------------------------------------------------------------------
# get_template_summary
# ---------------------------------------------------------------------------


def test_get_template_summary_fields(knowledge):
    result = knowledge.get_template_summary("sample-worker")
    assert result["name"] == "sample-worker"
    assert result["language"] == "python"
    assert "required_files" in result
    assert "optional_artifacts" in result
    assert "template_variables" in result
    assert "all_template_files" in result
    assert "generated_output_structure" in result


def test_get_template_summary_variables_present(knowledge):
    result = knowledge.get_template_summary("sample-worker")
    variables = result["template_variables"]
    assert "project_name" in variables
    assert "project_slug" in variables
    assert "package_name" in variables
    assert "description" in variables


def test_get_template_summary_all_files_sorted(knowledge):
    result = knowledge.get_template_summary("sample-worker")
    files = result["all_template_files"]
    assert files == sorted(files)


# ---------------------------------------------------------------------------
# list_template_files
# ---------------------------------------------------------------------------


def test_list_template_files_sorted(knowledge):
    result = knowledge.list_template_files("sample-worker")
    assert result["files"] == sorted(result["files"])


def test_list_template_files_count(knowledge):
    result = knowledge.list_template_files("sample-worker")
    assert result["count"] == len(result["files"])


def test_list_template_files_includes_template_json(knowledge):
    result = knowledge.list_template_files("sample-worker")
    assert "template.json" in result["files"]


# ---------------------------------------------------------------------------
# read_template_file
# ---------------------------------------------------------------------------


def test_read_template_file_readme(knowledge):
    result = knowledge.read_template_file("sample-worker", "README.md.tmpl")
    assert "template" in result
    assert "path" in result
    assert "content" in result
    assert isinstance(result["content"], str)


def test_read_template_file_template_json(knowledge):
    result = knowledge.read_template_file("sample-worker", "template.json")
    assert result["path"] == "template.json"
    assert "sample-worker" in result["content"]


# --- KS-0019: the documented receipt and identity variables must match Forge ---
# forge-mcp is a read-only knowledge interface and is NEVER authoritative over
# Forge: if it disagrees with Forge source, Forge wins. These pin the two
# descriptions that drifted when Forge's receipt gained versioned identity
# fields (forge/project_metadata.py, RECEIPT_VERSION = 2).

_RECEIPT_V2_FIELDS = (
    "receipt_version",
    "project_name",
    "project_slug",
    "template_name",
    "created_at",
    "forge_version",
    "docker_enabled",
    "jenkins_enabled",
    "git_initialized",
    "remote_configured",
)


def test_receipt_description_lists_every_version_2_field(knowledge):
    """The documented field list must not omit the versioned identity fields."""
    described = knowledge.get_project_structure()["common_to_all_templates"][
        ".forge/project.json"
    ]

    missing = [field for field in _RECEIPT_V2_FIELDS if field not in described]
    assert not missing, f"receipt description omits: {missing}"


def test_receipt_description_explains_versioned_identity(knowledge):
    """Consumers must be told to branch on receipt_version, not guess.

    A field list alone is not enough: an unversioned historical receipt stores
    the derived slug in project_name, so a consumer that assumes project_name is
    always a display name reads the wrong value.
    """
    described = knowledge.get_project_structure()["common_to_all_templates"][
        ".forge/project.json"
    ]

    assert "version 2" in described
    assert "receipt_version" in described
    assert "not migrated" in described


def test_template_summary_reports_the_same_receipt_description(knowledge):
    """Both surfaces that expose the receipt must agree."""
    summary = knowledge.get_template_summary("sample-worker")
    structure = knowledge.get_project_structure()

    assert (
        summary["generated_output_structure"][".forge/project.json"]
        == structure["common_to_all_templates"][".forge/project.json"]
    )


def test_identity_variable_descriptions_match_forge_semantics(knowledge):
    """project_name is positional and project_slug is overridable by --slug.

    Forge's `new` takes `name` positionally, and project_slug defaults to a slug
    derived from it unless an explicit --slug is supplied. Describing the name as
    a `--name` flag, or the slug as merely derived, misstates the CLI.
    """
    variables = knowledge.get_template_summary("sample-worker")["template_variables"]

    assert "--name" not in variables["project_name"]
    assert "positional" in variables["project_name"]
    assert "--slug" in variables["project_slug"]
