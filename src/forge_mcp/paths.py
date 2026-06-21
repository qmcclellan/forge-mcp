"""Path safety, confinement, and approved-document allowlist for forge-mcp.

All user-controlled path values pass through this module before any file I/O.
The key invariant: every resolved path must remain under its designated sub-root.
"""

from __future__ import annotations

from pathlib import Path

from .errors import DocumentNotFoundError, PathViolationError
from .limits import MAX_FILE_BYTES, TEMPLATE_SLUG_RE

# Stable identifiers → relative paths within the Forge root.
# Only paths listed here are readable via read_forge_document.
APPROVED_DOCUMENTS: dict[str, str] = {
    "readme": "README.md",
    "runbook": "docs/runbook.md",
    "architecture": "docs/architecture.md",
    "artifact-publishing": "docs/artifact-publishing.md",
    "template-registry-runbook": "docs/template-registry-runbook.md",
    "interview-talk-track": "docs/interview-talk-track.md",
    "forge-yaml-example": "examples/forge.yaml",
}


def validate_template_slug(value: str) -> str:
    """Validate a template identifier as a safe lowercase kebab slug."""
    if not isinstance(value, str) or not TEMPLATE_SLUG_RE.fullmatch(value):
        raise PathViolationError(
            "Invalid template identifier: must match ^[a-z][a-z0-9-]{0,63}$"
        )
    return value


def validate_relative_path(rel: str) -> None:
    """Reject absolute paths, traversal sequences, and NUL bytes."""
    if not isinstance(rel, str):
        raise PathViolationError("Path must be a string")
    if "\x00" in rel:
        raise PathViolationError("Path contains NUL byte")
    p = Path(rel)
    if p.is_absolute():
        raise PathViolationError("Absolute paths are not allowed")
    if ".." in p.parts:
        raise PathViolationError("Path traversal (..) is not allowed")


def safe_join(root: Path, *parts: str) -> Path:
    """Join parts under root and verify the resolved result stays confined.

    Follows symlinks via resolve() so symlink-escape attempts (where a symlink
    inside the root points outside it) are caught by the parent check.
    """
    resolved_root = root.resolve()
    candidate = resolved_root.joinpath(*parts).resolve()
    if candidate != resolved_root and resolved_root not in candidate.parents:
        raise PathViolationError("Requested path escapes the Forge root")
    return candidate


def safe_template_dir(forge_root: Path, template: str) -> Path:
    """Return the validated directory path for a named template."""
    validate_template_slug(template)
    return safe_join(forge_root / "templates", template)


def safe_template_file(forge_root: Path, template: str, rel_path: str) -> Path:
    """Return the validated path for a specific file inside a template."""
    validate_template_slug(template)
    validate_relative_path(rel_path)
    tmpl_root = forge_root / "templates" / template
    return safe_join(tmpl_root, rel_path)


def safe_document_path(forge_root: Path, doc_id: str) -> Path:
    """Return the validated path for an approved Forge document."""
    if doc_id not in APPROVED_DOCUMENTS:
        raise DocumentNotFoundError(
            f"Unknown document identifier: {doc_id!r}. "
            f"Approved identifiers: {sorted(APPROVED_DOCUMENTS)}"
        )
    rel = APPROVED_DOCUMENTS[doc_id]
    return safe_join(forge_root, rel)


def check_readable_file(path: Path) -> None:
    """Raise PathViolationError if the path is not a safe, readable, text file.

    Checks (in order): symlink, existence, regular file, size limit, binary content.
    Symlink is checked first because is_file() and stat() follow symlinks.
    """
    if path.is_symlink():
        raise PathViolationError("Symlinks are not allowed")
    if not path.exists():
        raise PathViolationError("File not found")
    if not path.is_file():
        raise PathViolationError("Not a regular file")
    size = path.stat().st_size
    if size > MAX_FILE_BYTES:
        raise PathViolationError(
            f"File exceeds size limit ({size} bytes > {MAX_FILE_BYTES} byte limit)"
        )
    # Binary detection: NUL bytes in the first 8 KB indicate non-text content.
    sample = path.read_bytes()[:8192]
    if b"\x00" in sample:
        raise PathViolationError("File appears to be binary (NUL bytes detected)")
    try:
        sample.decode("utf-8")
    except UnicodeDecodeError:
        raise PathViolationError("File is not valid UTF-8")
