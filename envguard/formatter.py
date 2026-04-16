"""Formatter: rewrite a .env file with consistent style."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class FormatChange:
    key: str
    original_line: str
    formatted_line: str

    @property
    def changed(self) -> bool:
        return self.original_line != self.formatted_line


@dataclass
class FormatResult:
    changes: List[FormatChange] = field(default_factory=list)
    formatted: Dict[str, str] = field(default_factory=dict)

    @property
    def has_changes(self) -> bool:
        return any(c.changed for c in self.changes)

    @property
    def changed_keys(self) -> List[str]:
        return [c.key for c in self.changes if c.changed]

    def summary(self) -> str:
        n = len(self.changed_keys)
        if n == 0:
            return "All lines already well-formatted."
        return f"{n} line(s) reformatted."


def _format_line(key: str, value: str) -> str:
    """Produce a canonical KEY=value line (no surrounding quotes unless needed)."""
    # Strip surrounding whitespace from value
    value = value.strip()
    # Remove wrapping double or single quotes
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        value = value[1:-1]
    return f"{key.strip()}={value}"


def format_env(raw_lines: List[str]) -> FormatResult:
    """Parse *raw_lines* from a .env file and apply consistent formatting."""
    result = FormatResult()

    for raw in raw_lines:
        stripped = raw.strip()
        # Preserve blanks and comments as-is (not tracked as key changes)
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        formatted_line = _format_line(key, value)
        original_line = stripped
        change = FormatChange(
            key=key.strip(),
            original_line=original_line,
            formatted_line=formatted_line,
        )
        result.changes.append(change)
        result.formatted[key.strip()] = formatted_line.partition("=")[2]

    return result
