"""Tests for limits constants and template slug regex."""

from forge_mcp.limits import (
    DOCUMENT_ID_RE,
    MAX_FILE_BYTES,
    MAX_LIST_ENTRIES,
    MAX_RESPONSE_BYTES,
    TEMPLATE_SLUG_RE,
)


def test_max_file_bytes():
    assert MAX_FILE_BYTES == 64 * 1024


def test_max_list_entries():
    assert MAX_LIST_ENTRIES == 200


def test_max_response_bytes():
    assert MAX_RESPONSE_BYTES == 256 * 1024


def test_template_slug_valid():
    assert TEMPLATE_SLUG_RE.fullmatch("python-worker")
    assert TEMPLATE_SLUG_RE.fullmatch("java-spring-service")
    assert TEMPLATE_SLUG_RE.fullmatch("node-dashboard")
    assert TEMPLATE_SLUG_RE.fullmatch("a")
    assert TEMPLATE_SLUG_RE.fullmatch("a1")
    assert TEMPLATE_SLUG_RE.fullmatch("a" * 64)


def test_template_slug_invalid():
    assert not TEMPLATE_SLUG_RE.fullmatch("")
    assert not TEMPLATE_SLUG_RE.fullmatch("Python-Worker")
    assert not TEMPLATE_SLUG_RE.fullmatch("../evil")
    assert not TEMPLATE_SLUG_RE.fullmatch("/absolute")
    assert not TEMPLATE_SLUG_RE.fullmatch("has space")
    assert not TEMPLATE_SLUG_RE.fullmatch("a" * 65)
    assert not TEMPLATE_SLUG_RE.fullmatch("-starts-with-dash")
    assert not TEMPLATE_SLUG_RE.fullmatch("1starts-with-digit")


def test_document_id_re_valid():
    assert DOCUMENT_ID_RE.fullmatch("readme")
    assert DOCUMENT_ID_RE.fullmatch("runbook")
    assert DOCUMENT_ID_RE.fullmatch("artifact-publishing")


def test_document_id_re_invalid():
    assert not DOCUMENT_ID_RE.fullmatch("")
    assert not DOCUMENT_ID_RE.fullmatch("../etc/passwd")
    assert not DOCUMENT_ID_RE.fullmatch("README")
