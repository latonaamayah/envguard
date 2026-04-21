from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class IndexEntry:
    key: str
    value: str
    position: int
    length: int
    is: bool

    def __str__(self) -> str:
        return f"[{self.position}] {self.key}={self.value!r} (len={self.length})"


@dataclass
class IndexResult:
    entries: List[IndexEntry] = field(default_factory=list)
    _by_key: Dict[str, IndexEntry] = field(default_factory=dict, repr=False)

    def has_entries(self) -> bool:
        return len(self.entries) > 0

    def get(self, key: str) -> Optional[IndexEntry]:
        return self._by_key.get(key)

    def keys(self) -> List[str]:
        return [e.key for e in self.entries]

    def empty_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.is_empty]

    def longest(self) -> Optional[IndexEntry]:
        if not self.entries:
            return None
        return max(self.entries, key=lambda e: e.length)

    def shortest(self) -> Optional[IndexEntry]:
        if not self.entries:
            return None
        return min(self.entries, key=lambda e: e.length)

    def summary(self) -> str:
        total = len(self.entries)
        empty = len(self.empty_keys())
        return f"{total} entries indexed, {empty} empty"


def index(env: Dict[str, str]) -> IndexResult:
    """Build a positional index of all environment variables."""
    result = IndexResult()
    for position, (key, value) in enumerate(env.items()):
        entry = IndexEntry(
            key=key,
            value=value,
            position=position,
            length=len(value),
            is_empty=value.strip() == "",
        )
        result.entries.append(entry)
        result._by_key[key] = entry
    return result
