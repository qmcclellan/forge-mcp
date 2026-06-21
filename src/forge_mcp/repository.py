"""Confined read-only reader for the Forge repository.

ForgeRepository is the only layer that performs file I/O against the Forge root.
All paths go through paths.py safety checks before any read operation.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .errors import DocumentNotFoundError, TemplateNotFoundError
from .limits import MAX_LIST_ENTRIES
from .paths import (
    APPROVED_DOCUMENTS,
    check_readable_file,
    safe_document_path,
    safe_template_dir,
    safe_template_file,
    validate_template_slug,
)

_VERSION_RE = re.compile(r'^\s*version\s*=\s*"([^"]+)"', re.MULTILINE)


class ForgeRepository:
    """Confined reader for a single validated Forge repository root."""

    def __init__(self, root: Path) -> None:
        self._root = root

    @property
    def root(self) -> Path:
        return self._root

    # ------------------------------------------------------------------
    # Repository metadata
    # ------------------------------------------------------------------

    def read_forge_version(self) -> str:
        """Read the Forge package version from pyproject.toml."""
        pyproject = self._root / "pyproject.toml"
        if not pyproject.is_file() or pyproject.is_symlink():
            return "unknown"
        text = pyproject.read_text(encoding="utf-8")
        m = _VERSION_RE.search(text)
        return m.group(1) if m else "unknown"

    # ------------------------------------------------------------------
    # Template discovery
    # ------------------------------------------------------------------

    def list_template_names(self) -> list[str]:
        """Return sorted template names from the templates/ directory."""
        templates_dir = self._root / "templates"
        names = sorted(
            d.name
            for d in templates_dir.iterdir()
            if d.is_dir() and not d.is_symlink() and not d.name.startswith(".")
        )
        return names[:MAX_LIST_ENTRIES]

    def get_template_metadata(self, template: str) -> dict[str, Any]:
        """Return parsed template.json for the named template."""
        validate_template_slug(template)
        tmpl_dir = safe_template_dir(self._root, template)
        if not tmpl_dir.exists() or not tmpl_dir.is_dir():
            raise TemplateNotFoundError(f"Template not found: {template}")
        meta_path = tmpl_dir / "template.json"
        if not meta_path.exists():
            return {
                "name": template,
                "_inferred": True,
                "_note": "template.json not present; metadata is inferred from directory name only",
            }
        check_readable_file(meta_path)
        return json.loads(meta_path.read_text(encoding="utf-8"))

    def list_template_files(self, template: str) -> list[str]:
        """Return a sorted, bounded list of relative file paths for a template."""
        validate_template_slug(template)
        tmpl_dir = safe_template_dir(self._root, template)
        if not tmpl_dir.exists() or not tmpl_dir.is_dir():
            raise TemplateNotFoundError(f"Template not found: {template}")
        files = sorted(
            str(p.relative_to(tmpl_dir))
            for p in tmpl_dir.rglob("*")
            if p.is_file() and not p.is_symlink()
        )
        return files[:MAX_LIST_ENTRIES]

    def read_template_file(self, template: str, rel_path: str) -> str:
        """Read a text file from inside a template directory."""
        path = safe_template_file(self._root, template, rel_path)
        check_readable_file(path)
        return path.read_text(encoding="utf-8")

    # ------------------------------------------------------------------
    # Approved documents
    # ------------------------------------------------------------------

    def list_approved_document_ids(self) -> list[str]:
        """Return the sorted list of approved document identifiers."""
        return sorted(APPROVED_DOCUMENTS)

    def read_approved_document(self, doc_id: str) -> str:
        """Read an approved Forge document by stable identifier."""
        path = safe_document_path(self._root, doc_id)
        # Raise DocumentNotFoundError (not PathViolationError) for approved-but-absent files
        # so callers can distinguish "unknown identifier" from "approved but unavailable".
        # Symlinks fall through to check_readable_file and remain PathViolationError.
        if not path.is_symlink() and not path.exists():
            raise DocumentNotFoundError(
                f"Document {doc_id!r} is approved but not currently available "
                f"in this Forge repository"
            )
        check_readable_file(path)
        return path.read_text(encoding="utf-8")

    def document_exists(self, doc_id: str) -> bool:
        """Return True if the approved document exists and is readable."""
        if doc_id not in APPROVED_DOCUMENTS:
            return False
        try:
            path = safe_document_path(self._root, doc_id)
            check_readable_file(path)
            return True
        except Exception:
            return False
