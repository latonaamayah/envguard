"""Detect and report placeholder/stub values in .env files."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List

_PLACEHOLDER_PATTERNS = [
    "changeme", "placeholder", "your_", "<", ">", "example",
    "todo", "fixme", "replace", "insert", "fill", "xxx", "...",
]


@dataclass
class PlaceholderEntry:
    key: str
    value: str
    reason: str

    def __str__(self) -> str:
        return f"{self.key}={self.value!r} ({self.reason})"


@dataclass
class PlaceholderResult:
    entries: List[PlaceholderEntry] = field(default_factory=list)
    clean: List[str] = field(default_factory=list)

    @property
    def has_placeholders(self) -> bool:
        return len(self.entries) > 0

    @property
    def placeholder_keys(self) -> List[str]:
        return [e.key for e in self.entries]

    def summary(self) -> str:
        total = len(self.entries) + len(self.clean)
        if not self.has_placeholders:
            return f"No placeholders found in {total} variable(s)."
        return (
            f"{len(self.entries)} placeholder(s) found out of {total} variable(s)."
        )


def _is_placeholder(value: str) -> str | None:
    """Return a reason string if value looks like a placeholder, else None."""
    stripped = value.strip()
    if not stripped:
        return None
    lower = stripped.lower()
    for pattern in _PLACEHOLDER_PATTERNS:
        if pattern in lower:
            return f"matches pattern '{pattern}'"
    if stripped.startswith("${") and stripped.endswith("}"):
        return "unresolved variable reference"
    return None


def detect(env: Dict[str, str]) -> PlaceholderResult:
    """Scan env dict for placeholder values."""
    result = PlaceholderResult()
    for key, value in env.items():
        reason = _is_placeholder(value)
        if reason:
            result.entries.append(PlaceholderEntry(key=key, value=value, reason=reason))
        else:
            result.clean.append(key)
    return result
