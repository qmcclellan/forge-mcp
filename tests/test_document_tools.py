"""Tests for document tool handlers and the approved-document allowlist."""

from __future__ import annotations

from pathlib import Path

import pytest

from forge_mcp.errors import DocumentNotFoundError
from forge_mcp.paths import APPROVED_DOCUMENTS
from forge_mcp.repository import ForgeRepository
from forge_mcp.services import ForgeKnowledge


@pytest.fixture
def knowledge(forge_fixture_root: Path) -> ForgeKnowledge:
    return ForgeKnowledge(ForgeRepository(forge_fixture_root))


# ---------------------------------------------------------------------------
# Approved document allowlist
# ---------------------------------------------------------------------------


def test_approved_document_ids_present():
    assert "readme" in APPROVED_DOCUMENTS
    assert "runbook" in APPROVED_DOCUMENTS
    assert "architecture" in APPROVED_DOCUMENTS
    assert "artifact-publishing" in APPROVED_DOCUMENTS
    assert "template-registry-runbook" in APPROVED_DOCUMENTS
    assert "interview-talk-track" in APPROVED_DOCUMENTS
    assert "forge-yaml-example" in APPROVED_DOCUMENTS


def test_approved_documents_no_traversal():
    for doc_id, rel_path in APPROVED_DOCUMENTS.items():
        p = Path(rel_path)
        assert not p.is_absolute(), f"{doc_id}: path must not be absolute"
        assert ".." not in p.parts, f"{doc_id}: path must not contain .."


def test_approved_documents_known_only():
    for doc_id in APPROVED_DOCUMENTS:
        assert doc_id.replace("-", "").isalnum(), f"{doc_id} contains unexpected chars"


# ---------------------------------------------------------------------------
# read_forge_document via knowledge layer
# ---------------------------------------------------------------------------


def test_read_readme(knowledge):
    result = knowledge.read_forge_document("readme")
    assert result["document_id"] == "readme"
    assert result["path"] == "README.md"
    assert isinstance(result["content"], str)
    assert len(result["content"]) > 0


def test_read_runbook(knowledge):
    result = knowledge.read_forge_document("runbook")
    assert result["document_id"] == "runbook"
    assert isinstance(result["content"], str)


def test_read_unknown_document_raises(knowledge):
    with pytest.raises(DocumentNotFoundError, match="Unknown"):
        knowledge.read_forge_document("definitely-not-a-real-doc")


def test_read_traversal_attempt_raises(knowledge):
    with pytest.raises(DocumentNotFoundError):
        knowledge.read_forge_document("../etc/passwd")


def test_read_absolute_path_not_in_allowlist(knowledge):
    with pytest.raises(DocumentNotFoundError):
        knowledge.read_forge_document("/absolute/path")


# ---------------------------------------------------------------------------
# explain_doctor (static knowledge, no file I/O)
# ---------------------------------------------------------------------------


def test_explain_doctor_has_checks(knowledge):
    result = knowledge.explain_doctor()
    assert "checks" in result
    checks = result["checks"]
    for name in ("python", "git", "docker", "cwd_writable", "templates", "nexus"):
        assert name in checks, f"Missing doctor check: {name}"


def test_explain_doctor_required_checks(knowledge):
    result = knowledge.explain_doctor()
    required = set(result["required_checks"])
    assert required == {"python", "git", "cwd_writable", "templates"}


def test_explain_doctor_optional_checks(knowledge):
    result = knowledge.explain_doctor()
    optional = set(result["optional_checks"])
    assert optional == {"docker", "nexus"}


def test_explain_doctor_executed_false(knowledge):
    result = knowledge.explain_doctor()
    assert "executed" not in result  # doctor itself has no executed flag — validation commands do


def test_explain_doctor_has_source(knowledge):
    result = knowledge.explain_doctor()
    assert "source" in result


# ---------------------------------------------------------------------------
# get_validation_commands (static, never executed)
# ---------------------------------------------------------------------------


def test_validation_commands_executed_false(knowledge):
    result = knowledge.get_validation_commands()
    assert result["executed"] is False


def test_validation_commands_contains_pytest(knowledge):
    result = knowledge.get_validation_commands()
    commands = [c["command"] for c in result["commands"]]
    assert any("pytest" in cmd for cmd in commands)


def test_validation_commands_contains_validate(knowledge):
    result = knowledge.get_validation_commands()
    commands = [c["command"] for c in result["commands"]]
    assert any("validate" in cmd for cmd in commands)


# ---------------------------------------------------------------------------
# get_template_change_checklist (static, source-backed)
# ---------------------------------------------------------------------------


def test_checklist_has_required_fields(knowledge):
    result = knowledge.get_template_change_checklist()
    assert "checklist" in result
    assert "required_metadata_fields" in result
    assert "source_references" in result


def test_checklist_includes_validation_step(knowledge):
    result = knowledge.get_template_change_checklist()
    checklist_text = " ".join(result["checklist"])
    assert "validate" in checklist_text.lower()
    assert "pytest" in checklist_text.lower()


def test_required_metadata_fields(knowledge):
    result = knowledge.get_template_change_checklist()
    fields = set(result["required_metadata_fields"])
    assert {"name", "language", "runtime", "description", "tags", "recommended_use"}.issubset(fields)
