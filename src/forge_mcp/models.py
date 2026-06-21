"""Typed models for Forge MCP structured data."""

from __future__ import annotations

from typing import Any


class TemplateMetadata:
    """Parsed content of a template's template.json manifest."""

    __slots__ = (
        "name",
        "language",
        "runtime",
        "description",
        "tags",
        "recommended_use",
        "required_files",
        "optional_files",
        "smoke_test_command",
    )

    def __init__(self, raw: dict[str, Any]) -> None:
        self.name: str = raw.get("name", "")
        self.language: str = raw.get("language", "unknown")
        self.runtime: str = raw.get("runtime", "unknown")
        self.description: str = raw.get("description", "")
        self.tags: list[str] = raw.get("tags") or []
        self.recommended_use: str = raw.get("recommended_use", "")
        self.required_files: list[str] = raw.get("required_files") or []
        self.optional_files: list[str] = raw.get("optional_files") or []
        self.smoke_test_command: list[str] | None = raw.get("smoke_test_command")

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "language": self.language,
            "runtime": self.runtime,
            "description": self.description,
            "tags": self.tags,
            "recommended_use": self.recommended_use,
            "required_files": self.required_files,
            "optional_files": self.optional_files,
            "smoke_test_command": self.smoke_test_command,
        }
