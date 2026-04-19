from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class CompactEntry:
    key: str
    original_value: str
    compacted_value: str

    @property
    def changed(self) -> bool:
        return self.original_value != self.compacted_value


@dataclass
class CompactResult:
    entries: List[CompactEntry] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return any(e.changed for e in self.entries)

    @property
    def changed_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.changed]

    @property
    def as_dict(self) -> Dict[str, str]:
        return {e.key: e.compacted_value for e in self.entries}

    def summary(self) -> str:
        total = len(self.entries)
        changed = len(self.changed_keys)
        return f"{changed}/{total} values compacted"


def _compact_value(value: str) -> str:
    """Remove redundant whitespace and normalize separators inside a value."""
    # Collapse internal whitespace sequences to a single space
    import re
    return re.sub(r" {2,}", " ", value.strip())


def compact(env: Dict[str, str]) -> CompactResult:
    """Compact all values in the env dict by normalising whitespace."""
    result = CompactResult()
    for key, value in env.items():
        compacted = _compact_value(value)
        result.entries.append(CompactEntry(
            key=key,
            original_value=value,
            compacted_value=compacted,
        ))
    return result
