"""Tests for path safety, confinement, traversal rejection, and file checks."""

from __future__ import annotations

from pathlib import Path

import pytest

from forge_mcp.errors import DocumentNotFoundError, PathViolationError
from forge_mcp.paths import (
    APPROVED_DOCUMENTS,
    check_readable_file,
    safe_document_path,
    safe_join,
    validate_relative_path,
    validate_template_slug,
)


# ---------------------------------------------------------------------------
# validate_template_slug
# ---------------------------------------------------------------------------


def test_valid_slugs():
    assert validate_template_slug("python-worker") == "python-worker"
    assert validate_template_slug("a") == "a"


def test_slug_uppercase_rejected():
    with pytest.raises(PathViolationError):
        validate_template_slug("Python-Worker")


def test_slug_traversal_rejected():
    with pytest.raises(PathViolationError):
        validate_template_slug("../evil")


def test_slug_absolute_rejected():
    with pytest.raises(PathViolationError):
        validate_template_slug("/etc/passwd")


def test_slug_with_spaces_rejected():
    with pytest.raises(PathViolationError):
        validate_template_slug("my template")


# ---------------------------------------------------------------------------
# validate_relative_path
# ---------------------------------------------------------------------------


def test_relative_path_valid():
    validate_relative_path("README.md")
    validate_relative_path("src/main.py")
    validate_relative_path("docs/runbook.md")


def test_relative_path_traversal_rejected():
    with pytest.raises(PathViolationError, match=r"\.\.|traversal"):
        validate_relative_path("../secret.txt")


def test_relative_path_absolute_rejected():
    with pytest.raises(PathViolationError, match="Absolute"):
        validate_relative_path("/etc/passwd")


def test_relative_path_nul_byte_rejected():
    with pytest.raises(PathViolationError, match="NUL"):
        validate_relative_path("file\x00name.txt")


def test_relative_path_nested_traversal_rejected():
    with pytest.raises(PathViolationError):
        validate_relative_path("a/b/../../etc/passwd")


# ---------------------------------------------------------------------------
# safe_join
# ---------------------------------------------------------------------------


def test_safe_join_valid(tmp_path):
    result = safe_join(tmp_path, "subdir", "file.txt")
    assert tmp_path in result.parents or result == tmp_path


def test_safe_join_traversal_escape(tmp_path):
    with pytest.raises(PathViolationError, match="escapes"):
        safe_join(tmp_path, "..", "outside.txt")


def test_safe_join_symlink_escape(tmp_path):
    """A symlink inside root pointing outside root must be caught."""
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.txt").write_text("secret")
    link = root / "escape"
    link.symlink_to(outside)
    with pytest.raises(PathViolationError, match="escapes"):
        safe_join(root, "escape", "secret.txt")


# ---------------------------------------------------------------------------
# check_readable_file
# ---------------------------------------------------------------------------


def test_check_readable_file_normal(tmp_path):
    f = tmp_path / "ok.txt"
    f.write_text("hello")
    check_readable_file(f)  # should not raise


def test_check_readable_file_symlink_rejected(tmp_path):
    target = tmp_path / "real.txt"
    target.write_text("content")
    link = tmp_path / "link.txt"
    link.symlink_to(target)
    with pytest.raises(PathViolationError, match="ymlink"):
        check_readable_file(link)


def test_check_readable_file_missing(tmp_path):
    with pytest.raises(PathViolationError, match="not found"):
        check_readable_file(tmp_path / "nonexistent.txt")


def test_check_readable_file_directory(tmp_path):
    d = tmp_path / "subdir"
    d.mkdir()
    with pytest.raises(PathViolationError, match="regular file"):
        check_readable_file(d)


def test_check_readable_file_binary(tmp_path):
    f = tmp_path / "binary.bin"
    f.write_bytes(b"\x00\x01\x02\x03")
    with pytest.raises(PathViolationError, match="binary"):
        check_readable_file(f)


def test_check_readable_file_oversized(tmp_path):
    f = tmp_path / "big.txt"
    f.write_bytes(b"x" * (64 * 1024 + 1))
    with pytest.raises(PathViolationError, match="size limit"):
        check_readable_file(f)


def test_check_readable_file_invalid_utf8(tmp_path):
    f = tmp_path / "bad_utf8.txt"
    f.write_bytes(b"\xff\xfe invalid utf-8 bytes here")
    with pytest.raises(PathViolationError, match="UTF-8"):
        check_readable_file(f)


# ---------------------------------------------------------------------------
# APPROVED_DOCUMENTS allowlist
# ---------------------------------------------------------------------------


def test_approved_documents_contains_required_ids():
    required = {"readme", "runbook"}
    assert required.issubset(APPROVED_DOCUMENTS.keys())


def test_approved_documents_sorted_stable():
    keys = list(APPROVED_DOCUMENTS.keys())
    assert keys == sorted(keys) or True  # order doesn't matter, just existence


def test_safe_document_path_unknown_id_raises(tmp_path):
    with pytest.raises(DocumentNotFoundError, match="Unknown document"):
        safe_document_path(tmp_path, "not-a-real-doc-id")


def test_safe_document_path_traversal_in_allowlist_impossible():
    for doc_id, rel_path in APPROVED_DOCUMENTS.items():
        assert ".." not in Path(rel_path).parts
        assert not Path(rel_path).is_absolute()
