from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class QuoteEntry:
    key: str
    original: str
    quoted: str

    @property
    def changed(self) -> bool:
        return self.original != self.quoted


@dataclass
class QuoteResult:
    entries: List[QuoteEntry] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return any(e.changed for e in self.entries)

    @property
    def changed_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.changed]

    @property
    def as_dict(self) -> Dict[str, str]:
        return {e.key: e.quoted for e in self.entries}

    def summary(self) -> str:
        n = len(self.changed_keys)
        return f"{n} key(s) quoted."


def _needs_quoting(value: str) -> bool:
    """Return True if the value contains spaces, special chars, or is empty."""
    if value == "":
        return False
    if value.startswith('"') and value.endswith('"'):
        return False
    if value.startswith("'") and value.endswith("'"):
        return False
    return any(c in value for c in (" ", "\t", "#", "=", "\\", "'", '"'))


def quote(
    env: Dict[str, str],
    style: str = "double",
    keys: List[str] | None = None,
) -> QuoteResult:
    """Wrap values in quotes.

    Args:
        env: mapping of key -> value
        style: 'double' or 'single'
        keys: optional list of keys to quote; if None, auto-detect
    """
    q = '"' if style == "double" else "'"
    entries: List[QuoteEntry] = []

    for key, value in env.items():
        if keys is not None:
            should_quote = key in keys
        else:
            should_quote = _needs_quoting(value)

        if should_quote:
            quoted = f"{q}{value}{q}"
        else:
            quoted = value

        entries.append(QuoteEntry(key=key, original=value, quoted=quoted))

    return QuoteResult(entries=entries)
