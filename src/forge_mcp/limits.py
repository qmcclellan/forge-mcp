"""Size limits, entry limits, and validation patterns for forge-mcp."""

from __future__ import annotations

import re

MAX_FILE_BYTES: int = 64 * 1024       # 64 KB per file
MAX_LIST_ENTRIES: int = 200           # maximum file-listing entries
MAX_RESPONSE_BYTES: int = 256 * 1024  # total response size guard

# Template and document identifiers must be lowercase kebab slugs.
TEMPLATE_SLUG_RE = re.compile(r"^[a-z][a-z0-9-]{0,63}$")
DOCUMENT_ID_RE = re.compile(r"^[a-z][a-z0-9-]{0,63}$")
