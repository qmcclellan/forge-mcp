"""Tests for ForgeRepository using the public-safe fixture."""

from __future__ import annotations

from pathlib import Path

import pytest

from forge_mcp.errors import DocumentNotFoundError, PathViolationError, TemplateNotFoundError
from forge_mcp.repository import ForgeRepository


@pytest.fixture
def repo(forge_fixture_root: Path) -> ForgeRepository:
    return ForgeRepository(forge_fixture_root)


# ---------------------------------------------------------------------------
# Repository metadata
# ---------------------------------------------------------------------------


def test_read_forge_version(repo):
    version = repo.read_forge_version()
    assert version == "0.9.9-test"


def test_root_property(repo, forge_fixture_root):
    assert repo.root == forge_fixture_root


# ---------------------------------------------------------------------------
# Template discovery
# ---------------------------------------------------------------------------


def test_list_template_names(repo):
    names = repo.list_template_names()
    assert isinstance(names, list)
    assert "sample-worker" in names


def test_list_template_names_sorted(repo):
    names = repo.list_template_names()
    assert names == sorted(names)


def test_get_template_metadata(repo):
    meta = repo.get_template_metadata("sample-worker")
    assert meta["name"] == "sample-worker"
    assert meta["language"] == "python"
    assert meta["runtime"] == "python-3.12"
    assert isinstance(meta["tags"], list)


def test_get_template_metadata_unknown_raises(repo):
    with pytest.raises(TemplateNotFoundError):
        repo.get_template_metadata("does-not-exist")


def test_get_template_metadata_invalid_slug_raises(repo):
    with pytest.raises(PathViolationError):
        repo.get_template_metadata("../evil")


def test_list_template_files(repo):
    files = repo.list_template_files("sample-worker")
    assert isinstance(files, list)
    assert len(files) >= 1
    assert "template.json" in files
    assert "README.md.tmpl" in files


def test_list_template_files_sorted(repo):
    files = repo.list_template_files("sample-worker")
    assert files == sorted(files)


def test_list_template_files_unknown_raises(repo):
    with pytest.raises(TemplateNotFoundError):
        repo.list_template_files("does-not-exist")


def test_read_template_file(repo):
    content = repo.read_template_file("sample-worker", "README.md.tmpl")
    assert "project_name" in content or "{{ project_name }}" in content


def test_read_template_file_unknown_template_raises(repo):
    with pytest.raises((TemplateNotFoundError, PathViolationError)):
        repo.read_template_file("does-not-exist", "README.md.tmpl")


def test_read_template_file_traversal_rejected(repo):
    with pytest.raises(PathViolationError):
        repo.read_template_file("sample-worker", "../README.md")


def test_read_template_file_absolute_rejected(repo):
    with pytest.raises(PathViolationError):
        repo.read_template_file("sample-worker", "/etc/passwd")


# ---------------------------------------------------------------------------
# Approved documents
# ---------------------------------------------------------------------------


def test_list_approved_document_ids(repo):
    ids = repo.list_approved_document_ids()
    assert "readme" in ids
    assert "runbook" in ids


def test_list_approved_document_ids_sorted(repo):
    ids = repo.list_approved_document_ids()
    assert ids == sorted(ids)


def test_read_approved_document_readme(repo):
    content = repo.read_approved_document("readme")
    assert isinstance(content, str)
    assert len(content) > 0


def test_read_approved_document_runbook(repo):
    content = repo.read_approved_document("runbook")
    assert isinstance(content, str)


def test_read_approved_document_unknown_raises(repo):
    with pytest.raises(DocumentNotFoundError, match="Unknown"):
        repo.read_approved_document("not-a-real-doc")


def test_read_approved_document_traversal_not_possible(repo):
    with pytest.raises(DocumentNotFoundError):
        repo.read_approved_document("../etc/passwd")


def test_document_exists_readme(repo):
    assert repo.document_exists("readme") is True


def test_document_exists_unknown(repo):
    assert repo.document_exists("definitely-not-real") is False
